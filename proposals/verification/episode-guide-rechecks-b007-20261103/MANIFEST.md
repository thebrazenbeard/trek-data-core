# B007-VOY/ENT: 16 official publisher episode-guide cards, with draft synopses

**LIBRARIAN source-relative proposal only** · source observation at accepted `main@3c0b37564123166bf38bcfa66f018abc4d5c9996` · observed 2026-11-03 UTC.

This bounded tranche covers exactly `lead:0083`–`lead:0098` from the existing 1,214-row Wikidata-derived **discovery-only** catalog: seven *Voyager* candidates (`0083`–`0089`) and nine *Enterprise* candidates (`0090`–`0098`). None is an admitted Work or full-source read. Earlier B001–B006 lanes remain unaffected.

## Actual first-party source reads

The title, guide-slot and short-description cards were individually examined in Paramount+'s rendered U.S. episode guides:

| Publisher guide | Cards inspected |
| --- | ---: |
| [*Voyager* S3](https://www.paramountplus.com/shows/star_trek_voyager/episodes/3/) | 2 |
| [*Voyager* S4](https://www.paramountplus.com/shows/star_trek_voyager/episodes/4/) | 1 |
| [*Voyager* S5](https://www.paramountplus.com/shows/star_trek_voyager/episodes/5/) | 2 |
| [*Voyager* S7](https://www.paramountplus.com/shows/star_trek_voyager/episodes/7/) | 2 |
| [*Enterprise* S1](https://www.paramountplus.com/shows/enterprise/episodes/1/) | 4 |
| [*Enterprise* S2](https://www.paramountplus.com/shows/enterprise/episodes/2/) | 3 |
| [*Enterprise* S3](https://www.paramountplus.com/shows/enterprise/episodes/3/) | 2 |

`observations.json` retains exactly the first-party rendered card titles, season/episode slots, read-state and **original source-grounded synopsis drafts**. `records.json` is a deterministic, source-local derivative, linking each Wikidata QID discovery locator to its separately identified Paramount publisher guide card. The draft synopses are **held for human/editorial approval** and are neither incorporated into Explorer nor marked as public, canonical or verified narrative evidence. They are brief new prose, not reproductions of Paramount descriptions.

The actual audiovisual episodes, scripts and full transcripts were **not read**. Raw HTTP/page bytes were not retained or hashed. The cards establish only publisher guide metadata and a narrow basis for drafting; they do not establish full-text or CLOSE_READ coverage. Wikidata and Paramount are distinct provenance lineages, but a Paramount TV guide is still one corporate publisher family, not seven independent witnesses. No artwork was ingested.

## Held title and identity variants

| Lead | Wikidata-derived title | Paramount card title/slot | Resolution |
| --- | --- | --- | --- |
| `lead:0087` | *Basics, Part II* | *Basics, Part 2*, S3E1 | `PART_NUMERAL_STYLE_UNRESOLVED` |
| `lead:0088` | *Future's End, Part II* | *Future's End, Part 2*, S3E9 | `PART_NUMERAL_STYLE_UNRESOLVED` |
| `lead:0089` | *Year of Hell, Part II* | *Year Of Hell, Part 2*, S4E9 | `PART_NUMERAL_STYLE_UNRESOLVED` (also capitalization) |

The first-party cards are real observations, but the differing title formats and potential multipart scope are not resolved merely by string normalization. These three rows have `original_synopsis_draft: null` and must receive an explicit reviewed alias/scope decision before identity binding or public synopsis consideration.

> **Hostile challenge:** A card blurb is not the episode. Even when a source-local title matches literally and a draft accurately reflects a short guide description, it may omit competing perspectives, alternate cuts or discontinuities. It cannot support a neutral close reading, arbitrary semantic tag, character continuity assertion or canonical Work identity. If the webpage's layout or card-to-description association changes, the draft requires rechecking, not automatic admission.

## Accounting and reproducibility

- 16 publisher card metadata observations: **13 literal title matches**, **3 held variants**.
- 13 original synopsis drafts pending human/editorial review: **0 approved or public**.
- Raw publisher HTML pinned: **0**. Full episode/source texts read: **0**. Governed Source/Work admissions or coverage increments: **0**.
- No changes to Explorer's accepted catalog, source counts or reconciliation registry.
- Generate with `python tools/build_episode_guide_rechecks_b007.py`; verify with `python tools/build_episode_guide_rechecks_b007.py --check` and `python -m unittest tests.test_episode_guide_rechecks_b007 -v`.

The generator pins the catalog SHA256, lead range, card titles/slots, draft review hold and protected-effect constraints. The durable source-of-truth remains accepted research evidence, not publisher blurb-derived editorial copy.
