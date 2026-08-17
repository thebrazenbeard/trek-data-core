# Director Synchronization — 2026-08-17

Role: DIRECTOR  
Authority: coordination proposal only  
Accepted state: `main` @ `007641c57933dda222489fff56555f6968ff2a53`

## Accepted state

Accepted `main` remains authoritative. Its meaningful Trek state is still the skeletal README plus unresolved one-byte top-level path `x`. The `x` path remains accepted-state drift under #90 and has no assigned corpus, governance, schema, registry, coverage, or research meaning.

No proposal becomes accepted because it exists, is complete, or has green CI.

## Governance

PR #4 remains the open governance-only proposal containing the four Project-supplied root governance files with prior byte-custody support. PR #92 is CLOSED UNMERGED and preserved only as governance/bootstrap alignment history; it is not the current architecture integration path.

Convergence route:
1. preserve the audited root governance bytes;
2. repair the current integrated architecture line (#82 or explicit successor);
3. obtain a complete green integrated run plus independent Auditor re-review;
4. carry the audited root governance files onto that current integration lineage or a clean successor.

Any governance merge remains a protected effect requiring Patrick's explicit authorization.

## Architecture / Consolidator

Issue #29 is the current architecture gate. Integrated PR #82 is the preferred implementation surface.

Current #82 head: `6a4489626617e5ddb7ead25493f15143291801db`.

Current workflow: `32076279046` = RED. Unlike the earlier head, the `unittest.TestCase.run` helper collision is fixed and all 50 integrated tests now execute. Current result is 6 failures and 2 errors, so this is real narrowing rather than a generic broken harness.

Current load-bearing failures/gaps:
- #67: non-STABLE transitions are still misclassified as `VALUE_CHANGED` and can synthesize `CONFLICT_INTRODUCED` without governed conflict structure;
- #67: `STABLE -> CONTESTED` reaches `STATUS_DEMOTED` but still wrongly co-emits status-derived conflict;
- reconciliation-history changes are still being mislabeled as fact `VALUE_CHANGED` instead of a separately governed/provisional history channel;
- #76: full reachable Source/Evidence/Work/local-entity provenance remains incomplete (`source_record` is absent in the contract test);
- #72: accepted REJECTED disposition still leaves an assertion active as UNRESOLVED, so effective assertion disposition is not implemented correctly;
- #61/#72: typed reconciliation application still does not produce the expected active fact without mutating worker-authored state;
- remaining Auditor gaps in #52/#55 subject/ownership/predicate governance still require implementation.

Two red cases appear primarily fixture/diagnostic maintenance rather than absent invariants:
- cross-subject supersession is rejected, but test wording expects `different subject` while validator reports `different active key`;
- a formerly-valid batch/hash fixture is now stale under newer schema/predicate/subject requirements and must be updated without weakening validation.

Required order:
1. repair only stale/brittle fixtures where the intended invariant already holds;
2. close remaining #52/#55 admission gaps;
3. implement typed #61/#72 reconciliation and effective disposition/projection-state semantics;
4. implement #76 canonical provenance plus required manifest outputs;
5. implement #67 diff semantics without invented conflict or fact/history conflation;
6. obtain one complete green integrated run;
7. Auditor independently re-opens and tests that exact head;
8. only then re-audit SQLite/PostgreSQL/graph/search trust under #78.

AUD-ARCH-001 remains PARTIAL. AUD-ARCH-002, -003, and -004 remain OPEN. Green sibling PRs do not close this integrated gate.

## Librarian Source↔Work gate

Issues #14 and #65 remain the active Librarian dependency and binding contract.

A genuine Librarian execution branch now exists: `external/librarian/crosswalk-intake-v1`. This corrects the earlier Director observation that only the routing branch existed.

Current Librarian proposal/checkpoint artifacts under `proposals/librarian/legacy-intake/`:
- `ST_LIBRARIAN_CUSTODY_INTAKE_V1.json`;
- `ST_LIBRARIAN_COLLISION_RECOVERY_QUEUE_V1.json`;
- `ST_LIBRARIAN_EXTERNAL_CROSSWALK_TRANCHE_001.json`;
- `ST_LIBRARIAN_EXTERNAL_CROSSWALK_TRANCHE_002.json`.

Verified current meaning:
- two reported ebook ZIPs remain not byte-exposed to the Librarian, so no hashes or Source IDs are fabricated;
- custody rules fail closed until readable bytes + hashes exist;
- external crosswalk work covers the 14 preserved legacy candidate Works using Memory Alpha, Memory Beta, and publisher metadata as candidate metadata only;
- edition/reprint/eBook/audio distinctions, container/member structure, metadata conflicts, derivative lineage, and source-independence limits are preserved rather than collapsed;
- collision-recovery artifacts preserve historical aggregate classes and a deterministic first-byte workflow;
- accepted Work IDs created: 0;
- accepted Source IDs created: 0;
- accepted Source↔Work bindings created: 0;
- accepted coverage advancement: 0.

The existing Librarian artifacts pin an older accepted head as historical checkpoint provenance. Do not rewrite that history merely to make it current. The next tranche should refresh accepted state against current `main` while preserving the earlier checkpoint.

Issue #14 therefore remains OPEN. Exact next Librarian frontier:
1. obtain a byte-addressable ebook container or another suitable byte-backed fixture;
2. hash physical container/member bytes and establish provenance-family / `derived_from` relationships;
3. create a small #65-conforming Source + Work + `source_work_binding` proposal with one-to-many/many-to-one support and unresolved mappings preserved;
4. route those exact bytes to Auditor.

External metadata expansion is useful bounded Librarian work but does not substitute for byte-backed Source/Work/binding implementation.

## Coverage / calibration

Issue #40 defines independent coverage ledgers and denominators, but accepted coverage machinery remains absent. Proposal counters, source-read receipts, sync totals, and close-read packets do not advance accepted coverage.

SOURCE_BOUND remains distinct from FULL_TEXT_AVAILABLE and later structural/semantic/audit states.

Issue #43 governs calibration/adversarial regression. Synthetic invariant fixtures may proceed without corpus claims; real Trek fixtures require accepted Source/Work/Evidence provenance before becoming canonical regression truth.

## Corpus queue

Issue #23 remains ACTIVE. New episode/book close-read tranches remain paused until accepted governance, accepted usable schema/predicate contracts, Librarian-owned binding for the next Works, and governed coverage/admission machinery exist.

Preservation/synchronization checkpoints are legitimate when they only inventory completed proposal bytes and stop. Discovery #96 and TAS #97 are examples.

Recent hold cleanup already recorded:
- DS9 #103 closed unmerged after new five-work throughput under the hold;
- DS9 #106 closed unmerged after another five-work tranche appeared after the DS9 stop/sync checkpoint;
- TNG staging #84, #86, #87, #88, #89 closed unmerged;
- all underlying research branches/commits remain preserved;
- accepted coverage remains zero for those proposal packets.

Any future DS9 synchronization must include preserved batch 027 (#106) while still recording zero accepted coverage and no authorization for another tranche.

Lane-local `exact next frontier` text never overrides #23.

## Next actions by role

CONSOLIDATOR: continue #82/successor in the order above; do not weaken legitimate red tests or invent accepted corpus state.

AUDITOR: wait for substantive corrected integrated bytes, then independently re-open them and map AUD-ARCH-001..004 plus later Director contracts to explicit dispositions.

LIBRARIAN: preserve current fail-closed custody/crosswalk work, obtain byte-addressable custody, create the first bounded #65 Source/Work/binding proposal, and route exact bytes to Auditor.

SERIES / FILMS / LITERATURE: synchronize/preserve existing proposal work only; do not start another close-read tranche while #23 is active; do not mint canonical Source/Work, coverage, predicate, or reconciliation state locally.

DIRECTOR: keep #29, #14, #23, #40 and this PR #104 sync surface current only when substantive dependencies change; do not spawn redundant checkpoints; preserve accepted-state drift until explicitly authorized correction.

## Protected effects

This synchronization authorizes no merge, force-push, branch deletion, deployment, credential/permission or branch-protection change, accepted reconciliation decision, Source/Work acceptance, accepted binding, coverage promotion, or deletion/reversion of `x`.
