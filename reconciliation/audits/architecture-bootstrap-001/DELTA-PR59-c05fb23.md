# Architecture audit delta — logical projection PR #59 at c05fb23

Role: AUDITOR  
Proposal audited: PR #59 `architecture/logical-projection-v0.1` @ `c05fb23895248f2123ac4f96cdfe13703bb7d923`  
CI: `validate-core` run `31814700394` SUCCESS

## Disposition

**SUBSTANTIAL PROGRESS / AUD-ARCH-002 AND AUD-ARCH-003 REMAIN PARTIALLY OPEN**

PR #59 now implements a real deterministic logical projection and passes nine projection regressions. It materially resolves important portions of the original architecture findings. It does not yet support full reconciliation semantics or full provenance observability.

## Positive controls confirmed

The compiler now emits canonical:
- `entities.jsonl`;
- `facts.jsonl`;
- `relations.jsonl`;
- `contested.jsonl`;
- `unresolved.jsonl`;
- `provenance.jsonl`;
- accepted assertion history;
- accepted reconciliation history.

It also:
- preserves local entity identity while adding derived entity-link resolution;
- excludes superseded accepted decisions from active application while retaining accepted history;
- fails missing projection status closed to explicit `UNRESOLVED`;
- preserves `CONTESTED` and `STRUCTURAL_PARADOX` out of stable facts;
- rejects unknown reconciled projection-state strings;
- includes all emitted output hashes in `projection_hash`;
- includes Source/Work/Local Entity/Evidence plus accepted Assertion input content in `logical_input_records_hash`;
- makes source content-hash and locator changes visible through canonical provenance output and therefore projection hash;
- deliberately leaves `relations.jsonl` empty rather than inventing fact-vs-relation semantics absent from the predicate registry.

These are meaningful closures, not cosmetic changes.

## Remaining findings

### AUD-ARCH-002E — ASSERTION_STATUS is implemented as projection-status override, not assertion promotion/demotion

**Verdict:** CONFIRMED  
**Severity:** CRITICAL

The reconciliation contract states that accepted reconciliation owns `assertion promotions/demotions`.

Current compiler first computes:

```python
accepted_assertions = [record for record in assertions.values() if record.get("status") == "ACCEPTED"]
```

Only those assertions are ever projected.

Later, `ASSERTION_STATUS` is interpreted as a value from:

`STABLE | CONTESTED | UNRESOLVED | STRUCTURAL_PARADOX`

and used to override `projection_status`.

Consequences:
- an accepted reconciliation decision cannot promote a worker assertion from `PROPOSED` to accepted projection input because it was already filtered out;
- it cannot demote/reject/supersede an accepted worker assertion at the assertion-admission layer;
- the name `ASSERTION_STATUS` is being conflated with `projection_status`, whose state vocabulary is different from assertion record status (`PROPOSED`, `ACCEPTED`, `REJECTED`, `SUPERSEDED`).

**Required resolution:** define decision-type value semantics explicitly, separate assertion acceptance/promotion from projection disposition, and add fixtures proving promotion and demotion without rewriting worker evidence.

---

### AUD-ARCH-002F — untyped raw IDs make reconciliation application collision-prone

**Verdict:** CONFIRMED / DEPENDENT ON ISSUE #52  
**Severity:** CRITICAL

Decision indexing uses only `(decision_type, subject_id)`. Application similarly looks up raw IDs:
- ENTITY_LINK against local entity ID;
- ASSERTION_STATUS against assertion ID;
- SCOPE_RESOLUTION against assertion ID.

Current schema has no `subject_type` and ENTITY_LINK value is arbitrary JSON/string.

Therefore a reconciliation decision can be applied to the wrong record class if different ID domains collide, and the compiler has no typed target semantics to prevent it.

Director issue #52 now defines typed subject requirements. PR #59 should not be considered safe for real reconciliation application until the compiler consumes those typed semantics.

---

### AUD-ARCH-002G — SCOPE_RESOLUTION implementation covers only assertion subjects

**Verdict:** CONFIRMED  
**Severity:** HIGH

Issue #52 permits `SCOPE_RESOLUTION` subjects of assertion, work, or local entity.

Current compiler applies scope decisions only by looking up:

`("SCOPE_RESOLUTION", assertion_id)`

while processing assertions.

Work- or local-entity-scoped accepted resolutions are therefore retained in history but have no deterministic projection effect.

Additionally, scope value/dimension identity is still unconstrained, so one-active-per-raw-subject cardinality remains premature for potentially orthogonal scope dimensions.

---

### AUD-ARCH-003B — canonical provenance output omits material source/evidence provenance fields

**Verdict:** CONFIRMED  
**Severity:** CRITICAL

Current provenance rows include:
- assertion ID;
- evidence ID;
- source ID;
- work ID;
- evidence kind;
- evidence locator;
- source content hash;
- source locator;
- work title.

This is a major improvement, but current Source and Evidence schemas contain additional provenance/epistemic fields that are not emitted:

Source examples:
- `retrieved_at`;
- `source_variant`;
- `provenance_family`;
- `derived_from`.

Evidence examples:
- `observed`;
- `observer_local_entity_id`;
- `frame`;
- `epistemic_status`;
- `passage_fingerprint`.

A correction that changes only these omitted fields changes the compiler's `logical_input_records_hash` / `input_hash`, but does not change any canonical logical output row and therefore leaves `projection_hash` unchanged.

That is still provenance-semantic invisibility. It is particularly serious for source-lineage correction, evidence-frame correction, and observed-evidence correction because those can change witness independence or epistemic interpretation without changing an assertion string.

**Required correction:** canonical provenance output (or another canonical logical output included in `projection_hash`) must preserve the material source/evidence fields needed to make such corrections observable. Add provenance-only regression fixtures for source lineage and evidence frame/observed content, not only source content hash.

---

### AUD-ARCH-003C — Work provenance is underrepresented

**Verdict:** CONFIRMED  
**Severity:** HIGH

Provenance includes `work_id` and `work_title` but not current Work fields such as medium, series, continuity scope, or parent/container relationship.

A correction to Work containment/continuity metadata can therefore alter `input_hash` while leaving canonical projection outputs unchanged if title/ID and assertions remain the same.

This intersects the Librarian/container cases already found in Prodigy/literature. Work provenance needs enough canonical representation that material Work-binding/scope corrections are projection-visible.

---

### AUD-ARCH-003D — projection manifest schema still does not constrain canonical output contract

**Verdict:** SUPPORTED WITH CAVEAT  
**Severity:** MEDIUM

The implementation emits the intended canonical output set, but `projection-manifest.schema.json` still defines `outputs` only as a generic object. It does not require the canonical logical files or metadata shape.

A future compiler change could omit `provenance.jsonl` yet still satisfy the manifest schema.

**Required correction:** constrain the manifest output contract or add validation/regression proving required canonical logical outputs and their hash/count metadata cannot silently disappear.

## AUD-ARCH-004

Still OPEN. PR #59 does not implement the governed semantic diff taxonomy.

## CI interpretation

Green run 31814700394 is valid evidence for the nine implemented regression invariants and deterministic double build. It is not evidence for the missing reconciliation/provenance cases above because those cases are not yet in the oracle.

## Exact next frontier

1. Define/implement typed reconciliation subjects and decision-type value semantics before real mapping application is accepted.
2. Add assertion promotion/demotion fixtures distinct from projection-status disposition.
3. Expand canonical provenance to include material Source/Evidence/Work provenance and test provenance-only projection-hash sensitivity.
4. Implement AUD-ARCH-004 semantic diff separately.
