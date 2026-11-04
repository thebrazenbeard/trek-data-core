# PIC S3 first-five official guide description tranche — HELD

Date: 2026-11-04. Role: **PIC** audiovisual researcher. This is a
source-relative proposal on accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91`.
No accepted research state is altered. The earlier season-three title-only
inventory is under
`proposals/discovery/modern-paramount-season3-20261102/pic/bundle.json`
(SHA-256 `d8cd6e1edbb3c592acd5561904af323c53692d09f8945af399a2b4a3cf9d677a`).
No comparable PIC S3 first-five source-description packet was found in the
PIC research lane at selection time.

## Exact first-party retrieval

- Source: [Paramount+ *Star Trek: Picard* Season 3 episode guide](https://www.paramountplus.com/shows/star-trek-picard/episodes/3/)
- HTTP response: **200**; Date `Wed, 04 Nov 2026 21:00:09 GMT`.
- Observed UTC: `2026-11-04T21:00:09.575538+00:00`.
- Complete accessible HTML response: **272,699 bytes**, SHA-256
  `54f51850043a1073f8ac4f4e68a22b6acf2bd5b70ad416adce695c36d9e659b3`.
- Method: read-only HTTP GET, in-memory HTML parsing of **all ten** season
  cards, extracting exact title/episode/season badge, `aa-link` analytics
  ordinal, direct video route locator, raw publisher `datetime`, anchor
  line, and source-description length/SHA-256. All ten descriptions were
  encountered and fingerprinted; **five** (episodes 1–5) were read for
  original, bounded synopsis paraphrases.
- Raw publisher HTML and full publisher synopsis text were **not committed**;
  no video route, thumbnail URL, linked episode, audio, subtitle, or full
  transcript was requested.

This is an actual complete **webpage** retrieval, not an episode
`FULL_TEXT_AVAILABLE` or audiovisual `CLOSE_READ`. The five source-text
fingerprints and original paraphrases are paired in `records.json` with
HTML description lines 1488, 1516, 1544, 1572, 1600. The latter five
guide cards are inventory context only, not claimed as analyzed synopses.

| PIC S3 slot | Official card title | Description fingerprint prefix | Observation class |
| --- | --- | --- | --- |
| E01 | The Next Generation | `4c81f2fabf65` | Publisher describes |
| E02 | Disengage | `19d24fa5ae36` | Publisher describes |
| E03 | Seventeen Seconds | `e12c551a469f` | Publisher describes |
| E04 | No Win Scenario | `ff828d78204a` | Publisher describes |
| E05 | Imposters | `3f9cc910315e` | Publisher describes |

## Evidence boundary

Every local entity is a **publisher card** with no canonical Work ID.
The evidence says what the guide describes; the descriptions' fictional
events have **not** been verified from any episode or script. No entity
reconciliation has occurred. The card badge and analytics ordinal are two
fields on **one** publisher source, not independent witness streams. The
publisher's raw datetime strings are preserved without assuming broadcast
time, first streaming availability, or viewers' local date.

> **Hostile challenge:** A publisher guide can contain factual mistakes,
> editorial descriptions that simplify or foreshadow events, or stale
> availability metadata. Ten matching card labels establish only this
> webpage's observed metadata. Five original paraphrases do not turn five
> source descriptions into five episode CLOSE_READs or a canonical
> denominator.

All research, acceptance, reconciliation, Explorer release, artwork and
coverage effects remain `NONE`; original publisher description prose and
thumbnail bytes are not redistributed. This packet is intended for
source-relative validation and eventual independent custody review.

## Reproduction and next frontier

```sh
python3 source_probe.py
python3 validate.py
python3 -m unittest discover -s . -p test_validate.py
```

`source_probe.py` performs a fresh live page read (raw hash may change)
and emits only normalized metadata and fingerprints, not copyrighted
description text. `validate.py` pins this observed receipt, the ten exact
card routes and description fingerprints, the five original-analysis
records, the prior held discovery inventory, and zero protected effects.

**Exact next bounded task:** PIC S3 E06–E10 official-guide description
paraphrases from a new source-custody receipt, followed by independent
methodological review. Audiovisual source or transcript custody and
canonical Work admission remain separate unresolved gates.
