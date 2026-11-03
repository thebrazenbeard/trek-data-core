# B002 — sixteen TOS rendered official episode-guide card rechecks

Proposal only. Source-local bibliographic/episode discovery metadata, not governed Work admission or research coverage. Accepted catalog input: `explorer/discovery-catalog.json` from `main@792e01284c914fde10ca3f5a43ef3ae39675d91b` (the generator checks exact 1,214-row catalog shape; its recorded catalog hash pins actual bytes). Observation date: `2026-11-03` UTC.

## Primary pages actually read

- [Paramount+ TOS season 1 episode guide](https://www.paramountplus.com/shows/star_trek/episodes/1/) — rendered episode cards containing title, season/episode ordinal, and a short description.
- [Paramount+ TOS season 2 episode guide](https://www.paramountplus.com/shows/star_trek/episodes/2/) — same fields.
- [Paramount+ TOS season 3 episode guide](https://www.paramountplus.com/shows/star_trek/episodes/3/) — same fields.

The rendered browser/web reading returned the card headings and descriptions, **not canonical raw HTML bytes**. No raw-body hashes or content-custody receipts are fabricated. A shared guide URL is **not** automatically counted as row-level evidence: each record identifies its specific observed title, SxEy ordinal and brief-description card within that guide. All 16 recorded card descriptions were actually displayed and read. The page's observed series label is simply `Star Trek`; the `TOS` context belongs to the source-local discovery row and is **not elevated into an independently proven page title**. These 16 cards belong to **one Paramount corporate publisher family**, not 16 independent sources. Their initial Wikidata source-local locators remain separate and unaltered.

| Initial discovery row | Paramount title and ordinal | Check |
| --- | --- | --- |
| `lead:0003` | The Man Trap — S1E2 | Exact title |
| `lead:0004` | The Devil in the Dark — S1E26 | Exact title |
| `lead:0005` | The Conscience of the King — S1E14 | Exact title |
| `lead:0006` | Charlie "X" — S1E3 | **Unresolved display-title variant:** Wikidata row says `Charlie X` |
| `lead:0007` | Mudd's Women — S1E7 | Exact title |
| `lead:0008` | The Naked Time — S1E5 | Exact title |
| `lead:0009` | The Enemy Within — S1E6 | Exact title |
| `lead:0010` | Dagger of the Mind — S1E10 | Exact title |
| `lead:0011` | Balance of Terror — S1E15 | Exact title |
| `lead:0012` | Mirror, Mirror — S2E4 | Exact title |
| `lead:0013` | By Any Other Name — S2E22 | Exact title |
| `lead:0014` | A Taste of Armageddon — S1E24 | Exact title |
| `lead:0015` | Wolf in the Fold — S2E14 | Exact title |
| `lead:0016` | A Private Little War — S2E19 | Exact title |
| `lead:0017` | And the Children Shall Lead — S3E4 | Exact title |
| `lead:0018` | Catspaw — S2E7 | Exact title |

## Honest result and synopsis boundary

- **16** official rendered guide cards inspected, including title, season/ordinal and brief description.
- **15** exact official-title/source-local-title matches; **1** punctuation/title variant explicitly unresolved (`Charlie X` vs `Charlie "X"`).
- **16** short, independently worded synopsis **drafts**, based on official brief descriptions only; `human_review: PENDING`. They are **not** approved public synopses or episode-close-read summaries. Every remaining source-local row still has a missing synopsis state in the separate B001 ledger.
- **0** raw source-body hashes authenticated, **0** full episodes viewed, **0** governed Works/Evidence/Assertions admitted, **0** accepted coverage advancement.
- B001 was independently reviewed, CI-passed and accepted through [PR #269](https://github.com/thebrazenbeard/trek-data-core/pull/269) at `d13e179f`, retaining 8 rendered rechecks. If B002 is also independently reviewed and admitted **as metadata only**, the batches supply **24 non-overlapping source-local rendered metadata observations** of 1,214, not 24 completed Works. This B002 batch remains a proposal until separately accepted.

The source descriptions are not republished verbatim. The complete copyrighted episode scripts or recordings were not accessed; an original one-sentence paraphrase cannot substantiate a full episode's narrative.

## Rebuild and checks

```bash
python3 tools/build_episode_guide_rechecks_b002.py --check
python3 -m unittest tests/test_episode_guide_rechecks_b002.py
```

The validator requires the exact 16 queued source-local IDs, source group and TOS context; rejects false official title matches, ordinal collisions, malformed snapshots, added raw-body SHA claims, invented approval, and admission effects. It computes each official guide URL and per-card locator, and reproduces `records.json` byte-for-byte. It does **not** fetch or authenticate the pages at test time: the observations require independent human/source review prior to acceptance.

## Next bounded frontier

Continue from the next unreviewed episode leads (starting `lead:0019` if B001/B002 both accepted), in batches no larger than 16. Retrieve exact season-guide cards with heading, episode ordinal and description, flag mismatches without auto-merging global Work identity, author short original synopsis drafts, and obtain independent review. Seek authenticated source-body custody separately; a rendered web scrape remains explicitly `UNPINNED`. Memory Alpha remains a secondary discovery/crosswalk source only, not authoritative episode verification.
