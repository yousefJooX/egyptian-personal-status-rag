"""Task 3 "Done when" checks.

    python check_dense.py            # both embedders
    python check_dense.py e5         # one embedder

1. Embedding shape is (N, dim) with N = number of chunks.
2. A sentence taken from an article returns that article in the top 5.
3. A second build loads from the cache without re-encoding.
"""

import json
import random
import re
import sys
import gc
import time
from pathlib import Path

import torch

from blocks.dense import DenseRetriever
from blocks.embedders import Embedder

CHUNKS_PATH = Path(__file__).resolve().parents[1] / "data" / "chunks.json"  # written by chunking/


def pick_sentence(text: str, rng: random.Random) -> str | None:
    """A whole sentence (8+ words) from the article body, not an OCR line fragment."""
    body = " ".join(text.split("\n")[1:])  # drop the heading/article-number line
    sentences = [s.strip() for s in re.split(r"[.؛:]", body)]
    sentences = [s for s in sentences if len(s.split()) >= 8]
    return rng.choice(sentences) if sentences else None


def check(name: str, chunks: list[dict]) -> bool:
    print(f"\n===== {name} =====")
    embedder = Embedder(name)

    dense = DenseRetriever(chunks, embedder)
    shape_ok = dense.embeddings.shape == (len(chunks), embedder.dim)
    print(f"1. shape {dense.embeddings.shape}  ->  {'OK' if shape_ok else 'FAIL'}")

    rng = random.Random(42)
    hits, misses = 0, []
    for c in chunks:
        sentence = pick_sentence(c["text"], rng)
        if sentence is None:
            continue
        top = [r["chunk_id"] for r in dense.search(sentence, 5)]
        if c["id"] in top:
            hits += 1
        else:
            misses.append((c["id"], top[0], sentence[:60]))
    tested = hits + len(misses)
    rate = hits / tested
    print(f"2. self-retrieval top5: {hits}/{tested} ({rate:.1%})")
    for cid, got, sent in misses:
        print(f"     miss {cid} -> got {got}: {sent}...")

    start = time.time()
    again = DenseRetriever(chunks, embedder)
    cache_ok = (again.embeddings == dense.embeddings).all()
    print(f"3. cache reload in {time.time() - start:.2f}s  ->  {'OK' if cache_ok else 'FAIL'}")

    del dense, again, embedder
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()  # free this model before the next embedder loads

    return shape_ok and cache_ok and rate >= 0.95


def main() -> None:
    chunks = json.loads((CHUNKS_PATH).read_text(encoding="utf-8"))
    names = sys.argv[1:] or ["e5", "bge"]
    results = {name: check(name, chunks) for name in names}
    print("\n" + "  ".join(f"{n}: {'PASS' if ok else 'FAIL'}" for n, ok in results.items()))


if __name__ == "__main__":
    main()
