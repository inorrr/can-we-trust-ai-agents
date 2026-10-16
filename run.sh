#!/usr/bin/env bash
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/shell.sh"
rc=0
RUN_START="$($PY -c 'from datetime import datetime, timezone; print(datetime.now(timezone.utc).isoformat())')"
if [[ $# -eq 0 ]]; then
  RUN_DIR="$($PY lib/run_setup.py)" || exit $?
  export PIPELINE_RUN_DIR="$RUN_DIR"
  echo "Run: $RUN_DIR" >&2
  bash data/store.sh init || rc=1
  bash workflows/collect_sources.sh "$RUN_DIR" || rc=1
  # Continue into inspectable decisions/checks even after a partial collection.
  bash workflows/create_series.sh "$RUN_DIR" || rc=1
elif [[ $# -eq 2 && "$1" == "--resume" && -f "$2/run.json" ]]; then
  RUN_DIR="$2"
  "$PY" -c 'import sys;sys.path.insert(0,"lib");from common import run_dir;run_dir(sys.argv[1])' "$RUN_DIR" || exit 2
  export PIPELINE_RUN_DIR="$RUN_DIR"
  "$PY" -c 'import json,sys,datetime,pathlib; r=pathlib.Path(sys.argv[1]); m=json.load(open(r/"run.json")); a=json.load(open(r/"approval.json")) if (r/"approval.json").exists() else {}; ok=m["as_of_date"]==datetime.datetime.now(datetime.timezone.utc).date().isoformat() and a.get("decision")!="approve"; sys.exit(0 if ok else 2)' "$RUN_DIR" || { echo "Resume requires the same actual UTC day and no approved drafts; start a new run otherwise." >&2; exit 2; }
  bash data/store.sh init || rc=1
  bash workflows/collect_sources.sh "$RUN_DIR" || rc=1
  bash workflows/create_series.sh "$RUN_DIR" || rc=1
elif [[ $# -eq 2 && "$1" == "--package" && -f "$2/run.json" ]]; then
  RUN_DIR="$2"
  "$PY" -c 'import sys;sys.path.insert(0,"lib");from common import run_dir;run_dir(sys.argv[1])' "$RUN_DIR" || exit 2
  export PIPELINE_RUN_DIR="$RUN_DIR"
  stage_to_file review/check_content.sh "$RUN_DIR/review.json" || rc=1
  if [[ "$rc" -eq 0 ]]; then
    stage_to_file publishing/prepare_package.sh "$RUN_DIR/package-output.json" || rc=1
  fi
else
  echo "Usage: bash run.sh | bash run.sh --resume runs/RUN_ID | bash run.sh --package runs/RUN_ID" >&2
  exit 2
fi
if [[ -f "$RUN_DIR/review.json" ]]; then
  "$PY" -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1])).get("passed") else 1)' "$RUN_DIR/review.json" || rc=1
fi
"$PY" lib/workflow_receipt.py "$RUN_DIR" run "$RUN_START" "$rc" 0
stage_to_file reporting/summarize_run.sh "$RUN_DIR/summary.json" || rc=1
cat "$RUN_DIR/summary.json"
exit "$rc"
