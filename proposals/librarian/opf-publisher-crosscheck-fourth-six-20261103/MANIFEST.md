# Fourth librarian OPF publisher tranche: six first-party edition-metadata leads

**Date:** 2026-11-03 · **Accepted base:** `a3ca40e94ef4c0a4ba47455333a0c122ded38c9a`
**Disposition:** SOURCE-ONLY PROPOSAL. Every synopsis candidate is **HELD**. No Work/edition identity or Explorer coverage is claimed.

## Actual source work

1. Read the accepted sanitized owner-private OPF observation snapshot (`private-opf-metadata-20261103/observations.json`; SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`), plus the three accepted publisher crosscheck tranches containing **29 distinct prior OPF IDs**. The owner ZIPs and ebooks were not opened or exported.
2. Selected six nonduplicative checksum-valid OPF identifiers `0073`, `0076`, `0079`, `0082`, `0084`, `0085`. Source `0073` (*Grounded*) had been explicitly deferred when its first-party page could not be located in the preceding research pass; this wave independently located and read it.
3. For all six, directly checked the publicly rendered first-party Simon & Schuster **eBook** product page for ISBN13, title, author(s), date, and About the Book description. All six match the conversion of their OPF-declared checksum-valid ISBN10; this verifies a catalog metadata correlation, **not** that a private book has the catalog's contents.
4. Authored six short independent paraphrases of the official publisher descriptions, each with `synopsis_review_state=HELD_PUBLISHER_PARAPHRASE_NO_PRIVATE_TEXT`. These are **candidate catalog descriptions**, not close readings, accepted episode/novel synopses, canonical Work assertions, or approved Explorer display content.
5. Validated source-row fingerprints and upstream digest, ISBN checksums and conversion, tenable official URLs, publisher title/bylines/eBook/date, prior-batch nonoverlap, full-row reviewed SHA256 pins, exact JSON schema, recursive path protection and fail-closed no-admission flags. Mutation tests explicitly challenge fake synopsis, title, author, paths, ISBN, Work coverage and source claims.

## Source-local results

| OPF row | Official publisher product listing | eBook ISBN13 | Status |
| --- | --- | --- | --- |
| `0073` | [Grounded](https://www.simonandschuster.com/books/Grounded/David-Bischoff/Star-Trek-The-Next-Generation/9780743421089) — David Bischoff | `9780743421089` | Matching publisher ISBN; previous *page not located* lead resolved |
| `0076` | [Here There Be Dragons](https://www.simonandschuster.com/books/Here-There-Be-Dragons/John-Peel/Star-Trek-The-Next-Generation/9780743421119) — John Peel | `9780743421119` | Matching publisher ISBN |
| `0079` | [Foreign Foes](https://www.simonandschuster.com/books/Foreign-Foes/Dave-Galanter/Star-Trek-The-Next-Generation/9780743421140) — Dave Galanter, Greg Brodeur | `9780743421140` | Matching publisher ISBN; public two-author byline retained |
| `0082` | [Blaze of Glory](https://www.simonandschuster.com/books/Blaze-of-Glory/Simon-Hawke/Star-Trek-The-Next-Generation/9780743421232) — Simon Hawke | `9780743421232` | Matching publisher ISBN |
| `0084` | [Into the Nebula](https://www.simonandschuster.com/books/Into-the-Nebula/Gene-DeWeese/Star-Trek-The-Next-Generation/9780743421379) — Gene DeWeese | `9780743421379` | Matching publisher ISBN |
| `0085` | [The Last Stand](https://www.simonandschuster.com/books/The-Last-Stand/Brad-Ferguson/Star-Trek-The-Next-Generation/9780743421393) — Brad Ferguson | `9780743421393` | Matching publisher ISBN |

All six first-party pages listed `Pocket Books/Star Trek`, eBook format and September 22, 2000 as the product publication date at this snapshot. Public page URLs are preserved as locators. One publisher domain/source family generated all six observations—**not** six independent lineages. No direct raw publisher HTML response bytes were retained, and `publisher_raw_html_sha256` is null.

### Held material, unknowns and next boundary

- The OPF entry names, ISBN tokens and OPF-entry SHA256 fingerprints were inherited from the separately accepted host-audited **sanitized** snapshot. The original OPF containers' raw bytes were **not rechecked on the owner host during this wave**. Source-level hash verification of the committed derivative is not proof of private archive or ebook text identity.
- **Six original paraphrases remain held publisher-only candidates.** They describe publicly listed products; they cannot be asserted as close readings of private files, approved canonical literary synopses or global evidence-bearing Work facts.
- Candidate OPF `0077` (*Sins of Commission*) surfaced a related public publisher listing under a different ISBN13 in this preliminary search; exact private format/edition equivalence was not established. `0077`, `0078`, and `0080` were **not counted** in this completed six-item batch and require separate source-bound investigation; do not infer absence or edition equality.
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

The code-owned complete-row hashes require source re-review if publisher metadata, byline, locators, notes, or paraphrase changes. The tests intentionally attack fabricated publisher titles and synopsis content, path leakage, hidden fields, duplicate prior OPF IDs and forbidden private/coverage promotions. These are **internal consistency** tests, not reproducible live publisher HTML-byte attestation.

**Next frontier:** independently recheck uncertain `0077`/`0078`/`0080` eBook format and ISBN variants against first-party publisher product listings; then proceed through later nonduplicate checksum-valid OPF entries. The Consolidator owns any later accepted evidence reconciliation and deterministic Explorer publication.
