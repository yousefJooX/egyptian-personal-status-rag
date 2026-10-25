"""Task 6: answer generation.

Loads one instruction model, answers from the given chunks with the fixed
Task 6 prompt, and parses the cited articles and refusals out of the answer.

    llm = LLM("qwen3b")
    llm.generate("سؤال", top_chunks)
    # {"answer": "...", "cited_chunks": ["law1_2000_a076bis"], "refused": False}
"""

from __future__ import annotations

import re

import torch

from utils import normalize_ar

MODELS = {
    "qwen3b": {"id": "Qwen/Qwen2.5-3B-Instruct", "load_in_4bit": False},
    "qwen7b": {"id": "Qwen/Qwen2.5-7B-Instruct", "load_in_4bit": True},
    "aya8b": {"id": "CohereForAI/aya-expanse-8b", "load_in_4bit": True},
    # extra (not in the Task 6 spec); thinking off so it answers directly like the others
    "qwen3_8b": {"id": "Qwen/Qwen3-8B", "load_in_4bit": True, "chat_kwargs": {"enable_thinking": False}},
}

SEED = 42
MAX_NEW_TOKENS = 300

REFUSAL = "لم أجد إجابة في القواعد المتاحة."

PROMPT = """أجب عن السؤال باستخدام النصوص التالية فقط.
اذكر رقم المادة بعد كل معلومة.
إذا لم تجد الإجابة في النصوص قل: "لم أجد إجابة في القواعد المتاحة."

النصوص:
{contexts}

السؤال: {question}"""

# Matched on normalized text: "مادة 76", "المادة (77)", "رقم المادة: 65", "مادة 76 مكرر", "مادة 11 مكررا ثانيا"
CITATION_RE = re.compile(r"مادة\s*:?\s*\(?\s*(\d+)\s*\)?(\s*مكرر\S*(?:\s*\(?\s*(ثانيا|ثالثا))?)?")
BIS_LEVEL = {"ثانيا": "2", "ثالثا": "3"}

# Qwen3 marks reasoning with <think>...</think>; it is off, but never let it reach parsing.
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)

# The refusal sentence without its final period, so "... المتاحة" still counts.
REFUSAL_KEY = normalize_ar(REFUSAL).rstrip(".")


def cited_articles(normalized_answer: str) -> set[str]:
    """'مادة 76 مكرر' -> {'76bis'}, 'المادة 77' -> {'77'}, in the chunks' `article` format."""
    found = set()
    for num, bis, level in CITATION_RE.findall(normalized_answer):
        article = str(int(num))
        if bis:
            article += "bis" + BIS_LEVEL.get(level, "")
        found.add(article)
    return found


def parse_answer(answer: str, chunks: list[dict]) -> dict:
    normalized = normalize_ar(answer)
    refused = REFUSAL_KEY in normalized

    cited_chunks = []
    if not refused:
        articles = cited_articles(normalized)
        cited_chunks = [c["id"] for c in chunks if str(c["article"]) in articles]

    return {"answer": answer, "cited_chunks": cited_chunks, "refused": refused}


class LLM:
    def __init__(self, name: str):
        if name not in MODELS:
            raise ValueError(f"unknown llm {name!r}, expected one of {list(MODELS)}")
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        self.name = name
        self.cfg = MODELS[name]
        model_id = self.cfg["id"]

        print(f"[llm:{name}] loading {model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        if self.cfg["load_in_4bit"]:
            quant = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, quantization_config=quant, device_map="auto"
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, dtype=torch.float16, device_map="auto"
            )
        self.model.eval()

    def generate(self, question: str, chunks: list[dict]) -> dict:
        if not chunks:
            return {"answer": REFUSAL, "cited_chunks": [], "refused": True}

        contexts = "\n\n".join(c["text"] for c in chunks)
        prompt = PROMPT.format(contexts=contexts, question=question)
        text = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
            **self.cfg.get("chat_kwargs", {}),
        )
        # the chat template already contains the special tokens
        inputs = self.tokenizer(text, return_tensors="pt", add_special_tokens=False).to(self.model.device)

        torch.manual_seed(SEED)
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=MAX_NEW_TOKENS,
                pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
            )

        new_tokens = output[0][inputs["input_ids"].shape[1]:]
        answer = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        answer = THINK_RE.sub("", answer).strip()
        return parse_answer(answer, chunks)
