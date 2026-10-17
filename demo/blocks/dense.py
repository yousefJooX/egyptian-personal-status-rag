"""STUB for Task 3. Returns fake data in the right shape.

Task 3 replaces this file. Keep the same class and method names.
"""

import random


class DenseRetriever:
    def __init__(self, chunks: list[dict], embedder):
        self.chunks = chunks
        self.embedder = embedder

    def search(self, question: str, k: int) -> list[dict]:
        rng = random.Random(hash(("dense", question)) & 0xFFFFFFFF)
        sample = rng.sample(self.chunks, min(k, len(self.chunks)))
        return [
            {"chunk_id": c["id"], "score": round(1.0 - i * 0.05, 4)}
            for i, c in enumerate(sample)
        ]
