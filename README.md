# ĐỀ TÀI 3: ỨNG DỤNG RAG HỖ TRỢ SINH VIÊN TRA CỨU THÔNG TIN HỌC VỤ
## BÁO CÁO TIẾN ĐỘ THỰC TẬP — TUẦN 2 (TIỀN XỬ LÝ, CHUNKING & METADATA)

---

## 1. Tổng quan đề tài & Phạm vi Tuần 2
Căn cứ theo bản đặc tả yêu cầu thực tập tại tài liệu `YeuCauThucTap.pdf` (Đề tài 3), đề tài tập trung xây dựng hệ thống hỏi đáp thông minh dựa trên kỹ thuật **RAG (Retrieval-Augmented Generation)** giúp sinh viên Đại học Thăng Long tra cứu chính xác quy chế, học phí, lịch thi và 25 chương trình đào tạo chuyên ngành với dẫn chứng nguồn chính thống.

Trong chu trình 10 tuần, **Tuần 2** đảm nhận vai trò hoàn thiện **Pha Indexing**:
- Làm sạch triệt để dữ liệu website crawl từ Tuần 1 (chuẩn hóa danh xưng 37 đơn vị, lọc trùng lặp tiêu đề).
- Khắc phục toàn bộ 529 lỗi OCR từ 51 file PDF CTĐT K39 (chuẩn hóa 92 mã học phần TLU, xóa 39 rác đường kẻ bảng, bóc tách 395 cụm từ tiếng Việt).
- Triển khai chiến lược **Hybrid Splitting** (Cắt đệ quy 650–700 ký tự kèm overlap 120 ký tự + Bóc tách cấu trúc môn học theo năm) sinh **496 Chunks sạch**.
- Đóng gói **12 trường siêu dữ liệu (Metadata Schema)** hỗ trợ lọc trước (Pre-filtering) và trích dẫn nguồn.

---

## 2. Kiến trúc thư mục mô-đun hóa (Project Directory Tree)

```text
d:/Intern/Bao_cao_tuan_2/
├── data/                                 # QUẢN LÝ DỮ LIỆU ĐA TẦNG (DATA PIPELINE)
│   ├── raw/                              # Tầng 1: Dữ liệu thô ban đầu (kế thừa từ Tuần 1)
│   │   ├── crawl_v2.json                 # 141 bài crawl thô từ website Đại học Thăng Long
│   │   ├── crawl_v2.csv                  # Bảng dữ liệu crawl thô (141 dòng x 8 thuộc tính)
│   │   └── loi_crawl.xlsx                # File theo dõi 529 lỗi OCR từ 51 file CTĐT K39
│   ├── processed/                        # Tầng 2: Dữ liệu đã tiền xử lý & làm sạch
│   │   ├── crawl_v2_cleaned.json         # 141 bài đã chuẩn hóa danh xưng phòng ban, lọc trùng tiêu đề
│   │   ├── crawl_v2_cleaned.csv          # Bảng dữ liệu web đã làm sạch
│   │   └── loi_crawl_hoan_thien.xlsx     # 529/529 lỗi OCR đào tạo đã sửa triệt để (100% hoàn thành)
│   └── chunks/                           # Tầng 3: Ngữ liệu phân đoạn (Clean Corpus) sẵn sàng cho Vector DB
│       ├── clean_chunks.json             # 496 Chunks hoàn chỉnh kèm 12 trường siêu dữ liệu chuẩn
│       └── clean_chunks.csv              # Bảng tra cứu & kiểm toán chất lượng 496 chunks
│
├── src/                                  # MÃ NGUỒN PIPELINE THEO MÔ-ĐUN (MODULAR ARCHITECTURE)
│   ├── cleaning/                         # Phân hệ 1: Tiền xử lý & làm sạch ngữ liệu
│   │   ├── clean_crawl_data.py           # Làm sạch bài viết web, chuẩn hóa danh xưng 37 đơn vị
│   │   └── fill_loi_crawl.py             # Tự động sửa 529 lỗi OCR theo luật học vụ TLU & từ điển
│   ├── chunking/                         # Phân hệ 2: Phân mảnh ngữ nghĩa & Đóng gói Metadata (Trọng tâm Tuần 2)
│   │   └── chunking_pipeline.py          # Thuật toán Hybrid Splitting & gán 12 trường metadata
│   └── evaluation/                       # Phân hệ 3: Kiểm toán chất lượng & phân tích thống kê
│       └── audit_and_analyze.py          # Phân tích phân bố độ dài, độ bao phủ và tính toàn vẹn 3 tầng dữ liệu
│
├── reports/                              # BÁO CÁO TIẾN ĐỘ & TÀI LIỆU HỌC THUẬT
│   ├── Bao_Cao_Tuan_2_v2.html            # Báo cáo tiến độ Tuần 2 (Phiên bản Academic / Chuẩn in ấn Word)
│   ├── Bao_Cao_Tuan_2.html               # Báo cáo tiến độ Tuần 2 (Phiên bản Dashboard tương tác trực quan)
│   └── Bao_Cao_Thuc_Tap_Tuan_2.md        # Tài liệu báo cáo chi tiết định dạng Markdown
│
├── Bao_Cao_Tuan_2_v2.html                # Trang báo cáo chính mở trực tiếp từ thư mục gốc
└── README.md                             # Tài liệu tổng quan kiến trúc dự án và hướng dẫn thực thi
```

---

## 3. Hướng dẫn thực thi nhanh Pipeline (Quickstart)

Chạy tuần tự các lệnh sau từ thư mục gốc `d:/Intern/Bao_cao_tuan_2`:

```bash
# Bước 1: Làm sạch dữ liệu crawl website & chuẩn hóa danh xưng phòng ban
python src/cleaning/clean_crawl_data.py

# Bước 2: Tự động khắc phục 529 lỗi OCR từ 51 file PDF CTĐT K39
python src/cleaning/fill_loi_crawl.py

# Bước 3: Phân mảnh đệ quy Hybrid Chunking & đóng gói 12 trường Metadata
python src/chunking/chunking_pipeline.py

# Bước 4: Kiểm toán toàn diện chất lượng ngữ liệu và xác thực Clean Corpus
python src/evaluation/audit_and_analyze.py
```

---

## 4. Kế hoạch triển khai Tuần 3 (Pha Embedding & Vector Database)
1. **Benchmark Embedding Models**: So sánh `BAAI/bge-m3`, `intfloat/multilingual-e5-large`, `bkai-foundation-models/vietnamese-bi-encoder`.
2. **Khởi tạo Vector Database**: Cấu hình `ChromaDB` / `FAISS` cục bộ, nạp 496 chunks cùng siêu dữ liệu.
3. **Thử nghiệm Retrieval**: Đánh giá Top-k Recall và MRR trên bộ câu hỏi trắc nghiệm học vụ thực tế.
