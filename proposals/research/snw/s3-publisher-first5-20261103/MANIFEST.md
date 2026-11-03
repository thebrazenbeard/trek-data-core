# Strange New Worlds S3, first five Paramount+ publisher cards (proposal)

- Batch: `SNW.PPLUS.S3.FIRST5.20261103`
- Partition: SNW series-worker source-relative proposal; not Librarian inventory, Consolidator reconciliation, or accepted coverage.
- Accepted `main` at PR comparison: `e49ee5c51e2157ee505603b1394b511313ca50b7` (2026-11-03 observation; this proposal branch itself was created from earlier accepted `51afeedd3d976400e87a895ef402174d6af18873`).
- Primary metadata publisher: [Paramount+ Season 3 episode guide](https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/3/).
- Retrieval: 2026-11-03, Lappy WSL Python `urllib.request.urlopen`, HTTP 200, 271,774 raw response bytes, SHA-256 `a2b3363d658b003c83732945b75c23621f16bb4fc782fb395b2b0c2a79796863`; body not committed.
- **Volatile response observation:** a second same-day fetch was also HTTP 200, 271,774 bytes but SHA-256 `dffc10f7e996ab0de9f2acc671823468d720c93cabed2f687a3c742843994254`. Whole-document hashes are retrieval receipts, **not** immutable guide identity; an independent auditor must compare the five cards' actual fields rather than demanding persistent byte-for-byte page identity.
- Source lineage: all five cards and their thumbnail URLs derive from **one Paramount+ publisher page**; not five independent corroborations.
- **Previously accepted discovery lineage, not five newly discovered episodes:** `proposals/discovery/modern-paramount-season3-20261102/snw/bundle.json` already lists **ten** source-relative SNW S3 candidate episode slots (`SNW.PPLUS.S3.20261102`) from the *same* Paramount+ guide URL and independence group. This proposal adds publisher description/episode-video/thumbnail **evidence detail** to the first five of those already indexed candidate slots. The source-local records here do **not** create five additional canonical Works, independent corroborations, or coverage increments.
- Observation: HTML card title, S3/E ordinal, `datetime`, synopsis, video URL, and adjacent `img src` for episodes 1–5. Exact source lines/URLs are in `records.json`. The synopsis entries are fresh paraphrases, not copyrighted quotes.
- Research model: one publisher-guide `SOURCE`, five source-local candidate `WORK` records, nine source-local entity mentions, five source-relative `EVIDENCE` records, five `PUBLISHER_SUMMARY_MENTIONS` assertions. No global identity resolution is performed.
- Source scope: publisher editorial descriptions only. **No streaming episode, caption, full transcript or screenplay was accessed, and no episode-level plot claims are verified as depicted.**
- Artwork: five first-party thumbnail **locator candidates only**. License/publication status unassessed; no downloaded bytes, no hotlinking/public distribution/Explorer effect.
- Coverage/publication delta: **zero** accepted source bindings, **zero** admitted Works, **zero** audiovisual coverage, **zero** denominator changes, **zero** Explorer effects.
- Unresolved edge: S2 `Hegemony` vs S3 `Hegemony, Part II` title sequence does not justify automatically identifying Works or asserting a canonical sequel relation.
- No overlapping B006/B007 or SHORT partition records altered.

Validation command (from this directory):

```sh
python3 validate.py
python3 -m unittest test_validate.py -v
```

## Next gate

The independent Auditor should check the captured page's five title/ordinal/date/description/image associations and all line locators against the publisher guide (including response-digest volatility), and the Librarian should check whether any existing source-local IDs need revision. Only then should the Consolidator consider source binding/reconciliation through the accepted-evidence path; this packet has no direct live Explorer publishing effect.
