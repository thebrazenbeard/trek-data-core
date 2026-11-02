# Offline candidate crosswalk importer

`tools/import_candidate_crosswalk.py` normalizes a **user-supplied**, Wikidata-like
JSON export into deterministic *candidate* external crosswalk proposals. It never
queries a service, scrapes a website, assigns a canonical Trek identity, accepts a
Source/Work record, or advances coverage.

This is intentionally narrower than a general importer. The existing
`registry/librarian_registry_contract.schema.json` defines fixed fields for
`external_crosswalk` and forbids extra properties. Every `records[]` row in the
output stays within those fields. Source licensing and receipt metadata live in
the surrounding proposal envelope, not as ungoverned schema extensions.

## Prerequisites

- Python 3.10 or later, standard library only.
- A locally supplied JSON export of Wikidata **structured data** licensed CC0-1.0.
- A locally supplied accepted Source/Work registry snapshot. Each target must
  already have `record_type: source|work`, `status: ACCEPTED`, and
  `fixture_only: false`. A proposed record or an `ACCEPTED` fixture is rejected.
- The exact, complete 40-character Git commit SHA that the operator **claims**
  the supplied registry came from. This tool records the claim and hashes the
  local registry bytes; it does *not* independently verify that GitHub head.

The existing `registry/librarian_registry_fixtures.json` is **not** an accepted
catalog. Do not point this tool at it to mint apparently accepted data. The
repository currently has no accepted corpus target IDs to import against; the
normal production result is a fail-closed rejection until that changes.

## Input format

```json
{
  "source": {
    "system": "Wikidata",
    "url": "https://query.wikidata.org/sparql",
    "license": "CC0-1.0",
    "license_url": "https://www.wikidata.org/wiki/Wikidata:Licensing",
    "retrieved_at": "2026-11-02T14:00:00Z",
    "snapshot": "WDQS-EXPORT-20261102"
  },
  "candidates": [
    {
      "external_id": "Q12345",
      "target_kind": "WORK",
      "target_id": "EXISTING_ACCEPTED_WORK_ID",
      "mapping_basis": "Manually compared title, release, and edition metadata"
    }
  ]
}
```

The QID is an external crosswalk ID, not a canonical Trek ID. The target is a
reference to an **existing** accepted local record; it is never created by this
tool. The example target ID above is explanatory, not an assertion that such a
Work exists. Candidate mappings require human verification before any later
admission process considers them. A supplied label or QID is not proof of a
depicted episode, chronology, character identity, or narrative fact.

An accepted registry snapshot uses the existing fixture container shape
(`sources` and `works` arrays) but its entries must be real accepted non-fixture
records. The importer checks only target type, ID, status and fixture flag;
other registry schema/authority verification belongs to the separate admission
and custody process.

## Usage

```bash
python tools/import_candidate_crosswalk.py \
  --input /path/to/wikidata-export.json \
  --registry /path/to/accepted-registry.json \
  --registry-ref 0123456789abcdef0123456789abcdef01234567 \
  --output /path/to/candidate-crosswalk-proposal.json
```

The output file must not exist; the command refuses to overwrite it. Its receipt
contains input SHA-256 hashes, the claimed registry head, source URL, license,
retrieval time, snapshot label, explicit `proposal_only: true`, and
`accepted_corpus_effect: NONE`. All crosswalk records use
`mapping_status: CANDIDATE`, `external_system: Wikidata`, and a shared
independence group to avoid treating Wikidata-derived restatements as independent
story evidence. Record order and generated candidate IDs are deterministic.

The importer rejects invalid licenses, malformed QIDs, unknown/non-accepted or
fixture-only targets, duplicate/ambiguous QID-to-target mappings, invalid input
shapes, and duplicate JSON keys. It deliberately restricts one input batch to
one-to-one mappings; uncertain many-to-many cases require explicit human
adjudication outside this tool.

## Research, rights, and operational boundaries

Wikidata structured data is [CC0](https://www.wikidata.org/wiki/Wikidata:Licensing),
but third-party linked pages, images, and narrative excerpts are not necessarily
CC0. This importer admits none of those bytes. It never makes HTTP requests; any
upstream data acquisition must independently comply with source terms and API
limits. Respect the [Wikidata Query Service user manual](https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual)
if preparing an export elsewhere.

Do not paste Star Trek episode scripts, subtitles, book text, still images, or
other protected source bytes into these JSON files. The project stores original
analytical structure and source locators/hashes, not copied full works. External
metadata supplies discovery hints and lineage, not official franchise canon.

## Verification

```bash
python -m unittest discover -s tests -p 'test_candidate_crosswalk.py' -v
```

Passing tests establish this offline formatter's contract on synthetic input;
they do not verify an actual Wikidata download, an authentic accepted registry
snapshot, or source-level correctness of an individual mapping.
