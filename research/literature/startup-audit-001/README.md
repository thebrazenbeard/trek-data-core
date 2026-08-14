# LIT startup audit 001

## Scope

Star Trek Literary Corpus Research & Index (`LIT`) lane only.

This record captures the accepted-state startup audit while the repository has no accepted Librarian-owned Source/Work registry assigning licensed literary works to this lane. It does **not** advance literary research coverage and contains no semantic book research.

## Accepted-state pin

- accepted base: `main`
- accepted head observed: `694cb833ac5197f45276089d45dc2d4e0b16f556`
- accepted tree observed: `2cbf2d9d3f4911e63941e509a76ffc2205b75200`
- accepted files observed: `README.md` only
- accepted LIT Work records observed: 0
- accepted LIT Source records observed: 0
- accepted LIT Source↔Work bindings observed: 0
- accepted LIT research batches observed: 0

The accepted head advanced through an accidental sentinel-file change and its revert. The accepted tree is unchanged from the earlier skeletal state, so that head movement creates **no literary registry, source-binding, infrastructure, or coverage effect**.

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

The convergence checkpoint likewise records 14 abstract literary Works but zero canonical book Sources, zero preferred Sources, zero source-bound Works, and no reading-ledger effect. This is consistent with the current repository gate rather than evidence of hidden completed book research.

File Library searches for both ebook ZIP names, `BOOK_TEXT`, `SOURCE_BOUND`, canonical book Source IDs, `STS-*`, and candidate individual titles found no admitted complete literary Source.

## Infrastructure dependency

LIT also requires accepted governed research infrastructure before a formal batch can be admitted.

Current PR #1 (`architecture/v0.1-bootstrap`) head observed: `a26b444cd64be25c34cdb46c76721da7aeb777a2`.

Useful compatible pieces exist, including the restored five-object flow, independent Source and Work schemas, and provenance fields. Remaining LIT-critical gaps include:

- `FULL_TEXT_AVAILABLE` still absent from the proposed processing-depth ladder;
- no explicit Librarian-owned Source↔Work binding record/schema;
- incomplete research-partition declaration (`SHORT` remains omitted);
- no governed legal coverage-transition enforcement.

PR #33 (`architecture/admission-validation-v0.1`) materially improves the earlier validator. At head `1bf5eedb9bebfc5a3c96300263bc7fdc643d1363`, direct inspection shows schema-subset enforcement, cross-record referential checks, and predicate-registry membership checks, with CI success. This **reduces** the validation blocker.

PR #33 remains proposal state and does not supply Source↔Work binding, `FULL_TEXT_AVAILABLE`, coverage-transition semantics, byte custody, source completeness, or source-family/container correctness. It also does not by itself close Auditor PR #19's separate deterministic reconciliation, provenance-projection, and semantic-diff findings.

Auditor PR #38 adds a relevant coverage constraint: proposal worker effort may record downstream processing while `SOURCE_BOUND=false`, but that vector cannot be imported unchanged into the governed ordered coverage ladder. For LIT, close-reading effort and accepted coverage therefore remain deliberately distinct.

PR #26 (`architecture/librarian-bootstrap-route-001`) was Director routing only and was closed **without merge**. It created no Source IDs, Work IDs, hashes, bindings, or coverage. No separate Librarian-owned Source/Work implementation branch or PR was found in the latest scan.

## Blocker

The dependency sequence is now precise:

**accepted infrastructure + byte custody → Librarian source-family reconciliation/binding → accepted literary Source/Work admission → LIT deep-reading → legal coverage transitions**.

Accepted `main` currently contains no Source registry, Work registry, literary source bindings, accepted research infrastructure, or accepted literary coverage ledger. Selecting a title from memory, archive filenames, external metadata, legacy Work IDs, or an unaccepted proposal would cross the Librarian-owned registry boundary and risk collapsing editions, containers, derivatives, or contained stories into false Work identities.

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

In parallel, governed infrastructure must be corrected, validated, audited, and accepted before formal research admission.

Only after both independent gates pass may LIT select the next 1–3 substantial works for deep research.

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

When accepted `main` contains both accepted governed research infrastructure and Librarian-accepted literary Work records with sufficient source binding and complete readable text, refresh the accepted LIT inventory, select the next 1–3 eligible substantial works, and begin the first bounded deep-research batch using the common Source → Work → Local Entity → Evidence → Assertion method while advancing only legally supported coverage tiers.
