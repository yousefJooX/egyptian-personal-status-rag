"""Fuse dense and BM25 rankings with Reciprocal Rank Fusion."""
from __future__ import annotations

RRF_K = 60
POOL = 20


class HybridRetriever:
    def __init__(self, dense, bm25):
        self.dense = dense
        self.bm25 = bm25

    def search(self, question: str, k: int) -> list[dict]:
        if k <= 0:
            return []

        dense_hits = self.dense.search(question, POOL)
        bm25_hits = self.bm25.search(question, POOL)

        rank_dense = {h["chunk_id"]: i + 1 for i, h in enumerate(dense_hits)}
        rank_bm25 = {h["chunk_id"]: i + 1 for i, h in enumerate(bm25_hits)}

        fused = []
        for chunk_id in rank_dense.keys() | rank_bm25.keys():
            score = 0.0
            if chunk_id in rank_dense:
                score += 1 / (RRF_K + rank_dense[chunk_id])
            if chunk_id in rank_bm25:
                score += 1 / (RRF_K + rank_bm25[chunk_id])
            fused.append((chunk_id, score))

        fused.sort(key=lambda pair: (-pair[1], pair[0]))
        return [{"chunk_id": cid, "score": round(score, 6)} for cid, score in fused[:k]]
