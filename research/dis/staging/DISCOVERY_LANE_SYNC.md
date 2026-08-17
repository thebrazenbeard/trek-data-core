# Discovery lane staging synchronization

Status: PROPOSAL / NON-CANONICAL SYNC INDEX
Lane: DIS
Sync date: 2026-08-17
Base: current accepted `main` at branch creation

This index synchronizes the preserved Discovery worker checkpoints without merging, rebasing, rewriting, or promoting them. It creates no canonical Source/Work identities, no accepted coverage, no global identity reconciliation, and no new episode close read.

## Accepted-state gate

Director issue #23 (`Director queue hold: pause new corpus staging until admission bottleneck clears`) is active. It explicitly prohibits beginning new episode/book close-read tranches merely because a worker has a next title. Already completed/in-progress work may be brought to a clean preservation checkpoint; after that, the lane stops until the resume conditions are met.

Accepted `main` still does not provide the minimum Discovery admission dependencies: accepted governance/method contract, accepted usable research schema/predicate contract, Librarian-owned Discovery Work/Source inventory with accepted binding, and governed coverage/admission representation. The accepted one-byte top-level `x` file is treated by Director issue #23/#95 as unresolved accepted-state drift and has no Discovery research meaning.

## Preserved Discovery source-read tranches

All rows below are proposal preservation only. None is accepted coverage.

| Tranche | Episodes | Preservation branch | Receipt commit | State |
|---|---|---|---|---|
| DIS-S01-B001 | S01E01-S01E05 | `research/dis/dis-s01-b001` | `a7598036f88ecbfa7d038808d02eb3b1daf26b88` | complete source-read receipt preserved |
| DIS-S01-B002 | S01E06-S01E10 | `research/dis/dis-s01-b002` | `12c62bf1f619365171856b5ee593ca7717f42639` | complete source-read receipt preserved |
| DIS-S01-B003 | S01E11-S01E15 | `research/dis/dis-s01-b003` | `da2301b494c04e85716043cdf0e884cf5c77fd60` | complete source-read receipt preserved |
| DIS-S02-B001 | S02E01-S02E05 | `research/dis/dis-s02-b001` | `5513fd50c2cbe5c07d3d1decf8373281e1cb892d` | complete source-read receipt preserved; E05 source tail contamination recorded/excluded |
| DIS-S02-B002 | S02E06-S02E10 | `research/dis/dis-s02-b002` | `fcc088cb9e27fa8435769712d276b90dbf5d711c` | complete source-read receipt preserved |

## Worker-effort frontier versus accepted frontier

Worker-effort preservation reaches through Discovery S02E10.

This is **not** an accepted corpus frontier. Accepted Discovery coverage remains unpromoted because the required Source/Work binding, governed record admission, and coverage semantics are absent from accepted `main`.

The provisional next source-reading title would be S02E11, but Director issue #23 explicitly says a staging branch's `exact next frontier` is not authorization to start another tranche. Therefore S02E11-S02E14 is intentionally **not started** in this sync.

## Research distinctions already preserved

The five receipts retain, among other cases:

- testimony, memory, medical/sensor reports, altered/mycelial experience, synthetic evidence, alternate-universe records, and direct depiction as distinct evidence frames;
- Tyler/Voq biological, psychological, memory, legal, relational, and self-identified continuity without forced binary identity resolution;
- Mirror counterparts as locally distinct occurrences rather than automatic SAME_AS relations;
- Culber's death/network embodiment/reconstruction with continuity dimensions kept separate;
- Airiam's retained awareness and wishes distinguished from externally controlled motor action;
- Control's holographic impersonation/fabrication distinguished from the persons represented;
- Red Angel identification hypotheses preserved together with later falsification/correction;
- wartime institutional rule/exception conflicts without flattening Starfleet into either perfect adherence or inevitable abandonment of principle;
- source-quality defects and provider substitutions recorded rather than silently normalized.

## Current blockers

1. Accepted governance/method contract absent from `main`.
2. Accepted usable research schema and predicate contract absent from `main`.
3. Librarian-owned Discovery Work/Source inventory and accepted Source↔Work binding absent from `main`.
4. Governed coverage/admission representation absent from `main`.
5. Director issue #23 actively pauses new corpus staging until those shared dependencies clear.
6. Existing proposal receipts remain preservation/migration input, not accepted evidence ledger records.

## Resume procedure

When issue #23's resume condition is actually satisfied:

1. refresh accepted `main` rather than trusting this index as current authority;
2. read accepted Discovery Work/Source bindings and accepted coverage ledger;
3. normalize/revalidate the preserved S01E01-S02E10 staging against the accepted schemas and predicates;
4. generate proper local entities, evidence, assertions, manifests, hashes, and legal coverage transitions only for source-bound Works;
5. submit normalized Discovery batches as proposals under the accepted admission contract;
6. determine the next uncovered accepted Work from repository state, not from the provisional sequence recorded here.

Until then, this synchronization index is the clean Discovery worker checkpoint. No new semantic batch is authorized by this file.