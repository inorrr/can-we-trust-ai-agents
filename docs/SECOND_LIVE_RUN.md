# Second live pipeline run

Run: [20261016T004940-4d840c](../runs/20261016T004940-4d840c/summary.json). Actual start: October 15, 2026 in New York / October 16 UTC. The pipeline automatically records UTC as-of date 2026-10-16; the evidence window is September 17–October 16 inclusive. The first run was October 12 UTC. This is a fresh network collection and actual API generation, separate from the earlier policy-only comparison.

## Observed result

- 14 items discovered and extracted in this collection; the persistent corpus supplies 15 eligible items from nine publishers (10 written, two YouTube, three podcasts; four written items discovered by RSS).
- Store observations: zero new, one changed, 13 unchanged. The retained budget-caps article remains eligible even though it was not rediscovered in this collector output.
- The changed version is Willison's Wikimedia commentary: its Recent articles navigation changed. The incident text and publication date did not change. This is an extraction/versioning false positive for substantive updates, not new evidence. See [saved diff](../runs/20261016T004940-4d840c/observed_navigation_change.diff).
- No meaningful new material was observed. No change to the published series is claimed on that basis.
- The model again accepted all 15 eligible items under policy v2. Human source exclusions remain applied to the October 12 published drafts; this rerun does not overwrite them. This remains an editorial-enforcement limitation.
- Three briefs, three articles, and three video scripts are retained. The mechanical review passes with warnings for human interpretation checks and one uncited empty transcript cue. Current per-run status: **awaiting_review**.
- Estimated API cost: **$0.2895**, uncertain-cost calls: 0. Stored transcripts were reused; this run made no new paid transcription calls.

## Real recovery

The original article writer failed because Article 3 remained above the word limit after its bounded revisions. All failed responses and receipts remain preserved. The assistant removed introductory/concluding repetition from the first completed response and retained the original response and exact removed passages under editorial_edits/. The same writer replayed that matching response plus the retained edit, validated the 768-word body and all claim markers, and generated the missing article record without another API call. A recovery implementation initially used a set operation on a list; that failed attempt is also preserved and was corrected. The original create_series workflow receipt remains failed; current component completion and passing review reflect recovery. No student approval was generated.

## Required labeled replay

[Isolated withheld-item replay](../output/repeatability_replay/README.md): deliberately retain 14 real records, introduce one previously withheld eligible record, then replay all 15. Actual results are one new record followed by 15 unchanged records. This is labeled replay, not fresh discovery or a simulated live change. The main evidence store is untouched by this demonstration.

## Submission disposition

The later drafts are inspection artifacts, not a second published series or reviewed replacements for the original three pairs. Final factual/transcript review, human approval, repository completion, publication links, and the student's [technical demonstration](https://youtu.be/P9cKPBVAGNo) are recorded in the submission. The model's failure to produce rejected/deferred decisions is reported explicitly; three student rejections are disagreements with AI acceptance, not retroactive AI rejections.
