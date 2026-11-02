# Episode discovery inventory gap audit — 2026-11-02

**Review target:** accepted `main@441289e2521f1cb529a7a3343b5064184a713e8f`, `explorer/discovery-catalog.json` and its declared input receipts.  **Scope:** discovery metadata only.  No episode was watched/read, no Work identity reconciled, no Briefing admitted, and no source-independent coverage denominator established by this audit.

## Correct denominator boundary

The public Explorer has **439 `EPISODE` source-local rows**, not 439 independently identified episodes.  Of these, **208** originate in a bounded Wikidata query sample, **226** use two Paramount/Paramount+ publisher labels, and **5** use StarTrek.com publisher references.  Some rows are observations of the **same** title, and undated Wikidata rows do not establish source-audited season coverage.  `Missions=12` is the count of television-series containers; `Briefings=0` is the admitted episode-research count.  Neither is an episode census.

The following matrix counts **only explicitly season-numbered publisher-style source observations currently in the public discovery JSON**.  It does not infer absent episodes from an incomplete sample or treat a single publisher URL as an independently verified Work.

| Mission | Primary publisher-attested season span at audit | Explicit published season observations in current index | Unfilled season-oriented inventory frontier |
| --- | --- | --- | --- |
| TOS | 1–3 | S2: 26 | Source-bind S1 and S3 |
| TAS | 1–2 | S1: 5 | Complete S1 observation, then S2 |
| TNG | 1–7 | S1: 1 reference; S2: 22; S5: 1 reference; 3 references with season unresolved | Full S1, S3–S7; do not call isolated refs season rosters |
| DS9 | 1–7 | S1: 5; S2: 26 | Remaining S1 and S3–S7 |
| VOY | 1–7 | S1: 5; S2: 26 | Remaining S1 and S3–S7 |
| ENT | 1–4 | S2: 26 | S1, S3 and S4 |
| DIS | 1–5 | S1: 15; S2: 5 | Finish S2, then S3–S5 |
| PIC | 1–3 | S1: 10; S2: 5 | Finish S2, then S3 |
| LD | 1–5 | S1: 10; S2: 5 | Finish S2, then S3–S5 |
| PRO | 1–2 | No explicit publisher season-numbered observations; 20 undated Wikidata sample rows | Officially source-bind both season rosters, including distribution/edition variation |
| SNW | 1–3 | S1: 10; S2: 5 | Finish S2, then S3; later seasons need fresh cutoff checks |
| SFA | 1 currently advertised | S1: 20 separate publisher-source observations, with likely repeated episode slots across two proposed lists | Reconcile same-publisher overlapping S1 observations before claiming ten distinct episodes; refresh evolving inventory |

This matrix is an **inventory queue, not a sum of missing episodes**.  The official season spans are supported by StarTrek.com and Paramount publications, linked below.  SFA is time-sensitive, and source pages can change.  *Short Treks* and promotional *very Short Treks* live in separate short-form lanes, not these 12 Mission denominators.

## Primary publisher discovery citations and caveats

- StarTrek.com [series and films directory](https://www.startrek.com/series-and-movies) identifies the twelve Mission series and a separate film catalog.
- StarTrek.com [official distribution index](https://www.startrek.com/en-un/where-to-watch) lists DIS 5, LD 5, PIC 3, PRO 2, SNW 3, SFA 1 seasons in its current snapshot.
- The first-party [Paramount+ Canada series transfer announcement](https://www.startrek.com/news/paramount-plus-streaming-home-star-trek-canada) gives legacy ranges TNG 1–7, DS9 1–7, VOY 1–7, ENT 1–4, TAS 1–2, TOS 1–3.
- The official [TNG series page](https://www.startrek.com/series/star-trek-the-next-generation) says seven seasons and 178 episodes, and the [Voyager series page](https://www.startrek.com/series/star-trek-voyager) says seven seasons and 172.  Paramount+ describes [Voyager as 168 subscription episodes](https://www.paramountplus.com/shows/star_trek_voyager/).  These **do not agree** and may count two-part premieres, alternate packaging or regional availability differently.  Do not choose one number without a documented Work/part counting convention and source snapshot reconciliation.
- Paramount+ provides [TNG's season-selector guide](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/), [DS9's guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/), and [Voyager's guide](https://www.paramountplus.com/shows/star_trek_voyager/episodes/) for further source-first extraction.  Respect edition-specific publisher ordinal gaps (e.g. S1E1 multipart premieres followed by S1E3); do not fill them as fabricated missing episodes.

## Material audit challenges

> **Source independence:** `publisher:paramount` and `publisher:paramountplus.com` are distinct source-group labels in the current index but not independent rights holders or corroborating observers.  StarTrek.com is also in the Paramount/CBS corporate publisher family.  A future reconciliation must version the common provenance family separately from individual page/edition locators.

> **Counting unit conflict:** StarTrek.com and Paramount+ present different aggregate Voyager episode counts (172 vs 168).  A deterministic compiler must not silently sum or normalize those figures.  Require a fixed cutoff, explicit episode-vs-part definition, and source-stable roster before an accepted denominator exists.

> **Research depth:** An episode title/index row cannot advance `FULL_TEXT_AVAILABLE`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, or an admitted Briefing.  A complete franchise metadata index and a complete evidence-backed research corpus are separate multi-stage objectives.

## Reproduce accepted-index counts

From repository root:

```bash
python3 tools/build_unified_discovery.py --check
python3 - <<'PY'
import collections, json, re
d = json.load(open('explorer/discovery-catalog.json', encoding='utf-8'))
rows = [r for r in d['rows'] if r['medium'] == 'EPISODE']
assert len(rows) == 439
groups = collections.Counter(r['source_group'] for r in rows)
print('Source groups:', dict(sorted(groups.items())))
seasons = collections.Counter()
for row in rows:
    # Anchored whitespace is important: DS9 itself contains "S9".
    hit = re.search(r'\sS([0-9]+)E[0-9]+\b', row['context'])
    if hit and row['source_group'] != 'wikidata:wdqs':
        seasons[row['context'].split()[0], int(hit.group(1))] += 1
print('Season-numbered publisher observations:', dict(sorted(seasons.items())))
PY
```

**Priority:** Fill complete source-local publisher season rosters, especially missing S3+ seasons, without merging duplicate identity.  Separately investigate Prodigy distribution/source versions.  Then run reconciliation and admitted full-source research as distinct queues.  This audit does not authorize adding an unresolved denominator to the coverage ledger.
