# LIT synchronization checkpoint 002

Status: **BLOCKED / SYNC-ONLY / NO COVERAGE EFFECT**

Role: Star Trek Literary Corpus Research & Index (`LIT`).

This checkpoint refreshes the literature lane against current accepted repository state and current dependency proposals. It does not perform book close-reading, mint Source/Work identity, or advance any coverage ledger.

## Accepted state

Accepted `main` remains authoritative.

Observed accepted state during this checkpoint:

- head: `007641c57933dda222489fff56555f6968ff2a53`
- tree: `eb662d3dab7b47c26162a041bd315499be9385b0`
- accepted top-level content: `README.md` plus one-byte file `x`
- accepted governance/method contract in repository: absent
- accepted usable research schema/predicate contract: absent
- accepted LIT Work records: 0
- accepted LIT Source records: 0
- accepted LIT Source↔Work bindings: 0
- accepted LIT research batches: 0

The accepted `x` file is unresolved repository drift and supplies no observed corpus, registry, schema, coverage, or literary meaning.

## Prior LIT proposal state

PR #16 (`Record LIT startup blocker pending source binding`) is **closed unmerged**. Its branch `research/lit/startup-audit-001` remains historical proposal material only. This checkpoint does not reopen, merge, rewrite, or delete it.

## Active queue control

Director issue #23 remains **OPEN** and explicitly reaffirms the hold on new episode/book close-read tranches while the admission bottleneck remains unresolved.

For LIT, the operative rule is therefore:

- do not begin another literary close-read tranche merely because a candidate title or source container is known;
- do not create canonical Source/Work IDs, binding state, coverage semantics, or predicate contracts locally;
- preserve proposal/history bytes and stop after a clean synchronization checkpoint.

The resume condition in #23 still requires accepted `main` to provide at minimum:

1. accepted governance/method contract;
2. accepted usable research schema/predicate contract;
3. Librarian-owned Work/Source inventory and accepted binding for LIT's next Works;
4. governed coverage/admission representation sufficient to record the batch honestly.

## Librarian / Source↔Work state

Issue #14 remains the active Librarian dependency-clearing queue.

Issue #31 was closed as duplicate coordination state and points back to #14 / #23.

Issue #65 now defines a stronger Director contract for an independent Librarian-owned `source_work_binding` concept. The contract requires, among other things:

- Source and Work identity remain independent;
- binding exists before downstream Evidence and independently of it;
- accepted evidence-bearing binding is required for `SOURCE_BOUND`;
- one-to-many / many-to-one mappings and source slices are legal;
- metadata/crosswalk-only association must not masquerade as `SOURCE_BOUND`;
- source lineage, provenance family, independence grouping, and `derived_from` remain reconstructable;
- container/member and derivative-format cases must not collapse physical source identity into Work identity;
- corrections append/supersede rather than rewrite history.

Issue #65 creates no Source IDs, Work IDs, bindings, or accepted coverage.

Fresh branch searches found:

- no `registry` branch;
- no `binding` branch;
- the only `libr*` branch is the older Director routing branch `architecture/librarian-bootstrap-route-001`;
- the only `source*` branch hit is an Auditor DS9 source-offset audit, not Librarian registry implementation.

Therefore no current Librarian-owned implementation branch was observed.

## Coverage contract state

Director issue #40 remains open and defines the independent ordered coverage semantics:

`DISCOVERED -> SOURCE_BOUND -> FULL_TEXT_AVAILABLE -> STRUCTURALLY_INDEXED -> CLOSE_READ -> SEMANTICALLY_ANALYZED -> ENTITY_LINKED -> CROSS_REFERENCED -> AUDITED`

It explicitly keeps `FULL_TEXT_AVAILABLE` separate from Source binding and close reading, and requires accepted/proposal accounting to remain distinct.

The contract remains proposal methodology, not accepted repository implementation.

## Validation / architecture state

PR #33 remains open/draft at observed head `bfe5515eeae65194e087d4b99fc5d378e38e16e7`.

It now materially enforces:

- schema constraints used by current proposed record schemas;
- typed-ID uniqueness and cross-record referential integrity;
- predicate-registry membership;
- deterministic batch hashes and record counts;
- manifest Work/source-hash references;
- lane `worker_id` ownership including `SHORT`;
- rejection of Librarian-owned Source/Work records inside worker batches;
- reconciliation decision exclusivity/supersession invariants.

PR #33 deliberately still does **not** invent the missing coverage-transition ledger or Librarian Source↔Work binding model.

PR #92 remains open/draft and proposes aligning the four root governance files with the bootstrap architecture on one branch. It has not been accepted into `main`.

These proposal improvements do not satisfy issue #23's accepted-state resume condition.

## Literary source custody refresh

Current File Library evidence is mixed and must not be flattened:

- older Librarian custody artifacts report both ebook containers as not byte-exposed and keep literary Source count / source-bound Work count at zero;
- a recent exported Vera conversation reports that `Star_Trek_OPF_Converted(1).zip` and `ST ebooks(1).zip` were supplied;
- current File Library searches by those exact names did **not** surface the ZIP objects themselves as byte-addressable files to this LIT worker.

Therefore the correct current LIT statement is:

**container supply is reported, but byte-addressable custody and Librarian binding remain unresolved from this lane's accessible evidence.**

This checkpoint does not infer hashes, archive membership, Source IDs, completeness, preferred source, or readable-book status from the report alone.

## No-work conclusion

No valid LIT deep-research batch can begin now because all of the following remain unmet in accepted `main`:

- governance/method admission;
- usable schema/predicate admission;
- Librarian Work/Source inventory;
- accepted Source↔Work binding for a literary Work;
- governed coverage/admission representation.

Additionally, issue #23 explicitly prohibits beginning a new book tranche while those conditions remain unmet.

## Exact next frontier

On the next LIT continuation:

1. refresh accepted `main` first;
2. refresh issue #23 status;
3. inspect #14/#65 or any successor Librarian implementation;
4. locate accepted LIT Work/Source/binding records if they exist;
5. verify `FULL_TEXT_AVAILABLE` for the selected bound Source;
6. only then select the next 1–3 substantial Works and execute the first governed complete-source batch under `Source -> Work -> Local Entity -> Evidence -> Assertion`.

Until that state exists, additional literary reading or local registry invention would violate the active Director hold and LIT/Librarian ownership boundary.
