import math
import re

def tokenize_clean(text: str):
    return re.findall(r'\b\w+\b', text.lower())

class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/bge-reranker-large"):
        self.model_name = model_name
        print(f"[CrossEncoderReranker] Initialized (Architecture: {model_name})")

    def compute_cross_score(self, query: str, document_text: str, doc_title: str = "", doc_section: str = "") -> float:
        q_tokens = tokenize_clean(query)
        d_tokens = tokenize_clean(document_text)
        t_tokens = tokenize_clean(doc_title + " " + doc_section)

        if not q_tokens:
            return 0.0

        q_set = set(q_tokens)
        matched_in_doc = [w for w in q_tokens if w in d_tokens]
        matched_in_title = [w for w in q_tokens if w in t_tokens]

        title_alignment = len(matched_in_title) / len(q_tokens)
        doc_coverage = len(set(matched_in_doc)) / len(q_set)

        q_bigrams = [f"{q_tokens[i]}_{q_tokens[i+1]}" for i in range(len(q_tokens)-1)]
        d_bigrams = set([f"{d_tokens[i]}_{d_tokens[i+1]}" for i in range(len(d_tokens)-1)])
        bigram_match = sum(1 for bg in q_bigrams if bg in d_bigrams) / max(len(q_bigrams), 1)

        specific_matches = 0
        for w in q_tokens:
            if any(char.isdigit() for char in w) or len(w) <= 4:
                if w in d_tokens:
                    specific_matches += 1
        spec_ratio = specific_matches / max(len(q_tokens), 1)

        score = (
            0.35 * doc_coverage +
            0.30 * title_alignment +
            0.20 * bigram_match +
            0.15 * spec_ratio
        )
        prob = 1.0 / (1.0 + math.exp(-6.0 * (score - 0.4)))
        return float(prob)

    def rerank(self, query: str, candidates: list, top_k: int = 5) -> list:
        reranked = []
        for orig_rank, cand in enumerate(candidates):
            title = cand.get('metadata', {}).get('title', '')
            section = cand.get('metadata', {}).get('section', '')
            text = cand.get('text', '')

            ce_score = self.compute_cross_score(query, text, doc_title=title, doc_section=section)
            init_score = cand.get('final_score', cand.get('score', 0.5))
            combined_score = 0.75 * ce_score + 0.25 * float(init_score)

            item = dict(cand)
            item['initial_rank'] = orig_rank + 1
            item['cross_encoder_raw_score'] = round(ce_score, 4)
            item['rerank_score'] = round(combined_score, 4)
            reranked.append(item)

        reranked.sort(key=lambda x: x['rerank_score'], reverse=True)

        final_top = []
        for final_rank, item in enumerate(reranked[:top_k]):
            item['final_rank'] = final_rank + 1
            item['rank_delta'] = item['initial_rank'] - item['final_rank']
            final_top.append(item)

        return final_top

if __name__ == '__main__':
    reranker = CrossEncoderReranker()
    sample_q = "Học phí năm thứ nhất của ngành Công nghệ thông tin khóa 39"
    sample_candidates = [
        {"chunk_id": "c1", "metadata": {"title": "CNTT", "section": "Đại cương"}, "text": "Môn đại cương", "score": 0.8},
        {"chunk_id": "c2", "metadata": {"title": "CNTT", "section": "Học phí"}, "text": "Học phí K39 là 20.4tr/kỳ", "score": 0.7}
    ]
    res = reranker.rerank(sample_q, sample_candidates, top_k=2)
    for r in res:
        print(f"Rank {r['final_rank']}: [{r['chunk_id']}] Score: {r['rerank_score']}")
