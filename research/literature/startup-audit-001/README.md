# LIT startup audit 001

## Scope

Star Trek Literary Corpus Research & Index (`LIT`) lane only.

This record captures the accepted-state startup audit while the repository has no accepted Librarian-owned Source/Work registry assigning licensed literary works to this lane. It does **not** advance literary research coverage and contains no semantic book research.

## Accepted-state pin

- accepted base: `main`
- accepted head observed: `d58359a207da89e812d0a0330558c66774ed1241`
- accepted LIT Work records observed: 0
- accepted LIT Source records observed: 0
- accepted LIT research batches observed: 0

These are repository-state counts only. They are not a claim that the licensed Star Trek literary corpus contains zero works.

## Admission requirement

LIT deep-reading begins only after the Librarian has sufficiently source-bound a literary work. File presence alone is not a Work record and must not be used to infer one work per archive member.

The eventual literary registry must preserve distinctions relevant to admission and provenance, including where applicable:

- editions and release variants;
- omnibuses and anthologies versus contained works;
- multipart works;
- duplicate formats and derivative conversions;
- LIT/TXT/OPF lineage relationships;
- alternate naming;
- series/subseries placement;
- continuity/canon scope.

## Current Librarian dependency evidence

Current Librarian handoff artifacts remain proposal/migration evidence rather than accepted `trek-data-core/main` state, but they narrow the blocker materially.

`ST_LIBRARIAN_COLLISION_RECOVERY_QUEUE_V1` reports:

- the two candidate containers `Star_Trek_OPF_Converted(1).zip` and `ST ebooks(1).zip` are reported but not byte-exposed to the Librarian;
- neither container is byte-verified, hashed, or assigned a Source ID;
- the promotion rule is `NO_STS_OR_BOOK_TEXT_PROMOTION_BEFORE_READABLE_BYTES_AND_HASH`;
- a legacy 14-work abstract literary inventory is recoverable only as migration evidence and must not be promoted directly to accepted Work IDs;
- historical collision evidence includes 84 high-confidence LIT↔TXT candidates, 121 title-overlap groups, and 41 suspicious short LIT-derived conversions, with exact memberships still unresolved;
- named source-quality/container edge cases include `Ghost Ship`, `Millennium`, `A Time to...`, and `Worlds of Star Trek: Deep Space Nine, Volume Three`.

`ST_LIBRARIAN_EXTERNAL_CROSSWALK_TRANCHE_001` adds external candidate metadata for six legacy work candidates, but explicitly creates zero accepted Work IDs, zero accepted Source IDs, and zero accepted crosswalks. Those rows therefore cannot be used by LIT to select a deep-reading batch.

The historical convergence checkpoint likewise records 14 abstract literary Works but zero canonical book Sources, zero preferred Sources, zero source-bound Works, and no reading-ledger effect. This is consistent with the current repository gate rather than evidence of hidden completed book research.

## Blocker

The immediate dependency is now precise: **byte custody precedes source binding, and source binding precedes LIT deep-reading**.

Accepted `main` currently contains no Source registry, Work registry, literary source bindings, or accepted literary coverage ledger. Selecting a title from memory, archive filenames, external metadata, legacy Work IDs, or an unaccepted proposal would cross the Librarian-owned registry boundary and risk collapsing editions, containers, derivatives, or contained stories into false Work identities.

## Required upstream sequence before LIT admission

The Librarian's current first-byte queue requires, in order:

1. obtain readable bytes for an ebook container and hash the container;
2. enumerate and hash physical archive members;
3. classify original/primary candidates, derivative conversions, metadata/sidecars, containers, and unresolved members;
4. detect byte-identical and normalized-content duplicate candidates without collapsing physical-source identity;
5. construct provenance families and `derived_from` chains across LIT/TXT/OPF/HTML or other representations;
6. run readability/completeness checks, including body/spine and beginning/end integrity;
7. propose byte-backed Source records;
8. propose Source-to-Work mappings only after source-family reconciliation, preserving container/contained-work distinctions;
9. admit stable Source/Work binding through the accepted repository process.

Only after step 9 may LIT select the next 1–3 substantial works for deep research.

## Validation constraints

This startup audit intentionally creates no:

- canonical Source or Work IDs;
- local literary entities;
- evidence records;
- assertion records;
- continuity reconciliation;
- coverage advancement;
- copyrighted source text.

## Resume condition

When accepted `main` contains Librarian-accepted literary Work records with sufficient source binding, refresh the accepted LIT inventory, select the next 1–3 eligible substantial works, verify full-source availability, and begin the first bounded deep-research batch using the common Source → Work → Local Entity → Evidence → Assertion method.
