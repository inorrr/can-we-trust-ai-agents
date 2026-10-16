#!/usr/bin/env bash
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib/shell.sh"
[[ $# -eq 1 && -f "$1/run.json" ]] || { echo "Usage: create_series.sh RUN_DIR" >&2; exit 2; }
RUN_DIR="$1"
"$PY" -c 'import sys;sys.path.insert(0,"lib");from common import run_dir;run_dir(sys.argv[1])' "$RUN_DIR" || exit 2
export PIPELINE_RUN_DIR="$RUN_DIR"
START="$($PY -c 'from datetime import datetime, timezone; print(datetime.now(timezone.utc).isoformat())')"
rc=0
stage_to_file editorial/select_items.sh "$RUN_DIR/decisions.jsonl" "$RUN_DIR/eligible.jsonl" || rc=1
if [[ "$rc" -eq 0 ]]; then stage_to_file editorial/create_briefs.sh "$RUN_DIR/briefs.jsonl" "$RUN_DIR/decisions.jsonl" || rc=1; fi
if [[ "$rc" -eq 0 ]]; then
  stage_to_file content/write_articles.sh "$RUN_DIR/articles.jsonl" "$RUN_DIR/briefs.jsonl" || rc=1
  stage_to_file content/write_video_scripts.sh "$RUN_DIR/video_scripts.jsonl" "$RUN_DIR/briefs.jsonl" || rc=1
fi
stage_to_file review/check_content.sh "$RUN_DIR/review.json" || rc=1
"$PY" lib/workflow_receipt.py "$RUN_DIR" create_series "$START" "$rc" 0
exit "$rc"
