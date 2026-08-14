# Voyager batch voy-s01-b001

Status: WORKING EXTRACTION COMPLETE; ACCEPTED COVERAGE NOT ADVANCED.

Scope: `Caretaker` through `The Cloud` (five episode works / six broadcast-number slots when the two-part pilot numbering is counted separately).

## Governance

This branch starts from accepted `main` at `d58359a207da89e812d0a0330558c66774ed1241`.

Accepted `main` contains no Source/Work registry, accepted research schema, or Voyager batch. The architecture in PR #1 is a proposal, not accepted state. Accordingly:

- this batch does not create or mutate global Source, Work, or identity records;
- `provisional_work_ref` and `provisional_source_ref` are batch-local placeholders only;
- working evidence/assertions are not eligible for deterministic projection;
- accepted coverage remains zero until the Librarian supplies accepted bindings and the governing schema/methodology is accepted;
- source hashes are deliberately left null rather than fabricated.

## Source basis

Five complete third-party transcript pages from Forever Dreaming were read and processed in full. They are full textual transcript sources, not official production scripts and not audiovisual captures. Source-relative findings therefore establish what those transcript artifacts support.

## Method

Neutral coding was applied across plot/problem structure, agency, institutions, interpersonal dynamics, identity/self-concept, epistemic frames, ethics, technology/material constraints, continuity, consequences, and counterevidence.

Temporal anomalies, holographic-person evidence, constructed personas, and superseded timeline states are represented as scoped evidence/assertions. No global identity reconciliation is attempted.

## Files

- `source-read-log.jsonl`: source locators and actual processing status
- `caretaker.json`, `parallax.json`, `time-and-again.json`, `phage.json`, `the-cloud.json`: batch-local entities, source-relative evidence, and typed assertions
- `provisional-manifest.json`: non-projectable working manifest

## Blocking conditions for acceptance

1. Librarian-approved Work IDs for the five episode works.
2. Librarian-approved Source IDs/hash bindings for the transcript artifacts or preferred replacement sources.
3. Accepted schema/methodology state on `main`.
4. Rebinding of batch-local placeholders to accepted identifiers.
5. Deterministic validation against the then-accepted schemas.
6. Final batch manifest and coverage update generated only after 1–5 pass.
