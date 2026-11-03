# AFI film theatrical-release metadata — source-local proposal (2026-11-03 UTC)

**Status: PROPOSAL ONLY.** Five AFI Catalog release-date field observations from the first five *Star Trek* motion pictures. These are bibliographic/catalog assertions about theatrical-release dates, not observations of the films' contents. No audiovisual film, complete screenplay, transcript, artwork binary, or source-page snapshot was obtained or evaluated.

| AFI Catalog ID | Candidate film discovery ID | AFI lists theatrical release date |
| --- | --- | --- |
| [53863](https://catalog.afi.com/Catalog/MovieDetails/53863) | `film-motion-picture` | 7 December 1979 |
| [67066](https://catalog.afi.com/Catalog/MovieDetails/67066) | `film-wrath-of-khan` | 4 June 1982 |
| [57202](https://catalog.afi.com/Film/57202-STAR-TREK-III-THE-SEARCH-FOR-SPOCK) | `film-search-for-spock` | 1 June 1984 |
| [57482](https://catalog.afi.com/Catalog/MovieDetails/57482) | `film-voyage-home` | 26 November 1986 |
| [58297](https://catalog.afi.com/Catalog/MovieDetails/58297) | `film-final-frontier` | 9 June 1989 |

The target IDs are *candidate crosswalk references* to the accepted film discovery manifest at `proposals/librarian/films-official-index-20261102/bundle.json`. They do not create governed Work IDs, Source–Work bindings, or reconciled film identities. Each observation preserves a local catalog-entity identifier and the catalog's own sourced release-date assertion.

## Known contradiction

The franchise publisher's [*The Search for Spock* detail page](https://www.startrek.com/movies/star-trek-iii-the-search-for-spock) labels that film **1982**. AFI Catalog [57202](https://catalog.afi.com/Film/57202-STAR-TREK-III-THE-SEARCH-FOR-SPOCK) lists a **1 June 1984** release. The existing official-film discovery manifest already flags this inconsistency. Here the observations remain attributed to their distinct sources; this batch does **not** overwrite the catalog year, declare a reconciled release fact, or treat AFI's summary as proof of all historical details.

## Provenance and rights boundaries

- Source access: relevant AFI Catalog page sections surfaced through web retrieval and search on 2026-11-03 UTC. No durable raw HTML or SHA-256 is held, hence `raw_page_sha256: null` in every record. No claim of source edition immutability.
- Source family: AFI Catalog of Feature Films, five entries belonging to one catalog lineage. Its compiled history cites newspapers and trade publications; those underlying materials have **not** been independently read. A publisher directory and AFI entry are not automatically two independent primary-film witnesses.
- Film audiovisual research coverage: **none**. This metadata tranche has `coverage_effect=NONE`, `admission_effect=NONE`; no `SOURCE_BOUND` or `CLOSE_READ` upgrade.
- Artwork: AFI page image labels, film posters, franchise marks, and film stills have no verified public-display reuse permission in this batch. No image URL, binary, thumbnail sidecar, CSP, or Pages changes.
- Release scope: original theatrical listing only, not remasters, director's cuts, international premieres, television exhibition, or streaming releases.

## Deterministic validation

```bash
python3 proposals/films/afi-theatrical-release-20261103/validate.py
python3 -m unittest proposals/films/afi-theatrical-release-20261103/test_validate.py -v
```

The validator requires one-to-one local identifiers, AFI page IDs, a real proposal-only source-local metadata evidence→assertion link, valid Gregorian dates and candidate references matching the already accepted discovery manifest. It rejects any fabricated rights release, admitted coverage, or global identity status.

**Next frontier:** Independently capture date-field source-page snapshots with immutable hashes, check underlying archival materials for the *Search for Spock* discrepancy, and seek explicit release review before any accepted Work binding or public display.
