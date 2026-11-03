# DS9 S1 source-relative publisher guide tranche (five cards)

**Role:** DS9 audiovisual worker

**State:** `PROPOSAL_ONLY / PUBLISHER_GUIDE_STRUCTURALLY_INDEXED / NO_PRIMARY_AV_READ / NO_COVERAGE_EFFECT`

**Accepted base:** `main@d4ecd970bf28019696abd692011007d7d47f9ff8`
**Capture:** 2026-11-03 UTC

## Actual source retrieval and processing

I retrieved the full public [Paramount+ Deep Space Nine Season 1 guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/1/) by HTTP GET (`200`, **298,872** HTML bytes, SHA-256 `2862e1bf5e8e3541ee697b16a3b195b1139e094393e83c8576c51d0fd7f246fd`) and read the rendered guide text for its first five displayed episode cards (rendered lines 113–139). The raw source was retained only transiently, outside the public checkout. Its publisher titles/ordinals reproduce existing candidate roster metadata, while the five synopsis-coded source-relative observations are newly indexed here. No full episode was streamed, viewed or transcribed.

| Source-local card | Displayed slot | Neutral synopsis coding |
| --- | --- | --- |
| The Emissary, Parts I and II | S1 E1 combined | New station crew and assignment |
| Past Prologue | S1 E3 | Kira's loyalty/duty tension |
| A Man Alone | S1 E4 | Odo facing a murder suspicion |
| Babel | S1 E5 | Station illness and remedy search |
| Captive Pursuit | S1 E6 | O'Brien and a pursued being |

The card descriptions are **publisher testimony about works**, not episode depictions or accepted fictional-world facts. Existing roster source-local IDs are not silently globally reconciled. `local_entities.json` has 8 scoped card/mention referents, `evidence.json` records 5 synopsis observations and 5 tentative date-label conflicts, and `assertions.json` holds 6 provisional publisher-relative assertions. No source-bound Work, Briefing or coverage event results.

## Unexpected same-publisher date-label disagreement

The search-indexed rendering of the [publisher season guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/1/) and the indexed individual video pages display these differing labels:

| Card | Guide label | Individual video label |
| --- | --- | --- |
| [The Emissary, Parts I and II](https://www.paramountplus.com/shows/video/zbYJuXEpNDasxVJf48I7BRo3vg5ogjuF/) | Jan 4, 1993 | Jan 3, 1993 |
| [Past Prologue](https://www.paramountplus.com/shows/video/B8iwoYdTgzQd6XXiE9L8hiQL73E0XEar/) | Jan 11, 1993 | Jan 10, 1993 |
| [A Man Alone](https://www.paramountplus.com/shows/video/98levBtEWk4kMsTkEse1gOOXUbb6n2T_/) | Jan 18, 1993 | Jan 17, 1993 |
| [Babel](https://www.paramountplus.com/shows/video/CnOtv5JvGqoBVJfyM9F3tu3HJrFdk1yF/) | Jan 25, 1993 | Jan 24, 1993 |
| [Captive Pursuit](https://www.paramountplus.com/shows/video/5D_1m9MMJBeWpDQkLlBl9aSR3o8hg1WF/) | Feb 1, 1993 | Jan 31, 1993 |

**Lower-grade receipt caveat:** The date labels were observed in search-indexed publisher page excerpts (same corporate lineage, not independent witnesses). The date labels were **not isolated in the direct raw guide HTML receipt**, and direct GET of the individual video URLs returned HTTP 500 (some browser-open attempts were region-redirected or 404). Therefore the five date comparisons are discovery hypotheses only, **not authenticated airdate facts or a reconciliation decision**. A timezone conversion, page-field difference or stale indexing could explain them; none is proven. This discrepancy must survive as `UNRESOLVED`, with no automatic promotion of one date.

## Boundaries and next gate

- Provenance independence group: `publisher:paramount`, even though more than one URL was observed. No independent source corroboration is claimed.
- Public repository has factual metadata and original paraphrase codes only; no transcript, media, copyrighted still or source HTML copied into the proposal.
- The existing DS9 metadata candidate ledger already covers the seven publisher season pages; these five observations **do not increase the count of distinct Works or admitted Briefings**.
- Deterministic local check: `python3 proposals/research/ds9-paramount-s1-guide-20261103/validate.py`.
- Next: retrieve pinned edition-specific page representations of each date label and an independent broadcast listing; determine date field meaning. Then acquire a full primary audiovisual/script witness and Librarian Source↔Work binding before any episode `CLOSE_READ`, semantic research, coverage promotion or admitted Briefing.
