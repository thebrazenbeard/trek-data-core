# Auditor delta — PR #82 head `e8d965c`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #82 `architecture/consolidator-v0.1-integration`
Previous audited head: `1842f89c0362bb2866d1963620e91f1692379a42`
Current audited head: `e8d965c7810ec7c47d37b0debc728b16be9217cb`
Workflow: `validate-core` run `32078010308` — **SUCCESS**

## Delta scope

One commit adds only `tools/test_adversarial_invariants.py`.

No production validator/compiler/diff/verifier/derived-adapter code changed.

## Confirmed useful adversarial coverage

The new suite correctly adds fixed structural invariants for:

- source-lineage diamond ancestry deduplication without false cycle detection;
- same display name across Works does not silently merge local entities;
- testimony framing/observed utterance survives while worker-proposed STABLE status remains non-authoritative without accepted projection-status reconciliation;
- input iteration order does not alter deterministic logical projection;
- actual Source derivation cycle fails closed.

These are methodologically aligned with the Project's drift-control requirements and should remain in the suite.

## Acceptance blockers unaffected

The new tests do **not** cover or change the independently reproduced open findings from the prior green-head audit:

1. worker-PROPOSED assertion under EXPERIMENTAL predicate reconciled to effective ACCEPTED;
2. PROPOSED/REJECTED successor assertion suppressing accepted predecessor;
3. ENTITY_LINK multi-target/cardinality semantics;
4. Work-targeted scope-resolution materialization;
5. provenance-diff orthogonality;
6. contradiction disappearance versus explicit conflict resolution;
7. verifier cross-record identity/support consistency.

Nor do they alter the inherited predicate use-level, inactive-history diff, derived schema-dependency identity, or #65 binding-provenance findings.

## CI interpretation

Run `32078010308` is green and is useful evidence that the additional invariants coexist with the integrated stack. It does not alter the acceptance disposition because no production behavior relevant to the open findings changed and those findings remain absent from the oracle.

## Disposition

**SUPPORTED test expansion; PR #82 remains CONTESTED / not acceptance-ready.**

## Exact next frontier

Add the missing red adversarial cases above before touching the corresponding production semantics. Preserve the end-to-end green mechanical/reproducibility gate while forcing the semantic gaps to become visible failures.

No merge, acceptance decision, predicate promotion, reconciliation acceptance, deployment, database execution, accepted-state mutation, or protected effect performed.
