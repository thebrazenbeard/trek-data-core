# TOS publisher-card title/slot verification of 13 legacy Explorer leads — B002

**Date:** 2026-11-03 UTC. **Role:** Librarian. **Status:** additive source-local proposal only.
**Selected accepted-main baseline:** `aebf9e8a69ab44919f2d89ab60dd1e824e05a807`.

## Actual new first-party checks

From the accepted 218-row `explorer/research-leads.json` (SHA-256 `efab937a...`), I selected **13 non-overlapping TOS candidates**: `lead:0006`, `0007`, `0009`–`0019` inclusive. The accepted B001 directory ledger had already directly rechecked `0000`–`0002`; the accepted five-QID first crosswalk covered `0003`, `0004`, `0005`, `0008`; the accepted 61-card overlay covers other series. None of the 13 selected IDs appeared in those prior accepted crosswalk batches. This proposal *does not overwrite* any of them.

I directly read three **official Paramount+ TOS full season guide pages** (the complete rendered card lists, not a third-party recap):

| Publisher source | Direct reader observation | Selected title/slot matches | Transient Lappy GET SHA-256 (raw HTML, not archived) |
|---|---|---:|---|
| [Season 1](https://www.paramountplus.com/shows/star_trek/episodes/1/) | 2026-11-03, `S1` title and card ordinal displayed together | 6 | `82128797a9bf54cfc4128f0ce1d2e26506e578b8b317af8b43abb9983aad4dc9` |
| [Season 2](https://www.paramountplus.com/shows/star_trek/episodes/2/) | 2026-11-03, `S2` title and card ordinal displayed together | 6 | `1be024161e1a3d7366f68f3d772db380dc3b9daf31201be79b7869d1c82a2a96` |
| [Season 3](https://www.paramountplus.com/shows/star_trek/episodes/3/) | 2026-11-03, `S3` title and card ordinal displayed together | 1 | `c6d7c064b950e387ae704999ddffcbfd1a5ddbaec948762a0d63b74191a4da4f` |

The separate Lappy HTTP 200 responses yielded these SHA values from a streaming hash operation. **The response bodies were not archived or copied into GitHub.** The independently rendered guide read supports the card claims; it is not byte-linked to those transient HTML hashes, whose bytes cannot be replayed. Dynamic page changes may legitimately produce new hashes on later GETs. Offline validators test the historical observation *record*, not the live website or source reproducibility.

The new `observations.json` records each archived Wikidata-derived candidate **QID, source-local title**, exact observed publisher **title, season, episode slot**, guide URL, and SHA-256 of a short **publisher own-card description**. Description text is not copied; no complete audiovisual work or transcript was read. All 13 records retain source provenance labels and are **candidate crosswalks**, not Work identities. Paramount+ is one publisher corporate family; two web surfaces in that family would not constitute independent corroboration.

**12 exact title matches, one deliberately unresolved punctuation difference:**

> `lead:0006` (Wikidata-derived `Charlie X`) versus Paramount+ Season 1 Episode 3 displayed as `Charlie "X"`. This is likely a presentation difference but remains `PUNCTUATION_VARIANT_HELD`; the Librarian does not silently declare canonical Work identity.

The Paramount+ TOS guides are **streaming edition-specific**. Season 1 lists *The Cage* at slot 1, which can differ from broadcast chronology; neither airing order nor global season/episode identity is asserted here.

## Non-effects and next frontier

- **13/218 candidate source-local publisher metadata checks proposed**, not 13 verified audiovisual Works and **not** research coverage admitted.
- No edition-resolved Source↔Work binding, global identity, full source close-read, neutral semantic analysis, new synopsis, index denominator, or Explorer page publication.
- No copied image data, artwork use, release permission or new displayed thumbnail.
- Archived Wikidata source lineage is not authenticated by a historical query snapshot; QIDs remain external discovery IDs rather than canonical Work IDs.
- Crosswalk must undergo independent hostile review, exact GitHub CI, and separately authorized acceptance before any promoted projection.

**Next:** choose 10–15 of `lead:0020` onward without accepted overlap; for *The Animated Series*, confirm whether the official series guide distinguishes episode slots and special-order ambiguities before binding. A separate Consolidator may later consume independently accepted source-local verifications in an Explorer projection, with row-level source binding and no silent coverage promotions.

## Local reproducibility checks

```bash
python -B proposals/librarian/tos-leads-official-guide-b002-20261103/validate.py
python -B -m unittest discover -s proposals/librarian/tos-leads-official-guide-b002-20261103 -p 'test_*.py' -v
python -O -B -m unittest discover -s proposals/librarian/tos-leads-official-guide-b002-20261103 -p 'test_*.py' -q
python -B tools/validate.py
```

These protect row IDs, archived QIDs, same-card description hashes, exact season/slot, official host and URL, independent-family labels, historical nonreplayable SHA receipts, and all forbidden publication/Work/coverage effects. Source readers must independently re-open official pages for live-content verification.
