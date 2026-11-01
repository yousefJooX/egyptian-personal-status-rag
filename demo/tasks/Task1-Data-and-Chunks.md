# Task 1: Clean text and chunks

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

Nothing. You are the first link. Everyone else depends on you, so push a 10-chunk sample of `data/chunks.json` (real format, real articles) on day 0.

## Input

`data/rules.pdf`: the rules section of the book (the laws and ministerial decrees).

## What to implement

1. Extract the text. Try PyMuPDF and `pdftotext` on the same pages.
2. Check the result by eye on 20 pages. Known problems in this PDF: the lam-alef ligature comes out reversed (`لا` becomes `ال`, `لأ` becomes `أل`, `لإ` becomes `إل`) and stray alefs appear inside words. If both extractors show this, OCR the pages instead (render at 300 DPI, Tesseract `ara`; use a vision model for pages where Tesseract fails).
3. Split into one chunk per article. Keep the section heading above the article (for example "قواعد تقدير النفقة") at the start of the chunk text, followed by the line "مادة N" and the article body.
4. Build ids and fields as specified below. Decrees restart numbering at "مادة 1", so the `law` field is required.
5. Write `utils.py` with `normalize_ar(text: str) -> str`: remove tashkeel and tatweel, replace أ إ آ with ا, convert Arabic-Indic digits to 0-9. Push it on day 0. Everyone calls it on chunk text and on questions.
6. Write `data/check_chunks.py` and run it: ids are unique, no empty text, article numbers increase inside each law. Fix every flagged chunk by hand. The book has misprints (for example "مادة 76" printed where 67 belongs).

## Output

`data/chunks.json`, a list:

```json
[
  {
    "id": "law1_2000_a076bis",
    "text": "تنفيذ حكم النفقة\nمادة 76 مكرر\nإذا امتنع المحكوم عليه ...",
    "law": "law1_2000",
    "article": "76bis",
    "page": 41
  }
]
```

Rules for the fields:
- `law`: `law{number}_{year}` for laws, `decree{number}_{year}` for ministerial decrees.
- `article`: a string. Number without leading zeros, plus `bis` for مكرر ("76", "76bis").
- `id`: `{law}_a{number padded to 3 digits}` plus `bis` if needed (`law1_2000_a076bis`, `decree1087_2000_a004`).
- `text`: cleaned Arabic, ligature errors fixed. Do not remove tashkeel or unify alef here. Retrievers do that through `normalize_ar`.

## Done when

- `check_chunks.py` reports no problems.
- 20 randomly chosen chunks match the PDF page when read by a person.
- Tasks 2 to 6 can load the file without changes.

## Do not

- Do not change field names or the id format after day 0 without telling the team.
- Do not merge several articles into one chunk.

## Update after the chunk fixes (branch `chunk-fixes`)

**What was wrong.** `is_heading()` in `chunking/chunk_articles.py` treated the last line of two articles as the title of the next article. At a page break the line moved into the wrong chunk:

| Line | Belongs to | Was in |
|---|---|---|
| "إحدى الحدائق العامة" | end of `decree1087_2000_a004` | start of `decree1087_2000_a005` |
| "عدم صلاحيته لأداء العمل من الإحصائيين الاجتماعيين" | end of `decree1089_2000_a003` | start of `decree1089_2000_a004` |

**What changed.**
- Root cause fixed in `chunking/chunk_articles.py`: a `NOT_HEADINGS` set lists those two lines, and `is_heading()` skips them.
- `data/chunks.json` regenerated from the fixed chunker. It is still 188 chunks. Four chunks changed: `decree1087_2000_a004`, `decree1087_2000_a005`, `decree1089_2000_a003`, `decree1089_2000_a004`.
- All 188 chunks were scanned for the same problem. No other spilled lines were found.
- Field names and id format are unchanged.

**Known weak chunk.** `law25_1920_a010` is only 31 characters ("الفرقة بالعيب طلاق بائن"). It is hard for any retriever to find. This is a data limit, not a bug, and it is kept as a failure example.

**After any chunk change.** Delete the cached embeddings in `demo/data/index/` (except `.gitkeep`). The cache name depends only on the embedder, so old embeddings would otherwise be reused. Then re-run the retrieval notebooks.

