"""Portable paths and shared constants for RetinaCellTwin."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("RCT_DATA_DIR", REPO_ROOT / "data")).expanduser().resolve()
RESULTS_DIR = Path(os.environ.get("RCT_RESULTS_DIR", REPO_ROOT / "results")).expanduser().resolve()
MANIFEST = REPO_ROOT / "data" / "datasets.json"


def require(path: Path, description: str) -> Path:
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {description}: {path}. Run analysis/fetch_open_data.py "
            "or set RCT_DATA_DIR."
        )
    return path

