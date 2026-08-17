# Auditor review — Librarian Source/Work/binding PR #125 @ `4ccc10b`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #125 `external/librarian/source-work-binding-v1`
Audited head: `4ccc10b84e2a9896f80fa4822cf67d9c709335b9`
Director contracts: #14 / #65

## Disposition

**STRONG BOUNDED MODEL / CONTESTED BEFORE INTEGRATION OR ACCEPTANCE.**

PR #125 is the first concrete Librarian-owned Source / Work / Source↔Work binding implementation proposal. It correctly keeps the fixture set proposal-only, preserves Source/Work cardinality independence, separates external crosswalks and analysis passes from Source witness identity, preserves metadata/body disagreement, and refuses literary bindings without byte-addressable source custody.

The Director's exact-head review already identified six load-bearing corrections. This Auditor record does not treat those same findings as independent corroboration. It records additional adversarial findings on contested state, supersession domain, multi-parent source independence, schema/validator divergence, and integration with the common v0.2 architecture.

No Source ID, Work ID, binding, crosswalk, coverage state, merge, or protected effect is accepted/performed by this audit.

## Upstream Director blockers retained

Director review on the same head already requires correction of:
1. ACCEPTED binding over merely PROPOSED Source/Work endpoints;
2. current SOURCE_BOUND ignoring accepted binding supersession;
3. missing explicit binding correction reason;
4. caller-bypassable free-form `exclusive_scope_key`;
5. missing Work parent-cycle validation;
6. under-governed analysis-pass records / IDs;
plus accepted-crosswalk endpoint status, accepted Source identity pinning, and schema/validator nonempty-field agreement.

Those remain open and should be fixed in the successor.

## LIB-AUD-001 — CRITICAL — CONTESTED incompatible mapping does not inhibit current SOURCE_BOUND

#65 defines `CONTESTED` as incompatible binding evidence where no accepted resolution is justified.

Current validator computes exclusive conflicts only among bindings whose lifecycle is `ACCEPTED`; `source_bound_pairs()` likewise returns every ACCEPTED EVIDENCE_BEARING pair without considering competing CONTESTED bindings.

Therefore the model can simultaneously contain:
- ACCEPTED Source A -> Work X over a source scope; and
- CONTESTED Source A -> Work Y over the same incompatible/exclusive source scope;

while still reporting A/X as SOURCE_BOUND.

That is semantically inconsistent with the lifecycle definition when the CONTESTED record represents unresolved incompatible evidence.

Required successor behavior:
- define the deterministic current binding-state key from canonical source/source-scope/work-scope semantics;
- distinguish a historical contest already superseded/resolved from an **active** contest;
- an active incompatible CONTESTED binding over a declared exclusive mapping domain must prevent SOURCE_BOUND from being treated as settled until governed resolution/supersession exists;
- preserve legitimate nonexclusive one-Source->N-Works mappings.

Add regression: active ACCEPTED X + active CONTESTED incompatible Y on same canonical exclusive source scope -> no settled SOURCE_BOUND for that contested mapping domain.

## LIB-AUD-002 — CRITICAL — supersession can cross unrelated binding domains

`supersedes_binding_id` is validated for existence and cycles only. There is no check that successor and predecessor belong to the same correction lineage/domain.

A successor binding for an unrelated Source/scope can therefore supersede an arbitrary predecessor. Once the Director-required active-supersession logic is implemented, that could remove an unrelated valid SOURCE_BOUND relation from current state.

A binding correction may legitimately change the mapped Work, but the correction must retain a governed subject/domain identity. At minimum the successor should be constrained to the same Source identity and same canonical source scope/exclusivity domain unless a separately governed re-identification operation explicitly says otherwise.

Required regressions:
- unrelated Source B binding cannot supersede Source A binding;
- successor on a different source slice cannot silently supersede predecessor on another slice;
- Work target may change only within the same governed correction domain;
- proposed/contested successor does not deactivate an accepted predecessor unless the lifecycle rules explicitly say it does.

## LIB-AUD-003 — HIGH — scalar independence_group cannot represent legitimate multi-parent derivation

Current Source rule requires every derived Source to have the same scalar `independence_group` as each direct parent.

That correctly blocks a one-parent derivative from minting a fresh independent witness. It fails for a legitimate multi-parent derived artifact whose parents are genuinely independent Sources with different groups.

Example structure:
- Source P1 in independence group G1;
- Source P2 in independence group G2;
- derived comparison/merged/converted artifact D with `derived_from=[P1,P2]`.

D must not count as independent of P1 **or** P2, but no single scalar value can equal both G1 and G2. Current validation must either reject the legitimate lineage or falsely collapse G1 and G2 into one independence group.

#65 explicitly says provenance family and source independence are related but not identical and requires the derivation chain + independence grouping to remain reconstructable.

Required design: model witness dependence as a set/closure or other structure capable of saying D is downstream-dependent on multiple upstream independence groups, rather than forcing every derivation DAG into a one-group tree.

Add diamond/multi-parent fixtures analogous to the Consolidator's Source-lineage adversarial test.

## LIB-AUD-004 — HIGH — proposed JSON Schema is not an executable contract

`registry/librarian_registry_contract.schema.json` contains `$defs` for Source, Work, binding and crosswalk records, but:
- it has no top-level instance shape / `oneOf` / fixture-container contract;
- `validate_librarian_registry.py` never loads or applies the schema;
- tests exercise only the handwritten validator.

Consequences include possible schema/validator drift for:
- field types;
- `additionalProperties:false`;
- enum values;
- scope object shapes;
- nonempty strings / basis values;
- nullable-versus-required fields.

This drift is already visible: schema gives accepted `method` only type string while handwritten validator separately requires nonempty accepted method; basis item `value` has schema minLength but handwritten validator checks only basis kind for content grounding.

Required successor:
- make the record schemas directly executable by the common admission validator, or load them deterministically in the Librarian validator;
- add negative tests where a record passes handwritten semantic checks but violates schema shape/type/minLength and vice versa;
- avoid two independent schema authorities.

## LIB-AUD-005 — HIGH — SOURCE_BOUND helper is not a safe derivation boundary by itself

`source_bound_pairs(bindings)` accepts bindings alone and currently returns pairs solely from lifecycle=`ACCEPTED` + mapping_role=`EVIDENCE_BEARING`.

It cannot independently check:
- Source/Work endpoint acceptance;
- active supersession;
- active contest state;
- method/basis validity;
- Source concrete-identity sufficiency;
- exclusivity conflicts.

Director already identified several of these semantic omissions. The architectural point is that a public/current-state helper that returns SOURCE_BOUND eligibility should consume the **validated active registry state**, not a raw binding list whose caller may bypass validation.

Required design: make SOURCE_BOUND derivation an explicit deterministic function over validated Source + Work + binding lifecycle state (or return a validated state object), and test that invalid/raw records cannot produce current coverage eligibility by direct helper use.

## LIB-AUD-006 — HIGH — standalone Librarian validator is not integrated with common v0.2 admission/projection/diff

PR #125 is correctly based on accepted `main`, but accepted `main` has no validator workflow. The exact head has **no GitHub Actions run**. The stated 16/16 result is local only.

Meanwhile PR #82 now contains the independently green integrated v0.2 admission/projection/diff/derived-consumer surface.

Current PR #125 record types/schemas are therefore not yet part of:
- common repository record-type/schema admission;
- common cross-record referential validation;
- canonical projection manifest/input identity;
- #76 Source↔Work binding provenance;
- semantic diff for binding-only corrections;
- #40 coverage-state derivation.

#65 explicitly requires binding/provenance-only correction to remain observable even when assertion values do not change. A standalone helper/validator does not yet satisfy that project-wide requirement.

Required integration after the Librarian contract itself is corrected:
1. add governed Source/Work/binding/crosswalk schemas/record types to the integrated architecture without putting them under worker partitions;
2. make accepted registry/binding snapshot identity part of canonical build identity;
3. expose binding provenance in canonical provenance as required by #76;
4. ensure binding-only correction changes the canonical projection/provenance hash and emits a governed/provisional semantic diff event;
5. let #40 derive SOURCE_BOUND from the same accepted active binding state;
6. add CI that combines Librarian fixtures with the integrated v0.2 validator, rather than maintaining a permanently separate validator island.

## LIB-AUD-007 — MEDIUM/HIGH — contested/superseded evidence obligations are under-specified

Schema requires `method` and `basis` fields on every binding, but allows empty method/basis. Handwritten semantic requirements are applied only when lifecycle is ACCEPTED.

A CONTESTED record is supposed to represent incompatible evidence; a SUPERSEDED record is historical provenance. Allowing either to carry empty method/basis can make the reason for contest/correction unreconstructable.

At minimum:
- CONTESTED bindings should carry nonempty method/basis sufficient to explain the contest;
- successor bindings should carry explicit supersession reason + method/basis;
- historical SUPERSEDED predecessor records must remain self-describing enough to reconstruct what was formerly asserted.

This should be expressed in schema/validator consistently rather than inferred from free-form notes.

## Positive controls confirmed

The proposal correctly demonstrates:
- metadata/body disagreement preserved rather than rewritten;
- 1 Source -> N Work components;
- N Sources -> 1 Work component;
- CANDIDATE external crosswalk separate from canonical ID;
- analysis passes over one Source do not mint extra Source witnesses;
- metadata/crosswalk-only binding cannot be ACCEPTED evidence-bearing SOURCE_BOUND under current validator;
- dangling refs/cycles and one-parent derivative pseudo-independence are at least recognized;
- no ebook binding is invented without byte custody;
- `FULL_TEXT_AVAILABLE` is kept outside the binding object.

## Current exact-head disposition

- #65 conceptual separation: **SUPPORTED**.
- fixture safety / no accepted Trek IDs: **CONFIRMED**.
- binding lifecycle/current-state semantics: **CONTESTED**.
- Source independence model: **PARTIAL / scalar overconstraint**.
- executable schema alignment: **OPEN**.
- common architecture integration: **OPEN**.
- actual literary Source binding: **BLOCKED on byte custody**.
- accepted coverage effect: **NONE**.

## Exact next frontier

First fix the Director six blockers plus LIB-AUD-001..007 on a successor head. Then run the corrected Librarian fixture set through the integrated v0.2 admission/provenance/diff pipeline and re-open Auditor review on those exact bytes. Do not scale to a franchise registry before this small fixture surface survives the combined gate.

No merge, binding acceptance, coverage advancement, source preference, or protected effect performed.
