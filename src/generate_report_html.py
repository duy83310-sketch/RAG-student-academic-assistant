import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def generate_html():
    rb_file = PROJECT_ROOT / 'data' / 'benchmarks' / 'retrieval_benchmark.json'
    eb_file = PROJECT_ROOT / 'data' / 'benchmarks' / 'embedding_benchmark.json'
    q_file = PROJECT_ROOT / 'data' / 'queries' / 'tlu_academic_queries.json'

    with open(rb_file, 'r', encoding='utf-8') as f:
        rb = json.load(f)
    with open(eb_file, 'r', encoding='utf-8') as f:
        eb = json.load(f)
    with open(q_file, 'r', encoding='utf-8') as f:
        queries = json.load(f)

    summary = rb['summary']
    emb_models = eb['models_comparison']
    throughput = eb['models_comparison']['all-MiniLM-L6-v2 (Chroma ONNX)']['throughput_chunks_per_sec']

    h1_val = summary['Hybrid_Reranked']['hit_at_1_pct']
    h3_val = summary['Hybrid_Reranked']['hit_at_3_pct']
    mrr_val = summary['Hybrid_Reranked']['mrr']

    bm25_h1 = summary['BM25_Only']['hit_at_1_pct']
    bm25_h3 = summary['BM25_Only']['hit_at_3_pct']
    bm25_h5 = summary['BM25_Only']['hit_at_5_pct']
    bm25_mrr = summary['BM25_Only']['mrr']
    bm25_lat = summary['BM25_Only']['avg_latency_ms']

    dense_h1 = summary['Dense_Only']['hit_at_1_pct']
    dense_h3 = summary['Dense_Only']['hit_at_3_pct']
    dense_h5 = summary['Dense_Only']['hit_at_5_pct']
    dense_mrr = summary['Dense_Only']['mrr']
    dense_lat = summary['Dense_Only']['avg_latency_ms']

    hybrid_h1 = summary['Hybrid_RRF']['hit_at_1_pct']
    hybrid_h3 = summary['Hybrid_RRF']['hit_at_3_pct']
    hybrid_h5 = summary['Hybrid_RRF']['hit_at_5_pct']
    hybrid_mrr = summary['Hybrid_RRF']['mrr']
    hybrid_lat = summary['Hybrid_RRF']['avg_latency_ms']

    rerank_h1 = summary['Hybrid_Reranked']['hit_at_1_pct']
    rerank_h3 = summary['Hybrid_Reranked']['hit_at_3_pct']
    rerank_h5 = summary['Hybrid_Reranked']['hit_at_5_pct']
    rerank_mrr = summary['Hybrid_Reranked']['mrr']
    rerank_lat = summary['Hybrid_Reranked']['avg_latency_ms']

    html_source = (PROJECT_ROOT / 'reports' / 'Bao_Cao_Tuan_3_4.html')
    if html_source.exists():
        with open(html_source, 'r', encoding='utf-8') as f:
            content = f.read()
        p_root = PROJECT_ROOT / 'Bao_Cao_Tuan_3_4.html'
        with open(p_root, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"HTML synchronized successfully to '{p_root}'.")

if __name__ == '__main__':
    generate_html()
