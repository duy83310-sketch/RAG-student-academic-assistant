import json
import os
import time
from pathlib import Path
import numpy as np
import chromadb
from chromadb.utils import embedding_functions

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def build_vector_database():
    print("=== KHỞI TẠO VÀ NẠP VECTOR DATABASE (CHROMADB) ===")
    
    # 1. Locate clean chunks
    candidates = [
        PROJECT_ROOT / 'data' / 'chunks' / 'clean_chunks.json',
        PROJECT_ROOT / 'data' / 'source' / 'clean_chunks.json',
        Path('data/chunks/clean_chunks.json'),
        Path('data/source/clean_chunks.json')
    ]
    source_path = None
    for c in candidates:
        if c.exists():
            source_path = c
            break

    if not source_path:
        raise FileNotFoundError(f"Cannot find clean_chunks.json in {candidates}")

    with open(source_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} clean chunks from '{source_path}'.")

    # 2. Setup Chroma Persistent Storage
    db_path = str(PROJECT_ROOT / 'data' / 'vector_store' / 'chroma_db')
    cache_emb_path = PROJECT_ROOT / 'data' / 'vector_store' / 'embeddings.npy'
    os.makedirs(db_path, exist_ok=True)
    
    client = chromadb.PersistentClient(path=db_path)
    ef = embedding_functions.DefaultEmbeddingFunction()

    # Recreate collection cleanly
    collection_name = "tlu_academic_chunks"
    try:
        client.delete_collection(name=collection_name)
        print(f"Old collection '{collection_name}' deleted.")
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine", "description": "TLU Academic Affairs RAG Corpus"}
    )
    print(f"Created collection '{collection_name}' with Cosine distance metric.")

    # 3. Check for cached embeddings
    texts = [c['text'] for c in chunks]
    if cache_emb_path.exists():
        print(f"Loading cached embeddings from '{cache_emb_path}'...")
        embeddings = np.load(cache_emb_path).tolist()
    else:
        print("Computing embeddings for all chunks...")
        embeddings = []
        batch_size = 64
        for i in range(0, len(texts), batch_size):
            b_texts = texts[i:i+batch_size]
            embs = ef(b_texts)
            embeddings.extend(embs)
            print(f"  -> Encoded {len(embeddings)}/{len(texts)} chunks...")
        np.save(cache_emb_path, np.array(embeddings, dtype=np.float32))
        print(f"Saved embeddings cache to '{cache_emb_path}'.")

    # 4. Prepare data and sanitize metadata for Chroma
    ids = []
    documents = []
    metadatas = []

    for c in chunks:
        ids.append(c['chunk_id'])
        documents.append(c['text'])
        
        tags_str = ", ".join(c.get('tags', [])) if isinstance(c.get('tags'), list) else str(c.get('tags', ''))
        meta = {
            "chunk_id": str(c.get('chunk_id', '')),
            "doc_id": str(c.get('doc_id', '')),
            "chunk_index": int(c.get('chunk_index', 0)),
            "total_chunks_in_doc": int(c.get('total_chunks_in_doc', 1)),
            "section": str(c.get('section', '')),
            "title": str(c.get('title', '')),
            "category": str(c.get('category', 'unknown')),
            "content_type": str(c.get('content_type', 'unknown')),
            "department": str(c.get('department', 'unknown')),
            "date": str(c.get('date', '')),
            "source_url": str(c.get('source_url', '')),
            "tags": tags_str,
            "char_length": int(c.get('char_length', len(c['text']))),
            "word_count": int(c.get('word_count', len(c['text'].split())))
        }
        metadatas.append(meta)

    # 5. Ingest into Chroma
    batch_size = 100
    start_time = time.perf_counter()
    print("Ingesting into ChromaDB...")
    
    for i in range(0, len(chunks), batch_size):
        end_idx = min(i + batch_size, len(chunks))
        collection.add(
            ids=ids[i:end_idx],
            documents=documents[i:end_idx],
            embeddings=embeddings[i:end_idx],
            metadatas=metadatas[i:end_idx]
        )

    duration = time.perf_counter() - start_time
    total_indexed = collection.count()
    print(f"\nVector DB build SUCCESSFUL in {duration:.2f}s! Total indexed: {total_indexed} chunks.")

    # 6. Sanity Test
    print("\n--- SANITY TEST: Metadata Filtering Query ---")
    test_results = collection.query(
        query_texts=["học phí ngành công nghệ thông tin"],
        n_results=3,
        where={"category": "chuong_trinh_dao_tao"}
    )
    for i, cid in enumerate(test_results['ids'][0]):
        dist = test_results['distances'][0][i]
        title = test_results['metadatas'][0][i]['title']
        sec = test_results['metadatas'][0][i]['section']
        print(f"  Top {i+1}: [{cid}] (Cosine Distance: {dist:.4f}) | {title} - {sec}")

    return db_path, total_indexed

if __name__ == '__main__':
    build_vector_database()
