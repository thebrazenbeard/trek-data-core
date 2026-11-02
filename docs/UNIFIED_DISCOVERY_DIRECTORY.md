# Source-local multimedia discovery directory

`tools/build_unified_discovery.py` creates the optional, static, searchable
`explorer/discovery-catalog.json` index. This is an independent **candidate
metadata** lane: it does not alter Mission/Briefing admission, coverage,
continuity assertions, canonical Work IDs, or episode denominators.

## Inputs (deterministically checked)

- `explorer/research-leads.json` — 218 existing candidate observations, mostly archived Wikidata sample rows, including ten SFA publisher slots.
- `proposals/discovery/publisher-catalog.json` — 15 source-local references from two explicitly allowlisted publisher batches. Some may describe the same episode as the above sample; no cross-source deduplication occurs.
- `proposals/discovery/ds9-voy-episode-slots-20261102/` — five publisher-listed season-one slots each for DS9, Voyager and TAS. CSV bytes must match their SHA-256 receipts and generated bundles. DS9 and Voyager preserve first-party S1E1 then S1E3 numbering gaps.
- `proposals/discovery/modern-paramount-season1-20261102/`, `modern-paramount-season2-first5-20261102/`, and `modern-paramount-season3-20261102/` — 108 separate source-local publisher slots across four modern series; metadata-only, not 108 independently verified Works. The third-season tranche contributes 43 observations.
- `proposals/discovery/legacy-paramount-season1-20261102/` — 114 Paramount+ season-one listing slots across TOS, TNG, DS9, VOY and ENT. Publisher pages may expose gaps in numbering; the CSV and source-body receipts preserve listed slots, without inventing missing episodes. Raw HTML remains outside Git.
- `proposals/discovery/legacy-paramount-season2-20261102/` — 126 publisher season-two episode-listing rows across TOS, TNG, DS9, VOY, ENT, with source-body SHA-256 **receipts** and exact CSV observations. The original publisher HTML bodies stay outside Git; source hashes do not independently authenticate a live web response.
- `proposals/discovery/legacy-paramount-season3-20261102/` — 126 additional official Paramount+ season-three listing rows in the same five series. Each has a source-body SHA-256 receipt and an exact normalized CSV observation; the source bodies remain outside Git.
- `proposals/discovery/prodigy-startrek-publisher-20261102/` — 30 StarTrek.com title-list slots for *Prodigy* Season 1 Episodes 11–20 and Season 2 Episodes 1–20. Publisher-numbered primary evidence for Season 1 Episodes 1–10 is **unresolved in this tranche**, not declared absent from the series. These observations share the Paramount corporate independence group and are not independent corroboration.
- `proposals/discovery/shorts-audio-20261102/records.json` — 10 *Short Treks* guide slots, five **promotional** *very Short Treks* releases, and one *Khan* audio-series container. The audio listing represents **zero evidenced audio episodes**. It is not merged with possible later literary/audio references under the same title.
- `explorer/film-catalog.json` — 14 publisher film metadata candidates.
- `proposals/librarian/ring-of-fire-editions-20261102/records.json` — one proposed literary Work with four publisher editions, not four novels.

The proposed expansion has **783 source-local rows**: 752 episode-related metadata
references, 14 films, one literary Work with four editions, 15 short-form
releases and one audio-series container. These numbers
are not a count of distinct Star Trek Works, complete episodes, admitted
Briefings, verified sources, or a denominator for the universe. The same Work
can appear multiple times under independent and dependent publisher snapshots.
Source-group labels are navigation aids, **not** claims of independent
corroboration. Paramount and Paramount+ labels may share corporate lineage.

## Safety and provenance

1. Every input is recomputed through its owning deterministic builder or
   checked against its source CSV receipt and existing roster validator.
2. Output includes SHA-256 over exact input-file bytes, a fixed status for
   every row and explicit `SOURCE_LOCAL` identity rather than canonical IDs.
3. The generator rejects stale/symlinked inputs and outputs. GitHub Pages
   validates exact committed bytes and its strict public artifact allowlist.
4. The Explorer renders text with DOM text nodes and permits link targets only
   on an explicit first-party/catalog host allowlist; tones remain opt-in.
5. Source pages are mutable. Publisher URL attribution is not proof of source
   capture, full audiovisual viewing, book reading, transcript rights, or
   semantic analysis. The archived Wikidata observations are not guaranteed
   externally verified in this environment.

The accepted research pipeline remains Source → Work → Local Entity → Evidence
→ Assertion and requires separate explicit admission. Do not promote these
discovery rows automatically, even when titles match.

## Local verification

```bash
python3 tools/build_unified_discovery.py --check
python3 -m unittest tests.test_unified_discovery -v
node tests/test_explorer.mjs
```

Rebuild only after reviewed input proposals change:

```bash
python3 tools/build_unified_discovery.py
```

No external services, telemetry or paid dependencies are required.
