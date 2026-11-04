# LIBRARIAN artwork custody and display gate — five representative routes

**Scope:** source-relative provenance, publisher/Commons/Open Library rights and
consent distinctions only. No licensed binary, screenshot, thumbnail URL,
copyright text, image, public Sidecar, accepted Work, Source binding, coverage,
deployment or release is created.

**Accepted source state:** `trek-data-core/main@3028765359001b90bc3e6b5c1835ee283b326e91`.
**Draft UI inspected:** [Explorer PR #486](https://github.com/thebrazenbeard/trek-data-core/pull/486),
head `8f71963f905eb4c2169ef46a1b488a257a99cc7e`, still an unmerged proposal.
**Director issue #23:** OPEN; no new research-admission tranches.

## Exact determinations

| Source-relative image candidate | Source/custody actually available | Authorized public delivery from accepted state |
| --- | --- | --- |
| *Strange New Worlds*, S3 E1 card | Paramount+ publisher guide source card and a pinned CDN locator, **no image bytes** | **HELD** — no reuse license established |
| *The Wrath of Khan* film art | StarTrek.com page `og:image` header, **not a verified theatrical poster** | **HELD** — a page header locator is not studio permission |
| *The Kobayashi Maru* eBook cover (ISBN 9780743419987) | Simon & Schuster linked downloadable high-res cover for this **eBook edition**; original observer did not read image bytes | **HELD** — resource link is not reproduction permission; do not swap across formats |
| Joe Ross museum prop photograph | Commons file description reports photographer **CC BY-SA 2.0**, Flickr provenance and a reported SHA-1, but no independently downloaded JPEG SHA-256 | **HELD** — underlying Trek props/branding review, scope, attribution, license obligations and binary custody remain unresolved |
| *Picard: The Dark Veil* trade-paperback jacket (ISBN 9781982154073) | Open Library API cover ID 10691195; accepted edition/large+medium visual receipt and attribution; no mirrored image | **Opt-in remote API preview only**, expressly `API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED`, not a licensed local copy |

The accepted v1.3 autobiography sidecar has **four** exact edition-linked
Open Library API jacket options; the Picard sidecar adds **two**, for six
possible opt-in remote API covers overall (subject to reader/sidecar release
compatibility), **zero** local licensed-image binary releases. These numbers
are options/sidecar rows, **not** a count of copyright-cleared covers or
independently admitted literary Works.

No `explorer/licensed-artwork/` physical binary directory or
`registry/artwork-rights-receipts/` approved rights receipt directory exists
in accepted main. The standalone `validate_artwork_release.py --check
--verify-git` reports four locally reviewed autobiography API options ready
for a *separate compatible UI release*, not an all-media public image license.

## Independent current documentation check, 2026-11-04

- [Open Library Covers API](https://openlibrary.org/dev/docs/api/covers)
  documents embedding its own `covers.openlibrary.org` URLs on public-facing
  pages, `M` detail-page size and courtesy attribution. Its
  [licensing overview](https://openlibrary.org/developers/licensing)
  warns underlying third-party rights may remain. API display is a separate
  limited option, **not** a license to rehost a jacket.
- [Simon & Schuster site terms](https://www.simonandschuster.com/p/terms-of-use)
  contain express permission limitations on copying/distributing site
  content. No standing permission for Explorer rehosting a jacket was found.
- [Wikimedia Commons photo page](https://commons.wikimedia.org/wiki/File:Iconic_Original_Series_Props_-Star_Trek_-_Exploring_New_Worlds_Exhibit_at_the_Henry_Ford_Museum.jpg)
  reports CC BY-SA 2.0 and a 2023 Flickr-review check for the *photograph*,
  not a release review for the underlying fictional prop designs or logos.
  Neither Commons metadata SHA-1 nor page text authenticates local JPEG bytes.

These are text/page observations, not independently archived remote-body
digests. This audit makes no legal finding that the rights holders actually
granted a license; it records specific missing release prerequisites.

## Draft Explorer #486 consequence

The exact draft changes **seven files**: three Explorer HTML/JS/CSS UI files
and four tests/validation files. It changes a misleading "Source-bound
imagery" label to **Pinned image previews**, adds a `receipt_pinned` filter,
and preserves the narrow `img-src` allowlist for same-origin and documented
Open Library/archive media hosts. It adds **no** binary, publisher CDN host,
artwork sidecar, or rights receipt. Visitor opt-in is consent to a network
request, **not consent by an image copyright holder**.

> **Hostile challenge:** A hash-pinned image *locator* can be perfectly
> reproducible and still point to a copyrighted asset that cannot be copied
> or displayed under the project's release rules. Five valid metadata
> references are not five cleared thumbnails. In particular, the film
> `og:image` is only a publisher header, and an Open Library API-allowed
> remote preview is not a licensed file for local redistribution.

## Deterministic audit and tests

[`review.json`](review.json) records five source-local decisions without
asset bytes. `tools/audit_artwork_five_routes.py` pins exact accepted input
SHA-256 digests, validates the five media/identity/route mappings and
denies rights escalation, image SHA-1→SHA-256 substitution, edition crossing,
unaudited new rights directories and copyrighted public-release claims.

```sh
python3 tools/audit_artwork_five_routes.py --verify-pr486
python3 -m unittest discover -s tests -p test_artwork_five_routes.py -v
python3 -O -m unittest discover -s tests -p test_artwork_five_routes.py -v
python3 tools/validate_artwork_release.py --check --verify-git
python3 tools/validate.py
```

`--verify-pr486` additionally requires the exact locally fetched Git PR head
and confirms the seven-file diff/consent/CSP boundaries; this optional check
fails closed if the draft Git object is unavailable. The offline source audit
does not fetch or inspect third-party image pixels or grant legal permission.

**Exact next frontier:** For publisher episode/film/book images, document
asset-specific permission and independent exact binary custody *before*
proposing a local release; for Commons photograph, resolve the permitted
scope and underlying image/prop/brand questions plus attribution and
share-alike obligations; for Open Library, preserve only reviewed,
edition-exact visitor-initiated API previews without mirroring. Do not use
metadata visual receipts to promote `SOURCE_BOUND` or research coverage.
