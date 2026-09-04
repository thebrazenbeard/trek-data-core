# Auditor delta — PR #82 head `dca65c1`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #82 `architecture/consolidator-v0.1-integration`
Previous audited head: `a695b0273e3bc4eb8fe2e67622e62daa70d28556`
Current audited head: `dca65c14b2e9982d5033f45422bbff8ab437b0d9`
Workflow: `validate-core` run `32077416117` — FAILURE

## Delta scope

Four commits change:

- new `schema/projection-relation.schema.json`
- `tools/build_sqlite.py`
- `tools/build_postgres.py`
- `tools/test_postgres_projection.py`

## Confirmed #78 progress

### SQLite

The SQLite builder now:

- calls the shared `verify_projection()` before creating/replacing any database;
- builds into a temporary file and atomically `os.replace()`s only after successful import, count validation, SQLite integrity check and commit;
- preserves the prior known-good target when verification/import fails;
- pins upstream projection/input/governing identities;
- stores derived schema version, independent builder identity, verification receipt hash/full receipt, and imported-output contract;
- imports active partitions with exact projection status/effective disposition;
- imports assertion history, canonical provenance, reconciliation history and relations;
- derives queryable Source/Work/Evidence catalogs from verified provenance, including source/work lineage records;
- fails on conflicting repeated catalog metadata.

This closes the previously audited destructive-rebuild and unverified-input SQLite defects at the code level, subject to the canonical compiler/verifier interoperability blocker below.

### PostgreSQL bundle

The PostgreSQL generator now:

- calls the shared verifier before generation;
- pins verified receipt and independent builder identity;
- imports all eight canonical outputs into the derived schema/query surface;
- preserves assertion/reconciliation history, relations, provenance and Source/Work/Evidence catalogs;
- sets `standard_conforming_strings = on` and UTF-8 explicitly;
- keeps SQL generation separate from database execution;
- hashes generated SQL and writes a bundle manifest containing upstream verification receipt + imported-output contract + builder identity.

Hostile-text tests now exercise apostrophes, backslashes/newlines and SQL-looking content. The quoting approach remains deterministic under the explicit standard-string setting.

## Remaining tranche-specific blockers

### AUD-DERIVED-RELATION-SCHEMA — HIGH — new relation schema is not enforced by shared verifier

`projection-relation.schema.json` now defines required fields and allowed relation kinds/types, but `verify_projection()` does not load or validate rows against it. It checks only:

`row.record_type == "projection_relation"`

A coherently hashed bundle can therefore contain structurally malformed relation rows with missing/invalid subject/predicate/target fields and still pass the shared verifier, after which SQLite/PostgreSQL import NULL/incomplete structural metadata.

The schema itself also lacks relation-kind-specific requirements: e.g. ASSERTION_PREDICATE should require the applicable assertion/status identity, while IDENTITY_LINK should require reconciliation decision provenance and the currently governed local-entity domain. Those can be expressed with conditional schema or deterministic verifier rules.

Required regression: a bundle with valid manifest/hash/count but malformed relation structure must fail `verify_projection()` and therefore fail every derived builder.

### AUD-BUNDLE-COMPILER-INTEROP — CRITICAL — still open

The actual canonical compiler still writes two extra compatibility JSONL aliases that the verifier rejects as unexpected outputs. Neither compiler nor verifier interoperability changed in this tranche.

SQLite/PostgreSQL tests use the handcrafted canonical fixture, not the exact output directory from `build_projection.py`.

The derived builders are now correctly strict enough that they would reject the real compiler output until this is resolved. Add an end-to-end compiler -> verifier -> SQLite/PostgreSQL regression.

### PostgreSQL bundle output replacement hygiene — MEDIUM

`write_bundle()` creates/writes `projection.sql` and `manifest.json` in an existing output directory but does not build in a fresh temporary directory or reject/clear stale undeclared files. This is less dangerous than SQLite because the bundle is file-only and declared outputs are explicit, but a stale file can survive beside a new bundle.

Prefer temp-directory generation + atomic directory/declared-file replacement or explicit stale-file rejection for a clean content-addressed derived bundle.

## Still outside this tranche

- Graph/search builder has not yet been migrated to the verifier.
- All semantic findings from the green-head audit remain open because validator/compiler/diff files did not change here.
- #65 Source↔Work binding provenance remains blocked externally.

## Status update

- SQLite #78 integration: **STRONG PARTIAL / code-level trust boundary substantially fixed**.
- PostgreSQL #78 integration: **STRONG PARTIAL**.
- Shared verifier: **PARTIAL**, now blocked notably by relation-schema enforcement and compiler interoperability.
- Graph/search #78 integration: **OPEN**.
- PR #82 overall: **CONTESTED / red**.

## Exact next frontier

1. Make real compiler output verifiable without weakening unexpected-output checks.
2. Enforce projection-relation structural/semantic schema in shared verifier.
3. Migrate graph/search to the shared verified receipt and backend identity contract.
4. Add full compiler -> verifier -> all-derived-adapters integration tests.
5. Continue independent semantic corrections from the green-head audit.

No database execution/deployment, merge, accepted-state mutation, or protected effect performed.
