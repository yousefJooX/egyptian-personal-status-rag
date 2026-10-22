# Task 6: LLM block

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
- Task 5 has pushed a stub `blocks/llms.py`. Replace it. Keep the class and method names.
- You do not need retrieval to work. Test with chunks you pick by hand.

## Input

`generate` receives a question string and a list of 5 chunk dicts (the format of `chunks.json`).

## What to implement

```python
class LLM:
    def __init__(self, name: str): ...                       # "qwen3b", "qwen7b", "aya8b"
    def generate(self, question: str, chunks: list[dict]) -> dict: ...
```

Models:
- `qwen3b`: `Qwen/Qwen2.5-3B-Instruct`.
- `qwen7b`: `Qwen/Qwen2.5-7B-Instruct`, 4-bit (`BitsAndBytesConfig`).
- `aya8b`: `CohereForAI/aya-expanse-8b`, 4-bit. You may need to accept the license on HuggingFace first, do it today. If access is delayed, tell the team and use `qwen7b` in its place.

Generation settings: `do_sample=False`, `max_new_tokens=300`, seed 42. Use each model's chat template.

Prompt (exactly this; `{contexts}` is the chunk texts joined by a blank line):

```
أجب عن السؤال باستخدام النصوص التالية فقط.
اذكر رقم المادة بعد كل معلومة.
إذا لم تجد الإجابة في النصوص قل: "لم أجد إجابة في القواعد المتاحة."

النصوص:
{contexts}

السؤال: {question}
```

Parsing the answer:
- Pass the answer through `normalize_ar` (this converts Arabic-Indic digits).
- Find article numbers after "مادة" or "المادة", with optional "مكرر" (gives "76bis").
- `cited_chunks` = ids of the given chunks whose `article` matches a cited number. If two given chunks share the number, cite both.
- `refused` = the normalized answer contains the normalized refusal sentence. If refused, `cited_chunks` is empty.

## Output

```json
{
  "answer": "تشترط القواعد ... (مادة 76 مكرر)",
  "cited_chunks": ["law1_2000_a076bis"],
  "refused": false
}
```

## Done when

- Each of the three models answers an answerable question with a correct citation and refuses an off-topic one, using chunks you chose by hand.
- Parsing handles "مادة ٧٦ مكرر" and "المادة 77".
- You have read 5 answers per model and noted whether it follows the citation rule. A 3B model may not.

## Do not

- Do not change the prompt wording. All configs must use the same prompt.
- Do not load more than one model at a time. The runner uses one config per process.
