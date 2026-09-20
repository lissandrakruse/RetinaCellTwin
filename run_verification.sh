#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
echo "RetinaCellTwin verification passed."

