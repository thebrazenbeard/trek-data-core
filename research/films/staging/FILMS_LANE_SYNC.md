# FILMS lane synchronization

Status: PROPOSAL / NON-CANONICAL SYNC INDEX
Lane: FILMS
Sync date: 2026-08-17
Base: accepted `main` `007641c57933dda222489fff56555f6968ff2a53`

This file synchronizes the FILMS worker checkpoint from the current accepted base without merging, rebasing, rewriting, reopening, or promoting preserved proposal history. It creates no canonical Source/Work identities, no accepted coverage, no global identity reconciliation, and no film close read.

## Accepted-state gate

Director issue #23 remains open and explicitly pauses new corpus close-read tranches until accepted governance/method, usable schema/predicate contracts, Librarian-owned Work/Source bindings, and governed coverage/admission state exist on `main`.

Accepted `main` currently contains the skeletal repository state plus the unresolved one-byte top-level `x` file. It still provides no accepted FILMS Work registry, Source registry, Source↔Work binding surface, coverage ledger, or admitted FILMS batch.

Therefore the accepted FILMS denominator remains `UNRESOLVED`. Repository-state counts of zero FILMS records must not be misread as a franchise-film count.

## Preserved FILMS checkpoint

The only FILMS preservation branch currently present is:

- branch: `research/films/startup-audit-001`
- current branch head: `9370e31a33ec84b73eabd14421d616001ca27016`
- original startup audit commit: `b3588db9c2f1dfc0d8310d281b588b7b72db4860`
- former PR: #13, closed unmerged
- worker state: `QUEUE_HELD_BLOCKED_PRE_BATCH`

That preserved branch contains only startup/readiness audit material. No film source was opened for semantic research, no local entities/evidence/assertions were generated, and no FILMS coverage transition was claimed.

## Synchronization result

FILMS has no completed source-read tranche to normalize or index. The lane is synchronized by preserving the blocker checkpoint and pinning its relationship to current accepted state.

The older blocker branch is intentionally not rebased or merged with current `main`; Director issue #23 instructs workers to preserve proposal branches rather than rewrite them merely for queue tidiness. This sync branch is instead created directly from current accepted `main` and references the preserved checkpoint by branch/commit identity.

No PR is opened for this sync index because issue #23's active-queue normalization directs corpus PR surfaces to remain closed while the hold is active.

## Current blockers

1. Accepted governance/method contract is absent from `main`.
2. Accepted usable research schema and predicate contract is absent from `main`.
3. Librarian-owned FILMS Work/Source inventory and accepted Source↔Work bindings are absent from `main`.
4. Governed coverage/admission representation sufficient to record a FILMS batch is absent from `main`.
5. Director issue #23 actively prohibits starting a new film close-read tranche before those conditions clear.
6. Issue #14 remains open; the Source↔Work contract is better specified at proposal/methodology level, but no Librarian-owned execution branch or accepted FILMS binding records exist.

## Identity and continuity guardrails retained

When FILMS eventually resumes:

- continuity/timeline scope must be explicit per accepted Work;
- Prime, Kelvin, alternate, duplicate, restored, synthetic, copied, or otherwise unusual identities must not be merged because names or performers match;
- workers create local entities only;
- testimony, memory, sensor/computer output, simulations, altered realities, and alternate timelines remain source-relative evidence frames;
- external filmographies and remembered franchise lists may support discovery only, never substitute for the accepted Work registry.

## Resume procedure

When issue #23's resume condition is actually satisfied:

1. refresh accepted `main` rather than trusting this sync file as current authority;
2. enumerate every Work assigned to FILMS by the accepted Work registry;
3. read accepted FILMS Source↔Work bindings and accepted coverage state;
4. identify the first uncovered source-bound tranche;
5. obtain complete primary/full source representations for that tranche;
6. execute a bounded FILMS batch using `Source → Work → Local Entity → Evidence → Assertion`;
7. validate generated records, manifest, and legal coverage transitions before claiming batch completion.

Until then, there is no valid additional FILMS research unit. The correct state is `QUEUE_HELD_BLOCKED_PRE_BATCH`.
