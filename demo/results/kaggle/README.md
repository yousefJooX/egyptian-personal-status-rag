# Kaggle results

Produced by `run.py` on a Kaggle **Tesla T4 (15 GB)**, one config per process,
from commit `c75ad69` (PR #9). torch 2.11, transformers 5.16.
Run twice; all 105 answers were identical between runs.

| Config | Retrieval | LLM | recall@5 | MRR | citation_acc | refusal_acc | avg seconds | peak GPU MB |
|---|---|---|---|---|---|---|---|---|
| `arch1` | e5 dense | Qwen2.5-3B (fp16) | 0.88 | 0.88 | 0.64 | 0.69 | 3.4 | 7674 |
| `arch1_bge` | bge-m3 dense | Qwen2.5-3B (fp16) | 0.92 | 0.89 | 0.72 | 0.80 | 4.4 | 8622 |
| `arch2` | bge-m3 dense | Qwen2.5-7B (4-bit) | 0.92 | 0.89 | 0.86 | 0.89 | 4.9 | 8727 |
| `arch2_qwen3` * | bge-m3 dense | Qwen3-8B (4-bit) | 0.92 | 0.89 | 0.68 | **1.00** | 6.3 | 9507 |
| `arch3_qwen3` * | hybrid + reranker | Qwen3-8B (4-bit) | **0.94** | **0.97** | 0.84 | **1.00** | 7.5 | 10956 |

\* Extra configs, not in the Task 6 spec. Qwen3-8B runs with thinking off.
`cited_chunks`/`refused` for the Qwen3 configs were re-derived from the saved answers
after the parser learned the "رقم المادة: 65" form (commit on PR #9); the answers themselves are unchanged.

Metrics follow the Task 7 definitions over the 35-question test set
(25 answerable). No configuration answered an off-topic question; the
refusal errors are all answerable questions the model refused
(arch1: 11, arch1_bge: 7, arch2: 4, Qwen3 configs: 0).

Not yet run: `arch3`, `arch3_no_rr` (aya8b needs an HF token).
These numbers are preliminary until Task 7's `evaluate.py` reproduces them.
