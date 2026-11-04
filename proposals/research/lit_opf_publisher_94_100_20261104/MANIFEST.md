# HELD owner OPF / official publisher leads 0094–0100 — 2026-11-04

**Status:** local research **HELD_METADATA_ONLY_NOT_ACCEPTED**. These seven publisher edition observations do **not** admit an owner manifestation, Source, Work, evidence claim, synopsis release, public catalog entry, or CLOSE_READ state.

## Source and provenance

- Accepted `main` baseline: `3028765359001b90bc3e6b5c1835ee283b326e91`. The working base includes earlier HELD local packet `0d1bea8`, not merged main.
- Owner source: `proposals/librarian/private-opf-metadata-20261103/observations.json`, full-file SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`. This contains **347 source-local OPF metadata entries**, not 347 admitted Works. Individual `opf_entry_sha256` values in `records.json` pin the exact seven owner-local source observations.
- Publisher: seven genuinely opened Simon & Schuster first-party ebook product pages, checked 2026-11-04. All share **one** upstream publisher family, not independent corroboration. Publisher page snapshots not retained; current URL metadata has no immutable downloaded HTML digest. Original short metadata-relative paraphrases authored for this proposal, not copied descriptions or copyrighted ebook prose.
- Crucial limitation: **none** of these seven owner OPF records has an ISBN. Even an exact title/creator comparison does not bind the private manifestation to the publisher ebook ISBN or imply that an ebook was read. One local creator string materially conflicts; one local ordinal collides with a previous owner-local observation.

## Bounded first-party publisher evidence

| Owner OPF | First-party publisher edition metadata | Source anomaly / disposition |
| --- | --- | --- |
| `0094` | [The Q Continuum: Book One: Q-Space](https://www.simonandschuster.com/books/The-Q-Continuum-Book-One-Q-Space/Greg-Cox/Star-Trek-The-Next-Generation/9780671041014), Greg Cox; eBook `9780671041014`, July 14, 1999, 288 pp. | Owner title locally calls it `TNG 047`; that number is not attested on the opened publisher edition page. HELD title-only. |
| `0095` | [The Q Continuum: Book Two: Q-Zone](https://www.simonandschuster.com/books/The-Q-Continuum-Book-Two-Q-Zone/Greg-Cox/Star-Trek-The-Next-Generation/9780671041021), Greg Cox; eBook `9780671041021`, July 14, 1999, 288 pp. | Owner title labels `TNG 046`, **the same source-local ordinal** claimed by OPF `0093` for *To Storm Heaven*. Neither ordinal silently overwrites the other. HELD title-only. |
| `0096` | [The Q Continuum: Book Three: Q-Strike](https://www.simonandschuster.com/books/The-Q-Continuum-Book-Three-Q-Strike/Greg-Cox/Star-Trek-The-Next-Generation/9780671041038), **Greg Cox**; eBook `9780671041038`, July 14, 1999, 288 pp. | **Explicit creator conflict:** owner OPF says `William C. Deets &Dean Williams`; publisher says Greg Cox. This is a metadata contradiction, not a verified author identity. Quarantine pending owner-local reinspection. |
| `0097` | [Dyson Sphere](https://www.simonandschuster.com/books/Dyson-Sphere/Charles-Pellegrino/Star-Trek-The-Next-Generation/9780743421294), Charles Pellegrino / George Zebrowski; eBook `9780743421294`, April 1, 1999, 256 pp. | Owner OPF has neither ISBN nor creator. HELD title-only. |
| `0098` | [Vectors](https://www.simonandschuster.com/books/Vectors/Dean-Wesley-Smith/Star-Trek-The-Next-Generation/9780743421324), Dean Wesley Smith / Kristine Kathryn Rusch; eBook `9780743421324`, September 22, 2000, 304 pp. | Owner local creator string `Dean W. Smith & Kristine K. Rusch` abbreviates publisher credits; no ISBN. Retain unverified edition. |
| `0099` | [Red Sector](https://www.simonandschuster.com/books/Red-Sector/Diane-Carey/Star-Trek-The-Next-Generation/9780743421331), Diane Carey; eBook `9780743421331`, September 22, 2000, 336 pp. | Owner OPF has neither creator nor ISBN. HELD title-only. |
| `0100` | [Quarantine](https://www.simonandschuster.com/books/Quarantine/John-Vornholt/Star-Trek-The-Next-Generation/9780743421348), John Vornholt; eBook `9780743421348`, September 22, 2000, 288 pp. | Owner creator matches publisher spelling but local OPF has no ISBN. HELD title-and-creator only. |

## Evidence boundaries and falsifiers

The deterministic validator checks exact OPF inventory SHA, ID, per-entry hash, title, literal creator, and absent ISBN; exact official URL host/path, title/author/date/page extent/ISBN and independent checksum; original synopsis hash; every explicit anomaly; prior OPF 0093 duplicate `TNG 046` counterevidence; and packet-level no-full-text/no-acceptance/no-rights-release constraints. New red/green hostile tests include forged ISBN insertion, creator conflict laundering, duplicate-ordinal erasure, publisher URL spoofing, synopsis tampering, invalid extent/date, and admission/copyright leaks. No source prose or full book was exported.

The local branch contains **46 distinct owner-OPF source-local HELD leads (0055–0100 inclusive)**, with 7 from this tranche. These are not additional accepted Works or close reads. Ten earlier Consolidator publisher-only preview editions belong to a separate lane and are **not** added to the 46.

**Reviewer frontier:** determine whether OPF 0096 embeds a mistagged creator; investigate conflicting local TNG ordinal `046` independently of publisher series numbers, without using either to auto-reconcile. Next contiguous owner-local metadata tranche begins `opf-local:0101` if source evidence supports it. All held until explicit accepted research decisions.
