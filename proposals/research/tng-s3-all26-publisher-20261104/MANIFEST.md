# TNG Season 3 B016 — complete publisher guide card read (HELD)

**Role:** TNG series researcher. **Date:** 2026-11-04 UTC. **Accepted baseline:** `main@3028765359001b90bc3e6b5c1835ee283b326e91`.

**Accessible primary surface read:** [Official Paramount+ TNG Season 3 guide](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/3/) in full rendered web-reader form: **26 displayed episode cards**, every episode title, S3 ordinal and complete promotional description. All 26 source-local slots in the accepted-main Season 3 CSV and discovery catalog were checked one by one against those reader cards. **26 original one-sentence editorial paraphrases**, exact title/ordinal/URL card locators, named or labeled literal mentions, independently computed trimmed UTF-8/NFC description SHA-256 fingerprints, and explicit epistemic anomalies were recorded in `observations.json` and deterministically compiled to `records.json`.

This is **source-relative publisher metadata enrichment**, not episode viewing, transcript close reading, canonical Work adjudication, verified episode-level interpretation, or public synopsis publication. The publisher is a **single corporate-source family**, regardless of how many cards it displays. No copyrighted description prose, episode scripts, videos, or artwork were copied into this repository.

## Complete processed slot inventory

| S3 card | Existing source-local ID | Official publisher title | Epistemic framing flag |
| ---: | --- | --- | --- |
| 1 | `legacy:s3:tng:000` | *Evolution* | `NONE` |
| 2 | `legacy:s3:tng:001` | *The Ensigns of Command* | `NONE` |
| 3 | `legacy:s3:tng:002` | *The Survivors* | `PUBLISHER_SURVIVOR_COUNT_UNVERIFIED` |
| 4 | `legacy:s3:tng:003` | *Who Watches the Watchers* | `ATTRIBUTED_BELIEF_NOT_DIVINITY` |
| 5 | `legacy:s3:tng:004` | *The Bonding* | `UNNAMED_DECEASED_PERSON_AND_CHILD` |
| 6 | `legacy:s3:tng:005` | *Booby Trap* | `NONE` |
| 7 | `legacy:s3:tng:006` | *The Enemy* | `NONE` |
| 8 | `legacy:s3:tng:007` | *The Price* | `UNNAMED_DELEGATE_AND_VALUE_JUDGMENT` |
| 9 | `legacy:s3:tng:008` | *The Vengeance Factor* | `UNNAMED_FACTIONS_AND_ASSASSIN` |
| 10 | `legacy:s3:tng:009` | *The Defector* | `UNNAMED_DEFECTOR_AND_WAR_PROSPECT` |
| 11 | `legacy:s3:tng:010` | *The Hunted* | `CAUSAL_MIND_CONTROL_CLAIM` |
| 12 | `legacy:s3:tng:011` | *The High Ground* | `POLITICAL_GROUP_LABEL` |
| 13 | `legacy:s3:tng:012` | *Deja Q* | `NONE` |
| 14 | `legacy:s3:tng:013` | *A Matter of Perspective* | `ACCUSATION_NOT_GUILT` |
| 15 | `legacy:s3:tng:014` | *Yesterday's Enterprise* | `ALTERNATE_HISTORY_IDENTITY_UNRESOLVED` |
| 16 | `legacy:s3:tng:015` | *The Offspring* | `PARENTAL_RELATION_NOT_LEGAL_STATUS` |
| 17 | `legacy:s3:tng:016` | *Sins of the Father* | `UNNAMED_BROTHER` |
| 18 | `legacy:s3:tng:017` | *Allegiance* | `REPLACEMENT_IDENTITY_UNRESOLVED` |
| 19 | `legacy:s3:tng:018` | *Captain's Holiday* | `FUTURE_ORIGIN_CLAIM_UNVERIFIED` |
| 20 | `legacy:s3:tng:019` | *Tin Man* | `UNNAMED_LIFE_FORM` |
| 21 | `legacy:s3:tng:020` | *Hollow Pursuits* | `UNNAMED_ENGINEER_HOLODECK_WORLD` |
| 22 | `legacy:s3:tng:021` | *The Most Toys* | `PRESUMED_DEATH_NOT_VERIFIED_DEATH` |
| 23 | `legacy:s3:tng:022` | *Sarek* | `TITLE_NAME_NOT_PUBLISHER_DESCRIPTION_ASSERTION` |
| 24 | `legacy:s3:tng:023` | *Ménage à Troi* | `TROI_DEANNA_RELATION_NOT_GLOBALLY_LINKED` |
| 25 | `legacy:s3:tng:024` | *Transfigurations* | `UNNAMED_RESCUED_HUMANOID` |
| 26 | `legacy:s3:tng:025` | *The Best Of Both Worlds, Part 1* | `EVALUATIVE_EVIL_LABEL` |

These flags are research cautions, not automatically accepted claims. A `NONE` flag only means there was no additional special caution noted beyond the universal publisher-description evidence frame.

## Exact source custody separation

- The **current** full-guide observations came from a rendered web reader. Its individual description SHA-256 values fingerprint that reader's trimmed NFC-normalized UTF-8 text. They are **not** authenticating hashes of publisher HTML bytes, nor cryptographically signed studio versions.
- An **earlier accepted discovery proposal** (`proposals/discovery/legacy-paramount-season3-20261102/index.json`) records a local raw page capture on **2026-11-02**, **317,083 bytes**, SHA-256 `3b0492e8dac432bf82334a9bc27baf0a7718c1fc34d8ee4ac73a9b49ac714244`. That older receipt is lineage context **only**; these new reader observations did not retrieve or re-hash those historical raw HTTP bytes. `fresh_raw_html_custody=UNAVAILABLE` and `fresh_raw_html_sha256=null`.
- Accepted source-local listing CSV `tng.csv` SHA-256 `b7d9718f20c9c74d0552483b99accb66c48d1d62fd22864febf14ae0f5a6b514`. Accepted source-local bundle SHA-256 `cd38dbdd2095585736a25b4a3821d80ad7f3150e31914330e936b0c5e224ebf4`. Accepted public discovery directory SHA-256 `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`.
- Prior historical TNG S3 close-read-labeled PRs **#84, #86, #87, #88** are **closed without merge**. Their labels do not establish accepted episode close reads; this fresh publisher-card proposal neither incorporates nor validates their assertions.
- Draft TNG Season 2 proposals [#538](https://github.com/thebrazenbeard/trek-data-core/pull/538) and [#551](https://github.com/thebrazenbeard/trek-data-core/pull/551) remain separate, unmerged proposal siblings.

## Specific falsifiers and unresolved ontology

> **Hostile challenge:** A source excerpt saying that inhabitants *believe* Picard divine (S3E4), someone *suspects* Riker of murder (S3E14), Data *becomes a father* (S3E16), history *changes* (S3E15), or Picard is *replaced* (S3E18) cannot alone prove divinity, guilt, legal parenthood, a globally reconciled timeline, or the identity of any impersonator. Each is held as the publisher's promotional framing.

> **Hostile challenge:** S3E22 says the crew leaves Data for dead. That is a report about a presumption, not direct proof of his death. S3E23's title *Sarek* and description's unnamed Vulcan ambassador cannot be merged into an identified character solely by title adjacency. S3E26 uses the publisher's evaluative label for the Borg; value judgments are not accepted analytic predicates.

- The Riker/Troi/Deanna/Lwaxana relationship wording in S3E24 stays source-relative. No source-local mention implies a global identity key or accepted family ontology.
- Unnamed delegates, assassins, deceased persons, aliens, humanoids and family members remain unnamed where the publisher guide omits their names; no familiar franchise knowledge is inserted.
- The ordinal is a **publisher's streaming Season 3 listing observation**, not verified production order or edition equivalence. Source-family independence is **one**; downstream derivative datasets are not new witnesses.
- The contiguous full-season selection was driven by guide order and processing availability, not Patrick's preferences or thematic salience.

**Admission/coverage effects:** No newly authenticated audiovisual Source→Work binding; no new global Works; no held synopsis publication clearance; no episode/script CLOSE_READ; no entity-linking, cross-work reconciliation, accepted evidence/assertion batch, cover art, coverage ledger event or denominator change. Every record remains `HELD_SOURCE_LOCAL_PUBLISHER_METADATA`. The Director admission gate in [issue #23](https://github.com/thebrazenbeard/trek-data-core/issues/23) remains closed.

## Reproducibility and next frontier

```bash
python3 proposals/research/tng-s3-all26-publisher-20261104/validate.py --check
python3 -m unittest discover -s proposals/research/tng-s3-all26-publisher-20261104 -p 'test_*.py' -v
python3 -O -m unittest discover -s proposals/research/tng-s3-all26-publisher-20261104 -p 'test_*.py' -q
python3 tools/validate.py
```

The validator pins prior accepted-main source bundle/CSV/discovery/index bytes and this full 26-row reader observation artifact by SHA-256. It rejects wrong titles/ordinals, row IDs, reader-fingerprints, incomplete batches, altered issuer/independence/custody effects, asserted global identity, changed original synopses or suppressed epistemic cautions. The derivative projection is deterministic from these bytes, with no semantic reconciliation in the compiler.

**Exact next TNG lane frontier:** Official Season 4 publisher-card enrichment, or a truly rights-valid, complete episode/script custody proposal for a small audited close-read pilot, only after issue #23's independent acceptance gates.
