"""Runs the RAG pipeline configs on a Kaggle GPU and leaves results in /kaggle/working/results."""
import glob, os, shutil, subprocess, sys, tarfile, time

CONFIGS = ["arch1", "arch1_bge", "arch2", "arch2_qwen3", "arch3_qwen3"]  # + "arch3", "arch3_no_rr" once HF access to aya is granted

def sh(cmd, **kw):
    print(f"\n$ {cmd}", flush=True)
    return subprocess.run(cmd, shell=True, **kw)

sh("nvidia-smi --query-gpu=name,memory.total --format=csv")
sh(f"{sys.executable} -m pip install -q faiss-cpu rank_bm25 FlagEmbedding bitsandbytes sentence-transformers")
sh(f"{sys.executable} -c \"import torch, transformers, sentence_transformers; print('torch', torch.__version__, 'transformers', transformers.__version__, 'st', sentence_transformers.__version__)\"")

# code: the dataset may arrive as the .tar.gz or already extracted
repo = "/kaggle/working/repo"
os.makedirs(repo, exist_ok=True)
archives = glob.glob("/kaggle/input/**/code.tar.gz", recursive=True)
if archives:
    tarfile.open(archives[0]).extractall(repo)
else:
    src = os.path.dirname(glob.glob("/kaggle/input/**/utils.py", recursive=True)[0])
    shutil.copytree(src, repo, dirs_exist_ok=True)
print("repo:", sorted(os.listdir(repo)), flush=True)

# HF token for gated models (aya8b): Kaggle secret "HF_TOKEN", attached to this notebook in the UI
try:
    from kaggle_secrets import UserSecretsClient
    os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")
    print("HF_TOKEN: loaded from Kaggle secrets", flush=True)
except Exception as exc:
    print(f"HF_TOKEN: not available ({type(exc).__name__}); gated models will fail", flush=True)

env = dict(os.environ, CUDA_VISIBLE_DEVICES="0", TOKENIZERS_PARALLELISM="false")
demo = os.path.join(repo, "demo")
os.makedirs("/kaggle/working/results", exist_ok=True)
status = {}
for cfg in CONFIGS:
    start = time.time()
    with open(f"/kaggle/working/results/{cfg}.log", "w") as log:
        rc = subprocess.run([sys.executable, "-u", "run.py", cfg], cwd=demo, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
    status[cfg] = (rc, round(time.time() - start))
    print(f"[{cfg}] exit={rc} in {status[cfg][1]}s", flush=True)
    for f in glob.glob(os.path.join(demo, "results", f"{cfg}_*.json")):
        shutil.copy(f, "/kaggle/working/results/")
    if rc != 0:
        sh(f"tail -30 /kaggle/working/results/{cfg}.log")

shutil.rmtree(repo, ignore_errors=True)  # keep the output small: results only
print("\nSTATUS", status, flush=True)
