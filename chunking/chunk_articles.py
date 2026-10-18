"""Structure-based (article-based) chunking of the personal status laws compilation.
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "personal_status_laws_compilation.txt"
OUT = HERE.parent / "data" / "chunks.json"


LAW_BY_PAGE = [
    # start, end, law_id,          law_name
    (2, 5,   "law25_1920",      "القانون 25 لسنة 1920"),
    (6, 15,  "law25_1929",      "القانون 25 لسنة 1929"),
    (19, 44, "law1_2000",       "القانون 1 لسنة 2000"),
    (45, 45, "decree1086_2000", "قرار وزير العدل 1086 لسنة 2000"),
    (46, 47, "decree1087_2000", "قرار وزير العدل 1087 لسنة 2000"),
    (48, 51, "decree1088_2000", "قرار وزير العدل 1088 لسنة 2000"),
    (52, 55, "decree1089_2000", "قرار وزير العدل 1089 لسنة 2000"),
    (56, 58, "decree1090_2000", "قرار وزير العدل 1090 لسنة 2000"),
    (61, 65, "law10_2004",      "القانون 10 لسنة 2004 (محاكم الأسرة)"),
]


def law_for_page(p):
    """Return (law_id, law_name) for PDF page p, or (None, None) if p is not mapped."""
    for start, end, law_id, law_name in LAW_BY_PAGE:
        if start <= p <= end:
            return law_id, law_name
    return None, None


ARTICLE_RE = re.compile(r"^مادة\s+(\d+)\s*(.*)$")


def article_suffix(num, extra):
    """'1','' -> a001 | '76','مكرر' -> a076bis | '11','مكرر ثانيا' -> a011bis2"""
    s = f"a{int(num):03d}"              # 3 digits so ids sort correctly (a002 < a010)
    if "مكرر" in extra:
        s += "bis"
        if "ثانيا" in extra:
            s += "2"
        if "ثالثا" in extra:
            s += "3"
    return s


def is_heading(line):
    """Short line that is not a sentence -> probably a title."""
    return (0 < len(line.split()) <= 8
            and not line.endswith((".", ":", "،"))   
            and not re.search(r"\d", line)          
            and not line.startswith("ألغيت"))        


def build_chunks(src=SRC):
    chunks = []    # finished articles
    cur = None     # the article we're filling right now
    page = 0       # current PDF page

    for raw in open(src, encoding="utf-8"):
        line = raw.strip()

        # (A) page marker -> remember the page
        m = re.match(r"^=== صفحة (\d+) ===$", line)
        if m:
            page = int(m.group(1))
            continue

        law_id, law_name = law_for_page(page)
        m = ARTICLE_RE.match(line)

        # (B) a new article starts
        if m and law_id:
            heading = []
            if cur:
                # move titles from the end of the previous article to this one
                # (keep at least one body line: some articles are a single short line)
                while len(cur["lines"]) > 1 and is_heading(cur["lines"][-1]):
                    heading.insert(0, cur["lines"].pop())
                chunks.append(cur)
            num, extra = m.group(1), m.group(2).strip()
            label = (num + " " + re.sub(r"\(.*?\)", "", extra)).strip()   # "76 مكرر", drop "(مضافة)"
            suffix = article_suffix(num, extra)                               # "a076bis"
            cur = {"id": f"{law_id}_{suffix}",
                   "law": law_id, "law_name": law_name,
                   "article": suffix[1:].lstrip("0"),                         # "76bis"
                   "label": label,
                   "heading": " | ".join(heading), "page": page, "lines": []}
            continue

        # (C) a normal line -> add it to the current article
        if cur and line:
            # stop if we left this law's pages or a new law/decree title starts
            if law_id != cur["law"] or line.startswith(("القانون رقم", "قرار وزير العدل رقم")):
                chunks.append(cur)
                cur = None
                continue
            cur["lines"].append(line)

    if cur:
        chunks.append(cur)
    return chunks



def finalize(chunks):
    # text = section title (if any) + "مادة N" line + article body  (Task 1 spec)
    out = []
    for c in chunks:
        body = "\n".join(c["lines"])
        title = c["heading"].replace(" | ", "\n")
        text = (title + "\n" if title else "") + f"مادة {c['label']}\n" + body
        out.append({"id": c["id"], "text": text, "law": c["law"], "article": c["article"],
                    "page": c["page"], "law_name": c["law_name"], "heading": c["heading"],
                    "n_words": len(body.split())})
    return out

