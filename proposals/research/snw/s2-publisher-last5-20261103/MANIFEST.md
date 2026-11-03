# SNW Season 2 episodes 6–10 — publisher-page structural research

State: **PROPOSAL ONLY — PUBLISHER DESCRIPTION READ, AUDIOVISUAL WORK NOT READ.**

Accepted base: `main@d4ecd970bf28019696abd692011007d7d47f9ff8`.
Lane: SNW. Batch: `SNW.PPLUS.S2.LAST5.20261103`.

## Source and actual processing

- Public source: [Paramount+ Season 2 episode guide](https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/2/).
- Retrieved and read the HTTP 200 HTML guide on 2026-11-03 UTC; response body: **273,092 bytes**, SHA-256 `b8665d256eeee7bb4bb148c6c2d4389ebcdfd1cc398fd36c05bd567ee598cc32`.
- Private working snapshot was **not committed**. Source locators are the episode title `h2`, neighboring `abbr.seNum`, `abbr.epNum`, `time[datetime]`, and `div.ep__copy` fields, with raw HTML line ranges in `records.json`.
- The five cards were actually inspected: S2E6 *Lost in Translation* (HTML lines 1639–1651), S2E7 *Those Old Scientists* (1667–1679), S2E8 *Under the Cloak of War* (1695–1707), S2E9 *Subspace Rhapsody* (1723–1735), S2E10 *Hegemony* (1751–1763).
- Existing proposal `proposals/discovery/modern-paramount-season2-first5-20261102/snw/bundle.json` already records S2E1–E5; this tranche does not re-add those slots.
- The only source family is `publisher:paramountplus.com`: five cards from a single page are **not five independent confirmations**. The publisher HTML may change. No independent archival custody or second source has been established.

## Evidence boundary

The synopsis cards are **publisher claims about episodes**, not our observation of episode events, dialogue, or character intent. The batch creates five source-local Work candidates, local entity mentions, five evidence observations and five narrow assertions that Paramount+ *describes* the episodes this way. No global identity is inferred. The prose in records is original paraphrase; no transcript or large copyrighted passage is stored.

Dates retain the source's exact machine timestamps. Notably, the S2E7 HTML uses `2023-07-22T18:45:00-07:00`, which corresponds to July 23 UTC; a raw calendar-date comparison without timezone would create a false discrepancy.

No primary episode stream, complete closed captions, official script or soundtrack was accessed. Thus **no** `FULL_TEXT_AVAILABLE`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, `ENTITY_LINKED`, `AUDITED` or accepted `DISCOVERED` coverage event is claimed. `coverage_effect=NONE`, `denominator_effect=NONE`, `accepted_source_binding_effect=NONE`, and `accepted_work_effect=NONE`.

## Validation and next frontier

`python3 proposals/research/snw/s2-publisher-last5-20261103/validate.py` checks the bounded records, local links, source digest, expected publisher slot order, provenance flags, temporal source fidelity and absence of accidental admission. `python3 proposals/research/snw/s2-publisher-last5-20261103/test_validate.py` exercises fail-closed mutations.

Next: independently archive/retrieve publisher page version, qualify exact Source→Work identities with the Librarian, and obtain the complete primary audiovisual sources under legitimate access before attempting episode close-reading. Do not promote publisher synopsis semantics into fictional-world assertions.
