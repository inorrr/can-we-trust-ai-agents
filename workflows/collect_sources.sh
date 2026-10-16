#!/usr/bin/env bash
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib/shell.sh"
[[ $# -eq 1 && -f "$1/run.json" ]] || { echo "Usage: collect_sources.sh RUN_DIR" >&2; exit 2; }
RUN_DIR="$1"
"$PY" -c 'import sys;sys.path.insert(0,"lib");from common import run_dir;run_dir(sys.argv[1])' "$RUN_DIR" || exit 2
export PIPELINE_RUN_DIR="$RUN_DIR"
START="$($PY -c 'from datetime import datetime, timezone; print(datetime.now(timezone.utc).isoformat())')"
rc=0
mkdir -p "$RUN_DIR/candidates"
stage_to_file collectors/fetch_feeds.sh "$RUN_DIR/candidates/feeds.jsonl" || rc=1
stage_to_file collectors/fetch_youtube.sh "$RUN_DIR/candidates/youtube.jsonl" || rc=1
stage_to_file collectors/fetch_podcasts.sh "$RUN_DIR/candidates/podcasts.jsonl" || rc=1
cat "$RUN_DIR/candidates/feeds.jsonl" "$RUN_DIR/candidates/youtube.jsonl" "$RUN_DIR/candidates/podcasts.jsonl" > "$RUN_DIR/candidates.jsonl"
# A real pipe sends the discovery stream into the independently runnable extractor.
cat "$RUN_DIR/candidates.jsonl" | bash processing/extract_content.sh "$RUN_DIR" > "$RUN_DIR/items.jsonl" || rc=1
bash data/store.sh upsert "$RUN_DIR" < "$RUN_DIR/items.jsonl" > "$RUN_DIR/changes.jsonl" || rc=1
bash data/store.sh list > "$RUN_DIR/corpus.jsonl" || rc=1
stage_to_file processing/filter_items.sh "$RUN_DIR/eligible.jsonl" "$RUN_DIR/corpus.jsonl" || rc=1
"$PY" lib/workflow_receipt.py "$RUN_DIR" collect_sources "$START" "$rc" 0
exit "$rc"
