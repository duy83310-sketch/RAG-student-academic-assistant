# BÁO CÁO TIẾN ĐỘ THỰC TẬP — TUẦN 2

* **Học phần**: Thực tập tốt nghiệp / Thực tập chuyên ngành  
* **Đề tài**: **Ứng dụng RAG hỗ trợ sinh viên tra cứu thông tin học vụ (Trường Đại học Thăng Long)**  
* **Sinh viên thực hiện**: [Họ và tên sinh viên] — MSSV: [Mã sinh viên]  
* **Người hướng dẫn (Mentor)**: [Họ và tên Giảng viên / Mentor]  
* **Thời gian thực hiện**: Tuần 2  
* **Trang Báo Cáo Web HTML (Dashboard tương tác)**: [Bao_Cao_Tuan_2.html](file:///d:/Intern/Bao_cao_tuan_2/Bao_Cao_Tuan_2.html)

---

## MỤC LỤC BÁO CÁO

1. **PHẦN 1: TỔNG QUAN TIẾN ĐỘ & BỐI CẢNH DỰ ÁN**  
   1.1. Mục tiêu đề tài & Lộ trình thực tập  
   1.2. Bảng đối soát tiến độ chuyển giao từ Tuần 1 sang Tuần 2  
2. **PHẦN 2: GIẢI QUYẾT TRIỆT ĐỂ CÁC VẤN ĐỀ TỒN ĐỌNG TỪ TUẦN 1**  
   2.1. Vấn đề 1: Dữ liệu crawl website còn thô, nhiễu và thiếu nhất quán  
   2.2. Vấn đề 2: 529 lỗi OCR từ tài liệu đào tạo PDF bị "treo" (99.2% chưa xử lý)  
   2.3. Đánh giá chất lượng tập ngữ liệu sau làm sạch (Clean Corpus)  
3. **PHẦN 3: CHIẾN LƯỢC VÀ TRIỂN KHAI PIPELINE CHUNKING**  
   3.1. Cơ sở lý thuyết: Tại sao hệ thống RAG bắt buộc phải Chunking?  
   3.2. Lựa chọn chiến lược: Phân mảnh đệ quy kết hợp cấu trúc môn học (Hybrid Splitting)  
   3.3. Thiết lập tham số: Kích thước Chunk (Chunk Size) và Độ gối đầu (Chunk Overlap)  
   3.4. Thống kê phân bố và đánh giá chất lượng 496 Chunks  
4. **PHẦN 4: THIẾT KẾ VÀ ĐÓNG GÓI METADATA CHO TRUY VẤN RAG**  
   4.1. Vai trò của Metadata trong lọc ngữ cảnh (Pre-filtering) và trích dẫn nguồn  
   4.2. Thiết kế Schema Metadata chi tiết  
   4.3. Minh họa bản ghi Chunk hoàn chỉnh kèm Metadata  
5. **PHẦN 5: NGHIÊN CỨU MỞ RỘNG VỀ CÁC PHƯƠNG PHÁP THAY THẾ**  
   5.1. So sánh 5 kỹ thuật Chunking tiên tiến (Fixed, Recursive, Semantic, Parent-Child, Late Chunking)  
   5.2. Đánh giá phản biện: Có thể bỏ RAG nếu dùng LLM ngữ cảnh triệu tokens không?  
6. **PHẦN 6: KẾT LUẬN VÀ KẾ HOẠCH TUẦN 3**  
   6.1. Đánh giá mức độ hoàn thành nhiệm vụ  
   6.2. Kế hoạch triển khai Tuần 3 (Embedding & Vector Database)  

---

## NỘI DUNG CHI TIẾT BÁO CÁO

---

### PHẦN 1: TỔNG QUAN TIẾN ĐỘ & BỐI CẢNH DỰ ÁN

#### 1.1. Mục tiêu đề tài & Lộ trình thực tập
Căn cứ theo lộ trình 8–10 tuần của **Đề tài 3 (Ứng dụng RAG hỗ trợ sinh viên tra cứu thông tin học vụ)** trong tài liệu đặc tả [YeuCauThucTap.pdf](file:///d:/Intern/YeuCauThucTap.pdf), mục tiêu cốt lõi của đề tài là xây dựng hệ thống hỏi đáp tự động giúp sinh viên tra cứu quy chế, học phí, lịch thi và chương trình đào tạo một cách chuẩn xác, có dẫn chứng nguồn chính thống.

Trong chu trình 10 tuần, **Tuần 2** đảm nhận vai trò then chốt trong Pha Indexing: chuyển hóa dữ liệu thô và tài liệu scan nhiễu thành **Bộ tài liệu sạch (Clean Corpus)**, thực hiện **Phân đoạn ngữ nghĩa (Chunking)** và **Đóng gói Siêu dữ liệu (Metadata)** chuẩn bị đưa vào Vector Database ở Tuần 3.

#### 1.2. Bảng đối soát tiến độ chuyển giao từ Tuần 1 sang Tuần 2

| Hạng mục công việc | Trạng thái kết thúc Tuần 1 | Tồn đọng chuyển giao sang Tuần 2 | Kết quả giải quyết trong Tuần 2 |
| :--- | :--- | :--- | :--- |
| **1. Dữ liệu Crawl Web** | Thu thập thô 141 bài từ website trường. | 37 tên khoa/phòng ban bị viết hoa hoặc sai chính tả; tiêu đề bị lặp 2 lần ở đầu bài viết; file CSV bị vỡ cấu trúc mảng links/tags. | **Hoàn thành 100%**: Chuẩn hóa toàn bộ, xuất bản sạch [crawl_v2_cleaned.json](file:///d:/Intern/Bao_cao_tuan_2/crawl_v2_cleaned.json) và [crawl_v2_cleaned.csv](file:///d:/Intern/Bao_cao_tuan_2/crawl_v2_cleaned.csv). |
| **2. Trích xuất OCR từ PDF** | Trích xuất OCR từ 51 file PDF CTĐT K39, phát hiện 529 lỗi. | **Tồn đọng 99.2%**: Mới sửa tay 4 dòng (STT 3–6), còn 525 dòng để trống. Nhiều mã học phần bị sai (`ECMI151`, `NWSI403`) và rác kẻ bảng (`\| \| ! !`). | **Hoàn thành 100%**: Giải quyết triệt để 529/529 lỗi bằng thuật toán, điền hoàn tất vào [loi_crawl.xlsx](file:///d:/Intern/Bao_cao_tuan_2/loi_crawl.xlsx). |
| **3. Phân mảnh (Chunking)** | Chưa triển khai. | Dữ liệu thô bài dài tới 7,838 ký tự; khung môn học bị lưu thành chuỗi JSON thô trong trường `curriculum`. | **Đã sinh 496 Chunks**: Áp dụng Hybrid Splitting (cắt đệ quy + bóc tách môn học theo năm), lưu tại [clean_chunks.json](file:///d:/Intern/Bao_cao_tuan_2/clean_chunks.json). |
| **4. Gắn Siêu dữ liệu (Metadata)** | Chưa thiết lập schema. | Thiếu siêu dữ liệu danh mục, đơn vị ban hành và link trích dẫn nguồn trên từng đoạn văn bản. | **Đóng gói 12 trường**: Đính kèm đầy đủ `chunk_id`, `category`, `department`, `date`, `source_url`. |

---

### PHẦN 2: GIẢI QUYẾT TRIỆT ĐỂ CÁC VẤN ĐỀ TỒN ĐỌNG TỪ TUẦN 1

#### 2.1. Vấn đề tồn đọng 1: Dữ liệu crawl website còn thô, nhiễu và thiếu nhất quán
* **🔴 Thực trạng đã có từ Tuần 1**:
  * Dẫn chứng trực tiếp từ file gốc [crawl_v2.json](file:///d:/Intern/Bao_cao_tuan_2/crawl_v2.json) và [crawl_v2.csv](file:///d:/Intern/Bao_cao_tuan_2/crawl_v2.csv).
  * **37 phòng ban/khoa bị lỗi danh xưng**: Bị viết hoa toàn bộ (`KHOA CÔNG NGHỆ THÔNG TIN`, `KHOA KINH TẾ QUẢN LÝ`), sai lỗi chính tả (`Viên nghiên cứu nhận thức và giáo dục...`), hoặc chứa khoảng trắng kép (`Trung tâm Khảo thí và  Đảm bảo chất lượng`).
  * **Trùng lặp tiêu đề**: Trình crawler trước đó đã bóc tách trùng lặp tiêu đề bài viết vào ngay đầu trường nội dung `content`.
  * **Vỡ cấu trúc CSV**: Các trường mảng `links`, `tags` bị serialize thành chuỗi phẳng khiến việc truy xuất liên kết bài viết bị lỗi cú pháp.
* **🟡 Cách xử lý trong Tuần 2**:
  * Lập trình script tiền xử lý [clean_crawl_data.py](file:///d:/Intern/Bao_cao_tuan_2/clean_crawl_data.py).
  * Xây dựng bảng từ điển chuẩn hóa danh xưng (`DEPT_STANDARDIZATION`) chuyển toàn bộ tên phòng ban về dạng Title Case chuẩn của Đại học Thăng Long.
  * Sử dụng biểu thức chính quy (Regex) bóc tách phần lặp tiêu đề và loại bỏ các breadcrumb thừa (`\nPhòng ban chức năng`).
  * Chuẩn hóa khoảng trắng (` `), loại bỏ khoảng trắng cuối dòng và rút gọn dòng trống liên tiếp.
* **🟢 Kết quả đạt được**:
  * Xuất bản độc lập bộ dữ liệu sạch: [crawl_v2_cleaned.json](file:///d:/Intern/Bao_cao_tuan_2/crawl_v2_cleaned.json) và [crawl_v2_cleaned.csv](file:///d:/Intern/Bao_cao_tuan_2/crawl_v2_cleaned.csv).
  * Đồng bộ 100% tên đơn vị, không còn lỗi lặp văn bản hay rác ký tự điều khiển.

* **Ví dụ minh họa Trước & Sau khi làm sạch (Bản ghi `page-co-cau-to-chuc`)**:
```diff
- [TRƯỚC]: "Cơ cấu tổ chức\nCơ cấu tổ chức|Trường Đại học Thăng Long\nTrường Đại học Thăng Long tự hào có  đội ngũ cán bộ giảng viên là các Giáo sư, Phó Giáo sư, Tiến sĩ..."
+ [SAU]  : "Trường Đại học Thăng Long tự hào có đội ngũ cán bộ giảng viên là các Giáo sư, Phó Giáo sư, Tiến sĩ, Thạc sĩ và những nhà giáo ưu tú..."
```

---

#### 2.2. Vấn đề tồn đọng 2: 529 lỗi OCR từ tài liệu đào tạo PDF bị "treo" (99.2% chưa xử lý)
* **🔴 Thực trạng đã có từ Tuần 1**:
  * Dẫn chứng từ bảng theo dõi lỗi [loi_crawl.xlsx](file:///d:/Intern/Bao_cao_tuan_2/loi_crawl.xlsx): Khi bóc tách văn bản từ 51 file PDF CTĐT K39 bằng công cụ OCR, hệ thống tự động ghi nhận 529 vị trí nghi ngờ sai lệch.
  * **Tình trạng tồn đọng nghiêm trọng**: Tuần 1 mới chỉ sửa thủ công thử nghiệm đúng **4 dòng (STT 3–6, chiếm 0.8%)**, còn lại **525 dòng bị bỏ trống hoàn toàn**!
  * **Hậu quả kỹ thuật**: 
    * 92 mã học phần bị sai (ví dụ: `ECMI151`, `NWSI403`, `PHEII0I`) khiến sinh viên tra cứu mã môn sẽ bị trả về rỗng do thuật toán tìm kiếm từ khóa BM25 không khớp chuỗi.
    * 39 dòng rác bảng (ví dụ: `P | | ! ! | | | \ |`, `Z = ! | | | | | | |`) làm sai lệch vector đặc trưng trong không gian nhúng của mô hình Embedding.
* **🟡 Cách xử lý trong Tuần 2**:
  * Lập trình công cụ tự động hóa [fill_loi_crawl.py](file:///d:/Intern/Bao_cao_tuan_2/fill_loi_crawl.py) sử dụng thư viện `openpyxl`.
  * **Thuật toán xử lý**:
    * *Nhiễu bảng (39 lỗi)*: Phân tích tỷ lệ ký tự kẻ khung (`|`, `!`, `=`, `\`) ➡️ Tự động điền nhãn `[XÓA]` theo đúng hướng dẫn.
    * *Sai mã học phần (92 lỗi)*: Nhận diện quy chuẩn mã học phần TLU (3 chữ cái + 4 số) ➡️ Tự động thay thế ký tự số bị đọc nhầm: chữ `I` và `l` thành số `1`, chữ `O` và `o` thành số `0` (ví dụ `NWSI403` ➡️ `NWS1403`, `ECMI151` ➡️ `ECM1151`, `PHEII0I` ➡️ `PHE1101`), sửa mã nhầm `IMC` ➡️ `JMC`.
    * *Sai chữ (395 lỗi)*: Tách từ dính tiếng Việt dựa trên từ điển môn học (`Quảntrịhọocđại` ➡️ `Quản trị học đại cương`, `ThưctậptốtmehiếP` ➡️ `Thực tập tốt nghiệp`), loại bỏ ký tự `đ` nhiễu tiếng Anh (`đfinance` ➡️ `finance`), xóa bỏ chuỗi ký tự rác viền bảng.
* **🟢 Kết quả đạt được**:
  * Điền hoàn tất **529/529 lỗi (100% dòng có kết quả khắc phục)** trong file [loi_crawl.xlsx](file:///d:/Intern/Bao_cao_tuan_2/loi_crawl.xlsx) và tạo bản sao lưu an toàn [loi_crawl_hoan_thien.xlsx](file:///d:/Intern/Bao_cao_tuan_2/loi_crawl_hoan_thien.xlsx).

| Nhóm lỗi phát hiện | Số lượng | Tỷ lệ | Mẫu lỗi OCR thực tế | Phương án đã khắc phục & Ghi chú |
| :--- | :---: | :---: | :--- | :--- |
| **Nhiễu bảng (dòng ký tự rời)** | 39 lỗi | 7.4% | `P \| \| ! ! \| \| \| \ \|`, `` ` = A A A \| A `` | **[XÓA]** — Xóa sạch rác đường kẻ ô |
| **Sai mã học phần** | 92 lỗi | 17.4% | `ECMI151`, `NWSI403`, `PHEII0I` | **ECM1151**, **NWS1403**, **PHE1101** (Chuẩn 3 chữ + 4 số) |
| **Sai chữ (từ dính, sai dấu)** | 395 lỗi | 74.7% | `Quảntrịhọocđại`, `đfinance`, `sơhhmmnmmmmm` | `Quản trị học đại cương`, `finance`, **[XÓA]** |
| **Sai số (lẫn chữ cái)** | 2 lỗi | 0.4% | `I2`, `I12` | **12**, **112** (Thay I thành số 1) |
| **Sai ngày tháng** | 1 lỗi | 0.2% | `05/0/2027` | **05/07/2027** (Chuẩn hóa dd/mm/yyyy theo hướng dẫn) |

---

### PHẦN 3: CHIẾN LƯỢC VÀ TRIỂN KHAI PIPELINE CHUNKING

#### 3.1. Cơ sở lý thuyết: Tại sao hệ thống RAG bắt buộc phải Chunking?
1. **Rào cản giới hạn Context của Embedding Model**: Các mô hình nhúng hiện đại chỉ nhận tối đa 512–8192 tokens. Việc cố nhồi nhét tài liệu dài vượt ngưỡng sẽ dẫn đến việc văn bản bị cắt cụt (truncation), làm mất thông tin quan trọng phía sau.
2. **Hiện tượng pha loãng ngữ nghĩa (Semantic Dilution)**: Nếu biểu diễn cả một văn bản quy chế dài 20 trang thành một vector duy nhất 768 chiều, ý nghĩa chi tiết của từng điều khoản sẽ bị triệt tiêu lẫn nhau trong phép trung bình hóa toán học, khiến độ tương đồng Cosine giữa câu hỏi ngắn của sinh viên và tài liệu bị giảm sút nghiêm trọng.
3. **Hiện tượng "Lost in the Middle" của LLM**: Khi đưa toàn bộ văn bản dài vào Prompt, mô hình ngôn ngữ lớn có xu hướng chỉ chú ý vào đầu và cuối ngữ cảnh, bỏ qua chi tiết quan trọng nằm ở giữa. Chunking giúp LLM nhận đúng đoạn văn trọng tâm chứa câu trả lời.

#### 3.2. Lựa chọn chiến lược: Phân mảnh đệ quy kết hợp cấu trúc môn học (Hybrid Splitting)
Dữ liệu học vụ của Đại học Thăng Long có 2 nhóm văn bản đặc thù:
* **Nhóm 1: Văn bản thông báo, quy chế, giới thiệu phòng ban**: Áp dụng thuật toán **Recursive Character Text Splitting**. Thuật toán ưu tiên chia nhỏ văn bản theo các ranh giới tự nhiên theo thứ tự: Ngắt đoạn đôi (`\n\n`) ➡️ Ngắt dòng đơn (`\n`) ➡️ Dấu chấm hết câu (`. `) ➡️ Dấu cách từ (` `). Điều này giữ cho các câu không bị cắt cụt giữa chừng.
* **Nhóm 2: Chương trình đào tạo chuyên ngành**: Bóc tách trường `curriculum` dạng JSON để tạo các chunk chuyên biệt theo từng **Năm học** và **Khối kiến thức** (Môn học cơ sở, Môn chuyên ngành, Môn tự chọn). Cách làm này giúp câu trả lời của Chatbot khi sinh viên hỏi về khung chương trình năm 1, năm 2 đạt độ chính xác tối đa.

#### 3.3. Thiết lập tham số: Kích thước Chunk và Độ gối đầu
* **Kích thước đoạn đích (Target Chunk Size)**: `600–700 ký tự` (~120–150 từ). Đây là kích thước tối ưu, đủ lớn để chứa trọn vẹn một điều khoản quy chế hoặc một khối danh sách môn học, nhưng đủ nhỏ để mô hình Embedding bắt trọn vẹn ngữ nghĩa.
* **Độ gối đầu (Chunk Overlap)**: `120 ký tự` (~15–20% kích thước chunk). Mục đích nhằm bảo toàn tính liên tục của ngữ cảnh; câu kết của đoạn trước sẽ xuất hiện ở đầu đoạn sau, tránh trường hợp một câu bị cắt đôi ở đường biên phân mảnh.

#### 3.4. Thống kê phân bố và đánh giá chất lượng 496 Chunks
Pipeline [chunking_pipeline.py](file:///d:/Intern/Bao_cao_tuan_2/chunking_pipeline.py) đã sinh ra tập dữ liệu [clean_chunks.json](file:///d:/Intern/Bao_cao_tuan_2/clean_chunks.json) với các thông số phân bố:
* Số lượng: **496 chunks** từ 141 tài liệu sạch ban đầu.
* Độ dài ký tự: Trung bình **447.6 ký tự**; Trung vị **436.0 ký tự**; Nhỏ nhất 58 ký tự; Lớn nhất 819 ký tự.
* Phân bổ theo chủ đề: Chương trình đào tạo (388 chunks), Quy chế đào tạo (22 chunks), Lịch thi (21 chunks), Học phí (20 chunks), Chức năng đơn vị (17 chunks), Kế hoạch đào tạo (10 chunks), Thông tin liên lạc (9 chunks), Thời khóa biểu (5 chunks), Thông tin sinh viên (4 chunks).

---

### PHẦN 4: THIẾT KẾ VÀ ĐÓNG GÓI METADATA CHO TRUY VẤN RAG

#### 4.1. Vai trò của Metadata trong lọc ngữ cảnh và trích dẫn nguồn
1. **Lọc trước truy vấn (Metadata Pre-filtering)**:
   * Khi sinh viên hỏi: *"Quy định đóng học phí muộn học kỳ này như thế nào?"*, hệ thống có thể kết hợp bộ lọc Metadata `category == 'hoc_phi'` trước khi thực hiện tìm kiếm vector. Việc này thu hẹp phạm vi tìm kiếm, loại bỏ 95% tài liệu không liên quan, tăng tốc độ truy vấn và ngăn chặn triệt để hiện tượng lấy nhầm thông tin lịch thi.
2. **Minh bạch thông tin & Trích dẫn nguồn (Source Grounding)**:
   * Metadata cho phép câu trả lời của Chatbot tự động hiển thị link trích dẫn: *"Nguồn: Cổng thông tin Đào tạo - [Quyết định số 2234](url) - Ban hành ngày 26/06/2026"*. Điều này triệt tiêu tình trạng sinh viên nghi ngờ thông tin của AI.
3. **Xác thực thời gian (Temporal Validity)**:
   * Giúp hệ thống phân biệt và ưu tiên các thông báo học vụ còn hiệu lực trong năm học hiện tại (2026) so với các quy định cũ.

#### 4.2. Thiết kế Schema Metadata chi tiết
Mỗi chunk trong [clean_chunks.json](file:///d:/Intern/Bao_cao_tuan_2/clean_chunks.json) đều được gán nhãn siêu dữ liệu đầy đủ:

| Trường Metadata | Kiểu dữ liệu | Mục đích sử dụng trong Pipeline RAG |
| :--- | :---: | :--- |
| `chunk_id` | String | Khóa chính duy nhất định danh chunk (ví dụ `tb-2234_c001`) |
| `doc_id` | String | Mã định danh văn bản gốc, hỗ trợ gom nhóm lại tài liệu cha |
| `chunk_index` / `total_chunks` | Integer | Vị trí thứ tự của chunk trong bài viết gốc |
| `section` | String | Phân mục chi tiết (ví dụ: *Năm 1 - Môn học cơ sở* hoặc *Toàn văn*) |
| `title` | String | Tiêu đề văn bản/thông báo học vụ |
| `category` | String | Danh mục học vụ phục vụ Metadata Filtering (`hoc_phi`, `lich_thi`,...) |
| `content_type` | String | Loại văn bản (`announcement`, `major`, `unit`, `page`) |
| `department` | String | Tên phòng ban/khoa ban hành đã chuẩn hóa |
| `date` | String | Ngày văn bản có hiệu lực (`YYYY-MM-DD`) |
| `source_url` | String | Đường dẫn liên kết nguồn bài viết trên website trường |
| `char_length` / `word_count` | Integer | Độ dài văn bản phục vụ thống kê và quản lý chi phí token |

#### 4.3. Minh họa bản ghi Chunk hoàn chỉnh kèm Metadata
```json
{
  "chunk_id": "nganh-cong-nghe-thong-tin_c002",
  "doc_id": "nganh-cong-nghe-thong-tin",
  "chunk_index": 2,
  "total_chunks_in_doc": 5,
  "section": "Năm 1 - Môn học cơ sở",
  "title": "Ngành Công nghệ thông tin",
  "category": "chuong_trinh_dao_tao",
  "content_type": "major",
  "department": "Khoa Công nghệ thông tin",
  "date": "2026-06-26",
  "source_url": "https://thanglong.edu.vn/nganh-hoc/cong-nghe-thong-tin",
  "char_length": 482,
  "word_count": 94,
  "text": "Chương trình đào tạo ngành: Ngành Công nghệ thông tin\nGiai đoạn: Năm 1\nNhóm môn: Môn học cơ sở\nDanh sách môn học (9 môn): Giải tích, Đại số tuyến tính, Xác suất thống kê, Lập trình cơ bản, Lập trình hướng đối tượng, Toán rời rạc, Cấu trúc dữ liệu và giải thuật, Cơ sở dữ liệu, Tiếng Anh chuyên ngành."
}
```

---

### PHẦN 5: NGHIÊN CỨU MỞ RỘNG VỀ CÁC PHƯƠNG PHÁP THAY THẾ

#### 5.1. So sánh các kỹ thuật Chunking tiên tiến
Ngoài phương pháp Recursive Splitting đã triển khai, trong nghiên cứu thực nghiệm có các lựa chọn thay thế sau:

1. **Semantic Chunking (Cắt theo độ biến thiên ngữ nghĩa)**:
   * *Nguyên lý*: Nhúng từng câu đơn thành vector và tính khoảng cách Cosine giữa hai câu liên tiếp. Nếu khoảng cách vượt ngưỡng cho phép, thuật toán sẽ thực hiện ngắt chunk.
   * *Đánh giá*: Rất tốt cho văn xuôi, bài viết luận; tuy nhiên với dữ liệu bảng biểu học vụ và danh sách môn học, phương pháp này tốn thêm chi phí nhúng ban đầu và dễ ngắt vụn danh sách.
2. **Parent-Child Chunking (Phân mảnh phân cấp Cha - Con)**:
   * *Nguyên lý*: Chia thành các Child Chunk nhỏ (100 tokens) để nhúng vector và tìm kiếm chính xác, nhưng khi tìm thấy sẽ trả về Parent Chunk lớn (800 tokens) chứa toàn bộ đoạn văn bản xung quanh cho LLM.
   * *Đánh giá*: Đây là phương án rất tiềm năng để nâng cấp hệ thống ở các tuần sau nhằm cung cấp ngữ cảnh rộng hơn cho LLM.
3. **Late Chunking (Kỹ thuật mới từ Jina AI - 2024)**:
   * *Nguyên lý*: Nạp toàn bộ tài liệu dài qua mô hình Transformer để các từ ở đầu và cuối văn bản giao tiếp ngữ cảnh thông qua cơ chế Self-Attention, sau đó mới gom vector trung bình theo từng đoạn chunk.
   * *Đánh giá*: Khắc phục hiện tượng mất liên kết ngữ cảnh giữa các đoạn cắt, nhưng đòi hỏi mô hình embedding chuyên dụng hỗ trợ context dài.

#### 5.2. Đánh giá phương án dùng LLM ngữ cảnh triệu tokens thay thế RAG
Hiện nay các mô hình như Gemini 1.5 Pro hỗ trợ ngữ cảnh từ 1–2 triệu tokens. Tuy nhiên, việc thay thế hoàn toàn RAG bằng cách nhồi toàn bộ tài liệu vào prompt không khả thi trong môi trường thực tế vì:
* **Chi phí quá đắt**: Mỗi câu hỏi của sinh viên lại phải xử lý lại hàng triệu tokens dữ liệu toàn trường.
* **Độ trễ phản hồi lớn**: Xử lý ngữ cảnh triệu tokens mất từ 30–60 giây, không thể đáp ứng trải nghiệm chatbot tra cứu tức thì của sinh viên.
* **Hiện tượng bỏ sót**: Vẫn có xác suất mô hình bỏ qua một chi tiết nhỏ (ví dụ số hiệu phòng học, giờ thi) nằm lọt thỏm giữa hàng nghìn trang văn bản.
* 👉 **Kết luận**: Pipeline **RAG truyền thống kết hợp Chunking & Metadata** vẫn là giải pháp chuẩn mực, cân bằng tối ưu giữa độ chính xác, tốc độ phản hồi và chi phí vận hành.

---

### PHẦN 6: KẾT LUẬN VÀ KẾ HOẠCH TUẦN 3

#### 6.1. Đánh giá mức độ hoàn thành nhiệm vụ Tuần 2
* Đã hoàn thành **100% khối lượng công việc** theo kế hoạch Tuần 2:
  * [x] Làm sạch và chuẩn hóa toàn bộ dữ liệu crawl website trường.
  * [x] Khắc phục triệt để 529 lỗi OCR trong các tài liệu chương trình đào tạo.
  * [x] Xây dựng và thực thi thành công pipeline Chunking đệ quy và cấu trúc môn học.
  * [x] Đóng gói hoàn tất tập ngữ liệu sạch gồm 496 chunks kèm đầy đủ siêu dữ liệu.

#### 6.2. Kế hoạch triển khai Tuần 3 (Embedding & Vector Database)
Căn cứ theo mục tiêu của Tuần 3, các nhiệm vụ trọng tâm tiếp theo bao gồm:
1. **Lựa chọn mô hình Embedding tiếng Việt**:
   * Tiến hành benchmark thực nghiệm so sánh chất lượng giữa: `BAAI/bge-m3` (đa ngôn ngữ, hỗ trợ cả Dense và Sparse), `intfloat/multilingual-e5-large`, và mô hình chuyên tiếng Việt `bkai-foundation-models/vietnamese-bi-encoder`.
2. **Khởi tạo và cấu hình Vector Database**:
   * Thiết lập `ChromaDB` (chạy cục bộ) hoặc `FAISS` để lưu trữ 496 vector chunks kèm metadata.
   * Đánh giá thời gian nhúng và dung lượng lưu trữ index vector.
3. **Thử nghiệm bước đầu về Truy xuất (Retrieval)**:
   * Viết script truy vấn thử nghiệm với 10 câu hỏi học vụ phổ biến của sinh viên (về học phí, điều kiện tốt nghiệp, khung môn học ngành CNTT) và đo đạc độ tương đồng Cosine Similarity.
