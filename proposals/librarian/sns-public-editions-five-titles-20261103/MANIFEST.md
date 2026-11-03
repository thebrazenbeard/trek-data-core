# Seven further public Simon & Schuster ISBN editions — five titles

**Role:** LIBRARIAN. **State:** source-local proposal, not accepted research.

**Accepted baseline inspected:** `main@37d6863da94b8ccfa64af81dbe7ed179272241bc` on 2026-11-03 UTC.
**Batch:** `SNS.PUBLIC.EDITIONS.FIVE.TITLES.20261103.001`.

**Exact records.json SHA-256:** `8ee8bbefbedf67fb93d0f7027a5f27d9a8455c93a88330f57e768690b087a09f` (hash of this proposed metadata packet, **not** an HTML-source hash).

## Direct publisher observations

Seven distinct public **ISBN-specific Simon & Schuster product detail pages** were read on 2026-11-03 UTC. The rendered publisher pages explicitly displayed each title, author, format, imprint, date, page count and ISBN13. The edition identity is the **publisher's public product page and ISBN**, not a claim about a privately owned copy or the contents of an ebook.

| Public title | ISBN-13 | Format | Imprint | Publisher date | Pages |
| --- | --- | --- | --- | --- | ---: |
| [*Identity Theft*](https://www.simonandschuster.com/books/Identity-Theft/Greg-Cox/Star-Trek-The-Original-Series/9781668096642), Greg Cox | `9781668096642` | eBook | Pocket Books/Star Trek | 2025-12-02 | 352 |
| [*Identity Theft*](https://www.simonandschuster.com/books/Identity-Theft/Greg-Cox/Star-Trek-The-Original-Series/9781668096628), Greg Cox | `9781668096628` | Trade paperback | Pocket Books/Star Trek | 2025-12-02 | 352 |
| [*Lost to Eternity*](https://www.simonandschuster.com/books/Lost-to-Eternity/Greg-Cox/Star-Trek-The-Original-Series/9781668050057), Greg Cox | `9781668050057` | Trade paperback | Pocket Books/Star Trek | 2024-07-23 | 400 |
| [*Lost to Eternity*](https://www.simonandschuster.com/books/Lost-to-Eternity/Greg-Cox/Star-Trek-The-Original-Series/9781668050064), Greg Cox | `9781668050064` | eBook | **Gallery Books** | 2024-07-23 | 400 |
| [*Collateral Damage*](https://www.simonandschuster.com/books/Collateral-Damage/David-Mack/Star-Trek-The-Next-Generation/9781982113599), David Mack | `9781982113599` | eBook | Pocket Books/Star Trek | 2019-10-08 | 384 |
| [*Star Trek: Picard: Rogue Elements*](https://www.simonandschuster.com/books/Star-Trek-Picard-Rogue-Elements/John-Jackson-Miller/Star-Trek-Picard/9781982175214), John Jackson Miller | `9781982175214` | eBook | Pocket Books/Star Trek | 2021-08-17 | 416 |
| [*The Captain's Oath*](https://www.simonandschuster.com/books/The-Captains-Oath/Christopher-L-Bennett/Star-Trek-The-Original-Series/9781982113308), Christopher L. Bennett | `9781982113308` | eBook | Pocket Books/Star Trek | 2019-05-28 | 400 |

**Source scope:** For each record, the publisher's `Product Details > ISBN13` section and adjacent product title/format were actually read. Seven pages share **one** `publisher:simonandschuster.com` lineage; this is not seven independent corroborating institutions. No unaltered HTTP HTML response was saved and `source_raw_sha256` is `null`. Page dates and counts can change; the exact URL and separately pinned values make later rechecks possible, but are not immutable source-content hashes.

## Duplicate/identity boundary

The seven exact ISBNs were absent from accepted repository source/edition proposals and Explorer indexes at the pinned baseline (`rg` over `proposals`, `explorer`, `registry`), and from pending literary draft PRs #212, #216, #222 and #330. This bounded duplicate search does **not** imply these are seven new Works, or even five newly discovered fictional Works. Other ISBN editions and title-level leads for *Rogue Elements* and *The Captain's Oath* already exist elsewhere in accepted source-relative records, and remain separate. The two formats under each of *Identity Theft* and *Lost to Eternity* have no asserted text-equivalence or global Work merge. Crucially, the publisher assigns **Gallery Books** to the *Lost to Eternity* eBook while assigning **Pocket Books/Star Trek** to its trade paperback; the two must not be normalized into one imprint.

## Rights, privacy and effects

Only independently retrieved **public publisher product metadata** is used. No owner-private OPF/ebook/ZIP metadata, private filename/path/ISBN linkage, downloaded book, book text, synopsis, cover, image locator, author photo, raw web page or audio was included. Even when the public page offers a cover download, a publisher URL does **not** establish image-display permission.

Every row is `PROPOSED_METADATA_ONLY`. Source admission, Work admission, Source↔Work identity, `FULL_TEXT_AVAILABLE`, `CLOSE_READ`, semantic analysis, coverage and public artwork effects are **NONE**. This proposal does not change the Explorer or any canonical registry.

## Local checks and next frontier

```bash
python3 -O -B proposals/librarian/sns-public-editions-five-titles-20261103/validate.py
python3 -B -m unittest discover -s proposals/librarian/sns-public-editions-five-titles-20261103 -p 'test_validate.py' -v
python3 tools/validate.py
```

The validator pins exact ISBN/title/creator/series/format/imprint/date/pages/URL associations and rejects duplicate JSON keys, swapped edition URLs, fake source-byte or private-data claims, unsupported extra fields and admission/coverage promotions, including with Python `-O`. It does not perform future network retrieval, edition-text comparison or independent licensing review. Next: independently audit these seven product-page locators and decide which bounded source records may be admitted under current governance.
