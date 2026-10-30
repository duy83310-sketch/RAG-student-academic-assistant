import sys
import json
import re
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

# Dictionary to standardize department names
DEPT_STANDARDIZATION = {
    'KHOA CÔNG NGHỆ THÔNG TIN': 'Khoa Công nghệ thông tin',
    'KHOA KHOA HỌC SỨC KHỎE': 'Khoa Khoa học Sức khỏe',
    'KHOA KINH TẾ QUẢN LÝ': 'Khoa Kinh tế - Quản lý',
    'Khoa Kinh tế và Quản lý': 'Khoa Kinh tế - Quản lý',
    'KHOA TRUYỀN THÔNG ĐA PHƯƠNG TIỆN': 'Khoa Truyền thông Đa phương tiện',
    'KHOA ÂM NHẠC ỨNG DỤNG': 'Khoa Âm nhạc Ứng dụng',
    'PHÒNG SAU ĐẠI HỌC & QUẢN LÝ KHOA HỌC': 'Phòng Sau Đại học & Quản lý Khoa học',
    'Phòng Sau đại học và Quản lý Khoa học': 'Phòng Sau Đại học & Quản lý Khoa học',
    'Phòng Sau đại học và Quản lý khoa học': 'Phòng Sau Đại học & Quản lý Khoa học',
    'PHÒNG TIẾP SINH VIÊN': 'Phòng Tiếp sinh viên',
    'Phòng Công tác chính trị sinh viên': 'Phòng Công tác Chính trị sinh viên',
    'Phòng Công tác Chính trị - Sinh viên': 'Phòng Công tác Chính trị sinh viên',
    'Phòng Thanh tra-pháp chế': 'Phòng Thanh tra - Pháp chế',
    'Trung tâm E-learning': 'Trung tâm E-Learning',
    'Trung tâm Khảo thí và  Đảm bảo chất lượng': 'Trung tâm Khảo thí và Đảm bảo chất lượng',
    'Trung tâm Đảm bảo chất lượng và Khảo thí': 'Trung tâm Khảo thí và Đảm bảo chất lượng',
    'TƯ VẤN TUYỂN SINH ĐẠI HỌC': 'Tư vấn Tuyển sinh Đại học',
    'Viên nghiên cứu nhận thức và giáo dục Thăng Long (TICES)': 'Viện Nghiên cứu Nhận thức và Giáo dục Thăng Long (TICES)',
    'Viện toán học và khoa học ứng dụng Thăng Long (TIMAS)': 'Viện Toán học và Khoa học Ứng dụng Thăng Long (TIMAS)',
    'VĂN PHÒNG TRƯỜNG': 'Văn phòng Trường',
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Normalize unicode spaces and double spaces
    t = re.sub(r'[ \t\r\f\v]+', ' ', text)
    # Normalize multiple newlines
    lines = [line.strip() for line in t.split('\n')]
    cleaned_lines = []
    prev_blank = False
    for l in lines:
        if not l:
            if not prev_blank:
                cleaned_lines.append('')
                prev_blank = True
        else:
            cleaned_lines.append(l)
            prev_blank = False
    return '\n'.join(cleaned_lines).strip()

def clean_content_field(content: str, title: str) -> str:
    if not content:
        return ""
    c = clean_text(content)
    # Check if title is duplicated at the start of content
    title_clean = title.strip()
    if title_clean and c.startswith(title_clean):
        # Remove the first occurrence of title if followed by newline or similar
        remainder = c[len(title_clean):].lstrip('\n').strip()
        if remainder:
            # Check if there is another redundant header like "Title|Trường Đại học Thăng Long"
            tlu_header = f"{title_clean}|Trường Đại học Thăng Long"
            if remainder.startswith(tlu_header):
                remainder = remainder[len(tlu_header):].lstrip('\n').strip()
            if remainder:
                c = remainder
    return c

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'

def process_crawl_data():
    raw_json_path = RAW_DIR / 'crawl_v2.json'
    if not raw_json_path.exists():
        raw_json_path = Path('crawl_v2.json')

    print(f"[*] Reading raw crawl data from {raw_json_path}...")
    with open(raw_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = []
    cleaned_count = 0

    for item in data:
        new_item = dict(item)
        
        # 1. Standardize department
        dept = new_item.get('department')
        if dept and dept in DEPT_STANDARDIZATION:
            new_item['department'] = DEPT_STANDARDIZATION[dept]
            cleaned_count += 1
            
        # 2. Clean title
        title = new_item.get('title', '')
        clean_tit = re.sub(r'\s+', ' ', title).strip()
        new_item['title'] = clean_tit
        
        # 3. Clean content
        content = new_item.get('content', '')
        new_item['content'] = clean_content_field(content, clean_tit)
        
        cleaned_data.append(new_item)

    print(f"[*] Processed {len(cleaned_data)} items. Standardized {cleaned_count} department names.")
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save cleaned JSON
    out_json = PROCESSED_DIR / 'crawl_v2_cleaned.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved {out_json}")
    
    # Save cleaned CSV (dùng utf-8-sig có BOM để Excel không lỗi font)
    df_cleaned = pd.DataFrame(cleaned_data)
    out_csv = PROCESSED_DIR / 'crawl_v2_cleaned.csv'
    df_cleaned.to_csv(out_csv, index=False, encoding='utf-8-sig')
    print(f"[+] Saved (UTF-8-SIG) {out_csv}")

if __name__ == '__main__':
    process_crawl_data()

