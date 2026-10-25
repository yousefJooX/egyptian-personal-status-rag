"""Pipeline blocks. Makes the repo-root `utils.py` (normalize_ar) importable from every block."""

import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parents[2])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
