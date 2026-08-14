# Architecture audit delta — Consolidator PR #33 at bfe5515

Role: AUDITOR  
Proposal audited: PR #33 `architecture/admission-validation-v0.1` @ `bfe5515eeae65194e087d4b99fc5d378e38e16e7`

## Disposition

**AUD-ARCH-001 remains PARTIALLY RESOLVED / materially stronger.**

This successor implements the prior red worker-ownership test, adds reconciliation supersession/active-decision checks, runs all `test_*.py` files in CI, and is green at workflow run 46.

It does not yet satisfy the full typed-reference/ownership contract in Director issue #52.

## Improvements confirmed

### Worker-batch payload ownership

The validator now rejects `source`, `work`, and `reconciliation_decision` record types when they occur inside a recognized worker-owned batch root. This is a useful concrete enforcement of the producer-owned payload boundary.

### Reconciliation history integrity

The validator now checks several useful invariants for accepted reconciliation records:
- accepted supersession requires nonempty reason and evidence;
- a superseding decision must preserve decision type and subject ID relative to its predecessor;
- supersession cycles are rejected;
- multiple active `ENTITY_LINK`, `ASSERTION_STATUS`, or `SCOPE_RESOLUTION` decisions for the same raw subject ID are rejected.

Regression tests cover active-link conflict, missing supersession reason, valid supersession, cross-subject supersession, and cycle rejection.

These are useful history-integrity controls. They are not equivalent to deterministic reconciliation application (AUD-ARCH-002).

## Remaining / new findings

### AUD-ARCH-001E — worker Source/Work ownership is enforced only inside manifest batch roots

**Verdict:** CONFIRMED  
**Severity:** HIGH

Director issue #52 requires authoritative Source/Work records referenced by worker Evidence/Local Entity records to resolve to a Librarian-owned registry/binding surface **outside the worker's research partition**.

Current `validate_batch_integrity()` checks forbidden record types only for `batch_records_for(manifest_path, records)` when `expected_worker_for_path(manifest_path)` is recognized.

Therefore a Source or Work record placed under a known worker lane but outside the manifest's batch directory, for example conceptually:

`research/tng/loose-source.json`

is not rejected by the current ownership logic merely because it is inside the TNG partition. It can enter the global record index and satisfy worker Evidence references.

The current test fixture avoids this by placing registry records in `research/_registry/`, but the validator does not establish `_registry` as a governed Librarian-owned surface and does not prohibit authoritative Source/Work records elsewhere under `research/tng/...`.

**Required correction:** enforce ownership/location at the record-path level, not only at batch-root membership. At minimum reject authoritative Source/Work records under known research-worker lane subtrees unless an explicitly governed derived/cache exception exists. The eventual Librarian registry path/surface should be architectural, not inferred from a test fixture name.

---

### AUD-ARCH-001B — assertion typed subject contract remains unimplemented

**Verdict:** CONFIRMED  
**Severity:** HIGH

Issue #52 now defines the Director contract: governed assertions need explicit `subject_type` and `(subject_type, subject)` existence validation.

Current assertion schema and validator remain unchanged on this point. Assertion subject is still an untyped nonempty string and `validate_references()` does not validate it.

This is no longer an ambiguous requirement; it is an implementation gap.

---

### AUD-ARCH-001C — reconciliation typed subject contract remains unimplemented

**Verdict:** CONFIRMED  
**Severity:** CRITICAL

Current reconciliation schema still requires only untyped `subject_id`; no `subject_type` exists. The new reconciliation tests themselves demonstrate the gap: their `ENTITY_LINK` fixtures use `subject_id: local-1` without providing a Local Entity record, and the valid-supersession fixture is accepted.

The new checks compare subject IDs between decisions but do not prove the subject exists or is a legal target type for the decision type.

Issue #52 now supplies a typed-subject contract, so this should be implemented or explicitly deferred to reconciliation remediation behind a failing fixture.

---

### AUD-ARCH-002A — reconciliation value/application semantics remain underdefined

**Verdict:** CONFIRMED / SEPARATE RECONCILIATION GATE  
**Severity:** CRITICAL

The new validator introduces active-decision conflict rules, but the reconciliation schema's `value` remains unconstrained JSON.

For `ENTITY_LINK`, typing only the subject would define one side of a mapping; deterministic application still needs a typed/versioned target value. `ASSERTION_STATUS` needs legal status value/transition semantics. `SCOPE_RESOLUTION` needs an explicit scope value model.

This belongs primarily to AUD-ARCH-002 rather than admission validation. Do not close deterministic reconciliation merely because supersession history is internally consistent.

---

### AUD-ARCH-002B — single-active SCOPE_RESOLUTION is premature without scope identity semantics

**Verdict:** PROVISIONAL CONFLICT  
**Severity:** HIGH

Current validator groups active `SCOPE_RESOLUTION` decisions only by `(decision_type, subject_id)` and rejects more than one.

The governing method permits multiple dimensions of scope/continuity to become relevant lazily. A single assertion or local entity may eventually require independently governed timeline, narrative-frame, continuity, jurisdiction, or other scope dimensions.

Until `SCOPE_RESOLUTION.value` or a scope key/type defines whether one decision is intended to contain all dimensions or whether orthogonal resolutions may coexist, enforcing one active scope-resolution record per raw subject may reject legitimate future structures.

**Required resolution:** define scope-resolution identity/value semantics before treating this cardinality rule as a permanent invariant. A synthetic fixture should cover two orthogonal non-conflicting scope resolutions if the model permits them.

## CI interpretation

Workflow run 46 is green on this exact head and now runs all validator/reconciliation unit tests. This is meaningful positive evidence for the implemented invariants. It does not supply the missing typed-subject/value semantics above.

## Other architecture findings

AUD-ARCH-003 (provenance-bearing logical projection/hash) and AUD-ARCH-004 (governed semantic diff taxonomy) remain unchanged/open.

## Exact next frontier

Re-audit the next PR #33 successor only if it changes Source/Work record-location ownership or typed assertion/reconciliation subjects. Otherwise move to a separate reconciliation/compiler proposal for AUD-ARCH-002/-003/-004.
