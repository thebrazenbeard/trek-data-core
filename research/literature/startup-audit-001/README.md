# LIT startup audit 001

## Scope

Star Trek Literary Corpus Research & Index (`LIT`) lane only.

This record captures the accepted-state startup audit while the repository has no accepted Librarian-owned literary Source/Work registry and no admitted LIT frontier. It does **not** advance literary research coverage and contains no semantic book research.

## Accepted-state pin

- accepted base: `main`
- accepted head observed: `007641c57933dda222489fff56555f6968ff2a53`
- accepted tree observed: `eb662d3dab7b47c26162a041bd315499be9385b0`
- accepted files observed: `README.md` and one-byte file `x`
- accepted LIT Work records observed: 0
- accepted LIT Source records observed: 0
- accepted LIT Source↔Work bindings observed: 0
- accepted LIT research batches observed: 0

The current accepted `x` file contains only the literal character `x`. It adds no governance, schema, registry, source binding, coverage mechanism, or corpus research. It is therefore accepted repository content but has no observed LIT/corpus effect.

These counts describe repository state only, not the real-world licensed Star Trek literary corpus.

## Literary admission requirement

LIT deep-reading begins only after the Librarian has sufficiently source-bound a literary Work and the accepted infrastructure can represent the batch honestly.

The eventual literary registry must preserve editions/release variants, omnibuses/anthologies versus contained works, multipart works, duplicate formats and derivative conversions, LIT/TXT/OPF lineage, alternate naming, series/subseries placement, and continuity/canon scope where applicable.

## Current Librarian/source evidence

Current Librarian artifacts remain migration/proposal evidence rather than accepted `main` state.

They report:

- candidate containers `Star_Trek_OPF_Converted(1).zip` and `ST ebooks(1).zip` are not byte-exposed to the Librarian;
- neither container is byte-verified, hashed, or assigned a Source ID;
- canonical book Sources remain 0;
- source-bound literary Works remain 0;
- preferred literary Sources remain 0;
- reading-ledger effect remains none;
- a legacy 14-Work abstract literary inventory is recoverable only as migration/convergence evidence, not accepted Work identity;
- unresolved historical collision classes include 84 high-confidence LIT↔TXT candidates, 121 title-overlap groups, and 41 suspicious short LIT-derived conversions;
- named source/container edge cases include `Ghost Ship`, `Millennium`, `A Time to...`, and `Worlds of Star Trek: Deep Space Nine, Volume Three`.

External candidate metadata/crosswalk work does not substitute for book bytes and created no accepted literary Source or Work identity.

Exhaustive LIT-side File Library searches for both ZIP names, `BOOK_TEXT`, `SOURCE_BOUND`, canonical book Source IDs, `STS-*`, and representative legacy candidate titles found no complete byte-addressable literary Source.

## Infrastructure state

PR #1 (`architecture/v0.1-bootstrap`) remains unaccepted at observed head `a26b444cd64be25c34cdb46c76721da7aeb777a2`.

LIT-relevant unresolved proposal gaps include:

- `FULL_TEXT_AVAILABLE` absent from the proposed processing ladder;
- no independent Librarian Source↔Work binding schema/registry;
- incomplete partition declaration (`SHORT` omitted);
- no accepted governed coverage-transition mechanism.

PR #33 (`architecture/admission-validation-v0.1`) has materially improved deterministic validation. At observed head `ec25f6525255fe019b4a51652d353eeb6ecd4844`, it checks schema conformance within the repository subset, cross-record references, predicates, batch hashes, record counts, manifest Work references, and manifest source hashes. Its current regression tests and `validate-core` workflow pass.

That progress remains proposal-only and does not itself supply literary Source↔Work binding, full-text availability semantics, legal coverage transitions, byte custody, source-family reconciliation, or closure of Auditor PR #19's separate reconciliation/provenance/diff findings.

Auditor PR #38 further confirms that worker-effort processing states cannot simply be promoted into the ordered governed coverage ladder when `SOURCE_BOUND=false`.

## Director queue control

Director issue #23 is open and pauses new episode/book close-read tranches while the admission bottleneck remains unresolved. It explicitly records LIT as correctly stopped at the missing accepted Work/Source registry and directs workers with no admitted frontier to remain at startup/blocker state.

Issue #14 remains the Librarian Source/Work dependency-clearing queue. Its latest Director refresh reports no Librarian/source-binding implementation branch or PR. The recommended first tranche is to define the binding shape and validate a small hard-case fixture set, including literary derivative/container distinctions, before broad binding expansion.

PR #26 was Director routing only and is closed without merge. It created no Source IDs, Work IDs, hashes, bindings, or coverage.

## Current blocker

The dependency sequence remains:

**accepted governance/schema/coverage infrastructure + byte custody → Librarian source-family reconciliation/binding → accepted literary Source/Work admission → full readable source availability → LIT deep-reading → legal coverage advancement**.

Selecting a title from memory, filenames, external metadata, legacy Work IDs, or proposal ordering would violate the current queue and Librarian ownership boundary.

## Validation constraints

This startup/readiness branch intentionally creates no canonical Source or Work IDs, local literary entities, evidence, assertions, continuity reconciliation, coverage advancement, or copyrighted source text.

## Resume condition

Recalculate from accepted `main` only after issue #23's minimum resume conditions are actually met: accepted governance/method, accepted usable schema/predicate contract, Librarian-owned Work/Source inventory and binding for the next LIT Works, and a governed coverage/admission mechanism sufficient to represent the batch honestly. Then select the next 1–3 eligible substantial Works and begin complete-source research under Source → Work → Local Entity → Evidence → Assertion.
