# Librarian artwork-source and rights boundary — six jackets, no episode/film stills

**Local-only PROPOSED audit** · accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91` · 2026-11-04. No public asset release, remote Git mutation, image download, new Source/Work admission, or research coverage transition.

## Observed accepted Explorer state

| Medium and accepted projection scope | Actual image route | Count | Rights status |
| --- | --- | ---: | --- |
| Literature, four original autobiographical source-local directory rows | Open Library **medium** jacket via visitors' explicit opt-in | 4 | API display documented; underlying copyright **unresolved** |
| Literature, separate Picard literary supplement | Same API route and opt-in | 2 | Same unresolved underlying copyright |
| Episodes, 1,155 source-local metadata rows in baseline discovery | Original LCARS category placeholders | **0** episode stills | No image-specific display permission receipts |
| Films, 14 film rows in separate film projection | Original LCARS category placeholders | **0** film posters/stills | No image-specific display permission receipts |

The baseline `tools/report_artwork_coverage.py --check --verify-git` reports **4 reviewed mappings across 1,214 original discovery rows**, including literature 4/9, episodes 0/1,155, films 0/14, short-form 0/35 and audio 0/1. Its denominator deliberately excludes the separately additive **two** Picard edition rows. `tools/validate_picard_jacket_release.py --check --verify-git` independently reports **4+2**, zero local image bytes, and `SIX_REMOTE_API_COVERS_OPT_IN_REVIEWED`. Do **not** say six of the original 1,214 were mapped; the six belong to two different explicitly versioned scopes. The visuals/coverage worker owns any new combined denominator projection.

`ledger.json` pins all six exact source-local row IDs, ISBNs, cover IDs, and first-party publisher URLs from `explorer/artwork-catalog-v1.3.json` and `explorer/picard-jackets-v1.0.json`. The entire upstream catalog byte digests are pinned for deterministic regression. The six edition pages were separately located and read **today** as publisher metadata:

- Penguin Random House/Titan: [James T. Kirk](https://www.penguinrandomhouse.com/books/250795/the-autobiography-of-james-t-kirk-by-david-a-goodman/), [Jean-Luc Picard](https://www.penguinrandomhouse.com/books/555327/the-autobiography-of-jean-luc-picard-by-david-a-goodman/), [Kathryn Janeway](https://www.penguinrandomhouse.com/books/646637/the-autobiography-of-kathryn-janeway-by-una-mccormack/), [Mr. Spock](https://www.penguinrandomhouse.com/books/577045/the-autobiography-of-mr-spock-by-una-mccormack/).
- Simon & Schuster/Pocket Books: [*The Dark Veil*](https://www.simonandschuster.com/books/Star-Trek-Picard-The-Dark-Veil/James-Swallow/Star-Trek-Picard/9781982154073), [*Rogue Elements*](https://www.simonandschuster.com/books/Star-Trek-Picard-Rogue-Elements/John-Jackson-Miller/Star-Trek-Picard/9781982175207).

These pages establish publisher-attributed bibliographic edition identity; they are **not** book-cover image license evidence and not an independent copyright ownership determination. Previously accepted publisher/edition/Open Library metadata hashes and separate visual reviews support the six exact API thumbnail crosswalks; this audit did not download or visually recheck pixels. First-party pages may change after this observation and the local CI validator does not fetch live publisher pages.

## Permissible current display path vs. unlicensed publication

[Open Library's Covers API documentation](https://openlibrary.org/dev/docs/api/covers) describes direct HTML `<img src>` display on public-facing pages, asks sites to use `covers.openlibrary.org`, discourages crawling/bulk fetching, and appreciates attribution backlinks. The [separate developer licensing statement](https://openlibrary.org/developers/licensing) says Open Library does not newly assert copyright over database contributions and explicitly warns that existing rights issues can remain. Thus the documented API display route is **a provider usage method, not an image copyright license, public-domain declaration, or permission to rehost**.

The accepted Explorer honors that narrow route: no remote image loaded at startup; a user enables **Show sourced artwork**; only six code-reviewed remote Open Library cover IDs become `<img>` requests with `no-referrer`, lazy loading, ISBN attribution links, and fallback to original LCARS art. All six carry `API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED`. Two Picard images live in a separate pinned sidecar; their `registry/artwork-edition-receipts/picard-jackets-review.json` says `image_bytes_mirrored=false` and `copyright_status=UNRESOLVED`.

**Rehosted/downloaded artwork:** No public license/permission receipt is accepted for any of these six jacket images, nor for an episode still or film poster. A high-resolution image download link on a publisher product page is not, alone, a general reuse license. No `explorer/licensed-artwork/` or image-specific accepted rights-receipt directory exists in this accepted checkout. A self-hosted binary release remains **HELD** pending actual image-specific permission/licensing, byte hash, source-row identity and independent review.

**Episode/film artwork:** The Librarian's accepted `proposals/librarian/artwork-primary-asset-locators-20261103/` contains **ten** source-only image URL observations: three StarTrek.com film *site headers* (not verified theatrical posters), three S&S literature/audio edition covers (an audio cover is not a book jacket), and four Paramount+ Strange New Worlds S3 episode-card thumbnails. They are `HELD_NO_PUBLIC_DISPLAY_LICENSE`; source pages prove that the publisher pointed at an image, not permission to embed or redistribute it. Memory Alpha search results are derivative discovery leads, not a separate copyright grant.

The original CSS/SVG LCARS category illustrations can remain as **abstract navigation placeholders**, properly labeled as *not* production imagery. They are not counted as episode/film visual coverage. The repository hero image has its own supplied-artwork provenance; this audit does not extend its permissions to third-party thumbnails.

## Hostile challenges and falsifiers

> **Hostile review:** An exact ISBN-to-cover-ID match and a perfect image SHA-256 receipt prove an image was inspected, not that its creator or rights holder granted redistribution. Open Library documenting public-page `<img>` use is not equivalent to clearing all underlying rights under every jurisdiction.

> **Hostile review:** Six API jacket candidates cannot be counted as 6/1,214 baseline artwork coverage. The two Picard supplement rows extend a separate scope; the consolidated numerator needs an explicitly combined, audited denominator.

> **Hostile review:** Film HTML `og:image` can be a generic header; Paramount+ episode-card CDN URL can be correct and still remain unlicensed. One source page's picture must not be swapped into a different source-local episode or work to fill a blank.

**Next evidence to upgrade episode/film actual thumbnails:** authenticated official-source image identity, image byte and permission/license receipt (rights holder, scope, revision, provenance, attribution, allowed display/rehosting), exact row mapping, separate rights reviewer, and no-lazy-load regression tests. For new Open Library API book previews: exact-edition ISBN/covers metadata/visual review, separately pinned code allowlist, documented API terms, and an explicit unresolved-copyright label. Neither path changes SOURCE_BOUND or literary CLOSE_READ.

## Verification

```bash
python3 proposals/librarian/artwork-source-rights-audit-20261104/validate.py
python3 -m unittest tests.test_artwork_source_rights_audit -v
python3 tools/validate_artwork_release.py --check --verify-git
python3 tools/validate_picard_jacket_release.py --check --verify-git
python3 tools/report_artwork_coverage.py --check --verify-git
```

The local validator fails on image ISBN/ID/source crosswalk substitutions, false public-domain or licensed claims, an always-on remote-image route, invented episode/film artwork counts, duplicated/reclassified rows, hash drift and a surprise local licensed-artwork directory. It proves packet consistency **against accepted code-owned source snapshots**; it cannot independently decide copyright law or authenticate a future remote HTML/image response.
