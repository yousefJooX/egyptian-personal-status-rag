"""STUB for Task 4. Returns fake data in the right shape.

Task 4 replaces this file. Keep the same class and method names.
"""

import random


class BM25Retriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks

    def search(self, question: str, k: int) -> list[dict]:
        rng = random.Random(hash(("bm25", question)) & 0xFFFFFFFF)
        sample = rng.sample(self.chunks, min(k, len(self.chunks)))
        return [
            {"chunk_id": c["id"], "score": round(10.0 - i * 0.3, 4)}
            for i, c in enumerate(sample)
        ]
