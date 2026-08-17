# Director Synchronization — 2026-08-17

Role: DIRECTOR
Authority: coordination proposal only
Accepted state observed: `main` @ `007641c57933dda222489fff56555f6968ff2a53`

## Accepted state

Accepted `main` remains authoritative. The current accepted tree contains the skeletal README plus the unresolved one-byte top-level path `x`. The `x` path is tracked as accepted-state drift under issue #90 and has no assigned Trek corpus, governance, schema, registry, coverage, or research meaning. Issue #91 is a closed duplicate of #90.

No open or closed-unmerged governance, architecture, registry, reconciliation, coverage, or research proposal is accepted merely because it exists or has green CI.

## Current shared gates

### Governance

PR #4 remains the open byte-preserving proposal for the four Project-supplied governance files. PR #92 is closed-unmerged and therefore preserved only as proposal history, not an active review surface. Governance acceptance remains separate from architecture acceptance.

Before PR #92 closed, its branch reached head `be957be4a4f893d9467fc0e22cb74f896d20ae08`. That preserved proposal contains the corrected canonical flow `SOURCE -> WORK -> LOCAL ENTITY -> EVIDENCE -> ASSERTION -> ACCEPTED RECONCILIATION -> DETERMINISTIC PROJECTION -> QUERY DATABASE`, restores the governed `FULL_TEXT_AVAILABLE` coverage state in implementation methodology, and strengthens the bootstrap validator so governed record schemas are actually enforced. `validate-core` workflow run `32076118155` passed on that exact head, including repository validation, two projection builds, and deterministic output diff. Those bytes remain available for comparison/migration but do not reopen or supersede PR #4 or the current architecture gate.

A fresh Director audit of the closed #92 branch re-observed the canonical-projection incompleteness already governed by issue #76. Temporary issue #107 was closed as a duplicate of #76 rather than creating competing projection authority.

### Architecture / Consolidator

Issue #29 is the current architecture admission gate. Material remediation exists across PRs #33, #59, #64, #68, #71, #74 and integrated PR #82.

PR #82 is the preferred integrated execution surface. Current head `6a4489626617e5ddb7ead25493f15143291801db` is mergeable but not acceptance-ready. Workflow run `32076279046` fails during the integrated regression suite before repository validation or derived builds execute.

The latest two commits after Auditor-reviewed head `8491ae3` modify only contract/reconciliation tests. This is still useful progress: the prior `unittest.TestCase.run` helper collision is fixed and all 50 integrated tests now execute. Current result is 6 failures and 2 errors.

Current blocking implementation evidence:
- #67: non-STABLE transitions are still misclassified as `VALUE_CHANGED` and can still synthesize `CONFLICT_INTRODUCED` without an explicit governed conflict structure;
- #67: `STABLE -> CONTESTED` now reaches `STATUS_DEMOTED`, but incorrectly co-emits status-derived conflict;
- #67: reconciliation-history changes are still laundered into fact `VALUE_CHANGED` rather than a separate governed/provisional history channel;
- #76: full reachable provenance remains absent (`source_record` is missing in the contract test), so required Source/Evidence/Work/local-entity provenance observability is not yet implemented;
- #72: an accepted REJECTED disposition still leaves the assertion active as UNRESOLVED, so the compiler has not implemented effective assertion disposition;
- #61/#72: typed reconciliation application remains incomplete and does not yet produce the expected active fact without mutating worker-authored state.

Two remaining red cases appear primarily fixture/diagnostic maintenance rather than missing invariant enforcement:
- cross-subject supersession is rejected, but the test expects wording `different subject` while validation reports `different active key`;
- the formerly-valid batch/hash fixture now fails under the newer schema/predicate/subject contract and must be inspected/updated without weakening validation.

Positive latest delta:
- the test harness collision is resolved;
- `test_worker_proposed_status_is_not_authoritative` now passes;
- the suite reaches the complete integrated regression surface, making the remaining red failures actionable.

Required implementation order:
1. repair the two stale/brittle fixtures only where the intended invariant already holds;
2. close remaining #52/#55 admission and predicate-governance gaps from the Auditor delta;
3. implement typed #61/#72 reconciliation and compiler semantics;
4. implement #76 canonical provenance and required manifest outputs;
5. implement #67 semantic diff semantics against governed taxonomy without invented conflict or fact-history conflation;
6. obtain a complete green integrated run;
7. Auditor independently re-opens and tests the exact green bytes;
8. only then re-evaluate downstream SQLite/PostgreSQL/graph/search trust chains under #78.

AUD-ARCH-001 remains PARTIAL; AUD-ARCH-002, AUD-ARCH-003, and AUD-ARCH-004 remain OPEN. Do not route PR #82 to architecture acceptance while the integrated suite is red or those findings remain unresolved.

### Librarian Source↔Work gate

Issues #14 and #65 define the active Librarian dependency and binding contract. Fresh branch/PR inspection on 2026-08-17 found no Librarian-owned implementation branch or bounded registry/binding proposal. The only previously observed `librarian`-named branch is the older Director routing branch `architecture/librarian-bootstrap-route-001`, which does not create registry state.

Therefore accepted Source records, Work records, Source↔Work bindings, provenance-lineage registry state, and SOURCE_BOUND coverage remain absent.

The next Librarian tranche should be deliberately small and exercise the binding contract against audited hard cases such as the DS9 metadata/body mismatch and Prodigy segmentation, preserving uncertainty rather than canonicalizing worker staging.

### Coverage/admission

Issue #40 defines independent coverage ledgers and denominator rules, but accepted coverage machinery is still absent. Proposal-local staging counters, transcript-read receipts, or branch completeness do not advance accepted coverage.

### Calibration/audit

Issue #43 defines the calibration/adversarial regression policy. Corpus-derived fixed fixtures cannot become accepted truth until their Source/Work/Evidence basis is accepted and Auditor-verified. Synthetic invariants may proceed independently where they do not smuggle corpus conclusions into the oracle.

## Corpus queue synchronization

Issue #23 remains active and has been refreshed to this accepted-state snapshot. New episode/book close-read tranches are paused until accepted governance, usable accepted schema/predicate contracts, Librarian-owned Work/Source binding for the next Works, and governed coverage/admission machinery exist.

The hold was materially violated by earlier continued staging through at least TNG #89 and DS9 #85. Preserve those bytes as proposal/migration inputs; do not count them as accepted coverage and do not extend their provisional next-frontier text into further source-reading work.

Recent lane PRs #96–#100 are synchronization/preservation checkpoints rather than new authorized corpus expansion. Existing proposal branches remain preservation/migration inputs and must not be deleted or rewritten merely to simplify topology.

## Required next actions by role

CONSOLIDATOR:
1. continue PR #82 or an explicit successor using the implementation order above;
2. do not weaken red tests merely to obtain green CI;
3. do not invent accepted corpus records, global identities, Source/Work bindings, or semantic defaults to make tests pass.

AUDITOR:
1. re-audit the exact integrated green architecture head when it exists;
2. map original AUD-ARCH findings plus later Director contracts to CONFIRMED / RESOLVED / CONTESTED;
3. independently verify adversarial fixtures rather than accepting producer CI as proof.

LIBRARIAN:
1. create the first bounded Source/Work/source_work_binding implementation proposal under issues #14/#65;
2. preserve provenance families, independence, derivatives, container/member structure, mapping role/scope, lifecycle, supersession, and unresolved mappings;
3. do not convert provider metadata or worker staging into canonical truth merely because downstream batches are waiting.

SERIES / FILMS / LITERATURE WORKERS:
1. synchronize/preserve already completed work;
2. stop before new close-read tranches while #23 is active;
3. do not mint canonical Source/Work IDs, coverage semantics, predicates, or reconciliation state locally.

DIRECTOR:
1. keep issue #29, issue #23, issue #14, and this synchronization checkpoint current;
2. treat PR #4 as the active governance baseline proposal, closed #92 as preserved alignment history, and #82/successor as the implementation admission surface;
3. reassess acceptance readiness only after integrated implementation plus Auditor re-review and Librarian/coverage progress;
4. preserve accepted-state drift as unresolved until explicitly corrected through an authorized path.

## Protected effects

This synchronization authorizes no merge, force-push, branch deletion, deployment, credential/permission change, branch-protection change, accepted reconciliation decision, Source/Work acceptance, or coverage promotion.
