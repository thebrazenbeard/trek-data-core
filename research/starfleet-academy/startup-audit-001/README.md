# Starfleet Academy Startup Audit 001

Status: `BLOCKED_PRE_BATCH`
Role: `SFA` - Star Trek: Starfleet Academy Research & Index

This is an operational startup audit, not a completed research batch and not a coverage advancement.

## Accepted-state pin

- Repository: `thebrazenbeard/trek-data-core`
- Accepted branch: `main`
- Accepted head: `d58359a207da89e812d0a0330558c66774ed1241`
- Accepted tree observed: `2cbf2d9d3f4911e63941e509a76ffc2205b75200`
- Accepted top-level corpus/research state observed: no Work registry, no Source registry, no `research/starfleet-academy` partition, no accepted Starfleet Academy batch records.

## Starfleet Academy accepted frontier

The accepted repository currently exposes:

- accepted Starfleet Academy Work records: 0
- accepted Starfleet Academy Source records: 0
- accepted Starfleet Academy research batches: 0
- accepted Starfleet Academy local entities: 0
- accepted Starfleet Academy evidence records: 0
- accepted Starfleet Academy assertions: 0
- accepted Starfleet Academy coverage records: 0

These are repository-state counts only. They do not assert that Starfleet Academy has zero installments, that no installments have been released, or that no historical/chat research exists.

## Time-sensitive inventory rule

Starfleet Academy is an actively developing corpus. This worker must not infer an episode denominator from memory, old chat state, announcements, streaming listings, or external episode guides. The current accepted Work registry is the only permitted basis for selecting the research frontier.

## Proposal-state observation

Branch `architecture/v0.1-bootstrap` at `07b5152e2a6bcb18768e9eb7800a74cbc013d6ef` is proposal state under open PR #1. The PR is open, unmerged, and its description states that the branch establishes architecture but does not migrate existing Trek research or ingest new corpus content. It is not used here as accepted Work-registry state.

## Blocking dependency

An SFA series worker must select installments from the accepted Work registry and bind evidence to identified Source and Work records. Because accepted `main` currently contains no Work registry or SFA work assignments, selecting an episode batch now would invent the assignment boundary and create parallel corpus state outside the Librarian-owned registry.

Therefore no episode source was opened for research in this unit, and no local entity, evidence, assertion, semantic coding, counterevidence, or coverage record was generated.

## Resume condition

Resume Starfleet Academy research immediately when accepted `main` exposes an accepted Work registry with SFA-assigned works. Then:

1. refresh the complete accepted SFA Work inventory rather than relying on any prior denominator;
2. enumerate accepted SFA coverage and locate the exact first uncovered work or works;
3. verify accepted Source bindings and complete primary/full source availability;
4. execute a bounded batch of about five installments unless the accepted source structure justifies another size;
5. emit local entities, source-relative evidence, assertions, explicit counterevidence, structural/semantic coding, and the appropriate coverage update inside `research/starfleet-academy`;
6. validate before advancing coverage.

## Guardrails preserved

- no global identity resolution;
- no silent merging of legacy characters, institutions, technologies, historical references, duplicates, alternate states, or cross-series entities;
- no recap substitution for missing full primary sources;
- no denominator inferred from stale external information;
- no coverage advancement from titles, filenames, announcements, or historical chat claims;
- no merge or protected repository effect performed.
