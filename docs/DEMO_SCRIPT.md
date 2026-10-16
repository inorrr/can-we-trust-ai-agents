# Technical demonstration script — about 5 minutes

Everything in square brackets is an on-screen action, not narration.

## 0:00–0:35 — Purpose and entry point

[Start on `SUBMISSION.md`, with the title, project status, and published-series table visible.]

Hi, I’m Yinuo Zhao. I built **The Agent Trust Check**, a repeatable research and editorial pipeline for developers and product managers asking: what evidence should we require before giving an AI agent permission to act?

The system collects recent written, YouTube, and podcast material, preserves the evidence, uses AI for bounded editorial decisions and drafting, and stops for human review. It produced three Substack articles and three companion videos.

[Open `run.sh`, then briefly show `workflows/collect_sources.sh` and `workflows/create_series.sh`.]

`run.sh` is the entry point. Bash controls a fixed sequence: collection first, then editorial production. The model makes structured decisions inside individual stages; it does not choose which tools to run.

## 0:35–1:35 — Architecture and one published claim

[Open the diagram in `docs/ARCHITECTURE_IMPLEMENTATION.md` and slowly follow it from the collectors to the store, editorial stages, review, and manual publication.]

Collectors discover sources, and extraction retains article text and timestamped transcripts. Only the store component can access the SQLite evidence index. After the 30-day filter, the editorial stages select sources, create evidence-linked briefs, and generate articles and scripts. Mechanical checks run before student approval and manual publication.

[Open `docs/CLAIM_TRACE.md`. Highlight the published location and steps 1 through 8. Then open the linked retained Salt Labs text, the matching record in the first run’s `decisions.jsonl`, claim `02-c1` in `briefs.jsonl`, and `output/substack_ready/article_02.md`.]

Here is one claim traced end to end. Article 2 discusses Salt Labs’ report that a malicious email redirected the Manus agent and led to code execution in its sandbox. The retained source has a stable item and version ID. The AI accepted it. My review kept it with a narrower role: it supports this reported attack, but not vendor efficacy or industry-wide prevalence.

That limitation carries into claim `02-c1`, the draft, and the published citation. The trace identifies the evidence; it does not claim independent reproduction.

## 1:35–2:35 — Two live runs and update behavior

[Open `runs/20261012T172153-9a3b9d/run.json`, then `runs/20261016T004940-4d840c/run.json` and `summary.json`.]

I completed live runs on October 12 and October 16 UTC. The second began on October 15 in New York, after midnight UTC, and performed fresh collection and generation.

The second run observed 14 sources. Thirteen were unchanged, none were new, and one received a new stored version. The persistent corpus still supplied 15 eligible items from nine publishers: ten written items, two YouTube videos, and three podcasts.

[Open `runs/20261016T004940-4d840c/observed_navigation_change.diff`.]

The article evidence did not change. A “Recent articles” navigation list changed, producing a versioning false positive. I recorded it instead of presenting it as a new development, and did not revise the published series.

[Open `output/repeatability_replay/README.md`, followed by the two changes files named there.]

An isolated, labeled replay makes insertion and duplicate handling visible. It starts with 14 real records and one eligible item withheld. Introducing it produces one new record; replaying all 15 produces 15 unchanged records. It never touches the live store and is not presented as live discovery.

## 2:35–3:35 — Human correction and policy revision

[Open `docs/POLICY_COMPARISON.md`. Show the result line, the six reviewed rows, and the three disagreements.]

Human review exposed the main editorial failure. The selector accepted all 15 items, including derivative commentary and product positioning. I reviewed three sources that I retained with limits and three that I excluded.

I revised the policy to demand originality, claim-specific credibility, and novelty, then reran selection on the same evidence.

The model again accepted all 15, and matched only three of my six judgments. I preserved that failure. Human exclusions were applied to the published drafts, but I did not rewrite the historical decisions. Prose rules were too weak; the next design should require claim-level evidence and route disagreements to a human.

## 3:35–4:25 — Failure recovery and architectural tradeoff

[Open `docs/RECOVERY_LOG.md`. Highlight the YouTube rate-limit and transcription-recovery bullets. If time permits, show one failed receipt from the first run.]

The system preserves real failures. YouTube caption requests were rate-limited, so extraction fell back to timestamped audio transcription. Two transcription calls then failed. The pipeline retained receipts and unknown-cost reservations, cached completed chunks by media hash, and recovered through an explicit resume.

The local SQLite store gives me stable identities, immutable versions, and inspectable provenance. It fits a one-person weekly pipeline, but not a multi-user publication system. The fixed workflow is easy to audit and resume, with less flexibility than an open-ended agent loop.

## 4:25–5:10 — Outputs, checks, and limits

[Return to `SUBMISSION.md` and show the three article/video pairs. Then open the second run’s `summary.json` and `review.json`.]

The result is three published article-and-video pairs, each from the same reviewed brief and evidence set. The later run produced inspection drafts but did not overwrite the published series.

The second run cost about 29 cents. Mechanical review passed with human-review warnings and one empty transcript cue that cannot support a claim. The checks verify structure, dates, coverage, claim markers, and references. They do not prove source truth, transcript accuracy, or sound synthesis.

That is the boundary I designed around: automation makes the research process repeatable and traceable, while publication authority and factual judgment remain explicit human responsibilities. Thank you.

## Recording notes

- Target pace: about 135–145 spoken words per minute.
- Keep filenames and the relevant lines readable; zoom in before recording.
- Prepare all files as editor tabs in the order used above.
- Keep `.env.local`, API credentials, and account pages off-screen.
- Show saved results rather than triggering another paid pipeline run.
