# Auditor acceptance re-audit — PR #82 green head `205544b`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #82 `architecture/consolidator-v0.1-integration`
Previous audited head: `733e87c4917cba5149109c381f2c63a2652e0d46`
Current audited head: `205544bd93d18815bd56f347c413b972c9d3ee36`
Workflow: `validate-core` run `32077053424` — **SUCCESS**

## Disposition

**CONTESTED / NOT ACCEPTANCE-READY despite first complete green integrated run.**

The green run is meaningful: the prior test-harness/oracle failures were repaired, compiler/provenance work is now integrated, and the semantic diff implementation was substantially rewritten. Producer CI is no longer the blocker.

Independent adversarial review of the exact green bytes still finds acceptance-critical semantic defects that the current test suite does not cover.

## Delta scope from `733e87c`

Five commits changed only:

- `tools/diff_projection.py`
- `tools/test_diff_projection.py`
- minor fixture corrections in `tools/test_build_projection.py`, `tools/test_reconciliation_validation.py`, `tools/test_validate.py`

Validator/compiler implementation findings from `d822243` / `733e87c` therefore remain current unless explicitly closed by tests only. A green test cannot repair unchanged production code.

## Confirmed diff-engine progress

### 1. Governed core taxonomy is implemented conservatively

The diff engine now emits:

- ADDED_FACT / REMOVED_FACT
- VALUE_CHANGED only through explicit assertion supersession pairing
- STATUS_PROMOTED / STATUS_DEMOTED only for STABLE boundary crossings
- provisional, explicitly versioned `PROVISIONAL_STATUS_CHANGED` for non-STABLE transitions while #67 STATUS_CHANGED remains unaccepted
- ENTITY_LINK_CHANGED
- per-key SCOPE_CHANGED
- PROVENANCE_CHANGED
- CONFLICT_INTRODUCED / CONFLICT_RESOLVED from explicit contradiction relations, not merely status membership

Unaccepted entity/relation/reconciliation-history lifecycle events are explicitly prefixed `PROVISIONAL_` instead of being smuggled into root governance. This is the correct instinct.

### 2. Deterministic pairing avoids fuzzy similarity

Same assertion IDs pair directly. Successor assertion IDs pair only through explicit `supersedes`. Unrelated replacements become remove + add. This is directionally aligned with #67.

### 3. Manifest comparison context is carried into events

Diff events include old/new projection/input/schema/method/compiler/research/reconciliation/predicate/scope-key identities when manifests exist, improving traceability.

## Independently reproduced acceptance blockers

### AUD-GREEN-001 — CRITICAL — effective reconciliation can promote EXPERIMENTAL predicate semantics into active projection

This remains unchanged from the `733e87c` compiler finding.

Current validator predicate lifecycle checks inspect the worker-authored assertion `status`. An EXPERIMENTAL predicate is allowed when that record remains PROPOSED. Current reconciliation can then apply an accepted ASSERTION_DISPOSITION setting effective disposition to ACCEPTED. The compiler projects effectively ACCEPTED assertions but does not re-check predicate lifecycle/projection eligibility against the **effective** disposition.

Independent deterministic reproduction of the exact state transition gives:

- worker assertion status = PROPOSED + EXPERIMENTAL predicate -> validator lifecycle path permits collection;
- accepted disposition override -> effective assertion status = ACCEPTED;
- compiler active-partition condition -> assertion is projected.

This violates Director #55's core rule that experimental semantics remain non-promoted and must not become accepted consensus merely through a status change.

Required gate regression: PROPOSED + EXPERIMENTAL predicate + accepted disposition promotion must fail closed before active projection, with and without a STABLE projection-status decision.

### AUD-GREEN-002 — HIGH — PROPOSED/REJECTED successor assertion can suppress accepted predecessor

Unchanged production logic computes predecessor suppression from **every** assertion carrying `supersedes`, regardless successor effective disposition.

Independent deterministic reproduction:

- A = status ACCEPTED;
- B = status PROPOSED, `B.supersedes = A`;
- current `superseded_assertions` set contains A;
- `effective_disposition(A)` becomes SUPERSEDED.

Thus proposal lineage can remove accepted A from active projection before B itself is accepted. #72 does not authorize that.

Required gate regressions:
1. PROPOSED B supersedes ACCEPTED A -> A remains active;
2. REJECTED B supersedes ACCEPTED A -> A remains active;
3. define/test the exact accepted/effective-successor condition that deactivates A.

### AUD-GREEN-003 — HIGH — diff PROVENANCE_CHANGED is not orthogonal to status/value/scope/link changes

`provenance.jsonl` deliberately embeds full assertion records plus effective disposition, projection status, decision IDs, scope/link decision IDs and other reconciled fields.

`normalized_provenance()` strips only top-level provenance/assertion IDs when pairing a superseded assertion. It does **not** remove semantic assertion/status/scope/link fields before deciding whether provenance changed.

Independent deterministic reproduction using production-shaped provenance rows shows:

- identical Source/Evidence/Work provenance;
- only projection status changed UNRESOLVED -> STABLE;
- canonical provenance rows compare unequal;
- current diff therefore emits PROVENANCE_CHANGED in addition to STATUS_PROMOTED.

Likewise, explicit supersession with only object/value change causes nested `assertion_record` to differ and therefore manufactures PROVENANCE_CHANGED alongside VALUE_CHANGED even when support Source/Evidence provenance is unchanged.

This violates #67's atomic orthogonality. PROVENANCE_CHANGED is for provenance/support/lineage changes, not merely because the provenance row stores a copy of another semantic dimension.

Required regressions:
1. pure status change, identical support provenance -> STATUS_* only, **no PROVENANCE_CHANGED**;
2. pure resolved-scope change -> SCOPE_CHANGED only, absent actual provenance change;
3. pure identity-link change -> ENTITY_LINK_CHANGED only, absent actual provenance change;
4. explicit VALUE_CHANGED with identical support provenance -> VALUE_CHANGED only;
5. then repeat each with a real source/evidence/binding change and require both events.

### AUD-GREEN-004 — HIGH — conflict relation removal is automatically called RESOLVED

The diff engine emits CONFLICT_RESOLVED whenever a `CONTRADICTS` relation row disappears, regardless why it disappeared.

#67 explicitly warns that disappearance due scope movement, loss of evidence, rejected assertion, methodology change, or other removal is not automatically a semantic resolution of the contradiction.

The current test `test_removed_contradiction_relation_resolves_conflict` encodes the overly strong oracle directly: old relation present, new relation absent, no explicit resolution basis, expected CONFLICT_RESOLVED.

Required correction: distinguish explicit governed conflict resolution from mere conflict-record absence. At minimum fail closed/provisionally classify unexplained removal rather than assert resolution.

### AUD-GREEN-005 — HIGH — explicit supersession with changed proposition key aborts instead of remove+add

`assertion_pairs()` raises when an explicit successor changes `(subject_type, subject, predicate)`.

#67 says VALUE_CHANGED is appropriate only where proposition identity remains meaningfully continuous. When deterministic lineage exists but proposition key changes enough that continuity is not valid, the conservative fallback is REMOVED_FACT + ADDED_FACT rather than refusing the entire diff.

A correction must avoid fuzzy pairing while still allowing projections to be compared after legitimate explicit successor redesigns.

### AUD-GREEN-006 — MEDIUM/HIGH — inactive assertion-history/provenance changes can make projection diff fail without a representable event

Canonical projection includes historical PROPOSED/REJECTED/SUPERSEDED assertions and provenance. The diff engine compares active assertions plus entity/relation/reconciliation history, but it has no assertion-history lifecycle event surface for an inactive historical assertion added/removed.

A new inactive assertion can change assertion_history/provenance and therefore projection_hash while producing no active diff event. The final guard then raises `projection_hash changed but semantic diff produced no events`.

Failing closed is preferable to lying, but an acceptance-grade canonical diff must represent or explicitly version this canonical-history change rather than be unable to compare otherwise valid projections.

### AUD-GREEN-007 — CRITICAL / inherited #78 — green integrated derived consumers still consume unverified projection bundles

No shared canonical projection-bundle verifier was introduced on this green delta, and the previously audited SQLite/PostgreSQL/graph-search implementations did not change.

Therefore Director #78 remains open:

- consumers can still trust declared manifest/projection identity instead of recomputing required output hashes/counts/aggregate hash;
- partition/status consistency is not centrally verified;
- imported-output contracts and exact derivation receipts remain incomplete;
- backend builder identity remains independently incomplete where previously found;
- stale/mixed bundle attacks remain possible.

The green workflow proves deterministic behavior for the producer's fixtures, not a verified trust boundary.

## Inherited compiler/validator blockers still open at the green head

Because the relevant production files did not change after their audited checkpoints:

- **ENTITY_LINK cardinality remains invented** as one target per `(subject, relation_predicate)` without governed per-predicate cardinality.
- **Work-targeted SCOPE_RESOLUTION observability remains incomplete** because Work has no guaranteed current-state materialization when no active assertion uses the Work as subject.
- **Predicate use-level/scope metadata required by #55 remains absent.**
- **#65 Source↔Work binding provenance remains blocked** because no Librarian binding implementation exists.

## Green CI interpretation

Run `32077053424` is the first complete successful integrated run observed in this Auditor session. It is valuable evidence that the branch is mechanically coherent against its current tests.

It is **not** acceptance evidence for adversarial invariants the tests omit or encode incorrectly. Green tests certify their oracle, and the oracle still contains at least the conflict-resolution overclaim above while missing the effective-predicate/supersession/provenance-orthogonality cases.

## Finding status map

- **AUD-ARCH-001 validation:** PARTIAL; much stronger, still blocked by effective predicate lifecycle, assertion supersession activation, ENTITY_LINK cardinality, predicate use-level, positive Librarian ownership dependency.
- **AUD-ARCH-002 reconciliation application:** PARTIAL; major compiler implementation now exists, but above semantic blockers remain.
- **AUD-ARCH-003 canonical provenance/manifest:** STRONG PARTIAL; required output schema/hash/count/pins and rich provenance are present. Full closure waits on #65 binding provenance and correction of projection semantics that contaminate provenance/current state.
- **AUD-ARCH-004 semantic diff:** PARTIAL; substantial governed implementation exists but provenance orthogonality, conflict-resolution semantics, supersession fallback, and canonical inactive-history handling remain blocking.
- **AUD-DERIVED/#78:** OPEN / CRITICAL downstream trust boundary.

## Exact next frontier

1. Add red adversarial tests for AUD-GREEN-001 through -006 before changing implementation.
2. Correct validator/compiler effective predicate lifecycle and assertion supersession activation semantics.
3. Correct ENTITY_LINK cardinality and Work-scope materialization.
4. Normalize provenance comparison so semantic dimensions are diffed orthogonally.
5. Make conflict resolution require explicit governed resolution basis rather than mere disappearance.
6. Implement a shared #78 canonical bundle verifier and migrate every derived consumer to it.
7. Re-run integrated CI and independently re-audit the next exact green head.

No merge, acceptance decision, predicate promotion, reconciliation acceptance, database execution, accepted-state mutation, or protected effect performed.
