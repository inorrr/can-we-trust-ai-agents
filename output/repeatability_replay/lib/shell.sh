#!/usr/bin/env bash
# Common shell paths and stage execution; workflows own sequencing.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PIPELINE_PYTHON:-$ROOT/.venv/bin/python}"
cd "$ROOT"
export PIPELINE_PYTHON="$PY"
if [[ ! -x "$PY" ]]; then
  echo "Install dependencies into .venv first; see docs/SETUP.md" >&2
  exit 2
fi
stage_to_file() {
  local script="$1" output="$2" input="${3:-}" rc=0
  if [[ -n "$input" ]]; then
    bash "$ROOT/$script" "$RUN_DIR" < "$input" > "$output.tmp" || rc=$?
  else
    bash "$ROOT/$script" "$RUN_DIR" > "$output.tmp" || rc=$?
  fi
  mv "$output.tmp" "$output"
  return "$rc"
}
