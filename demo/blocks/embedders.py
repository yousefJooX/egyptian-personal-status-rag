"""Task 3: text embedders.

Turns texts (chunks or questions) into L2-normalized float32 vectors.
All model details (model id, prefixes, max length) live here and nowhere else.

    emb = Embedder("e5")
    vecs = emb.encode(["..."], is_query=False)   # shape (n, 768)
"""

from __future__ import annotations

import numpy as np

from utils import normalize_ar

MODELS = {
    "e5": {
        "id": "intfloat/multilingual-e5-base",
        "dim": 768,
        "max_len": 512,
        "query_prefix": "query: ",
        "passage_prefix": "passage: ",
    },
    "bge": {
        "id": "BAAI/bge-m3",
        "dim": 1024,
        "max_len": 1024,
        "query_prefix": "",
        "passage_prefix": "",
    },
}


class Embedder:
    DIMS = {name: cfg["dim"] for name, cfg in MODELS.items()}

    def __init__(self, name: str):
        if name not in MODELS:
            raise ValueError(f"unknown embedder {name!r}, expected one of {list(MODELS)}")
        self.name = name
        self.cfg = MODELS[name]
        self.dim = self.cfg["dim"]
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.cfg["id"])
            self._model.max_seq_length = self.cfg["max_len"]
        return self._model

    def encode(self, texts: list[str], is_query: bool) -> np.ndarray:
        prefix = self.cfg["query_prefix"] if is_query else self.cfg["passage_prefix"]
        prepared = [prefix + normalize_ar(t) for t in texts]

        self._report_truncation(prepared)

        vecs = self.model.encode(
            prepared,
            batch_size=32,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=len(prepared) > 32,
        )
        return np.asarray(vecs, dtype=np.float32)

    def _report_truncation(self, prepared: list[str]) -> None:
        max_len = self.cfg["max_len"]
        lengths = [len(ids) for ids in self.model.tokenizer(prepared)["input_ids"]]
        too_long = sum(1 for n in lengths if n > max_len)
        if too_long:
            print(f"[{self.name}] {too_long} of {len(prepared)} texts exceed {max_len} tokens and get truncated")
