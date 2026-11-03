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
  ships **no** licensed image binaries or `licensed-artwork/` directory.

The [publisher discovery catalog](PUBLISHER_DISCOVERY_CATALOG.md) documents
source metadata; it must not silently acquire cover URLs. The independently
reviewed `explorer/artwork-catalog.json` contains **four opt-in Open Library API
previews** for exact autobiographical book editions, and no local artwork.
The additive proposed `explorer/artwork-catalog-v1.3.json` upgrades only those
**four** cover previews from Open Library small (`S`, 38-pixel thumbnails) to
documented medium (`M`, 180-pixel jackets). The original
`explorer/artwork-catalog.json` (v1.2.0) remains **byte-identical** and
packaged alongside it indefinitely for cached older Explorer clients.
The matching dual-reader UI must try only the strictly reviewed v1.3.0
sidecar first and fall back to unchanged v1.2.0 on missing, invalid or
unavailable medium images; no remote requests occur before visitor opt-in.
**No merge or deployment ahead of a compatible independently browser-tested
UI: no temporary blank cover shelf.** If both optional artwork sidecars are
absent, the browser reports artwork unavailable, not an empty universe.

## Future sidecar contract (not a release receipt)

An authorized release may carry exactly the following keys:

| Field | Requirement |
| --- | --- |
| `schema_version` | `1.2.0` legacy fallback or `1.3.0` additive medium sidecar (matching dual-reader Explorer UI required) |
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
- `artwork_kind`: `PUBLICITY_STILL`, `POSTER`, `COVER`, or `OTHER`; must match
  the reviewed image and source-local medium.
- `attribution_text` (1–160 characters) and `attribution_url`: visible credit
  and exact reviewed HTTPS asset-page link. The source-local
  `source_locator` remains the work's first-party source URL, **not** an
  attribution substitute.
- An independently reviewed rights receipt in
  `registry/artwork-rights-receipts/` must record the exact image hash,
  Commons/rights-page revision and snapshot digest, license or permission
  basis, asset credit, row/source binding, and distinct reviewer identities.
  The code-owned release pin binds the entire tuple and the receipt's own
  byte digest. Neither a Commons license tag nor an uploader's eBay scan
  attribution proves rights by itself.

**Documented Open Library book-cover API:** only a `LITERATURE` source row.

- `provider`: `OPEN_LIBRARY_COVERS_API` (no arbitrary provider URLs).
- `cover_id`: bounded positive Open Library numeric cover ID; browser derives
  `https://covers.openlibrary.org/b/id/<id>-M.jpg?default=false` itself,
  strictly after opt-in, in the matching v1.3.0 UI.
- `image_size`: the exact code-pinned value `M`; no sidecar-selected size,
  arbitrary URL, provider, or fallback to an unreviewed rendition.
  [Open Library Covers API](https://openlibrary.org/dev/docs/api/covers)
  defines `M` as a medium detail-page cover.
- `isbn`: exact 13-digit edition ISBN; `attribution_url` must be
  `https://openlibrary.org/isbn/<isbn>`.
- `edition_metadata_sha256`: SHA-256 of the exact Open Library edition
  metadata used for the ISBN-to-cover crosswalk (64 lowercase hex).
- Independent `registry/artwork-edition-receipts/` records additionally pin
  the exact viewed `-L.jpg` preview SHA-256 and now also the distinct
  `-M.jpg?default=false` **JPEG SHA-256, byte length, 180-pixel width, bounded
  height, exact provider URL, official API docs, and separate visual reviewer**.
  Both inspections confirm a *front jacket rather than an interior title page*,
  edition metadata response identity, and distinct review roles. A valid
  ISBN/JSON digest/HTTP 200 alone is insufficient.
  The medium-byte/visual observation's author is
  `chatgpt.trek.librarian.private_inventory`, recorded in shared Blotter event
  #3466; the later Librarian source-only PR #421 is corroborating proposal
  metadata, not itself publication or an independent license grant.
- `rights_status`:
  `API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED`, explicitly distinct from
  licensed/public-domain status.
- The rendered image links visibly to Open Library. It is fetched only after
  opt-in, with `referrerPolicy='no-referrer'`, `loading='lazy'`, and a fallback.

**Staged v1.3.0 release gate:** four source-local autobiography editions have
independently checked publisher ISBN, Open Library edition JSON and visual
front-jacket review receipts. The code-owned Python release pins and public
medium sidecar include only those four; a separately reviewed Explorer JS code-owned
receipt map and live browser opt-in qualification must agree before the
previews display. Sidecar-supplied values cannot approve themselves. These
are API previews, **not mirrored image copies or copyright clearance**.
An independently checked *Enterprise War* edition's cover ID `12857937`
returned an **interior title page**, so that image is explicitly held despite
its valid ISBN and edition digest.

Even after a separately reviewed receipt is introduced, the requested ISBN
must appear in the target literary lead's independently generated publisher
edition details. Simon & Schuster product locators ending in an ISBN must also
identify that exact edition; a row may list other formats that belong to a
different product URL. The accepted Penguin Random House/Titan fictional
memoir leads use a distinct `Paperback ISBN …` detail format, and their
source URLs are restricted to that distributor's bounded `/books/<id>/<slug>/`
path, `FICTIONAL_MEMOIR` kind, and publisher-lineage group. These are
defense-in-depth consistency checks, not cover-authenticity or display-rights
proof. The **local licensed-binary** receipt map remains empty and fail-closed;
the Open Library API cover map contains exactly four reviewed editions.

The static Pages package includes only a sidecar passing
`python3 tools/validate_artwork_release.py --check --verify-git` and any
locally licensed binaries explicitly named by the reviewed manifest. The
validator rejects unreviewed entries, mismatched source rows or ISBNs,
arbitrary image/receipt SHA strings, unsupported media, symlinks and traversal,
unlisted files, and CSS/HTML tricks that would request remote images before
visitor opt-in. Separate rights and publisher evidence review remains
mandatory for any later licensed binary.
The JavaScript validator is a defense-in-depth contract, **not** a legal
license examiner; an attacker cannot make unlawful art lawful by supplying
syntactically valid hash strings.

On approval, images remain **off by default**. A visitor can choose
`Show sourced artwork` to load the current visible cards' allowed assets and
documented API previews. Images are lazy-loaded, `no-referrer`, and degrade
to `Image unavailable` without hiding the source record or its locator.

## Current source candidates still held from public artwork

The Librarian's [artwork candidate receipts](../proposals/librarian/artwork-source-candidates-20261103/MANIFEST.md)
include a source-relative Open Library crosswalk for *Star Trek: Picard: The
Last Best Hope* (ISBN 9781982142186, cover ID 10157401) with a documented
human-facing API route. **That book does not yet have a source-local literary
row in the current public directory.** Its cover must not be displayed under
*Strange New Worlds: Ring of Fire* merely to fill a blank. No sidecar entry
or cover binary is released until exact literary row identity is established.
Open Library's API route is a display-method record, not publisher permission
or proof of the jacket's copyright ownership.

The four autobiographies (*Kirk*, *Picard*, *Janeway*, *Spock*) have separate
edition/visual receipts and are source-local image-display options only. No
`SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, or semantic coverage transition follows
from displaying a cover. Other Commons publicity stills remain **candidates**
until independently verified image bytes, the Commons rights evidence page,
notice/licensing review, correct episode-row mapping and visible attribution
all pass the code-owned licensed-artwork gate.
