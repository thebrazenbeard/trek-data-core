# HELD: nine additional contiguous TNG edition metadata leads (OPF 0062–0070)

**Scope:** separate local research proposal based on accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91` and preceding local-only seven-row proposal `3265e4a`. Nothing here is admitted, merged, pushed, deployed, or projected into the public Explorer. No new Source/Work, canonical Evidence/Assertion, copyright release, semantic read, or coverage count is authorized by this metadata packet.

## Source chain

1. Accepted-public metadata receipt `proposals/librarian/private-opf-metadata-20261103/observations.json`, pinned by SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`, contributed **OPF-local** titles and eight ISBN10 claims; not ebook text or original LIT identity. The ninth OPF `0066` has no creator or ISBN in the receipt, so it remains title-only.
2. Nine official **Simon & Schuster** product pages read 2026-11-04 contributed publisher bibliographic facts and their short promotional descriptions. The *Exiles* page resolved under the publisher's `.net` domain; the remaining eight under its `.com` domain. Both are the **same publisher upstream family**, not independent witnesses. Web retrieval pages were inspected through search, but source HTML bytes were **not locally fingerprinted/snapshotted**, and publisher URLs need re-verification before any admission.
3. Nine `held_synopsis` strings are original, one-sentence paraphrases of publisher descriptions only. Their provenance is **publisher copy**; none was derived from a close read of an ebook, dialogue, original transcript or canon audit.

| Owner-local OPF | Publisher title | OPF ISBN10 | Official publisher ISBN13 | Metadata match state | Official page |
| --- | --- | --- | --- | --- | --- |
| `0062` | *Exiles* | `0743420942` | `9780743420945` | Checksum only | [S&S .net](https://www.simonandschuster.net/books/Exiles/Howard-Weinstein/Star-Trek-The-Next-Generation/9780743420945) |
| `0063` | *Fortune's Light* | `0743420950` | `9780743420952` | Checksum only | [S&S](https://www.simonandschuster.com/books/Fortunes-Light/Michael-Jan-Friedman/Star-Trek-The-Next-Generation/9780743420952) |
| `0064` | *Contamination* | `0743420969` | `9780743420969` | Checksum only | [S&S](https://www.simonandschuster.com/books/Contamination/John-Vornholt/Star-Trek-The-Next-Generation/9780743420969) |
| `0065` | *Boogeymen* | `0743420977` | `9780743420976` | Checksum only | [S&S](https://www.simonandschuster.com/books/Boogeymen/Mel-Gilden/Star-Trek-The-Next-Generation/9780743420976) |
| `0066` | *Q-in-Law* | **Absent** | `9780671040994` | **UNVERIFIED title-only** | [S&S](https://www.simonandschuster.com/books/Q-in-Law/Peter-David/Star-Trek-The-Next-Generation/9780671040994) |
| `0067` | *Perchance to Dream* | `0743420993` | `9780743420990` | Checksum only; OPF title anomaly | [S&S](https://www.simonandschuster.com/books/Perchance-to-Dream/Howard-Weinstein/Star-Trek-The-Next-Generation/9780743420990) |
| `0068` | *Spartacus* | `0743421000` | `9780743421003` | Checksum only | [S&S](https://www.simonandschuster.com/books/Spartacus/T-L-Mancour/Star-Trek-The-Next-Generation/9780743421003) |
| `0069` | *Chains of Command* | `0743421019` | `9780743421010` | Checksum only | [S&S](https://www.simonandschuster.com/books/Chains-of-Command/W-A-McCay/Star-Trek-The-Next-Generation/9780743421010) |
| `0070` | *Imbalance* | `0743421027` | `9780743421027` | Checksum only | [S&S](https://www.simonandschuster.com/books/Imbalance/V-E-Mitchell/Star-Trek-The-Next-Generation/9780743421027) |

These are **nine edition metadata leads**, eight owner OPF ISBN10→publisher ISBN13 checksum alignments, one title-only unresolved OPF candidate, zero accepted Works. They are non-overlapping with predecessor OPF IDs `0055–0061` (seven rows) and the older **ten** HELD draft edition ISBNs in the private preview. None of these numbers can be added to canonical book coverage.

## Explicit anomalies and non-evidence

- `0066`: The OPF receipt's local title is `Star Trek - Q-In-Law` with **empty creator and ISBN fields**. Publisher details about Peter David and ISBN13 belong **only to the publisher page**, not authenticated private ebook files. The typed state is `UNVERIFIED_LOCAL_TITLE_ONLY`.
- `0067`: The OPF local source writes `PRECHANCE TO DREAM`; the publisher writes `Perchance to Dream`. This potentially straightforward typo remains `OPF_PRECHANCE_VS_PUBLISHER_PERCHANCE_UNRESOLVED`; no silent global title reconciliation.
- Metadata dates in the converted owner OPF package differ from publisher U.S. eBook dates for several rows. They may reflect transformations, other release events or mistakes; this metadata packet **does not equate or overwrite the dates**.
- One publisher controls both `.net` and `.com` pages; downstream metadata copied among catalogs does not multiply independent confirmation.
- Owner OPF package bytes are not established as corresponding to original LIT content or a precise publisher eBook edition. ISBN string agreement is insufficient for content custody, completeness or legal read authority.

## Validation, hostile falsifiers and next gate

```bash
python3 proposals/research/lit_opf_publisher_nine_20261104/validate.py
python3 -m unittest tests.test_lit_opf_publisher_nine_held -v
```

The strict validator pins all nine OPF-local IDs, original OPF metadata source SHA and entry fingerprints; first-party publisher URLs, exact host, ISBN13, titles, authors, dates and extents; checksum alignment for only the eight ISBN-bearing local rows; and zero-effect/no-private-text flags. Adversarial tests reject row swaps, forged work IDs, source promotion, URL host/lookalike, unreviewed publisher rehosting, publisher-title replacement, and false claims of independent source families.

> **Hostile challenge:** Nine product-page observations may be perfectly accurate bibliographically and still offer zero evidence that any source was completely read. The proposed descriptions are publisher-derived labels, not close-read claims.

> **Hostile challenge:** A matching checksum is not a byte-equivalence test. The owner-private OPF or LIT may differ in manifestation, chapter contents, conversion, omissions or authorization from the publisher product.

> **Hostile challenge:** *Q-in-Law* has no local ISBN/creator in the accepted OPF receipt. A publisher page with a matching title does **not** fill those private-source fields or justify an edition/source link.

> **Hostile challenge:** Auto-correcting `PRECHANCE` might make the catalog appear cleaner while erasing evidence of conversion metadata quality. Keep both literal spellings and the unresolved proposal state.

**Next frontier:** independent refresh and stable publisher metadata receipt; review creator/title/date anomalies; prove source/edition custody separately from owner filename/OPF assertions; determine rights/read access before any full-text literary analysis. A separate Consolidator/Auditor review must authorize any move out of HELD; no remote or public projection effects were performed here.
