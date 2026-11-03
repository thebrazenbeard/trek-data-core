# Librarian source proposal: third tranche of ten OPF ↔ publisher eBook checks

**Research snapshot:** 2026-11-03 · **Accepted base:** `a3132cce8ffff240f34ca8f9659f7fffe8c702d8`
**Status:** proposed source-relative publisher metadata, not edition, author, global Work or coverage admission.

## Completed bounded processing

1. Read the previously accepted sanitized owner-private OPF observation file, `private-opf-metadata-20261103/observations.json`, SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`. The private OPF archive has 347 catalogued entries and 75 entries with at least one checksum-valid ISBN candidate. This batch did **not** open the source ZIP or ebook content.
2. Excluded the first nine and second ten accepted librarian publisher records. Selected **ten previously unreviewed ISBN leads**: `opf-local:0062`, `0063`, `0064`, `0065`, `0067`, `0068`, `0069`, `0070`, `0074`, and `0075`.
3. Independently retrieved and read the rendered first-party **Simon & Schuster** eBook product listings below. Each supports the converted ISBN13, source-specific official product title, byline, eBook format, public publication date and an About the Book overview. All ten source-local checksum-valid ISBN10 conversions match the respective publisher product ISBN13. No second independent publisher or raw publisher HTML-byte receipt is claimed.
4. Generated ten original short synopsis paraphrases based on the *publisher descriptions*, not on unread private book text. Preserved the OPF spelling error `PRECHANCE TO DREAM` alongside publisher `Perchance to Dream` as `PUBLISHER_ISBN_MATCH_TITLE_SPELLING_CONFLICT_UNRESOLVED` in source-relative evidence. Other punctuation/capitalization/combined-creator variants remain source-relative; no person or Work reconciliation was performed.
5. Ran source-digest, source-local hash, ISBN checksum/conversion, publisher locator, reviewed full-record digest, closed-schema, non-overlap, private-path leakage, null raw custody, Work/coverage, and adversarial mutation validations.

## Official publisher results

| OPF local | First-party publisher product | eBook ISBN13 | Outcome |
| --- | --- | --- | --- |
| `0062` | [Exiles](https://www.simonandschuster.com/books/Exiles/Howard-Weinstein/Star-Trek-The-Next-Generation/9780743420945) | `9780743420945` | ISBN/product metadata match |
| `0063` | [Fortune's Light](https://www.simonandschuster.com/books/Fortunes-Light/Michael-Jan-Friedman/Star-Trek-The-Next-Generation/9780743420952) | `9780743420952` | ISBN/product metadata match |
| `0064` | [Contamination](https://www.simonandschuster.com/books/Contamination/John-Vornholt/Star-Trek-The-Next-Generation/9780743420969) | `9780743420969` | ISBN/product metadata match |
| `0065` | [Boogeymen](https://www.simonandschuster.com/books/Boogeymen/Mel-Gilden/Star-Trek-The-Next-Generation/9780743420976) | `9780743420976` | ISBN/product metadata match |
| `0067` | [Perchance to Dream](https://www.simonandschuster.com/books/Perchance-to-Dream/Howard-Weinstein/Star-Trek-The-Next-Generation/9780743420990) | `9780743420990` | ISBN match; **OPF title spelling conflict held** |
| `0068` | [Spartacus](https://www.simonandschuster.com/books/Spartacus/T-L-Mancour/Star-Trek-The-Next-Generation/9780743421003) | `9780743421003` | ISBN/product metadata match |
| `0069` | [Chains of Command](https://www.simonandschuster.com/books/Chains-of-Command/W-A-McCay/Star-Trek-The-Next-Generation/9780743421010) | `9780743421010` | ISBN/product metadata match; two distinct publisher bylines |
| `0070` | [Imbalance](https://www.simonandschuster.com/books/Imbalance/V-E-Mitchell/Star-Trek-The-Next-Generation/9780743421027) | `9780743421027` | ISBN/product metadata match |
| `0074` | [The Romulan Prize](https://www.simonandschuster.com/books/The-Romulan-Prize/Simon-Hawke/Star-Trek-The-Next-Generation/9780743421096) | `9780743421096` | ISBN/product metadata match |
| `0075` | [Guises of the Mind](https://www.simonandschuster.com/books/Guises-of-the-Mind/Rebecca-Neason/Star-Trek-The-Next-Generation/9780743421102) | `9780743421102` | ISBN/product metadata match |

Each official catalog page lists the publisher `Pocket Books/Star Trek`, **eBook** format and September 22, 2000 publication date. Each record in `records.json` contains a source-local OPF entry SHA-256, the original ISBN10 candidate, its verified checksum conversion, exact publisher catalog ISBN13/URL/title/byline/date, an original publisher description paraphrase and an explicit evidence limitation. The ten URLs are **one upstream publisher family**, not ten independent corroborating sources.

## Held discovery and evidence limits

- Source entry `opf-local:0073` (*Grounded*, source ISBN10 `0743421086`) was encountered in the inventory, but a bounded public-first-party search did **not locate a matching official publisher eBook product page** for its converted ISBN13 `9780743421089`. It is **deferred**, not counted among the ten crosschecked records and not asserted nonexistent. Future workers should try publisher archives or exact format alternatives and keep result uncertainty.
- Source `0067` spells its OPF title `PRECHANCE TO DREAM`; publisher title is `Perchance to Dream`. Do not rewrite the OPF spelling or silently infer global Work equivalence from numerical ISBN correlation.
- The public publisher pages were inspected through rendered page/search content. No reproducible raw website HTML bytes or raw-page content SHA is held; `publisher_raw_html_sha256` is `null`. Product URLs are source locators, not content fingerprints.
- The accepted OPF row fingerprints refer to a separately host-audited **sanitized owner-private metadata snapshot**; the private OPF archive and converted ebooks were not opened or rehashed during this batch. No private member paths, cover art, full publisher blurbs, ebooks, chapters, dialogue, or copyrighted content are exported.
- **No** `SOURCE_BOUND`/`FULL_TEXT_AVAILABLE`/`CLOSE_READ`/`SEMANTICALLY_ANALYZED` status, author identity resolution, edition binding, global Work admission, coverage increase, reconciliation, or Explorer projection results from this source-only proposal. The ten publisher paraphrases are catalog descriptions, not primary full-work analysis.

> **Hostile challenge:** ISBN check digits and a public publisher ISBN match verify bibliographic metadata correlation, not source-text equivalence. A converter could embed a valid but wrong book ISBN; one publisher family could propagate its own metadata mistakes. The OPF `PRECHANCE` spelling conflict is direct evidence that source-relative strings must remain intact.

## Reproduction

From this directory:

```sh
python3 validate.py
python3 -O validate.py
python3 -m unittest -v test_validate.py
python3 -O -m unittest -v test_validate.py
```

The validator compares accepted source metadata, both predecessor publisher batches, exact ISBN conversion and publisher URL patterns, and code-owned SHA-256 pins over complete reviewed records; it rejects unreviewed field/prose mutations and recursive private path strings. These checks **cannot** independently attest a live publisher webpage or uninspected private book body. Independent source review and exact-head CI are required before accepting the proposal.

**Next frontier:** resolve or explicitly hold `0073` through a sourced edition check; then continue the next nonduplicative checksum-valid OPF leads after `0075`. The Consolidator alone decides any later accepted evidence reconciliation or deterministic Explorer integration.
