# Auditor delta — PR #1 calibration/drift fixtures

Date: 2026-08-17  
Role: AUDITOR  
Proposal: PR #1 @ `e20bf6797cc22bdc5211794ac0627fdb129fb592`  
CI: `validate-core` run `32076376704` — **SUCCESS**

## Disposition

**ISSUE #43 IMPLEMENTATION OPEN.** Green CI validates fixture-file structure/vocabulary, not the invariants named by the fixtures.

## Findings

1. `tools/test_invariants.py` checks only fixture-group presence, unique IDs, object-shaped input, nonempty invariants, and allowlisted invariant names. It does not execute validator/reconciliation/projection/diff behavior. A semantically broken implementation can therefore pass.
2. Only two synthetic adversarial descriptors exist, far short of the structural cases required by Director contract #43.
3. Named Trek entries (`Second Chances`, `Tuvix`, `Yesterday's Enterprise`) are placed in a fixed/known-difficult section without accepted Source/Work/Evidence IDs or accepted source-bound evidence. Under #43 they are candidate-only until accepted evidence exists.
4. `source-relative-memory-report` is structurally synthetic but is mixed into the known-difficult bucket with a non-Work `work_ref`.
5. Fixtures omit #43 reproducibility dependencies/expectations: accepted evidence basis where applicable, schema/methodology/predicate/compiler pins, allowed result set, explicit forbidden outcomes, and expectation supersession/version linkage.

## Required closure direction

- run synthetic fixtures through actual governed components and assert structural/fail-closed behavior;
- expand synthetic coverage to the #43 invariant set;
- keep named Trek cases candidate-only until accepted source-bound evidence can be independently verified;
- pin fixture dependencies and version expectation changes.

The existing file is useful as a seed/candidate inventory, but it is not yet a fixed real-Trek regression suite or adversarial drift enforcement.

No merge, implementation mutation, accepted semantic conclusion, coverage promotion, deployment, or other protected effect performed.
