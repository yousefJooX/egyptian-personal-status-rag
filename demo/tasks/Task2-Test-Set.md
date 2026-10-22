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

## Done when

- Every id in `gold_chunks` exists in `chunks.json` (check with a short script).
- 30 to 40 questions, at least 6 with `answerable: false`.
- A second team member has read each reference answer against the article and agrees.

## Do not

- Do not use questions copied from the book's Q&A section.
- Do not label a question answerable if the answer needs knowledge outside the chunks.
