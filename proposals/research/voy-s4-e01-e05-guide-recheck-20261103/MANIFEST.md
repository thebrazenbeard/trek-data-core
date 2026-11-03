# VOY S4 E01–E05 — Publisher guide source-card recheck (HELD)

**Role:** VOY series source worker

**Base accepted `main` at worker start:** `aebf9e8a69ab44919f2d89ab60dd1e824e05a807`

**Observation:** 2026-11-03 UTC

**Effect:** proposal only; zero global Works, source-bound Works, additional episode discoveries, close reads, accepted assertions, or coverage changes.

## Bounded source processing

The source actually inspected was the rendered [official Paramount+ Star Trek: Voyager Season 4 episode guide](https://www.paramountplus.com/shows/star_trek_voyager/episodes/4/). Its first five visible cards display, in order:

| Publisher card locator | Source-relative title | Research result |
|---|---|---|
| Season 4, S4 E1 | Scorpion, Part 2 | Local listing evidence + original synopsis draft held |
| Season 4, S4 E2 | The Gift | Local listing evidence + original synopsis draft held |
| Season 4, S4 E3 | Day Of Honor | Local listing evidence + original synopsis draft held |
| Season 4, S4 E4 | Nemesis | Local listing evidence + original synopsis draft held |
| Season 4, S4 E5 | Revulsion | Local listing evidence + original synopsis draft held |

The previous accepted discovery receipt already listed these same five headings in `proposals/discovery/publisher-season4-20261102/voy.csv` (26 total publisher slots). This tranche adds **five individually coded source-relative evidence records and five brief original synopsis review candidates**; it does **not** create five additional episode discoveries. The validator pins the old CSV SHA-256 (`e9e8ac0cae8a30ac1c71b0c36b1d0f28b9ff9cf25d5f2a8d2875fad2e34e598e`) and compares every candidate title/ordinal with those existing local discovery rows. An earlier publisher discovery index documents a body SHA-256, but **this session did not capture fresh raw source bytes**; it only inspected the current rendered guide, so `new_raw_source_sha256` is null.

The guide supplies very short promotional descriptions. Synopses in `records.json` are *new paraphrases of those blurbs*, not copied text or independent plot analyses. They are **HELD_FOR_HUMAN_REVIEW**, `public_release=false`; there is no license/asset claim or release-ready artwork attached. No episode, script, or transcript was read here. The prose must not be projected as full-source analysis or shown on the Explorer without a separate editorial admission decision.

## Source-surface conflict frontier (not promoted into this batch)

Search-indexed Paramount+ episode-detail results were found for four of the same cards. Their snippet dates apparently differ by one day from other index representations of the season listing. Attempts to open their direct detail pages during this tranche returned fetch errors or region-dependent redirects, and the rendered season guide inspected here showed **no date labels** in the episode cards. The fifth direct detail result was from an **Ireland-specific** page, not an equivalent U.S. source surface. Accordingly **no date value or airdate assertion is included**, and the snippet-only discrepancy is an unresolved follow-up, not a verified publication or broadcast fact. Both publisher surfaces share Paramount corporate lineage, so even accessible matching surfaces would not be independent corroboration.

## Source → local entity → evidence → assertion

- `source`: the named official guide and existing exact-file discovery receipt, with a shared corporate lineage key.
- `local_entities`: five guide-card entities tied to the source, with `work_id=null`; these are not global works.
- `evidence`: five source-relative heading/ordinal/short-description observations, each with a locator.
- `assertions`: five HELD claims **only** that the guide displays the observed local card. They do not assert canon, plot truth, chronology, psychological identity or global reconciliation.
- `synopsis_candidate`: five original one-sentence editorial drafts; none is released.

No lead was silently marked verified beyond this exact publisher-card display. There is no audiovisual close-read receipt, private media fingerprint, image metadata, or transcript extraction for these rows.

## Validation and independent review

Run:

```bash
python3 proposals/research/voy-s4-e01-e05-guide-recheck-20261103/validate.py
python3 proposals/research/voy-s4-e01-e05-guide-recheck-20261103/test_validate.py
python3 -O proposals/research/voy-s4-e01-e05-guide-recheck-20261103/test_validate.py
```

The checker fail-closes on duplicate JSON keys, source or corporate-lineage alteration, title/ordinal drift, foreign keys, unapproved Work identity, coverage/admission escalation, synopsis release, claimed close reads, and modified previously accepted CSV bytes. Its pass is **internal proposal integrity only**. A genuinely independent Auditor should review the exact candidate commit and source/copyright distinctions before any integration.

**Next frontier:** obtain a first-party, byte-custodied detail-page source for each title; resolve whether date labels represent release, availability or broadcast fields and whether regional packaging differs; subject the synopsis drafts to separate human/editorial review; only then propose an appropriate review-gated Explorer presentation. Do not increment research coverage on this basis.
