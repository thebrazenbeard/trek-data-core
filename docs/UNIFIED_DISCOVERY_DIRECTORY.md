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
- `proposals/discovery/publisher-season4-20261102/` — 122 official Paramount+ Season 4 listing observations across TNG (26), DS9 (25), Voyager (26), Enterprise (22), Discovery (13) and Lower Decks (10). The publisher's DS9 season guide jumps from episode 1 to episode 3; no episode 2 record is invented. All six original HTML captures remain outside Git and their SHA-256 receipts are source-consistency checks, not publisher authentication. The importer requires exactly one publisher-matching canonical URL in each raw HTML capture, including duplicate-attribute rejection.
- `proposals/discovery/publisher-season5-20261102/` — 97 official Paramount+ Season 5 listing observations across TNG (26), DS9 (26), Voyager (25), Discovery (10) and Lower Decks (10). The Voyager page has no S5E16 listing between E15 and E17; this **source gap remains unresolved**, not an assertion that the episode never existed. Enterprise Season 5 is not invented. Five private raw HTML responses are checked against SHA-256 receipts; the importer rejects spoofed, missing and duplicate canonical URLs. The receipts are not cryptographic publisher authentication.
- `proposals/discovery/publisher-season6-20261102/` — 78 official Paramount+ Season 6 source-local cards: TNG (26), DS9 (26), Voyager (26), each listing publisher ordinals E1–E26. Three privately captured HTML responses have byte-count and SHA-256 consistency receipts, and the importer rejects missing, forged, duplicated or ambiguous canonical links. The three guides share one Paramount publisher lineage; they do not authenticate audiovisual content or establish distinct Work identities.
- `proposals/discovery/publisher-season7-20261102/` — 74 official Paramount+ Season 7 source-local listings: TNG (25), DS9 (25), Voyager (24). Voyager's captured guide omits S7E10, which remains an unresolved publisher-source gap; no synthetic card is introduced. Three private HTML captures are checked by SHA-256/byte receipts and exact canonical URL attribution, with forged/missing/duplicate links rejected. These represent dependent publisher observations, not authenticated audiovisual Works or canon.
- `proposals/discovery/tas-publisher-seasons-20261102/` — 22 official Paramount+ *The Animated Series* Season 1–2 source-local listing observations (16 and six). Five Season 1 observations overlap the earlier TAS source snapshot and remain distinct provenance rows, not new deduplicated Works. Two raw HTML source captures have SHA-256/size receipts; their original bodies remain outside Git.
- `proposals/discovery/prodigy-mikros-volume1-20261102/` — ten titles from original animation studio Mikros Animation's Season 1 Volume 1 article. The publisher prose lists titles in order but does not number them: positions 1–10 are **inferred**, not a verified official episode-slot guide. A separate image caption in that same article labels `“Starstruck” Ep#103`, retained as a narrow same-source exception, not independent corroboration or justification to promote the other inferred positions. The original HTML is private; its response hash/size and CSV receipt remain reviewable.
- `proposals/discovery/prodigy-startrek-publisher-20261102/` — 30 StarTrek.com title-list slots for *Prodigy* Season 1 Episodes 11–20 and Season 2 Episodes 1–20. Publisher-numbered primary evidence for Season 1 Episodes 1–10 is **unresolved in this tranche**, not declared absent from the series. These observations share the Paramount corporate independence group and are not independent corroboration.
- `proposals/discovery/shorts-audio-20261102/records.json` — 10 *Short Treks* guide slots, five **promotional** *very Short Treks* releases, and one *Khan* audio-series container. The audio listing represents **zero evidenced audio episodes**. It is not merged with possible later literary/audio references under the same title.
- `proposals/discovery/scouts-firstparty-video-s1-20261103/` — **20 *Star Trek: Scouts* first-party publisher-video observations** from the official Nickelodeon/Blaze YouTube account's individually captured oEmbed metadata. The associated StarTrek.com/CBS announcement identifies a 20-installment short-form order. Six complete TrekCore captures provide *discovery crosswalks* to 19 publisher video IDs, not independent corroboration; the tenth Asteroid Blasters video is separately verified against publisher oEmbed. Both Asteroid Blasters and Holodeck Rescues use source-local #1–#10 numbering, **not** promoted to globally verified season ordinals, accepted Works or Briefings. Only titles, direct publisher links and source-body hashes are public; no video bytes. This publisher is in Paramount's corporate provenance family.
- `explorer/film-catalog.json` — 14 publisher film metadata candidates.
- `proposals/librarian/ring-of-fire-editions-20261102/records.json` — one proposed literary Work with four publisher editions, not four novels.
- `proposals/librarian/simon-schuster-three-novels-20261103/records.json` — three proposed novels (*Second Self*, *The High Country*, *The Enterprise War*) and nine distinct publisher product-page format observations (paperback, eBook and audiobook each). The publisher pages have no archived raw-response bytes or book-text receipts, and all nine views share one publisher independence family; Work groupings and format equivalence remain proposals, not accepted reconciliation.
- `proposals/librarian/picard-companion-editions-20261103/records.json` — independently versioned **proposal on accepted `main`**, not independently corroborating evidence. Its *Second Self* trade paperback ISBN `9781982194833` and proposed Work ID overlap the three-novel proposal. The generator checks all three Picard editions against code-owned identity/ISBN/source pins, emits **two additional source-local rows** for *The Dark Veil* and *Rogue Elements*, and emits **one** *Second Self* row from the existing three-novel source rather than duplicating it. All three depend on the **same Simon & Schuster publisher lineage**; their agreement is not independent corroboration or global reconciliation.
- `proposals/librarian/prh-star-trek-autobiographies-20261103/records.json` — five additional **fictional in-universe memoir** Work candidates, one ISBN edition observation each, sourced from full raw Penguin Random House (Titan Books distributor) HTML+JSON-LD page receipts. A Kirk/Picard/Janeway boxed set is separately recorded as a **container** and never a sixth new Work in this batch. [Source identity and rights caveats](../proposals/librarian/prh-star-trek-autobiographies-20261103/MANIFEST.md). No raw publisher HTML or cover image is in the public repository.

The proposed expansion has **1216 source-local rows**: 1155 episode-related metadata
references, 14 films, eleven literary candidate rows (six novels with 15 ISBN-format
observations and five fictional memoirs with one ISBN each), 35 short-form
releases and one audio-series container. These numbers
are not a count of distinct Star Trek Works, complete episodes, admitted
Briefings, verified sources, or a denominator for the universe. The same Work
can appear multiple times under independent and dependent publisher snapshots.
Source-group labels are navigation aids, **not** claims of independent
corroboration. Paramount and Paramount+ labels may share corporate lineage.

`python3 tools/audit_discovery_lineage.py --json` independently reports exact
URL reuse, normalized `(medium, context, title, source_locator)` overlaps,
and source-group aliases mapped to conservative upstream independence families.
The accepted 1214-row catalog has **25 overlapping metadata signatures (50
source-local rows)**, including 15 pairs where the same Paramount+ season-guide
URL is labeled `publisher:paramount` in one snapshot and
`publisher:paramountplus.com` in another; its 1214 rows reference **309 distinct
URLs**. The ten additional matching signatures within one `publisher:paramount`
label are separate SFA observations. These are a **review queue, not 25 proven
Work duplicates**; no row is removed and no global Work merge is proposed.
Different URL paths on one publisher domain likewise do not create independent
corporate witnesses. Unknown lineage labels fail the audit until reviewed.

## Safety and provenance

1. Every input is recomputed through its owning deterministic builder or
   checked against its source CSV receipt and existing roster validator.
2. Output includes SHA-256 over exact input-file bytes, a fixed status for
   every row and explicit `SOURCE_LOCAL` identity rather than canonical IDs.
3. The generator rejects stale/symlinked inputs and outputs. GitHub Pages
   validates exact committed bytes and its strict public artifact allowlist.
4. The Explorer renders text with DOM text nodes and permits link targets only
   on an explicit first-party/catalog host allowlist; it also checks that each
   source-group badge is compatible with the row's actual retrieval host, so
   a Wikidata item cannot impersonate a publisher listing. The broader
   `publisher:paramount` group explicitly permits its reviewed family of
   Paramount+, StarTrek.com, Mikros and YouTube source hosts. Publisher and
   distributor group claims require a non-null locator. A matching host,
   especially `youtu.be`, does **not** authenticate a publisher-operated
   channel or the claimed source content; that needs separate source review.
   Tones remain opt-in.
5. Source pages are mutable. Publisher URL attribution is not proof of source
   capture, full audiovisual viewing, book reading, transcript rights, or
   semantic analysis. The archived Wikidata observations are not guaranteed
   externally verified in this environment.
6. The novel-to-Picard overlap check fails closed on disagreement; it is limited
   to one reviewed source-local ISBN/Work pair and does not deduplicate the
   wider corpus or establish globally accepted literary identity.

The accepted research pipeline remains Source → Work → Local Entity → Evidence
→ Assertion and requires separate explicit admission. Do not promote these
discovery rows automatically, even when titles match.

The optional Explorer directory has separate medium, **series (source-local)**,
and source-group filters. Series values are derived only from episode-row
context codes and show counts of source observations, not unique episodes,
verified Works, or independent evidence. Selecting a series excludes other
media rather than assigning films, literary works, or shorts to that series.

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
