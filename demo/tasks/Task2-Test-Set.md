# Task 2: Test set

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

Task 1 has pushed the 10-chunk sample `data/chunks.json` and `utils.py`. Work with the sample first. When the full `chunks.json` is pushed, replace the ids.

## Input

`data/chunks.json` (ids and article texts). Each team member writes 5 questions and sends them to you; you also write your own.

## What to implement

Write 30 to 40 questions:
- At least 6 off-topic questions the text cannot answer. Mix two kinds: unrelated (cooking, football) and legal but not covered by the text. For the second kind, search `chunks.json` for the key words first to confirm the answer is not there.
- At least 5 questions that need two or more chunks.
- The rest need one chunk. Make about half use the article's own words and half paraphrase it.
- Phrase each question as a normal person would ask it. Do not copy the article sentence as the question.

For each answerable question write a reference answer: one or two sentences, ending with the article number in the form "(مادة N)".

## Output

`data/test_set.json`, a list:

```json
[
  {
    "qid": "q_001",
    "question": "هل يمكن حبس من يمتنع عن دفع النفقة؟",
    "gold_chunks": ["law1_2000_a076bis"],
    "answerable": true,
    "reference_answer": "نعم إذا ثبت قدرته على الأداء، بالحبس مدة لا تزيد على ثلاثين يوما (مادة 76 مكرر)"
  },
  {
    "qid": "q_031",
    "question": "كيف أطبخ الملوخية؟",
    "gold_chunks": [],
    "answerable": false,
    "reference_answer": "لم أجد إجابة في القواعد المتاحة."
  }
]
```

- `qid`: `q_001`, `q_002`, ... unique.
- `gold_chunks`: list of chunk ids from `chunks.json`. Empty list for off-topic questions.
- `type`: one of `literal`, `paraphrase`, `multi`, `off_topic`. The evaluation notebooks read it (they also accept `qtype`) to break results down by question kind.

## Done when

- Every id in `gold_chunks` exists in `chunks.json` (check with a short script).
- 30 to 40 questions, at least 6 with `answerable: false`.
- A second team member has read each reference answer against the article and agrees.

## Do not

- Do not use questions copied from the book's Q&A section.
- Do not label a question answerable if the answer needs knowledge outside the chunks.

## Update after the chunk fixes (branch `chunk-fixes`)

**What was wrong.** For q_015 and q_022 the question was fully answered by one chunk, but two chunks were listed as gold. A retriever that found the right answer was still counted as missing the second chunk.

**What changed.** The two questions were reworded so both gold chunks are really needed. Gold lists and reference answers were not changed.

| Question | Old | New |
|---|---|---|
| q_015 | ...مين بيتدخل وإيه الإجراء الممكن؟ | same, plus: وهل يجوز إعادة التنفيذ ودخول المنازل؟ |
| q_022 | مين بيحضر وجوبًا في قضايا الطلاق والحضانة، وإيه المطلوب منه بعد كده؟ | مين الخبراء اللي بيحضروا وجوبًا ... وبيتكونوا من أي تخصصات، وإيه المطلوب منهم بعد كده؟ |

**Test set after the change.** Still 35 questions: 11 `literal`, 9 `paraphrase`, 5 `multi`, 10 `off_topic` (25 answerable). The 5 multi-chunk questions required by this task are kept.

**Things to state openly in the report.**
- Two questions were reworded after the first retrieval test. Part of the recall gain on them comes from the changed test set, not from better retrieval.
- q_025 is kept unchanged on purpose. Its second gold chunk is 31 characters long, so it is a genuine hard case for the failure analysis.
- The question kind is stored under `type`. The notebooks read `type` as well as `qtype`.

**Retrieval results after the fix** (recall@5, 25 answerable questions, old on `main` and new on `chunk-fixes`):

| Retriever | Old | New | mrr@5 (new) |
|---|---|---|---|
| hybrid_rr | 0.92 | 0.98 | 1.0 |
| bge | 0.92 | 0.96 | 0.91 |
| e5 | 0.92 | 0.94 | 0.893 |
| hybrid | 0.88 | 0.90 | 0.841 |
| hybrid_e5 | 0.86 | 0.88 | 0.813 |
| bm25 | 0.76 | 0.78 | 0.667 |

The gain is mostly from the reworded questions (q_015 improved in all six retrievers). The chunk fix improved only hybrid_rr on q_004. hybrid_rr is still the best retriever.

