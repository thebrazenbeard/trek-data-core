# *Shadows of the Sun* — held Source/Work manifestation identity audit

**Role:** LIT. **State:** Proposal-only audit, not a source binding or close read. **Accepted baseline:** `main@3028765359001b90bc3e6b5c1835ee283b326e91` (2026-11-04). **Research effects:** NONE.

## Source inspection and exact distinction

I inspected accepted-main `proposals/research/lit-three-archive-discovered-publisher-editions-20261103/records.json` (SHA-256 `03173ed5ac94c7052a8c416bcca9cc762a8e7ca0ca3280eae0a4b3f902954dea`) and its validator. That batch reports title/creator-only leads from private OPF archive metadata, but does **not** establish edition identity with publisher products.

I also retrieved the [official Simon & Schuster *Shadows of the Sun* product page](https://www.simonandschuster.com/books/Shadows-of-the-Sun/Michael-Jan-Friedman/Star-Trek-The-Original-Series/9780743546744) on 2026-11-04. Its product metadata independently confirms **ISBN13 `9780743546744` is an abridged audio download**, narrated by **James Doohan**, released by **Simon & Schuster Audio** on **1993-08-01**, with a **three-hour** runtime. These are publisher-source bibliographic facts; the publisher website is the same upstream lineage as the older proposal, not a second independent witness. No publisher promotional prose, audio, or copyrighted cover was reproduced.

`AUDIT.json` records the bounded publisher-edition metadata and explicit non-admission fields. `audit.py` pins and validates the accepted-main public inventory, checks the specific candidate ISBN across packets, and rejects the dangerous ebook/audio identity substitution. Tests challenge false edition identity, inflated independent-source counts, invented close-read coverage, silently resolved source spelling, and extra copyrighted-text fields.

> **Hostile challenge:** A publisher-branded abridged audiobook can contain omissions, edits or narration choices absent from an ebook. A title/author match between a private OPF lead and an audio ISBN does **not** prove those are the same manifestation or that either contains the complete original text. The page's conflicting `Ssan` / `Susan` planet spelling is a copy anomaly; no new place entity should be inferred from it. This audit cannot establish that the private OPF lead is even a legitimate edition without examining private source bytes and edition identifiers.

**Remaining blockers:** issue #23 holds new book `CLOSE_READ`; the private OPF was not read this wave, no original ebook or audio content was inspected, and the Librarian has not accepted a Source↔Work↔edition binding. This is an **audited publisher audio-edition identity lead**, not `FULL_TEXT_AVAILABLE`, `STRUCTURALLY_INDEXED`, `CLOSE_READ`, or semantic coverage.

Run `python3 proposals/research/lit-shadows-audio-identity-audit-20261104/audit.py`, `python3 -m unittest discover -s proposals/research/lit-shadows-audio-identity-audit-20261104 -p test_audit.py -v`, and `python3 tools/validate.py`. No external effects are authorized by this packet.
