# Memory Alpha artwork and metadata discovery — 2026-11-03

**Owner:** LIBRARIAN (proposal only)
**Accepted-main baseline:** `f387126c60942ff90952cd6e9251a67c8f5c26fa`
**Artifact:** [`records.json`](records.json), validated with [`validate.py`](validate.py)
**Effects:** accepted Source/Work/Evidence/Coverage `NONE`; artwork publication `NONE`; no downloaded image or copied wiki article.

## What was actually retrieved

The [Memory Alpha portal](https://memory-alpha.fandom.com/wiki/Portal:Main) was requested as a discovery source. Direct portal, category, and `File:` page reads were blocked by the public retrieval service's robots restrictions. **The image files themselves, original uploader details, attribution text, individual copyright notices, and file-level licenses were not retrieved.** The eight filenames below came from public search-indexed category excerpts, **not** firsthand inspection of the image descriptions. Their title and subject matches are tentative.

| Indexed file lead | Possible subject in accepted Explorer | Mapping boundary |
| --- | --- | --- |
| `The Autobiography of James T. Kirk.jpg` | `literature:prh-autobiography-kirk` | Title only; no edition cover match |
| `The Autobiography of Jean-Luc Picard cover.jpg` | `literature:prh-autobiography-picard` | Title only; no edition cover match |
| `Autobiography of Kathryn Janeway cover.jpg` | `literature:prh-autobiography-janeway` | Title only; no edition cover match |
| `The Autobiography of Spock cover.jpg` | `literature:prh-autobiography-spock` | Title only; no edition cover match |
| `The Autobiography of Benjamin Sisko cover.jpg` | `literature:prh-autobiography-sisko` | Title only; no edition cover match |
| `2x06 The Doomsday Machine title card.jpg` | `lead:0000`, `legacy:s2:tos:005` | Two independent source-local episode rows; no global reconciliation |
| `Star Trek The Wrath of Khan artwork.jpg` | `film:film-wrath-of-khan` | Title only; poster/still permissions unknown |
| `USS Constellation remastered.jpg` | No accepted ship row | Candidate remains unbound |

The first five filename leads were indexed under [literature-cover images](https://memory-alpha.fandom.com/wiki/Category:Memory_Alpha_images_(literature_covers)); *Doomsday* and *Constellation* under [TOS remastered production files](https://memory-alpha.fandom.com/wiki/Category:Memory_Alpha_remastered_files_by_production_(TOS:_The_Doomsday_Machine)); and *Wrath of Khan* under [film production files](https://memory-alpha.fandom.com/wiki/Category:Memory_Alpha_files_by_production_(Star_Trek_II:_The_Wrath_of_Khan)). These category labels do not establish ownership or clearance. This is a set of **eight candidates**, not eight images, cover matches, verified sources, or admitted Works.

Two indexed article excerpts also suggest *The High Country* hardcover ISBN-10 `1668002388` and *The Autobiography of Kathryn Janeway* hardcover ISBN-10 `1789094798`. The accepted publisher-source rows show different paperback ISBN-13 editions (`9781668002391` and `9781789095333` respectively). These are **format-specific secondary leads only**; no identity merge or edition replacement is proposed.

## Why no thumbnails were activated

- [Memory Alpha's file-use policy](https://memory-alpha.fandom.com/wiki/Memory_Alpha:File_use_policy) calls for source/creator and fair-use/permission handling. [Its copyright notice](https://memory-alpha.fandom.com/wiki/Memory_Alpha:Copyrights) distinguishes Star Trek copyright owners from contributors. A wiki-specific fair-use assertion for a Paramount/CBS still or publisher cover does **not** give this public GitHub Pages project the same permission.
- [Fandom's reuse guidance](https://support.fandom.com/hc/en-us/articles/360035075654-I-want-to-reuse-text-or-images-from-a-Fandom-wiki) distinguishes wiki text licensing from rights in uploaded images and points to individual files and rights holders. A Creative Commons license on wiki text is **not** a blanket CC license on its artwork.
- [Wikimedia Commons' Fandom import guidance](https://commons.wikimedia.org/wiki/Commons:Fandom_files) cautions that Fandom files need demonstrable free rights before Commons reuse. A separately found Commons file with a reviewed compatible license, author, and attribution could become a new independent candidate; **none is verified in this tranche**.
- A hosted image's visibility does not imply image-hotlink, mirror, API, or redistribution permission. No Fandom image URL is recorded or invoked here, and no undocumented Fandom API endpoint is assumed to work.
- The Explorer's [artwork sidecar v1.1 contract](../../../docs/ARTWORK_THUMBNAIL_POLICY.md) remains fail-closed. These file titles do not supply a licensed local asset receipt, an independently reviewed Open Library exact-edition receipt, or a separate rights receipt. `explorer/artwork-catalog.json` is deliberately untouched.

Memory Alpha is **secondary discovery**. It may help locate an episode, book edition, film, ship, or source but cannot, without independent primary corroboration, establish canonical universe truth, work identity, a complete source read, or rights to image bytes. Search-index excerpts and multiple wiki pages are not independent primary corroboration.

## Independently inspected Commons alternatives

Unlike the indexed Memory Alpha files, these **two actual Wikimedia Commons file-description pages were read** and each displays a specific Creative Commons license. This verifies *the page's licensing claim*, not every possible underlying franchise right.

| Commons file | Creator and claimed license | Possible use and hold |
| --- | --- | --- |
| [TNG props at the Henry Ford Museum](https://commons.wikimedia.org/wiki/File:Star_Trek_-_The_Next_Generation_Props_-_Star_Trek-_Exploring_New_Worlds_Exhibit_at_the_Henry_Ford_Museum,_Dearborn,_Michigan.jpg) | Photo by Joe Ross, 22 Aug 2019; [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/), originally [Flickr](https://www.flickr.com/photos/joeross/49785566691/); Commons reports FlickreviewR confirmation 15 Jun 2023 | Possible decorative museum photograph, **not** an exact episode still or poster. Original prop-design/trademark considerations, attribution integration, and image release review unresolved. |
| [Starfleet OF1 rank insignia](https://commons.wikimedia.org/wiki/File:Starfleet_OF1.png) | Sano, self-described own work, 1 Dec 2014; [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | Potential design reference only; derivative franchise insignia/trademark review unresolved. Not a canonical studio-brand grant. |

Neither image was downloaded, hotlinked or published. A released CC BY-SA asset would require credit, license link, modification notice if changed, appropriate share-alike handling, actual bytes/hash and a separate approved public-use assessment. The photographed props may themselves depict protected franchise designs; the CC license granted by a photographer does not by itself cover rights they do not own. Their records are distinct from the eight uninspected Memory Alpha leads.

## Safe next gate

1. Obtain a permitted file-description view and record the exact title, creator/uploader, source, per-file terms, image fingerprint, and restrictions; do not evade robots or sign-in restrictions.
2. Seek a rights-cleared original, compatible Commons file, licensed publisher press asset, or separately authorized media. Independently check that permission applies to public web display and the exact art.
3. Bind a proposed cover to a **specific publisher edition** and exact source-local literary row, or a film/episode still to its exact production, without silently reconciling duplicate rows.
4. Review image rights apart from bibliographic identity, create a separate immutable receipt and tests, and only then consider an opt-in Explorer sidecar release. No automatic promotion from this packet.

**Result:** eight Memory Alpha image-file leads and two bibliographic leads indexed; **zero Memory Alpha file pages inspected**. Two Commons file-description pages checked for specific license claims, but **zero public artwork releases** and zero accepted source or coverage changes.
