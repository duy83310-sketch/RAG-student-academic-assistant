import os
from pathlib import Path
import numpy as np
import chromadb
from chromadb.utils import embedding_functions

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class DenseRetriever:
    def __init__(self, db_path=None, collection_name="tlu_academic_chunks"):
        if db_path is None:
            db_path = str(PROJECT_ROOT / 'data' / 'vector_store' / 'chroma_db')
            
        self.client = chromadb.PersistentClient(path=db_path)
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_collection(name=collection_name, embedding_function=self.ef)
        print(f"[DenseRetriever] Initialized from '{db_path}'. Collection size: {self.collection.count()} chunks.")

    def search(self, query: str, top_k: int = 5, where: dict = None):
        kwargs = {
            "query_texts": [query],
            "n_results": min(top_k, self.collection.count()),
            "include": ["documents", "metadatas", "distances"]
        }
        if where:
            kwargs["where"] = where
            
        res = self.collection.query(**kwargs)
        
        results = []
        if res['ids'] and len(res['ids'][0]) > 0:
            for i in range(len(res['ids'][0])):
                dist = res['distances'][0][i]
                sim = max(0.0, 1.0 - dist)
                results.append({
                    "chunk_id": res['ids'][0][i],
                    "text": res['documents'][0][i],
                    "metadata": res['metadatas'][0][i],
                    "score": float(sim),
                    "distance": float(dist),
                    "retrieval_source": "dense"
                })
        return results

    def search_mmr(self, query: str, top_k: int = 5, fetch_k: int = 20, lambda_mult: float = 0.65, where: dict = None):
        kwargs = {
            "query_texts": [query],
            "n_results": min(fetch_k, self.collection.count()),
            "include": ["documents", "metadatas", "embeddings", "distances"]
        }
        if where:
            kwargs["where"] = where

        res = self.collection.query(**kwargs)
        if not res['ids'] or len(res['ids'][0]) == 0:
            return []

        cand_ids = res['ids'][0]
        cand_docs = res['documents'][0]
        cand_metas = res['metadatas'][0]
        cand_embs = np.array(res['embeddings'][0], dtype=np.float32)
        
        cand_norms = np.linalg.norm(cand_embs, axis=1, keepdims=True)
        cand_embs_norm = cand_embs / np.maximum(cand_norms, 1e-12)

        q_emb = np.array(self.ef([query])[0], dtype=np.float32)
        q_norm = q_emb / max(np.linalg.norm(q_emb), 1e-12)

        query_sims = np.dot(cand_embs_norm, q_norm)
        doc_sims = np.dot(cand_embs_norm, cand_embs_norm.T)

        selected_indices = []
        unselected_indices = list(range(len(cand_ids)))

        for _ in range(min(top_k, len(cand_ids))):
            best_idx = None
            best_mmr_score = -float('inf')

            for idx in unselected_indices:
                rel = query_sims[idx]
                div = max([doc_sims[idx][sel] for sel in selected_indices]) if selected_indices else 0.0
                mmr_score = lambda_mult * rel - (1.0 - lambda_mult) * div

                if mmr_score > best_mmr_score:
                    best_mmr_score = mmr_score
                    best_idx = idx

            if best_idx is not None:
                selected_indices.append(best_idx)
                unselected_indices.remove(best_idx)

        results = []
        for rank, idx in enumerate(selected_indices):
            results.append({
                "rank": rank + 1,
                "chunk_id": cand_ids[idx],
                "text": cand_docs[idx],
                "metadata": cand_metas[idx],
                "score": float(query_sims[idx]),
                "retrieval_source": "dense_mmr"
            })
        return results

if __name__ == '__main__':
    r = DenseRetriever()
    q = "Học phí kỳ 1 ngành Công nghệ thông tin khóa 39"
    print(f"\n--- Testing Query: '{q}' ---")
    res_dense = r.search(q, top_k=3)
    for item in res_dense:
        print(f"  [{item['chunk_id']}] Score: {item['score']:.4f} | {item['metadata']['title']}")
