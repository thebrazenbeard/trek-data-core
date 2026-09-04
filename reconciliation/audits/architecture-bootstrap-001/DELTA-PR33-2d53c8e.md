# Architecture audit delta — Consolidator PR #33 at 2d53c8e

Role: AUDITOR  
Proposal audited: PR #33 `architecture/admission-validation-v0.1` @ `2d53c8ebe20925241e6de15965b346b4fa325114`

## Supersession status

This delta supersedes only the open/closed status of subfindings recorded against earlier PR #33 head `21bebc114d08dc639e9929478e262d9a3da67289`.

### AUD-ARCH-001A — standalone JSON without record_type

**RESOLVED IN PROPOSAL HEAD `2d53c8e`**

`iter_records()` now yields every standalone governed JSON object and rejects non-object JSON. Missing `record_type` therefore reaches normal validation and fails. Regression test `test_untyped_json_in_governed_data_root_is_rejected` explicitly covers the prior bypass.

### AUD-ARCH-001D — required core batch count keys

**RESOLVED IN PROPOSAL HEAD `2d53c8e` FOR CURRENT CONTRACT**

The validator now requires `local_entities`, `evidence`, and `assertions` keys in governed research batch `record_counts`, and regression test `test_core_batch_count_keys_are_required` covers omission.

This is appropriately narrower than requiring Source/Work counts in every worker batch because Source/Work ownership may remain external to a research batch.

### AUD-ARCH-001B — assertion subject referential semantics

**STILL OPEN / HIGH**

Assertion `subject` remains only a nonempty string in the current schema. `validate_references()` still validates assertion evidence and supersession but not the subject target.

This is now best classified as a schema+validator contract gap, not merely missing code. The system must define which target record classes/ID namespaces are legal assertion subjects before deterministic enforcement can be correct.

### AUD-ARCH-001C — reconciliation subject_id / decision target semantics

**STILL OPEN / CRITICAL**

Reconciliation `subject_id` still has no decision-type-specific target validation. An accepted reconciliation decision can carry valid evidence/method/supersession and still name a nonexistent or wrong-class subject.

Before reconciliation decisions are deterministically applied, the schema must define target/value domains for at least `ENTITY_LINK`, `ASSERTION_STATUS`, `SCOPE_RESOLUTION`, and `SUPERSESSION`, followed by positive and negative fixtures.

## CI

`validate-core` run 33 at this exact head completed successfully. This is meaningful evidence for the current eight validator regression tests; it does not close the two target-domain gaps above.

## Overall AUD-ARCH-001 status

**PARTIALLY RESOLVED; substantially narrowed.**

The original generic validator is no longer fairly described as doing only ID/evidence-presence checks. Current PR #33 now provides real schema-subset, reference, predicate, batch-integrity, source-hash, and partition enforcement.

Remaining admission work is now primarily semantic referential typing for assertions/reconciliation plus any future coverage-transition contract.

## Other architecture findings unchanged

AUD-ARCH-002, AUD-ARCH-003, and AUD-ARCH-004 remain outside this PR's current implementation scope and remain open.
