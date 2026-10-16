# Problem Set 4 Student Submission

**Student:** Yinuo Zhao
**Independent GitHub repository:** [https://github.com/inorrr/can-we-trust-ai-agents](https://github.com/inorrr/can-we-trust-ai-agents)
**Status:** Complete and ready for submission. The project, two live runs, editorial review, final student approval, three published article/video pairs, and separate technical demonstration are recorded.

**Technical demonstration (5:50):** [Watch on YouTube](https://youtu.be/P9cKPBVAGNo)

## Topic, audience, and publication purpose

**The Agent Trust Check** asks: what evidence should we require before giving an AI agent permission to act? The audience is developers and product managers evaluating tool-using software agents. Each piece connects recent disclosures, evaluation results, and practitioner arguments to decisions about permissions, containment, monitoring, accountability, and recovery. The series uses an opinionated essay voice while separating source claims from interpretation and qualified evidence.

## Published series

| Piece | Article | Video | Duration |
| --- | --- | --- | --- |
| 01 | [Before You Hand Over the Keys](https://kumato1.substack.com/p/before-you-hand-over-the-keys) | [YouTube](https://youtu.be/9VNTJX5ZNDU) | 3:44 |
| 02 | [A Locked Door Should Not Depend on Good Manners](https://kumato1.substack.com/p/a-locked-door-should-not-depend-on) | [YouTube](https://youtu.be/spFtXYdjddA) | 3:53 |
| 03 | [The Security Demo Ends. The Work Begins.](https://kumato1.substack.com/p/the-security-demo-ends-the-work-begins) | [YouTube](https://youtu.be/SKrj_CnHfjI) | 4:01 |

Substack pages were verified to contain their corresponding YouTube link, readable sources, and AI-assistance disclosure including Google Vids AI narration. Google Vids player durations were verified; YouTube cross-links back to the articles are confirmed by the student. See [publication records](docs/publication_links.json) and [production records](docs/VIDEO_PRODUCTION_STATUS.json).

## Architecture and execution

[Implemented architecture and diagram](docs/ARCHITECTURE_IMPLEMENTATION.md) · [Setup and commands](docs/SETUP.md) · [Pinned dependencies](requirements.txt)

The supplied README.md and ARCHITECTURE.md are preserved. All 16 Bash entry points implement the required boundaries. Bash owns fixed orchestration; Python helpers own collection, extraction, storage, filtering, model selection/synthesis, checking, packaging, and reporting. Only data/store.sh and its helper access the persistent SQLite index. This is bounded AI editorial judgment inside a deterministic workflow, not a self-directed tool loop.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
bash run.sh
bash run.sh --package runs/20261012T172153-9a3b9d
```

OpenAI credentials belong in the environment or ignored .env.local; no key is included. Text generation uses GPT-4.1 mini with structured Responses outputs. The transcript fallback uses whisper-1 and imageio-ffmpeg. Setup documents dependencies, the local $5 per-run cap, replay behavior, source retrieval, and omitted media.

The normal pipeline stops for review. Final approval must come from the student. Google Vids production, Substack/YouTube publication, and the demo recording were completed as manual handoffs. The published series uses the reviewed October 12 evidence date; later drafts do not replace it.

## Evidence and run records

Evidence index: data/evidence/index.sqlite3. Retained written text and timestamped transcripts: data/assets/. Original large recordings and the local runtime are excluded from Git; candidates retain original source/media URLs so recordings can be retrieved. The [source research notes](docs/SOURCE_RESEARCH.md) document incentives, independence, and missing perspectives.

| Run | Actual UTC execution date | Record and result |
| --- | --- | --- |
| First end-to-end run with recovery | 2026-10-12 | [Summary](runs/20261012T172153-9a3b9d/summary.json), [decisions](runs/20261012T172153-9a3b9d/decisions.jsonl), [briefs](runs/20261012T172153-9a3b9d/briefs.jsonl), [approved package](runs/20261012T172153-9a3b9d/package/manifest.json). Fifteen eligible items, nine publishers: ten written, two YouTube, three podcast; four written items found through RSS. |
| Second live run with recovery | 2026-10-16 (October 15 New York) | [Summary](runs/20261016T004940-4d840c/summary.json), [changes](runs/20261016T004940-4d840c/changes.jsonl), [decisions](runs/20261016T004940-4d840c/decisions.jsonl), [review](runs/20261016T004940-4d840c/review.json). Fourteen current observations; fifteen retained eligible items. Three drafts and scripts pass mechanical review; these are unpublished inspection artifacts. |

The second collection produced 13 unchanged observations and one navigation-text change, with no meaningful new evidence. The [second-run report](docs/SECOND_LIVE_RUN.md) explains that false positive. The [explicitly labeled withheld-item replay](output/repeatability_replay/README.md) shows one new insertion followed by 15 unchanged observations without altering the live store. Historical caption, API, content-generation, and recovery failures remain visible in [recovery notes](docs/RECOVERY_LOG.md) and actual stage receipts. No timestamps or failures are simulated as live events.

## Editorial review, approval, and claim trace

- [Student review and correction history](docs/EDITORIAL_REVIEW.md) and [structured source judgments](docs/source_reviews.jsonl).
- [Original policy](docs/policy_history/editorial_policy-v1.md), [revised policy](config/editorial_policy.md), [saved prompts](prompts/), and [actual before/after comparison](docs/POLICY_COMPARISON.md).
- [Final student approval record](runs/20261012T172153-9a3b9d/approval.json) and [scope of approval](docs/FINAL_REVIEW.md).
- [Trace of a published Manus claim](docs/CLAIM_TRACE.md), from exact retained source/version through decision, brief, draft, and public citation.

Three accepted-source judgments and three student exclusions are recorded. The original model accepted all 15; the policy comparison and second live run also accepted all 15. Student exclusions are disagreements with those acceptances, not fabricated original AI rejections. Those exclusions were applied to the published series; the mismatch remains an explicit limitation. Human wording and factual approval is recorded from the student’s direct statements.

## Reflection

**Insight:** Trust is most useful when expressed as bounded permissions, enforceable action checks, intervention authority, and recovery responsibilities. Identity delegation and reasoning visibility are mechanisms to evaluate; they are not evidence of reduced harm by themselves.

**Editorial failure:** A more specific prose policy did not stop the selector from accepting derivative commentary, product positioning, and secondhand proposals. Agreement with the six student judgments remained 3/6. The product required explicit human source exclusions. Whole-item acceptance also blurred what a particular claim could legitimately use.

**Operational limitation:** Full-page extraction treated a changed recent-post navigation list as a new source version. Timestamped machine transcripts and exact claim locators support inspection but do not prove accuracy.

**Next improvement:** Require explicit claim-level evidence of originality and permitted use before acceptance, route unresolved source-role disagreements to human review, and separate article-body changes from page chrome when versioning.

## Verification

Nine offline contract tests pass. Both live runs retain real network/model artifacts; current drafts pass mechanical checks. Packaging reassesses the approved original series and requires the matching student decision. The final package contains actual publication links. Exact requests, responses, usage, cost estimates, and failure receipts are preserved. Estimated costs are not invoices; uncertain-cost calls in the first run remain disclosed.

```bash
.venv/bin/python -m unittest discover -s tests -v
```

All required submission links and records are complete. The student-supplied technical demonstration was verified as an accessible 5:50 unlisted YouTube video on October 16, 2026.
