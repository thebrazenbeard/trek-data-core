# Enterprise Season 4 — final E21–E22 official publisher guide (HELD)

**Evidence class:** One complete first-party Paramount+ season-4 episode-guide HTML source, *not* two episode videos. This is a source-relative research proposal, not an accepted canonical Work, audiovisual CLOSE_READ, official coverage increment, or public Explorer release.

## Source retrieval and method

- First-party page: https://www.paramountplus.com/shows/enterprise/episodes/4/
- Read date (UTC): 2026-11-04T22:38:16.420232+00:00; HTTP response Date: Wed, 04 Nov 2026 22:38:16 GMT; status 200.
- Full HTML response: **301,606 bytes**, SHA-256 `8790bff4111c5ad3b0bafc1491189373998eae3b3498addddb6594d7237418a9`.
- All **22** season-4 cards were structurally inspected and their normalized titles, ordinals, video *route strings only*, page line locators, and description SHA-256s compared to the four earlier source observations. All 22 normalized fingerprints agree. The byte-level HTML SHA-256 differs among responses; no claim of byte-identical snapshots.
- Only the two remaining publisher descriptions (E21 and E22, 109 + 123 = **232 source characters**) were actually read for original brief paraphrases. Their copyrighted source paragraphs and raw HTML are not committed.
- Exact source parser: `source_probe.py`, importing the first-batch parser. `validate.py` checks predecessor file digests, their independent deterministic validators, exact source snapshot and all five disjoint ordinal scopes. `test_validate.py` actively challenges identity, title-case, source-lineage, and coverage inflation.

| Publisher source-local slot | Title as card H2 / analytics leaf | HTML anchor / description line | Description SHA-256 |
| --- | --- | ---: | --- |
| E21 | Terra Prime | 2042 / 2060 | `8feccc9522fde17b61d59a9dc0526bd60c3b985868b3a69c05b3f63fe433f903` |
| E22 | These Are the Voyages | 2070 / 2088 | `2e73d100233573f99ffcec035e3d40692d40a727afd4769daffbd779c09795cd` |

The original publisher-description paraphrases are in `records.json` as source-relative evidence. Assertions use `PUBLISHER_DESCRIBES`, not “episode proves.”

## E22 publisher-internal title token conflict

The **same HTML card** gives distinct spelling in two source-local locations:

| Source-local field | Exact title token | Source locator |
| --- | --- | --- |
| Card `h2` | These Are the Voyages | Card whose anchor begins HTML line 2070 |
| `aa-link` leaf segment | These Are the Voyages | HTML `aa-link` leaf at line 2070 |
| `aa-link` series-prefixed segment | These Are The Voyages | HTML `aa-link` series title at line 2070 |

The distinction is only the casing of *the/The*. That is a useful parser identity observation, but **not independent corroboration**, because all three tokens are in one publisher page. Exact spelling and canonical-title reconciliation remain **UNRESOLVED**; no global Work identity or title was selected.

## Predecessor lineage and honest completion

This local commit depends on these exact non-overlapping HELD research batches:

1. E01–E05 — commit `9da214b3231870c3879f9f645e9bf9e9ab6f7c53`; records SHA-256 `f8e65b062b7b53929341d6dbca31dd20f29bf09f995b9a5daf628dc12b6e4f10`.
2. E06–E10 — `1bd2d94506815a2039d95a5dbabc932ef6a35cfd`; SHA-256 `a21928c263501e34be287ffd2c8524267ab30fa50e19dca1262ae8c0b9e49b05`.
3. E11–E15 — `1dcd8662c2e7f0fdd7c9fd60fce789a28f2e841c`; SHA-256 `8515c84c55a4dd13d622d4d249624ed0b70b54e0a939ec792ee23cc13bf4bba7`.
4. E16–E20 — `c055a88d742ea48a4e095b9861cd6308811ca731`; SHA-256 `d84d077f9eb8ca82ec02f9962dfc2a78166f11f7dc1001aab7b37e5894bd9a5a`.
5. E21–E22 — this **final two-description HELD packet**, precisely two new entries. There is no E23 on the observed page and no fictional E23 packet.

**Closed within its narrow scope:** 22/22 publisher-guide descriptions have source-relative original research paraphrases in **five HELD packets**. One `publisher:paramountplus.com` source lineage across five page reads, not five witnesses. All remain proposals; **zero accepted Source bindings, Work bindings, audiovisual/full-script CLOSE_READs, semantic reconciliations, public Explorer effects, or coverage gains** arise from these packets.

**Next genuine frontier:** A Librarian/Consolidator review of proposal provenance and title spelling, plus rights-aware access to actual full primary episode material before any audiovisual CLOSE_READ. Do not substitute this publisher-guide packet for episode-content review.

No remote push, merge, deployment, full copyrighted prose, artwork, transcripts, or audiovisual bytes.
