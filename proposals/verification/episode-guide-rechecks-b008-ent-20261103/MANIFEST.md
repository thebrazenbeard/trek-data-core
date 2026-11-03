# B008-ENT: nine Enterprise first-party publisher guide-card observations

**LIBRARIAN source-local proposal only** · reconciled against accepted `main@e49ee5c51e2157ee505603b1394b511313ca50b7` · first-party guide cards read 2026-11-03 UTC.

This bounded tranche covers **`lead:0090`–`lead:0098`** only: nine Wikidata-derived *Enterprise* episode discovery leads. Each was matched literally to its distinct Paramount+ rendered official episode-guide title and season/episode slot. These are not full episode reads, Work admissions or global identity decisions.

## Why this tranche starts at 0090

Accepted main already contains the Voyager B007 source-local guide-card proposal for **`lead:0083`–`lead:0089`** at `proposals/librarian/voy-b007-source-card-20261103/` (accepted through #304). The earlier combined B007 draft included those seven duplicate records. On reconciliation it was **superseded by this nine-entry Enterprise-only B008 tranche**. No repeated Voyager rechecks, duplicated metadata admissions or new coverage counts are included.

## Actual first-party reads

The nine title, publisher slot and short-description cards were individually inspected on the first-party Paramount+ U.S. episode-guide season pages:

| Official guide | Titles/slots inspected |
| --- | --- |
| [*Enterprise* S1](https://www.paramountplus.com/shows/enterprise/episodes/1/) | *Dear Doctor* (S1E13), *Fallen Hero* (S1E23), *Detained* (S1E21), *Cold Front* (S1E11) |
| [*Enterprise* S2](https://www.paramountplus.com/shows/enterprise/episodes/2/) | *First Flight* (S2E24), *Bounty* (S2E25), *The Expanse* (S2E26) |
| [*Enterprise* S3](https://www.paramountplus.com/shows/enterprise/episodes/3/) | *The Xindi* (S3E1), *Anomaly* (S3E2) |

`observations.json` pins the source-local ID and each publisher-rendered title/slot. `records.json` attaches the originating Wikidata QID locator and the separate Paramount guide URL with source-relative section locator and original short synopsis **draft**. All nine titles are literal matches, and all nine short draft synopses are **held for human/editorial review**. No synopsis is approved or released to Explorer by this proposal. The draft synopses are newly authored paraphrases, not copied Paramount text.

Only rendered guide cards were read. Neither raw publisher HTML bytes nor the audiovisual episodes/transcripts were downloaded, watched, hashed or indexed as full sources. Wikidata-derived discovery and Paramount publisher cards remain distinct lineages; Paramount's three guide pages comprise **one corporate publisher family** and are not independent narrative corroboration.

> **Hostile challenge:** A first-party short-description card still cannot prove detailed episode events, continuity, character motivations, full-source scope or edition-specific Work identity. A synopsis grounded in such a card is editorial copy, not admissible source-relative semantic evidence. Even a literal title/slot match may reflect guide publishing conventions rather than an independently verified canonical Work.

## Validation and effects

- Exactly **9** source-local official card checks, **9** exact title/slot observations, **9** new draft synopses awaiting review.
- Source/Work admissions: **0**; full-text/close-read coverage: **0**; approved/public synopses: **0**; media/artwork: **0**.
- The accepted 1,214-row Explorer source-local catalog and search projections are untouched. A Consolidator must separately review source identity and publication gates for any future integration.
- Regenerate `python tools/build_episode_guide_rechecks_b008_ent.py`; verify with `python tools/build_episode_guide_rechecks_b008_ent.py --check`, `python -m unittest tests.test_episode_guide_rechecks_b008_ent -v` and the full repository validation suite.
