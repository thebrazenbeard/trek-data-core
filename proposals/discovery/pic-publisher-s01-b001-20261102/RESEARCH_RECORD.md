# Picard publisher Season 1: first five displayed entries

**Role:** PIC audiovisual worker. **Observed:** 2026-11-02. **Status:** `CANDIDATE_METADATA_ONLY` (`DISCOVERED`, not an accepted research batch or primary episode-content witness).

## Publisher page observation

The public [Paramount+ Picard Season 1 episode guide](https://www.paramountplus.com/shows/star-trek-picard/episodes/1/) opened through a web reader and redirected to the [Australia-localized page](https://www.paramountplus.com/au/shows/star-trek-picard/episodes/1/). Its Season 1 listing showed these first five display positions, each with an explicit season/episode label:

| Publisher display position | Publisher label | Observed publisher title |
| --- | --- | --- |
| 1 | S1 E1 | Remembrance |
| 2 | S1 E2 | Maps and Legends |
| 3 | S1 E3 | The End Is The Beginning |
| 4 | S1 E4 | Absolute Candor |
| 5 | S1 E5 | Stardust City Rag |

The page also displayed later episodes, but only the five above were transcribed into this bounded metadata tranche. These are **publisher-local display labels**, not globally reconciled episode identities. No inference from a review synopsis, memory, or external database is used as source evidence.

### Regional/title variation hold

The [United Kingdom Paramount+ Season 1 page](https://www.intl.paramountplus.com/gb/shows/star-trek-picard/episodes/1/) also displays the first five labels and titles, including `The End Is The Beginning` at E3. Search-result excerpts of the nonlocalized/US listing render this title `The End is the Beginning` (lowercase *is* and *the*). The AU direct page title is retained verbatim in `roster.csv`. Regional rendering and capitalization do **not** justify silently normalizing a Work title or proposing two distinct Works. Both pages are from the **same Paramount corporate source family**, not independent corroboration.

## Reproduction and bounded evidence

- `roster.csv` contains only titles and ordinal labels; `observation_receipt.json` records source-locator and the SHA-256 of the **local CSV**. This does **not** assert a hash of publisher page bytes, publisher version, licensed media, or a preserved original webpage snapshot.
- `bundle.json` is produced by `tools/normalize_episode_roster.py`, then checked by `tools/validate_publisher_episode_roster.py` and an offline regression. It has no accepted Work or Source-to-Work binding, no covered Briefings, and no change to any denominator.
- The website episode guide is not the episode itself. Neither the complete audiovisual episode nor captions/transcript were inspected. No `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, `STRUCTURALLY_INDEXED`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, `ENTITY_LINKED`, `CROSS_REFERENCED`, or `AUDITED` state has been earned.
- Excerpts from the publisher descriptions and copyrighted episode content are intentionally omitted. Exact original page bytes and content hash are unknown; the site's content can change.

**Accepted baseline:** At `main@c7a14ddb62dfa45d5d01855952d9e562c1af21de`, no nonfixture episode Works were accepted by `tools/check_episode_pilot_readiness.py`. This proposal makes no claim of acceptance or full Season 1 coverage.

Offline checks:

```sh
python3 -B tools/normalize_episode_roster.py --csv proposals/discovery/pic-publisher-s01-b001-20261102/roster.csv --receipt proposals/discovery/pic-publisher-s01-b001-20261102/observation_receipt.json --output proposals/discovery/pic-publisher-s01-b001-20261102/bundle.json --check
python3 -B tools/validate_publisher_episode_roster.py --input proposals/discovery/pic-publisher-s01-b001-20261102/bundle.json
python3 -B -m unittest discover -s tests -p 'test_pic_publisher_batch.py' -v
```

**Next frontier:** Librarian-led source custody, independently reviewable admission and scoped Work identity; then genuine primary episode processing and source-relative evidence. Title casing remains observed regional metadata until reviewed reconciliation.
