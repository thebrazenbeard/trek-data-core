# TREK REPOSITORY & BUILD PROTOCOL

Repository: `thebrazenbeard/trek-data-core`

## Accepted state
`main` is accepted state. Branches and PRs are proposals until accepted.

## Branch model
Use short-lived bounded branches:
- `research/<lane>/<batch-id>`
- `migration/<batch-id>`
- `external/<source>/<batch-id>`
- `reconciliation/<batch-id>`
- `architecture/<change-id>`

Do not create permanent chat branches.

## Batch model
Workers commit bounded research batches, not one Git commit per occurrence.

Typical audiovisual batch: about 5 installments.
Typical literary deep batch: about 1–3 substantial works.
Adjust only when source structure makes another size sensible.

A completed batch contains:
- manifest
- local entity records
- evidence records
- assertion records
- coverage update where applicable

## Write boundaries
Series/literary workers modify only their assigned research partition.
They do not mutate global entity registries or accepted reconciliation state.

The Librarian owns inventory/source-binding proposals.
The Consolidator owns global integration/reconciliation records and deterministic projections.
The Auditor produces findings/corrections rather than silently patching worker evidence.

## Deterministic reconciliation
LLMs may propose identity/reconciliation decisions.
Accepted reconciliation decisions must be explicit immutable/versioned records.
The compiler must not perform fresh LLM reasoning.

Projection input identity should include:
- accepted research head
- reconciliation head
- schema version
- methodology version
- predicate-registry hash
- compiler commit

## Canonical logical projection
Semantic continuity is measured against deterministic logical exports such as:
- entities.jsonl
- facts.jsonl
- relations.jsonl
- contested.jsonl
- unresolved.jsonl
- provenance.jsonl

Do not rely only on raw SQLite/Postgres file hashes because storage bytes can differ without semantic change.

## Diff classes
Projection diffs should distinguish:
- ADDED_FACT
- REMOVED_FACT
- VALUE_CHANGED
- STATUS_PROMOTED
- STATUS_DEMOTED
- ENTITY_LINK_CHANGED
- SCOPE_CHANGED
- PROVENANCE_CHANGED
- CONFLICT_INTRODUCED
- CONFLICT_RESOLVED

Semantic changes must be traceable to changed accepted evidence, reconciliation, schema/methodology, compiler code, or explicit correction.

## External adapters
External IDs remain crosswalk IDs, not canonical Trek IDs.
Record source version/snapshot, retrieval time, lineage, independence group, and mapping status.

## Public-repo policy
Do not commit complete copyrighted source works or large passages.
Keep source bytes outside the public repository. Commit only hashes, locators, metadata, evidence structure, and original analysis.

## Protected effects
Do not merge, force-push, deploy, alter credentials/permissions, or change repository protections without Patrick's exact authorization.
