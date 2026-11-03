# Source-local official movie poster-link locator tranche — 2026-11-03

**Role:** FILMS, isolated source-relative artwork candidate lane. **Status:** proposal only.

**Batch:** `FILMS.OFFICIAL.POSTER.LINKS.20261103.001`  
**Exact records SHA-256:** `4e222d001cce0e1ec4917c98f59e3d2a77868f084e0b381f5ff8f7d61d77993e`  
**Accepted source input:** `explorer/film-catalog.json`, SHA-256 `6513e5f96aac845727b57bd2f967170d56b95367fa95075e6919a4530bb3d6de`.

## Source retrieval and indexing

Eight independent *page reads*, but **one franchise-publisher lineage**. On 2026-11-03, the worker read the actual rendered/text-extracted official movie pages and followed each page's labeled **Poster** image link to extract its target URL. The web fetch of each `images.prismic.io` binary failed; the page's link/alt text is observed, **not its pixels or file contents**. No image bytes were saved or published.

| Source-local film directory ID | First-party page | Observation |
| --- | --- | --- |
| `film-motion-picture` | https://www.startrek.com/movies/star-trek-i-the-motion-picture | Poster-labeled target URL |
| `film-search-for-spock` | https://www.startrek.com/movies/star-trek-iii-the-search-for-spock | Poster-labeled target URL; source page says “1982,” **not adopted as release metadata** |
| `film-voyage-home` | https://www.startrek.com/movies/star-trek-iv-the-voyage-home | Poster-labeled target URL |
| `film-final-frontier` | https://www.startrek.com/movies/star-trek-v-the-final-frontier | Poster-labeled target URL |
| `film-undiscovered-country` | https://www.startrek.com/movies/star-trek-vi-the-undiscovered-country | Poster-labeled target URL |
| `film-generations` | https://www.startrek.com/movies/star-trek-generations | Poster-labeled target URL |
| `film-first-contact` | https://www.startrek.com/movies/star-trek-viii-first-contact | Poster-labeled target URL |
| `film-insurrection` | https://www.startrek.com/movies/star-trek-ix-insurrection | Poster-labeled target URL |

Prior artwork observations in `proposals/films/artwork-source-locators-20261103` pin poster **labels** for some of these films, but not these exact, labeled publisher poster-link target URLs. The OG/header-image records in `proposals/librarian/artwork-primary-asset-locators-20261103` are a different media variant and **must not be substituted** for official poster targets.

## Evidence and limitations

- Evidence class: `FIRST_PARTY_HTML_TEXT_READ` + linked poster-target URL extraction; **not** downloaded, visually inspected, or externally licensed images.
- Source-relative assertion: official pages label each linked asset as *poster art*. These are not assertions about individual pixels, original theatrical editions, or public display authorization. The `KeyArt_2023` strings are CDN filename metadata, not release-year evidence.
- Missing source snapshot: no immutable full original HTML response was retained in this batch. The first-party URL and the extracted target are pinned so an independent reviewer can re-check them, but retrieval replay and long-term permanence remain unverified.
- One source family: eight page observations are **not eight independent rights or authenticity corroborators**.
- Rights status: `HELD_NO_PUBLIC_DISPLAY_LICENSE`; `display_eligible=false` for all eight. Discovery of a CDN URL is not permission to mirror, embed, or hotlink copyrighted art. Fair-use questions remain separate; this packet neither licenses nor publishes artwork.
- Effects: **NONE** to accepted Work identity, audiovisual full-text/close-read, semantic coverage, public Explorer, artwork release, or denominators. The existing film directory links supply source-local IDs only.

## Validation gate

Run:

```bash
python proposals/films/official-poster-link-locators-20261103/validate.py
python -m unittest discover -s proposals/films/official-poster-link-locators-20261103 -p 'test_*.py' -v
python tools/validate.py
```

Validator fails on duplicate JSON keys, source SHA drift, any swapped film/page/alt/image pair, unpinned same-host image replacement, duplicate IDs, claimed display rights, invented binary reads, added schema fields, or coverage promotion. These are **offline custody checks**, not independent validation of the remote image bytes, human rights examination, or source–Work identity reconciliation.

**Next frontier:** independently re-open a sample of the exact target links, obtain source HTML/asset-byte receipts if possible, review genuine image-specific display rights, and only then consider public Explorer image release in the separately governed artwork pipeline.
