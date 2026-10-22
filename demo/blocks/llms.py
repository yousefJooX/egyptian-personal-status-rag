"""STUB for Task 6. Returns fake data in the right shape.

Task 6 replaces this file. Keep the class and method names.
"""


class LLM:
    def __init__(self, name: str):
        self.name = name

    def generate(self, question: str, chunks: list[dict]) -> dict:
        if not chunks:
            return {
                "answer": "لم أجد إجابة في القواعد المتاحة.",
                "cited_chunks": [],
                "refused": True,
            }
        top = chunks[0]
        return {
            "answer": f"إجابة تجريبية من {self.name} (مادة {top.get('article', '?')}).",
            "cited_chunks": [top["id"]],
            "refused": False,
        }
