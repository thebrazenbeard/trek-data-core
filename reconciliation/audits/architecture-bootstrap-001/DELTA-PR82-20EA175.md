# Auditor delta — PR #82 green integrated architecture head

Date: 2026-08-17  
Role: AUDITOR  
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`  
Integrated proposal: PR #82 @ `20ea17557fc2839e75f96900be3e084d77b56536`  
CI: `validate-core` run `32077162357` — **SUCCESS** through the full integrated pipeline

## Original architecture disposition

- **AUD-ARCH-001 RESOLVED** on integrated bytes: admission/schema/reference/ownership/batch regressions pass.
- **AUD-ARCH-002 RESOLVED:** typed reconciliation/disposition/scope/supersession application passes.
- **AUD-ARCH-003 RESOLVED for canonical projection/provenance core:** full reachable provenance is source-sensitive and build identity regressions pass.
- **AUD-ARCH-004 RESOLVED:** rewritten semantic diff satisfies the expanded Director #67 regression contract.

Integrated CI passes regression discovery, repository validation, double projection build/determinism diff, SQLite query determinism, PostgreSQL bundle determinism, graph/search determinism, and input-identity sensitivity.

## Broader gates still open

### Director #78 derived consumers — partial

A strong shared `tools/projection_bundle.py` verifier now exists and validates manifest schema, exact canonical output set, canonical JSONL bytes, per-output hashes/counts, governance pins, active partition/status invariants, relation/provenance row types, aggregate projection hash, and emits a verified upstream receipt.

The derived builders were not changed in the `7062c26... -> 20ea175...` successor and do not yet call the verifier. SQLite still uses its prior direct-load/target-replacement path. Green derived determinism therefore does not yet close hostile/stale-bundle verification, independent derived-builder identity, verified derivation receipts, imported-output contract, or atomic preservation of a prior known-good SQLite target.

### Other independent dependencies

Coverage #40, calibration #43, Librarian binding #65, predicate-governance #55, governance sequencing, and accepted-state drift remain separately governed. They are not original AUD-ARCH reopenings.

## Disposition

`ORIGINAL ARCHITECTURE AUDIT: RESOLVED ON EXACT HEAD 20ea175...`

`FOUNDATION ACCEPTANCE: STILL BLOCKED BY BROADER DIRECTOR/OWNER GATES.`

No merge, implementation mutation, accepted-state mutation, reconciliation acceptance, coverage promotion, deployment, or other protected effect performed.
