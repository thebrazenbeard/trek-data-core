# Frozen research registration — OPF 0089 and 0091

**Prepared:** 2026-11-03, before this wave's first-party retrieval. **Status:** PROPOSED.

## Frozen questions

1. Can the local OPF `0089` provisional title *Infiltrator*, with no creator, publisher, or ISBN, be correlated to any **specific first-party publisher edition**, without inventing a local edition binding?
2. Does Simon & Schuster provide a first-party edition-specific explanation or alternate page for OPF `0091` ISBN10 `0743421221` (`9780743421225`) versus its known *The Death of Princes* eBook ISBN13 `9780743422888`?

## Hypotheses and falsifiers

- **H1** (exploratory search, not conclusion): an official publisher page may identify an *Infiltrator* TNG book and responsible author. A page that lacks an edition identifier connected to the owner-private OPF **falsifies any asserted exact OPF edition binding**, even if title and character names agree.
- **H2** (exploratory search): the publisher may currently resolve `9780743421225` to a separate eBook edition. If the authoritative page only exposes `9780743422888`, **exact eBook equivalence remains unproven**, not disproven as impossible.
- **H3** (confirmatory invariant): no accepted OPF source-local identifier, local Work, text coverage, or art rights may be promoted by publisher title similarity or an ambiguous ISBN. The validation must reject such promotions and source substitutions.

## Frozen methods

- **P1:** Inspect accepted `origin/main`, prior Librarian OPF metadata digest, and accepted/proposed local identifier collisions.
- **W1:** Retrieve official Simon & Schuster product information by targeted title/ISBN queries and opening exact publisher pages; log URLs and decisive product-display lines.
- **W2:** Probe `9780743421225` within first-party Simon & Schuster catalog and compare against first-party `9780743422888`, distinguishing 404/no-index from a definitive no-edition claim.
- **V1:** Produce bounded source-local metadata observations with pinned OPF hash, official page source URL, explicit crosswalk state, and no Work/coverage/rights effects.
- **V2:** Run strict duplicate-key and hostile mutation tests in regular and optimized Python plus repository regression.

**Stopping rule:** Maximum four primary product/catalog surfaces per question, or an exact official identifier match plus independent source check. If access is unavailable or conflicting, preserve `UNRESOLVED` and stop without inventing records. Neither outside dataset citations nor memory count as primary source custody. Source HTML not captured means no raw-HTML hash claim.

## Evidence log

Append dated, source-referenced observations here after retrieval. Do not amend the frozen section above.

### 2026-11-03 observations (primary publisher surfaces)

- **E0, P1 — accepted input inspection:** main `806c4502af8eb5306137c13eaacea54f8cd469ba`, sanitized OPF source SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`. Source OPF0089 `73b2ed96170cdbd7f0db2ddebf4b9d1f6aad0d6011c07aec3c48022c6109b1f1` records a generic title *Star Trek - TNG - Infiltrator*, no creator/publisher/date/ISBN. OPF0091 `11d97f45a723d8dd0dad9adb517027b5a4b183b18ca8216ff667d05512ed25ab` records title *THE DEATH OF PRINCES*, creator *JOHN PEEL*, ISBN10 `0743421221`, date `2000-08-05`. Accepted earlier OPF 0090–0092 packet already holds OPF0091 edition mismatch. No duplicate OPF source-local insertion is permitted here.
- **E1, W1 — first-party book page:** [Simon & Schuster *Infiltrator*](https://www.simonandschuster.com/books/Infiltrator/W-R-Thompson/Star-Trek-The-Next-Generation/9780743421201), inspected rendered page lines 79–85, 100–103, 114–118: Book #42, W.R. Thompson, eBook, Pocket Books/Star Trek September 22 2000, 288 pages, ISBN13 `9780743421201`. Same page provides a publisher-written premise (Khan's followers on Hera). **Does not establish owner-private OPF edition identity** because OPF0089 has no matching ISBN or creator metadata. Publisher HTML bytes not captured; no raw HTML digest.
- **E2, W1 — same-family author index:** [Simon & Schuster W.R. Thompson author page](https://www.simonandschuster.com/authors/W-R-Thompson/1499806), rendered lines 185–209 lists *Infiltrator* #42 and author. This is the same corporate source lineage as E1, not independent corroboration.
- **E3, W2 — first-party title/ISBN page:** [Simon & Schuster *The Death of Princes*](https://www.simonandschuster.com/books/The-Death-of-Princes/John-Peel/Star-Trek-The-Next-Generation/9780743422888), publisher page previously observed on current wave; eBook John Peel, #44, September 22 2000, ISBN13 `9780743422888`. Owner OPF0091 ISBN10 `0743421221` converts mechanically to `9780743421225`—different identifier.
- **E4, W2 — decisive cross-title collision:** [Simon & Schuster *Balance of Power*](https://www.simonandschuster.com/books/Balance-of-Power/Dafydd-ab-Hugh/Star-Trek-The-Next-Generation/9780743421225), rendered official page lines 191–197, 227–231: **that exact ISBN13 `9780743421225` belongs to *Balance of Power*, by Dafydd ab Hugh, #33**, eBook, September 22 2000. This falsifies any automatic claim that OPF0091 title/creator and OPF ISBN both describe the same *The Death of Princes* publisher product. It does not establish which owner-private ebook content actually exists or explain how the inconsistent OPF metadata arose.
- **D1 — bounded dead end:** Attempted direct official URL under *The Death of Princes* path ending in `9780743421225`; web retrieval returned **inaccessible URL / tool Internal Error**, not a verified HTTP 404. Follow-up first-party exact-ISBN search identified the *Balance of Power* product E4. No negative universe-wide existence claim is supported by the failed direct URL probe.

### Evidence-backed verdict and remaining gate

- **H1 partially confirmed:** the official publisher title and author are identified for an *Infiltrator* eBook, but OPF0089 exact edition binding is unresolved.
- **H2 rejected in its simple same-title form:** official ISBN candidate belongs to a *different title*, so the OPF0091 identifier is cross-title conflicted against the displayed OPF title. Reason of corruption or edition provenance remains unknown.
- **H3 maintained:** source-local publisher metadata only; synopsis candidate HELD; no Work identity or coverage/public effect, no rights or private text claim.

**Next exact frontier:** read/reparse OPF0089 complete private package metadata and source contents under host-owned custody (not available in this wave) for author/ISBN evidence; separately inspect OPF0091 private publication metadata and content against two conflicting official titles without copying copyrighted text into this public repo. No automatic reattribution to *Balance of Power* is justified by its ISBN alone.
