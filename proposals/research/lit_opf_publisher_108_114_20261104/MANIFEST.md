# HELD owner OPF / publisher edition leads 0108–0114 — 2026-11-04

**Status: PROPOSAL — HELD source-local metadata.** No accepted Work, Source binding, close-read, semantic analysis, coverage, public Explorer, artwork release, or copyrighted text transfer.

## Source custody

- Accepted `main` baseline: `3028765359001b90bc3e6b5c1835ee283b326e91`. This packet is stacked locally on previous HELD proposal commit `7925418` and earlier proposals; draft PRs are **not** accepted main.
- Owner OPF-only inventory: `proposals/librarian/private-opf-metadata-20261103/observations.json`, SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`, 347 distinct source-local metadata rows. This is **not** a full-text source read or proof of ebook rights or edition.
- Independently opened seven distinct official Simon & Schuster US **eBook product pages**, November 4, 2026. All publisher evidence has one upstream family (`publisher:simonandschuster.com`); website content was not snapshotted or hash-pinned. Per-entry OPF XML SHA-256 is pinned in the records and validator. ISBN checksum calculations establish validity only, not local-file edition identity.
- Each `held_synopsis` is a new brief paraphrase of public publisher description, not copyright text from the ebook; no proprietary source passages, covers, book prose, images, or private ebook paths were transferred.

## Publisher evidence versus owner OPF claims

| Owner OPF ID | Independently read official publisher eBook edition | Identity uncertainty preserved |
| --- | --- | --- |
| `0108` | [Maximum Warp: Book Two](https://www.simonandschuster.com/books/Maximum-Warp-Book-Two/Dave-Galanter/Star-Trek-The-Next-Generation/9780743419536), Dave Galanter / Greg Brodeur, `9780743419536`, July 8, 2001, 240 pp. | Owner says `TNG - 63`, creator in combined string and no ISBN; US eBook page does not attest #63. Keep ordinal as local, **unverified title/creator link**. |
| `0109` | [A Hard Rain](https://www.simonandschuster.com/books/A-Hard-Rain/Dean-Wesley-Smith/Star-Trek-The-Next-Generation/9780743419277), Dean Wesley Smith, `9780743419277`, March 12, 2002, 256 pp. | OPF valid `074341926X` converts to **`9780743419260`**, not publisher eBook `9780743419277`. Bibliographic secondary discovery suggests paperback identifier, but does not prove the private file's format or manufacture. **Unbound valid ISBN, suspected edition-format difference; do not reconcile.** |
| `0110` | [A Star Trek: The Next Generation: Time #9: A Time for War, A Time for Peace](https://www.simonandschuster.com/books/A-Star-Trek-The-Next-Generation-Time-9-A-Time-for-War-A-Time-for-Peace/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation/9780743499972), Keith R. A. DeCandido, `9780743499972`, Oct. 1, 2004, 384 pp. | OPF lacks ISBN, abbreviates the publisher series title and spaces author initials differently. **Unverified title/creator**. Do not confuse a later trade-paperback ISBN with this eBook. |
| `0111` | [A Star Trek: The Next Generation: Time #1: A Time to Be Born](https://www.simonandschuster.com/books/A-Star-Trek-The-Next-Generation-Time-1-A-Time-to-Be-Born/John-Vornholt/Star-Trek-The-Next-Generation/9780743491495), John Vornholt, `9780743491495`, Feb. 1, 2004, 304 pp. | OPF only concatenated `ATimetoBeBorn`, no creator/ISBN. **Title-only** discovery, no authenticated edition binding. |
| `0112` | [A Star Trek: The Next Generation: Time #2: A Time to Die](https://www.simonandschuster.com/books/A-Star-Trek-The-Next-Generation-Time-2-A-Time-to-Die/John-Vornholt/Star-Trek-The-Next-Generation/9780743499446), John Vornholt, `9780743499446`, March 2, 2004, 320 pp. | OPF title only, no creator/ISBN. **Title-only** discovery, no authenticated edition binding. |
| `0113` | [Time #4: A Time to Harvest](https://www.simonandschuster.com/books/Time-4-A-Time-to-Harvest/Kevin-Dilmore/Star-Trek-The-Next-Generation/9780743488952), Kevin Dilmore / Dayton Ward, `9780743488952`, May 1, 2004, 352 pp. | Owner creator string says `Dayton Ward & Kevin Dilmore`, order opposite to publisher's credit; no ISBN. **Unverified title/creator**; no source-author correction. |
| `0114` | [A Time to Hate](https://www.simonandschuster.com/books/A-Time-to-Hate/Robert-Greenberger/Star-Trek-The-Next-Generation/9780743462907), Robert Greenberger, `9780743462907`, July 1, 2004, 304 pp. | Title and creator match, owner has no ISBN. **Unverified title/creator**, no authenticated format identity. |

## Deterministic checks and continuation

- Tranche: **7** owner source-local OPF observations; ISBN checksum-aligned to selected publisher ebook **0**; valid owner ISBN10 converting to different publisher ebook ISBN13 **1**; owner ISBN absent **6**.
- Contiguous cumulative local HELD owner OPF IDs `0055–0114`: **60**, distinct from unrelated separately HELD publisher-edition preview cards. This does **not** mean 60 Works, books read, verified manifestations, catalogue literary cards, or Source/Work coverage.
- `validate.py` rejects owner source hash changes, source-local XML entry changes, ISBN change/relabeling, reversed author-order normalization, owner identity backfill, wrong publisher ISBN/date/extent, URL spoofing, altered original paraphrases, added private content and acceptance claims. Regression tests assert nonoverlap against 53 prior source-local rows, six owner ISBN omissions, a divergent valid OPF ISBN, and no protected effects.
- Next frontier: `opf-local:0115` onward, under a new HELD proposal; resolve the `A Hard Rain` format question only with independently authenticated source/edition evidence, not filenames, owner checksum, or bibliographic guesses.
