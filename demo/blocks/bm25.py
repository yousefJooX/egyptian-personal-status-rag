"""BM25 retriever with a fingerprinted on-disk index cache."""

import hashlib
import json
import pickle
import re
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

from utils import normalize_ar

INDEX_DIR = Path(__file__).resolve().parents[1] / "data" / "index"
PICKLE_PATH = INDEX_DIR / "bm25.pkl"

PUNCTUATION = re.compile(r"[^\w\s]", flags=re.UNICODE)


def tokenize(text: str) -> list[str]:
    text = PUNCTUATION.sub(" ", normalize_ar(text))
    return text.split()


class BM25Retriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.ids = [chunk["id"] for chunk in chunks]
        self.fingerprint = hashlib.sha256(
            json.dumps(
                [[chunk["id"], normalize_ar(chunk["text"])] for chunk in chunks],
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()

        self.bm25 = self.load_cache()
        if self.bm25 is None:
            print(f"[bm25] building index over {len(chunks)} chunks")
            corpus = [tokenize(chunk["text"]) for chunk in chunks]
            self.bm25 = BM25Okapi(corpus)
            self.save_cache()
        else:
            print(f"[bm25] loaded cached index from {PICKLE_PATH}")

    def search(self, question: str, k: int) -> list[dict]:
        k = min(k, len(self.ids))
        if k <= 0:
            return []

        scores = np.asarray(self.bm25.get_scores(tokenize(question)), dtype=np.float64)
        top = np.argsort(-scores, kind="stable")[:k]
        return [
            {"chunk_id": self.ids[index], "score": round(float(scores[index]), 4)}
            for index in top
        ]

    def load_cache(self):
        if not PICKLE_PATH.exists():
            return None
        try:
            with open(PICKLE_PATH, "rb") as cache_file:
                payload = pickle.load(cache_file)
        except (OSError, pickle.PickleError, EOFError) as exc:
            print(f"[bm25] could not read cache ({exc}), rebuilding")
            return None

        if (
            not isinstance(payload, dict)
            or payload.get("fingerprint") != self.fingerprint
            or "bm25" not in payload
        ):
            print("[bm25] chunks changed or cache is invalid, rebuilding")
            return None
        return payload["bm25"]

    def save_cache(self) -> None:
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        with open(PICKLE_PATH, "wb") as cache_file:
            pickle.dump(
                {"fingerprint": self.fingerprint, "bm25": self.bm25},
                cache_file,
            )
