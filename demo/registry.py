"""Task 5: wires block names from a config into live objects."""

from blocks.bm25 import BM25Retriever
from blocks.dense import DenseRetriever
from blocks.embedders import Embedder
from blocks.hybrid import HybridRetriever
from blocks.llms import LLM
from blocks.rerankers import Reranker


def build(cfg: dict, chunks: list[dict]):
    embedder = Embedder(cfg["embedder"])
    dense = DenseRetriever(chunks, embedder)

    if cfg["retriever"] == "dense":
        retriever = dense
    elif cfg["retriever"] == "hybrid":
        retriever = HybridRetriever(dense, BM25Retriever(chunks))
    else:
        raise ValueError(f"unknown retriever {cfg['retriever']!r}")

    reranker = Reranker(chunks) if cfg["reranker"] else None
    llm = LLM(cfg["llm"])
    return retriever, reranker, llm
