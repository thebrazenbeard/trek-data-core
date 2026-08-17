# Auditor delta — PR #82 full-suite successor

Date: 2026-08-17  
Role: AUDITOR  
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`  
Integrated proposal: PR #82 @ `a21c9975a204ad6fa9eb5479ddb58a4d3e3dcc93`  
CI: `validate-core` run `32076416702` — **FAIL** (`50` tests executed; `6` failures, `2` errors)

## Disposition

**CONTESTED / SUBSTANTIAL PROGRESS.**

The stale unittest `run` collision is gone and the full discovered suite executes. The former PR #33 synchronization/harness defect is therefore resolved on this head.

## Substantive open failures

1. `ASSERTION_DISPOSITION` is not applied to active projection eligibility: an accepted REJECTED disposition still leaves the assertion in `unresolved`. This violates Director contract #72 and keeps AUD-ARCH-002 open.
2. Typed reconciliation decisions do not yet produce the expected derived projection under #61/#72. The typed reconciliation alignment test errors because no STABLE fact is produced.
3. Canonical provenance lacks full reachable governed records (`source_record` is absent), so #76/AUD-ARCH-003 remains open.
4. Semantic diff still infers conflict from status movement and uses generic `VALUE_CHANGED` for non-STABLE and reconciliation-history transitions, contrary to #67. AUD-ARCH-004 remains open. Legacy diff tests still encode the superseded conflict heuristic and must be reconciled with the current Director contract.

## Non-semantic red tests

- Cross-subject supersession is correctly rejected (`rc=1`); the test fails only because it requires the literal phrase `different subject` while validation reports `different active key`. This is brittle message-text coupling, not a missing rejection.
- The supposedly valid batch fixture is stale: its assertion omits now-required `subject_type`. Validator rejection is correct. Rebuild the fixture and canonical batch hash against the current schema rather than weakening admission validation.

## Predicate-governance gap

The predicate registry now carries useful near-miss, supersession/version, and identity-target metadata, but Director contract #55 also requires explicit predicate scope/level. Current entries expose `semantic_class` but no explicit scope/level field, and validator-required predicate metadata does not yet require all newly added lifecycle/provenance fields. Predicate-governance closure remains partial.

## Positive controls

- 50 tests actually run;
- typed assertion subject/object-reference checks pass;
- worker-proposed projection state is non-authoritative;
- reconciliation cycle, conflicting-active-disposition, and supersession-reason checks pass;
- worker Source/Work ownership and partition checks pass;
- SQLite/PostgreSQL/graph/search structural regressions reached in the suite continue to pass.

## Next gate

Consolidator should:
1. repair stale message/valid-batch test fixtures without weakening validators;
2. implement #61/#72 reconciliation/disposition projection semantics;
3. complete #76 provenance observability;
4. align diff code and legacy regression tests to #67;
5. complete #55 predicate scope/metadata enforcement;
6. rerun the entire integrated pipeline through downstream deterministic build steps.

Auditor re-opens only exact successor bytes.

No merge, accepted-state mutation, implementation edit, reconciliation acceptance, coverage promotion, deployment, or other protected effect is performed by this delta.
