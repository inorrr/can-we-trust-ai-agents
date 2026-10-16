# Implemented architecture

The required course ARCHITECTURE.md is preserved unchanged. Bash owns the entry point and two workflow sequences. Each substantive component has its own focused Python helper behind its required Bash interface. lib/common.py provides I/O, receipts, model transport, and cost reservations; it does not implement stages or orchestrate the whole pipeline.

```mermaid
flowchart TD
    R[run.sh: metadata and snapshots] --> C[collect_sources.sh]
    C --> F[fetch_feeds.sh: RSS and labeled page discoveries]
    C --> Y[fetch_youtube.sh: native metadata]
    C --> P[fetch_podcasts.sh: RSS audio enclosures]
    F --> E[extract_content.sh: retained text, media, timed transcripts]
    Y --> E
    P --> E
    E --> D[store.sh: versioned SQLite evidence]
    D --> W[filter_items.sh: 30 UTC dates]
    W --> S[create_series.sh]
    S --> A[select_items.sh: OpenAI editorial decisions]
    A --> B[create_briefs.sh: three evidence-linked arguments]
    B --> N[write_articles.sh]
    B --> V[write_video_scripts.sh]
    N --> K[check_content.sh: mechanical review fingerprint]
    V --> K
    K --> H[Student review and approval.json]
    H --> X[prepare_package.sh: unchanged-input approval check]
    X --> M[Manual Google Vids or HeyGen, Substack and YouTube]
    R --> T[summarize_run.sh: artifacts, receipts, costs, gaps]
```

## Important tradeoffs

SQLite is local, inspectable, and sufficient for a one-user weekly workflow. Store access is confined to store.sh's helper. Other components retrieve exact versions through its commands. Stable identities and immutable assets allow past claims to remain traceable after updates.

A fixed Bash workflow makes sequencing and failure behavior easy to explain. AI performs editorial judgment within bounded stages; this is not a self-directed agent loop. Structured outputs constrain record shape, while application checks verify references and coverage. Neither establishes truth or sound interpretation. Brief generation selects from a retained passage catalogue; deterministic serialization supplies exact source/version/locator fields and canonical claim IDs. Actual article assignments are saved separately from selection intentions.

Public feeds and individual video URLs avoid needing platform-specific credentials. Supplemental research pages broaden evidence but do not count as RSS-discovered written items. Source independence is asserted at producer level and must be reviewed at the claim level; copying a report does not create independent corroboration.

Whisper is a fallback when publisher/YouTube timestamps are unavailable. It adds cost and may introduce transcription mistakes. Exact chunk offsets are retained and machine transcripts need spot checks. Missing or failed sources remain explicit; no synthetic content fills the gaps.

Review fingerprints include manifests, drafts, briefs, decisions, eligible evidence, retained reference text/segments, and run metadata. Direct packaging reassesses these bytes and requires matching student approval. Machine consistency checks mainly ensure a shared claim inventory and resolvable citations; a student must still compare article/script meaning and evaluate synthesis.
