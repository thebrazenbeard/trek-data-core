# Six additional official-publisher literary Work candidates with brief synopses

**Role:** LIT. **State:** PROPOSAL_ONLY. **Observation date:** 2026-11-03 UTC. **Preceding tranches:** #261 (three distinct titles) and #266 (six distinct titles). This proposal contains no duplicate title/series/ISBN from those nine.

I directly opened six individual official Simon & Schuster trade-paperback product pages, inspected their **About the Book** promotional sections, and checked title, author, series, ISBN13, imprint, on-page publication date, and page extent. I wrote an original, concise source-grounded synopsis for each title. Every synopsis is explicitly `PUBLISHER_DESCRIPTION_PARAPHRASE`, **not** a close read of a novel and not a source-relative scene assertion. `observations.json` is a sidecar carrying the exact ISBN-specific primary locator and each Work's own metadata/synopsis; the validator pins raw sidecar SHA-256.

| Source-labeled candidate Work | ISBN13 | Publisher series | Existing Librarian candidate |
|---|---|---|---|
| *The Dark Veil* | 9781982154073 | Picard | Yes, `proposed-lit-picard-the-dark-veil` |
| *Rogue Elements* | 9781982175207 | Picard | Yes, `proposed-lit-picard-rogue-elements` |
| *Firewall* | 9781668046364 | Picard | No link asserted |
| *Pliable Truths* | 9781668046418 | The Next Generation | No link asserted |
| *Somewhere to Belong* | 9781668002292 | Discovery | No link asserted |
| *Revenant* | 9781982160821 | Deep Space Nine | No link asserted |

The first two are **additional to the nine synopsis Works**, but **not** new Librarian discovery. Their recorded ISBN/creator/publication metadata matches `proposals/librarian/picard-companion-editions-20261103/records.json`; this is a cross-check against an already known proposal, not independent corroboration. The remaining four are locally named candidate Works from directly inspected official product pages. A search of the then-current GitHub code index returned no title hits for the latter four, but code-search absence is not authoritative nonexistence evidence. Only a Librarian registry reconciliation can establish whether they duplicate any differently named existing Source/Work records.

All six pages are part of **one publisher source lineage**. No raw authenticated HTML bytes, raw page hashes, EPUB, scanned page, audiobook, cover, or lengthy promotional text has been obtained or committed. Observed page fields may change. `Revenant` and `Pliable Truths` are publisher display titles, with their Trek series stored separately; adding the franchise prefix would be an editorial display transformation, not a new Work.

## No accepted corpus effects

`SOURCE_BOUND=false`, `FULL_TEXT_AVAILABLE=false`, `STRUCTURALLY_INDEXED=false`, `CLOSE_READ=false`, `SEMANTICALLY_ANALYZED=false`, no Source→Work binding, no global identity/reconciliation, no accepted evidence or coverage, no publisher edition-family completeness, and no artwork rights clearance. Six publisher-description summaries are **not** six close-read synopses. Editorial use should retain the provenance label.

`validate.py` cross-checks the two existing Picard records against the accepted Librarian discovery bundle, enforces publisher URL/ISBN, rejects duplicate previous-work pairs and gate promotions, and freezes the full observation sidecar to its raw hash. Adversarial tests live in `tests/test_lit_six_next_publisher_works.py`. Review/admission/merging is separate from preparing this proposal.
