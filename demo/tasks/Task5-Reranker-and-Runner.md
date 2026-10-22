# Task 5: Reranker, runner and configs

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

You start first, on day 0, before the real blocks exist:
1. Push stub files for `blocks/embedders.py`, `blocks/dense.py`, `blocks/bm25.py`, `blocks/hybrid.py`, `blocks/llms.py`. A stub has the same classes and method signatures as the real one and returns fake data in the correct shape.
2. Push `registry.py`, `configs.py` and `run.py` working end to end with the stubs.

Tasks 3, 4 and 6 replace the stubs. Task 1 provides `chunks.json`, Task 2 provides `test_set.json`; use the sample versions first.

## Input

- `data/chunks.json` and `data/test_set.json`.
- A config name from the command line.

## What to implement

`blocks/rerankers.py`:

```python
class Reranker:
    def __init__(self, chunks: list[dict]): ...
    def rerank(self, question: str, hits: list[dict], k: int) -> list[dict]: ...
```

Use `BAAI/bge-reranker-v2-m3` through `FlagEmbedding.FlagReranker` (fp16). Score the question against each hit's chunk text, sort, keep k. Output items: `{"rank": 1, "chunk_id": "...", "score": 0.91}`.

`configs.py`:

```python
CONFIGS = {
  "arch1":       {"embedder": "e5",  "retriever": "dense",  "reranker": None, "llm": "qwen3b"},
  "arch2":       {"embedder": "bge", "retriever": "dense",  "reranker": None, "llm": "qwen7b"},
  "arch3":       {"embedder": "bge", "retriever": "hybrid", "reranker": "bge", "llm": "aya8b"},
  "arch1_bge":   {"embedder": "bge", "retriever": "dense",  "reranker": None, "llm": "qwen3b"},
  "arch3_no_rr": {"embedder": "bge", "retriever": "hybrid", "reranker": None, "llm": "aya8b"},
}
```

`registry.py`: `build(cfg, chunks)` returns `(retriever, reranker_or_None, llm)`, creating blocks from the names in the config.

`run.py`: `python run.py arch1` (and `--retrieval-only` to skip the LLM). One config per process. For each question in `test_set.json`:
1. Fixed settings: top_k 5, candidates 20, seed 42.
2. If there is a reranker: `hits = retriever.search(q, 20)`, then `results = reranker.rerank(q, hits, 5)`. If not: `hits = retriever.search(q, 5)` and add `rank` 1 to 5.
3. Look up the 5 chunks by id and call `llm.generate(q, chunks)`. Measure the seconds.
4. After all questions, record peak GPU memory (`torch.cuda.max_memory_allocated`).

## Output

Written to `results/`:

`{config}_retrieval.json`
```json
[{"qid": "q_001", "results": [{"rank": 1, "chunk_id": "law1_2000_a076bis", "score": 0.82}]}]
```

`{config}_answers.json`
```json
[{"qid": "q_001", "answer": "...", "cited_chunks": ["law1_2000_a076bis"], "refused": false, "seconds": 3.4}]
```

`{config}_cost.json`
```json
{"peak_gpu_mb": 7400}
```

## Done when

- With stubs, `python run.py arch1` produces the three files, one entry per question.
- With real blocks, all five configs run.
- Re-running a config does not re-embed (cache is used).

## Do not

- Do not put model-specific code in `run.py`. It only calls the block methods.
- Do not change an interface without telling the team.
