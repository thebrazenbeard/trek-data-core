# Explorer thumbnail policy and local display contract

The Explorer now reserves a small LCARS-style art frame for each source-local
episode, film, short-form, literary, or audio record. An **empty frame is not a
claim that the work lacks a published cover**: it means no artwork has passed
the separate public-display rights gate in this repository.

The ship-bridge hero is the repository's existing supplied image. The new card
frames are original CSS geometry and are not intended to resemble official
episode stills, licensed book jackets, or publisher posters.

## Rights before images

- A discovery source URL, ISBN, or image CDN link does **not** grant display,
  reproduction, hotlinking, or redistribution rights.
- No image is downloaded or mirrored by the Explorer or repository. It has
  two narrowly scoped display routes: rights-cleared same-origin local assets,
  and the **documented Open Library Covers API** for opt-in, attributed book
  identification previews. Open Library documents the endpoint for HTML image
  display but does not grant ownership or resolve underlying cover copyright.
  [Covers API](https://openlibrary.org/dev/docs/api/covers) ·
  [Licensing caveat](https://openlibrary.org/developers/licensing).
- No third-party image request occurs on page startup. The CSP permits only
  self-hosted images, `covers.openlibrary.org`, and its archive.org image
  redirects; a user must activate `Show sourced artwork` first.
- Publisher CDN images require actual reuse permission before a local asset
  release; no publisher image is hotlinked from an observed episode/movie page.
- The card's source-level metadata remains `UNVERIFIED_METADATA`; artwork
  permission is **not** proof that an episode was watched or a novel read.
- A future licensed binary is published only with an immutable image SHA-256
  receipt and a separate rights-document SHA-256. This repository currently
  ships no such approved card artwork and no `licensed-artwork/` directory.

The [publisher discovery catalog](PUBLISHER_DISCOVERY_CATALOG.md) documents
source metadata; it must not silently acquire cover URLs. The optional
`explorer/artwork-catalog.json` is intentionally absent until eligible
source-bound image entries are reviewed and packaged. The browser treats its
404 state as `ARTWORK_UNAVAILABLE`, not an empty universe or an episode error.

## Future sidecar contract (not a release receipt)

An authorized release may carry exactly the following keys:

| Field | Requirement |
| --- | --- |
| `schema_version` | `1.2.0` (older artwork sidecars are rejected) |
| `data_status` | `PROVENANCE_REVIEWED_ARTWORK` |
| `coverage_effect` | `NONE` |
| `rights_policy` | `PER_ENTRY_DISPLAY_GATE` |
| `artwork_count` | Exact array length, 1–5000 |
| `artwork` | Array of right-cleared entries, no duplicate keys |

All entries have an exact accepted `row_id` (`directory:<source-local-row-id>`
or `film:<film-catalog-id>`) and `source_locator` matching that row, plus an
honest `alt_text` (180 characters or fewer). Entry variants have distinct
rights gates:

**Locally licensed file:**

- `image_path`: an actual same-origin file under
  `./licensed-artwork/<bounded-name>.png|jpg|jpeg|webp`; no remote or `data:`
  URL, path traversal, scriptable SVG, query string, or port.
- `image_sha256`: SHA-256 of the licensed file bytes (64 lowercase hex).
- `rights_status`: `PUBLIC_DISPLAY_PERMISSION_VERIFIED` only.
- `rights_receipt_sha256`: SHA-256 of the independently retained permission
  or license evidence, not an invented constant.

**Documented Open Library book-cover API:** only a `LITERATURE` source row.

- `provider`: `OPEN_LIBRARY_COVERS_API` (no arbitrary provider URLs).
- `cover_id`: bounded positive Open Library numeric cover ID; browser derives
  `https://covers.openlibrary.org/b/id/<id>-S.jpg?default=false` itself.
- `isbn`: exact 13-digit edition ISBN; `attribution_url` must be
  `https://openlibrary.org/isbn/<isbn>`.
- The ISBN must independently match a complete `Format · ISBN <isbn>` item
  in the corresponding source-local `LITERATURE` discovery row's `details`
  array. A matching artwork `row_id` and `source_locator` are not sufficient:
  an unrelated book's cover cannot inherit another Work's card. This
  version-1.2 gate uses the current deterministic directory compiler's
  edition-list format; rows without that format remain in placeholder mode.
- `edition_metadata_sha256`: SHA-256 of the exact Open Library edition
  metadata used for the ISBN-to-cover crosswalk (64 lowercase hex).
- `rights_status`:
  `API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED`, explicitly distinct from
  licensed/public-domain status.
- The rendered image links visibly to Open Library. It is fetched only after
  opt-in, with `referrerPolicy='no-referrer'`, `loading='lazy'`, and a fallback.

Static Pages packaging, the artifact allowlist, and independent rights review
must be updated and rerun before adding any actual sidecar or image binaries.
The JavaScript validator is a defense-in-depth contract, **not** a legal
license examiner; an attacker cannot make unlawful art lawful by supplying
syntactically valid hash strings.
The edition check likewise cannot prove an external cover-ID-to-ISBN match:
that requires independent edition metadata review against the pinned source
receipt. It only blocks a cross-Work mismatch using the separate directory
edition list already accepted into the candidate-only build.

On approval, images remain **off by default**. A visitor can choose
`Show sourced artwork` to load the current visible cards' allowed assets and
documented API previews. Images are lazy-loaded, `no-referrer`, and degrade
to `Image unavailable` without hiding the source record or its locator.

## Current open source candidates, not accepted artwork

The Librarian's [artwork candidate receipts](../proposals/librarian/artwork-source-candidates-20261103/MANIFEST.md)
include a source-relative Open Library crosswalk for *Star Trek: Picard: The
Last Best Hope* (ISBN 9781982142186, cover ID 10157401) with a documented
human-facing API route. **That book does not yet have a source-local literary
row in the current public directory.** Its cover must not be displayed under
*Strange New Worlds: Ring of Fire* merely to fill a blank. No sidecar entry
or cover binary is released until exact literary row identity is established.
Open Library's API route is a display-method record, not publisher permission
or proof of the jacket's copyright ownership.
