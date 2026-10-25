"""Task 5: named architectures. run.py and evaluate.py select one by name."""

CONFIGS = {
    "arch1": {"embedder": "e5", "retriever": "dense", "reranker": None, "llm": "qwen3b"},
    "arch2": {"embedder": "bge", "retriever": "dense", "reranker": None, "llm": "qwen7b"},
    "arch3": {"embedder": "bge", "retriever": "hybrid", "reranker": "bge", "llm": "aya8b"},
    "arch1_bge": {"embedder": "bge", "retriever": "dense", "reranker": None, "llm": "qwen3b"},
    "arch3_no_rr": {"embedder": "bge", "retriever": "hybrid", "reranker": None, "llm": "aya8b"},
    # extra: Qwen3-8B, same retrieval as arch2 / arch3 so only the LLM changes
    "arch2_qwen3": {"embedder": "bge", "retriever": "dense", "reranker": None, "llm": "qwen3_8b"},
    "arch3_qwen3": {"embedder": "bge", "retriever": "hybrid", "reranker": "bge", "llm": "qwen3_8b"},
}
