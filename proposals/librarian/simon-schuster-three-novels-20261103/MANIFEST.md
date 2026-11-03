# Three novels, nine ISBN manifestations — publisher metadata tranche

**Role:** LIBRARIAN. **Baseline:** accepted `main@d4ecd970bf28019696abd692011007d7d47f9ff8`.
**Observed:** 2026-11-03 UTC. **Admitted effects:** NONE.

This metadata-only proposal identifies three plausible narrative Works and nine distinct publisher ISBN manifestations (paperback, eBook, and unabridged audio each). It **does not** represent nine distinct books, completed literary readings, accepted Work/Source bindings, or new literary coverage. Source-based grouping by title, author, publisher series, and linked formats is a **proposed identity hypothesis**, not a canonical Work reconciliation.

| Proposed Work | Trade paperback | eBook | Unabridged audio |
| --- | --- | --- | --- |
| *Star Trek: Picard: Second Self* (Una McCormack) | [9781982194833](https://www.simonandschuster.com/books/Star-Trek-Picard-Second-Self/Una-McCormack/Star-Trek-Picard/9781982194833) | [9781982194840](https://www.simonandschuster.com/books/Star-Trek-Picard-Second-Self/Una-McCormack/Star-Trek-Picard/9781982194840) | [9781797137278](https://www.simonandschuster.com/books/Star-Trek-Picard-Second-Self/Una-McCormack/Star-Trek-Picard/9781797137278) |
| *Star Trek: Strange New Worlds: The High Country* (John Jackson Miller) | [9781668002391](https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-The-High-Country/John-Jackson-Miller/Star-Trek-Strange-New-Worlds/9781668002391) | [9781668002407](https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-The-High-Country/John-Jackson-Miller/Star-Trek-Strange-New-Worlds/9781668002407) | [9781797149226](https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-The-High-Country/John-Jackson-Miller/Star-Trek-Strange-New-Worlds/9781797149226) |
| *Star Trek: Discovery: The Enterprise War* (John Jackson Miller) | [9781982113315](https://www.simonandschuster.com/books/Star-Trek-Discovery-The-Enterprise-War/John-Jackson-Miller/Star-Trek-Discovery/9781982113315) | [9781982113322](https://www.simonandschuster.com/books/Star-Trek-Discovery-The-Enterprise-War/John-Jackson-Miller/Star-Trek-Discovery/9781982113322) | [9781508283195](https://www.simonandschuster.com/books/Star-Trek-Discovery-The-Enterprise-War/John-Jackson-Miller/Star-Trek-Discovery/9781508283195) |

## Source processing and provenance

- The nine complete *rendered* official Simon & Schuster product-page views were opened through a public web reader during this tranche; the `Product Details` metadata for each ISBN was read, including publisher imprint, date, and page count or audio runtime. Pages are not complete novel text. A publisher description or free excerpt is not a close read.
- **Custody limitation:** the web reader supplied human-readable rendered pages but not an immutable raw HTTP response or a local byte stream. Accordingly every `raw_response_sha256` and `source_version` remains `null`; no page-byte hash, exact archived capture, HTTP status, or independent edition-text authentication is claimed. The URLs and publisher field locations are recheckable locators, not immutable receipts.
- All nine publisher pages are from the **same Simon & Schuster lineage** even when the imprint differs. Cross-format repetitions are not independent sources of literary fact.
- The publisher gives *The Enterprise War* the label “Book #5 of Star Trek: Discovery.” This is retained as publisher-series metadata, **not** a universal timeline ordering. Its audio product page also has a 304-page `Length` field alongside the 12h48 runtime, whereas the paperback and eBook each show 432 pages. No edition-text equivalence is inferred from those inconsistent extents.
- The 2026-11-02 Ring of Fire publisher-edition proposal and open literary memoir PR #212 were not modified or re-counted. None of these three titles overlaps their named Works.

## Unresolved and safety boundaries

- No full licensed text or complete audio was obtained or read; **FULL_TEXT_AVAILABLE**, **CLOSE_READ**, and **SEMANTICALLY_ANALYZED** remain unverified for all three candidates.
- No actual publisher page bytes, audiobook, ebook, cover art, image URL, promotional prose, or excerpt is committed. Publisher cover thumbnails visible on product pages **do not establish redistribution or hotlink permission**; maintain the existing artwork rights gate.
- Independent bibliographic corroboration, authorized physical/private edition custody, edition-content differences, exact ISBN→Source admission, Work reconciliation, and publisher permissions require additional review.
- User-owned private *ST Books* archives, if later provided through authorized host access, should be inventoried privately as **ZIP container → internal file/edition → possible Work** with byte hashes, exclusion of copyrighted content from this public repo, and explicit rights/access checks. Private archive filenames alone are not source reads or Work identity proof.

## Deterministic local validation

Run `python3 proposals/librarian/simon-schuster-three-novels-20261103/validate.py` from repo root. It checks ISBN-13 checksums, unique identifiers, link-to-ISBN consistency, proposed status, no admitted effects, exact three-format grouping, audio narrators, and absence of asserted raw-source hashes. These fail-closed checks use explicit exceptions rather than Python `assert`, so they still execute under `python3 -O`. Run `python3 -B -m unittest discover -s proposals/librarian/simon-schuster-three-novels-20261103 -p 'test_validate.py'` for optimized-mode tampering regressions. This **does not** validate the publisher's live pages, rights, full-text availability, or canonical narrative identity.
