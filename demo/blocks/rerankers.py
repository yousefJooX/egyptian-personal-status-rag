"""Task 5: reranker.

Scores each retrieved chunk against the question with
BAAI/bge-reranker-v2-m3 (through FlagEmbedding.FlagReranker, fp16) and keeps
the top k.
"""

from __future__ import annotations


class Reranker:
    _model = None  # loaded once per process, shared across configs/instances

    def __init__(self, chunks: list[dict]):
        self.chunks_by_id = {c["id"]: c for c in chunks}
        if Reranker._model is None:
            from FlagEmbedding import FlagReranker

            Reranker._model = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)
        self.model = Reranker._model

    @classmethod
    def release(cls) -> None:
        """Drop the shared model so its GPU memory can be reused (run.py, before the LLM)."""
        cls._model = None

    def rerank(self, question: str, hits: list[dict], k: int) -> list[dict]:
        pairs = [[question, self.chunks_by_id[h["chunk_id"]]["text"]] for h in hits]
        scores = self.model.compute_score(pairs, normalize=True)
        if isinstance(scores, float):
            scores = [scores]

        ranked = sorted(zip(hits, scores), key=lambda pair: pair[1], reverse=True)[:k]
        return [
            {"rank": i + 1, "chunk_id": hit["chunk_id"], "score": round(float(score), 4)}
            for i, (hit, score) in enumerate(ranked)
        ]
