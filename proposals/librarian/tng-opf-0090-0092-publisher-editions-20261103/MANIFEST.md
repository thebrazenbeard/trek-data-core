# Librarian proposal: TNG OPF 0090–0092 publisher-edition crosscheck

**Status:** PROPOSED / metadata only / `2026-11-03`. Not admitted corpus data.

## Input lineage and method

- **Upstream owner-private OPF observation:** accepted `proposals/librarian/private-opf-metadata-20261103/observations.json`, SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`. This sanitised snapshot already existed; this wave did **not** retrieve, open, or read any private EPUB/ZIP/book text.
- **Publisher lineage:** Simon & Schuster / Pocket Books Star Trek. All three public listings are from **one corporate source family**, so no claim of independent corroboration. Human-readable product pages were inspected via web retrieval on `2026-11-03`. We did not capture raw HTML bytes and therefore do not assert an HTML SHA-256 digest or immutable publisher-page custody.
- **Collection:** OPF-local IDs `0090`, `0091`, `0092` were newly checked against edition-specific first-party pages. Source-local OPF hashes and ISBN10 checksums are pinned in `records.json`. We did **not** resolve global Work identity, book contents, copyright permission, cover rights, or any study/semantic coverage.
- **Research outputs:** Three source-local rows, two matching publisher eBook ISBN metadata records, one **explicit edition-identifier conflict**, and three separately held short original publisher-description paraphrases (candidates, *not* book close reads).

## Actual product-page evidence

| OPF ID | Publisher observation | Edition result |
|---|---|---|
| `0090` | [*Star Trek: The Next Generation: A Fury Scorned*, eBook, Sargent/Zebrowski](https://www.simonandschuster.com/books/Star-Trek-The-Next-Generation-A-Fury-Scorned/Pamela-Sargent/Star-Trek-The-Next-Generation/9780743421218) — #43; page lines 216–266; 2000-09-22, 288 pages, ISBN13 `9780743421218` | OPF ISBN10 `0743421213` → ISBN13 `9780743421218`; **same identifier**, but no private edition/text equivalence verified. The default publisher paperback page ISBN `9781451641691` is a *different 2011 format*; follow the explicit eBook option. |
| `0091` | [*The Death of Princes*, eBook, John Peel](https://www.simonandschuster.com/books/The-Death-of-Princes/John-Peel/Star-Trek-The-Next-Generation/9780743422888) — #44; page lines 79–121; 2000-09-22, 304 pages, ISBN13 `9780743422888` | **Unresolved edition mismatch**: OPF ISBN10 `0743421221` → `9780743421225`, **not** the publisher listing `9780743422888`. Shared title and author do not fix edition identity. |
| `0092` | [*Intellivore*, eBook, Diane Duane](https://www.simonandschuster.com/books/Intellivore/Diane-Duane/Star-Trek-The-Next-Generation/9780743421249) — #45; publisher description/product details; 2000-09-22, 272 pages, ISBN13 `9780743421249` | OPF ISBN10 `0743421248` → ISBN13 `9780743421249`; **same identifier**, no private edition/text equivalence verified. |

**Source/edition distinction:** The OPF-local records carry `2000-08-05` for 0090–0091 and `2000-07-31` for 0092. The publisher pages carry a product publication date of `2000-09-22` for each. These dates are kept separately and do **not** establish a historical chronology of private file acquisition or text release.

**Art:** The official publisher pages expose cover-image links, but no image files were downloaded, redistributed, licensed, or assigned use rights in this tranche. Those links are discovery leads only, with source and format context preserved at the page URL.

**Rights/publication:** No source text, ebook, cover byte, proprietary page body, or derived large passage is published here. Three short summaries are **original, publisher-overview-based, HELD**, and have not been validated against book text. No public Explorer or accepted projection change is authorized by this Librarian packet.

## Validation and handoff

Run from repo root:

```bash
python proposals/librarian/tng-opf-0090-0092-publisher-editions-20261103/validate.py
python -m unittest discover -s proposals/librarian/tng-opf-0090-0092-publisher-editions-20261103 -p 'test_validate.py' -v
python -O -m unittest discover -s proposals/librarian/tng-opf-0090-0092-publisher-editions-20261103 -p 'test_validate.py' -v
```

The validator fails closed on duplicate JSON keys; changed upstream source bytes/OPF hashes; wrong checksum, title, publisher URLs, dates; silent conflation of OPF and public product ISBN; private-content/cover/equivalence claims; and global Work or coverage admission. It also checks for conflicting OPF source-local IDs in five earlier accepted publisher crosscheck packets.

**Next unresolved Librarian frontier:** `opf-local:0089` has only a title and no creator/ISBN in the sanitized OPF observations, so requires new source-binding evidence before publisher-edition confidence; `opf-local:0091` needs a verifiable edition-specific identifier `9780743421225` or explicit explanation of the two ISBNs from a primary catalog. Then select later uncovered OPF IDs after refreshing accepted main and all pending PRs; no fabricated batch coverage.
