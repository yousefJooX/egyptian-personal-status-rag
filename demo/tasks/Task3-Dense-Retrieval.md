# Task 3: Embedders and dense retriever

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
- Task 5 has pushed stub versions of `blocks/embedders.py` and `blocks/dense.py`. Replace them. Keep the same class and method names.

## Input

- `chunks`: the list loaded from `data/chunks.json`.
- A question string.

## What to implement

In `blocks/embedders.py`:

```python
class Embedder:
    def __init__(self, name: str): ...        # "e5" or "bge"
    def encode(self, texts: list[str], is_query: bool) -> np.ndarray: ...
```

- `e5`: `intfloat/multilingual-e5-base`, dimension 768. Add the prefix "passage: " to chunk texts and "query: " to questions, inside `encode`. Set max sequence length 512.
- `bge`: `BAAI/bge-m3`, dimension 1024. No prefixes. Set max sequence length 1024.
- Apply `normalize_ar` to every text before encoding.
- Return float32, L2-normalized, shape (len(texts), dim).
- Print how many chunks exceed the max length and get truncated.

In `blocks/dense.py`:

```python
class DenseRetriever:
    def __init__(self, chunks: list[dict], embedder: Embedder): ...
    def search(self, question: str, k: int) -> list[dict]: ...
```

- Build a FAISS `IndexFlatIP` from the chunk embeddings.
- Cache embeddings and index in `data/index/{embedder name}.npy` and `.faiss`. Load from the cache if it exists.

## Output

`search` returns the k best chunks, best first:

```json
[{"chunk_id": "law1_2000_a076bis", "score": 0.82}, {"chunk_id": "law1_2000_a077", "score": 0.77}]
```

## Done when

- Embedding shape is (N, 768) for e5 and (N, 1024) for bge, with N equal to the number of chunks.
- Taking a sentence from an article and searching it returns that article in the top 5, for both embedders.
- A second run loads from the cache without re-encoding.

## Do not

- Do not put model details (prefixes, max length) anywhere except `embedders.py`.
- Do not return anything other than the output shape above.
