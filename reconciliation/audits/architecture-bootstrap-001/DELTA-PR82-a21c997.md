# Auditor delta — PR #82 head `a21c997`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #82 `architecture/consolidator-v0.1-integration`
Previous audited head: `6a4489626617e5ddb7ead25493f15143291801db`
Current audited head: `a21c9975a204ad6fa9eb5479ddb58a4d3e3dcc93`
Workflow: `validate-core` run `32076416702` — FAILURE

## Delta scope

Four commits after `6a44896`, changing only:

- `registry/predicates.json`
- new `registry/scope_keys.json`
- `schema/assertion.schema.json`
- `schema/reconciliation-decision.schema.json`

No validator, projection compiler, semantic diff implementation, canonical manifest/provenance compiler, or derived consumer changed in this delta.

## Confirmed progress

### 1. Assertion subject schema aligns with #52

`assertion.subject_type` is now required and restricted to SOURCE, WORK, LOCAL_ENTITY, or ASSERTION. This is the four-domain v0.1 subject contract from Director #52, using the repository's uppercase type convention.

Schema-level subject ambiguity is therefore materially resolved. Referential enforcement still depends on validator behavior and path ownership.

### 2. Reconciliation decision names align with #72 split

The schema now enumerates:

- ENTITY_LINK
- ASSERTION_DISPOSITION
- ASSERTION_PROJECTION_STATUS
- SCOPE_RESOLUTION
- OTHER

The old ambiguous ASSERTION_STATUS / standalone SUPERSESSION shape is not present. This is correct schema-level movement under #61/#72.

`OTHER` remaining in the enum is acceptable only because #61 allows proposal/staging OTHER; ACCEPTED OTHER must continue to fail closed in validation.

### 3. Assertion lifecycle remains separate from proposed projection state

The Assertion schema retains research lifecycle `status` and uses `proposed_projection_status` separately. This is consistent with #72's two-axis model. `SUPERSEDED` remains a valid historical assertion-record status under #72; effective disposition decisions should ordinarily use PROPOSED/ACCEPTED/REJECTED.

### 4. Predicate registry metadata materially improves

Registry v0.2 entries now carry lifecycle, definition, semantic class, subject types, object mode/reference types, algebraic flags, projection eligibility, examples, near-miss text, supersession fields, and methodology/registry provenance.

Identity relations SAME_AS, COUNTERPART_OF, and IDENTITY_DIVERGES remain EXPERIMENTAL rather than being silently promoted merely to satisfy reconciliation tests. That caution is methodologically correct.

### 5. Scope-key registry introduced

`registry/scope_keys.json` now explicitly names CONTINUITY_SCOPE, TIMELINE_SCOPE, NARRATIVE_FRAME, and TEMPORAL_SCOPE with allowed subject domains. This is directionally aligned with #61's requirement that accepted scope resolution use governed keys rather than anonymous strings.

## Remaining blockers / contradictions

### A. Scope registry is not yet enforced or consumed

No validator/compiler implementation changed in this delta. `validate.py` therefore does not load or validate against `registry/scope_keys.json`, and the projection compiler does not consume that registry.

The current corrected contract test also still submits `resolution_key: "continuity"`, while the new registry's governed key is `CONTINUITY_SCOPE`. The test oracle and newly introduced registry are therefore internally inconsistent at this head.

Until validator/compiler/tests all use the same governed key identity, the registry is documentation/data, not an enforced contract.

### B. Reconciliation payload schema remains structurally unconstrained

`reconciliation_decision.payload` is still merely `{"type":"object"}` at schema level. #61 requires decision-type-specific payload semantics and conflict keys. Deterministic enforcement may live in validator code rather than JSON Schema, but no validator implementation changed here, so the earlier payload/domain gaps remain.

### C. Decision-type subject constraints are not expressed by schema

The generic reconciliation subject enum allows SOURCE, WORK, LOCAL_ENTITY, ASSERTION for every decision. #61/#72 require:

- ENTITY_LINK -> LOCAL_ENTITY
- ASSERTION_DISPOSITION -> ASSERTION
- ASSERTION_PROJECTION_STATUS -> effectively ACCEPTED ASSERTION
- SCOPE_RESOLUTION -> ASSERTION, WORK, or LOCAL_ENTITY

Those per-type invariants still require validator enforcement. No validator bytes changed in this tranche.

### D. #55 predicate governance remains incomplete

The new registry is substantially richer, but Director #55 also requires explicit predicate scope/level such as evidence-description, research assertion, reconciliation relation, or governed multi-level use. Current entries expose `semantic_class` and `projection_eligibility`, but no explicit use-level/scope field. The validator's required metadata set likewise does not include such a field.

That distinction matters most for identity relations because research-assertion use and reconciliation-relation use must not be silently conflated.

### E. No accepted identity relation exists for a positive ENTITY_LINK execution fixture

Every current IDENTITY_RELATION entry is EXPERIMENTAL with `projection_eligibility: EXPERIMENTAL_ONLY`. #55 says EXPERIMENTAL predicates must not be promoted as accepted stable/reconciliation truth merely for convenience.

Therefore the architecture currently has no repository-governed accepted identity predicate that can legitimately power a positive ACCEPTED ENTITY_LINK fixture. This is not a reason to promote SAME_AS casually. It is a reason AUD-ARCH-002 must remain open until either:

1. an identity predicate is explicitly governed/accepted with the required continuity and merge semantics; or
2. the regression harness supplies an isolated fixture-local accepted identity predicate without implying repository acceptance.

A negative fixture must still prove experimental/unknown identity relations fail closed.

### F. Implementation findings remain unchanged

Because no implementation file changed:

- path-wide Source/Work ownership enforcement remains open;
- effective assertion disposition / projection-status gating remains open;
- typed decision payload application remains open;
- SCOPE cardinality by resolution key remains open;
- full #76 canonical provenance/manifest remains open;
- diff semantics and provisional-extension governance remain open;
- derived SQLite/PostgreSQL/graph-search verification remains downstream-blocked.

## CI interpretation

Run `32076416702` remains RED. At this stage that is expected: schema/registry contracts have advanced without corresponding validator/compiler/diff implementation. Green would be suspicious unless the implementation followed.

## Exact next frontier

1. Make contract tests use actual governed scope-key IDs and add orthogonal-key/same-key supersession fixtures.
2. Add a legitimate ENTITY_LINK regression strategy without silently accepting an experimental identity predicate.
3. Wire scope-key and predicate use-level governance into validator semantics.
4. Implement per-decision subject/payload/effective-disposition constraints.
5. Then move compiler/provenance/diff behavior and run the complete integrated suite.

No merge, predicate acceptance, identity reconciliation, accepted-state mutation, or protected effect performed.
