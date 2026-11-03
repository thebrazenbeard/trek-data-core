# Artwork candidate review deck — 2026-11-03

**Role:** LIBRARIAN; **scope:** exact source/rights reconnaissance and an offline decision preview.

**Accepted baseline:** initially researched against `main@5b0fb86b322811ccea58f88f20d69bd4e62e9b22`, then revalidated on accepted `main@ae5402a0db5d00ffcb5feec8fe161f75e1500a27` with the intervening repository changes merged locally. The `explorer/discovery-catalog.json` row IDs are source-local, not globally reconciled Works.

**Effects:** Source, Work, Evidence, Coverage, public imagery, deployment and site release all `NONE`.

## A specific Creative Commons photo, still held

[Wikimedia Commons file-description page: *Iconic Original Series Props — Star Trek: Exploring New Worlds, Henry Ford Museum*](https://commons.wikimedia.org/wiki/File:Iconic_Original_Series_Props_-Star_Trek_-_Exploring_New_Worlds_Exhibit_at_the_Henry_Ford_Museum.jpg) was independently read. Its description says Joe Ross photographed a museum case on 22 August 2019; the source is [Flickr photo 49785620807](https://www.flickr.com/photos/joeross/49785620807/). Commons labels the photo **[CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/)** and reports a Flickr licensing check by FlickreviewR on 15 June 2023. Commons' structured metadata reports SHA-1 `12e2558d6a21367f9c02495489d8832c4c539369`, 6,836,153 bytes, 3,712×5,568 JPEG. Those are **Commons-reported metadata**, not a hash independently recomputed over downloaded bytes; no JPEG bytes were obtained.

Suggested narrow role: optional documentary/decorative image of an exhibition **not** a frame from an episode, canonical spaceship depiction, or substitute for a specific episode thumbnail. Its photographer's CC grant does not automatically cover **underlying fictional prop designs, identifiable branding or trademarks**. The exact per-file photographer license has been identified, but the entire public-display rights decision is **held** for separate human review. No claim that the museum or Paramount endorsed this project is implied.

If ultimately approved, public credit must name Joe Ross, link the file/source and CC license, note any modifications, and follow share-alike requirements when applicable. Distribution would need a separately audited allowed asset path, exact SHA-256 computed from the downloaded file, rights evidence digest, and tests. The current proposal has **no public image URL, hash pretending to authenticate local bytes, art sidecar, or media binary**.

## Exact publisher-edition cover route, not clearance

[Simon & Schuster's official *Star Trek: Strange New Worlds: Ring of Fire* product page](https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Ring-of-Fire/David-Mack/Star-Trek-Strange-New-Worlds/9781668095898) describes **hardcover ISBN-13 9781668095898** and offers a high-resolution book-cover JPG resource. This is the exact edition on accepted source-local row `literature:proposed-lit-snw-ring-of-fire`, which also contains other editions in its `details`; the cover must **not** be silently assigned to those different ISBNs.

Crucial distinction: a public publisher download link is not a grant for unrestricted reuse. [S&S Terms of Use](https://www.simonandschuster.com/p/terms-of-use) restrict copying/distributing site content without express permission; its [Rights & Permissions entry](https://www.simonandschuster.biz/p/rights-and-permissions) provides inquiry routes but does not itself grant use. A dedicated book-as-prop request can involve a fee and is **not** the same as this web-thumbnail use. **No price-bearing request or account signup was made; budget $0.**

For the current Titan/PRH-distributed memoirs, [PRH's portal](https://permissions.penguinrandomhouse.com/) warns that distributed third-party titles may require contacting the actual publisher instead of PRH. Hence even a matching distributor page is not proof that PRH controls jacket rights. The accepted [Open Library Covers API](https://openlibrary.org/dev/docs/api/covers) explicitly describes public-facing remote-image display with courtesy attribution, but the accepted Explorer has a separate **empty reviewed exact-edition receipt gate**. No Open Library cover ID is proposed here.

## One film poster route, not clearance

[StarTrek.com's official *Star Trek II: The Wrath of Khan* page](https://www.startrek.com/movies/star-trek-ii-the-wrath-of-khan) visibly includes poster art and a header photograph. This page matches source-local `film:film-wrath-of-khan`. Its copyright notice reserves CBS Studios/Paramount rights; **no image-reuse grant was located**. [Official Star Trek research on TOS publicity photos](https://www.startrek.com/news/the-original-series-publicity-photos) distinguishes production-frame grabs from commissioned publicity photographs, whose presence on a studio page is not itself a reproduction license.

Alternative technical path only: [TMDB's noncommercial API](https://developer.themoviedb.org/docs/faq) describes free API access with attribution and required logo/notice, but also expressly disclaims ownership of uploaded images. It requires an API key and a separately evaluated individual image right; no key, account, API call, rights assignment, poster hotlink, or logo was added. Thus the current $0, no-login path is **official page link discovery, not a thumbnail**.

## Offline review preview (never published as Explorer art)

`render_preview.py` validates the pinned packet and creates a self-contained LCARS-colored *review deck* with three CSS-only **VISUAL HELD** cards and visible source/credit links. It has `img-src 'none'`, no `<img>`, scripts, remote CSS, iframes, image URLs, or automatic third-party requests. Clicking a source link is a separate deliberate navigation. The script prints only a successful in-memory validation by default; `--output /some/local/fresh-file.html` writes only outside the repository to an absent file and never overwrites. Nothing under `explorer/`, `docs/` or GitHub Pages was modified for this preview.

## Gate before a real image preview/release

1. Separate written decision per asset: check photographer grant *and* whether photographed props/brand design or cover/poster assets permit the intended public display, independent of noncommercial status.
2. Bind to the exact accepted source-local row and, for a book, one precise edition ISBN; keep distinct rows unmerged until an accepted reconciliation record exists.
3. Fetch bytes only after that decision, compute an immutable SHA-256 and receipt digest, credit creator/license/modifications, and review share-alike obligations.
4. Submit a **different** release-specific PR against then-current Explorer sidecar and Pages artifact guard, with opt-in-only display, no third-party startup image requests, a11y fallback, and independent tests.

**Verdict:** one real Commons CC-license candidate, one exact hardcover cover-discovery route, and one official film-poster discovery route; **all three remain display-blocked**, so the offline deck renders neutral geometric placeholders. This preserves source truth and the $0 constraint.
