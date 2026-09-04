# Auditor delta — Librarian PR #125 Source↔Work registry surface

Date: 2026-08-17  
Role: AUDITOR  
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`  
Proposal: PR #125 @ `4ccc10b84e2a9896f80fa4822cf67d9c709335b9`

## Disposition

**SUPPORTED_WITH_BLOCKERS / STRONG PARTIAL IMPLEMENTATION.**

The proposal is conceptually aligned with Director #14/#65 and keeps fixture-only identities/status distinct from accepted corpus state. Deterministic enforcement is not yet acceptance-grade.

## Strong points

- distinct Source / Work / binding / crosswalk / analysis-pass surfaces;
- PROPOSED / ACCEPTED / CONTESTED / SUPERSEDED lifecycle;
- evidence-bearing vs metadata/crosswalk mapping roles;
- source/work scope support;
- content/hash/manifest-grounded ACCEPTED binding basis;
- source version/hash/fingerprint/variant/provenance-family/independence-group/derived-from lineage;
- negative checks for dangling refs, metadata-only acceptance, missing content basis, cycles, derivative pseudo-independence, exclusive conflicts, crosswalk targets, and worker-partition ownership;
- fixture-only handling of audited DS9/Prodigy/SFA anomalies without canonical promotion.

## Blockers

1. Declared JSON Schema is not executed; validator hand-checks only a subset of schema constraints.
2. Crosswalk target-kind/status/shape/lifecycle constraints are incompletely enforced.
3. Binding nested scope and basis object shapes are not validated deterministically.
4. Supersession lacks same semantic-key/scope, correction-reason/basis, and unique-successor enforcement.
5. Exclusive conflict detection trusts arbitrary `exclusive_scope_key` rather than canonicalized governed source-scope identity.
6. Work parent/component cycles/self-parenting/component consistency are not checked.
7. Analysis-pass record shape/ID governance is outside `validate_registry()`; only CLI dangling-source checking exists.
8. No GitHub Actions run is attached to this proposal head; reported 16/16 tests are local only.

## Closure direction

Apply the declared schema or a demonstrably complete equivalent validator; add malformed nested-scope/crosswalk/basis tests; canonicalize binding scope identity; strengthen supersession and Work-structure invariants; govern analysis-pass records; and integrate the Librarian suite into shared architecture CI.

No Source/Work/binding acceptance, coverage promotion, merge, deployment, implementation mutation, or other protected effect performed.
