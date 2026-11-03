# B004 — sixteen source-local leads / seventeen official episode guide cards

This bounded source-verification proposal covers `lead:0035` through `lead:0050` from accepted `explorer/discovery-catalog.json` (1,214 source-local discovery observations; exact catalog bytes SHA-256 preserved in generated `records.json`). Observed `2026-11-03` UTC. **No governed Works, Evidence, Assertions, coverage, full-source viewing, or synopsis publication.**

## Official primary cards actually read

- [Paramount+ TAS Season 1](https://www.paramountplus.com/shows/star_trek_animated/episodes/1/) and [Season 2](https://www.paramountplus.com/shows/star_trek_animated/episodes/2/) — five animated episode cards.
- [Paramount+ TNG Season 1](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/1/), [Season 4](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/4/), [Season 5](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/5/), and [Season 6](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/6/) — nine single-card observations plus the two-part `Chain Of Command` title candidates.
- [Paramount+ Deep Space Nine Season 4](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/4/) — `Crossfire` S4E13.

Rendered web text **actually displayed individual headings, season/episode ordinals and publisher brief descriptions**; raw canonical HTML bytes were not available, so no `sha256` of the source web body is invented. The source-local Wikidata URI remains distinct from the official Paramount card locator. All guide pages belong to one Paramount corporate publisher family, not seven independent corroborating source families or seventeen independent witness families.

| Discovery row | Publisher guide card(s) | Resolution |
| --- | --- | --- |
| `lead:0035` TAS | The Pirates of Orion — S2E1 | Exact title |
| `lead:0036` TAS | The Practical Joker — S2E3 | Exact title |
| `lead:0037` TAS | The Survivor — S1E6 | Exact title |
| `lead:0038` TAS | The Terratin Incident — S1E11 | Exact title |
| `lead:0039` TAS | More Tribbles, More Troubles — S1E5 | Exact title |
| `lead:0040` TNG | The Neutral Zone — S1E26 | Exact title |
| `lead:0041` TNG | Hide and "Q" — S1E10 | **Unresolved punctuation variant**: source-local has `Hide and Q` |
| `lead:0042` TNG | Chain Of Command - Part 1 — S6E10 **and** Part 2 — S6E11 | **Unresolved multipart Work identity**: source-local only says `Chain of Command` |
| `lead:0043` TNG | Skin of Evil — S1E23 | Exact title |
| `lead:0044` TNG | Rightful Heir — S6E23 | Exact title |
| `lead:0045` TNG | Brothers — S4E3 | Exact title |
| `lead:0046` TNG | Half a Life — S4E22 | Exact title |
| `lead:0047` TNG | Silicon Avatar — S5E4 | Exact title |
| `lead:0048` TNG | New Ground — S5E10 | Exact title |
| `lead:0049` TNG | Hero Worship — S5E11 | Exact title |
| `lead:0050` DS9 | Crossfire — S4E13 | Exact title |

## Strict result and synopsis boundaries

- **16** source-local row cases, **17** distinct publisher guide cards actually consulted, **14** exact row-title matches, **one** held title punctuation variant, **one** held multipart identity case.
- **15** original single-sentence synopsis **drafts** based only on the corresponding official brief descriptions, human-review **PENDING** and not publicly approved. For `lead:0042` the source-local title could mean either a two-part story grouping or an individual Work, so **no synopsis is fabricated**; the original synopsis field is `null` with `WITHHELD_MULTIPART_WORK_IDENTITY_UNRESOLVED`.
- Source chapter/episode identity is not globally reconciled by this batch. `source_local_discovery_state:CATALOGUED_METADATA_ONLY`, `governed_research_coverage_state:NOT_ADMITTED`, effects `NONE` on all rows.
- No original Paramount description is reproduced verbatim, no full audiovisual episode watched or transcript ingested, and no image/media files published.

## Deterministic qualification

```bash
python3 tools/build_episode_guide_rechecks_b004.py --check
python3 -m unittest tests/test_episode_guide_rechecks_b004.py
```

The compiler refuses false exact-title matches, replacing ambiguous two-part candidates with one fabricated episode, adding a composite synopsis, duplicate slots, cross-series contamination, unauthorized source byte custody claims or coverage promotions. It checks each source-local row against the accepted catalog and regenerates `records.json` byte-for-byte. It **cannot** independently re-fetch or authenticate the web pages or algorithmically prove prose originality; review against the actual publisher pages is required before PR acceptance.

Next bounded source-read frontier: `lead:0051` onward after a separately reviewed acceptance. Existing `Chain of Command` remains unresolved; reconciliation belongs to an explicit versioned decision, not this deterministic compiler.
