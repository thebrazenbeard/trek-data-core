# Modern Paramount+ season-two discovery — first five slots per series

- Batch: `modern-paramount-season2-first5-20261102`.
- Research status: **PROPOSED publisher metadata only**, independent of the prior season-one tranche.
- Four first-party U.S. Paramount+ guide pages observed 2026-11-02: `Discovery`, `Picard`, `Lower Decks`, `Strange New Worlds` (season two, first five displayed entries each).
- Each CSV contains only a short episode title and source-local season and episode number. Exact CSV SHA-256 and guide locator are pinned in a separate receipt. The published page HTML bytes are **not preserved/authenticated**.
- Deterministic candidate-only build uses `tools/normalize_episode_roster.py` and the four `*/bundle.json` files. Each proposed episode has null canonical Work and Source binding IDs.
- No accepted evidence, transcript, continuity assertion, complete season denominator, or franchise coverage is created by these **20 candidate source-local rows**.
- All four pages belong to the **same Paramount+ publisher independence group**. Cross-publisher identity comparison is pending.

Publisher source locators:

- https://www.paramountplus.com/shows/star-trek-discovery/episodes/2/
- https://www.paramountplus.com/shows/star-trek-picard/episodes/2/
- https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/2/
- https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/2/

These batches intentionally cover a five-entry slice, not the remainder of each season. They may supplement but must never be added to a separate Wikidata count as if every row were a different canonical Work.
