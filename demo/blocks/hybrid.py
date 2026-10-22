"""STUB for Task 4. Fuses the (fake) dense and BM25 stub results with
Reciprocal Rank Fusion so the interface and output shape match the real
thing. Task 4 replaces this file with the real dense/BM25-backed version.
Keep the same class and method names.
"""


class HybridRetriever:
    def __init__(self, dense, bm25):
        self.dense = dense
        self.bm25 = bm25

    def search(self, question: str, k: int) -> list[dict]:
        dense_hits = self.dense.search(question, 20)
        bm25_hits = self.bm25.search(question, 20)

        rank_dense = {h["chunk_id"]: i + 1 for i, h in enumerate(dense_hits)}
        rank_bm25 = {h["chunk_id"]: i + 1 for i, h in enumerate(bm25_hits)}

        fused = []
        for chunk_id in set(rank_dense) | set(rank_bm25):
            score = 0.0
            if chunk_id in rank_dense:
                score += 1 / (60 + rank_dense[chunk_id])
            if chunk_id in rank_bm25:
                score += 1 / (60 + rank_bm25[chunk_id])
            fused.append({"chunk_id": chunk_id, "score": round(score, 6)})

        fused.sort(key=lambda h: h["score"], reverse=True)
        return fused[:k]
