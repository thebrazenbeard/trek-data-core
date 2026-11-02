# Official Star Trek film discovery — 2026-11-02

Proposal status: **UNADMITTED / METADATA DISCOVERY ONLY**. This batch does not create a canonical Work, Source, evidence-bearing Source–Work binding, accepted Briefing, continuity assertion, season denominator, or audited coverage claim.

## Source observations

- Source directory: [Star Trek Series & Movies](https://www.startrek.com/series-and-movies), thirteen film links observed on 2026-11-02.
- Additional distinct film: [*Star Trek: Section 31*](https://www.startrek.com/news/star-trek-section-31-premieres-january-24), separately identified as an original streaming movie by the same publisher. It was absent from the thirteen-film directory at observation.
- Publisher lineage: `publisher:startrek.com`. The linked film pages and publisher announcements are **not independent corroboration** of one another.
- No raw page bytes, edition-stable snapshots, source revision identifiers, film audiovisual content, transcripts, frame captures or license clearances are attested in this batch. `observed_on` identifies this research session's observation, not authentication of original publication dates.

## Scope and unresolved questions

The fourteen entries are *identified candidates*, not a proven exhaustive film denominator. Distinct formats (cinematic features and streaming original) remain typed separately. Titles are display labels; they are not authoritative global identity decisions. `Star Trek (2009)` uses a year qualifier for display disambiguation.

The publisher's [*Star Trek III: The Search for Spock* detail page](https://www.startrek.com/movies/star-trek-iii-the-search-for-spock) currently displays `1982 • PG` even though the publisher's own [history video](https://www.startrek.com/videos/trek-history-star-trek-iii-the-search-for-spock) and the independent [AFI catalog](https://catalog.afi.com/Film/57202-STAR-TREK-III-THE-SEARCH-FOR-SPOCK) identify a June 1, 1984 theatrical opening. The generated discovery catalog intentionally includes **no release-year field** until a separately governed fact record can preserve both the error and its resolution.

## Build

From repository root:

```bash
python3 tools/build_film_catalog.py
python3 tools/build_film_catalog.py --check
python3 -m unittest tests.test_film_catalog -v
```

The generated `explorer/film-catalog.json` remains a strictly segregated *discovery view*; it cannot be consumed by the admitted-only `explorer/index.json` compiler or advance coverage.
