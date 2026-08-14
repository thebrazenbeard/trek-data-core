# SFA S01 B001 Staging — Opening Works

Status: `STAGING_CLOSE_READ_IN_PROGRESS`
Role: `SFA` — Star Trek: Starfleet Academy Research & Index
Authority: proposal-only; not accepted coverage; not SOURCE_BOUND

This packet preserves completed full-transcript close reads while accepted `main` still lacks a Librarian-owned Work/Source registry. It does not create canonical Work IDs or Source IDs, advance accepted coverage, or globally reconcile any legacy character, institution, technology, historical reference, or location.

## Accepted-state pin

- repository: `thebrazenbeard/trek-data-core`
- accepted branch at latest refresh: `main`
- accepted head observed: `d58359a207da89e812d0a0330558c66774ed1241`
- accepted SFA Work registry observed: absent
- accepted SFA Source registry observed: absent
- accepted SFA coverage ledger observed: absent

## Current external inventory observation — discovery only

Observed 2026-08-14 from the official Paramount+ Starfleet Academy page. This is a current external discovery snapshot, **not** an accepted project denominator and not a replacement for the Librarian-owned Work registry.

Paramount+ currently exposes one season with ten episode entries:

1. Kids These Days — 2026-01-15
2. Beta Test — 2026-01-15
3. Vitus Reflux — 2026-01-22
4. Vox in Excelso — 2026-01-29
5. Series Acclimation Mil — 2026-02-05
6. Come, Let's Away — 2026-02-12
7. Ko'Zeine — 2026-02-19
8. The Life of the Stars — 2026-02-26
9. 300th Night — 2026-03-05
10. Rubincon — 2026-03-12

Discovery source:
`https://www.paramountplus.com/shows/star-trek-starfleet-academy/`

Source-binding anomaly for Librarian review: Springfield's season index renders episode 10 as `Rubicon`, while the current official Paramount+ listing renders `Rubincon`. No correction is made here.

## Staged close reads

### 1. Kids These Days

Provisional label: `SFA-S01E01-KIDS-THESE-DAYS`
Official release observation: 2026-01-15
Official runtime observation: approximately 1h15m on Paramount+
Full-text representation used: Springfield transcript page for s01e01.

Status:
- transcript body read end-to-end through final scene;
- primary audiovisual media not directly inspected;
- provider lineage/independence unresolved;
- no reproducible source-byte hash claimed;
- detailed work-local staging from this close read is preserved in earlier commits on this same branch and remains recoverable from branch history; the current batch summary does not pretend that historical commit content is an accepted canonical record.

### 2. Beta Test

Provisional label: `SFA-S01E02-BETA-TEST`
Official release observation: 2026-01-15
Official runtime observation: approximately 1h on Paramount+
Full-text representation used: Springfield transcript page for s01e02.

Status:
- transcript representation read end-to-end through final scene;
- detailed local entity candidates, source-relative evidence, candidate assertions, explicit counterevidence, neutral coding, and cross-work hypotheses are preserved in `BETA_TEST.md`;
- primary audiovisual media not directly inspected;
- provider lineage/independence unresolved;
- no reproducible source-byte hash claimed.

## Batch-state limits

The two completed transcript close reads are staging work only. They do **not** establish:

- accepted Work identity;
- accepted Source identity;
- SOURCE_BOUND status;
- accepted FULL_TEXT_AVAILABLE status;
- accepted semantic coverage;
- global entity identity;
- source independence;
- primary audiovisual verification.

Those remain blocked on Librarian-owned source/work binding and accepted project infrastructure.

## Cross-work observations after two close reads

The following remain provisional hypotheses, not corpus conclusions:

- boundaries and walls appear both literally and socially in the first two staged works;
- the Academy is depicted mixing exploratory/scientific/cultural education with security/combat training;
- cadets are given consequential institutional roles rather than remaining only classroom observers;
- Caleb's relationship to Starfleet repeatedly combines distrust of control with selective use of institutional resources and emerging connection.

Each hypothesis requires later supporting, neutral, and disconfirming evidence before promotion.

## Promotion blockers

Before this staging material can become an accepted research batch:

1. accepted SFA Work identities must exist in the Librarian-owned registry;
2. accepted Source identities/variants and provenance must be bound;
3. stable/reproducible source identity or hashes must be recorded where feasible;
4. accepted schema/predicate state must exist;
5. staging records must be converted into governed batch records;
6. deterministic validation must pass;
7. a proper batch manifest must be generated;
8. accepted coverage may advance only after all prior requirements pass.

## Exact next frontier

If accepted infrastructure remains blocked, the next provisional staging candidate is `Vitus Reflux`, but only after a complete full-text representation is retrieved and read end-to-end.

If accepted Work/Source registry state lands first, stop using this external provisional sequence as authority, refresh accepted `main`, and choose the next SFA work strictly from the accepted registry and coverage state.

## Guardrails preserved

- no global identity resolution;
- no silent merging of legacy characters, institutions, technologies, historical references, duplicates, alternate states, or cross-series entities;
- no recap substitution for missing full primary/full-text sources;
- no denominator inferred from stale external information;
- no coverage advancement from titles, filenames, announcements, or historical chat claims;
- no merge or protected repository effect performed.
