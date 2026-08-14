# LIT current frontier

Status: **BLOCKED BEFORE DEEP RESEARCH**

This is a literature-lane handoff/checkpoint only. It does not create Source/Work identity or advance coverage.

## Accepted state

Accepted `main` observed during this checkpoint:

- head: `694cb833ac5197f45276089d45dc2d4e0b16f556`
- tree: `2cbf2d9d3f4911e63941e509a76ffc2205b75200`
- accepted files: `README.md` only
- accepted LIT Works: 0
- accepted LIT Sources: 0
- accepted LIT Source↔Work bindings: 0
- accepted LIT research batches: 0

The accepted head moved through an accidental sentinel-file change and revert, leaving the accepted tree semantically unchanged.

## Infrastructure gate

Current relevant proposals:

- PR #1 `Bootstrap provenance-aware Trek research architecture`
  - proposal head observed: `4b771b28406e1b2f41d93f5787e1978e98c6e432`
  - canonical five-object flow is corrected at this head;
  - `FULL_TEXT_AVAILABLE` remains absent from the proposed processing ladder;
  - no independent Source↔Work binding record/schema is present;
  - current validator remains insufficient for governed literary admission.

- PR #19 `Audit architecture bootstrap validation and projection gate`
  - Auditor finding set remains proposal state;
  - CRITICAL findings include missing schema/referential validation, accepted reconciliation not deterministically applied, and provenance/evidence omissions from logical projection/hash;
  - HIGH finding: semantic diff classes not implemented as governed.

- PR #32 `Director: refresh gate after accepted-main head movement`
  - confirms PR #1 is not acceptance-ready while PR #19 findings remain open;
  - confirms accepted tree remains README-only.

Infrastructure admission condition: a corrected architecture successor must be validated/audited and then become accepted `main` state. LIT does not decide or perform that acceptance.

## Librarian / source gate

Current dependency artifacts show:

- reported candidate containers:
  - `Star_Trek_OPF_Converted(1).zip`
  - `ST ebooks(1).zip`
- readable byte custody: not exposed to current Librarian surfaces;
- canonical book Sources: 0;
- source-bound literary Works: 0;
- preferred literary Sources: 0;
- reading-ledger effect: none.

Legacy/convergence material preserves 14 abstract literary Work candidates only as migration/convergence evidence, not accepted `trek-data-core/main` Work identity.

Current collision warnings include:

- 84 historical high-confidence LIT↔TXT candidates with exact membership unrecovered;
- 121 title-overlap groups with exact membership unrecovered;
- 41 suspicious short LIT-derived conversions with exact membership unrecovered;
- `Ghost Ship` conversion/readability edge case;
- `Millennium` container/component ambiguity;
- `A Time to...` component membership ambiguity;
- `Worlds of Star Trek: Deep Space Nine, Volume Three` container-versus-contained-work ambiguity.

PR #26 / branch `architecture/librarian-bootstrap-route-001` is Director routing only. It creates no Source IDs, Work IDs, hashes, bindings, or coverage. No separate Librarian-owned registry/source-binding implementation branch or PR was found at this checkpoint.

## Exhausted LIT-side searches

Current File Library searches have been performed for:

- both reported ebook ZIP names;
- `BOOK_TEXT` literary Sources;
- `SOURCE_BOUND` literary records;
- canonical book Source IDs;
- `STS-*` book Source identifiers;
- candidate individual titles including `The Wounded Sky`, `Metamorphosis`, `Vendetta`, and `Seven of Nine`.

Results exposed governance/checkpoint/crosswalk artifacts only, not complete byte-addressable literary Sources.

External/crosswalk metadata is not a substitute for book text and does not satisfy the LIT deep-read gate.

## Exact resume triggers

Refresh immediately when any of these occurs:

1. accepted `main` changes to include governed research infrastructure;
2. a Librarian-owned Source/Work registry or source-binding proposal appears;
3. readable bytes for either ebook container become exposed to the Librarian and produce byte-backed Source records;
4. accepted `main` gains at least one LIT-assigned Work with an accepted Source↔Work binding.

The first deep-research batch may begin only when **both** are true:

- governed research infrastructure is accepted; and
- at least one literary Work is accepted with sufficient byte-backed Librarian Source binding and complete readable text.

Then apply `ADMISSION_CHECKLIST.md`, select the next 1–3 eligible substantial Works, and execute complete-source research under `Source → Work → Local Entity → Evidence → Assertion`.

## No-work condition

If none of the resume triggers has occurred, additional title searches, external metadata gathering, speculative Work reconstruction, or semantic reading would cross LIT role boundaries or inflate coverage. At that point the correct LIT action is to remain blocked rather than manufacture progress.
