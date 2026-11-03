# Six more Star Trek novel leads — publisher descriptions, cover locators held

**Role:** LIT. **State:** PROPOSAL_ONLY. **Observation:** 2026-11-03 UTC. **Prior literary synopsis proposals:** #261, #266, #270 (15 distinct Work-level source-description summaries).

I opened and actually read **six official Simon & Schuster ISBN-specific product pages** (the publisher's product description and bibliographic details) before writing six new concise original synopsis paraphrases. The works extend the candidate set across Picard, Discovery, The Original Series, The Next Generation, Deep Space Nine, and Enterprise. The exact edition ISBN, publisher display title, author, series, on-page format/date/page count, descriptive source locator, and original short publisher-based synopsis are versioned in `observations.json`.

| Publisher display title | ISBN13 | Edition format |
|---|---|---|
| *Star Trek: Picard: The Last Best Hope* | 9781982142186 | Trade paperback |
| *Star Trek: Discovery: Die Standing* | 9781982136291 | Trade paperback |
| *Agents of Influence* | 9781982133689 | Trade paperback |
| *Available Light* | 9781982113278 | Trade paperback |
| *Enigma Tales* | 9781501152580 | Mass-market paperback |
| *Rise of the Federation: A Choice of Futures* | 9781501146336 | Trade paperback |

The six work title/ISBN pairs are distinct from the existing **15** publisher-synopsis candidates, checked against the three earlier versioned observation sidecars, not merely memory. They are **not** necessarily unique across the entire unwritten Star Trek bibliography: Librarian reconciliation and edition-family discovery remain separate work. Every synopsis has status `PUBLISHER_DESCRIPTION_PARAPHRASE`. Marketing descriptions cannot establish full-book semantics, story-world facts, or that a read of the literary source occurred.

**Hostile source-scope correction:** An earlier draft of *The Last Best Hope* incorrectly imported Romulan/supernova specifics not present in the cited ISBN-specific publisher description. This proposal replaces that with the page-supported rescue-armada, personal-consequences, and Starfleet-departure framing. An adversarial regression now rejects those independently falsified additions. Other publisher descriptions must still be evaluated by source reread, not by assuming this limited guard proves every paraphrase.

## Cover locators: explicit rights hold

Each official product page contains a **high-resolution book-cover hyperlink**. I followed those links through the web reader: it disclosed six exact `.jpg` URLs, but image decoding/download was unsupported; no image content was retrieved or stored. The six **source link locators only** appear in `cover_candidate_locator`, with `cover_locator_source=PUBLISHER_HIGH_RES_IMAGE_LINK` and **`cover_rights_status=RIGHTS_UNVERIFIED_HOLD_NO_PUBLIC_DISPLAY`**. They are not thumbnails to render or permission to publish. Image licensing and allowed display require separate qualification. `cover_image_bytes_retrieved=false` is a custody statement about this work session, not a claim that the publisher's images do not exist.

## What this does **not** do

- No complete source book, authenticated publisher HTML byte snapshot, cover bytes, derivative conversion, private artifact, or source-text hash.
- No Source→Work binding, accepted Work, evidence/plot assertion, global identity, coverage, or reconciliation.
- `SOURCE_BOUND=false`, `FULL_TEXT_AVAILABLE=false`, `STRUCTURALLY_INDEXED=false`, `CLOSE_READ=false`, `SEMANTICALLY_ANALYZED=false`; one publisher source lineage, not six independent witnesses.
- No public image display, rights clearance, or assertion that selected ISBNs exhaust their edition families.

`validate.py` pins the raw observation bytes; cross-checks Work IDs/ISBN/title deduplication against the **three prior accepted publisher-synopsis proposals**; enforces source/cover locator structure and hard negative status gates. The tests in `tests/test_lit_six_era_publisher_sources.py` probe tampering, source-label promotion, duplication, rights escalation, and source drift. Accepting and displaying synopses remains a governed Consolidator action.
