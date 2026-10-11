"""
crawl_docs.py - Thu thập tài liệu học vụ từ website trường (Bước 2: Crawl)

Quy trình:
  1. Đọc robots.txt  -> biết được phép crawl trang nào
  2. Mở các trang khởi đầu (START_URLS)
  3. Trong mỗi trang: tìm tất cả link
        - link tới file (.pdf/.docx/.doc) -> TẢI VỀ
        - link tới trang khác cùng website -> đưa vào hàng đợi để mở tiếp
  4. Mỗi lần tải xong -> ghi 1 dòng vào manifest.jsonl (nguồn, ngày tải, mã băm)
  5. Nghỉ vài giây giữa các request để không làm quá tải máy chủ

Cài đặt:  pip install requests beautifulsoup4
Chạy:     python crawl_docs.py
"""
import hashlib
import json
import re
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib import robotparser
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ============ CẤU HÌNH (sửa phần này) ============
BASE_URL = "https://thanglong.edu.vn"
START_URLS = [
    # --- LƯỢT 2: các bài viết có văn bản đính kèm (lấy từ kết quả khảo sát trang hub) ---
    "/quyet-dinh-ban-hanh-quy-che-dao-tao-trinh-do-dai-hoc-cua-truong-dai-hoc-thang-long-21000.html",
    "/quyet-dinh-ban-hanh-khung-chuong-trinh-dao-tao-dai-hoc-cac-nganh-cua-truong-dai-hoc-thang-long-nam-2024-20942.html",
    "/quyet-dinh-vv-ban-hanh-quy-dinh-thoi-gian-hoc-hang-ngay-va-ke-hoach-dao-tao-nam-hoc-2025-2026-21423.html",
    "/quyet-dinh-ban-hanh-chuan-dau-ra-chuong-trinh-dao-tao-cua-truong-dai-hoc-thang-long-19377.html",   # MỚI
    "/bieu-mau-don-tu-danh-cho-sinh-vien-19146.html",                                                      # MỚI
    "/thong-bao/phong-tai-vu",                                                                             # MỚI: Học phí (trang danh sách)
]
DRY_RUN = True         # True = chỉ LIỆT KÊ, không tải gì. Thấy danh sách [FILE] ổn thì đổi thành False
# Chỉ đi theo link khớp 1 trong các mẫu này (tránh lạc sang menu/khoa/ngành)
FOLLOW_URL_PATTERNS = [r"-\d{4,6}\.html$", r"/thong-bao/"]
# Không bao giờ đi theo link khớp các mẫu này
EXCLUDE_URL_PATTERNS = [r"facebook\.com", r"twitter\.com", r"youtube\.com", r"tuyen-sinh", r"doi-song",
                        r"/tag/", r"logout", r"login", r"/search/", r"2023-2024"]  # 2023-2024: kế hoạch đã cũ
FILE_EXTENSIONS = (".pdf", ".docx", ".doc")  # loại file cần tải
MAX_DEPTH = 1          # 0 = chỉ mở các URL trong START_URLS; 1 = mở thêm các bài viết con (vd: danh sách Học phí)
MAX_PAGES = 200        # chốt chặn an toàn, tránh crawl vô hạn
DELAY_SECONDS = 1.5    # nghỉ giữa các request
OUT_DIR = Path("data/raw")
USER_AGENT = "StudentRAGBot/0.1 (do an hoc tap; lien he: email-cua-ban@example.com)"
# ================================================

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def normalize_start_url(u):
    """Chống dán đôi địa chỉ: 'https://a.vn/https://a.vn/x' -> 'https://a.vn/x'.
    Chấp nhận cả đường dẫn ngắn '/x' lẫn URL đầy đủ."""
    cut = max(u.rfind("https://"), u.rfind("http://"))
    u = u[cut:] if cut > 0 else u
    return urljoin(BASE_URL, u)


def load_robots(base_url):
    rp = robotparser.RobotFileParser()
    rp.set_url(urljoin(base_url, "/robots.txt"))
    try:
        rp.read()
    except Exception:
        print("Không đọc được robots.txt, mặc định cho phép (hãy tự kiểm tra bằng tay).")
    return rp


def polite_get(url, **kwargs):
    """GET có nghỉ giữa các lần gọi và thử lại 2 lần nếu lỗi mạng."""
    for attempt in range(3):
        try:
            time.sleep(DELAY_SECONDS)
            resp = session.get(url, timeout=30, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.HTTPError as e:
            print(f"  ! lỗi HTTP {e.response.status_code}, bỏ qua: {url}")
            if e.response.status_code < 500:
                return None          # 404, 403... thử lại cũng vô ích
        except requests.RequestException as e:
            print(f"  ! lỗi mạng ({attempt + 1}/3) {url}: {e}")
    return None


def is_file_link(url):
    return urlparse(url).path.lower().endswith(FILE_EXTENSIONS)


def host(url):
    h = urlparse(url).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def same_site(url):
    """thanglong.edu.vn và www.thanglong.edu.vn được coi là một."""
    return host(url) == host(BASE_URL)


def unwrap_viewer(url):
    """Nhiều trang nhúng PDF qua khung xem, ví dụ  viewer?file=/files/abc.pdf
    hoặc Google Docs viewer ?url=...  -> lấy ra đường dẫn file thật."""
    query = parse_qs(urlparse(url).query)
    for key in ("file", "url", "src"):
        for value in query.get(key, []):
            if value.lower().split("?")[0].endswith(FILE_EXTENSIONS):
                return urljoin(url, value)
    return url


def extract_links(html_bytes, page_url):
    """Trả về danh sách (url_tuyệt_đối, chữ_hiển_thị) của:
       - thẻ <a href>                      (link bình thường)
       - thẻ <iframe/embed/object src>     (PDF NHÚNG trong trang)
    Truyền BYTES (không phải resp.text) để BeautifulSoup tự nhận bảng mã,
    tránh lỗi vỡ chữ tiếng Việt khi server không khai báo charset."""
    soup = BeautifulSoup(html_bytes, "html.parser")
    raw = [(a["href"], a.get_text(strip=True)) for a in soup.find_all("a", href=True)]
    for tag, attr in (("iframe", "src"), ("embed", "src"), ("object", "data")):
        raw += [(t[attr], f"<{tag}> nhúng") for t in soup.find_all(tag) if t.get(attr)]
    links = []
    for href, text in raw:
        href = re.split(r"[<>]", href)[0].strip()   # vá lỗi HTML thiếu dấu nháy đóng
        if not href or href.startswith(("mailto:", "javascript:", "#")):
            continue
        full = unwrap_viewer(urljoin(page_url, href).split("#")[0])
        links.append((full, text))
    return links


def allowed_to_follow(url):
    if any(re.search(p, url) for p in EXCLUDE_URL_PATTERNS):
        return False
    return not FOLLOW_URL_PATTERNS or any(re.search(p, url) for p in FOLLOW_URL_PATTERNS)


def safe_filename(url):
    name = unquote(Path(urlparse(url).path).name)
    return re.sub(r'[\\/:*?"<>|]', "_", name) or "unnamed"


def download_file(url, found_on, link_text, manifest):
    target = OUT_DIR / "files" / safe_filename(url)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        print(f"  = đã có, bỏ qua: {target.name}")
        return
    resp = polite_get(url, stream=True)
    if resp is None:
        return
    data = resp.content
    target.write_bytes(data)
    record = {
        "url": url,
        "found_on": found_on,
        "link_text": link_text,
        "saved_as": str(target),
        "content_type": resp.headers.get("Content-Type", ""),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest.write(json.dumps(record, ensure_ascii=False) + "\n")
    manifest.flush()
    print(f"  + đã tải: {target.name} ({len(data) // 1024} KB)")


def save_page_html(url, html_bytes):
    """Lưu cả bản HTML của trang (nhiều thông báo nằm ngay trong HTML)."""
    name = re.sub(r"[^\w\-]+", "_", urlparse(url).path.strip("/")) or "index"
    path = OUT_DIR / "html" / f"{name}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(html_bytes)


def crawl():
    if DRY_RUN:
        print("*** DRY_RUN: chỉ liệt kê link, KHÔNG tải file ***\n")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    robots = load_robots(BASE_URL)
    queue = deque((normalize_start_url(u), 0) for u in START_URLS)   # (url, độ sâu)
    visited = set()
    pages_seen = 0

    with open(OUT_DIR / "manifest.jsonl", "a", encoding="utf-8") as manifest:
        while queue and pages_seen < MAX_PAGES:
            url, depth = queue.popleft()
            if url in visited:
                continue
            visited.add(url)

            if not robots.can_fetch(USER_AGENT, url):
                print(f"[robots.txt cấm] {url}")
                continue

            print(f"[trang, sâu {depth}] {url}")
            resp = polite_get(url)
            if resp is None:
                continue
            pages_seen += 1
            save_page_html(url, resp.content)

            seen_here = set()
            for link, text in extract_links(resp.content, url):
                if link in seen_here:          # menu hay lặp lại cùng 1 link nhiều lần
                    continue
                seen_here.add(link)
                if is_file_link(link):
                    if DRY_RUN:
                        print(f"    [FILE] {link}   ({text[:50]})")
                    elif robots.can_fetch(USER_AGENT, link):
                        download_file(link, url, text, manifest)
                elif same_site(link) and allowed_to_follow(link):
                    if DRY_RUN:
                        print(f"    [trang] {link}   ({text[:50]})")
                    if depth < MAX_DEPTH and link not in visited:
                        queue.append((link, depth + 1))
                elif DRY_RUN and not any(re.search(p, link) for p in EXCLUDE_URL_PATTERNS):
                    why = "không khớp bộ lọc" if same_site(link) else "NGOÀI SITE"
                    print(f"    [bỏ qua: {why}] {link}   ({text[:50]})")

    print(f"\nXong. Đã mở {pages_seen} trang. Xem danh sách file tại {OUT_DIR / 'manifest.jsonl'}")


if __name__ == "__main__":
    crawl()
