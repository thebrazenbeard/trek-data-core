# Artwork source routes — second bounded Librarian tranche

**State: SOURCE DISCOVERY / RIGHTS REVIEW ONLY.** This records two distinct
identity-mark file descriptions and three provider routes. It does **not**
release images, authorize web display, bind global Works, or advance research
coverage. Baseline: accepted `main@d4ecd970bf28019696abd692011007d7d47f9ff8`.

## Actual discovery

1. [Wikimedia Commons: Star Trek Logo 1.png](https://commons.wikimedia.org/wiki/File:Star_Trek_Logo_1.png)
   identifies a modern Star Trek wordmark (source description: The Refinery /
   Mr Wonderful). Its [pinned Commons revision](https://commons.wikimedia.org/w/index.php?title=File:Star_Trek_Logo_1.png&oldid=1282184342)
   marks the design `PD-textlogo`, and its structured data lists a SHA-1.
   This is a **copyright characterization by Commons**, not a Paramount
   trademark permission. Repository branding and nonendorsement presentation
   still require review; no image was downloaded.
2. [Wikimedia Commons: Starfleet Shoulder Patch.svg](https://commons.wikimedia.org/wiki/File:Starfleet_Shoulder_Patch.svg)
   is attributed to uploader Shisma under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
   Its [pinned Commons revision](https://commons.wikimedia.org/w/index.php?title=File:Starfleet_Shoulder_Patch.svg&oldid=690293298)
   identifies the uploader's own work. The license permits attribution-based
   reuse of the uploader's contribution; rights in the underlying *Star Trek*
   fictional emblem may not belong to the uploader. **Do not publish merely
   because the Wikimedia license field is present.** SVG content has not been
   security-reviewed or downloaded.
3. [TMDB's official FAQ](https://developer.themoviedb.org/docs/faq) offers a
   free, attributed **noncommercial API** path for film/TV artwork; the
   [image URL guide](https://developer.themoviedb.org/docs/image-basics) and
   [movie image endpoint](https://developer.themoviedb.org/reference/movie-images)
   describe where image paths come from. The FAQ expressly says TMDB does
   **not** own the contributed images. It requires its logo and disclaimer in
   the site's Credits/About treatment. No account, credential, individual
   poster, or episode still was obtained; separate display-rights review is
   necessary. The static Explorer currently only allows local licensed assets
   and opt-in Open Library covers. No TMDB integration is proposed for direct
   release in this tranche.

## Reuse the already established book-cover route

The [earlier Librarian artwork receipt](../artwork-source-candidates-20261103/MANIFEST.md)
already identifies a **working** Open Library small-cover endpoint for
*Star Trek: Picard: The Last Best Hope* ISBN `9781982142186`, cover ID
`10157401`, and the edition-metadata digest. The [Covers API](https://openlibrary.org/dev/docs/api/covers)
explicitly documents HTML `img` thumbnails for public-facing sites, asks
for source credit and discourages API crawling. Its [licensing notice](https://openlibrary.org/developers/licensing)
does not settle underlying cover copyright. The book lacks a matching
source-local literary row in the current directory; **showing this image on
the existing *Ring of Fire* entry would be incorrect.** The parent proposal
must be joined to a verified edition row before the existing opt-in image
contract may be activated.

## Private ebook cover extraction is a different right

The connected private Star Trek ebook archives include OPF package records
and JPEG resources, potentially original jacket art and internal illustrations.
Possession of those files permits a private metadata/locator inventory; it
does not itself grant public-republication rights. Maintain original archive
and edition identities privately. Never infer that every JPEG is a book cover
or commit private image bytes to a public `licensed-artwork/` directory.

## Crosswalk and release gates

- `asset_candidates` are candidate **repository-brand identity assets**,
  not episode/film/book thumbnails or governed Work identities.
- `provider_routes` are policy/integration possibilities, not actual approved
  image records. Do not turn those into a populated `artwork-catalog.json`.
- For every future episode/film image: record exact Work-local ID, edition,
  image provenance and independent image-rights receipt, then review content
  copyright and hosting conditions. Discovery metadata alone is insufficient.
- For every literary image: bind ISBN/edition to one source-local book row and
  retain the exact cover ID/edition metadata digest. Open Library preview is
  API display with unresolved underlying copyright, not a sublicensable file.
- For logo/insignia: separately resolve trademark/nonendorsement, underlying
  design rights, attribution, and a reviewed artifact format (prefer a
  non-scriptable raster asset over unaudited SVG).
- Keep third-party artwork off by default, honor opt-in and attribution, and
  preserve accessible LCARS fallback. Do not edit the Pages artifact allowlist,
  deploy, or add a third-party CSP origin until independent approval.

**Next narrow deliverable:** After the private OPF inventory and book-edition
crosswalk, establish one exact source-local literature row for a cover with a
functioning documented Open Library API route; independently review rights and
the sidecar's deterministic binding. Film/episode TMDB candidate work requires
an authorized free API account/key and a per-image rights decision. These
are gates, not implied permission to fetch or display copyright content.
