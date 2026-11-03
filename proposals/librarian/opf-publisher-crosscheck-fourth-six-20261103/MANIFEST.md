# Fourth librarian OPF publisher tranche: six first-party edition-metadata leads

**Date:** 2026-11-03 · **Original accepted base:** `a3ca40e94ef4c0a4ba47455333a0c122ded38c9a` · **Post-concurrency overlap check:** `cdb0a53efb1c9988d4e3cf008105d2cf7145228e`
**Disposition:** SOURCE-ONLY PROPOSAL. Every synopsis candidate is **HELD**. No Work/edition identity or Explorer coverage is claimed.

## Actual source work

1. Read the accepted sanitized owner-private OPF observation snapshot (`private-opf-metadata-20261103/observations.json`; SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`), plus the three accepted publisher crosscheck tranches containing **29 distinct prior OPF IDs**. The owner ZIPs and ebooks were not opened or exported.
2. Selected six checksum-valid OPF identifiers `0073`, `0082`, `0084`, `0085`, `0087`, `0088`. Source `0073` (*Grounded*) had been explicitly deferred when its first-party page could not be located in the preceding research pass; this wave independently located and read it. Initial draft head `bcf7c831d4528afe224b58352905f3f324f433f8` also included `0076` and `0079`, but independent librarian PR #345 subsequently merged those source-local IDs plus `0077–0078` into accepted main `cdb0a53e`. This corrective revision **supersedes those two overlapping draft rows**, replacing them with `0087` and `0088`; draft history remains visible in GitHub, but does not count as new accepted coverage.
3. For all six, directly checked the publicly rendered first-party Simon & Schuster **eBook** product page for ISBN13, title, author(s), date, and About the Book description. All six match the conversion of their OPF-declared checksum-valid ISBN10; this verifies a catalog metadata correlation, **not** that a private book has the catalog's contents.
4. Authored six short independent paraphrases of the official publisher descriptions, each with `synopsis_review_state=HELD_PUBLISHER_PARAPHRASE_NO_PRIVATE_TEXT`. These are **candidate catalog descriptions**, not close readings, accepted episode/novel synopses, canonical Work assertions, or approved Explorer display content.
5. Validated source-row fingerprints and upstream digest, ISBN checksums and conversion, tenable official URLs, publisher title/bylines/eBook/date, prior-batch nonoverlap, full-row reviewed SHA256 pins, exact JSON schema, recursive path protection and fail-closed no-admission flags. Mutation tests explicitly challenge fake synopsis, title, author, paths, ISBN, Work coverage and source claims.

## Source-local results

| OPF row | Official publisher product listing | eBook ISBN13 | Status |
| --- | --- | --- | --- |
| `0073` | [Grounded](https://www.simonandschuster.com/books/Grounded/David-Bischoff/Star-Trek-The-Next-Generation/9780743421089) — David Bischoff | `9780743421089` | Matching publisher ISBN; previous *page not located* lead resolved |
| `0082` | [Blaze of Glory](https://www.simonandschuster.com/books/Blaze-of-Glory/Simon-Hawke/Star-Trek-The-Next-Generation/9780743421232) — Simon Hawke | `9780743421232` | Matching publisher ISBN |
| `0084` | [Into the Nebula](https://www.simonandschuster.com/books/Into-the-Nebula/Gene-DeWeese/Star-Trek-The-Next-Generation/9780743421379) — Gene DeWeese | `9780743421379` | Matching publisher ISBN |
| `0085` | [The Last Stand](https://www.simonandschuster.com/books/The-Last-Stand/Brad-Ferguson/Star-Trek-The-Next-Generation/9780743421393) — Brad Ferguson | `9780743421393` | Matching publisher ISBN |
| `0087` | [Rogue Saucer](https://www.simonandschuster.com/books/Rogue-Saucer/John-Vornholt/Star-Trek-The-Next-Generation/9780743421164) — John Vornholt | `9780743421164` | Matching publisher ISBN; original held synopsis |
| `0088` | [Possession](https://www.simonandschuster.com/books/Possession/J-M-Dillard/Star-Trek-The-Next-Generation/9780743421171) — J.M. Dillard, Kathleen O'malley | `9780743421171` | Matching publisher ISBN; OPF combined creator and publisher byline differences held |

All six first-party pages listed `Pocket Books/Star Trek`, eBook format and September 22, 2000 as the product publication date at this snapshot. Public page URLs are preserved as locators. One publisher domain/source family generated all six observations—**not** six independent lineages. No direct raw publisher HTML response bytes were retained, and `publisher_raw_html_sha256` is null.

### Held material, unknowns and next boundary

- The OPF entry names, ISBN tokens and OPF-entry SHA256 fingerprints were inherited from the separately accepted host-audited **sanitized** snapshot. The original OPF containers' raw bytes were **not rechecked on the owner host during this wave**. Source-level hash verification of the committed derivative is not proof of private archive or ebook text identity.
- **Six original paraphrases remain held publisher-only candidates.** They describe publicly listed products; they cannot be asserted as close readings of private files, approved canonical literary synopses or global evidence-bearing Work facts.
- Accepted independent PR #345 already covers OPF `0076–0079` as separate publisher metadata/source-local crosswalk evidence; the revised batch contains **zero OPF source-local overlap** with its four IDs or the three older publisher tranches. That other packet does not admit private ebook content or global Work identity, and neither does this one. OPF `0080` remains outside this batch.
- No private eBook text, complete publisher overviews, actual filesystem locations, archive member names, cover images or other image bytes appear here. No accepted `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, `CLOSE_READ`, Work identity, publisher art, semantic reconciliation, Explorer projection or coverage denominator changes.

> **Hostile challenge:** An ISBN10 that converts to an actual publisher ISBN13 may still be stale or incorrectly attached to a privately converted text. A review of publisher catalog descriptions only verifies the publisher's claims. Text-source correspondence requires a future separately authorized, source-specific inspection.

## Repeatable local checks

From this directory:

```sh
python3 validate.py
python3 -O validate.py
python3 -m unittest -v test_validate.py
python3 -O -m unittest -v test_validate.py
```

The code-owned complete-row hashes require source re-review if publisher metadata, byline, locators, notes, or paraphrase changes. The validator disallows all four accepted #345 source IDs in addition to its prior three publisher batches; tests intentionally attack a #345 overlap, fabricated titles and synopsis content, path leakage, hidden fields and forbidden private/coverage promotions. These are **internal consistency** tests, not reproducible live publisher HTML-byte attestation.

**Next frontier:** independent reviewer must re-open the six exact first-party publisher ISBN pages, confirm source-local disjointness against accepted #345, then proceed to later unreviewed checksum-valid OPF rows. The Consolidator owns any later accepted evidence reconciliation and deterministic Explorer publication.
