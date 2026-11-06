import json
import re
from pathlib import Path
import numpy as np
from rank_bm25 import BM25Okapi

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    from src.retrieval.dense_retriever import DenseRetriever
except ImportError:
    try:
        from .dense_retriever import DenseRetriever
    except ImportError:
        from dense_retriever import DenseRetriever

def tokenize_vietnamese(text: str):
    cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
    return [t for t in cleaned.split() if len(t) > 0]

class HybridRetriever:
    def __init__(self, json_path=None, db_path=None):
        if db_path is None:
            db_path = str(PROJECT_ROOT / 'data' / 'vector_store' / 'chroma_db')
            
        self.dense_retriever = DenseRetriever(db_path=db_path)
        
        if json_path is None:
            candidates = [
                PROJECT_ROOT / 'data' / 'chunks' / 'clean_chunks.json',
                PROJECT_ROOT / 'data' / 'source' / 'clean_chunks.json',
                Path('data/chunks/clean_chunks.json'),
                Path('data/source/clean_chunks.json')
            ]
            for c in candidates:
                if c.exists():
                    json_path = c
                    break
                    
        with open(json_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
            
        self.chunk_id_map = {c['chunk_id']: c for c in self.chunks}
        self.corpus_tokens = [tokenize_vietnamese(c['text'] + " " + c.get('title', '')) for c in self.chunks]
        self.bm25 = BM25Okapi(self.corpus_tokens)
        print(f"[HybridRetriever] Initialized with {len(self.chunks)} chunks for BM25 and Dense Search.")

    def search_bm25(self, query: str, top_k: int = 20, where: dict = None):
        q_tokens = tokenize_vietnamese(query)
        if not q_tokens:
            return []
            
        scores = self.bm25.get_scores(q_tokens)
        top_indices = np.argsort(scores)[::-1]
        
        results = []
        for idx in top_indices:
            if scores[idx] <= 0:
                break
            chunk = self.chunks[idx]
            if where:
                match = all(chunk.get(k) == v for k, v in where.items())
                if not match:
                    continue
                    
            results.append({
                "chunk_id": chunk['chunk_id'],
                "text": chunk['text'],
                "metadata": {
                    "title": chunk.get('title', ''),
                    "section": chunk.get('section', ''),
                    "category": chunk.get('category', ''),
                    "department": chunk.get('department', ''),
                    "source_url": chunk.get('source_url', '')
                },
                "bm25_score": float(scores[idx]),
                "retrieval_source": "bm25"
            })
            if len(results) >= top_k:
                break
        return results

    def search_hybrid(self, query: str, top_k: int = 5, alpha: float = 0.55, fusion_mode: str = "rrf", where: dict = None):
        candidate_k = max(20, top_k * 3)
        dense_results = self.dense_retriever.search(query, top_k=candidate_k, where=where)
        bm25_results = self.search_bm25(query, top_k=candidate_k, where=where)

        combined_candidates = {}

        if fusion_mode == "rrf":
            rrf_k = 60
            for rank, r in enumerate(dense_results):
                cid = r['chunk_id']
                rrf_score = 1.0 / (rrf_k + rank + 1)
                combined_candidates[cid] = {
                    "chunk_id": cid,
                    "text": r['text'],
                    "metadata": r['metadata'],
                    "rrf_score": rrf_score,
                    "dense_rank": rank + 1,
                    "bm25_rank": None,
                    "dense_sim": r['score'],
                    "bm25_score": 0.0,
                    "sources": ["dense"]
                }
            for rank, r in enumerate(bm25_results):
                cid = r['chunk_id']
                rrf_score = 1.0 / (rrf_k + rank + 1)
                if cid in combined_candidates:
                    combined_candidates[cid]["rrf_score"] += rrf_score
                    combined_candidates[cid]["bm25_rank"] = rank + 1
                    combined_candidates[cid]["bm25_score"] = r["bm25_score"]
                    combined_candidates[cid]["sources"].append("bm25")
                else:
                    combined_candidates[cid] = {
                        "chunk_id": cid,
                        "text": r['text'],
                        "metadata": r['metadata'],
                        "rrf_score": rrf_score,
                        "dense_rank": None,
                        "bm25_rank": rank + 1,
                        "dense_sim": 0.0,
                        "bm25_score": r["bm25_score"],
                        "sources": ["bm25"]
                    }
                    
            sorted_candidates = sorted(combined_candidates.values(), key=lambda x: x['rrf_score'], reverse=True)
            for item in sorted_candidates:
                item['final_score'] = item['rrf_score']
                item['fusion_mode'] = 'RRF'

        else:
            max_dense = max([r['score'] for r in dense_results], default=1.0)
            min_dense = min([r['score'] for r in dense_results], default=0.0)
            range_dense = max(max_dense - min_dense, 1e-6)

            max_bm25 = max([r['bm25_score'] for r in bm25_results], default=1.0)
            min_bm25 = min([r['bm25_score'] for r in bm25_results], default=0.0)
            range_bm25 = max(max_bm25 - min_bm25, 1e-6)

            for r in dense_results:
                cid = r['chunk_id']
                norm_d = (r['score'] - min_dense) / range_dense
                combined_candidates[cid] = {
                    "chunk_id": cid,
                    "text": r['text'],
                    "metadata": r['metadata'],
                    "norm_dense": norm_d,
                    "norm_bm25": 0.0,
                    "sources": ["dense"]
                }
            for r in bm25_results:
                cid = r['chunk_id']
                norm_b = (r['bm25_score'] - min_bm25) / range_bm25
                if cid in combined_candidates:
                    combined_candidates[cid]["norm_bm25"] = norm_b
                    combined_candidates[cid]["sources"].append("bm25")
                else:
                    combined_candidates[cid] = {
                        "chunk_id": cid,
                        "text": r['text'],
                        "metadata": r['metadata'],
                        "norm_dense": 0.0,
                        "norm_bm25": norm_b,
                        "sources": ["bm25"]
                    }
                    
            for cid, cdata in combined_candidates.items():
                cdata['final_score'] = alpha * cdata['norm_dense'] + (1.0 - alpha) * cdata['norm_bm25']
                cdata['fusion_mode'] = f'Weighted (alpha={alpha})'
                
            sorted_candidates = sorted(combined_candidates.values(), key=lambda x: x['final_score'], reverse=True)

        return sorted_candidates[:top_k]

if __name__ == '__main__':
    hr = HybridRetriever()
    q = "Mã ngành tuyển sinh và thời gian đào tạo Công nghệ thông tin"
    results = hr.search_hybrid(q, top_k=3, fusion_mode="rrf")
    for i, r in enumerate(results):
        print(f"Top {i+1}: [{r['chunk_id']}] Score: {r['final_score']:.5f} | {r['metadata']['title']}")
