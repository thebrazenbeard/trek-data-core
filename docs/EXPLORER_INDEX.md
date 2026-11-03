# Mission Explorer index contract

The browser-facing `explorer/index.json` is a static **derivative**, not an
authoritative research store. Its labels are deliberately literal:

- **Mission** is a television series in the project's display catalog.
- **Briefing** is an episode Work whose evidence is present in an
  accepted, source-bound canonical assertion projection.
- **Record** is a searchable assertion with its source IDs and projection
  status preserved. `STABLE`, `CONTESTED`, and `UNRESOLVED` must remain distinct.

The baseline catalog is sourced to the official franchise series list and is
explicitly marked `MISSION_CATALOG_ONLY`. This means **12 series cataloged,
zero episodes admitted**. The catalog cannot silently turn a historical
research branch's file list into episode coverage.

Generate deterministically from the repository root with Python 3:

```sh
python3 tools/build_explorer_index.py
python3 -m unittest discover -s tests -p 'test_explorer_index.py' -v
```

An optional admitted projection can later be supplied:

```sh
python3 tools/build_explorer_index.py --projection-dir path/to/verified-projection
```

All eight canonical projection output files must exist with matching
SHA-256/count receipts, and the aggregate projection hash must match. Each
indexed assertion must have accepted disposition, at least one attributable
evidence record, a matching Source and Work, and an **accepted
`EVIDENCE_BEARING` Source↔Work binding in each provenance row**. Missing
admission evidence fails the build. Every Source, Work and binding must
explicitly be non-fixture; the reviewed projection hash must also appear in
the separate `registry/approved_projection_hashes.json` allowlist, which is
**empty until mainline review approves a projection**. An internally
consistent, self-issued hash is never sufficient. The proposal architecture must emit
`source_work_binding_record` before it can generate nonempty Explorer records.

Hash receipts alone establish bundle integrity, not independent signoff or
source licensing. The admission/review process remains governed by
`TREK_RESEARCH_METHOD.md` and `TREK_REPO_PROTOCOL.md`. The derivative exposes
only short scalar assertion metadata; it does not copy transcripts or dialogue.
The builder recognizes both `work_type` and legacy `medium` classification,
and can resolve parent-series Work titles through provenance ancestry.

## Separate Research Leads, not Briefings

`explorer/research-leads.json` is independently generated with
`python3 tools/build_research_leads.py` and verified with `--check`. Its
version 2 schema keeps two kinds of **unverified** discoveries separate from
the accepted-only `explorer/index.json`:

| Research lead kind | Current published candidate source | Provenance and boundaries |
| --- | --- | --- |
| `WIKIDATA_METADATA` | 208 candidate items across 11 Missions, including 18 Enterprise P179 leads | Wikidata item QID, query/response SHA-256 receipts from an **offline user-supplied export**, single independence group `wikidata:wdqs`; receipt integrity does not verify remote acquisition or episode identity |
| `PUBLISHER_EPISODE_SLOT_METADATA` | 10 Starfleet Academy Season 1 slots from one Paramount+ publisher roster | Observed title, season/episode slot, bounded publisher guide locator, observation date and `publisher:paramount` independence group; **no** individual episode QID, webpage response hash, audiovisual inspection, verified completeness or independent corroboration |

The 20 Enterprise snapshot rows contain two extra research-review holds:
`Q56247746` (*Temporal Cold War arc*) is an arc rather than a clearly
individual episode; `Q866375` (*In a Mirror, Darkly*) may be a multipart
umbrella. The generator checks both explicit holds against the source batch
and **excludes both from public ordinary episode search**. The JSON records
`held_candidate_count: 2`, not episode counts or accepted omissions.

The total is **218 unverified search leads across all 12 cataloged Missions**,
not 218 admitted episodes or a verified television-series denominator.
Paramount+ and its press site share one publisher independence group. A
Wikidata redirect observation does not independently verify the publisher
roster. Every roster has `denominator_effect: NONE`; the coverage gate remains
`DENOMINATOR_UNRESOLVED`. The browser rejects mixed-source rows, unexpected
admission fields and held Enterprise identifiers. No generated research file
creates a canonical Work, Source↔Work binding, Evidence, accepted continuity
record or coverage effect.

The index is intentionally build-time JSON rather than a dynamic hosted API,
so GitHub Pages can serve the browser interface with no server, secrets, or
runtime access to research files. The Pages workflow should publish **only
`explorer/`** after tests pass.

## Separate film discovery catalog

`explorer/film-catalog.json` is another isolated, candidate-only display view,
deterministically generated from
`proposals/librarian/films-official-index-20261102/bundle.json` using
`python3 tools/build_film_catalog.py --check`. It contains 13 films linked
from the official StarTrek.com directory and a separately announced
streaming original, *Star Trek: Section 31*. The single publisher lineage is
`publisher:startrek.com`; link presence is not independently corroborated film
content. All entries remain `UNVERIFIED_METADATA`, `DISCOVERY_ONLY`, and have
`coverage_effect: NONE`. No film title is appended to the 12 television-series
Missions, no film is admitted as an episode Briefing, and the entries are not
an exhaustive franchise denominator. The underlying proposal manifest records
the conflicting publisher year metadata for *The Search for Spock*.

## Cross-medium discovery index is independent of the admitted projection

`explorer/discovery-catalog.json` is a third optional candidate-only artifact,
derived by `python3 tools/build_unified_discovery.py --check`. Unlike the
governed `index.json`, its rows deliberately retain **source-local** identity.
The expanded 1209 rows consist of 1155 episode-related observations (many
potentially overlapping), 14 films, 35 separate short-form releases, one
scripted audio-series container, and four proposed novels with 13 publisher-format ISBN observations.
There is no sum labeled “known universe Works” and no inferred completeness.

The generator checks input derivative bytes against their owning builders,
validates the DS9/Voyager/TAS, modern-series through season three, legacy seasons one through three, separate Seasons 4, 5, 6 and 7, TAS Seasons 1–2 publisher guides, Prodigy publisher-list and Mikros studio inferred-order CSV SHA
receipts and reviewed
publisher proposals, then
includes byte digests in the resulting artifact. The browser exposes title,
source-group and medium filters, never promotes discovery into a Briefing or
an accepted continuity record, and validates link origins before display.
GitHub Pages must verify this optional artifact deterministically and allow
only its exact committed bytes. See
[the multimedia directory contract](UNIFIED_DISCOVERY_DIRECTORY.md).
