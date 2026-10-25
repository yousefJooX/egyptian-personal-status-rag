"""Task 6 "Done when" checks.

    python check_llm.py              # parsing checks only (no model)
    python check_llm.py qwen3b       # + one answerable and one off-topic question

1. Parsing handles "مادة ٧٦ مكرر", "المادة 77", near-miss numbers and refusals.
2. The model answers an answerable question with the right citation.
3. The model refuses an off-topic question.
"""

import json
import sys
from pathlib import Path

from blocks.llms import parse_answer

CHUNKS_PATH = Path(__file__).resolve().parents[1] / "data" / "chunks.json"


def check_parsing(chunks_by_id: dict) -> bool:
    given = [chunks_by_id[i] for i in ["law1_2000_a076bis", "law1_2000_a077", "law1_2000_a007", "law1_2000_a017"]]
    cases = [
        ("يجوز حبسه (مادة ٧٦ مكرر)", ["law1_2000_a076bis"], False),
        ("الأولوية لنفقة الزوجة (المادة 77)", ["law1_2000_a077"], False),
        ("انظر المادة (7)", ["law1_2000_a007"], False),
        ("مادة 76 مكرراً ومادة 17", ["law1_2000_a076bis", "law1_2000_a017"], False),
        ("لم أجد إجابة في القواعد المتاحة.", [], True),
        ("لم أجد إجابة في القواعد المتاحة", [], True),
        ("الإجابة بدون رقم مادة", [], False),
    ]
    ok = True
    for answer, want_cited, want_refused in cases:
        got = parse_answer(answer, given)
        passed = sorted(got["cited_chunks"]) == sorted(want_cited) and got["refused"] == want_refused
        ok &= passed
        print(f"   {'OK  ' if passed else 'FAIL'} {answer!r} -> {got['cited_chunks']} refused={got['refused']}")
    return ok


def check_model(name: str, chunks_by_id: dict) -> bool:
    from blocks.llms import LLM

    llm = LLM(name)
    given = [chunks_by_id[i] for i in ["law1_2000_a076bis", "law1_2000_a077", "law1_2000_a065"]]

    answered = llm.generate("هل ممكن المحكمة تحبس الشخص اللي مش بينفذ حكم النفقة؟", given)
    print(f"   answerable: {answered['answer']!r}\n     -> cited {answered['cited_chunks']} refused={answered['refused']}")
    cite_ok = "law1_2000_a076bis" in answered["cited_chunks"] and not answered["refused"]

    off_topic = llm.generate("إزاي أطبخ الملوخية؟", given)
    print(f"   off-topic: {off_topic['answer']!r}\n     -> refused={off_topic['refused']}")
    refuse_ok = off_topic["refused"]

    print(f"2. correct citation  ->  {'OK' if cite_ok else 'FAIL'}")
    print(f"3. refuses off-topic ->  {'OK' if refuse_ok else 'FAIL'}")
    return cite_ok and refuse_ok


def main() -> None:
    chunks_by_id = {c["id"]: c for c in json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))}
    print("1. parsing")
    results = {"parsing": check_parsing(chunks_by_id)}
    for name in sys.argv[1:]:
        print(f"\n===== {name} =====")
        results[name] = check_model(name, chunks_by_id)
    print("\n" + "  ".join(f"{n}: {'PASS' if ok else 'FAIL'}" for n, ok in results.items()))


if __name__ == "__main__":
    main()
