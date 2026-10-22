"""STUB for Task 3. Returns fake data in the right shape so the rest of the
pipeline can be built and tested before the real embedders exist.

Task 3 replaces this file. Keep the same class and method names.
"""

import numpy as np


class Embedder:
    DIMS = {"e5": 768, "bge": 1024}

    def __init__(self, name: str):
        if name not in self.DIMS:
            raise ValueError(f"unknown embedder {name!r}, expected one of {list(self.DIMS)}")
        self.name = name
        self.dim = self.DIMS[name]

    def encode(self, texts: list[str], is_query: bool) -> np.ndarray:
        rng = np.random.default_rng(abs(hash((self.name, is_query, tuple(texts)))) % (2**32))
        vecs = rng.standard_normal((len(texts), self.dim)).astype(np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vecs / norms
