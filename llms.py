"""STUB for Task 6. Returns fake data in the right shape.

Task 6 replaces this file. Keep the class and method names.
"""


import torch
import re
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from utils import normalize_ar

class LLM:
    def __init__(self, name: str):
        self.name = name
        
        if name == "qwen3b":
            model_id = "Qwen/Qwen2.5-3B-Instruct"
            load_in_4bit = False
        elif name == "qwen7b":
            model_id = "Qwen/Qwen2.5-7B-Instruct"
            load_in_4bit = True
        elif name == "aya8b":
            model_id = "CohereForAI/aya-expanse-8b"
            load_in_4bit = True
        else:
            raise ValueError(f"Unknown model name: {name}")

        print(f"[*] Loading Tokenizer for {model_id}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

        print(f"[*] Loading Model {model_id}...")
        if load_in_4bit:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4"
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=quantization_config,
                device_map="auto"
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                device_map="auto"
            )

    def generate(self, question: str, chunks: list[dict]) -> dict:
        if not chunks:
            return {
                "answer": "لم أجد إجابة في القواعد المتاحة.",
                "cited_chunks": [],
                "refused": True,
            }

        contexts_text = "\n\n".join([chunk.get("text", "") for chunk in chunks])

        prompt = f"""أجب عن السؤال باستخدام النصوص التالية فقط.
اذكر رقم المادة بعد كل معلومة.
إذا لم تجد الإجابة في النصوص قل: "لم أجد إجابة في القواعد المتاحة."

النصوص:
{contexts_text}

السؤال: {question}"""

        messages = [
            {"role": "system", "name": "example", "content": "أنت مساعد قانوني مصري دقيق ملتزم بالنصوص فقط."},
            {"role": "user", "content": prompt}
        ]
        
        text_input = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )

        inputs = self.tokenizer([text_input], return_tensors="pt").to(self.model.device)

        torch.manual_seed(42)
        with torch.no_rad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=300,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )

        generated_ids = [
            output[len(input_ids):] for input_ids, output in zip(inputs.input_ids, outputs)
        ]
        answer = self.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0].strip()

        normalized_answer = normalize_ar(answer)
        refusal_phrase = normalize_ar("لم أجد إجابة في القواعد المتاحة.")
        refused = refusal_phrase in normalized_answer

        cited_chunks = []
        if not refused:
            pattern = r"(?:المادة|مادة)\s*(\d+)\s*(مكرر|bis)?"
            matches = re.findall(pattern, normalized_answer)

            found_articles = []
            for match in matches:
                art_num = match[0]
                modifier = match[1]
                if modifier:
                    art_num_str = f"{art_num}مكرر" if "مكرر" in modifier else f"{art_num}{modifier}"
                else:
                    art_num_str = art_num
                found_articles.append(art_num_str)

            for chunk in chunks:
                chunk_article = str(chunk.get("article", ""))
                if any(art in chunk_article for art in found_articles):
                    chunk_id = chunk.get("id")
                    if chunk_id and chunk_id not in cited_chunks:
                        cited_chunks.append(chunk_id)

        return {
            "answer": answer,
            "cited_chunks": cited_chunks,
            "refused": refused
        }
