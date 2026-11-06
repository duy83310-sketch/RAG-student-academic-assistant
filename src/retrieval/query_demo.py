import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.reranker import CrossEncoderReranker

def run_interactive_demo():
    print("="*75)
    print("  HỆ THỐNG TRUY VẤN HỌC VỤ RAG THĂNG LONG (TUẦN 3 & TUẦN 4)")
    print("  Kiến trúc: Hybrid Retrieval (BM25 + Chroma Dense) + Cross-Encoder Rerank")
    print("="*75)

    hybrid_retriever = HybridRetriever()
    reranker = CrossEncoderReranker()

    sample_queries = [
        "Học phí năm thứ nhất của ngành Công nghệ thông tin khóa 39 là bao nhiêu?",
        "Lịch thi chính thức TOEIC chuẩn đầu ra nội bộ tháng 6 năm 2026",
        "Chức năng và nhiệm vụ chính của Phòng Đào tạo?",
        "Thời khóa biểu khóa 39 và danh sách các lớp bị hủy học kỳ 1"
    ]

    print("\n--- CÂU HỎI MẪU THỬ NGHIỆM ---")
    for idx, q in enumerate(sample_queries):
        print(f"[{idx+1}] {q}")

    test_q = sample_queries[0]
    print(f"\nTruy vấn đang thử nghiệm: '{test_q}'")

    print("\n[Bước 1] Thu thập ứng viên bằng Hybrid Search (Top 10)...")
    hybrid_cands = hybrid_retriever.search_hybrid(test_q, top_k=10, fusion_mode="rrf")
    for i, c in enumerate(hybrid_cands[:5]):
        print(f"  Ứng viên #{i+1}: [{c['chunk_id']}] RRF Score: {c['final_score']:.5f} | Sources: {c['sources']} | {c['metadata']['title']}")

    print("\n[Bước 2] Tái sắp xếp ứng viên bằng Cross-Encoder Reranker...")
    reranked = reranker.rerank(test_q, hybrid_cands, top_k=3)
    
    print("\n" + "-"*75)
    print("KẾT QUẢ TOP 3 ĐƯỢC CHỌN CHO BƯỚC SINH CÂU TRẢ LỜI (GENERATION):")
    print("-"*75)
    for r in reranked:
        print(f"\nTOP {r['final_rank']} [Điểm Rerank: {r['rerank_score']:.4f}] (Thứ hạng ban đầu: #{r['initial_rank']}, Độ dịch chuyển: {r['rank_delta']:+d})")
        print(f"Tiêu đề: {r['metadata']['title']} | Phân mục: {r['metadata']['section']}")
        print(f"Đơn vị: {r['metadata']['department']} | URL: {r['metadata']['source_url']}")
        print(f"Đoạn trích dẫn ngữ cảnh:\n\"{r['text'][:300]}...\"")

if __name__ == '__main__':
    run_interactive_demo()
