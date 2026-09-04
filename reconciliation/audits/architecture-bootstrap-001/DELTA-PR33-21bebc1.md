# Architecture audit delta — Consolidator PR #33 at 21bebc1

Role: AUDITOR  
Proposal audited: PR #33 `architecture/admission-validation-v0.1` @ `21bebc114d08dc639e9929478e262d9a3da67289`  
Parent architecture proposal: PR #1 current head `a26b444cd64be25c34cdb46c76721da7aeb777a2`

## Disposition

**AUD-ARCH-001: PARTIALLY RESOLVED IN PROPOSAL, STILL OPEN**

PR #33 materially strengthens admission validation and should receive credit for the exact classes it now proves. It does not close the full referential/admission finding yet.

## Confirmed improvements

Current `tools/validate.py` now deterministically enforces, for the current schema subset:

- required properties;
- declared primitive/object/array types;
- `const` and `enum`;
- `minLength` and `minItems`;
- unknown `record_type` rejection for records that reach validation;
- duplicate IDs;
- Source `derived_from` references;
- Work `parent_work_id` references;
- Local Entity `work_id` references;
- Evidence `source_id`, `work_id`, and optional observer-local-entity references;
- Assertion evidence references and assertion supersession references;
- Reconciliation evidence/assertion references and reconciliation supersession references;
- predicate-registry name membership for assertions;
- deterministic batch hash verification;
- declared batch record-count checks for keys supplied;
- manifest Work references;
- manifest source-hash membership against known Source content hashes;
- research-partition versus manifest worker ownership.

The PR also adds regression tests for:

1. schema-invalid Source missing `locator`;
2. dangling assertion evidence;
3. unregistered predicate;
4. batch hash mismatch;
5. canonical batch hash acceptance;
6. worker/partition mismatch.

The tests are wired into `validate-core`, and the current PR head has a successful workflow run.

These changes materially close several concrete examples in the original AUD-ARCH-001 finding.

## Remaining findings

### AUD-ARCH-001A — standalone JSON without record_type is silently invisible

**Verdict:** CONFIRMED  
**Severity:** CRITICAL

`iter_records()` handles `.json` and `.jsonl` differently.

For `.jsonl`, every nonblank object is yielded and later fails if `record_type` is missing.

For standalone `.json`, the function yields the object **only if** it is a dictionary that already contains `record_type`:

```python
if isinstance(obj, dict) and "record_type" in obj:
    yield path, obj
```

A governed-data file such as:

```json
{"source_id":"source-hidden","source_kind":"transcript","locator":"fixture://hidden"}
```

placed under `research/`, `reconciliation/`, `external/`, or `migrations/` is therefore silently ignored instead of rejected for missing `record_type`.

Consequences:
- CI can be green with structurally malformed JSON data in governed roots;
- the file is absent from ID/reference validation;
- if placed in a batch directory, it is also absent from `batch_records_for()` and therefore from the canonical batch hash.

**Required correction:** every JSON object/file in governed record locations must either be explicitly classified as a non-record artifact by path/type policy or be validated/rejected. Do not use `record_type` presence as the precondition for deciding whether a JSON object deserves validation.

Add a negative regression fixture for a standalone `.json` object missing `record_type`.

---

### AUD-ARCH-001B — assertion subject referential semantics remain unverifiable

**Verdict:** CONFIRMED SCHEMA/VALIDATOR GAP  
**Severity:** HIGH

The assertion schema requires `subject` to be a nonempty string, but neither the schema nor validator defines what record classes/ID domains a subject may reference.

`validate_references()` checks assertion evidence and `supersedes`, but never `subject`.

Therefore an assertion with a registered predicate, valid evidence, and `subject: "definitely-not-a-real-record"` can satisfy current deterministic checks.

This cannot be fixed responsibly by guessing that every subject must be a Local Entity; Work-, Source-, institution-, event-, or other typed subjects may eventually be legitimate. The schema needs an explicit subject-reference contract before the validator can enforce it.

**Required correction:** define allowed typed subject reference semantics and add positive/negative fixtures. Until then, do not describe PR #33 as full referential-integrity validation.

---

### AUD-ARCH-001C — reconciliation subject_id is not referentially validated

**Verdict:** CONFIRMED  
**Severity:** CRITICAL

A reconciliation decision requires `subject_id`, but `validate_references()` never checks that subject against an allowed existing assertion/entity/scope target. Decision-type-specific subject/value semantics also remain unenforced.

An `ACCEPTED` reconciliation decision can therefore pass schema/evidence/method checks while naming a nonexistent subject.

Because reconciliation decisions are intended to drive deterministic projection semantics, dangling reconciliation subjects are not a cosmetic defect.

**Required correction:** define target domains by reconciliation decision type (`ENTITY_LINK`, `ASSERTION_STATUS`, `SCOPE_RESOLUTION`, `SUPERSESSION`, etc.) and enforce subject/value references with regression fixtures.

---

### AUD-ARCH-001D — declared record-count validation is optional by key

**Verdict:** SUPPORTED WITH CAVEAT  
**Severity:** MEDIUM

`record_counts` is required to be an object, but the current batch-manifest schema does not require specific count keys. The validator verifies only keys that happen to be present.

A manifest with an empty `record_counts` object can therefore avoid count comparison entirely while remaining schema-valid.

This is primarily a schema-contract insufficiency rather than an implementation bug. If governed batches require complete count accounting, the schema must enumerate required count keys (or provide an explicit typed count structure) before validator enforcement can be complete.

## Other original architecture findings

PR #33 does not address:
- AUD-ARCH-002 deterministic application of accepted reconciliation decisions;
- AUD-ARCH-003 provenance-bearing canonical logical projection / projection hash;
- AUD-ARCH-004 semantic diff taxonomy.

Those remain open.

## Exact next frontier

1. Re-audit PR #33 successor after it adds a missing-record-type standalone JSON regression and reconciliation-subject validation contract.
2. Audit a separate compiler successor for AUD-ARCH-002/003/004; validator hardening alone cannot close the architecture gate.
