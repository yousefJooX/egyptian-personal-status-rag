"""Task 3: dense retriever.

Encodes every chunk once, keeps the vectors in a FAISS IndexFlatIP
(inner product on L2-normalized vectors = cosine similarity), and caches
them under data/index/{embedder name}.npy / .faiss so later runs skip encoding.

    dense = DenseRetriever(chunks, Embedder("e5"))
    dense.search("سؤال", 5)  # [{"chunk_id": ..., "score": ...}, ...] best first
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import faiss
import numpy as np

from utils import normalize_ar

INDEX_DIR = Path(__file__).resolve().parents[1] / "data" / "index"


class DenseRetriever:
    def __init__(self, chunks: list[dict], embedder):
        self.chunks = chunks
        self.embedder = embedder
        self.ids = [c["id"] for c in chunks]
        self.fingerprint = hashlib.sha256(
            json.dumps([[c["id"], normalize_ar(c["text"])] for c in chunks], ensure_ascii=False).encode("utf-8")
        ).hexdigest()

        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        self.npy_path = INDEX_DIR / f"{embedder.name}.npy"
        self.faiss_path = INDEX_DIR / f"{embedder.name}.faiss"
        self.meta_path = INDEX_DIR / f"{embedder.name}.meta.json"

        if self._cache_is_valid():
            print(f"[dense:{embedder.name}] loading cached index from {INDEX_DIR}")
            self.embeddings = np.load(self.npy_path)
            self.index = faiss.read_index(str(self.faiss_path))
        else:
            print(f"[dense:{embedder.name}] encoding {len(chunks)} chunks")
            self.embeddings = embedder.encode([c["text"] for c in chunks], is_query=False)
            self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
            self.index.add(self.embeddings)
            self._save_cache()

    def search(self, question: str, k: int) -> list[dict]:
        k = min(k, self.index.ntotal)
        q_vec = self.embedder.encode([question], is_query=True)
        scores, positions = self.index.search(q_vec, k)
        return [
            {"chunk_id": self.ids[pos], "score": round(float(score), 4)}
            for pos, score in zip(positions[0], scores[0])
            if pos != -1
        ]

    def _cache_is_valid(self) -> bool:
        if not (self.npy_path.exists() and self.faiss_path.exists() and self.meta_path.exists()):
            return False
        meta = json.loads(self.meta_path.read_text(encoding="utf-8"))
        if meta.get("fingerprint") != self.fingerprint:
            print(f"[dense:{self.embedder.name}] chunks changed since the cache was built, re-encoding")
            return False
        return True

    def _save_cache(self) -> None:
        np.save(self.npy_path, self.embeddings)
        faiss.write_index(self.index, str(self.faiss_path))
        meta = {"fingerprint": self.fingerprint, "ids": self.ids}
        self.meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
