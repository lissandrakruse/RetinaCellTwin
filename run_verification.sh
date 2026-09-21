#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ -n "${RCT_PYTHON:-}" ]]; then
  PYTHON_CMD="$RCT_PYTHON"
elif [[ -x .venv/bin/python ]]; then
  PYTHON_CMD=".venv/bin/python"
else
  PYTHON_CMD="python"
fi
PYTHONDONTWRITEBYTECODE=1 "$PYTHON_CMD" -m unittest discover -s tests -v
echo "RetinaCellTwin verification passed."
