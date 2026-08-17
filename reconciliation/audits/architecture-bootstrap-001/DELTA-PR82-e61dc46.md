# Auditor delta — PR #82 head `e61dc46`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #82 `architecture/consolidator-v0.1-integration`
Previous audited head: `1c209a4898ff52e0b7ddaec577c3d5714008311e`
Current audited head: `e61dc464d28819fb9ff43ce59ece2b4bb6e51204`
Workflow: `validate-core` run `32077762749` — FAILURE

## Delta scope

One commit rewrites only `tools/build_projection.py`.

## Confirmed closures/progress

### Compiler -> verifier interoperability defect — RESOLVED

The compiler no longer writes the two legacy compatibility JSONL aliases (`accepted_assertions.jsonl`, `accepted_reconciliation.jsonl`) into the canonical bundle.

It now emits exactly the eight #76 canonical JSONL outputs plus `manifest.json`, then dynamically loads `projection_bundle.py` and calls `verify_projection(out)` on the exact directory it just produced.

This closes the prior critical incompatibility where the shared verifier rejected the compiler's own output for unexpected JSONL files.

### Pre-build repository validation added

`build_projection.py` now invokes the repository admission validator before reading/compiling repository records and fails closed when validation returns nonzero.

This is the correct sequencing direction: deterministic compilation no longer bypasses the current admission gate merely because direct `build_logical_projection()` can be called in tests.

### Canonical manifest/output behavior retained

The rewrite preserves the explicit eight-output manifest/hash/count family, complete governing/input pins, rich provenance, typed relation rows and immediate post-write bundle verification.

## Semantic blockers that survive unchanged

### EXPERIMENTAL predicate effective-promotion hole — STILL CRITICAL

The compiler still decides active assertion inclusion from reconciled effective disposition but does not re-check predicate lifecycle/projection eligibility against that effective disposition.

Because repository validation still permits an EXPERIMENTAL predicate on a worker-PROPOSED assertion, an accepted disposition decision can promote it to effective ACCEPTED and the compiler can project it.

Running repository validation first does not close a validator semantic hole.

### Inactive assertion successor suppression — STILL HIGH

The compiler still builds:

`superseded_assertions = {a.supersedes for every assertion carrying supersedes}`

without filtering successor assertions by effective disposition. A PROPOSED/REJECTED successor can therefore make an ACCEPTED predecessor effectively SUPERSEDED.

### ENTITY_LINK cardinality invention — STILL HIGH

Active decision keys still identify ENTITY_LINK by `(decision_type, subject_type, subject_id, relation_predicate)` without target ID or governed predicate cardinality. Multiple legitimate targets under one relation predicate remain impossible.

### Work-targeted scope observability — STILL HIGH

The compiler still has no canonical Work-state output. A valid accepted Work SCOPE_RESOLUTION can remain visible only through reconciliation history/input identity unless an active assertion happens to use that Work as its subject. Accepted executable Work-scope effects need guaranteed current-state materialization.

### Predicate use-level contract — STILL HIGH

No compiler/registry change in this rewrite adds the #55 explicit predicate use-level distinction. Typed-reference assertions continue to produce `ASSERTION_PREDICATE` relation rows without a governed assertion-vs-reconciliation/multi-level use contract.

## Additional build hygiene note

The compiler writes into an existing output directory and relies on the strict post-write verifier to reject stale unexpected JSONL files. This is fail-closed, which is acceptable for correctness, but it means a directory containing obsolete compatibility aliases from a prior build will cause the new build to fail rather than self-clean.

That is preferable to silently ignoring stale files. A future usability improvement could build into a fresh temporary canonical directory and atomically replace the target after verification, mirroring SQLite's approach.

## Status update

- compiler/verifier exact-bundle interoperability: **RESOLVED**;
- pre-build validator gate: **CONFIRMED**;
- AUD-ARCH-002 reconciliation application: still **PARTIAL**, blocked by effective predicate lifecycle, assertion supersession and identity-cardinality semantics;
- AUD-ARCH-003 canonical output/manifest plumbing: structurally strong; #65 binding provenance and semantic correctness still block full closure;
- broader PR #82: **CONTESTED / RED**.

## Exact next frontier

Fix the validator/compiler semantic blockers rather than relying on pre-build validation to bless them. Then rerun the full integrated suite and independently re-audit the next exact head, including compiler -> verifier -> all derived adapters.

No merge, assertion/predicate acceptance, reconciliation acceptance, accepted-state mutation, or protected effect performed.
