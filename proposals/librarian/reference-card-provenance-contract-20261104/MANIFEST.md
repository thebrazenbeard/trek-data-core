# Source-local provenance contract for original reference cards (HELD)

Accepted baseline: `main@3028765359001b90bc3e6b5c1835ee283b326e91`. The accepted `explorer/search-catalog.json` is an index of **1,214 source-local candidate rows**, not admitted canonical Works. Its `verification_status` is `UNVERIFIED_METADATA` for all 1,214 rows, even where a narrower `metadata_recheck_status` says `rechecked_exact`. The art input must preserve that distinction. This proposal uses six bounded rows: two episodes, two films, two literary listings, with their existing exact source locators.

## Existing original-art capabilities (avoid duplicate generators)

- Accepted `tools/build_explorer_abstract_art.py` emits five shared category SVGs (episode, film, literature, short-form, audio) from the safe renderer in `proposals/librarian/original-nasa-fallback-20261103/tools/render_original_abstract_art.py`. Existing `tests/test_explorer_abstract_art.py` verifies exact rebuilt bytes and safe SVG vocabulary.
- Accepted `explorer/app.js:makeArtworkSlot` **already displays per-record title, context, derived initials, and a source-reference link**, with its own category background, accessible label and explicit `NOT OFFICIAL ART` distinction. Separately reviewed real artwork is opt-in.
- There is no reason for the Librarian to create a competing SVG generator or alter the Explorer. This packet defines the **metadata binding interface** that a Consolidator/Designer may consume and test before any visual change.

## Contract

`tools/build_reference_card_inputs.py` reads only the pinned accepted catalog; it emits six reference/label payloads as JSON to stdout, never images. Each payload contains the exact accepted source-local `row_id`, medium, title, context, source locator, provenance status, and a row fingerprint. The `visual_seed_sha256` is `SHA256(medium + NUL + row_id)`, matching the existing renderer's seed source; rows with the same displayed title remain visually distinguishable when their source IDs differ. A genuine work/edition join is **not** inferred. An ISBN-looking publisher URL is not enough to populate `edition_identifier`: all six sample entries correctly leave it null.

The source locator is a link to inspect a discovery record, **not evidence that the narrative was close-read**. The title is factual directory metadata, not an authorization to use original jacket art, screen captures, film logos or Starfleet marks. Any future card graphic must prominently distinguish itself as an original index graphic rather than the actual episode/film/book cover. Repository ownership of procedural art is distinct from ownership of franchise material.

| Sample source row | Input category | Identity caution |
|---|---|---|
| `lead:0000` | TOS episode lead | Wikidata-derived candidate, recheck does not admit Work |
| `lead:0050` | DS9 episode lead | Source-local candidate, not plot evidence |
| `film:film-2009` | Film listing | Publisher page reference, not official poster authorization |
| `film:film-nemesis` | Film listing | Publisher listing, not license to use behind-scenes photo |
| `literature:prh-autobiography-janeway` | Literary listing | No edition join inferred from URL |
| `literature:proposed-lit-snw-ring-of-fire` | Literary listing | Publisher URL may contain ISBN but must remain source-specific |

## Hostile falsifiers

> `rechecked_exact` metadata could be misrendered as canon `VERIFIED`. The contract requires exact `verification_status` and `identity_scope`, with zero Source→Work/coverage effects.

> A card renderer might copy a publisher URL's numeric suffix into an ISBN label and thereby claim edition custody. The contract deliberately sets `edition_identifier:null` until an accepted exact edition record and reconciliation exists.

> A malicious title or URL could inject SVG or a remote image. Input validation and the existing SVG renderer test escaped XML, fixed HTTPS citation URLs, safe tags, no `<image>`, scripts, external resources, or likeness claims.

Validation:

```bash
python3 -m unittest tests.test_reference_card_provenance_contract tests.test_explorer_abstract_art -v
python3 tools/build_reference_card_inputs.py
```

No generated SVG, static asset, deployment, release policy or public artwork effect is part of this proposal. The next owner is **Consolidator/Explorer Designer** for optional UI visual treatment, rendered-browser inspection and release-gated deployment; Librarian owns source-binding truth.
