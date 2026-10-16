# Run The Agent Trust Check

## Installation

Use Bash and Python 3.11 or newer (tested locally with Python 3.14). From this folder:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
bash run.sh
```

Network access is required for feeds, public source pages, YouTube, media hosts, and api.openai.com. YouTube can rate-limit transcripts even when audio download works. The audio-converter executable comes from imageio-ffmpeg; no global installation is required.

`OPENAI_API_KEY` is read from the environment or the ignored `.env.local`. Never commit this file, copy it into runs, or include it in a submission ZIP. The configured key expires after 30 days. API billing is separate from a ChatGPT subscription.

## Configuration

- `config/project.json`: publication brief, GPT-4.1 mini text model, Whisper transcription, batch limits, pricing, and a local run-cost cap.
- `config/sources.json`: RSS feeds, individual YouTube URLs, podcast feeds, and explicitly labeled supplemental page discoveries. Several endpoints from one producer share publisher_id.
- `config/editorial_policy.md`: the policy applied during selection and synthesis.
- `prompts/*.md`: actual reusable generation instructions.

A run freezes these files under its own config/ and prompts/. Edit root configuration for future runs. Preserve previous snapshots; a policy revision should start a new run with separate outputs. Dates are captured once in UTC from the actual execution day; do not backdate runs. A byline that supplies only a calendar date stays date-only rather than inventing a time.

Text generation uses OpenAI Responses with a strict JSON schema and no browsing/tools. Exact instructions, supplied context, structured responses, and usage are saved under model_calls/. A text model override is rejected unless its snapshotted pricing matches the configured model. Current pricing references are in project.json; approximate costs are estimates, not an invoice. The local cost ledger reserves a conservative upper bound before each request, retains reservations after uncertain failures, and stops before exceeding the configured cap. It is not an account-wide billing limit.

## Commands and replay

```bash
bash run.sh
bash run.sh --resume runs/RUN_ID
bash workflows/collect_sources.sh runs/RUN_ID
bash workflows/create_series.sh runs/RUN_ID
bash review/check_content.sh runs/RUN_ID > runs/RUN_ID/review.json
bash reporting/summarize_run.sh runs/RUN_ID > runs/RUN_ID/summary.json
bash run.sh --package runs/RUN_ID
```

The optional --resume mode reruns an incomplete live run on its original UTC day, retaining old receipts and reusing stored evidence. It refuses approved drafts and date changes. Start a new run on a different day.

Each component can run independently using ARCHITECTURE.md's stdin/stdout contracts. Keep old outputs before manually replaying an affected editorial stage. Collectors can return partial results with exit 1; workflows retain them and report incomplete coverage. Exit 2 indicates invalid input/configuration. Content checks return 0 when assessment completes even if passed=false; inspect review.json.

Selection piece_ids are preliminary planning assignments. evidence_usage.jsonl records actual use in the validated briefs and makes changed assignments explicit; rejected/deferred material cannot enter a brief. The current brief serializer assigns canonical claim IDs and resolves every selected passage to an exact source/version locator.

The normal run stops for student review. It never writes approval.json. After reviewing actual drafts and evidence, the student creates approval.json with the current review_id, decision, reviewer, reviewed_at, and notes. A passing review and matching unchanged-input approval are required for packaging. See examples/approval.json for the shape only; fictional approval is not real approval.

## Storage and assets

- Persistent versioned evidence: `data/evidence/index.sqlite3`, accessed only through data/store.sh.
- Immutable extracted text and transcript assets: `data/assets/ITEM_HASH/VERSION_HASH/`.
- Large original recordings: `data/media/`, excluded from Git.
- Run configuration, candidates, decisions, briefs, drafts, reviews, receipts and summaries: `runs/RUN_ID/`.

Stable written identities hash canonical URLs; podcast identities hash publisher ID and episode GUID; YouTube uses native video IDs or explicitly reconciled underlying recording IDs. Version IDs hash sorted compact JSON containing title, canonical URL, publication date, text, transcript segments, publisher ID, and kind. Retrieval timestamps do not create versions. The store retains prior versions and observations; list exports latest versions for freshness filtering.

Written sources are fetched again to detect substantive updates. Unchanged media metadata reuses stored transcripts and recordings. Set PIPELINE_REFRESH_MEDIA=1 to deliberately re-extract media when checking for edits. Machine transcription and timestamps require human spot checks; do not treat transcripts as infallible. Model context is bounded to the first 24,000 text characters/300 segments per item for selection/briefs, with truncation labeled. Full evidence remains retained; this is a documented limitation of initial selection. Brief generation uses a complete catalogue of written paragraphs and consecutive transcript cue groups, with exact passage IDs mapped back to source versions. It stops rather than silently truncating when the catalogue exceeds the schema limit. Content generation reads the referenced evidence, using cited media cues plus neighboring context.

To retrieve omitted original recordings, use the media_url or original YouTube URL in saved candidates. Rerun the collector/extractor with appropriate network access. Retained text and segments are included for inspection without large media downloads.

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Tests use disposable copies and fictional fixtures, separately from live evidence. They verify duplicate replay, retained history, date boundaries and invalid dates, malformed input, review fingerprints, blocking missing or stale approval, preserving entered publication links when repackaging, cost-cap reservations, stored-version reversion, and safe resume guards.

## Remaining manual work

The student reviews at least three accepted and three rejected/deferred selections, revises the policy and compares outputs, corrects factual issues, and supplies final approval. Produce videos in Google Vids or HeyGen, publish article/video pairs to Substack and YouTube, cross-link them, and verify access. Remove internal claim markers from the audience-facing rendering only after readable citations are preserved. Record a separate technical demonstration. Two live runs must occur on different days; retries today do not satisfy that requirement.

## Partial content recovery

`PIPELINE_PIECE_IDS=02,03` limits a content writer to named pieces while validating all three briefs. Append these records only to a manifest that contains the other completed pieces, then rerun checks; duplicate or missing records fail review. `PIPELINE_REPLAY_CONTENT_RESPONSE` can point to a completed saved response in this run's model_calls folder to recover formatting without a fresh API call. The saved brief, instructions, and policy must match. Preserve original responses and record recovery in the recovery log.

## Retained content edits and project status

When a bounded content-generation attempt fails on length, preserve its response before making a documented editorial edit. PIPELINE_CONTENT_EDIT may point to a file under the same run's editorial_edits/ only when replaying a matching original response through PIPELINE_REPLAY_CONTENT_RESPONSE. The writer still validates length, date, and claim coverage. It logs retained_assistant_edit; it does not create student approval. The second live run demonstrates this recovery.

Run summaries use docs/PROJECT_STATUS.json, when present, for current project-level remaining actions, and docs/publication_links.json for actual published links. Without those files, the original conservative defaults remain. Per-run failure receipts, draft checks, and approval status remain separately reported.
