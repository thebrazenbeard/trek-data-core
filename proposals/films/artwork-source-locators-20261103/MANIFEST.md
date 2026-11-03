# Film artwork source locators — candidate-only (2026-11-03 UTC)

Seven source-relative **metadata leads** for three films: four directly inspected franchise-publisher image labels/gallery headings, and three Memory Alpha file titles observed in web-search indexes. This file neither reproduces images nor claims they can be reused.

## Source boundaries

| Film discovery candidate | Verified publisher page/gallery metadata | Indexed Memory Alpha file lead |
| --- | --- | --- |
| `film-motion-picture` | [Publisher movie page](https://www.startrek.com/movies/star-trek-i-the-motion-picture): poster label | [Publicity category](https://memory-alpha.fandom.com/wiki/Category%3AMemory_Alpha_images_%28publicity%29): 4K *Director's Edition* screening poster file title |
| `film-search-for-spock` | [Publisher movie page](https://www.startrek.com/movies/star-trek-iii-the-search-for-spock): poster label; [11-image gallery](https://www.startrek.com/gallery/search-for-spock-enterprise): editorial heading, not eleven verified image IDs | [Production file category](https://memory-alpha.fandom.com/wiki/Category%3AMemory_Alpha_files_by_production_%28Star_Trek_III%3A_The_Search_for_Spock%29): 1985 VHS advert file title |
| `film-voyage-home` | [Publisher movie page](https://www.startrek.com/movies/star-trek-iv-the-voyage-home): poster label | [Dutch-language category](https://memory-alpha.fandom.com/nl/wiki/Categorie%3AFilms_-_004_-_The_Voyage_Home): poster file title |

The official movie pages themselves expose image alt labels and a 2026 Paramount/CBS *All Rights Reserved* footer. This is evidence that the publisher presents artwork, **not** a public license allowing this project's independent display, reproduction, or hotlinking. The official *Search for Spock* page also displays `1982` despite the AFI Catalog's 1984 release record; publisher metadata is therefore not automatically error-free.

Memory Alpha category and file names were found in cached/search-index results. Direct requests to Fandom were blocked by robots.txt; no access workaround was attempted, and no file page was directly read. Even where a wiki claims a CC BY-NC license for community text, that does not establish the underlying studio poster, screen capture, marketing photograph, or home-video advertisement's reproduction rights. No individual Fandom file-page locator, uploader/license receipt, original-image identity, byte hash, or revision hash has been verified. There are no invented file URLs.

The 2022 4K *Director's Edition* screening poster and 1985 VHS advert are **not** safely interchangeable with original 1979/1984 theatrical-release poster art. The gallery is one publisher listing, not eleven identified/rights-cleared stills. Image reuse should remain blocked even after an alt label is found.

## Status and hostile falsifiers

- All seven: `proposal_only=true`, `coverage_effect=NONE`, `admission_effect=NONE`, `public_artwork_release_effect=NONE`, `display_eligible=false`, `rights_status=PUBLIC_REUSE_NOT_VERIFIED`.
- No images, thumbnails, assets, artwork sidecar, CSP change, Explorer modification, or Pages deployment.
- **Falsifier:** a specific rights-holder reuse license for the exact image and edition could make an entry eligible after independent review; it has not been located here.
- **Falsifier:** an indexed category file title may not correspond to the expected image, original artist, or correct version; direct file-page inspection remains blocked.
- **Falsifier:** source-page changes, alternate regional editions, and editorial metadata inconsistencies can make a title/image association stale; no raw HTML snapshot digest was retained.
- **Falsifier:** a publisher photo-credit or hosting CDN domain does not prove copyright ownership, derivative-work permission, or authorization for this public repository.

## Validation

```bash
python3 proposals/films/artwork-source-locators-20261103/validate.py
python3 -m unittest discover -s proposals/films/artwork-source-locators-20261103 -p 'test_*.py' -v
```

The validator checks exact work-candidate identity, strict access/lineage correspondence, source allowlists, bounded evidence, and fail-closed display/provenance. The next prerequisite to actual thumbnails is an independently reviewed image-level rights receipt and source-local film/work link. No accepted evidence or coverage is advanced by this metadata index.
