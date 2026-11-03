# Literary structural source proposal: *A Time to Kill*

**Role:** LIT research worker. **State:** DRAFT PROPOSAL ONLY. **Accepted baseline inspected:** `main@5127598af7e7c9a1148b11bb15863643f2914dfc` (2026-11-03 UTC).

This is an index of **one privately held converted ebook artifact**, not an admitted Work, a close reading, a verified complete book, or a copyright grant. The source's actual OPF member and converted HTML chapter body were opened and processed privately on Patrick's Lappy WSL2 host. Source bytes, local archive member paths, HTML, book excerpts and cover artwork remain outside Git.

## Edition-level source observations

| Channel | Observation | Evidence boundary |
| --- | --- | --- |
| Private converted OPF metadata | `A Time to Kill`; David Mack; Pocket Books; 2004; ISBN10 `0743494075` | Metadata in a **derivative** OPF package, not independently authenticated against original LIT bytes |
| Private converted OPF spine | Exactly one referenced `text/html` body present; 570,045 bytes; SHA-256 `f509150d56264056b6f1c2dc46361dd52d1a44faba82634af80a0f570078cb5f` | The body was parsed, but complete-edition authenticity has **not** been established |
| Private structural extraction | Title, author and ISBN appear in front matter; 69 sequential chapter headings (`Chapter 1`–`Chapter 69`); 2,225 normalized nonblank extracted lines | Source-relative structural observations only; no story propositions or global entity reconciliation |
| [Official publisher product page](https://www.simonandschuster.com/books/A-Star-Trek-The-Next-Generation-Time-7-A-Time-to-Kill/David-Mack/Star-Trek-The-Next-Generation/9780743494076) | Same Work title and author; eBook ISBN13 `9780743494076`; Pocket Books/Star Trek, 2004 | Bibliographic corroboration, **not** validation that the private HTML is unaltered, complete, or a particular publisher manifestation |

The ISBN10 is the valid counterpart of the publisher's ISBN13. The OPF and HTML belong to the same converted-archive lineage; they must not be counted as independent witnesses. Book text is copyrighted. Neither a private copy nor the publisher's cover link confers public redistribution rights.

## Chapter locator index

`CHAPTER_INDEX.json` records the **69 ordered chapter segments** using integer positions in a reproducible HTML-to-line normalization, per-segment normalized SHA-256 digests, and parser-specific whitespace token counts. It contains no fictional dialogue, scene facts, passages, private archive path or local filename.

Extraction method:

1. Parse a hash-verified OPF XML package; resolve its only spine `idref` through the OPF `manifest` inside the same archive; require that the referenced `text/html` member exists.
2. Decode that member as strict UTF-8. With Python's `HTMLParser(convert_charrefs=True)`, insert line separators at the start of `br`, `hr`, `p`, `div`, `h1`, `h2`, or `h3` elements; append text-node contents.
3. Split on line separators, normalize intra-line whitespace, discard blank lines. Detect lines that fully match `Chapter N` case-insensitively; require ordinals 1 through 69.
4. Treat each heading through the line before the next heading as a chapter segment (last segment through the end of the extracted text). SHA-256 hashes cover UTF-8 normalized lines joined by a single LF. Report line positions as zero-based within the **derived nonblank-line stream**, not raw HTML physical lines, pages, CFI coordinates, or native publisher positions.

The observed 71,974 whitespace tokens are **method-specific**; independent regex tokenization yielded 74,184, which is no contradiction and must not be used as an edition fingerprint. No assertion of a 69-chapter *published edition* or complete text follows from this conversion.

## Private custody and independent checks

An owner-only `0600` private receipt stores precise archive-member locators, spine checksums and these chapter hashes outside the public repository. Its 23,306 bytes hash to `efd2a7d3f6d3fbf7906ed52d3394d403fa860edb71be4f29f35c249315686362`. The public index pins the OPF and HTML content hashes but not local paths or original source bytes. A separate audit independently confirmed the keyed OPF checksum, the one resolved spine body, front-matter identity fields, and 69 ordered headings. An archive filename-stem match remains merely a pairing hint.

**Scope and coverage:**

- `SOURCE_BOUND`: **not admitted**; Librarian must review source-to-edition correspondence and provenance. This proposal exposes one plausible private source to bind later.
- `STRUCTURALLY_INDEXED`: the **converted file** has a provisional 69-chapter structural locator index. The accepted Work coverage ledger is unchanged.
- `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, `ENTITY_LINKED`, `AUDITED`: **not claimed**. No neutral story coding or counterevidence analysis has occurred.
- `accepted_work_effect=NONE`; `accepted_source_binding_effect=NONE`; `coverage_effect=NONE`.

> **Hostile challenge:** A parseable body with ordered chapters can still be missing content, contain conversion errors, represent a later edited text, or be misidentified despite matching front matter. Byte-level original LIT comparison, completeness checks and a private full-source reading must precede promotion.

Validation: `python3 proposals/research/lit-time-to-kill-structure-20261103/validate.py`, then `python3 tools/validate.py`. The public validator checks internal shape, monotonic locators, hashes and no-leak schema; it **cannot recompute source hashes** without the private archive.
