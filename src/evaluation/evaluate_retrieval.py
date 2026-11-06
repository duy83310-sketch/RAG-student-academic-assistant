import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import time
import numpy as np

from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.reranker import CrossEncoderReranker

def evaluate_pipelines():
    print("=== TUẦN 4: ĐÁNH GIÁ ĐỐI SOÁT CÁC PHƯƠNG PHÁP RETRIEVAL VÀ HIỆU QUẢ RERANK ===")
    
    candidates = [
        PROJECT_ROOT / 'data' / 'queries' / 'tlu_academic_queries.json',
        Path('data/queries/tlu_academic_queries.json')
    ]
    query_file = None
    for c in candidates:
        if c.exists():
            query_file = c
            break

    if not query_file:
        raise FileNotFoundError(f"Cannot find tlu_academic_queries.json in {candidates}")

    with open(query_file, 'r', encoding='utf-8') as f:
        queries = json.load(f)
    print(f"Loaded {len(queries)} evaluation queries from '{query_file}'.")

    dense_retriever = DenseRetriever()
    hybrid_retriever = HybridRetriever()
    reranker = CrossEncoderReranker()

    pipelines = ["BM25_Only", "Dense_Only", "Hybrid_RRF", "Hybrid_Reranked"]
    metrics = {
        p: {
            "hit_at_1": 0,
            "hit_at_3": 0,
            "hit_at_5": 0,
            "reciprocal_ranks": [],
            "latencies_ms": []
        } for p in pipelines
    }

    per_query_results = []

    print("\nExecuting evaluation across all 25 queries...")
    for q_item in queries:
        qid = q_item['query_id']
        q_text = q_item['query']
        expected_ids = set(q_item['expected_chunk_ids'])

        query_eval = {
            "query_id": qid,
            "query": q_text,
            "category": q_item['category'],
            "expected_chunk_ids": list(expected_ids),
            "pipeline_ranks": {}
        }

        # 1. BM25 Only
        t0 = time.perf_counter()
        res_bm25 = hybrid_retriever.search_bm25(q_text, top_k=10)
        t_bm25 = (time.perf_counter() - t0) * 1000
        bm25_ids = [r['chunk_id'] for r in res_bm25]
        
        # 2. Dense Only
        t0 = time.perf_counter()
        res_dense = dense_retriever.search(q_text, top_k=10)
        t_dense = (time.perf_counter() - t0) * 1000
        dense_ids = [r['chunk_id'] for r in res_dense]

        # 3. Hybrid RRF
        t0 = time.perf_counter()
        res_hybrid = hybrid_retriever.search_hybrid(q_text, top_k=15, fusion_mode="rrf")
        t_hybrid = (time.perf_counter() - t0) * 1000
        hybrid_ids = [r['chunk_id'] for r in res_hybrid]

        # 4. Hybrid + Rerank
        t0 = time.perf_counter()
        res_rerank = reranker.rerank(q_text, res_hybrid[:15], top_k=5)
        t_rerank = (time.perf_counter() - t0) * 1000 + t_hybrid
        rerank_ids = [r['chunk_id'] for r in res_rerank]

        pipeline_outputs = {
            "BM25_Only": (bm25_ids, t_bm25),
            "Dense_Only": (dense_ids, t_dense),
            "Hybrid_RRF": (hybrid_ids[:5], t_hybrid),
            "Hybrid_Reranked": (rerank_ids, t_rerank)
        }

        for p_name, (cand_ids, latency) in pipeline_outputs.items():
            metrics[p_name]["latencies_ms"].append(latency)
            
            first_rank = None
            for rank_idx, cid in enumerate(cand_ids):
                if cid in expected_ids:
                    first_rank = rank_idx + 1
                    break
            
            query_eval["pipeline_ranks"][p_name] = first_rank
            
            if first_rank is not None:
                if first_rank == 1:
                    metrics[p_name]["hit_at_1"] += 1
                if first_rank <= 3:
                    metrics[p_name]["hit_at_3"] += 1
                if first_rank <= 5:
                    metrics[p_name]["hit_at_5"] += 1
                metrics[p_name]["reciprocal_ranks"].append(1.0 / first_rank)
            else:
                metrics[p_name]["reciprocal_ranks"].append(0.0)

        per_query_results.append(query_eval)

    N = len(queries)
    summary_report = {}
    print("\n" + "="*80)
    print(f"{'PIPELINE':<20} | {'HIT@1':<8} | {'HIT@3':<8} | {'HIT@5':<8} | {'MRR':<8} | {'LATENCY (ms)':<12}")
    print("="*80)

    for p_name in pipelines:
        h1 = (metrics[p_name]["hit_at_1"] / N) * 100
        h3 = (metrics[p_name]["hit_at_3"] / N) * 100
        h5 = (metrics[p_name]["hit_at_5"] / N) * 100
        mrr = float(np.mean(metrics[p_name]["reciprocal_ranks"]))
        avg_lat = float(np.mean(metrics[p_name]["latencies_ms"]))

        summary_report[p_name] = {
            "hit_at_1_pct": round(h1, 1),
            "hit_at_3_pct": round(h3, 1),
            "hit_at_5_pct": round(h5, 1),
            "mrr": round(mrr, 4),
            "avg_latency_ms": round(avg_lat, 2)
        }
        print(f"{p_name:<20} | {h1:>6.1f}% | {h3:>6.1f}% | {h5:>6.1f}% | {mrr:>6.4f} | {avg_lat:>8.2f} ms")
    print("="*80)

    benchmark_data = {
        "benchmark_name": "TLU Academic Affairs Retrieval Benchmark",
        "total_queries": N,
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": summary_report,
        "detailed_queries": per_query_results
    }

    out_file = PROJECT_ROOT / 'data' / 'benchmarks' / 'retrieval_benchmark.json'
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(benchmark_data, f, ensure_ascii=False, indent=2)

    print(f"\nDetailed evaluation saved to '{out_file}'.")
    return benchmark_data

if __name__ == '__main__':
    evaluate_pipelines()
