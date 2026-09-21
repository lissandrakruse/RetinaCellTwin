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

"$PYTHON_CMD" analysis/fetch_open_data.py
"$PYTHON_CMD" analysis/analyze_open_data.py
"$PYTHON_CMD" analysis/analyze_gravity_hypothesis.py
"$PYTHON_CMD" analysis/analyze_sample_level_audit.py
"$PYTHON_CMD" analysis/analyze_count_level_audit.py
"$PYTHON_CMD" analysis/fetch_functional_data.py
"$PYTHON_CMD" analysis/analyze_go_enrichment.py
"$PYTHON_CMD" analysis/analyze_cell_context.py
"$PYTHON_CMD" analysis/analyze_cross_modal_context.py
"$PYTHON_CMD" analysis/make_figures.py
./run_verification.sh
