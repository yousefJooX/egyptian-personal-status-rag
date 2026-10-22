# demo — Task 5 scaffold

Day-0 scaffolding for the RAG pipeline (retriever -> reranker -> LLM) plus
the real Task 5 piece: `blocks/rerankers.py`.

## What's real vs. stub

| File | Status |
|---|---|
| `blocks/rerankers.py` | Real (Task 5). Uses `BAAI/bge-reranker-v2-m3` via `FlagEmbedding.FlagReranker`. |
| `configs.py`, `registry.py`, `run.py` | Real (Task 5). |
| `blocks/embedders.py`, `blocks/dense.py` | Real (Task 3). e5 / bge-m3 + FAISS, cached in `data/index/`. Check with `python check_dense.py`. |
| `blocks/bm25.py`, `blocks/hybrid.py` | Stub — Task 4 replaces. |
| `blocks/llms.py` | Stub — Task 6 replaces. |
| `../data/chunks.json` | Real 188 article chunks from Task 1 (`chunking/`). Single copy at the repo root. |
| `data/test_set.json` | Placeholder sample — Task 2 replaces with the real 30-40 question set. |

Stubs return fake data in the exact output shape the real block must produce,
so `run.py` and everything downstream (Task 7's `evaluate.py`) can be built
and tested today.

## Run it

```bash
cd demo
pip install -r requirements.txt   # only needed for configs with a reranker, e.g. arch3
python run.py arch1               # no reranker, no heavy deps needed
python run.py arch1 --retrieval-only
python run.py arch3               # loads the real bge-reranker-v2-m3
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
