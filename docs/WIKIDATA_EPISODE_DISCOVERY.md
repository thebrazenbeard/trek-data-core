# Offline Wikidata episode discovery (candidate-only)

`tools/import_wikidata_episodes.py` converts a **previously downloaded** Wikidata
Query Service SPARQL JSON response to a deterministic episode *discovery
proposal*. It never connects to Wikidata, modifies the canonical registry,
creates Work/Source IDs or bindings, or advances any coverage ledger.

The output must be a new relative file under `proposals/`. The CLI will not
overwrite existing files. Proposed episode labels, series relationships,
seasons and numbers are external metadata, not official franchise canon.

## Inputs

1. A raw WDQS response JSON with the variables `episode`, `episodeLabel`,
   `series` and optionally `seriesLabel`, `seasonNumber`, `episodeNumber`.
   Entity values are Wikidata `/entity/Q...` URIs. Labels must be English
   literal bindings (`xml:lang: en`). Optional numbers must be positive integer
   literals. Rows are deduplicated by episode QID; duplicate QIDs cause rejection
   rather than silent merging.
2. An independently supplied, explicit provenance receipt JSON, for example:

```json
{
  "source_url": "https://query.wikidata.org/sparql",
  "license": "CC0-1.0",
  "license_url": "https://www.wikidata.org/wiki/Wikidata:Licensing",
  "retrieved_at_epoch": 1793630000,
  "snapshot_id": "wdqs-episode-discovery-20261102",
  "query_text": "SELECT ?episode ?episodeLabel ?series WHERE { ?episode ?predicate ?series . }"
}
```

The importer checks the exact source URL and explicit Wikidata structured-data
CC0 license, an integer Unix retrieval epoch between 2000 and 2100, nonempty
snapshot ID, and a bounded SELECT query. It records SHA-256 hashes of both the
source response bytes and supplied SPARQL query text. **This is a local-input
receipt, not proof the claimed export actually came from Wikidata.** Source
authenticity must be established separately before a later acceptance process.

## Example offline operation

```bash
mkdir -p proposals/wikidata
python tools/import_wikidata_episodes.py \
  --input /path/to/previously-downloaded-wdqs-results.json \
  --receipt /path/to/source-receipt.json \
  --output proposals/wikidata/episode-discovery-20261102.json
```

This is intentionally no recipe for bulk scraping. To prepare a compliant export
elsewhere, consult the [Wikidata Query Service documentation](https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual),
respect its User-Agent and rate-limit requirements, and independently verify the
query describes the scope you intend. No raw episode media, scripts, subtitles,
book passages, stills, or images belong in the output. Wikidata structured data
is [CC0](https://www.wikidata.org/wiki/Wikidata:Licensing); linked third-party
content may have different rights.

## Output contract

The proposal records:

- `proposal_only: true`;
- `accepted_work_effect`, `accepted_source_binding_effect`, and `coverage_effect`
  all `NONE`;
- source URL, license, retrieval epoch, snapshot identity, query and response
  hashes, and the explicit warning that remote provenance is unverified;
- candidate episode QID, English label, parent series QID, optional series
  label/season/episode numbers, and `canonical_work_id: null`;
- `evidence_status: EXTERNAL_DISCOVERY_METADATA_ONLY` for every row.

Every entry is marked `status: CANDIDATE`. Neither source names nor QIDs are
promoted into canonical Trek identity or independent narrative witnesses.

Rows are sorted by numeric episode QID. An invalid URL/license/epoch,
unexpected field, malformed QID, unknown language, missing required result,
duplicate QID, or ambiguous number fails closed. Input JSON duplicate keys fail
closed too. This makes the format suitable for reviewable candidate proposals,
not automated canon admission.

## Tests

```bash
python -m unittest discover -s tests -p 'test_wikidata_episode_discovery.py' -v
```

The suite uses synthetic SPARQL JSON. A passing run proves the local formatter's
specified behavior only; it does not verify the truth of a Wikidata statement.
