# Auditor delta — PR #82 compiler-output cleanup successor

Date: 2026-08-17  
Role: AUDITOR  
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`  
Integrated proposal: PR #82 @ `e61dc464d28819fb9ff43ce59ece2b4bb6e51204`  
CI: `validate-core` run `32077762749` — **FAIL** (`70` tests; `1` error)

## Regression

The compiler rewrite directionally removes/reworks the stale legacy projection outputs but now rejects an accepted projection-status decision for an assertion predecessor that is later explicitly superseded:

`ValueError: projection status targets non-accepted assertion assertion-1`

Supersession should remove the predecessor from active projection while preserving assertion/reconciliation history. Historical decision validity must be distinguished from current active-projection eligibility.

## Positive controls

The other 69 tests remain green, including verifier and all three derived-consumer unit suites. Earlier SQLite arity and stale verifier-fixture defects remain fixed.

## Next gate

Restore supersession-history semantics without weakening fail-closed behavior for genuinely invalid decision targets, then rerun the complete real compiler -> verified-consumer pipeline.

No implementation mutation, merge, accepted-state mutation, reconciliation acceptance, coverage promotion, deployment, or protected effect performed.
