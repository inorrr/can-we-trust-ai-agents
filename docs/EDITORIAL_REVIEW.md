# Student editorial review worksheet

This worksheet is unfinished. It does not constitute student review or approval. Fill it after reading actual source passages and generated decisions.

## Article 1 voice review — 2026-10-15

Student feedback: “Its tone is notably dry, analytical, and heavily restrained, reading more like a synthesized briefing than an opinion piece. While that cautious style keeps it objective, it definitely sacrifices a stronger authorial perspective or deeper critical commentary on the implications.”

Assistant revision: reorganized Article 1 around a position on action-specific permissions, intervention, and accountability. Kept factual attribution and evidence limitations explicit. Preserved the previous draft in the run's editorial_history/01-before-tone-revision.md.

Status: revised article awaits the student's assessment. This feedback concerns voice and argument; it is not source verification, a completed selection audit, or final approval. The corresponding video script still reflects the earlier structure and needs alignment after the article's direction is agreed.

## Article 1 second voice review — 2026-10-15

Student feedback: “It reads more like a dry technical memo than a piece of writing with any real style or literary flair. Stripped of narrative rhythm, metaphor, or stylistic ambition, the prose feels purely functional rather than engaging.”

Assistant response: rewrote the article as an essay titled “Before You Hand Over the Keys.” Added an explicitly imagined opening, a recurring keys/permissions metaphor, varied paragraph rhythm, and critical commentary about costs borne by people outside the deployment decision. Retained source attribution, limitations, and all claim markers. The first argument-focused revision is preserved in editorial_history/01-before-literary-revision.md.

Status: the student responded “Good!” to the revised voice. This is stylistic acceptance, not factual or final publication approval. The opening is an illustration, not a reported event. Script alignment, factual verification, source-selection review, and final approval remain outstanding.

## Article 2 argument review — 2026-10-15

Student feedback: “This second article makes a much stronger point by bringing real technical examples—like prompt injections and supply-chain exploits—into the fold. I like its warning that models act differently when they know they're being tested, though calling AI failures just "software bugs" feels a bit too simple for unpredictable models. Ultimately, relying on model "skepticism" to stop bad commands seems naive; real security needs hard API boundaries, not just better-behaved prompts.”

Assistant revision: centered the essay on security that survives model manipulation, qualified the software-bug framing, and distinguished external authorization from model instruction-following. Preserved technical examples and evaluation caveats. Original saved in editorial_history/02-before-student-revision.md.

## Article 3 argument review — 2026-10-15

Student feedback: “This third piece offers a refreshingly practical turn by shifting focus from theoretical panic to concrete operational tools, like Okta identity delegation and vendor-backed runtime security. Its highlight is the realistic assessment of real-time chain-of-thought monitoring—acknowledging that models can easily evade oversight or act without explicit reasoning traces. Overall, grounding agent security in established cybersecurity practices rather than speculative alignment feels like the right move, though relying on vendor assertions without independent benchmarks remains a obvious blind spot.”

Assistant revision: retained operational examples, made the independent-evaluation gap central, distinguished identity attribution from task authorization, and framed vendor efficacy as a question for testing. Clarified that evasion is possible without claiming it is universally easy. Original saved in editorial_history/03-before-student-revision.md.

Both revised essays await student assessment. These comments are editorial judgments, not completed source verification or final approval. Video scripts still need alignment with the revised essays.

## Decision sample

Choose at least three accepted and three rejected/deferred items from the completed run's decisions.jsonl. Record item/version IDs and exact evidence passages or media timestamps.

| Item and version | AI decision and reason | Student judgment | Agree/disagree and why | Correction or policy change |
| --- | --- | --- | --- | --- |
| Salt Labs Manus disclosure — `web:54c033ffc1eaf619f6cc78dc` / `7104e94fda1c0e41c21abd5e1a07edc4021ff2d37b032f8595223ffbce9b9d4b` | Accept: detailed, directly relevant vulnerability disclosure despite vendor interest. Full saved reason in [source review record](source_reviews.jsonl). | Keep as evidence of the disclosed attack. | Agree with acceptance; reject extrapolation to industry frequency or product effectiveness. | Require independent confirmation for prevalence and AI-DR efficacy claims. |
| Willow feature announcement — `web:6b7a4fd29b3e7419544c7257` / `b216dbba17dd31f128fd6a450b658d9e7a4b777416ea47f2c2a2e963175393f9` | Accept: concrete identity delegation and auditability features; see full saved reason in source_reviews.jsonl. | Keep with limits as an access-control architecture example. | Agree on relevance; no empirical evidence of reduced breaches. | Attribute features to the vendor and require independent evidence for risk reduction. |
| Wikimedia first-party incident account — `web:c7de8a9c60da8633bdb63e16` / `e7007b1e854770c30a9a2acbf41c37a8a0f78c5ba24c20bb1bbf786f2d6abd65` | Accept; exact rationale saved in source_reviews.jsonl. | Keep with limits for reported operational observations. | Attribution and outage causation are deductions; do not generalize to all agents. | Separate observations, attribution, causality, and generalization. |
| Willison Wikimedia commentary — `web:7cc0255a3132017e9645f034` / `1908abdd6011fc980024a6008f2f83a004bba601cf73e7097f3b3b65c5a0cb63` | AI accepted; original decision preserved. | Student: exclude as redundant. | Disagree: interpretation does not add enough beyond retained primary account. | Remove from synthesis; prefer original report and track derivative sources. |
| Salt runtime product post — `web:3800ef90ead639b8c8b3922f` / `9e0eabb01601d4e945b7fa8d1cb236ee3b54df08837519d3f1e0a44dfa334e57` | AI accepted; original rationale saved. | Student: exclude as redundant product marketing. | No new empirical results or independent case evidence. | Remove source and unsupported claim 03-c1; retain separate Manus disclosure. |
| CSIS AI Safety Goes Mainstream — `podcast:74d4dd378ce184845fadf184` / `c34ccd2adffbe3151e791787769437445e0041728077d573a58b8fafac904a92` | AI accepted; original saved. | Student: exclude (changed from keep with limits). | Mainly relays proposals; insufficient value for this series. | Remove proposal claim 03-c5 and its source citations. |

If the AI accepts everything, do not fabricate rejections to fill this table. Expand or revise the candidate selection so genuinely contestable eligible material is evaluated, and preserve the original output.

## Accepted item 1: evidence and scope

The student's three-part assessment is preserved in [source_reviews.jsonl](source_reviews.jsonl), alongside the exact AI decision, item/version IDs, and an exact retained evidence passage about successful sandbox command execution. The passage supports the described mechanism; retaining it is not independent reproduction of the exploit.

This is one reviewed accepted source. Rejecting its use to prove vendor efficacy does not turn the source into a rejected/deferred item and does not fill that part of the required sample. The proposed policy rule remains a proposal until the policy is revised and rerun.

## Accepted item 2: mechanism versus effectiveness

The student's full three-part Willow assessment is saved in [source_reviews.jsonl](source_reviews.jsonl), with the AI rationale and a verbatim account-delegation passage. This is a second reviewed accepted item, not a rejected/deferred source. Acting under the initiating user's account should not be described as direct access to raw Okta credentials without evidence of that implementation. The feature announcement does not establish reduced breach rates.

## Accepted item 3: observations versus conclusions

The student's full three-part Wikimedia assessment is saved in [source_reviews.jsonl](source_reviews.jsonl), with the original AI decision and a retained evidence passage. The student accepts its value as a first-party account of operational burden while qualifying actor attribution, outage causation, and generalization. This assessment does not independently verify those forensic details.

Three accepted-source judgments are now recorded. The rejected/deferred sample, policy revision and rerun, media checks, script alignment, and final approval remain incomplete. A claim-level limitation within an accepted source does not count as a rejected/deferred item.

## Willison commentary: conditional assessment

The student identifies useful developer interpretation but no independent factual corroboration. They describe exclusion as valid when only primary evidence is needed and retention as valid when interpretation contributes. Full feedback, exact item/version, original AI acceptance, and an interpretation passage are in [source_reviews.jsonl](source_reviews.jsonl).

Final student decision: “exclude as redundant.” This is the first student rejection of an originally AI-accepted item. It is not retrospectively labeled an AI rejection. The original AI decisions remain unchanged. Its evidence references and citations have been removed from the briefs and drafts, with prior versions preserved in editorial_history/. Proposed rule: assess commentary for distinct interpretive value and track its dependence on the underlying disclosure.

## Salt runtime post: second student exclusion

The student excludes the conceptual product-positioning post as redundant marketing without new empirical tests or independent cases. Exact feedback, AI rationale, and a retained passage are recorded in source_reviews.jsonl. The briefs and draft citations no longer use it; claim 03-c1, which depended solely on it, was removed rather than reassigned to unrelated evidence. Earlier versions remain in editorial_history/.

The review now contains three accepted items and two student-rejected items. All original AI decisions were accept; a policy revision and genuine model rerun are still needed for the requested before/after comparison.

## CSIS oversight discussion: accepted with limits

Student decision: “mainly relay proposals, keep it with limits.” The AI rationale, item/version identity, and exact segment used for claim 03-c5 are saved in source_reviews.jsonl. Treat the episode as secondary reporting on proposed oversight, not evidence of implementation, evaluator independence, or reduced risk. This is a fourth accepted-source review; two student exclusions remain recorded. No third rejection is manufactured.

## Policy revision

1. Preserve the first run's policy and decisions.
2. State the observed weakness, with specific examples from the sample.
3. Edit the root editorial policy and record a version heading.
4. Start a new run to freeze the revised policy and prompts; rerun the affected stages.
5. Compare actual decisions and synthesis before/after. A same-day policy comparison is additional evidence, not a substitute for the second live run on a different day.

## Factual corrections

| Claim ID / draft passage | Original wording | Corrected wording | Source passage or timestamp | Reason |
| --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending |

For media, listen to the cited audio around each timestamp and compare it to the machine transcript. Verify publication dates against original recordings, distinguish new disclosure from old events, and assess whether apparent corroboration merely repeats the same report.

## Final approval

Rerun checks after factual corrections. Read the current review.json, compare all three articles with their scripts, and then supply approval.json yourself. The pipeline must not create a human decision on your behalf. Copy the exact current review_id; record your name, UTC review time, decision, and notes.

## CSIS decision changed by student

After initially keeping the episode with limits, the student requested exclusion and explicitly confirmed it. Both judgments are preserved in source_reviews.jsonl. Claim 03-c5 depended solely on this episode and has been removed from the brief, article, and video script; the source was also removed from the combined evidence for 03-c8. Previous artifacts are preserved in editorial_history/.

Current sample: three retained sources and three student exclusions. These exclusions are disagreements with originally AI-accepted sources; they do not retrospectively create AI reject decisions. Policy revision and a real model rerun remain necessary for the before/after comparison. The budget-caps commentary has not been reviewed and no decision is inferred for it.

## Policy v2 derived from the completed student sample

On 2026-10-15 the student authorized revising the rules and rerunning selection. The original policy is preserved in docs/policy_history/editorial_policy-v1.md and in the October 12 run. The root policy now explicitly distinguishes concrete disclosures and architectural examples from redundant commentary, unevidenced product positioning, and secondary governance proposals. It separates observations, attribution, causality, and generalization, and makes the limits of accepted evidence explicit.

The controlled comparison uses the exact original 15 source versions and original cohort date, with a new execution timestamp and mode policy_comparison. It is not a fresh collection and cannot satisfy the separate different-day live-run requirement. Student source labels are not passed to the model; matching and disagreement will be assessed after its response.

## Actual policy comparison result

The v2 selection run completed on 2026-10-15 using the identical 15-item cohort. Both original and revised model runs accepted all 15. There were zero changed decisions; the model matched the student's three keeps and disagreed with all three exclusions. The complete before/after table and diagnosis are in [POLICY_COMPARISON.md](POLICY_COMPARISON.md). The comparison is evidence of a policy-enforcement limitation, not a successful reproduction of human judgment. The student's exclusions remain applied to the edited drafts.

## Video scripts aligned to the revised essays — 2026-10-15

All three scripts now follow their companion essays' arguments, metaphors, and source restrictions. Article 1 uses the keys/permissions illustration; Article 2 centers external authorization rather than model skepticism; Article 3 distinguishes concrete mechanisms from product efficacy. Excluded Willison commentary, Salt product marketing, and the CSIS governance-proposal episode are absent from the scripts and their source notes. The separate CSIS incident-reporting episode remains attributed and qualified as secondary reporting.

Narration is separated from proposed visual directions, descriptions, and exact source notes. Word counts and speaking-time estimates are recorded in the run's script_alignment.json. These are estimates, not measured video durations. The scripts preserve the October 12 evidence date and carry the October 15 revision date. Earlier scripts are preserved in editorial_history/.

Script alignment is complete; student read-through, factual/transcript verification, final approval, and actual video production remain pending. No synthetic presenter or rendered video is claimed.

## Student script wording acceptance — 2026-10-15

After reviewing Script 1, the student said “it's good.” After being directed to Scripts 2 and 3, the student said “both scripts are good.” All three scripts therefore have student acceptance for wording and spoken style.

This is not a claim that an actual timed read-through, source/audio verification, or final publication approval occurred. No approval.json has been created. Video production and publication remain pending.

## Video 1 production reported by student

The student reports completing the first Google Vids video with a total duration of three and a half minutes (approximately 210 seconds), within the required 3–5-minute range. The assistant has not viewed the video or independently verified its duration, source cards, narration, disclosures, or final visuals. No publication link has been supplied. Videos 2 and 3 remain unconfirmed. See VIDEO_PRODUCTION_STATUS.json.

## Video 1 link and playback verification

The student supplied [Video 1](https://docs.google.com/videos/d/19bc2UZ62lg4U6AlyhButITGEZyT6W06s4zdXl15Oqig/play?usp=sharing). Its Google Vids page is accessible and titled “Before You Hand Over the Keys.” Playback starts successfully and the player displays a total duration of **3:24** (204 seconds), within the 3–5-minute requirement. This refines the earlier approximate student report of 3½ minutes. Only opening playback and duration were checked; the full narration, factual content, end-card citations, and disclosure have not been reviewed. A Google Vids link is not recorded as a YouTube publication.

## All three video links received and playback checked

The student reports all three videos complete and supplies their Google Vids links in article order. Each page opens with the expected title and playback starts. Current displayed lengths: Video 1 3:44, Video 2 3:53, Video 3 4:01. All meet the 3–5-minute requirement by visible player duration. Video 1's updated duration supersedes the earlier 3:24 observation. Links and verification scope are in VIDEO_PRODUCTION_STATUS.json. Full narration, sources, AI disclosures, and content accuracy have not been reviewed end to end. These are Google Vids production copies; no YouTube publication is inferred.

## YouTube links supplied by student

The student supplied YouTube links for Videos 1–3 in order: https://youtu.be/9VNTJX5ZNDU, https://youtu.be/spFtXYdjddA, https://youtu.be/SKrj_CnHfjI. These are recorded in VIDEO_PRODUCTION_STATUS.json and SUBMISSION.md. Public/unlisted visibility, descriptions, disclosures, and complete uploaded content have not been independently verified. The student confirmed use of Google Vids AI voiceover and requested that narration disclosure be included in all three descriptions. Substack links and reciprocal article/video links remain pending.

## All three Substack posts published and verified

The student supplied all three post links in order. Each post opens in the browser, shows the expected essay, includes the matching YouTube link, lists its sources, and includes the AI-assistance disclosure including Google Vids AI narration. Canonical URLs without tracking parameters are saved in docs/publication_links.json and SUBMISSION.md. This confirms published-page presence and listed content, not independent source verification. Links from YouTube descriptions back to the articles have not been checked. The separate second-day live collection, final factual approval, repository completion, and technical demonstration remain outstanding.
