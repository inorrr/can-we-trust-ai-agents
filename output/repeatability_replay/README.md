# Clearly labeled withheld-item replay

This is an isolated replay using real retained records from the second live run. It does not discover new material. One eligible budget-caps article is deliberately withheld from a 14-record baseline, then introduced. The store reports one new record. Replaying all 15 then reports 15 unchanged records. The isolated store is owned by the copied data/store.sh helper; the main evidence index is untouched. No model calls or simulated failures occur here.

Inspect runs/replay/baseline_changes.jsonl, introduce_withheld_changes.jsonl, replay_unchanged_changes.jsonl, corpus.jsonl, and eligible.jsonl. The text/segment paths in these copied records refer to the original repository evidence assets; this replay exercises metadata storage and filtering, not extraction or content generation.
