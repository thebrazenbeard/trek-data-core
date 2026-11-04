# *A Time to Kill* — held literary custody cross-packet audit

**Role:** LIT independent public-receipt audit. **Status:** DRAFT proposal only. **Accepted main baseline inspected:** `3028765359001b90bc3e6b5c1835ee283b326e91` (2026-11-04). **Research effects:** NONE.

## Materials actually inspected in this wave

- Accepted-main `proposals/research/lit-time-to-kill-original-lit-20261103/RECEIPT.json` and its validator: SHA-256 `0207a7288851890dee074f9c44f60331ce7981c5f7ddeed9e891df4a4251e444`.
- Accepted-main `proposals/research/lit-time-to-kill-structure-20261103/CHAPTER_INDEX.json` and its validator: SHA-256 `a568ac8e3b7bd439b0939d3177b683f6b182a7189ceebd913646d2fbee6917c7`.
- Their explanatory manifests and open [literary close-read hold #23](https://github.com/thebrazenbeard/trek-data-core/issues/23).

This pass **did not open** the owner-held original ZIP, `.lit` bytes, private converted ZIP, OPF, HTML body, or book text. It did not independently compute a private source hash. The private-custody readings in the earlier packets are **prior-worker observations**, not my independent source-probe evidence.

## Deterministic public reconciliation

The packet audit checks both packets' own validators and strict hash-pinned public bytes, then joins three derivative fingerprints: ZIP container, OPF member, and HTML spine. Their candidate title/creator fields agree (*A Time to Kill*; David Mack), and both proposals retain `accepted_source_binding_effect=NONE`, `accepted_work_effect=NONE`, `coverage_effect=NONE`. The converted observation has **69 structural chapter locators**; this is not an authenticated publisher chapter count, whole-book completeness check, source binding, or close read.

> **Hostile challenge:** Agreement of public receipts can be circular. These packets report the same converted artifact lineage. A matching filename stem and matching three hashes cannot establish that the unread original LIT and the converted derivative contain equivalent text, that any omitted pages did not exist, or that the bytes match the advertised edition. The validators detect public drift and false status promotion, not private authenticity. This is **not independent corroboration**.

**Remaining gates:** issue #23's Librarian source↔Work binding and coverage/schema admissions, a lawful private decoding/reading of original LIT, original-versus-conversion textual equivalence including front/back-matter boundaries, edition completeness, then a source-first neutral close read. The separate publisher ISBN13 is bibliographic support only.

Run `python3 proposals/research/lit-time-to-kill-custody-audit-20261104/audit.py`, `python3 -m unittest discover -s proposals/research/lit-time-to-kill-custody-audit-20261104 -p test_audit.py -v`, and `python3 tools/validate.py`. No licensed content, path to user-owned files, or chapter prose is published.
