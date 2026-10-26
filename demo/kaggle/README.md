# Running on Kaggle

The heavier configs do not fit a 6 GB laptop GPU, so they run on a Kaggle T4.

1. Package the code as a private Kaggle dataset (`code.tar.gz` with `utils.py`,
   `data/chunks.json` and `demo/`):
   ```bash
   git archive --format=tar.gz -o code.tar.gz HEAD utils.py data/chunks.json demo/blocks demo/configs.py demo/registry.py demo/run.py demo/data/test_set.json demo/data/index/.gitkeep demo/results/.gitkeep
   kaggle datasets version -p <dataset-dir> -m "update"
   ```
2. Push `run_kaggle.py` as a GPU script kernel with internet on and the dataset
   attached (`kaggle kernels push`). It runs each config in `CONFIGS` in its own
   process and leaves the result JSONs and logs in `/kaggle/working/results`.
3. `kaggle kernels output <kernel> -p out/` downloads them.

Gated models (aya8b) need an `HF_TOKEN` Kaggle secret, accepted access on the
model page, and a run started from the Kaggle website (Save Version): secrets
are not available to runs pushed from the CLI.
