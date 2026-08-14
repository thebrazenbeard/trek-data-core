# TOS Startup Audit 001

Status: `BLOCKED_PRE_BATCH`
Role: `TOS` — The Original Series Research & Index

This is an operational startup audit, not a completed research batch and not a coverage advancement.

## Accepted-state pin

- Repository: `thebrazenbeard/trek-data-core`
- Accepted branch: `main`
- Accepted head: `d58359a207da89e812d0a0330558c66774ed1241`
- Accepted tree observed: `2cbf2d9d3f4911e63941e509a76ffc2205b75200`
- Accepted top-level corpus/research state observed: no Work registry, no Source registry, no `research/tos` partition, no accepted TOS batch records.

## TOS accepted frontier

The accepted repository currently exposes:

- accepted TOS Work records: 0
- accepted TOS Source records: 0
- accepted TOS research batches: 0
- accepted TOS local entities: 0
- accepted TOS evidence records: 0
- accepted TOS assertions: 0
- accepted TOS coverage records: 0

These are repository-state counts only. They do not assert that TOS has zero installments or that no historical chat research exists.

## Proposal-state observation

Branch `architecture/v0.1-bootstrap` at `07b5152e2a6bcb18768e9eb7800a74cbc013d6ef` is proposal state under open PR #1. Its PR description states that the branch establishes architecture and does not migrate existing Trek research or ingest new corpus content. It is not used here as accepted Work-registry state.

## Blocking dependency

A TOS series worker must select installments from the accepted Work registry and bind evidence to identified Source and Work records. Because accepted `main` currently contains no Work registry or TOS work assignments, selecting an episode batch now would invent the assignment boundary and create a parallel corpus state.

Therefore no episode source was opened for research in this unit, and no local entity, evidence, assertion, semantic coding, or coverage record was generated.

## Resume condition

Resume TOS research immediately when accepted `main` exposes an accepted Work registry with TOS-assigned works. Then:

1. enumerate accepted TOS works and accepted TOS coverage;
2. locate the exact first uncovered work(s);
3. bind complete primary/full source(s);
4. execute a bounded batch of about five installments unless source structure justifies another size;
5. emit local entities, source-relative evidence, assertions, counterevidence, structural/semantic coding, and coverage update inside `research/tos`;
6. validate before advancing coverage.

## Guardrails preserved

- no global identity resolution;
- no cross-series merging with TAS, SNW, films, alternate timelines, duplicates, or later incarnations;
- no recap substitution for missing full sources;
- no coverage advancement from filenames, titles, or historical chat claims;
- no merge or protected repository effect performed.
