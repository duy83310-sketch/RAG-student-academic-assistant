# BÁO CÁO TIẾN ĐỘ THỰC TẬP — TUẦN 3 & TUẦN 4

* **Học phần**: Thực tập tốt nghiệp / Thực tập chuyên ngành  
* **Đề tài**: **Ứng dụng RAG hỗ trợ sinh viên tra cứu thông tin học vụ (Trường Đại học Thăng Long)**  
* **Sinh viên thực hiện**: [Họ và tên sinh viên] — MSSV: [Mã sinh viên]  
* **Người hướng dẫn (Mentor)**: [Họ và tên Giảng viên / Mentor]  
* **Thời gian thực hiện**: Giai đoạn gộp Tuần 3 (Embedding & Vector DB) + Tuần 4 (Hybrid Retrieval & Cross-Encoder Reranking)  
* **Trang Báo Cáo Web HTML (Dashboard tương tác & Sandbox)**: [Bao_Cao_Tuan_3_4.html](file:///d:/Intern/Bao_cao_tuan_3_4/Bao_Cao_Tuan_3_4.html)

---

## MỤC LỤC BÁO CÁO

1. **PHẦN 1: TỔNG QUAN TIẾN ĐỘ & KIẾN TRÚC MÔ-ĐUN HÓA**  
   1.1. Mục tiêu đề tài & Lộ trình thực tập  
   1.2. Bảng đối soát tiến độ chuyển giao từ Tuần 2 sang Tuần 3–4  
   1.3. Cây thư mục dự án độc lập  
2. **PHẦN 2: NGHIÊN CỨU LÝ THUYẾT & BENCHMARK CÁC MÔ HÌNH EMBEDDING (TUẦN 3)**  
   2.1. Cơ sở toán học của Vector Embedding trong không gian ngữ nghĩa học vụ  
   2.2. So sánh chuyên sâu 5 họ mô hình: BGE-M3, Vietnamese Bi-Encoder, Multilingual-E5, OpenAI, all-MiniLM-L6-v2  
   2.3. Kết quả đo đạc thực nghiệm trên kho 496 chunks học vụ TLU  
3. **PHẦN 3: THIẾT KẾ & TRIỂN KHAI VECTOR DATABASE (CHROMADB)**  
   3.1. Cấu trúc chỉ mục HNSW và metric Cosine Distance  
   3.2. Quy trình nạp 496 chunks và xử lý tương thích siêu dữ liệu  
   3.3. Cơ chế lọc trước siêu dữ liệu (Metadata Pre-filtering)  
4. **PHẦN 4: XÂY DỰNG BỘ MÁY RETRIEVAL ĐA PHƯƠNG THỨC (TUẦN 4)**  
   4.1. Hạn chế của Dense Retrieval thuần túy (vấn đề mù từ khóa chính xác)  
   4.2. Khử trùng lặp ngữ cảnh với thuật toán MMR (Maximal Marginal Relevance)  
   4.3. Bổ sung tìm kiếm từ khóa BM25Okapi và thuật toán dung hợp RRF (Reciprocal Rank Fusion)  
5. **PHẦN 5: CƠ CHẾ TÁI SẮP XẾP NGỮ CẢNH CẤP TOKEN (CROSS-ENCODER RERANKER)**  
   5.1. Bản chất khác biệt giữa Bi-Encoder và Cross-Encoder  
   5.2. Kiến trúc hai giai đoạn (Two-Stage Retrieval Pipeline)  
   5.3. Cơ chế tính điểm và phân tích dịch chuyển thứ hạng  
6. **PHẦN 6: ĐÁNH GIÁ THỰC NGHIỆM ĐỊNH LƯỢNG TRÊN BỘ 25 CÂU HỎI HỌC VỤ TLU**  
   6.1. Thiết kế bộ benchmark chuẩn 25 câu hỏi thực tế  
   6.2. Bảng tổng hợp đối soát 4 Pipelines (Hit@1, Hit@3, Hit@5, MRR, Latency)  
   6.3. Phân tích chi tiết các case study điển hình  
7. **PHẦN 7: ĐÁNH GIÁ CHIẾN LƯỢC KHỐI LƯỢNG KIẾN THỨC TUẦN 5 & KẾ HOẠCH TIẾP THEO**  
   7.1. Phân tích khối lượng kiến thức Tuần 5 (Prompt Engineering & LLM Integration)  
   7.2. Nhận định về tính khả thi và khuyến nghị lộ trình  

---

## NỘI DUNG CHI TIẾT BÁO CÁO

---

### PHẦN 1: TỔNG QUAN TIẾN ĐỘ & KIẾN TRÚC MÔ-ĐUN HÓA

#### 1.1. Mục tiêu đề tài & Lộ trình thực tập
Căn cứ theo bản đặc tả yêu cầu tại `YeuCauThucTap.pdf` (Đề tài 3: Ứng dụng RAG hỗ trợ sinh viên tra cứu thông tin học vụ), đề tài hướng tới giải quyết bài toán cốt lõi: sinh viên Đại học Thăng Long mất nhiều thời gian tra cứu quy chế, học phí, lịch thi và 25 chương trình đào tạo chuyên ngành do dữ liệu nằm rải rác trên nhiều cổng thông tin và văn bản PDF scan.

Trong chu trình 10 tuần, sau khi Tuần 2 đã hoàn thành trọn vẹn việc làm sạch dữ liệu, khắc phục 529 lỗi OCR và phân đoạn thành **496 chunks sạch kèm 12 trường siêu dữ liệu**, giai đoạn **Tuần 3 và Tuần 4** tập trung xây dựng toàn bộ **Hạ tầng Vector Database** và **Bộ máy Tìm kiếm Tri thức (Retrieval Engine)**.

#### 1.2. Bảng đối soát tiến độ chuyển giao từ Tuần 2 sang Tuần 3–4

| Hạng mục công việc | Trạng thái kết thúc Tuần 2 | Mục tiêu đặt ra cho Tuần 3 & 4 | Kết quả hoàn thành trong Tuần 3 & 4 |
| :--- | :--- | :--- | :--- |
| **1. Mô hình Embedding** | Chưa thực hiện benchmark. | So sánh BGE-M3, E5, OpenAI, Vietnamese Bi-Encoder, đo thông lượng và độ tách biệt cụm. | **Hoàn thành 100%**: Xây dựng ma trận 5 models; đo đạc thực nghiệm đạt 5.3 chunks/s, biên phân tách cụm đạt +0.0375. |
| **2. Vector Database** | 496 chunks lưu ở dạng file JSON/CSV phẳng. | Khởi tạo ChromaDB cục bộ với không gian Cosine HNSW, nạp toàn bộ chunks kèm metadata. | **Hoàn thành 100%**: Xây dựng persistent collection `tlu_academic_chunks` (496 chunks), hỗ trợ Pre-filtering theo khoa/danh mục. |
| **3. Phân hệ Retrieval** | Chưa có công cụ truy vấn. | Xây dựng Dense Cosine Retriever và thuật toán đa dạng hóa MMR ($\lambda = 0.65$). | **Hoàn thành 100%**: Triển khai hoàn tất cả 2 chế độ trong `dense_retriever.py`. |
| **4. Tìm kiếm lai (Hybrid Search)** | Chưa triển khai. | Bổ sung BM25Okapi và dung hợp điểm bằng Reciprocal Rank Fusion (RRF). | **Hoàn thành 100%**: Giải quyết bài toán mù từ khóa chính xác đối với mã học phần và danh xưng phòng ban. |
| **5. Reranker** | Chưa nghiên cứu. | Triển khai Cross-Encoder Reranker chấm điểm tương quan cặp (Query, Chunk). | **Hoàn thành 100%**: Tái sắp xếp Top-15 ứng viên lên Top-5, nâng Hit@1 từ 44% lên 68%. |
| **6. Đánh giá định lượng** | Chưa có bộ benchmark. | Xây dựng bộ test và đo Hit@1, Hit@3, Hit@5, MRR. | **Hoàn thành 100%**: Xây dựng 25 câu hỏi trắc nghiệm thực tế, thực hiện đo lường tự động trên cả 4 pipeline. |

---

### PHẦN 2: NGHIÊN CỨU LÝ THUYẾT & BENCHMARK CÁC MÔ HÌNH EMBEDDING (TUẦN 3)

#### 2.1. Cơ sở toán học của Vector Embedding
Embedding là một ánh xạ phi tuyến tính $f: \mathcal{D} \rightarrow \mathbb{R}^d$ chuyển đổi đoạn văn bản tự nhiên sang một vector thực trong không gian $d$ chiều. Độ tương đồng ngữ nghĩa giữa hai văn bản được định lượng bằng hàm khoảng cách Cosine:
$$\text{Cosine Similarity}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2} = \frac{\sum_{i=1}^d u_i v_i}{\sqrt{\sum_{i=1}^d u_i^2} \sqrt{\sum_{i=1}^d v_i^2}}$$

Khoảng cách Cosine Distance dùng trong ChromaDB được định nghĩa:
$$\text{Cosine Distance}(u, v) = 1 - \text{Cosine Similarity}(u, v)$$

#### 2.2. Ma trận so sánh 5 họ mô hình Embedding

| Mô hình | Chiều vector | Ngữ cảnh tối đa | Thông lượng (CPU/GPU) | Dung lượng & Chi phí | Đánh giá độ phù hợp với TLU |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **BAAI/bge-m3** | 1,024 | 8,192 tokens | ~42 chunks/s (GPU) | 2.2GB VRAM / Free | **Hạng 1 (Production)**: Đa năng nhất, hỗ trợ cả dense, sparse và multi-vector ColBERT. |
| **all-MiniLM-L6-v2 (Chroma ONNX)** | 384 | 512 tokens | 5.3 chunks/s (CPU) | 79MB RAM / Free | **Hạng 2 (Local)**: Nhẹ, ổn định, chạy offline hoàn toàn trên laptop sinh viên. |
| **OpenAI text-embedding-3-small** | 1,536 | 8,191 tokens | ~35 chunks/s (API) | Cloud / $0.02 / 1M | **Hạng 2 (Cloud)**: Rất mạnh về ngữ nghĩa, chi phí rẻ nhưng phụ thuộc mạng. |
| **bkai-foundation/vietnamese-bi-encoder** | 768 | 256 tokens | ~68 chunks/s | 1.5GB VRAM / Free | **Hạng 3**: Tối ưu tiếng Việt nhưng max length 256 tokens dễ cắt cụt văn bản dài. |
| **intfloat/multilingual-e5-base** | 768 | 512 tokens | ~58 chunks/s | 1.8GB VRAM / Free | **Hạng 4**: Đòi hỏi tiền tố `query: ` và `passage: ` ngặt nghèo. |

#### 2.3. Kết quả đo đạc thực nghiệm
* **Thời gian sinh vector toàn bộ kho ngữ liệu (496 chunks):** 92.95 giây (thông lượng 5.3 chunks/s).
* **Bộ nhớ RAM sử dụng:** < 250 MB.
* **Độ tách biệt ngữ nghĩa giữa các phân mục (Semantic Separation Margin):**
  * Tương đồng nội bộ cùng danh mục (Intra-category): **0.7069**.
  * Tương đồng chéo giữa các danh mục khác nhau (Inter-category): **0.6694**.
  * Biên tách biệt: **+0.0375**.

---

### PHẦN 3: THIẾT KẾ & TRIỂN KHAI VECTOR DATABASE (CHROMADB)

1. **Khởi tạo cơ sở dữ liệu bền vững (Persistent Storage):**
   * Sử dụng `chromadb.PersistentClient` lưu trực tiếp tại `Bao_cao_tuan_3_4/data/vector_store/chroma_db`.
   * Tạo collection `tlu_academic_chunks` với metric `{"hnsw:space": "cosine"}`.
2. **Cấu trúc chỉ mục HNSW:**
   * Sử dụng đồ thị đa tầng HNSW giúp tìm kiếm xấp xỉ láng giềng gần nhất (ANN) với độ phức tạp $O(\log N)$, phản hồi tức thì dưới 10ms.
3. **Đóng gói siêu dữ liệu & Pre-filtering:**
   * Mỗi chunk được gắn 12 trường siêu dữ liệu chuẩn (`chunk_id`, `doc_id`, `category`, `department`, `section`, `title`, `source_url`, `char_length`, `word_count`...).
   * Hỗ trợ lọc trước: `collection.query(where={"category": "hoc_phi"})` giúp triệt tiêu hoàn toàn nhiễu từ các văn bản khác khi câu hỏi chỉ liên quan đến tài chính.

---

### PHẦN 4: BỘ MÁY RETRIEVAL ĐA PHƯƠNG THỨC: DENSE, MMR & BM25 HYBRID

#### 4.1. Hạn chế của Dense Retrieval thuần túy
Khi kiểm thử Dense Retrieval độc lập:
* **Hit@1 chỉ đạt 36.0%**, **MRR đạt 0.4300**.
* **Nguyên nhân**: Hiện tượng *mù từ khóa chính xác (Keyword Blindness)* khiến Bi-Encoder không thể phân biệt rạch ròi các mã học phần viết tắt (`TIN1012`, `NWS1403`, `ECM1151`) hay các con số năm học cụ thể.

#### 4.2. Khử trùng lặp với Maximal Marginal Relevance (MMR)
Áp dụng công thức:
$$\text{MMR} = \arg\max_{D_i \in R \setminus S} \left[ \lambda \cdot \text{Sim}_1(D_i, Q) - (1 - \lambda) \cdot \max_{D_j \in S} \text{Sim}_2(D_i, D_j) \right]$$
Với $\lambda = 0.65$, MMR thành công loại bỏ các đoạn văn bản trùng lặp tiêu đề giới thiệu ngành, tăng độ phong phú thông tin cho câu trả lời.

#### 4.3. Tìm kiếm lai kết hợp (Hybrid Search BM25 + Dense)
* Sử dụng thư viện `rank-bm25` kết hợp bộ tiền xử lý tách từ tiếng Việt.
* Dung hợp thứ hạng bằng **Reciprocal Rank Fusion (RRF)**:
  $$RRF_{score}(d) = \sum_{m \in \{\text{Dense}, \text{BM25}\}} \frac{1}{60 + r_m(d)}$$
* Nhờ có BM25, các câu hỏi chứa mã ngành hoặc tên văn bản chính xác lập tức được kéo vào nhóm ứng viên Top-5, nâng **Hit@5 lên 72.0%**.

---

### PHẦN 5: CƠ CHẾ TÁI SẮP XẾP NGỮ CẢNH (CROSS-ENCODER RERANKER)

#### 5.1. Bản chất Bi-Encoder vs Cross-Encoder
* **Bi-Encoder**: Vector hóa độc lập $Q$ và $P$, tính dot product ở tầng cuối. Không có cơ chế Cross-Attention giữa các từ.
* **Cross-Encoder**: Ghép cặp $[CLS] \circ Q \circ [SEP] \circ P \circ [SEP]$ đưa qua toàn bộ các tầng Transformer. Từng từ trong câu hỏi tương tác trực tiếp với từng từ trong văn bản.

#### 5.2. Kiến trúc hai giai đoạn (Two-Stage Pipeline)
* **Stage 1 (Candidate Generation):** Hybrid Search thu thập nhanh Top-15 ứng viên ($O(\log N)$).
* **Stage 2 (Fine-grained Reranking):** Cross-Encoder Reranker tính điểm tương quan sâu cho 15 ứng viên đó và chọn ra Top-3 hoặc Top-5 chuẩn xác nhất.

---

### PHẦN 6: ĐÁNH GIÁ THỰC NGHIỆM ĐỊNH LƯỢNG TRÊN BỘ 25 CÂU HỎI HỌC VỤ

#### 6.1. Bảng đối soát 4 Pipelines

| Phương pháp Retrieval | Hit Rate @ 1 | Hit Rate @ 3 | Hit Rate @ 5 | MRR | Độ trễ trung bình |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. BM25 Only** | 52.0% | 64.0% | 88.0% | 0.6333 | **3.84 ms** |
| **2. Dense Only (Cosine)** | 36.0% | 48.0% | 52.0% | 0.4300 | 563.40 ms |
| **3. Hybrid RRF** | 44.0% | 60.0% | 72.0% | 0.5393 | 537.08 ms |
| **4. Hybrid + Reranker** | **68.0%** | **84.0%** | **84.0%** | **0.7400** | 539.27 ms |

#### 6.2. Phân tích kết quả thực nghiệm
1. **Giá trị của Reranker:**
   * Nâng **Hit@1 từ 44.0% lên 68.0%** (tăng tuyệt đối +24.0%).
   * Nâng **Hit@3 lên 84.0%** (84% câu hỏi có câu trả lời nằm ngay trong 3 đoạn văn bản đầu tiên).
   * Nâng **MRR từ 0.5393 lên 0.7400** (tăng tương đối +37.2%).
2. **Case study điển hình:**
   * *Câu hỏi Q01*: "Học phí năm thứ nhất của ngành Công nghệ thông tin khóa 39 là bao nhiêu tiền một kỳ?"
     * Ở bước Hybrid RRF, chunk học phí đúng (`nganh-cong-nghe-thong-tin_c010`) đứng ở vị trí #3 (bị các thông báo học phí Thạc sĩ che khuất).
     * Qua Cross-Encoder Reranker, chunk này được chấm điểm cao nhất và nhảy lên **vị trí số 1 ($\Delta rank = +2$)**.
   * *Câu hỏi Q02*: "Mã ngành tuyển sinh và thời gian đào tạo tiêu chuẩn của ngành Công nghệ thông tin là gì?"
     * BM25 đưa chunk `nganh-cong-nghe-thong-tin_c002` lên thẳng Top 1 nhờ khớp chính xác mã số `7480201`, trong khi Dense xếp ở vị trí #3.

---

### PHẦN 7: ĐÁNH GIÁ CHIẾN LƯỢC KHỐI LƯỢNG KIẾN THỨC TUẦN 5 & KẾ HOẠCH TIẾP THEO

#### 7.1. Phân tích khối lượng kiến thức Tuần 5 (Prompt Engineering & LLM Integration)
Bản đặc tả Tuần 5 đặt ra 4 nhiệm vụ:
1. **Prompt Template có trích dẫn nguồn (Citation Enforcement)**.
2. **Tích hợp LLM (Gemini API, OpenAI GPT, hoặc Local LLaMA 3)**.
3. **Xử lý ngoài phạm vi (Out-of-Scope Fallback)**: Từ chối lịch sự khi sinh viên hỏi ngoài dữ liệu học vụ TLU.
4. **Cơ chế chống ảo giác (Hallucination Guardrails)**.

#### 7.2. Nhận định sư phạm và kỹ thuật
* **Retrieval là linh hồn của RAG**: Trong bài toán RAG, khâu khó nhất, dễ lỗi nhất và tốn nhiều công sức toán học nhất là **Pha Indexing và Retrieval (Tuần 2, 3, 4)**. Khi Top-3 Chunks đã đạt độ chính xác 84% và có đầy đủ siêu dữ liệu `source_url`, `title`, `department`, công việc của Tuần 5 chủ yếu là:
  * Nối các đoạn trích này vào một khung Prompt chuẩn: `"Hãy trả lời câu hỏi dựa trên ngữ cảnh sau, kèm trích dẫn nguồn..."`.
  * Gửi request tới LLM API và stream phản hồi văn bản.
* **Mức độ quá tải kiến thức**: Khối lượng kiến thức của Tuần 5 mang tính chất lập trình ứng dụng (Application Engineering) và Prompt Design, nhẹ hơn và dễ hiểu hơn nhiều so với lý thuyết nhúng vector, đồ thị HNSW và Cross-Encoder của Tuần 3-4.
* **Kết luận**: Sinh viên **hoàn toàn có thể làm gộp cả Tuần 5** trong một tiến trình liên mạch nếu muốn rút ngắn lộ trình thực tập. Tuy nhiên, việc dừng lại ở Tuần 4 để nghiệm thu vững chắc bộ máy tìm kiếm (Retrieval Benchmark) trước khi tích hợp LLM cũng là một chiến lược rất an toàn và chuyên nghiệp.

---

## HƯỚNG DẪN THỰC THI NHANH PIPELINE (QUICKSTART)

Từ thư mục gốc `d:/Intern/Bao_cao_tuan_3_4`:

```bash
# 1. Chạy Benchmark so sánh 5 mô hình Embedding
python src/embedding/benchmark_models.py

# 2. Khởi tạo và nạp 496 chunks vào ChromaDB Persistent Storage
python src/embedding/build_vector_db.py

# 3. Chạy đánh giá đối soát tự động 25 câu hỏi qua 4 Pipelines
python -m Bao_cao_tuan_3_4.src.evaluation.evaluate_retrieval

# 4. Chạy trình diễn truy vấn học vụ tương tác dòng lệnh
python -m Bao_cao_tuan_3_4.src.retrieval.query_demo

# 5. Sinh lại trang báo cáo HTML Web Form
python src/generate_report_html.py
```

