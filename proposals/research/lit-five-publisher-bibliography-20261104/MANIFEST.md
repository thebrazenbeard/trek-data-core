# Five first-party Star Trek literary Work/edition discovery leads

**Role:** LIT. **Status:** Held public bibliography proposal; accepted effects **NONE**. **Inspected accepted main:** `3028765359001b90bc3e6b5c1835ee283b326e91` (2026-11-04 UTC). **Source investigation:** five official Simon & Schuster publisher product pages retrieved 2026-11-04. No copyrighted book pages, audiobooks, covers, or publisher promotional passages reproduced.

## Five distinct local Work candidates and their publisher editions

| Local Work candidate | Creator credit on publisher page | Edition | First-party source locator |
| --- | --- | --- | --- |
| *Mosaic* — Star Trek: Voyager | Jeri Taylor, **author** | eBook, ISBN13 `9780743453868`, Pocket Books/Star Trek, 2002-10-04, 320 pages | [Publisher](https://www.simonandschuster.com/books/Mosaic/Jeri-Taylor/Star-Trek-Voyager/9780743453868) |
| *Pathways* — Star Trek: Voyager | Jeri Taylor, **author** | eBook, ISBN13 `9780743453851`, Pocket Books/Star Trek, 2009-09-29, 528 pages | [Publisher](https://www.simonandschuster.com/books/Pathways/Jeri-Taylor/Star-Trek-Voyager/9780743453851) |
| *Unification* — Star Trek: The Next Generation | Jeri Taylor, **author** in product metadata | eBook, ISBN13 `9780743420730`, Pocket Books/Star Trek, 2000-09-22, 256 pages | [Publisher](https://www.simonandschuster.com/books/Unification/Jeri-Taylor/Star-Trek-The-Next-Generation/9780743420730) |
| *The Lives Of Dax* — Star Trek: Deep Space Nine | Marco Palmieri, **editor**, not sole author | eBook, ISBN13 `9780743400817`, Pocket Books/Star Trek, 1999-12-01, 384 pages | [Publisher](https://www.simonandschuster.com/books/The-Lives-Of-Dax/Marco-Palmieri/Star-Trek-Deep-Space-Nine/9780743400817) |
| *The Romulan Way* — Star Trek: The Original Series | Diane Duane **and** Peter Morwood, **coauthors** | eBook, ISBN13 `9780743419864`, Pocket Books/Star Trek, 2000-09-22, 304 pages | [Publisher](https://www.simonandschuster.com/books/The-Romulan-Way/Diane-Duane/Star-Trek-The-Original-Series/9780743419864) |

Each publisher ISBN belongs to an **eBook edition** of a different candidate Work; page links to audio, print, or other editions are not substitutions for the recorded ISBN. The publisher is one upstream family for all five pages, not five independent corroborators. Querying accepted-main JSON proposal records found no existing entries for these exact five ISBNs before this batch. The discovery scan is constrained to records in accepted `main`; it cannot certify the broader universe has no duplicate title or other edition.

## Evidentiary limits and anomalies

`records.json` contains original bibliographic metadata only. Its local IDs are **worker candidate IDs**, not globally reconciled Work identities. The producer-to-consumer direction is publisher product-page metadata → proposed local Work/edition candidate; there is **no private file/edition match, Source↔Work binding, objective fictional story assertion, or text-based character evidence**. None of these five works was close-read. `FULL_TEXT_AVAILABLE`, `STRUCTURALLY_INDEXED`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, `ENTITY_LINKED`, and `AUDITED` coverage are **not claimed**. The single publisher upstream is not independent multi-source corroboration.

> **Hostile challenge:** Product metadata establishes a marketed manifestation, not its complete text or the authenticity of an owner-held copy. Edition lengths are publisher display values, not extracted page/line counts. *The Lives Of Dax* is presented as an edited anthology; promoting Marco Palmieri to sole author erases contributors. The official *Unification* page has `Jeri Taylor` in the author field but `Teri Taylor` in its promotional paragraph; this remains a **source copy discrepancy**, not evidence of a distinct person or a resolved name identity. The promotion also describes a television-episode connection, but I did not independently compare the book and episode. No narrative facts follow from that description.

Issue [#23](https://github.com/thebrazenbeard/trek-data-core/issues/23) still holds new literary CLOSE_READ work pending governance, Librarian Source↔Work/edition custody, and coverage admission. This proposal may enter inventory review only; it must not be interpreted as an accepted evidence ledger entry or Explorer coverage increase.

Validation: `python3 proposals/research/lit-five-publisher-bibliography-20261104/validate.py`, `python3 -m unittest discover -s proposals/research/lit-five-publisher-bibliography-20261104 -p test_validate.py -v`, and `python3 tools/validate.py`. The validator rejects duplicate ISBNs, format substitutions, author/editor/coauthor drift, unverified private-file identity promotion, fake coverage, untracked publisher-copy resolution, and copyrighted prose fields.
