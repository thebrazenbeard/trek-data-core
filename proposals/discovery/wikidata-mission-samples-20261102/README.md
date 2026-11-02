# Wikidata Mission Briefing discovery samples — 2026-11-02

This directory contains **180 external episode-metadata candidates**, grouped by
Star Trek **Mission** (television series). A **Mission Briefing** means an
episode. The records are discovery leads, **not accepted Mission Briefings**
and not evidence for on-screen events or continuity claims.

| Discovery group | Missions sampled | Candidates | Other result |
| --- | --- | ---: | --- |
| `classic/` | The Original Series, The Animated Series, Deep Space Nine | 60 | — |
| `modern/` | Voyager, Discovery, Picard | 60 | Enterprise request timed out; no candidate records |
| `nextgen/` | Lower Decks, Prodigy, Strange New Worlds | 60 | Starfleet Academy query returned zero rows; no candidate records |

Each successful Mission query was capped at **20 results**, ordered by
Wikidata item. These are neither complete episode catalogs nor coverage
denominators. The Next Generation's separate ten-candidate pilot is proposed
in its own discovery batch. Together the proposals cover *candidate
discovery*, not *canonical admission*.

## Files and evidence boundary

- `queries/` preserves the exact SPARQL text supplied to Wikidata Query
  Service, including terminal newlines.
- `receipts/` records the claimed retrieval time, snapshot identifier,
  structured-metadata license, source locator, and exact query string.
- `proposals/` holds deterministic offline-normalized records with Wikidata
  QIDs, labels and SHA-256 digests of the query and source response.
- `RESEARCH_RECORD.md` documents the frozen method, retrieval results,
  failures, provenance and limitations for each acquisition group.

Raw `responses/*.json` snapshots are **deliberately not committed** under the
repository's public source-byte policy. Their exact bytes were independently
checked against the recorded SHA-256 hashes during acquisition and review and
are retained in a separate research archive. A Git checkout alone cannot
replay the normalization of an historical response without that archive.
Queries may be rerun, but a later response is *not* proof of the original
snapshot's bytes. The locally recorded receipts are not cryptographically
signed statements from Wikidata.

All 180 proposed records must remain `status: CANDIDATE` with
`canonical_work_id: null`, `accepted_work_effect: NONE`,
`accepted_source_binding_effect: NONE` and `coverage_effect: NONE`.
The canonical Work registry, authoritative Source↔Work bindings,
coverage ledger and Explorer index are **unchanged** by this batch.

## Reconciliation needed before admission

- Voyager has an item labelled `Q2` that needs title and identity review.
- Discovery includes *Terra Firma* and its separately indexed parts.
- Prodigy has *Lost and Found* and distinct items for its multipart segments.
- Enterprise's timeout and Starfleet Academy's zero-row query must be
  investigated with an explicitly approved new retrieval plan, not treated
  as claims about episode availability.

Use [`tools/import_wikidata_episodes.py`](../../../tools/import_wikidata_episodes.py)
from the prerequisite offline-importer change to normalize future source
snapshots. Do not promote these candidates automatically or derive canon
coverage from the sample size.
