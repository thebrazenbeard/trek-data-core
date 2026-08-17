# Auditor delta — PR #82 head `1a9ade2`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #82 `architecture/consolidator-v0.1-integration`
Previous audited head: `1507db0b3f4ba98255b26fb3a6a80d30028c72b5`
Current audited head: `1a9ade239f3edb40778f4eed95abce597521eaa1`
Workflow: `validate-core` run `32077628304` — FAILURE

## Delta scope

Two commits change:

- `tools/build_graph_search.py`
- `tools/test_projection_bundle.py`

## Confirmed graph/search progress

The graph/search builder is now substantially aligned with #78/current canonical projection semantics:

- calls shared `verify_projection()` before consuming rows;
- uses exact canonical active assertion partitions and preserves explicit status/partition, including STRUCTURAL_PARADOX;
- supports typed assertion subjects via SOURCE/WORK/LOCAL_ENTITY/EVIDENCE/ASSERTION/reconciliation reference mapping rather than raw local-ID guessing;
- consumes current nested canonical provenance records and restores EVIDENCE_SOURCE / EVIDENCE_WORK / observer / lineage structural edges;
- preserves inactive assertion-history nodes and assertion supersession edges;
- preserves reconciliation-history nodes, typed subject edges and reconciliation supersession edges;
- maps governed canonical relation rows to generic `GOVERNED_RELATION` edges while retaining relation kind/predicate/status/full record rather than inventing predicate names as edge kinds;
- emits literal deterministic search documents without adding semantic confidence/topics;
- pins independent builder identity, verified upstream receipt, imported-output contract and relation mapping contract;
- fails before bundle generation when the shared verifier rejects canonical input.

This closes the old graph/search flattened-provenance, local-subject-only, non-empty-relations fail-closed, and unverified-input implementation gaps at the code level.

## Remaining findings

### AUD-DERIVED-IDENTITY-DEPS — HIGH — derived builder identity omits verifier schema dependencies

SQLite, PostgreSQL and graph/search compute derived builder identity from:

- the backend builder file; and
- `projection_bundle.py`.

But `projection_bundle.py` dynamically loads and semantically depends on at least:

- `schema/projection-manifest.schema.json`;
- `schema/projection-relation.schema.json`;
- `schema/projection-provenance.schema.json`.

If one of those schema files changes while the Python files do not, verification/import behavior can change while `derived_builder_identity` remains identical.

#78 requires derived identity to track the actual transformation/trust contract, not just an incomplete subset of implementation files.

Fix by including verifier schema dependency hashes in a shared verifier/tool identity, then include that identity in each backend builder identity/receipt. The same principle should cover any future imported schema/registry dependency used by derived transformation logic.

### AUD-GRAPH-RELATION-CONTRACT-ID — MEDIUM

Graph bundle manifest hard-codes:

`relation_mapping_contract = projection-relation.schema.json@0.2.0`

The referenced schema currently has no explicit embedded `schema_version = 0.2.0` field/content identity. A hard-coded suffix can drift from actual bytes.

Prefer a deterministic schema content hash plus governed version identity, or derive the version from an explicit schema contract rather than a string literal.

### AUD-GRAPH-OUTPUT-HYGIENE — MEDIUM

Graph/search still writes its three JSONL files and manifest directly into an existing output directory and does not reject/clear stale undeclared files. PostgreSQL has the analogous bundle hygiene issue.

Use fresh/temp bundle generation and atomic/clean replacement, or explicitly reject unexpected leftovers so an old derived file cannot remain beside a new manifest.

### Shared verifier cross-record integrity remains open

No production change in `projection_bundle.py` on this delta closes the prior embedded-record ID/support/relation-kind consistency findings. Its tests likewise still cover hash/shape/partition failures, not contradictory cross-record identity.

### Compiler/verifier exact-output incompatibility remains open

The actual canonical compiler still emits extra compatibility JSONL aliases while the verifier accepts exactly the eight canonical outputs. No build_projection -> verify_projection integration test exists yet.

## Inherited semantic blockers

The green-head effective-predicate, assertion-supersession, identity-cardinality, Work-scope, provenance-diff orthogonality, conflict-resolution, supersession-diff fallback, and inactive-history-diff findings remain untouched.

## Status

- graph/search #78 integration: STRONG PARTIAL / production rewrite substantially complete;
- SQLite/PostgreSQL: STRONG PARTIAL from prior delta;
- derived builder identity: still incomplete across all adapters;
- shared verifier cross-record integrity: open;
- PR #82 overall: red / CONTESTED.

## Exact next frontier

1. Close verifier dependency identity and cross-record integrity.
2. Make exact compiler output verifiable.
3. Add clean/atomic derived bundle output hygiene.
4. Run compiler -> verifier -> SQLite/PostgreSQL/graph-search end-to-end tests.
5. Continue semantic corrections from the first-green-head audit.

No graph/search service execution, database execution, merge, deployment, accepted-state mutation, or protected effect performed.
