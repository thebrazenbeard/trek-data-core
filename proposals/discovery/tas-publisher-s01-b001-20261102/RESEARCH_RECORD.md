# TAS publisher Season 1: first five displayed episode entries

**Role:** TAS audiovisual worker. **Observation date:** 2026-11-02.
**Status:** `CANDIDATE_METADATA_ONLY` / publisher discovery, not an admitted Work inventory or source-content research batch.

## Publisher observation

The public [Paramount+ *Star Trek: The Animated Series* Season 1 episode guide](https://www.paramountplus.com/shows/star_trek_animated/episodes/1/) was inspected as a publisher-owned listing on 2026-11-02. Its first five **display positions** are:

| Display position | Source-local label | Publisher display title |
| --- | --- | --- |
| 1 | S1 E1 | Beyond the Farthest Star |
| 2 | S1 E2 | Yesteryear |
| 3 | S1 E3 | One of Our Planets is Missing |
| 4 | S1 E4 | The Lorelei Signal |
| 5 | S1 E5 | More Tribbles, More Troubles |

The title case `is` in entry 3 is preserved as shown by the publisher, not silently replaced with a different catalog spelling. The guide labels are **streaming presentation slots**, not evidence about production order, original network broadcast master identity, later remasters, canonical Work identity, or global continuity. Although these five labels happen to be consecutive, no outside sequence policy is inferred. The guide also displays remaining episodes, but this bounded proposal records only the first five display positions and **does not claim a complete Season 1 inventory**.

The separate [Paramount+ series landing page](https://www.paramountplus.com/shows/star_trek_animated/) provides a same-platform crosscheck for these entries; it is **not independent** corroboration. Both locators belong to `publisher:paramount`. Existing Wikidata TAS QID leads in `proposals/discovery/wikidata-mission-samples-20261102/classic/proposals/tas-qids.json` are useful external discovery candidates, but neither those IDs nor their episode labels are promoted into Work bindings here. Source lineage remains unresolved.

## Evidence, effects, and reproducibility

- `roster.csv` preserves the publisher's exact five display titles and source-local episode numbers; `observation_receipt.json` binds the observation to the original public page and contains the SHA-256 of **these local CSV bytes**, not of a publisher response.
- `bundle.json` is the deterministic output of `tools/normalize_episode_roster.py`, checked with `tools/validate_publisher_episode_roster.py`. All candidate episode entries have null canonical Work and source-binding IDs.
- `response_sha256` and `publisher_revision` are `null`; no independently captured page-body hash/version was obtained. Publisher page revisions and territorial presentation variation remain possible.
- The publisher's short promotional synopses were **not** ingested as original full-source research, and no scripts, complete transcripts, episode video, subtitle bodies, or protected media were read, indexed, or reproduced. No diegetic event, narrative interpretation, character identity, semantic assertion, or source-relative episode evidence is claimed.
- No accepted registry, reconciliation, Work, Source, coverage ledger, denominator, or public deployment was changed. `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, `STRUCTURALLY_INDEXED`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, `ENTITY_LINKED`, `CROSS_REFERENCED`, and `AUDITED` remain unasserted.

**Accepted baseline:** This research began at accepted `main@c7a14ddb62dfa45d5d01855952d9e562c1af21de`, not at a proposed branch. The accepted nonfixture episode Work and full-source research frontier was not advanced by this discovery-only proposal.

## Validation

```sh
python3 tools/validate_publisher_episode_roster.py --input proposals/discovery/tas-publisher-s01-b001-20261102/bundle.json
python3 -m unittest discover -s tests -p 'test_tas_publisher_batch.py' -v
```

**Exact next frontier:** Librarian source/edition and Work admission decisions, then permissioned access to and actual reading/processing of complete TAS primary source representations before a proper TAS episode evidence/assertion batch. Source and ordering ambiguities must survive admission rather than being erased by the publisher's display sequence.
