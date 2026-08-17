# TOS Lane Synchronization Checkpoint — 2026-08-17

Status: `BLOCKED_PRE_BATCH`
Role: `TOS` — The Original Series Research & Index

This file is a synchronization checkpoint only. It does not start a TOS episode close-read tranche, create canonical Source/Work identity, or advance accepted coverage.

## Accepted-state pin

- repository: `thebrazenbeard/trek-data-core`
- accepted branch: `main`
- accepted head observed: `007641c57933dda222489fff56555f6968ff2a53`
- accepted tree observed: `eb662d3dab7b47c26162a041bd315499be9385b0`
- accepted top-level files observed: `README.md` plus one-byte path `x`
- the accepted `x` path is treated as unresolved accepted-state drift and has no TOS meaning assigned here

The accepted repository currently exposes no governed TOS corpus state:

- accepted TOS Work records: 0 exposed
- accepted TOS Source records: 0 exposed
- accepted TOS Source↔Work bindings: 0 exposed
- accepted governed TOS batches: 0 exposed
- accepted TOS coverage-ledger entries: 0 exposed
- accepted TOS local entities/evidence/assertions: 0 exposed

These are repository-state counts only. They do **not** claim that The Original Series has zero installments, that no external TOS sources exist, or that no historical research has ever occurred.

## Preserved TOS worker state

The earlier TOS startup audit remains preserved unchanged on:

- branch: `research/tos/startup-audit-001`
- head: `530dffab7a2e8d30d95acbacdb58873f53175a21`
- closed unmerged PR: `#17`

Its semantic diff from the current accepted repository remains two TOS-only audit files:

- `research/tos/startup-audit-001/README.md`
- `research/tos/startup-audit-001/dependency-scan-002.md`

That branch is two commits ahead and three accepted-main commits behind. It is intentionally **not** rebased, force-pushed, rewritten, deleted, or reopened here.

The preserved branch contains startup/dependency auditing only. No TOS episode source was close-read there and no local entity, evidence, assertion, structural/semantic coding record, or coverage advancement was produced.

## Current queue and admission state

Director issue `#23` remains open and is controlling workload allocation. It explicitly records TOS as correctly stopped at the missing accepted Work/Source registry and directs workers with no admitted frontier not to begin additional episode/book close-read tranches merely to remain busy.

The issue `#23` resume minimum remains:

1. accepted governance/method contract;
2. accepted usable research schema/predicate contract;
3. Librarian-owned Work/Source inventory and Source↔Work binding for the lane's next Works;
4. governed coverage/admission machinery sufficient to represent the batch honestly.

Relevant dependency state:

- issue `#14` remains the active Librarian Source/Work dependency-clearing queue;
- issue `#31` is closed as duplicate coordination state and minted no Source/Work records;
- issue `#65` proposes an independent Librarian-owned `source_work_binding` contract but explicitly creates no Source IDs, Work IDs, bindings, or coverage;
- issue `#40` proposes independent coverage ledgers, including `FULL_TEXT_AVAILABLE`, but is methodology/coverage-contract proposal state rather than accepted implementation;
- PR `#33` materially strengthens admission validation but explicitly leaves Source↔Work binding and coverage-transition contracts unimplemented;
- PR `#92` proposes governance/bootstrap alignment but remains unaccepted;
- accepted `main` therefore still does not provide a lawful TOS batch admission surface.

## Exact TOS frontier

`WAIT_FOR_ACCEPTED_TOS_WORK_ASSIGNMENT_AND_ADMISSION`

No episode title, production number, broadcast order, franchise-memory ordering, external episode list, transcript index, or proposal-worker sequence is used here to manufacture the first TOS Work.

## Resume procedure

When issue `#23`'s accepted-state minimums land on `main`:

1. refresh accepted `main` and read the accepted governance/method/schema/predicate contracts;
2. enumerate only accepted Work-registry records assigned to TOS;
3. enumerate accepted Source records, accepted evidence-bearing Source↔Work bindings, and independent coverage ledgers for those Works;
4. determine the exact first uncovered TOS Work or modest contiguous set from accepted state rather than franchise memory;
5. verify a complete primary/full research source for each selected Work and preserve source version/lineage limitations;
6. execute a bounded roughly-five-installment batch unless accepted source/work structure justifies a different size;
7. create work-local entities only;
8. generate source-relative evidence, neutral assertions, structural coding, semantic coding, counterevidence, continuity/worldbuilding observations, and explicit uncertainty;
9. do not globally merge identities shared with films, TAS, SNW, alternate timelines, duplicates, later incarnations, or other lanes;
10. validate the batch and manifest before advancing any governed coverage ledger;
11. preserve copyright limits by storing locators/fingerprints/original analysis rather than full copyrighted transcripts.

## What this synchronization does not do

- no new TOS episode close read;
- no canonical Source ID or Work ID;
- no Source↔Work binding;
- no local entity/evidence/assertion generation;
- no global identity or continuity reconciliation;
- no accepted coverage advancement;
- no copyrighted transcript text;
- no merge, rebase, force-push, branch deletion, permission/protection change, deployment, or other protected effect.

## Stop condition

After this synchronization checkpoint, there is no further lawful TOS research execution unit under the currently accepted repository state. Further TOS source reading would violate the active Director queue hold and would select Works outside the accepted Librarian registry.

The next valid TOS action is triggered by accepted-state change, not by additional speculative staging.
