# Auditor delta — PR #82 integrated Consolidator head `8491ae3`

Date: 2026-08-17
Role: AUDITOR
Accepted `main` pin: `007641c57933dda222489fff56555f6968ff2a53`
Audited proposal: PR #82, `architecture/consolidator-v0.1-integration`
Audited head: `8491ae38219c23d4517c201a1192963104f15b06`
Base: `bf82c55eb764ccac2d4f253fe7f977df8a2f5b80`

## Disposition

**CONTESTED / RED TDD INTEGRATION CHECKPOINT.**

PR #82 is a useful convergence point because it finally places the hardened admission validator and the projection/query stack on one executable branch. It is not yet an acceptance-ready implementation of Director contracts #52, #55, #61, #67, #72, and #76.

The current CI failure is partly expected implementation lag and partly a test-oracle defect. The latter must be corrected before making the branch green; otherwise the branch can become deterministically wrong with excellent test coverage.

No merge, accepted-state mutation, reconciliation acceptance, coverage advancement, source binding, deployment, or protected effect is authorized or performed by this audit.

## Deterministic validation state

`validate-core` run `31816707164` on the exact audited head fails in the integrated regression-test step. Repository validation and all projection/query build steps are skipped after that failure.

Observed contract-alignment failures/errors before the suite aborts:
- diff status-change oracle;
- full-provenance oracle;
- reconciliation-history diff oracle;
- rejected-disposition projection oracle;
- typed reconciliation projection oracle;
- worker-proposed-status oracle.

The suite then crashes because `ReconTests` in `tools/test_reconciliation_validation.py` defines a helper method named `run(self, rows)`, overriding `unittest.TestCase.run(result)`. `unittest` passes its `TextTestResult` to that method and the helper attempts to iterate it as `rows`, raising `TypeError: 'TextTestResult' object is not iterable`.

### AUD-INT-001 — HIGH — reconciliation regression suite cannot execute

`tools/test_reconciliation_validation.py` must not override `unittest.TestCase.run` with a fixture helper. Rename the helper and update callers. In addition, the file's reconciliation fixtures still use the superseded raw `value` payload and omit required `subject_type` / `payload`, so fixing only the method name will reveal stale-schema failures rather than a valid reconciliation regression suite.

## Test-oracle contract drift

### AUD-INT-002 — CRITICAL — status/conflict oracle contradicts Director #67

`test_diff_uses_status_changed_not_fake_rank` constructs `STABLE -> CONTESTED` but requires `STATUS_CHANGED` and forbids `STATUS_DEMOTED`.

Director #67 defines:
- non-STABLE -> STABLE = `STATUS_PROMOTED`;
- STABLE -> any non-STABLE = `STATUS_DEMOTED`;
- `STATUS_CHANGED` is the proposed extension only for transitions among distinct non-STABLE states.

The same test requires `CONFLICT_INTRODUCED` solely because the new projection row is `CONTESTED`. The later #67 Director correction explicitly forbids deriving conflict introduction/resolution from projection-status buckets without a governed explicit conflict structure.

**Required correction:** use a non-STABLE transition such as `UNRESOLVED -> CONTESTED` for a provisional `STATUS_CHANGED` fixture, and do not require a conflict event unless the fixture also carries governed conflict structure.

### AUD-INT-003 — CRITICAL — identity-link oracle executes an invalid reconciliation decision

`active_decisions()` in `test_contract_alignment.py` constructs an ACCEPTED `ENTITY_LINK` using `SAME_AS` with `target_type = GLOBAL_ENTITY`, then expects the compiler to write that payload into `resolved_subject` / `resolved_entity`.

Current governed proposal state says:
- `SAME_AS` remains `EXPERIMENTAL` in the predicate registry;
- accepted ENTITY_LINK may not use an experimental identity predicate;
- #61 fixes ENTITY_LINK subject to `local_entity` and says its target should ordinarily be another local entity until a separate global-entity schema is governed;
- #61 expressly forbids generic identity-bucket collapse from an arbitrary ENTITY_LINK payload.

There is no governed `GLOBAL_ENTITY` record schema/index on this branch.

**Required correction:** the fixture must either remain PROPOSED/non-executable, or use an actually accepted identity-relation contract once one exists. Do not make compiler behavior green by legitimizing this invalid accepted decision.

### AUD-INT-004 — HIGH — accepted assertion incorrectly requires a disposition decision

`test_worker_proposed_status_is_not_authoritative` creates an Assertion whose immutable `status` is already `ACCEPTED` and expects the absence of an `ASSERTION_DISPOSITION` decision to produce `MISSING_ASSERTION_DISPOSITION`.

Director #72 says effective disposition begins from the immutable assertion record and is then overridden by an active accepted disposition decision if one exists. Therefore an already-ACCEPTED record needs no separate disposition decision to be eligible. Its missing **projection** decision should fail closed to UNRESOLVED.

The worker's `proposed_projection_status` is correctly non-authoritative, but the expected reason axis is wrong.

### AUD-INT-005 — MEDIUM — proposed diff extension tested as already canonical

`test_reconciliation_history_has_dedicated_diff_class` requires exact canonical class `RECONCILIATION_HISTORY_CHANGED`.

Director #67 proposes that extension but explicitly says it is not accepted merely by the comment; until governance accepts it, implementation should expose the delta through a versioned provisional/history channel rather than mislabel it as fact `VALUE_CHANGED`.

A regression can protect against `VALUE_CHANGED`, but should not silently promote the proposed taxonomy extension into accepted protocol semantics.

## Assertion schema / predicate governance

### AUD-INT-006 — HIGH — assertion subject domain exceeds current #52 contract

`schema/assertion.schema.json` allows:
- SOURCE
- WORK
- LOCAL_ENTITY
- EVIDENCE
- ASSERTION
- RECONCILIATION_DECISION

Current Director #52 v0.1 assertion subject domain is source/work/local_entity/assertion. Its only later correction concerns reconciliation supersession and states all other typed-subject guidance remains current.

Allowing `RECONCILIATION_DECISION` also creates a worker-assertion dependency onto Consolidator-owned reconciliation state, contrary to the intended layer boundary unless explicitly governed later.

**Required correction:** either restrict the v0.1 schema to the current contract or obtain an explicit superseding Director contract before expanding it.

### AUD-INT-007 — MEDIUM — predicate lifecycle metadata remains incomplete relative to #55 minimum

The v0.2 predicate registry materially improves the previous name/status-only list and does not promote the existing EXPERIMENTAL predicates. The validator now enforces lifecycle compatibility, subject typing, object mode, and typed object reference targets.

However #55's stated minimum governance also includes, where applicable:
- predicate supersedes / superseded_by lineage;
- methodology/registry-version provenance at the entry level;
- positive example **and near-miss/counterexample**.

`PREDICATE_METADATA_REQUIRED` and the current entries do not carry those fields. The registry is therefore strong partial implementation, not full #55 closure.

## Reconciliation validation

### AUD-INT-008 — HIGH — ASSERTION_DISPOSITION value set is wrong

Validator `DISPOSITIONS` is `{ACCEPTED, REJECTED, SUPERSEDED}`.

Director #72 defines reconciliation `ASSERTION_DISPOSITION` payload as `PROPOSED | ACCEPTED | REJECTED`; assertion `SUPERSEDED` should normally derive from explicit assertion lineage rather than a free-standing disposition flip.

Current validator therefore rejects a legal #72 `PROPOSED` disposition and accepts a forbidden/overloaded `SUPERSEDED` disposition.

### AUD-INT-009 — HIGH — SCOPE_RESOLUTION subject domain is too narrow

The validator currently requires `SCOPE_RESOLUTION.subject_type == ASSERTION`.

Director #61 permits typed assertion, Work, or Local Entity subjects. Orthogonal resolution keys for the same subject must coexist.

The active-key implementation correctly includes `resolution_key`, but the subject restriction prevents two of the three governed subject domains.

### AUD-INT-010 — HIGH — accepted scope keys remain anonymous free-form strings

The validator checks only that `resolution_key` is a nonempty string. Director #61 states that accepted SCOPE_RESOLUTION decisions must not use anonymous free-form keys whose semantics the compiler invents; the initial key registry/enumeration is an architecture choice, but governance is mandatory before acceptance.

No governed resolution-key registry/enumeration is present here.

### AUD-INT-011 — HIGH — ENTITY_LINK does not enforce Local Entity subject

Director #61 requires `ENTITY_LINK.subject_type = local_entity`.

The current validator relies on the selected identity predicate's subject typing instead. The registry's experimental identity predicates allow both `LOCAL_ENTITY` and `GLOBAL_ENTITY`, so a PROPOSED ENTITY_LINK can use an ungoverned GLOBAL_ENTITY subject and the validator has no GLOBAL_ENTITY record index to resolve it against.

Decision-type subject constraints must be enforced independently of predicate typing.

### AUD-INT-012 — HIGH — no effective-disposition gate for projection-status decisions

Director #72 requires `ASSERTION_PROJECTION_STATUS` to target an effectively ACCEPTED assertion; a projection-status decision targeting a non-accepted assertion is invalid.

The validator checks payload state and typed assertion subject existence, but does not compute/evaluate effective assertion disposition before admitting the projection-status decision. A PROPOSED/REJECTED assertion can therefore still carry an accepted projection-status decision through admission validation.

### AUD-INT-013 — HIGH — worker Source/Work ownership is still batch-root-local, not partition-wide

The validator rejects Source/Work/Reconciliation records discovered **inside a worker batch root**. It does not apply a generic path-level ownership rule to every authoritative `source` / `work` / binding record under `research/<lane>/...`.

Director #52 and #65 require authoritative Source/Work/binding ownership to remain outside worker research partitions regardless of whether a batch manifest happens to enclose the file.

This is the same underlying path-ownership gap previously identified against PR #33 and remains open in the integrated validator.

## Projection / provenance / diff integration

### AUD-INT-014 — CRITICAL — compiler is still the pre-#61/#72 implementation

`tools/build_projection.py` at the audited head is byte-identical to the previously audited compiler (`6324bf9...`). It still:
- recognizes old decision type `ASSERTION_STATUS` rather than `ASSERTION_DISPOSITION` + `ASSERTION_PROJECTION_STATUS`;
- reads raw reconciliation `value` instead of typed `payload`;
- filters worker assertions to `status == ACCEPTED` before reconciliation, so reconciliation cannot promote a PROPOSED assertion or demote an accepted one on the separate disposition axis;
- treats ENTITY_LINK as generic `resolved_entity` / `resolved_subject` payload;
- treats SCOPE_RESOLUTION as one opaque value per assertion rather than key-addressable orthogonal resolutions;
- cannot execute the schema it now validates.

This mismatch is exactly why the new projection contract tests fail/error. Do not weaken the tests to preserve this compiler.

### AUD-INT-015 — CRITICAL — provenance remains incomplete under #76

The compiler still projects only a narrow provenance subset: evidence/source/work IDs, evidence kind/locator, source hash/locator, and Work title.

It still drops canonical visibility for governed state required by #76, including Source lineage/variant/retrieval/provenance family/independence, Evidence observed/frame/epistemic/observer/fingerprint fields, Work structural/continuity/container fields, Source↔Work binding provenance, assertion disposition/projection/link/scope decision provenance, and full support/history semantics.

A change to several of those fields can alter input identity while leaving canonical provenance and `projection_hash` unchanged. AUD-ARCH-003 therefore remains open.

### AUD-INT-016 — HIGH — projection manifest still does not require canonical outputs

`schema/projection-manifest.schema.json` still defines `outputs` as an unconstrained object. #76 requires the complete canonical output set with filename/role, hash, and count, including deterministic empty outputs. Missing required outputs must fail validation.

The current manifest schema cannot enforce that.

### AUD-INT-017 — HIGH — semantic diff remains pre-#67 and test oracle must not force the wrong repair

`tools/diff_projection.py` remains the previously audited implementation. It still:
- emits VALUE_CHANGED for non-STABLE state changes;
- infers CONFLICT_INTRODUCED/RESOLVED from status buckets;
- treats same-ID subject/predicate/object mutation as ordinary VALUE_CHANGED instead of immutable-record corruption;
- ignores entity added/removed/metadata lifecycle;
- ignores relation lifecycle;
- compares provenance only over intersection, so appearance/disappearance of a support set can be silent;
- diffs all scope as one opaque blob rather than per resolution key;
- labels reconciliation-history additions/removals/changes as fact-style VALUE_CHANGED.

Director #67 and its corrections explicitly close these interpretations. The red contract tests are directionally right that this file needs replacement, but AUD-INT-002/005 show that the current new test oracle also needs correction first.

## Positive controls preserved

The integrated validator now materially supports several previously missing gates:
- schema required/type/enum/additional-property checks used by current schemas;
- unknown/untyped governed JSON failure;
- typed assertion subject existence checks for indexed types;
- typed object reference existence checks;
- predicate name/lifecycle/subject/object-mode checks;
- required research-batch count keys;
- lane worker_id checks including SHORT;
- batch hash/source-hash checks;
- accepted OTHER reconciliation rejection;
- decision payload shape checks for the new named decision types;
- supersession-cycle and same-active-key checks;
- accepted superseding decision reason requirement.

These are real improvements and should survive remediation.

## Required next implementation order

1. **Repair the regression oracle first**: rename `ReconTests.run`, update stale reconciliation fixtures, correct #67 status/conflict expectations, remove invalid accepted experimental SAME_AS/GLOBAL_ENTITY execution, and align effective-disposition expectations with #72.
2. Fix validator contract mismatches AUD-INT-006 through 013 while keeping all valid admission regressions green.
3. Rewrite projection application against #61/#72 typed payload/effective-disposition semantics.
4. Expand canonical provenance + projection manifest against #76.
5. Rewrite semantic diff against #67 and its Director corrections, using only governed/provisional taxonomy as appropriate.
6. Re-run the entire integrated suite, then rerun SQLite/PostgreSQL/graph/search adapter audits against the verified canonical-projection bundle rather than their current trust-on-input model.
7. Keep Source↔Work/coverage/calibration gates separate until their Librarian/implementation artifacts actually exist.

## Current closure state

- AUD-ARCH-001 admission validation: **PARTIALLY RESOLVED, still open**.
- AUD-ARCH-002 reconciliation/compiler: **OPEN / incompatible with current schema contract**.
- AUD-ARCH-003 provenance observability: **OPEN**.
- AUD-ARCH-004 semantic diff: **OPEN**.
- downstream SQLite/PostgreSQL/graph/search derivation-trust findings: **OPEN and downstream-blocked on canonical projection verification**.
- Librarian Source↔Work implementation: **NOT PRESENT**.
- coverage-ledger implementation: **NOT PRESENT**.
- calibration-runner implementation: **NOT PRESENT**.

This audit records proposal state only. Accepted coverage and accepted `main` are unchanged.
