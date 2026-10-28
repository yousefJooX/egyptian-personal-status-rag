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
  run_kaggle.py        task 5 (optional batch runner for Kaggle)
  notebooks/           task 7 (replaces evaluate.py)
    01_retrieval_test.ipynb
    02_retrieval_compare.ipynb
    03_llm_gold_chunks_test.ipynb
    04_full_pipeline_run.ipynb
    05_evaluate_all.ipynb
  results/             created by run.py and the notebooks
    {config}_retrieval.json         run.py or notebook 04
    {config}_answers.json           run.py or notebook 04
    {config}_cost.json              run.py or notebook 04
    {config}_timing.json            notebook 04 (extra: retrieval vs generation seconds)
    retrieval_test_{retriever}.json notebook 01
    retrieval_compare.csv           notebook 02
    retrieval_decision.json         notebook 02
    llm_gold_{llm}_*.json / .csv    notebook 03
    llm_gold_compare.csv            notebook 03
    metrics.csv                     notebook 05
    metrics_by_type.csv             notebook 05
    metrics_counts.csv              notebook 05
    manual_check_{config}.csv       notebook 05
    failures_{config}.csv           notebook 05
```

In the GitHub repo this same tree sits under `demo/` (with `data/chunks.json` one level up). The notebooks find the right folders automatically, so do not move files.

## Before you start

- Task 2 has pushed a sample `data/test_set.json`.
- Task 5 has pushed a working `run.py` with stubs, which produces files in `results/`. Use those files to test notebook 05. Do not wait for the real models.
- Every notebook needs only the repo and `results/`. Notebooks 01, 03 and 04 need a GPU (Colab T4 or Kaggle). Notebooks 02 and 05 need no GPU and never load a model.

## Input

- `data/test_set.json`
- For each config name: `results/{config}_retrieval.json`, `results/{config}_answers.json`, `results/{config}_cost.json`

Formats are in Task 5 and Task 2.

## What to implement

Five notebooks. Phases A and B run in parallel across teammates, one setting per session.

| Phase | Notebook | Setting to change | Who | Needs |
|---|---|---|---|---|
| A | `01_retrieval_test` | `RETRIEVER`: e5, bge, bm25, hybrid, hybrid_rr (optional hybrid_e5) | one person per retriever | GPU for e5, bge, reranker |
| A | `03_llm_gold_chunks_test` | `LLM_NAME`: qwen3b, qwen7b, aya8b | one person per LLM | GPU, HF token for aya8b |
| B | `02_retrieval_compare` | none | one person | reads the `retrieval_test_*.json` files |
| B | `04_full_pipeline_run` | `CONFIG_NAME`: arch1, arch2, arch3, arch1_bge, arch3_no_rr | one person per config | GPU, HF token for aya8b |
| C | `05_evaluate_all` | `CONFIGS_TO_SCORE` | one person | reads files only |

Order: 01 and 03 together, then 02, then 04, then 05. `run_kaggle.py` can replace 04 when one person runs all configs in one Kaggle session. Notebook 05 reads its files too.

### Notebook 05 (this is the Task 7 deliverable)

Computes per config:

| Metric | Definition |
|---|---|
| recall@5 | Answerable questions only. Fraction of the question's gold chunks found in the 5 retrieved, averaged over questions. |
| mrr | Answerable questions only. 1 divided by the rank of the first gold chunk, 0 if none is in the 5. |
| citation_acc | Answerable, not refused. A question is correct if `cited_chunks` is non-empty and every cited chunk is in `gold_chunks`. A missing citation counts as wrong. Report the fraction correct. |
| refusal_acc | All questions. Correct if `refused` equals `not answerable`. |
| avg_seconds | Mean of `seconds` over all questions. |
| peak_gpu_mb | From the cost file. |

A config whose files are missing is skipped with a warning. A missing cost file leaves `peak_gpu_mb` empty.

## Output

`results/metrics.csv`, one row per config:

```
config,recall@5,mrr,citation_acc,refusal_acc,avg_seconds,peak_gpu_mb
arch1,0.71,0.58,0.62,0.83,2.1,3100
```

Also print the table to the console (the notebook does).

`results/manual_check_{config}.csv`: 20 answerable questions chosen with seed 42, columns:
`qid,question,answer,reference_answer,correct,faithful`. Leave `correct` and `faithful` empty; team members fill them with 1 or 0 (correct: matches the reference; faithful: every claim is in the retrieved chunks). After they are filled, notebook 05 adds `manual_correct` and `manual_faithful` (the means) to `metrics.csv`. Re-running notebook 05 never overwrites a manual check file that has been filled.

`results/failures_{config}.csv`: every question where no gold chunk is in the 5 retrieved, or the citation is wrong, or refusal is wrong. Columns: `qid,question,gold_chunks,retrieved_top5,cited_chunks,refused`. The team picks 10 examples from these for the report.

Extra files (not required by the spec, they help the decision):
- `metrics_by_type.csv`: the same metrics for single-chunk, multi-chunk and unanswerable questions (and for `qtype` if you add that field to the test set).
- `metrics_counts.csv`: raw counts like 27/34. With 30 to 40 questions, a gap of 1 or 2 questions between configs is noise.
- `retrieval_compare.csv` and `retrieval_decision.json` (notebook 02): recall@1, 3, 5, 10, 20 and the chosen retrieval setup.
- `llm_gold_compare.csv` (notebook 03): the LLMs compared when they are given the correct chunks.

## Done when

- Notebook 05 runs on the stub results without errors.
- Each metric is checked by hand on 3 questions against the definitions above (notebook 05 prints the per-question numbers for this).
- It runs on the real results with no code changes.
- Notebook 02 and notebook 03's last cell run once all their input files are in `results/`.

## Do not

- Do not compute a metric over a different set of questions than the table says.
- Do not run the models in notebook 02 or 05. They only read files.
- Do not load more than one model per session. Restart the session before running another config or LLM.
- Do not choose a block on a difference of 1 or 2 questions. Use the manual check to break ties.
