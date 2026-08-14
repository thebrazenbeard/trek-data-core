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

Current relevant proposals/findings:

- PR #1 `Bootstrap provenance-aware Trek research architecture`
  - current proposal head observed: `a26b444cd64be25c34cdb46c76721da7aeb777a2`;
  - canonical five-object flow is corrected;
  - `FULL_TEXT_AVAILABLE` remains absent from the proposed processing ladder;
  - no independent Source↔Work binding record/schema is present;
  - `research/README.md` still omits SHORT.

- PR #33 `Consolidator: strengthen research admission validation`
  - current head observed: `1bf5eedb9bebfc5a3c96300263bc7fdc643d1363`;
  - proposal now performs schema-subset enforcement, cross-record referential integrity, and predicate-registry membership checks;
  - regression tests cover schema-invalid Source rejection, dangling Assertion evidence, and unregistered predicates;
  - current `validate-core` workflow at that head succeeded;
  - still proposal-only and does not provide Source↔Work binding, `FULL_TEXT_AVAILABLE`, legal coverage transitions, byte custody, or source-family semantics.

- PR #19 `Audit architecture bootstrap validation and projection gate`
  - Auditor finding set remains proposal state;
  - the original validation defect is materially reduced by PR #33 but is not accepted infrastructure yet;
  - separate CRITICAL findings remain around deterministic application of accepted reconciliation and provenance/evidence observability in projection/hash;
  - HIGH semantic-diff finding remains separate.

- PR #38 `Audit TNG proposal batch tng-s01-b001`
  - confirms worker-effort processing states cannot simply be imported into the ordered governed coverage ladder when `SOURCE_BOUND=false`;
  - reinforces the distinction between performed close-reading work and legally admitted coverage tiers.

- PR #32 `Director: refresh gate after accepted-main head movement`
  - confirms accepted tree remains README-only;
  - records PR #1 as unaccepted/gated and research staging as proposal-only.

Infrastructure admission condition: corrected infrastructure must be validated/audited and then become accepted `main` state. LIT does not decide or perform that acceptance.

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

PR #26 / branch `architecture/librarian-bootstrap-route-001` was Director routing only and is now **closed unmerged**. It created no Source IDs, Work IDs, hashes, bindings, or coverage. Latest branch/PR searches found no separate Librarian-owned registry/source-binding implementation.

## Exhausted LIT-side searches

Current File Library and repository searches have been performed for:

- both reported ebook ZIP names;
- `BOOK_TEXT` literary Sources;
- `SOURCE_BOUND` literary records;
- canonical book Source IDs;
- `STS-*` book Source identifiers;
- candidate individual titles including `The Wounded Sky`, `Metamorphosis`, `Vendetta`, and `Seven of Nine`;
- Librarian/source-binding branches and PRs;
- Source↔Work binding implementation;
- `FULL_TEXT_AVAILABLE` / coverage-transition implementation.

Results exposed governance/checkpoint/crosswalk artifacts and infrastructure proposals only, not complete byte-addressable literary Sources or an admitted literary binding implementation.

External/crosswalk metadata is not a substitute for book text and does not satisfy the LIT deep-read gate.

## Exact resume triggers

Refresh immediately when any of these occurs:

1. accepted `main` changes to include governed research infrastructure;
2. a Librarian-owned Source/Work registry or source-binding implementation appears;
3. readable bytes for either ebook container become exposed to the Librarian and produce byte-backed Source records;
4. accepted `main` gains at least one LIT-assigned Work with an accepted Source↔Work binding;
5. accepted coverage semantics include `FULL_TEXT_AVAILABLE` and enforce legal coverage transitions.

The first deep-research batch may begin only when **both** are true:

- governed research infrastructure is accepted with sufficient literary coverage semantics; and
- at least one literary Work is accepted with sufficient byte-backed Librarian Source binding and complete readable text.

Then apply `ADMISSION_CHECKLIST.md`, select the next 1–3 eligible substantial Works, and execute complete-source research under `Source → Work → Local Entity → Evidence → Assertion`.

## No-work condition

If none of the resume triggers has occurred, additional title searches, external metadata gathering, speculative Work reconstruction, or semantic reading would cross LIT role boundaries or inflate coverage. At that point the correct LIT action is to remain blocked rather than manufacture progress.
