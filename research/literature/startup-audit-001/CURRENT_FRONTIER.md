# LIT current frontier

Status: **BLOCKED BEFORE DEEP RESEARCH / DIRECTOR QUEUE HOLD ACTIVE**

This is a literature-lane preservation checkpoint only. It does not create Source/Work identity, coverage semantics, validation contracts, or literary research coverage.

## Accepted state

Accepted `main` observed during this checkpoint:

- head: `007641c57933dda222489fff56555f6968ff2a53`
- tree: `eb662d3dab7b47c26162a041bd315499be9385b0`
- accepted files: `README.md` plus one-byte file `x`
- accepted LIT Works: 0
- accepted LIT Sources: 0
- accepted LIT Source↔Work bindings: 0
- accepted LIT research batches: 0

The `x` file contains only `x` and has no observed corpus/governance effect.

## Director queue hold

Issue #23 is open and controls worker allocation while the admission bottleneck remains unresolved.

For LIT, the applicable instructions are:

- do not begin another book close-read tranche merely to keep the lane busy;
- a lane with no admitted frontier remains at startup/blocker state;
- do not mint worker-local canonical Source/Work IDs, predicate standards, coverage semantics, or validation contracts;
- preserve existing proposal work as future migration/normalization input;
- recalculate the frontier from accepted `main` only after the minimum resume condition lands.

Issue #23 explicitly lists LIT among the lanes that correctly stopped at the missing accepted Work/Source registry.

## Infrastructure gate

- PR #1 `Bootstrap provenance-aware Trek research architecture`
  - observed head: `a26b444cd64be25c34cdb46c76721da7aeb777a2`;
  - canonical five-object flow corrected;
  - `FULL_TEXT_AVAILABLE` still absent;
  - no independent Source↔Work binding record/schema;
  - partition list still omits SHORT;
  - remains unaccepted.

- PR #33 `Consolidator: strengthen research admission validation`
  - observed head: `ec25f6525255fe019b4a51652d353eeb6ecd4844`;
  - validates repository schema subset, record references, predicates, batch hash, declared counts, manifest Work references, and manifest source hashes;
  - regression suite includes invalid Source, dangling Assertion evidence, unregistered predicate, and bad batch-hash rejection;
  - current `validate-core` workflow succeeds;
  - remains proposal-only and does not create Source↔Work binding or coverage-transition/full-text semantics.

- PR #19 retains separate Auditor findings around deterministic reconciliation application, provenance/evidence projection observability, and governed semantic diff classes. PR #33 does not by itself close those findings.

- PR #38 establishes that worker-effort processing flags cannot be imported unchanged into the governed ordered coverage ladder when `SOURCE_BOUND=false`.

## Librarian/source gate

Issue #14 is the active Librarian dependency-clearing queue.

Its current Director guidance says the first tranche should optimize for dependency leverage rather than bulk binding:

1. define the Source↔Work binding shape;
2. bind a small cross-lane hard-case fixture set, including literary derivative/container distinctions;
3. validate those bindings deterministically;
4. only then expand binding coverage.

Latest repository/issue scans still expose no Librarian-owned source-binding implementation branch or PR.

Current literary custody state remains:

- `Star_Trek_OPF_Converted(1).zip`: reported, not byte-exposed;
- `ST ebooks(1).zip`: reported, not byte-exposed;
- canonical literary Sources: 0;
- source-bound literary Works: 0;
- preferred Sources: 0;
- book-reading ledger effect: none.

Legacy 14-Work state remains migration/convergence evidence only. Historical collision/quality warnings remain unresolved for the 84 LIT↔TXT candidate class, 121 title-overlap groups, 41 suspicious short derived conversions, `Ghost Ship`, `Millennium`, `A Time to...`, and `Worlds of Star Trek: Deep Space Nine, Volume Three`.

PR #26 was Director routing only and is closed unmerged.

## Exhausted LIT-side work under the active hold

Within LIT authority, the following work is complete for the current checkpoint:

- accepted-state refresh;
- startup/blocker proposal preservation;
- Librarian custody/collision/crosswalk dependency review;
- exhaustive File Library search for available literary bytes/bound Sources;
- architecture compatibility review;
- validator-successor review through current PR #33 head;
- ordered-coverage audit incorporation from PR #38;
- Director queue #23 and Librarian queue #14 reconciliation;
- explicit first-source admission readiness notes preserved without creating canonical IDs or coverage semantics.

No additional source reading, title selection, speculative Work reconstruction, external metadata trawling, or new LIT contract creation is authorized or useful while the hold remains active.

## Exact resume condition

Do not begin a new LIT research batch until accepted `main` provides, at minimum:

- accepted governance/method contract;
- accepted usable research schema/predicate contract;
- Librarian-owned Work/Source inventory and binding for LIT's next Works;
- a governed coverage/admission mechanism sufficient to represent the batch honestly;
- complete readable source availability for the selected literary Source(s).

When those conditions land, refresh accepted `main`, ignore old proposal ordering as an authority source, apply the accepted admission rules, select the next 1–3 eligible substantial Works, and begin complete-source research.

## Current next frontier

**External dependency only:** first accepted governance/schema/coverage + Librarian Source↔Work admission event satisfying issue #23.

Until that event occurs, there is no further valid LIT execution unit.
