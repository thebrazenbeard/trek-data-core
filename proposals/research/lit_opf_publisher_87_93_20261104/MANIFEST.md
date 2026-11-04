# HELD literary OPF / publisher metadata 0087–0093 — 2026-11-04

Status: **HELD proposal, not accepted source/Work/evidence, not a close-read or Explorer display change**.

## Method and custody

- Baseline accepted `main`: `3028765359001b90bc3e6b5c1835ee283b326e91` (the wave's independently checked GitHub remote baseline).
- Owner-controlled **OPF XML metadata inventory only**: `proposals/librarian/private-opf-metadata-20261103/observations.json`; SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`. That inventory has 347 parsed local observations, not 347 accepted literary Works. The seven exact `opf_entry_sha256` values are in `records.json`.
- Product metadata and short marketing descriptions: independently opened **seven first-party publisher product URLs** on 2026-11-04, all with upstream family `publisher:simonandschuster.com` (one publisher family, not seven independent corroborations). No publisher HTML snapshot/byte SHA is asserted. The publisher's descriptions were **not** copied; short record synopsis sentences are original metadata-relative paraphrases, not ebook content-derived summaries.
- No source ebook text or local private file path was inspected or moved into this packet. OPF local metadata does not prove manifestation identity, rights to copy a book, full-text access, or a close read.
- All publisher ISBNs represent particular **publisher ebook** editions; matching a valid local ISBN10 checksum and transformed ISBN13 does not prove the owner-controlled local file is that manifestation. Nonmatching title/ISBN is explicit unresolved evidence, not a reason to silently reconcile titles.

## Publisher product pages and disposition

| Owner-local ID | Publisher title; source | OPF ISBN check | Disposition |
| --- | --- | --- | --- |
| `0087` | [Rogue Saucer](https://www.simonandschuster.com/books/Rogue-Saucer/John-Vornholt/Star-Trek-The-Next-Generation/9780743421164), John Vornholt; 288 pp, 2000-09-22 | `0743421167` → `9780743421164` | HELD checksum-aligned only |
| `0088` | [Possession](https://www.simonandschuster.com/books/Possession/J-M-Dillard/Star-Trek-The-Next-Generation/9780743421171), J.M. Dillard / Kathleen O'malley; 288 pp, 2000-09-22 | `0743421175` → `9780743421171` | HELD checksum-aligned only |
| `0089` | [Infiltrator](https://www.simonandschuster.com/books/Infiltrator/W-R-Thompson/Star-Trek-The-Next-Generation/9780743421201), W.R. Thompson; 288 pp, 2000-09-22 | Local OPF has neither ISBN nor creator | HELD title-only; identity unresolved |
| `0090` | [A Fury Scorned](https://www.simonandschuster.com/books/Star-Trek-The-Next-Generation-A-Fury-Scorned/Pamela-Sargent/Star-Trek-The-Next-Generation/9780743421218), Pamela Sargent / George Zebrowski; 288 pp, 2000-09-22 | `0743421213` → `9780743421218` | HELD checksum-aligned only; distinguished from 2011 trade paperback ISBN `9781451641691` |
| `0091` | [The Death of Princes](https://www.simonandschuster.com/books/The-Death-of-Princes/John-Peel/Star-Trek-The-Next-Generation/9780743422888), John Peel; 304 pp, 2000-09-22 | `0743421221` → `9780743421225`, **does not match** `9780743422888` | **CONFLICT**: [Balance of Power](https://www.simonandschuster.com/books/Balance-of-Power/Dafydd-ab-Hugh/Star-Trek-The-Next-Generation/9780743421225) by Dafydd ab Hugh carries `9780743421225`; earlier HELD OPF `0081` was only title-based; no identity assignment or duplicate edition addition |
| `0092` | [Intellivore](https://www.simonandschuster.com/books/Intellivore/Diane-Duane/Star-Trek-The-Next-Generation/9780743421249), Diane Duane; 272 pp, 2000-09-22 | `0743421248` → `9780743421249` | HELD checksum-aligned only |
| `0093` | [To Storm Heaven](https://www.simonandschuster.com/books/To-Storm-Heaven/Esther-Friesner/Star-Trek-The-Next-Generation/9780743421256), Esther Friesner; 240 pp, 2000-09-22 | Local OPF has neither ISBN nor creator | HELD title-only; identity unresolved |

## Non-additive count discipline

- 7 source-local OPF IDs newly reviewed in this HELD packet; 4 owner ISBN/publisher edition checksum alignments, 2 title-only identity holds, 1 ISBN/title conflict.
- Cumulative nonoverlapping owner OPF HELD source-local **lead** packets in this local branch: **39** (`0055–0093` inclusive). The ten separate earlier Consolidator publisher-draft rows are **not added** to that source-local count.
- 39 is **not** 39 admitted Works, full-text holdings, source-bound Works, close reads, or canonical titles. Both publisher metadata and owner inventory remain proposal evidence until independent admission and reconciliation procedures.
- Public Explorer, Pages allowlist, accepted index, image rights, existing Work inventory, and all coverage denominators: **unchanged**.

## Falsifiers and continuation

`validate.py` verifies the owner OPF file's complete SHA, each row's exact ID/entry hash/title/creator/ISBN and validity, first-party URL/ISBN/title/author/date/extent, exact typed anomaly and synopsis hash, and forbids private bytes, authority fields, coverage promotion, or crosswalk laundering. A separate hostile test explicitly falsifies an attempt to treat `0091` as an ISBN match, and confirms collision with previously held `Balance of Power`.

Next reviewer: independently inspect the source-local `0091` ebook metadata at the owner-controlled machine, with owner permission and without public text transfer, to determine whether its title or ISBN claim is wrong. Until then retain the contradiction. Next metadata batch starts at `opf-local:0094` and should not count these metadata rows as admitted works.
