# Librarian OPF0089 title lead and OPF0091 cross-title ISBN collision

**Status: PROPOSED / HELD / source-local only**, research date 2026-11-03. Based accepted `main@806c4502af8eb5306137c13eaacea54f8cd469ba`. Read `RESEARCH_LOG.md` for frozen questions, retrieval channels, page evidence, failed URL probe and falsifiers.

## Material discovery

1. **OPF0089** is a filename-like title-only record, without creator/ISBN. A first-party Simon & Schuster [*Infiltrator* eBook listing](https://www.simonandschuster.com/books/Infiltrator/W-R-Thompson/Star-Trek-The-Next-Generation/9780743421201) supplies W.R. Thompson, TNG #42, and ISBN13 `9780743421201`. **This is a title candidate only:** no edition identifier exists in OPF0089 to bind the owner's private source. The single original publisher-overview-based synopsis candidate is HELD.
2. **OPF0091** calls itself *The Death of Princes* by John Peel with ISBN10 `0743421221`. That ISBN correctly converts to `9780743421225`, which a first-party Simon & Schuster [*Balance of Power* eBook listing](https://www.simonandschuster.com/books/Balance-of-Power/Dafydd-ab-Hugh/Star-Trek-The-Next-Generation/9780743421225) attributes to **Dafydd ab Hugh's different TNG #33 book**. Simon & Schuster separately lists [*The Death of Princes*](https://www.simonandschuster.com/books/The-Death-of-Princes/John-Peel/Star-Trek-The-Next-Generation/9780743422888) as TNG #44 under ISBN13 `9780743422888`.

**Provenance interpretation:** The OPF0091 metadata fields are in cross-title conflict according to the publisher's current public ISBN mapping. This is stronger than an unexplained edition-number mismatch. It does **not** establish whether the private ebook contains *The Death of Princes*, *Balance of Power*, or something else; no source text was read. A dishonest "repair" that changes the owner-private OPF title or author to *Balance of Power* based on ISBN alone is invalid.

## Scope and reproducibility

- `records.json` holds **three distinct publisher-source-local observations**, not three admitted Works or duplicate global OPF records. OPF0089 is referenced once, OPF0091 twice for the two conflicting first-party product pages. The earlier accepted OPF0091 crosscheck remains unchanged; its exact bytes are SHA-pinned here.
- The accepted sanitized OPF observations are SHA-256 pinned to `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`, with individual OPF entry hashes and immutable publisher row digests. Earlier accepted publisher crosscheck bytes are pinned to `ac67d958c0c75aee0fe3979bba8cd145972cfaca40aca920748ceec55b892964`.
- All product pages belong to a **single Simon & Schuster corporate lineage**. Retrieved/rendered page lines, not captured raw HTML, are the public publisher evidence. No source-page SHA-256 asserted. No audiobook, chapter/ebook text, cover image bytes, rights permission, private path, global identity, plot verification, public synopsis or coverage effect appears here.

Run from repository root:

```bash
python proposals/librarian/opf-0089-0091-firstparty-gap-20261103/validate.py
python -m unittest discover -s proposals/librarian/opf-0089-0091-firstparty-gap-20261103 -p test_validate.py -q
python -O -m unittest discover -s proposals/librarian/opf-0089-0091-firstparty-gap-20261103 -p test_validate.py -q
python -m unittest discover -s tests -p 'test_*.py' -q
```

The validator rejects changes to the prior accepted mismatch, source hashes, ISBN conversion, title/author assignments, URLs, duplicate source-local observations, covert private paths, and scope/rights/coverage/synopsis escalation. A future accepted correction must **append/supersede** these observations rather than silently edit history.

## Next frontier

Source custodian should inspect the actual full private package for OPF0089 and OPF0091 under authorized host custody, comparing title page, author, edition identifiers, and content fingerprint to the publisher's conflicting metadata. No publicity or Work identity follows automatically. After that, refresh accepted main and index only genuinely uncovered next OPF IDs.
