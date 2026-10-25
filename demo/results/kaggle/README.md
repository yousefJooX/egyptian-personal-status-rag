# Kaggle results

Produced by `run.py` on a Kaggle **Tesla T4 (15 GB)**, one config per process,
on the Task 2 test set after #11 (35 questions: 11 literal, 9 paraphrase,
5 multi-article, 10 off-topic). torch 2.11, transformers 5.16.

| Config | Retrieval | LLM | recall@5 | MRR | citation_acc | refusal_acc | avg seconds | peak GPU MB |
|---|---|---|---|---|---|---|---|---|
| `arch1` | e5 dense | Qwen2.5-3B (fp16) | 0.92 | 0.91 | 0.59 | 0.77 | 3.7 | 8028 |
| `arch1_bge` | bge-m3 dense | Qwen2.5-3B (fp16) | 0.92 | 0.91 | 0.75 | 0.86 | 4.2 | 8672 |
| `arch2` | bge-m3 dense | Qwen2.5-7B (4-bit) | 0.92 | 0.91 | **0.86** | 0.91 | 4.3 | 8805 |
| `arch2_qwen3` * | bge-m3 dense | Qwen3-8B (4-bit) | 0.92 | 0.91 | 0.64 | **1.00** | 5.9 | 9615 |
| `arch3_qwen3` * | hybrid + reranker | Qwen3-8B (4-bit) | 0.92 | **1.00** | 0.72 | **1.00** | 6.9 | 11611 |

\* Extra configs, not in the Task 6 spec. Qwen3-8B runs with thinking off.

Metrics follow the Task 7 definitions (recall@5, MRR, citation_acc over the
25 answerable questions; refusal_acc over all 35). No configuration answered
an off-topic question; every refusal error is an answerable question the model
refused (arch1: 8, arch1_bge: 5, arch2: 3, Qwen3 configs: 0).

Not yet run: `arch3`, `arch3_no_rr` (aya8b).
These numbers are preliminary until Task 7's `evaluate.py` reproduces them.
