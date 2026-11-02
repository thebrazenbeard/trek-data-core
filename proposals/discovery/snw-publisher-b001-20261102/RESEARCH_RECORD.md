# Strange New Worlds — first five publisher-listed episodes (proposal)

Research date: **2026-11-02**. Mission: `snw` / *Star Trek: Strange New Worlds*.

## Question and method

Can the first five Season 1 episode identities be reconciled against original franchise publisher material, while keeping metadata discovery separate from watching an episode or accepting continuity evidence?

I compared the [Paramount+ Season 1 episode guide](https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/1/) (season/episode slot and English title as indexed by the web search provider) against episode-numbered primary editorial pages from [StarTrek.com](https://www.startrek.com/). The direct web-reader fetch of the Paramount guide redirected to its German localized version, which still showed S1 episodes 1–5, in the same sequence, under translated headings. This is a live page observation, **not a retained publisher-byte snapshot**. Both sites belong to the Paramount/Star Trek publishing family; they share **one** independence group and do not count as two independent publishers.

| Slot | Short English title | Official editorial title/ordinal confirmation | Wikidata lead already in repository |
| --- | --- | --- | --- |
| S01E01 | Strange New Worlds | [SNW 101](https://www.startrek.com/news/recap-star-trek-strange-new-worlds-strange-new-worlds) | No exact QID asserted here |
| S01E02 | Children of the Comet | [SNW 102](https://www.startrek.com/news/recap-star-trek-strange-new-worlds-children-of-the-comet) | `Q111832729` |
| S01E03 | Ghosts of Illyria | [SNW 103](https://www.startrek.com/news/recap-star-trek-strange-new-worlds-ghosts-of-illyria) | `Q111832736` |
| S01E04 | Memento Mori | [SNW 104](https://www.startrek.com/news/recap-star-trek-strange-new-worlds-memento-mori) | `Q111832741` |
| S01E05 | Spock Amok | [SNW 105](https://www.startrek.com/news/recap-star-trek-strange-new-worlds-spock-amok) | `Q111832746` |

The QIDs are crosswalk *leads* already present in `proposals/discovery/wikidata-mission-samples-20261102/nextgen/proposals/snw.json`, not freshly verified Work identities. No canonical Work identifier is assigned.

## Evidence class and caveats

- **RETRIEVED, publisher metadata:** The Paramount+ episode guide showed S1 episode slots 1–5 and short titles in web search; the direct opened page returned a region-localized German page, also enumerating S1 episodes 1–5.
- **RETRIEVED, same corporate publisher:** StarTrek.com episode recap headings independently within that publisher family identify installment numbers 101–105 and the five English titles. Editorial recap articles are *not* direct observation of underlying audiovisual bytes.
- **SOURCE-IDENTITY UNCERTAINTY:** A separately indexed Paramount+ individual-episode URL displayed a May 11 date for E2 while the season guide displayed May 12. This batch deliberately omits release dates until a separate version/time-zone reconciliation.
- **NO CONTENT INSPECTION:** No episode stream, script, subtitle, book or transcript was obtained, watched, read or committed. No response SHA-256 was computed, since publisher HTTP bytes were not retained.
- **NO ACCEPTANCE:** `observed_slots.csv` is an original metadata-only observation list. Its SHA-256 in `observation.json` binds this local CSV, not the publisher page. `bundle.json` is an offline proposal only: no accepted Source, Work, Evidence, Assertion, Source↔Work binding, coverage event or denominator effect. No inference that five selected slots constitute a complete season.

## Reproduce and review

```sh
python3 tools/normalize_episode_roster.py --csv proposals/discovery/snw-publisher-b001-20261102/observed_slots.csv --receipt proposals/discovery/snw-publisher-b001-20261102/observation.json --output proposals/discovery/snw-publisher-b001-20261102/bundle.json --check
python3 tools/validate_publisher_episode_roster.py --input proposals/discovery/snw-publisher-b001-20261102/bundle.json
```

Next gate: an independent Librarian/source reviewer must reconcile publisher ordering and source identity, then make a **separate** acceptance decision. This proposed observation cannot satisfy source-content or continuity-admission gates.
