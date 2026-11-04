# LIT: independent first-party page recheck of seven held OPF edition leads

**Status: independent LIT review, proposal only; source/edition admission `0`, literary close reads `0`, Work identity decisions `0`, public Explorer releases `0`.** Reviewed against accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91` on **2026-11-04**. Issue #23's close-read/source-admission hold remains in force.

## Scope and observation method

I independently opened the **rendered full Simon & Schuster product pages**, not snippets, for all seven source-local OPF rows represented by `proposals/research/opf-seven-official-editions-20261103/observations.json`. The first OPF row has two format-specific publisher products, so this is **seven local source rows, eight publisher products, one publisher corporate lineage**. I inspected visible book headings, author/byline, format, series line, the book-description section, and `Product Details` for publisher/imprint, product date, page extent, and ISBN13. I did not fetch raw HTTP response bytes; no immutable HTML body hashes are claimed. Page presentation may change and must be rechecked before future source decisions.

The accepted 347-row private OPF derivative and its former independent owner-host source/member digests are previous receipts. **I did not open or read any owner-private `.lit`, `.txt`, OPF XML, chapter prose, or covers**, and I cannot independently elevate derivative-to-original authenticity or source-to-Work equivalence. All `opf-local:*` labels stay local. The public publisher descriptions are advertising/source testimony, not ground-truth fictional events, canon classifications, or substitute close reads.

## Exact source-local recheck

| OPF local | First-party rendered publisher product | Format / ISBN13 | Product Details and metadata recheck | Disposition |
|---|---|---|---|---|
| `0110` | [*A Time for War, A Time for Peace* — 2004 ebook](https://www.simonandschuster.com/books/A-Star-Trek-The-Next-Generation-Time-9-A-Time-for-War-A-Time-for-Peace/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation/9780743499972) | ebook `9780743499972` | Keith R. A. DeCandido; Pocket Books/Star Trek; 2004-10-01; 384 pp.; TNG page #9. The earlier independent original-XML ISBN10 `0-7434-9997-2` converts to this ISBN13, but I have not rechecked owner XML. | Publisher bibliographic candidate; source-text identity held |
| `0110` | [*A Time for War, A Time for Peace* — 2019 trade](https://www.simonandschuster.com/books/A-Star-Trek-The-Next-Generation-Time-9-A-Time-for-War-A-Time-for-Peace/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation/9781982134907) | trade paperback `9781982134907` | Same byline; **Gallery Books**; 2019-05-18; 384 pp.; TNG page #9. A separate ISBN/format/imprint/date; never collapse into the 2004 ebook edition. | Separate publisher product; source-text identity held |
| `0150` | [*Yesterday's Son*](https://www.simonandschuster.com/books/Yesterdays-Son/A-C-Crispin/Star-Trek-The-Original-Series/9780743419628) | ebook `9780743419628` | A.C. Crispin; Pocket Books/Star Trek; 2000-09-22; 192 pp.; TOS page #11. OPF-added Yesterday Saga label not independently edition-bound. | No discrepancy in published product fields; held |
| `0181` | [*Doctor's Orders*](https://www.simonandschuster.com/books/Doctors-Orders/Diane-Duane/Star-Trek-The-Original-Series/9780743420013) | ebook `9780743420013` | Diane Duane; Pocket Books/Star Trek; 2000-09-22; 291 pp.; TOS page #50. | No discrepancy in published product fields; held |
| `0275` | [*Homecoming*](https://www.simonandschuster.com/books/Homecoming/Christie-Golden/Star-Trek-Voyager/9780743475631) | ebook `9780743475631` | Christie Golden; Pocket Books/Star Trek; 2003-05-12; 288 pp.; Voyager **part of series**, no publisher series ordinal shown. Already accepted as same-family publisher lead `SSEBOOK-VOY-HOMECOMING-9780743475631`. | Do not double-count independent sources; held |
| `0296` | [*The Heart of the Warrior*](https://www.simonandschuster.com/books/The-Heart-of-the-Warrior/John-Gregory-Betancourt/Star-Trek-Deep-Space-Nine/9780743420488) | ebook `9780743420488` | John Gregory Betancourt; Pocket Books/Star Trek; 2000-09-22; 288 pp.; DS9 page #17. | No discrepancy in published product fields; held |
| `0326` | [*Enterprise: Shockwave*](https://www.simonandschuster.com/books/Star-Trek-Enterprise-Shockwave/Paul-Ruditis/Star-Trek-Enterprise/9780743464574) | ebook `9780743464574` | Paul Ruditis; Pocket Books/Star Trek; 2002-10-30; 256 pp.; Enterprise **part of series**, no series ordinal shown. Publisher marketing description does not constitute TV transcript or event evidence. | No discrepancy in published product fields; held |
| `0335` | [*Fire On High*](https://www.simonandschuster.com/books/Fire-On-High/Peter-David/Star-Trek-The-Next-Generation/9780743455725) | ebook `9780743455725` | Peter David; Pocket Books/Star Trek; 2002-08-04; 288 pp. Publisher page oddly presents **TNG #6**, while source-local OPF labels **New Frontier #6**. Publisher description mentions the Excalibur, but is not a neutral adjudication of series taxonomy or canon. | **Series/continuity classification remains CONTESTED; held** |

All eight displayed product ISBN13 values pass the ISBN13 checksum. The distinct 2004 ISBN10↔ISBN13 link is only an **edition metadata correspondence**, not verification of private ebook text. I found **zero contradicting title/byline/format/imprint/date/pages/ISBN13 fields** relative to the pinned held publisher proposal; that is a bounded result, not an authenticity finding.

> **Hostile challenge:** The publisher itself can label *Fire On High* TNG #6 while source-local metadata calls it *New Frontier* #6. Treating the first-party navigation category as a canonical/continuity resolution would erase the disagreement. Conversely, treating the owner's OPF label as definitive would be equally unsupported. Keep both labels with distinct source provenance and do not admit a resolved Work or continuity class.

> **Hostile challenge:** The retained first-party links and their printed details can be checked on a later date, but our `validate.py` merely pins the accepted *local receipt* and its invariants. Its passing does not prove that the network page stayed unchanged, that a private file has matching text, or that these eight publisher products are eight distinct Works.

## Deterministic receipt checks

```sh
python3 proposals/research/lit/opf-seven-publisher-page-audit-20261104/validate.py
python3 -m unittest discover -s proposals/research/lit/opf-seven-publisher-page-audit-20261104 -p 'test_validate.py' -v
python3 tools/build_opf_seven_publisher_crosschecks.py --check
```

**Next frontier:** A separately reviewed source-identifier extraction correction for `opf-local:0110`, with its original `dc:Identifier` case preserved; then governed source/edition correspondence under issue #23. No new literary content coverage from this review.
