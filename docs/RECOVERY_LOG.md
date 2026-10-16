# First-run recovery record

These were real implementation and execution failures during the October 12 live attempt, not simulated source failures. Earlier component receipts and model responses are retained under runs/20261012T172153-9a3b9d/; the initial collection attempt is separate under runs/20261012T171821-a3432e/.

- A candidate URL was empty because feed metadata fields were not consistently populated. Discovery now falls back through canonical link/alternate fields; podcast records without a page link use the specific media URL rather than a generic feed URL. Publisher-specific bylines are parsed in article headers rather than searching arbitrary body dates.
- YouTube caption endpoints returned HTTP 429 even though audio downloaded. OpenAI transcription was used as the fallback, with timestamped segments retained alongside source media.
- Two transcription requests failed with APIConnectionError. Their exact billed cost is unknown; conservative cost reservations remain. The affected items were recovered in a later explicit replay. Completed transcription chunks are now cached by media content hash for future resumes.
- The assistant edited the Bash launcher while it was executing, causing a footer parsing error. The source was syntax-checked and the run was resumed through the repaired entry point. Do not edit executing shell files during a run.
- A valid structured selection response omitted two candidates. It was rejected. Selection now requires one keyed response slot per input item and attaches the actual item/version identity deterministically.
- An early brief used only two distinct publishers for piece 01 despite citing several reports. Validation rejected it. Source records from one organization count as one publisher.
- Early brief generation shortened quotations with ellipses and another response exhausted its output limit. Brief generation was changed to select an exact retained passage catalogue. The serializer resolves passage IDs to immutable item/version/text or segment locators; it cannot invent a quotation.

The initial valid selection accepted all 15 items. This remains an editorial limitation to inspect, not a manufactured rejection sample. See INITIAL_SELECTION_AUDIT.md and EDITORIAL_REVIEW.md for student review work still required.

## Content recovery and formatting

Article generation exposed missing claim markers and length failures. The writer now requests bounded revisions for both conditions. References written as bold headings were initially counted as body text; normalizing these headings recovered a previously completed article response without another API request. A completed script response was similarly recovered and formatted with the actual run date. Replay checks that the saved response belongs to this run and that the brief, prompt, and editorial policy match. Some later API connections failed or returned incomplete output; receipts and cost reservations remain retained.

Assistant editorial corrections are listed in ASSISTANT_CORRECTIONS.md. They do not substitute for student review.

## Second live run recovery

The October 16 UTC run's third article exceeded its length bound after revisions. A retained assistant edit removed repetitive introduction/conclusion text from a saved response; the writer replayed and validated it without a fresh model call. The response, removed passages, edit, original failed workflow receipt, and current mechanical review are all retained. A list/set method error in the recovery path was corrected after a recorded failure. See SECOND_LIVE_RUN.md for the complete outcome.
