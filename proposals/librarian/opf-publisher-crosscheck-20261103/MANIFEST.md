# Librarian proposal: nine owner-private OPF ↔ publisher metadata crosschecks

**Date:** 2026-11-03

**Status:** source-only research proposal, **not accepted Work/Edition binding**
**Input lineage:** previously accepted sanitized `private-opf-metadata-20261103/observations.json` (SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`). The source observations originated in an owner-private archive, but this PR contains neither archive member paths nor source text. See the original accepted batch's own scope and private-source custody disclaimers.

## Actual bounded processing

1. Selected nine checksum-valid ISBN-10 tokens from the 75 such candidates among 347 previously parsed OPF rows. The checksum merely validates digit structure, not the existence or edition identity of an ISBN.
2. Independently searched publisher-first records from Simon & Schuster's public catalog. Compared the catalog's *edition-level* ISBN-13, product title, lead author/creator, publication date (when exposed), and stated eBook format to the source-local OPF ISBN/title/creator. Each `records.json` row preserves the publisher URL and source-local OPF fingerprint.
3. Found **seven exact ISBN conversions present in first-party publisher eBook product metadata** (source-local `0010`, `0028`, `0029`, `0031`, `0034`, `0050`, `0051`); **two related publisher products have different ISBNs** (`0009`, `0015`), and those candidates stay held. Title capitalization, subseries and author-list variants are deliberately retained as source-specific metadata.
4. Wrote short original synopsis paraphrases only for the seven catalog matches. These describe the publisher-listed works; they have **not** been checked against private book bodies and cannot establish source-local full-text identity.

## Publisher-source access / custody

- One upstream publisher domain/source family: `www.simonandschuster.com` / `publisher:simonandschuster.com:pocket-books-star-trek`. Nine publisher URLs do **not** represent nine independent provenance families.
- Publisher details were inspected through public web search result renderings and publicly rendered publisher product pages (including `/Foundations-1/` and `/Foundations-2/`), not direct publisher HTTP byte custody. A raw direct request from Lappy returned HTTP 403. Accordingly, `publisher_raw_html_sha256` is **null** and no claim is made to a reproducible raw-page byte digest. The table below hashes **UTF-8 URL locator strings only**, **not webpage content**. These hashes are useful as citation-identity fingerprints, not source-content hashes.
- No private eBook text was read during this batch. No complete books, excerpts, cover art, or private filesystem paths are present. No accepted identity record, authoritative work graph, projection, or coverage denominator is modified.

| Source-local OPF | Publisher URL SHA-256 (locator only) | Result |
| --- | --- | --- |
| `0009` | `1a0d5fee57b079c770144be0f6ba19062362f1a0e311957546a95afd6d9d8c38` | HOLD; eBook ISBN differs |
| `0010` | `a2ced29e969555ffa2d0d232b1ceb953d36966c47482e6d3ab27464968779015` | catalog ISBN metadata match |
| `0015` | `7ade9e154cba600e4b208f0bcf8f6550650a985be2d3ed504beba93dfe9993ef` | HOLD; eBook ISBN differs |
| `0028` | `02981fa8b1a6ed1f235f2c726aeefe8cbd3e4e03896047a495d5fba5ff0c2d37` | catalog ISBN metadata match |
| `0029` | `8f4b2299101c4bec95bdf8e8abaa98f7626ed9f068cf162725c070406c3394d1` | catalog ISBN metadata match |
| `0031` | `2274fe320f43cf03c2b86e5ecbb6d2df9597280a8d909c07ac575ee20e1b6040` | catalog ISBN metadata match |
| `0034` | `6922a06c9f7a82197c3081568ce6501d9dbb5547b8eb88961b7234e84796f4af` | catalog ISBN metadata match |
| `0050` | `36f2de9bdc13ad38b0e18f25671c7608a722efd37903ddd18a4f7e5ac68ca94f` | catalog ISBN metadata match |
| `0051` | `8a8b258f4b8fa71d17ae7bd3bc78ca7a548a8850b96edd283a8afd6c1bf34eb0` | catalog ISBN metadata match |

Full publisher product URLs appear in `records.json`; all are first-party links, and reviewers should re-retrieve the live page before any admission. Page details may change between snapshots. A domain-level match or ISBN string is **not** an independent inspection of a privately converted ebook.

## Repeatable checks

From this directory, run `python3 validate.py`, `python3 -O validate.py`, `python3 -m unittest -v test_validate.py`, and `python3 -O -m unittest -v test_validate.py`.

**Hostile-review correction:** The original validator only anchored some individual source fields. An independent reviewer demonstrated four bypasses: an extra non-lead author containing a private path, invented canonical-claim wording in an otherwise bounded synopsis, a private path in the uncertainty paragraph, and an unknown `source_private_local_path` key. That exact proposed head was held.

The corrected validator adds a recursive private-path scan over all strings and map keys, exact envelope and record field sets, and a trusted code-owned SHA-256 of the **complete canonical JSON of each of the nine reviewed records**. Any change to an author list, paraphrase, uncertainty, source locator, status, or any other field now requires an explicit source review and new pin. All four hostile mutations and two additional schema/privacy probes must fail in normal and optimized Python. The checksum, ISBN conversion, and explicit no-admission checks remain.

These are internal mechanical consistency and review-snapshot checks, **not** independently reproducible publisher raw-byte retrieval and not an assertion that the publisher information is unchangeable.

## Next frontier

- Find a first-party exact **print** ISBN product page for `opf-local:0009` and `opf-local:0015`, or preserve HOLD. Do not swap nearby eBook ISBNs into the OPF row.
- Check more checksum-valid OPF leads in bounded tranches; mark absent/mismatched catalog evidence explicitly.
- Only a later separately authorized source-specific content/edition inspection can consider full private edition equivalence. Subsequent identity reconciliation and any published Explorer display require the Consolidator's accepted-decision pipeline.
