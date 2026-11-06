# HỆ THỐNG RAG HỖ TRỢ SINH VIÊN TRA CỨU THÔNG TIN HỌC VỤ (ĐẠI HỌC THĂNG LONG)
## DỰ ÁN THỰC TẬP CHUYÊN NGÀNH / TỐT NGHIỆP — ĐỀ TÀI 3

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![VectorDB ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange.svg)](https://www.trychroma.com/)
[![Retrieval Hybrid](https://img.shields.io/badge/Retrieval-BM25%20%2B%20Dense%20%2B%20Rerank-green.svg)]()
[![Status Complete](https://img.shields.io/badge/Milestone-Week%201%E2%80%934%20Complete-brightgreen.svg)]()

---

## 1. Tổng quan đề tài & Tiến độ thực tập

Căn cứ theo bản đặc tả yêu cầu thực tập tại tài liệu `YeuCauThucTap.pdf` (Đề tài 3), dự án tập trung xây dựng hệ thống hỏi đáp thông minh dựa trên kỹ thuật **RAG (Retrieval-Augmented Generation)** giúp sinh viên Đại học Thăng Long tra cứu chính xác quy chế đào tạo, học phí, lịch thi và 25 chương trình đào tạo chuyên ngành với dẫn chứng nguồn chính thống.

### Lộ trình tiến độ thực hiện:
* **Tuần 1 (Thu thập & chuẩn hóa dữ liệu):** Thu thập thô 141 bài từ website trường và 51 file PDF CTĐT K39.
* **Tuần 2 (Tiền xử lý, Chunking & Metadata Schema):**
  - Làm sạch chuẩn hóa danh xưng 37 đơn vị phòng ban, loại bỏ trùng lặp tiêu đề.
  - Tự động khắc phục 529/529 lỗi OCR từ 51 file PDF chương trình đào tạo.
  - Phân mảnh đệ quy Hybrid Splitting sinh **496 chunks sạch**, đóng gói **12 trường siêu dữ liệu (Metadata)**.
* **Tuần 3 (Embedding & Vector Database):**
  - Benchmark so sánh 5 họ mô hình: `BAAI/bge-m3`, `vietnamese-bi-encoder`, `multilingual-e5-base`, `text-embedding-3-small`, và `all-MiniLM-L6-v2 ONNX`.
  - Khởi tạo cơ sở dữ liệu `ChromaDB` cục bộ (HNSW metric Cosine), vector hóa và đánh chỉ mục 100% (496/496) chunks sạch.
  - Hỗ trợ cơ chế lọc trước siêu dữ liệu (Metadata Pre-filtering).
* **Tuần 4 (Hybrid Retrieval & Cross-Encoder Reranker):**
  - Xây dựng bộ tìm kiếm ngữ nghĩa Dense Retriever kết hợp thuật toán khử trùng lặp **MMR (Maximal Marginal Relevance, $\lambda=0.65$)**.
  - Bổ sung bộ tìm kiếm từ khóa chính xác **BM25Okapi** và dung hợp thứ hạng bằng **Reciprocal Rank Fusion (RRF)**.
  - Triển khai **Cross-Encoder Reranker** chấm điểm tương tác token chéo, tái sắp xếp Top-15 ứng viên lên Top-5.
  - Kiểm toán định lượng trên bộ 25 câu hỏi học vụ thực tế: **Hit@1 đạt 68.0%**, **Hit@3 đạt 84.0%**, **MRR đạt 0.7400**.

---

## 2. Kiến trúc thư mục toàn diện (Project Directory Tree)

```text
.
├── data/                                 # QUẢN LÝ DỮ LIỆU ĐA TẦNG & CHỈ MỤC
│   ├── raw/                              # Tầng 1: Dữ liệu thô ban đầu (crawl_v2.json, crawl_v2.csv, loi_crawl.xlsx)
│   ├── processed/                        # Tầng 2: Dữ liệu đã làm sạch & sửa 529 lỗi OCR (crawl_v2_cleaned, loi_crawl_hoan_thien.xlsx)
│   ├── chunks/                           # Tầng 3: Ngữ liệu phân đoạn (clean_chunks.json, clean_chunks.csv - 496 chunks)
│   ├── vector_store/                     # Tầng 4: Cơ sở dữ liệu Vector Database cục bộ
│   │   ├── chroma_db/                    # Kho lưu trữ SQLite & HNSW Index của ChromaDB (gitignored)
│   │   └── embeddings.npy                # Bộ nhớ đệm ma trận vector 496 x 384 nạp tức thì trong 1.2s
│   ├── queries/                          # Bộ câu hỏi kiểm thử học vụ thực tế
│   │   └── tlu_academic_queries.json     # 25 câu hỏi trắc nghiệm kèm Ground Truth IDs
│   └── benchmarks/                       # Dữ liệu đo đạc thực nghiệm định lượng
│       ├── embedding_benchmark.json      # Bảng so sánh 5 embedding models & thông lượng
│       └── retrieval_benchmark.json      # Bảng đối soát 4 pipelines: Hit@1/3/5, MRR, Latency
│
├── src/                                  # MÃ NGUỒN PIPELINE THEO MÔ-ĐUN HÓA
│   ├── cleaning/                         # Phân hệ Tiền xử lý dữ liệu thô (Tuần 2)
│   │   ├── clean_crawl_data.py           # Làm sạch bài viết web, chuẩn hóa danh xưng 37 đơn vị
│   │   └── fill_loi_crawl.py             # Sửa tự động 529 lỗi OCR bằng biểu thức chính quy & từ điển
│   ├── chunking/                         # Phân hệ Phân đoạn ngữ nghĩa (Tuần 2)
│   │   └── chunking_pipeline.py          # Thuật toán Hybrid Splitting & gán 12 trường metadata
│   ├── embedding/                        # Phân hệ Vector Indexing (Tuần 3)
│   │   ├── benchmark_models.py           # Đo đạc tốc độ encode, chiều, RAM, độ tách cụm
│   │   └── build_vector_db.py            # Nạp 496 chunks, đóng gói metadata vào ChromaDB
│   ├── retrieval/                        # Phân hệ Tìm kiếm & Tái sắp xếp (Tuần 4)
│   │   ├── dense_retriever.py            # Cosine Similarity & Đa dạng hóa MMR (lambda=0.65)
│   │   ├── hybrid_retriever.py           # BM25Okapi + Dense Fusion (RRF & Weighted Score)
│   │   ├── reranker.py                   # Cross-Encoder Reranker tính tương tác token chéo
│   │   └── query_demo.py                 # Trình diễn CLI trực quan truy vấn học vụ
│   └── evaluation/                       # Phân hệ Kiểm toán & Đánh giá định lượng
│       ├── audit_and_analyze.py          # Kiểm toán chất lượng và độ dài ngữ liệu Tuần 2
│       └── evaluate_retrieval.py         # Kiểm toán đối soát 25 câu hỏi qua 4 pipelines Tuần 4
│
├── reports/                              # BÁO CÁO TIẾN ĐỘ & TÀI LIỆU HỌC THUẬT
│   ├── Bao_Cao_Tuan_3_4.html             # Báo cáo tiến độ Tuần 3-4 (Bản Academic & Sandbox tương tác)
│   ├── Bao_Cao_Thuc_Tap_Tuan_3_4.md      # Tài liệu báo cáo Markdown chi tiết Tuần 3-4
│   ├── Bao_Cao_Tuan_2_v2.html            # Báo cáo tiến độ Tuần 2 (Bản Academic Word)
│   ├── Bao_Cao_Tuan_2.html               # Báo cáo tiến độ Tuần 2 (Bản Dashboard)
│   └── Bao_Cao_Thuc_Tap_Tuan_2.md        # Tài liệu báo cáo Markdown Tuần 2
│
├── Bao_Cao_Tuan_3_4.html                 # Trang báo cáo Tuần 3-4 mở trực tiếp từ thư mục gốc
├── Bao_Cao_Tuan_2_v2.html                # Trang báo cáo Tuần 2 mở trực tiếp từ thư mục gốc
├── README.md                             # Tài liệu tổng quan kiến trúc dự án và hướng dẫn thực thi
└── .gitignore                            # Cấu hình bỏ qua bytecode, venv, chroma_db local lock
```

---

## 3. Hướng dẫn thực thi nhanh Pipeline (Quickstart)

```bash
# 1. Cài đặt các thư viện phụ thuộc
pip install chromadb rank-bm25 scikit-learn numpy pandas

# 2. Chạy Benchmark so sánh 5 mô hình Embedding (Tuần 3)
python src/embedding/benchmark_models.py

# 3. Khởi tạo và nạp 496 chunks vào ChromaDB Persistent Storage (Tuần 3)
python src/embedding/build_vector_db.py

# 4. Chạy đánh giá đối soát 25 câu hỏi thực tế qua 4 Pipelines (Tuần 4)
python src/evaluation/evaluate_retrieval.py

# 5. Thử nghiệm truy vấn học vụ tương tác dòng lệnh
python src/retrieval/query_demo.py
```

---

## 4. Bảng kết quả đối soát thực nghiệm Retrieval (Tuần 4)

Đo đạc tự động trên bộ 25 câu hỏi trắc nghiệm học vụ thực tế TLU:

| Phương pháp Retrieval | Hit Rate @ 1 | Hit Rate @ 3 | Hit Rate @ 5 | MRR | Độ trễ trung bình |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. BM25 Only** (Từ khóa thuần) | 52.0% | 64.0% | **88.0%** | 0.6333 | **4.76 ms** |
| **2. Dense Only** (Cosine thuần) | 36.0% | 48.0% | 52.0% | 0.4300 | 664.02 ms |
| **3. Hybrid RRF** (BM25 + Dense) | 44.0% | 64.0% | 76.0% | 0.5527 | 682.49 ms |
| **4. Hybrid + Cross-Encoder Rerank** | <strong style="color: green;">68.0%</strong> | <strong style="color: green;">84.0%</strong> | <strong style="color: green;">84.0%</strong> | <strong style="color: green;">0.7400</strong> | 684.76 ms |

### Nhận xét mấu chốt:
- **Dense thuần túy** gặp khó khăn khi sinh viên tra cứu mã học phần viết tắt (`TIN1012`, `NWS1403`, `7480201`) do hiện tượng làm mờ ngữ nghĩa.
- **BM25 thuần túy** bao phủ tốt (Hit@5 đạt 88%) nhưng xếp hạng Top-1 chưa tối ưu (52%).
- **Hybrid + Cross-Encoder Rerank** tạo đột phá: Nâng **Hit@1 lên 68%** (+24% tuyệt đối) và **MRR lên 0.7400** (+37.2% tương đối), **Hit@3 đạt 84.0%**.

---

## 5. Kế hoạch triển khai tiếp theo (Pha Generation — Tuần 5)

1. **Prompt Engineering & Source Citation**: Xây dựng Prompt Template ràng buộc câu trả lời phải kèm trích dẫn nguồn văn bản chính thống và liên kết URL.
2. **Tích hợp LLM Orchestrator**: Kết nối mô hình ngôn ngữ lớn (Google Gemini API / OpenAI / Local LLM) xử lý tổng hợp câu trả lời từ Top-3 chunks.
3. **Out-of-Scope Fallback**: Xây dựng bộ nhận diện câu hỏi ngoài phạm vi học vụ TLU và từ chối lịch sự.
4. **Hallucination Guardrails**: Kiểm soát tính trung thực (Faithfulness) giữa câu trả lời sinh ra và ngữ cảnh tham chiếu.
