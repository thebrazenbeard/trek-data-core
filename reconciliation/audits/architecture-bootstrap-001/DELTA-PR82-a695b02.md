# Auditor delta — PR #82 head `a695b02`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #82 `architecture/consolidator-v0.1-integration`
Previous audited head: `20ea17557fc2839e75f96900be3e084d77b56536`
Current audited head: `a695b0273e3bc4eb8fe2e67622e62daa70d28556`
Workflow: `validate-core` run `32077304056` — FAILURE

## Delta scope

Three commits after `20ea175` change only:

- `tools/projection_bundle.py` (small helper/refactor delta)
- new `tools/test_projection_fixture.py`
- `tools/test_sqlite_projection.py` rewritten toward #78

`tools/build_sqlite.py` itself does **not** change in this delta.

## Confirmed useful movement

The new shared projection fixture gives derived-adapter tests a common canonical eight-output bundle containing active STABLE/STRUCTURAL_PARADOX/UNRESOLVED assertions, inactive history, provenance, relations and reconciliation history.

SQLite tests now correctly require several previously missing #78 properties:

- verified upstream projection receipt hash;
- independent derived builder identity;
- derived schema version;
- active partition/status preservation including STRUCTURAL_PARADOX;
- inactive assertion history preservation;
- provenance and relation preservation;
- query determinism;
- invalid new projection must leave previous known-good DB intact;
- queryable Source/Work/Evidence provenance catalogs.

These are good red acceptance tests. They should not be weakened merely to restore green.

The verifier also adds a deterministic `tool_identity()` helper suitable for backend-specific builder identity.

## Current production mismatch

The unchanged SQLite builder still:

- reads/trusts `manifest.json` directly rather than calling the shared verifier;
- deletes the existing target DB before verifying/importing the new projection;
- removes a partial/old DB on failure rather than atomically preserving the last known-good target;
- imports legacy `accepted_reconciliation.jsonl` rather than canonical `reconciliation_history.jsonl`;
- does not import `assertion_history.jsonl`;
- does not expose Source/Work/Evidence provenance catalogs;
- uses old resolved-entity/resolved-subject/value fields rather than the current typed compiler surface;
- lacks verification receipt hash, derived schema version and independent builder identity metadata.

Therefore the red run is expected and methodologically useful.

## Verifier/compiler incompatibility remains

The projection fixture creates exactly the eight canonical outputs and therefore verifies cleanly. It still does not exercise the **actual** canonical compiler output directory, which currently also emits two unmanifested compatibility JSONL aliases. `verify_projection()` continues to reject any extra JSONL.

Add a build_projection -> verify_projection integration regression before declaring the shared verifier interoperable.

## Status

- #78 verifier primitive: STRONG PARTIAL.
- SQLite #78 integration: RED / implementation pending.
- Previous semantic findings from `205544b` remain open and untouched.

## Exact next frontier

Implement SQLite against `verify_projection()` and the canonical output names, build to a temporary DB, validate it, atomically replace only after success, retain backend-specific import/build receipt metadata, and preserve required history/provenance surfaces. Then run the red tests without weakening them.

No DB execution outside test fixtures, merge, deployment, accepted-state mutation, or protected effect performed.
