# demo — the RAG pipeline

Retriever -> (reranker) -> LLM, one block per file, wired by `registry.py`
from a named config in `configs.py`.

## Blocks

| File | Status |
|---|---|
| `blocks/rerankers.py` | Real (Task 5). Uses `BAAI/bge-reranker-v2-m3` via `FlagEmbedding.FlagReranker`. |
| `configs.py`, `registry.py`, `run.py` | Real (Task 5). |
| `blocks/embedders.py`, `blocks/dense.py` | Real (Task 3). e5 / bge-m3 + FAISS, cached in `data/index/`. Check with `python check_dense.py`. |
| `blocks/bm25.py`, `blocks/hybrid.py` | Real (Task 4). `rank_bm25.BM25Okapi` cached in `data/index/bm25.pkl`; hybrid = RRF over dense + BM25 top 20. |
| `blocks/llms.py` | Real (Task 6). Qwen2.5 3B / 7B (4-bit), Aya Expanse 8B (4-bit). Check with `python check_llm.py [qwen3b]`. |
| `../data/chunks.json` | Real 188 article chunks from Task 1 (`chunking/`). Single copy at the repo root. |
| `data/test_set.json` | Real (Task 2). 35 questions, 10 of them unanswerable. |

`run.py` runs retrieval for every question first, writes the retrieval file,
frees the embedder and reranker, and only then loads the LLM, so one 6-8 GB GPU
never holds both. `--retrieval-only` never loads an LLM.

## Run it

```bash
cd demo
uv sync                                     # from the repo root
uv run python run.py arch1 --retrieval-only  # retrieval only, no LLM
uv run python run.py arch1                   # full pipeline with qwen3b
uv run python run.py arch3                   # hybrid + bge-reranker-v2-m3 + aya8b
```

Output lands in `results/{config}_retrieval.json`, `_answers.json`, `_cost.json`.

## Swapping in the real pieces

Task 1, 3, 4, 6 each replace one or more files under `blocks/` (and Task 1
replaces `../data/chunks.json`, Task 2 replaces `data/test_set.json`) without
touching `registry.py`, `configs.py`, or `run.py` — as long as the class and
method signatures below are kept.

- `Embedder(name).encode(texts, is_query) -> np.ndarray`
- `DenseRetriever(chunks, embedder).search(question, k) -> list[dict]`
- `BM25Retriever(chunks).search(question, k) -> list[dict]`
- `HybridRetriever(dense, bm25).search(question, k) -> list[dict]`
- `Reranker(chunks).rerank(question, hits, k) -> list[dict]`
- `LLM(name).generate(question, chunks) -> dict`
