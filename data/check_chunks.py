import json, re
from pathlib import Path

CHUNKS = Path(__file__).parent / "chunks.json"
ART_RE = re.compile(r"^(\d+)(bis(\d)?)?$")       # "76", "76bis", "11bis2"


def article_key(article):
    """'76' -> (76, 0) | '76bis' -> (76, 1) | '11bis2' -> (11, 2)"""
    m = ART_RE.match(article)
    if not m:
        return None
    num, bis, level = m.groups()
    return int(num), (int(level) if level else 1) if bis else 0


chunks = json.loads(CHUNKS.read_text(encoding="utf-8"))
problems = []

# 1) ids are unique
seen = set()
for c in chunks:
    if c["id"] in seen:
        problems.append(f"duplicate id: {c['id']}")
    seen.add(c["id"])

# 2) no empty text, article format is valid
for c in chunks:
    if not c["text"].strip():
        problems.append(f"empty text: {c['id']}")
    if article_key(c["article"]) is None:
        problems.append(f"bad article format: {c['id']} -> {c['article']!r}")

# 3) article numbers increase inside each law
last = {}
for c in chunks:
    key = article_key(c["article"])
    if key is None:
        continue
    prev = last.get(c["law"])
    if prev and key <= prev[0]:
        problems.append(f"order: {c['id']} comes after {prev[1]}")
    last[c["law"]] = (key, c["id"])

print(len(chunks), "chunks checked")
print("\n".join(problems) if problems else "no problems found")
