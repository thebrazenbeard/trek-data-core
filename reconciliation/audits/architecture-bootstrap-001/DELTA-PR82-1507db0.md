# Auditor delta — PR #82 head `1507db0`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #82 `architecture/consolidator-v0.1-integration`
Previous audited head: `dca65c14b2e9982d5033f45422bbff8ab437b0d9`
Current audited head: `1507db0b3f4ba98255b26fb3a6a80d30028c72b5`
Workflow: `validate-core` run `32077506091` — FAILURE

## Delta scope

Three commits change:

- new `schema/projection-provenance.schema.json`
- `tools/projection_bundle.py`
- `tools/test_graph_search_projection.py`

`tools/build_graph_search.py` production code does not change in this delta.

## Confirmed verifier progress

The shared verifier now validates every canonical relation and provenance row against explicit schemas instead of checking only `record_type`.

The new provenance schema requires the canonical support/provenance spine:

- assertion/evidence IDs;
- full assertion record;
- effective assertion disposition;
- support set;
- full evidence/source/work records;
- source/work lineage arrays;
- optional effective projection/reconciliation/observer/subject/object context.

This closes the prior "record_type only" structural-validation hole at the syntactic row-shape level.

## Remaining verifier integrity finding

### AUD-BUNDLE-CROSSRECORD — HIGH — schema-valid contradictory embedded records can still pass

The relation/provenance schemas validate field presence/types but do not establish internal cross-record identity consistency.

Examples a coherently hashed bundle can currently encode and pass schema validation:

- provenance `assertion_id = A` while `assertion_record.assertion_id = B`;
- provenance `evidence_id = e1` while `evidence_record.evidence_id = e2`;
- `evidence_record.source_id` / `work_id` inconsistent with the embedded `source_record` / `work_record` IDs;
- a `support_set` that does not equal the embedded assertion record's evidence support set;
- an IDENTITY_LINK relation whose subject/target types violate the currently governed LOCAL_ENTITY-only executable domain;
- relation-kind-specific provenance missing semantically even though the generic relation schema passes.

Director #78 requires failure on contradictory structural metadata the consumer depends on. SQLite/PostgreSQL now derive Source/Work/Evidence catalogs from these embedded records, so cross-record identity is load-bearing.

Required verifier regressions:
1. top-level assertion/evidence IDs must match embedded records;
2. evidence source/work references must match embedded Source/Work identities;
3. support_set must deterministically match assertion support identity;
4. subject/object/observer referenced records, when present, must match their advertised typed IDs;
5. IDENTITY_LINK relation must satisfy current governed subject/target domains and reconciliation-decision provenance;
6. ASSERTION_PREDICATE relation must satisfy its assertion identity/status provenance requirements.

Use deterministic verifier logic or kind-specific schemas; do not leave these as backend-specific guesses.

## Graph/search red tests are correctly ahead of implementation

The rewritten graph/search tests now require:

- mapping governed canonical relation rows to a generic `GOVERNED_RELATION` edge while preserving predicate metadata rather than inventing the predicate as an edge kind;
- structural provenance edges;
- inactive assertion-history and reconciliation-history nodes;
- projection status/partition preservation including STRUCTURAL_PARADOX;
- literal search content;
- verified upstream receipt + independent builder identity + imported-output contract;
- deterministic output bundles;
- rejection of malformed/stale canonical input through the actual builder entry point.

These are directionally correct #78 tests.

## Current graph/search production mismatch

The unchanged builder still:

- trusts manifest/projection hash directly and never calls `verify_projection()`;
- rejects **all** non-empty `relations.jsonl` even though a governed projection-relation schema now exists;
- creates ASSERTION_SUBJECT edges only by checking whether the raw subject string happens to match a local-entity ID, so SOURCE/WORK/ASSERTION typed subjects are silently lost;
- reads obsolete flattened provenance fields (`source_id`, `work_id`, `evidence_kind`, `source_content_hash`) that the current compiler no longer emits at top level; current canonical provenance nests them in full evidence/source/work records;
- therefore loses EVIDENCE_SOURCE/EVIDENCE_WORK structural edges under the current compiler shape;
- omits assertion-history and reconciliation-history nodes/surfaces;
- lacks upstream verification receipt, independent builder identity and explicit imported-output contract;
- writes output in place without stale-file hygiene.

The red run is therefore expected and should remain red until production moves.

## Compiler/verifier interop remains open

The actual compiler still emits two extra non-canonical JSONL compatibility aliases, so strict verifier integration remains blocked until compiler output is cleaned or the compatibility surface is moved outside the canonical bundle.

## Status

- shared verifier: stronger PARTIAL; row schemas now enforced, cross-record integrity remains open;
- graph/search #78 integration: RED / implementation pending;
- SQLite/PostgreSQL progress from prior delta unchanged;
- independent semantic findings remain open.

## Exact next frontier

1. Add verifier cross-record consistency checks.
2. Rewrite graph/search against verified canonical rows, typed subjects, governed relations and history surfaces.
3. Carry backend identity/receipt/import contract and clean output replacement semantics.
4. Add actual compiler -> verifier -> graph/search integration test.
5. Continue semantic corrections from the first-green-head audit.

No graph/search service execution, merge, deployment, accepted-state mutation, or protected effect performed.
