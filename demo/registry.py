"""Task 5: wires block names from a config into live objects.

Retrieval and generation are built separately so run.py can free the
retrieval models before the LLM is loaded (one 6-8 GB GPU cannot hold both).
"""

from blocks.bm25 import BM25Retriever
from blocks.dense import DenseRetriever
from blocks.embedders import Embedder
from blocks.hybrid import HybridRetriever
from blocks.rerankers import Reranker


def build_retrieval(cfg: dict, chunks: list[dict]):
    embedder = Embedder(cfg["embedder"])
    dense = DenseRetriever(chunks, embedder)

    if cfg["retriever"] == "dense":
        retriever = dense
    elif cfg["retriever"] == "hybrid":
        retriever = HybridRetriever(dense, BM25Retriever(chunks))
    else:
        raise ValueError(f"unknown retriever {cfg['retriever']!r}")

    reranker = Reranker(chunks) if cfg["reranker"] else None
    return retriever, reranker


def release_retrieval() -> None:
    Reranker.release()


def build_llm(cfg: dict):
    from blocks.llms import LLM

    return LLM(cfg["llm"])


def build(cfg: dict, chunks: list[dict]):
    retriever, reranker = build_retrieval(cfg, chunks)
    return retriever, reranker, build_llm(cfg)
