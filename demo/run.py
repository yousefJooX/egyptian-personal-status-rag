"""Task 5: runner. One config per process.

    python run.py arch1
    python run.py arch1 --retrieval-only
"""

import argparse
import json
import time
from pathlib import Path

from configs import CONFIGS
from registry import build

try:
    import torch
except ImportError:
    torch = None

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"
TOP_K = 5
CANDIDATES = 20
SEED = 42


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", choices=sorted(CONFIGS))
    parser.add_argument("--retrieval-only", action="store_true")
    args = parser.parse_args()

    if torch is not None:
        torch.manual_seed(SEED)
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()

    cfg = CONFIGS[args.config]
    chunks = load_json(DATA_DIR / "chunks.json")
    test_set = load_json(DATA_DIR / "test_set.json")
    chunks_by_id = {c["id"]: c for c in chunks}

    retriever, reranker, llm = build(cfg, chunks)

    retrieval_out = []
    answers_out = []

    for item in test_set:
        qid, question = item["qid"], item["question"]

        if reranker is not None:
            hits = retriever.search(question, CANDIDATES)
            results = reranker.rerank(question, hits, TOP_K)
        else:
            hits = retriever.search(question, TOP_K)
            results = [
                {"rank": i + 1, "chunk_id": h["chunk_id"], "score": h["score"]}
                for i, h in enumerate(hits)
            ]

        retrieval_out.append({"qid": qid, "results": results})

        if args.retrieval_only:
            continue

        top_chunks = [chunks_by_id[r["chunk_id"]] for r in results]
        start = time.time()
        generated = llm.generate(question, top_chunks)
        seconds = time.time() - start

        answers_out.append(
            {
                "qid": qid,
                "answer": generated["answer"],
                "cited_chunks": generated["cited_chunks"],
                "refused": generated["refused"],
                "seconds": round(seconds, 4),
            }
        )

    RESULTS_DIR.mkdir(exist_ok=True)
    write_json(RESULTS_DIR / f"{args.config}_retrieval.json", retrieval_out)

    if not args.retrieval_only:
        write_json(RESULTS_DIR / f"{args.config}_answers.json", answers_out)
        peak_mb = 0
        if torch is not None and torch.cuda.is_available():
            peak_mb = torch.cuda.max_memory_allocated() // (1024 * 1024)
        write_json(RESULTS_DIR / f"{args.config}_cost.json", {"peak_gpu_mb": peak_mb})


if __name__ == "__main__":
    main()
