# Task 4: BM25 and hybrid retriever

## Folder layout (same for everyone)

```
project/
  data/
    rules.pdf          given
    chunks.json        task 1
    test_set.json      task 2
    index/             cached embeddings and indexes, created by code
  blocks/
    embedders.py       task 3
    dense.py           task 3
    bm25.py            task 4
    hybrid.py          task 4
    rerankers.py       task 5
    llms.py            task 6
  utils.py             task 1 (normalize_ar)
  registry.py          task 5
  configs.py           task 5
  run.py               task 5
  evaluate.py          task 7
  results/             created by run.py and evaluate.py
```

## Before you start

- Task 1 has pushed `utils.py` and a sample `data/chunks.json`.
- Task 3 exposes `DenseRetriever.search(question, k)`. Until it is ready, use the stub that Task 5 pushed.
- Task 5 has pushed stub versions of `blocks/bm25.py` and `blocks/hybrid.py`. Replace them. Keep the same class and method names.

## Input

- `chunks`: the list loaded from `data/chunks.json`.
- A question string.
- For hybrid: a `DenseRetriever` and a `BM25Retriever` object.

## What to implement

In `blocks/bm25.py`:

```python
class BM25Retriever:
    def __init__(self, chunks: list[dict]): ...
    def search(self, question: str, k: int) -> list[dict]: ...
```

- Apply `normalize_ar` to chunk texts and questions, remove punctuation, split on whitespace.
- Use `rank_bm25.BM25Okapi`.
- Save the object with `pickle` to `data/index/bm25.pkl`. Load it if it exists.

In `blocks/hybrid.py`:

```python
class HybridRetriever:
    def __init__(self, dense: DenseRetriever, bm25: BM25Retriever): ...
    def search(self, question: str, k: int) -> list[dict]: ...
```

- Take the top 20 from dense and the top 20 from BM25.
- Fuse with Reciprocal Rank Fusion: `score = 1/(60 + rank_dense) + 1/(60 + rank_bm25)`, where ranks start at 1. If a chunk is missing from one list, skip that term.
- Return the top k by fused score.

## Output

Same shape as every retriever, best first:

```json
[{"chunk_id": "law1_2000_a076bis", "score": 0.0325}, {"chunk_id": "law1_2000_a077", "score": 0.0318}]
```

## Done when

- `BM25Retriever.search` finds the right article for a question that uses an exact term from it (for example "بنك ناصر").
- `HybridRetriever.search` returns k unique chunk ids.
- The BM25 object reloads from disk.

## Do not

- Do not add stemming or stopword lists. Keep it plain.
- Do not change the `search` signature. The runner swaps retrievers by name.
