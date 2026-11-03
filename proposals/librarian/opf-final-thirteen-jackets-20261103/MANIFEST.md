# Final thirteen checksum-valid OPF metadata ISBNs — five held public jacket leads

**ROLE LIBRARIAN · SOURCE-ONLY DRAFT · NO RELEASE / NO WORK ADMISSION.** Snapshot baseline accepted `main@a3b30aa686a3fadd7ec0ea572cdcf483730a2c41`; observed 2026-11-03 UTC. Inputs are accepted sanitized owner-private OPF metadata (no private member filenames, source texts or archive body) and independently observed public Open Library / publisher edition pages.

## Why thirteen, not twenty or six hundred

The accepted private metadata ledger has **347 OPF entries, 75 with checksum-valid ISBN candidates**. After taking the union of explicit `opf-local:NNNN` source references in current earlier Librarian *proposal records* (including draft PR446), exactly **thirteen** checksum-valid IDs remained without a proposal crosswalk. This batch covers those thirteen, not an arbitrary invented next twenty. Earlier proposals are not yet all accepted and this calculation is **proposal-queue coverage only**, not accepted source/Work coverage or full-text processing. The separate 347 LIT and 220 TXT file entries overlap unknown amounts; none of these are additive distinct novel counts.

These thirteen have **13 different OPF entry SHA256s, 13 different valid ISBN-10s and their deterministically converted ISBN-13s**; their title/creator identity and original narrative content have not been independently reconciled. Five are namespace-recovered XML metadata (`opf-local:0282`–`0286`), eight ordinarily parsed metadata. The original private book narratives were not opened.

## Open Library snapshot and visual candidate crosswalk

Thirteen exact `/isbn/{isbn13}.json` probes produced **11 HTTP 200** responses and **two HTTP 404**. Five of eleven 200 returned a `covers` ID. The other **six** had no cover field. Those are only observed endpoint states, not proof a book or jacket does not exist.

Five public Open Library `-M.jpg?default=false` endpoints returned HTTP 200 `image/jpeg`; each byte count and raw SHA256 is pinned in `records.json`. Five jackets were actually visually inspected by the Librarian, including their visible titles. **Zero JPEG bytes are committed.**

| OPF metadata source | Public visual jacket / cover ID | First-party publisher ISBN source | Eligibility |
| --- | --- | --- | --- |
| `opf-local:0238`, *The Aliens Are Coming!* | OL `10827006` | [Simon & Schuster eBook exact ISBN 9780743464543](https://www.simonandschuster.com/books/The-Aliens-Are-Coming%21/Dayton-Ward/9780743464543) | HELD |
| `opf-local:0284`, *Bloodletter* | OL `13904465` | [Simon & Schuster eBook exact ISBN 9780743412223](https://www.simonandschuster.com/books/Bloodletter/K-W-Jeter/Star-Trek-Deep-Space-Nine/9780743412223) | HELD |
| `opf-local:0306`, *Star Trek: Deep Space Nine Companion* | OL `405687` | No exact-ISBN first-party product page established. The publisher has [an author biography mentioning this nonfiction work](https://www.simonandschuster.com/authors/Terry-J-Erdmann/1804419), which does not bind ISBN `9780671501068`. | **EDITION SOURCE HOLD** |
| `opf-local:0323`, *Enterprise: By the Book* | OL `10701689` | [Simon & Schuster eBook exact ISBN 9780743448727](https://www.simonandschuster.biz/books/By-the-Book/Dean-Wesley-Smith/Star-Trek-Enterprise/9780743448727) | HELD |
| `opf-local:0346`, *Gauntlet* | OL `476607` | [Publisher eBook ISBN 9780743427951](https://www.simonandschuster.com/books/Stargazer-Book-One/Michael-Jan-Friedman/Star-Trek-The-Next-Generation/9780743427951) is **NOT** the OPF lookup ISBN `9780743427920`. Same-title visual lead, edition unresolved. | **EDITION MISMATCH HOLD** |

The *Deep Space Nine Companion* image visibly carries the full companion title, but the Open Library edition JSON gives its title only as **Star Trek Deep Space Nine**, and lists ISBN10 `0671501062` without an `isbn_13` field. *Gauntlet* JSON likewise lists ISBN10 only. The converted ISBN13 lookup responding with an edition does not independently insert an ISBN13 into the returned crowdsourced record. The publisher's first-party *Stargazer Book One: Gauntlet* page is the same work-family lead but a **different ISBN**. No inference should silently resolve those manifestation discrepancies.

## Defensible claim boundary

Four distinct proof layers remain separate:

1. A private **OPF metadata** entry contains a checksum-valid ISBN and a cryptographic OPF-entry hash. No story text was read.
2. A mutable public **Open Library edition JSON** response associates a particular ISBN lookup to an edition key and, in five cases, a cover ID. Response body hashes are snapshot receipts, not chain-of-custody guarantees.
3. A fetched public medium **JPEG** visibly looks like a book jacket and has raw byte/hash receipt. This is not proof the publisher used that image on the exact owner-private ebook manifestation.
4. **Official publisher metadata** matches the same ISBN on three product pages; one matches the title but not ISBN and one only mentions the work on an author bio page. Copyright/image display rights are **NOT** automatically granted by any preceding layer.

> Hostile challenge: A title-bearing cover labeled *Deep Space Nine Companion* combined with an underspecified Open Library title and no exact public publisher ISBN evidence must not be promoted to an exact edition association, however plausible the image appears.

> Hostile challenge: Finishing a checksum-valid OPF *proposal queue* has no causal implication that 347 private ebooks, 567 LIT/TXT entries, or hundreds of Star Trek Works have been read, deduplicated, indexed, or semantically analyzed. The next frontier is rights-aware source identity reconciliation and the 272 OPF entries **without** checksum-valid ISBN candidates, not a false completion percentage.

No public repository image binaries, ebooks, archives, textual excerpts, or private filenames. [Open Library Covers API](https://openlibrary.org/dev/docs/api/covers) documents image retrieval conditions; [Open Library licensing](https://openlibrary.org/developers/licensing) is not blanket copyright permission over publisher jacket art. A separate reviewer must verify exact source IDs / image bytes / edition mismatches, and any public Explorer visual integration requires independent approved eligibility and human authority.

### Reproduce local pinned checks

```sh
python3 proposals/librarian/opf-final-thirteen-jackets-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/opf-final-thirteen-jackets-20261103 -p test_validate.py -v
python3 -O -m unittest discover -s proposals/librarian/opf-final-thirteen-jackets-20261103 -p test_validate.py -v
```

**Current state: 13 private metadata IDs assessed, 5 visually inspected held jackets, 3 public first-party exact ISBN records, 1 publisher ISBN mismatch, 1 no exact publisher product page, 6 no-cover API responses, 2 API 404, 0 admitted Works, 0 Explorer images released.**
