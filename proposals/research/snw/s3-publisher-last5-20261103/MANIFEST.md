# SNW Season 3, episodes 6–10: source-relative Paramount+ card packet

**State:** PROPOSAL ONLY. Publisher metadata/synopsis observed; episodes not watched/read; no accepted source binding, Work admission, database, or Explorer effect.

- Batch `SNW.PPLUS.S3.LAST5.20261103`; partition: SNW series research worker.
- Accepted `main` inspected: `e49ee5c51e2157ee505603b1394b511313ca50b7` on 2026-11-03 UTC.
- First-party metadata source: [Paramount+ Strange New Worlds Season 3 guide](https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/3/).
- Direct retrieval 2026-11-03 UTC: HTTP 200 HTML, **271,803 response bytes**, SHA-256 `a970f41f9257adc002d86d7036dd0e495d0c3e92a9c51b2ef234638e859317bb`. Private retrieval snapshot was inspected and not committed. Page is dynamic; this digest is one retrieval receipt, not immutable publisher-edition identity.
- Direct read, five actual cards: E06 *The Sehlat Who Ate Its Tail* HTML lines **1630–1654**; E07 *What is Starfleet?* **1658–1682**; E08 *Four-and-a-Half Vulcans* **1686–1710**; E09 *Terrarium* **1714–1738**; E10 *New Life and New Civilizations* **1742–1766**. Each span includes adjacent title `h2`, S3/E ordinal `abbr`, `time[datetime]`, episode video URL, publisher description, and image `src`.
- Source lineage: all five descriptions and image locators derive from **one Paramount+ publisher page**, not five independent confirmations. No Wikipedia/Memory Alpha metadata was used to inflate agreement.
- Existing accepted `proposals/discovery/modern-paramount-season3-20261102/snw-observed-slots.csv` **already identifies ten Season 3 title/ordinal slots including E06–E10**. This packet enriches the same five observed slots with source-relative descriptions and locators; it does **not** claim five new unique or admitted Works. The proposed E01–E05 richer packet is independent draft PR #314 (same upstream publisher family), not accepted baseline.
- Research chain: one publisher-guide `SOURCE`; five candidate source-local `WORK` records; seven work-local mentions; five `PUBLISHER_DESCRIPTION` evidence observations; five narrow assertions of what the publisher says. No global identity reconciliation.
- Original paraphrases are tagged `PUBLISHER_TEXT_ONLY`. **No streaming episode, official screenplay, subtitle, caption track, complete transcript or audio was inspected.** An editorial teaser is not observed fictional-world truth.
- Artwork is **five URL source candidates only** from the guide; rights unassessed; no fetched bytes, download, public hotlinks, or Explorer publication.
- Observed dates reproduce source `datetime` and UTC offset, which should not be flattened to a calendar day outside that time zone.
- Coverage effects: zero accepted `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, `STRUCTURALLY_INDEXED`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, `ENTITY_LINKED`, `CROSS_REFERENCED`, and `AUDITED` admissions. No denominator change or production compilation.

## Local deterministic validation

```sh
python3 proposals/research/snw/s3-publisher-last5-20261103/validate.py
python3 -m unittest discover -s proposals/research/snw/s3-publisher-last5-20261103 -p 'test_*.py' -v
```

## Next independent gates

The Auditor should re-retrieve/compare the five current publisher cards (including dynamic-page drift) and detect semantic overreach in each paraphrase. The Librarian should check collisions with accepted SNW S3 slot observations. The Consolidator can later propose source binding and a deterministic projection only after the accepted evidence path; no automatic indexing/Explorer update is authorized by this source-only packet.
