#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
exec "${PIPELINE_PYTHON:-$ROOT/.venv/bin/python}" "$ROOT/collectors/fetch_youtube.py" "$@"
