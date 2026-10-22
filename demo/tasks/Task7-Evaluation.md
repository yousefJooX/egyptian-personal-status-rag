# Task 7: Evaluation

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

- Task 2 has pushed a sample `data/test_set.json`.
- Task 5 has pushed a working `run.py` with stubs, which produces files in `results/`. Use those files to build and test your script. Do not wait for the real models.

## Input

- `data/test_set.json`
- For each config name: `results/{config}_retrieval.json`, `results/{config}_answers.json`, `results/{config}_cost.json`

Formats are in Task 5 and Task 2.

## What to implement

`python evaluate.py arch1 arch2 arch3 arch1_bge arch3_no_rr`

Compute per config:

| Metric | Definition |
|---|---|
| recall@5 | Answerable questions only. Fraction of the question's gold chunks found in the 5 retrieved, averaged over questions. |
| mrr | Answerable questions only. 1 divided by the rank of the first gold chunk, 0 if none is in the 5. |
| citation_acc | Answerable, not refused. A question is correct if `cited_chunks` is non-empty and every cited chunk is in `gold_chunks`. Report the fraction correct. |
| refusal_acc | All questions. Correct if `refused` equals `not answerable`. |
| avg_seconds | Mean of `seconds` over all questions. |
| peak_gpu_mb | From the cost file. |

## Output

`results/metrics.csv`, one row per config:

```
config,recall@5,mrr,citation_acc,refusal_acc,avg_seconds,peak_gpu_mb
arch1,0.71,0.58,0.62,0.83,2.1,3100
```

Also print the table to the console.

`results/manual_check_{config}.csv`: 20 answerable questions chosen with seed 42, columns:
`qid,question,answer,reference_answer,correct,faithful`. Leave `correct` and `faithful` empty; team members fill them with 1 or 0 (correct: matches the reference; faithful: every claim is in the retrieved chunks). After they are filled, add `manual_correct` and `manual_faithful` (the means) to `metrics.csv`.

`results/failures_{config}.csv`: every question where no gold chunk is in the 5 retrieved, or the citation is wrong, or refusal is wrong. Columns: `qid,question,gold_chunks,retrieved_top5,cited_chunks,refused`. The team picks 10 examples from these for the report.

## Done when

- The script runs on the stub results without errors.
- Each metric is checked by hand on 3 questions against the definition above.
- It runs on the real results with no code changes.

## Do not

- Do not compute a metric over a different set of questions than the table says.
- Do not run the models. This script only reads files.
