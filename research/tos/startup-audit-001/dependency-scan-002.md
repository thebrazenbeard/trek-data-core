# TOS Dependency Scan 002

Status: `BLOCKED_PRE_BATCH`
Role: `TOS` — The Original Series Research & Index

This is a continuation of `startup-audit-001`, not a research batch and not a coverage advancement.

## Accepted state refresh

- accepted branch: `main`
- accepted head remains: `d58359a207da89e812d0a0330558c66774ed1241`
- accepted TOS Work records exposed: 0
- accepted TOS Source records exposed: 0
- accepted TOS research batches exposed: 0
- accepted TOS coverage records exposed: 0

No episode was selected or researched because accepted Work assignments remain absent.

## Proposal topology observed

### PR #1 — architecture bootstrap

Open and unmerged. Director comments now explicitly gate it from acceptance until methodology/alignment defects are corrected, including the five-object flow, FULL_TEXT_AVAILABLE coverage state, explicit Source<->Work binding, separate coverage ledgers, stronger validation, and drift/calibration requirements.

### PR #2 — DS9 staging

Open draft, stacked on the unaccepted bootstrap. It explicitly refuses accepted coverage advancement and states that Librarian Source/Work identities, source variants/provenance, and reproducible source hashes are required before promotion.

### PR #3 — TNG initial batch

Open draft proposal. It explicitly states that accepted main had no Librarian-owned Source/Work registry and therefore does not claim SOURCE_BOUND.

### Branch survey

The repository contains multiple proposal research branches and governance branches, but no Librarian/registry branch exposing Source/Work inventory. `architecture/bootstrap-governance` currently adds chat-starter coordination only and does not resolve the Source/Work dependency.

## Exact TOS dependency chain

1. architecture/governance foundation becomes accepted on `main`;
2. Librarian publishes accepted Source/Work registry and explicit Source<->Work bindings including TOS-assigned works;
3. TOS worker enumerates accepted TOS coverage and identifies the first uncovered work;
4. TOS worker opens complete primary/full source(s) and executes a bounded research batch;
5. batch validation passes before coverage advancement.

This ordering is a dependency statement, not authorization for this worker to perform architecture or Librarian work.

## Current frontier

`WAIT_FOR_ACCEPTED_TOS_WORK_ASSIGNMENT`

Resume immediately when accepted `main` contains TOS-assigned Work records. Do not substitute proposal branches, historical chats, franchise memory, episode lists, or another worker's provisional ordering for the accepted registry.

## Guardrails

- no global identity resolution;
- no cross-series identity merging;
- no source substitution with recaps;
- no coverage advancement from proposal-state research;
- no protected repository effect performed.
