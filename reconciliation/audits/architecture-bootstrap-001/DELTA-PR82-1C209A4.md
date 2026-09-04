# Auditor delta — PR #82 real-compiler bundle integration

Date: 2026-08-17  
Role: AUDITOR  
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`  
Integrated proposal: PR #82 @ `1c209a4898ff52e0b7ddaec577c3d5714008311e`  
CI: `validate-core` run `32077655951` — **FAIL after unit suite/repo validation/projection determinism**

## Closure

All 70 integrated unit tests pass. SQLite verified-consumer regressions are green, including known-good preservation and provenance/history/receipt behavior.

## Pipeline blocker

The real compiler output still emits two legacy extra JSONL files:
- `accepted_assertions.jsonl`
- `accepted_reconciliation.jsonl`

The shared verifier correctly rejects these as outside the exact governed canonical output set. CI therefore fails at the first real compiler -> SQLite consumer step, despite the fixture-based unit suite being green.

## #78 status

- verifier: correct/fail-closed;
- SQLite/PostgreSQL/graph-search consumers: supported at unit level;
- real compiler -> derived-consumer pipeline: blocked by stale legacy compiler output contract.

Remove/migrate the legacy outputs or explicitly govern them through a Director contract change; do not weaken exact-output verification merely to pass CI.

Original AUD-ARCH-001..004 remain resolved.

No implementation mutation, merge, accepted-state mutation, reconciliation acceptance, coverage promotion, deployment, or protected effect performed.
