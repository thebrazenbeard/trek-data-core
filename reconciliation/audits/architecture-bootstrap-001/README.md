# Architecture bootstrap audit 001

Role: AUDITOR  
Accepted base: `main` @ `d58359a207da89e812d0a0330558c66774ed1241`  
Primary proposal audited: PR #1 `architecture/v0.1-bootstrap` @ `07b5152e2a6bcb18768e9eb7800a74cbc013d6ef`  
Successor hardening inspected: PR #8 `architecture/projection-input-identity-v0.1` @ `87cbdd89528a1861173c20b009db9182b315ea56`  
Disposition: **CONTESTED — do not treat the architecture proposal as acceptance-ready yet**

This audit does not merge, rewrite, or repair either proposal. It records deterministic and semantic findings against the current Project method and repository/build protocol.

## Accepted-state observation

Accepted `main` contains only `README.md`. None of the architecture, schema, research, reconciliation, or projection files in PR #1 or PR #8 are accepted state yet.

## Validation performed

- Inspected PR #1 changed-file set and head.
- Inspected `tools/validate.py`, `tools/build_projection.py`, `tools/diff_projection.py`, evidence/source/work/batch/reconciliation schemas, and predicate registry on the proposal branch.
- Inspected PR #1 CI run `31793416370`; `validate-core` completed successfully.
- CI log shows `VALIDATION PASSED: 0 identified records`, followed by two identical empty projection builds.
- Reproduced the validator's relevant acceptance logic with an adversarial malformed assertion: an assertion containing only `record_type`, `assertion_id`, and a non-empty list naming a nonexistent evidence ID produces no validation error under the current checks even though the JSON Schema requires `subject`, `predicate`, `object`, and `status`.
- Inspected PR #8's hardened `build_projection.py` and confirmed that it fixes missing build-identity pins but leaves the validator and logical-output model below unchanged.

## Findings

### AUD-ARCH-001 — schema and referential validation are not enforced

**Verdict:** CONFIRMED  
**Severity:** CRITICAL

`tools/validate.py` does not load or apply the repository's JSON Schemas. It currently checks record-type/id presence and uniqueness, requires an assertion's `evidence` array to be non-empty, and requires `method` on accepted reconciliation decisions.

It does not verify, among other things:

- required schema fields;
- field types/enums;
- assertion evidence IDs actually exist;
- evidence `source_id` and `work_id` actually exist;
- local-entity references exist and remain within the intended batch/lane;
- assertion predicates exist in the governed predicate registry or have an allowed status;
- supersession targets exist and are type-compatible;
- batch manifest record counts, source hashes, or `batch_hash` match batch contents.

A malformed record can therefore pass CI while violating the schema and provenance graph.

**Recommended correction:** make schema validation and cross-record referential validation mandatory; add adversarial fixtures that must fail CI.

---

### AUD-ARCH-002 — accepted reconciliation decisions are not applied to the logical projection

**Verdict:** CONFIRMED  
**Severity:** CRITICAL

Both PR #1 and the PR #8 hardening select research assertions whose research record already says `status == ACCEPTED`, write them unchanged to `accepted_assertions.jsonl`, and separately write accepted reconciliation-decision records to `accepted_reconciliation.jsonl`.

The compiler does not deterministically apply decision types such as:

- `ASSERTION_STATUS`;
- `SCOPE_RESOLUTION`;
- `SUPERSESSION`;
- `ENTITY_LINK`.

That means an accepted reconciliation decision can exist while the projection still exposes the unreconciled research assertion unchanged. A downstream query/database layer would have to interpret the decision itself, moving semantic reconciliation out of the deterministic compiler and defeating the stated projection model.

**Recommended correction:** implement deterministic application of accepted reconciliation decisions into canonical logical outputs while preserving the immutable decision history separately. Ambiguous/contested cases must remain explicitly represented rather than collapsed.

---

### AUD-ARCH-003 — projection identity is provenance-blind

**Verdict:** CONFIRMED  
**Severity:** CRITICAL

PR #8 improves `input_hash` by pinning research head, reconciliation head, schema version, methodology version, predicate-registry hash, compiler commit, and the two accepted-output hashes.

However, the canonical logical projection still contains only:

- `accepted_assertions.jsonl`;
- `accepted_reconciliation.jsonl`.

Source, Work, Local Entity, Evidence, and provenance records are absent from the logical outputs and `projection_hash`.

Therefore a material provenance correction — for example a changed source hash, evidence locator, evidence frame, source lineage, or source/work binding — can leave `projection_hash` unchanged if the assertion and reconciliation JSON are unchanged. That contradicts the requirement that semantic/provenance changes be traceable through deterministic logical projection state.

**Recommended correction:** include canonical provenance/evidence linkage in the logical projection (or an equivalently content-addressed canonical output whose hash participates in `projection_hash`) so `PROVENANCE_CHANGED` and source-binding corrections are observable without relying only on Git-head metadata.

---

### AUD-ARCH-004 — projection diff taxonomy is too coarse for the governed protocol

**Verdict:** CONFIRMED  
**Severity:** HIGH

`tools/diff_projection.py` currently emits only:

- `ADDED`;
- `REMOVED`;
- `CHANGED`.

The Project protocol requires semantically meaningful classes including:

- `ADDED_FACT`;
- `REMOVED_FACT`;
- `VALUE_CHANGED`;
- `STATUS_PROMOTED`;
- `STATUS_DEMOTED`;
- `ENTITY_LINK_CHANGED`;
- `SCOPE_CHANGED`;
- `PROVENANCE_CHANGED`;
- `CONFLICT_INTRODUCED`;
- `CONFLICT_RESOLVED`.

The current diff therefore cannot support the audit trail the architecture promises.

**Recommended correction:** classify deterministic logical diffs by semantic field/record meaning and preserve a generic fallback only for genuinely unclassified changes.

---

### AUD-ARCH-005 — PR #1 build identity is incomplete; PR #8 is a valid partial correction

**Verdict:** CONFIRMED / PARTIALLY RESOLVED IN PROPOSAL  
**Severity:** HIGH on PR #1; resolved for the named identity fields by PR #8

PR #1 writes `research_head`, `reconciliation_head`, and `predicate_registry_hash` as null and allows methodology/compiler identity to be defaulted or unpinned. PR #8 correctly changes those to required pinned inputs and hashes the predicate registry.

This is a real improvement, but PR #8 does not resolve AUD-ARCH-001 through AUD-ARCH-004.

## CI interpretation

PR #1's green CI is valid evidence that its current code executes deterministically on its current **empty research/reconciliation record set**. It is not evidence that malformed corpus records, broken references, reconciliation semantics, provenance changes, or required semantic diff classes are handled correctly.

The run's own output says `VALIDATION PASSED: 0 identified records`.

## Audit disposition

**CONTESTED**

Do not infer acceptance-readiness from the green workflow alone. Before the architecture becomes accepted project state, at minimum AUD-ARCH-001 and AUD-ARCH-002 should be closed, and the projection/provenance contract in AUD-ARCH-003 plus semantic-diff requirement in AUD-ARCH-004 should have an explicit accepted resolution.

PR #8 should be considered a partial hardening dependency rather than proof that the foundation is complete.

## Exact next frontier

1. Audit any successor proposal that closes AUD-ARCH-001/002 with adversarial invalid-record fixtures and reconciliation application tests.
2. Verify provenance changes alter canonical logical projection state in the intended way.
3. Verify semantic diff fixtures exercise promotion, demotion, identity-link, scope, provenance, and conflict transitions.
4. Only after the architecture gate is adequate should staged research PRs be audited for promotion into governed accepted batches.
