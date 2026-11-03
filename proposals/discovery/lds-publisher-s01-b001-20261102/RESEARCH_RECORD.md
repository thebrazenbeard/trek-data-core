# Lower Decks Season 1 — first five publisher display entries

**Worker:** LD / *Star Trek: Lower Decks* audiovisual lane. **Observed:** 2026-11-02. **Accepted `main` reference:** `c7a14ddb62dfa45d5d01855952d9e562c1af21de`.

**State:** `CANDIDATE_METADATA_ONLY`, `DISCOVERED` listing. This is **not** an episode-content research batch, accepted Work registry, or an admitted Source→Work binding.

## Source-local observations

The [Paramount+ Season 1 episode guide](https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/1/) visibly lists the following first five entries in order. I directly inspected its text via the public web-reader view on 2026-11-02. The [publisher show page](https://www.paramountplus.com/shows/star-trek-lower-decks/) independently displays corresponding metadata within the **same** corporate publisher family; these two Paramount+ pages must **not** be counted as independent corroborating sources.

| Display position | Publisher slot | Title |
| --- | --- | --- |
| 1 | Season 1, episode 1 | Second Contact |
| 2 | Season 1, episode 2 | Envoys |
| 3 | Season 1, episode 3 | Temporal Edict |
| 4 | Season 1, episode 4 | Moist Vessel |
| 5 | Season 1, episode 5 | Cupid's Errant Arrow |

These five observed display entries are **not** a season-completeness finding. The guide presently shows additional entries; this is an intentionally bounded five-entry tranche. The publisher's local ordinal is not a canonical cross-platform Work identity. No asserted local person/ship/entity identities or semantic claims are created from synopsis text.

## Provenance and limits

- `roster.csv` contains the five observed slot/title pairs, without publisher prose. `observation_receipt.json` records original locators and the SHA-256 of **our CSV bytes**. It is **not** a hash of the publisher's HTML response.
- `bundle.json` is a deterministic candidate-only output of `tools/normalize_episode_roster.py`; it makes no canonical Work, Source, source-binding, coverage, denominator, projection, or acceptance effect.
- No full audiovisual representation, complete script/transcript, captions, audio, or primary episode content was acquired or close-read. `FULL_TEXT_AVAILABLE`, `STRUCTURALLY_INDEXED`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, `ENTITY_LINKED`, `CROSS_REFERENCED`, and `AUDITED` are **not claimed**.
- Public web-reader presentation may differ by country, entitlement, or future publisher revision. The page is treated as one mutable upstream source family, not an immutable response-byte witness.
- No copyrighted episode content or substantial source text is included.

## Reproduce and validate

```sh
python3 -B tools/normalize_episode_roster.py --csv proposals/discovery/lds-publisher-s01-b001-20261102/roster.csv --receipt proposals/discovery/lds-publisher-s01-b001-20261102/observation_receipt.json --output proposals/discovery/lds-publisher-s01-b001-20261102/bundle.json --check
python3 -B tools/validate_publisher_episode_roster.py --input proposals/discovery/lds-publisher-s01-b001-20261102/bundle.json
python3 -B -m unittest discover -s tests -p 'test_lds_publisher_batch.py' -v
```

**Next evidence frontier:** Librarian ownership of Source and Work variant/custody verification; then lawful processing of a complete primary episode representation in this lane before generating local entities, source-relative evidence, and neutral assertions. Do not promote this metadata-only roster into an admitted episode batch.
