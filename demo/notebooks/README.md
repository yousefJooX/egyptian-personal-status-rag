# Notebooks for Colab/Kaggle

This directory contains Jupyter notebooks for running the Egyptian Personal Status RAG pipeline on cloud platforms (Google Colab or Kaggle).

## 📓 Available Notebooks

### 1. `Full_Pipeline_Colab_Kaggle.ipynb` ⭐ **NEW**
**Complete end-to-end pipeline** - runs all tasks from retrieval to evaluation.

**What it does:**
- ✅ Task 3: Dense retrieval (e5/bge embedders + FAISS)
- ✅ Task 4: BM25 & Hybrid retrieval (RRF)
- ✅ Task 5: Reranking with bge-reranker-v2-m3
- ✅ Task 6: LLM generation (Qwen 3B/7B, Aya 8B, Qwen3-8B)
- ✅ Task 7: Evaluation metrics (recall@5, MRR, citation_acc, etc.)
- 💾 Saves results to JSON files
- 📊 Displays sample outputs and metrics

**Perfect for:**
- Running complete experiments on different configs
- Comparing architectures (arch1, arch2, arch3, etc.)
- Generating results for analysis

### 2. `t3_dense_retrieval.ipynb`
**Task 3 focused** - explores dense retrieval with embedders.

**What it does:**
- Tests e5 and bge-m3 embedders
- Builds FAISS index
- Demonstrates search and self-retrieval
- Educational/exploratory notebook

---

## 🚀 How to Run on Colab

### Option 1: Direct Link (Recommended)
Click this link to open directly in Colab:

```
https://colab.research.google.com/github/yousefJooX/egyptian-personal-status-rag/blob/main/demo/notebooks/Full_Pipeline_Colab_Kaggle.ipynb
```

### Option 2: Manual Upload
1. Go to [Google Colab](https://colab.research.google.com/)
2. File → Upload notebook
3. Upload `Full_Pipeline_Colab_Kaggle.ipynb`
4. Enable GPU: Runtime → Change runtime type → Hardware accelerator: **GPU (T4)**

### Step-by-Step:
1. **Enable GPU** (Runtime → Change runtime type → GPU)
2. Run the setup cells to clone repo and install dependencies
3. **Choose your configuration:**
   - Edit `CONFIG_NAME` variable (e.g., `"arch1"`, `"arch2"`, `"arch3"`)
   - Edit `EMBEDDER_NAME` for retrieval tests (`"e5"` or `"bge"`)
   - Edit `LLM_NAME` for generation (`"qwen3b"`, `"qwen7b"`, `"aya8b"`)
4. Run all cells (Runtime → Run all)
5. Download results at the end

---

## 🔬 How to Run on Kaggle

### Step 1: Create New Notebook
1. Go to [Kaggle](https://www.kaggle.com/)
2. Create → New Notebook
3. Settings → **Accelerator: GPU T4 x2** (or P100)
4. Settings → **Internet: ON** (required for cloning repo)

### Step 2: Copy-Paste Cells
1. Copy all cells from `Full_Pipeline_Colab_Kaggle.ipynb`
2. Paste into Kaggle notebook cells
3. Run all cells

### Step 3: Save Results
Results are saved to `/kaggle/working/egyptian-personal-status-rag/demo/results/`

You can download them from the Kaggle notebook output or commit them to a Kaggle dataset.

---

## ⚙️ Configuration Options

### Available Configs (in `configs.py`):
```python
CONFIGS = {
    "arch1":       {"embedder": "e5",  "retriever": "dense",  "reranker": None, "llm": "qwen3b"},
    "arch1_bge":   {"embedder": "bge", "retriever": "dense",  "reranker": None, "llm": "qwen3b"},
    "arch2":       {"embedder": "bge", "retriever": "dense",  "reranker": None, "llm": "qwen7b"},
    "arch3_no_rr": {"embedder": "bge", "retriever": "hybrid", "reranker": None, "llm": "aya8b"},
    "arch3":       {"embedder": "bge", "retriever": "hybrid", "reranker": "bge", "llm": "aya8b"},
    "arch2_qwen3": {"embedder": "bge", "retriever": "dense",  "reranker": None, "llm": "qwen3_8b"},
    "arch3_qwen3": {"embedder": "bge", "retriever": "hybrid", "reranker": "bge", "llm": "qwen3_8b"},
}
```

### To Run a Different Config:
Change this cell in the notebook:
```python
CONFIG_NAME = "arch3"  # ← Change this
```

---

## 📊 Expected Output

After running, you'll get:

### 1. **Metrics Summary**
```
📊 Evaluation Metrics for arch1:
  recall@5:       0.712
  mrr:            0.583
  citation_acc:   0.621
  refusal_acc:    0.829
  avg_seconds:    2.14
  peak_gpu_mb:    3108
```

### 2. **Result Files**
- `{config}_retrieval.json` - Top 5 retrieved chunks per question
- `{config}_answers.json` - LLM answers with citations
- `{config}_cost.json` - GPU memory usage

### 3. **Sample Outputs**
Shows 5 random Q&A examples with gold vs predicted citations

---

## 💡 Tips

### For Faster Iteration:
1. **Start with `arch1`** (smallest model: qwen3b)
2. Test on a subset first (edit `test_set = test_set[:10]`)
3. Use `"qwen3b"` for quick experiments

### For Best Results:
1. **Use `arch3`** (hybrid retrieval + reranker + aya8b)
2. Run on Kaggle with **P100 GPU** for more memory
3. For Aya 8B model, you may need to accept license on HuggingFace

### GPU Memory Issues:
- **Colab Free Tier (T4)**: 15GB → Use `qwen3b` or `qwen7b` (4-bit)
- **Kaggle (P100)**: 16GB → Can run all models including `aya8b`
- If OOM, reduce batch size in `embedders.py` or use smaller models

---

## 🐛 Troubleshooting

### "GPU not available"
- Colab: Runtime → Change runtime type → GPU
- Kaggle: Settings → Accelerator → GPU T4 x2

### "Repository not found"
Check the git clone URL is correct:
```bash
!git clone https://github.com/yousefJooX/egyptian-personal-status-rag.git
```

### "No module named 'utils'"
Make sure `sys.path.insert(0, str(ROOT))` ran successfully. Check that `ROOT` points to the repo root.

### Model download fails
- Colab/Kaggle need internet access
- Some models (like Aya) require accepting license on HuggingFace
- Try a different model first (e.g., qwen3b)

### Out of Memory (OOM)
```python
# Reduce batch size in blocks/embedders.py line 62
batch_size=16,  # Default is 32
```

Or use 4-bit quantized models (qwen7b, aya8b already use 4-bit).

---

## 📝 Notes

- The notebook automatically detects Colab vs Kaggle environment
- First run downloads ~3-8GB of models (cached afterwards)
- Full pipeline on 35 questions takes:
  - **arch1** (qwen3b): ~5-10 minutes
  - **arch2** (qwen7b): ~10-15 minutes  
  - **arch3** (aya8b + reranker): ~15-25 minutes
- Results are saved in `demo/results/` directory

---

## 🔗 Links

- **Repository**: https://github.com/yousefJooX/egyptian-personal-status-rag
- **Colab Link**: https://colab.research.google.com/github/yousefJooX/egyptian-personal-status-rag/blob/main/demo/notebooks/Full_Pipeline_Colab_Kaggle.ipynb
- **Demo Task Specs**: `demo/tasks/`
- **Results on Kaggle**: `demo/results/kaggle/`

---

## 👥 Team

This is a team project for Egyptian Personal Status RAG system. Each task was completed by different team members:

- **T1** (Data & Chunks): @yousefJooX
- **T2** (Test Set): @mariasamir173-tech
- **T3** (Dense Retrieval): @yousefJooX
- **T4** (BM25 & Hybrid): @marwan149
- **T5** (Reranker & Runner): @KareemAlwam
- **T6** (LLM): @hm136101-png
- **T7** (Evaluation): TBD

---

Happy experimenting! 🚀
