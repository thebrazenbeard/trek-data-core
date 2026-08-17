# Auditor delta — PR #82 reconciliation/provenance successor

Date: 2026-08-17  
Role: AUDITOR  
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`  
Integrated proposal: PR #82 @ `f5986cf01d426c91e181bed08079c80401202666`  
CI: `validate-core` run `32076896745` — **FAIL** (`52` tests; exactly `3` failures)

## Disposition

**CONTESTED — one original core architecture finding remains.**

## Material closure on this exact head

- **AUD-ARCH-002 RESOLVED:** typed disposition/reconciliation/scope application, REJECTED exclusion, assertion supersession, and worker-proposal/derived-state separation pass current regressions.
- **AUD-ARCH-003 core provenance RESOLVED:** full reachable provenance and source-sensitive provenance change regressions pass.
- stale integration fixture debt from prior heads is cleared: batch/hash, worker Source/Work ownership, cross-subject supersession, typed references, and reconciliation validation tests pass.

## Remaining core failure — AUD-ARCH-004

All three remaining CI failures are Director contract #67 semantic-diff failures:

1. non-STABLE -> different non-STABLE emits `CONFLICT_INTRODUCED` + `VALUE_CHANGED` rather than a non-ordinal provisional status-change event;
2. STABLE -> CONTESTED emits correct `STATUS_DEMOTED` plus an invented `CONFLICT_INTRODUCED` based only on status/partition movement;
3. reconciliation-history-only change emits no dedicated semantic event.

Legacy diff regressions still encode the superseded inferred-conflict heuristic and must be reconciled with #67 rather than preserved as competing authority.

## Next gate

Align `diff_projection.py` and legacy/current tests to #67, then run the complete integrated pipeline through repository validation and all deterministic derived-build steps currently skipped after the test failure.

Broader acceptance dependencies (#40/#43/#55/#65/#76/#78 and governance/registry state) remain separately governed even after original AUD-ARCH closure.

No merge, implementation mutation, accepted-state mutation, reconciliation acceptance, coverage promotion, deployment, or other protected effect performed.
