# Star Trek: Picard — three publisher-edition inventory candidates

This Librarian-only tranche records **three proposed narrative Works and three distinct trade-paperback manifestations** from Simon & Schuster's official product catalog. It does not admit Source↔Work bindings, index book text, reconcile global identity, alter the public Explorer, supply artwork rights, or advance literary coverage.

| Work candidate | Publisher series designation | Author | Trade paperback ISBN13 | Publisher product date / length |
| --- | --- | --- | --- | --- |
| [*The Dark Veil*](https://www.simonandschuster.com/books/Star-Trek-Picard-The-Dark-Veil/James-Swallow/Star-Trek-Picard/9781982154073) | Book #2 | James Swallow | `9781982154073` | 2021-09-07 / 336 pp. |
| [*Rogue Elements*](https://www.simonandschuster.com/books/Star-Trek-Picard-Rogue-Elements/John-Jackson-Miller/Star-Trek-Picard/9781982175207) | Book #3 | John Jackson Miller | `9781982175207` | 2022-06-07 / 416 pp. |
| [*Second Self*](https://www.simonandschuster.com/books/Star-Trek-Picard-Second-Self/Una-McCormack/Star-Trek-Picard/9781982194833) | Part of Star Trek: Picard (no ordinal asserted) | Una McCormack | `9781982194833` | 2023-09-19 / 320 pp. |

## Evidence and lineage

- **Observed:** 2026-11-03 UTC, through bounded public web retrieval of Simon & Schuster's official product-page metadata (title, author, publisher series description, format, ISBN13, publisher date and length). The exact publisher HTML bytes were **not downloaded or archived**; `content_hash`, `content_fingerprint`, `source_version` and `retrieved_at` therefore remain null. The observation date records this research pass, not a verified server timestamp.
- **One upstream independence group:** `publisher:simonandschuster.com`. Its author/series search listings and product pages are **not independent witnesses**. No external catalog second witness is claimed.
- **Scope:** each Source is the metadata representation of one trade-paperback edition. The three proposed Work IDs are not accepted global identities. Alternate eBook, audio, reprint and adaptation manifestations were not processed.
- **No content read:** title/author/ISBN concordance permits a `METADATA_ONLY` proposal, not a `SOURCE_BOUND` or `FULL_TEXT_AVAILABLE` coverage increment. No fictional event, character assertion, continuity, or interpretation is recorded.
- **No content copied:** neither publisher page body, book excerpt, cover, soundtrack, artwork binary nor full text enters this public repository.

The separately proposed *Star Trek: Picard: The Last Best Hope* (ISBN `9781982142186`) is deliberately **not duplicated here**; that source/edition candidate belongs to a separate literary work tranche. The previously reported Open Library cover ID for that title is also **not** evidence or permission for these three covers.

## Deterministic build and audit gates

`bundle.json` is the bounded publisher-source declaration. `validate.py` validates URLs, ISBN checksums, dates, typing, unique Work/Source IDs, metadata-only lifecycle, source lineage and the repository's Source/Work/binding schema before emitting byte-deterministic `records.json`.

```bash
python3 proposals/librarian/picard-companion-editions-20261103/validate.py --check
python3 tools/validate_librarian_registry.py registry/librarian_registry_fixtures.json
python3 tools/validate.py
```

**Coverage/admission effects:** `accepted_work_effect=NONE`, `accepted_source_binding_effect=NONE`, `coverage_effect=NONE`. The current literary Work denominator, text-reading ledger and audited coverage remain unresolved. A future Librarian review may connect independent bibliographic sources or content-addressed private editions; only separate accepted reconciliation and content review could advance research states.
