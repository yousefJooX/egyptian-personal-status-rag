import json

from chunk_articles import OUT, build_chunks, finalize


def main():
    chunks = finalize(build_chunks())

    ids = [c["id"] for c in chunks]
    dups = sorted({i for i in ids if ids.count(i) > 1})
    words = sorted(c["n_words"] for c in chunks)
    print("duplicate ids:", dups or "none")
    print("words  min:", words[0], " median:", words[len(words) // 2], " max:", words[-1])

    OUT.write_text(json.dumps(chunks, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(chunks), "chunks saved ->", OUT.name)


main()
