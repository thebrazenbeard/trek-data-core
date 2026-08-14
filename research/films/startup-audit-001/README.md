# FILMS Startup Audit 001

Status: `BLOCKED_PRE_BATCH`
Role: `FILMS` — Star Trek Films Research & Index

This is an operational startup audit, not a completed research batch and not a coverage advancement.

## Accepted-state pin

- Repository: `thebrazenbeard/trek-data-core`
- Accepted branch: `main`
- Accepted head: `d58359a207da89e812d0a0330558c66774ed1241`
- Accepted tree observed: `2cbf2d9d3f4911e63941e509a76ffc2205b75200`
- Accepted top-level corpus/research state observed: no Work registry, no Source registry, no `research/films` partition, and no accepted FILMS batch records.

## FILMS accepted frontier

Repository-state counts discoverable on accepted `main`:

- accepted FILMS Work records: 0
- accepted FILMS Source records: 0
- accepted FILMS research batches: 0
- accepted FILMS local entities: 0
- accepted FILMS evidence records: 0
- accepted FILMS assertions: 0
- accepted FILMS coverage records: 0

These are repository-state counts only. They do **not** assert that Star Trek has zero feature-length works. The franchise-film denominator remains `UNRESOLVED` until the accepted Work registry assigns works to the FILMS lane.

## Blocking dependency

The FILMS worker must establish its inventory from the accepted Work registry rather than a remembered franchise list. Evidence must then bind to identified Source and Work records. Accepted `main` currently contains neither registry, so selecting a film now would invent the assignment boundary and create parallel corpus state.

Therefore no film source was opened for semantic research in this unit, and no local entity, evidence, assertion, continuity coding, or coverage record was generated.

## Resume condition

Resume FILMS research immediately when accepted `main` exposes an accepted Work registry with FILMS-assigned works. Then:

1. enumerate every accepted FILMS-assigned work and its continuity/timeline scope metadata;
2. determine accepted FILMS coverage and the exact uncovered frontier;
3. bind complete primary/full source(s) to the selected works;
4. execute a bounded audiovisual batch, normally about five works unless source structure justifies another size;
5. emit local entities, source-relative evidence, assertions, counterevidence, neutral structural/semantic coding, and coverage update inside `research/films`;
6. validate before advancing coverage.

## Guardrails preserved

- no remembered franchise list substituted for the accepted Work registry;
- no global identity resolution;
- no merging of Prime, Kelvin, alternate, duplicate, restored, synthetic, or other unusual identities merely from names or performers;
- no recap substitution for complete primary/full sources;
- no coverage advancement from titles, filenames, snippets, or historical chat claims;
- no merge or other protected repository effect performed.
