# B003 — sixteen official rendered TOS/TAS guide-card source rechecks

Status: **proposal-only**, no Work, Evidence, Assertion, coverage or synopsis publication effect. Source-local input: accepted `explorer/discovery-catalog.json`, exactly 1,214 observations; SHA-256 pinned in deterministic `records.json`. Observed on `2026-11-03` UTC. This is a continuation after accepted B001 (8 checks, PR #269) and B002 (16 checks, PR #273, merged on `main@5663932`). If B003 itself is accepted as metadata only, these three disjoint tranches contain 40 rendered metadata observations, **not 40 completed researched Works**.

## Primary pages actually opened and read

- [Paramount+ TOS season 2 episode guide](https://www.paramountplus.com/shows/star_trek/episodes/2/): row `lead:0019`, *Bread and Circuses* (S2E25).
- [Paramount+ TAS season 1 episode guide](https://www.paramountplus.com/shows/star_trek_animated/episodes/1/): twelve TAS rows in this tranche, with title/SxEy and a brief description in each individual card.
- [Paramount+ TAS season 2 episode guide](https://www.paramountplus.com/shows/star_trek_animated/episodes/2/): three TAS rows (*Albatross* S2E4, *Bem* S2E2, *How Sharper Than a Serpent's Tooth* S2E5).

All three pages were actually read as **rendered web text**, not captured as raw HTML bytes. The exact rendered card titles, season/episode ordinals and brief descriptions were examined. Individual records retain exact source-local Wikidata URI, separate Paramount+ guide URI, local series context, displayed page label, card locator, and independent provenance-family relationship. A shared guide URI or a HTTP 200 response by itself proves none of those individual card observations.

| Source row | Paramount guide card | Outcome |
| --- | --- | --- |
| `lead:0019` | TOS Bread and Circuses — S2E25 | Exact title |
| `lead:0020` | TAS The Slaver Weapon — S1E14 | Exact title |
| `lead:0021` | TAS Yesteryear — S1E2 | Exact title |
| `lead:0022` | TAS Albatross — S2E4 | Exact title |
| `lead:0023` | TAS Bem — S2E2 | Exact title |
| `lead:0024` | TAS Beyond the Farthest Star — S1E1 | Exact title |
| `lead:0025` | TAS How Sharper Than a Serpent's Tooth — S2E5 | Exact title |
| `lead:0026` | TAS The Ambergris Element — S1E13 | Exact title |
| `lead:0027` | TAS Mudd's Passion — S1E10 | Exact title |
| `lead:0028` | TAS Once Upon a Planet — S1E9 | Exact title |
| `lead:0029` | TAS One of Our Planets **is** Missing — S1E3 | **Case/title variant unresolved:** source-local uses `Is` |
| `lead:0030` | TAS The Eye of the Beholder — S1E15 | Exact title |
| `lead:0031` | TAS The Infinite Vulcan — S1E7 | Exact title |
| `lead:0032` | TAS The Jihad — S1E16 | Exact title |
| `lead:0033` | TAS The Lorelei Signal — S1E4 | Exact title |
| `lead:0034` | TAS The Magicks of Megas-tu — S1E8 | Exact title |

## Claim boundary

This batch records **16** distinct primary *rendered guide cards*: **15 literal title matches**, **one intentionally unresolved case variant**, **one TOS and fifteen TAS rows**. The sixteen original one-sentence synopsis drafts are grounded only in the **publisher's short card description**, not actual viewing of full episodes. Every draft remains **not human-approved for public display**. Neither distributor text nor copyrighted episode dialogue is reproduced. All three guide URLs belong to one Paramount corporate family, **not sixteen independent corroborations**. Each original Wikidata locator remains a secondary discovery row, not automatically the same globally reconciled Work.

`raw_page_body_sha256` is null for each observation: web rendering did not provide authenticated raw bytes. The batch has **zero** newly governed works/evidence, complete source reads, coverage promotions, or accepted synopses. Any catalogue remainder not explicitly observed stays pending.

## Corrected future TOS slot boundary

The previous B002 compiler capped TOS season one at E29. The official Paramount+ season-one guide includes **S1E30: Operation: Annihilate!** This B003 compiler's `valid_official_slot("TOS",1,30)` explicitly permits E30 and rejects E31; the test suite prevents a silent return to 29. No row in this 16-row B003 tranche itself claims to have verified E30. Future batches must individually read that card before producing an observation.

## Deterministic checks

```bash
python3 tools/build_episode_guide_rechecks_b003.py --check
python3 -m unittest tests/test_episode_guide_rechecks_b003.py
```

The builder rejects forged input title, source context, ordinal collisions, wrong series, false exact-title match, unauthorized metadata-to-coverage promotion, unapproved raw-body hash claims and malformed or oversized synopsis drafts. **It cannot itself prove originality or prevent close paraphrasing of a copyrighted blurb; human review remains required.** It produces the 16 records byte-for-byte from the declared observations plus accepted source-local catalog. It does **not** authenticate the remote source again during CI; an independent reviewer must re-open official publisher pages before any draft is considered qualified.

Next frontier if this batch is accepted: `lead:0035` onward, one bounded source-read unit at a time, preserving title variants and source provenance. No automatic Work identity reconciliation or public synopsis release.
