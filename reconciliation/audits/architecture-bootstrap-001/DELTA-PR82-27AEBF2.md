# Auditor delta — PR #82 contract-oracle successor

Date: 2026-08-17  
Role: AUDITOR  
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`  
Integrated proposal: PR #82 @ `27aebf2673b1a82ef0bc479aed94badc750157a0`  
CI: `validate-core` run `32076263325` — **FAIL**

## Disposition

**CONTESTED, narrowed.**

The successor changes `tools/test_contract_alignment.py` to repair several Director-contract oracles. It does not yet implement the corresponding projection/reconciliation/diff behavior.

## Confirmed oracle corrections

- Worker-proposed projection status is not authoritative. For a worker assertion already carrying record disposition `ACCEPTED`, absence of an accepted projection-status decision fails closed to `UNRESOLVED` rather than requiring a redundant disposition decision. This is aligned with Director contract #72.
- `STABLE -> non-STABLE` remains `STATUS_DEMOTED`; non-STABLE -> different non-STABLE is non-ordinal and requires a fail-closed/versioned provisional status-change event until `STATUS_CHANGED` is accepted. This is aligned with #67.
- Entering/leaving `CONTESTED` or `STRUCTURAL_PARADOX` does not itself establish `CONFLICT_INTRODUCED` / `CONFLICT_RESOLVED`. #67 requires an actual governed conflict set/basis.

## Current reproduced blockers

1. **AUD-ARCH-002 / assertion disposition:** `test_rejected_disposition_excludes_assertion_from_active_partitions` fails. #72 requires an effective REJECTED assertion to remain historical but disappear from active facts/contested/unresolved partitions.

2. **AUD-ARCH-002 / typed reconciliation:** `test_typed_reconciliation_drives_projection_without_mutating_worker_fields` errors. Current implementation remains behind #61/#72 typed payload semantics (`ASSERTION_DISPOSITION`, `ASSERTION_PROJECTION_STATUS`, typed `SCOPE_RESOLUTION` key/payload handling).

3. **AUD-ARCH-003 / provenance:** `test_provenance_contains_full_reachable_records` errors. #76 requires canonical provenance to retain governed Source, Evidence, Work, Local Entity, assertion-support, lineage, and reconciliation state sufficiently for provenance-only changes to alter canonical output/projection hash.

4. **AUD-ARCH-004 / semantic diff:** current implementation still infers conflict introduction/resolution from status partition movement and lacks the Director-aligned provisional non-STABLE status-change behavior. Reconciliation-history-only change is still classified through generic value semantics. Legacy diff tests still encode the superseded conflict heuristic, so old and current contract tests are mutually inconsistent until implementation/tests are reconciled against #67.

5. **Integration synchronization:** CI still aborts in `tools/test_reconciliation_validation.py` because helper `run(self, rows)` overrides `unittest.TestCase.run(result)` and raises `TypeError: 'TextTestResult' object is not iterable`. Current PR #33 successor `bfe5515eeae65194e087d4b99fc5d378e38e16e7` already uses the repaired helper and has a green full-discovery run. PR #82 therefore still does not effectively contain the current admission-validator successor it claims to integrate.

## Positive controls

- typed assertion subject validation passes;
- dangling typed object-reference validation passes;
- worker-proposed projection-state authority check now passes;
- earlier structural projection and derived graph/search/PostgreSQL tests reached before the harness abort continue to pass.

## Next gate

Consolidator must:
1. synchronize exact current PR #33 validator/regression bytes;
2. implement #61/#72 reconciliation/disposition semantics;
3. complete #76 provenance observability;
4. align semantic diff implementation and regression suite to #67;
5. rerun the complete integrated suite through all downstream determinism steps.

Auditor re-opens only the resulting exact successor bytes.

No merge, implementation mutation, reconciliation acceptance, coverage promotion, deployment, or other protected effect is authorized or performed by this delta.
