# DS9 lane synchronization — 2026-08-17

## Scope

This is a Deep Space Nine (`DS9`) research-lane synchronization checkpoint only.

It does **not** perform new episode close reading, mint canonical Source/Work identities, advance accepted coverage, reconcile global identities, or modify any non-DS9 research partition.

The purpose is to reconcile preserved DS9 proposal work against current accepted `main`, obey Director issue #23, close stale corpus PR surfaces while preserving branches, record the one remaining source gap, and define the exact resume procedure.

## Accepted state pin

Accepted `main` is authoritative at:

- commit: `007641c57933dda222489fff56555f6968ff2a53`
- tree: `eb662d3dab7b47c26162a041bd315499be9385b0`
- visible top-level contents: `README.md` and one-byte path `x`

The `x` path is unresolved accepted-state drift tracked by Director coordination and is assigned no DS9 meaning here.

Current accepted `main` exposes:

- accepted DS9 Work records: 0
- accepted DS9 Source records: 0
- accepted DS9 Source↔Work bindings: 0
- accepted governed DS9 batches: 0
- accepted DS9 coverage-ledger entries: 0

These are repository-state observations only. They are **not** a claim that DS9 has zero real-world works, and no percentage denominator is asserted because the accepted Work inventory/coverage denominator does not yet exist.

## Active queue control

Director issue #23 remains open and explicitly pauses new corpus close-read tranches until the admission bottleneck clears.

Its enforcement requires workers to:

- preserve completed proposal bytes;
- close corpus research/staging PR surfaces;
- leave branches and commits unchanged;
- begin no new episode/book close-read tranche;
- avoid minting local canonical Source/Work/coverage contracts to bypass the shared blocker.

During this synchronization pass, the remaining open DS9 corpus staging PR surfaces were closed without merge, rebase, force-push, rewrite, or branch deletion:

- PR #81 — batch 021
- PR #83 — batch 022
- PR #85 — batch 023
- PR #101 — batch 024
- PR #102 — batch 025
- PR #103 — batch 026, created concurrently while this sync was being finalized

Auditor PRs #41 and #53 remain outside this disposition and were not closed.

## Preserved worker-effort inventory

There are 26 preserved DS9 staging branches representing 130 sequential proposal work slots from `Emissary` through `Resurrection`.

Of those slots:

- 129 have completed transcript-representation close reads preserved on proposal branches;
- 1 (`Shakaar`) remains `SOURCE_RETRIEVAL_BLOCKED` / partial and is not counted as a completed full-source close read;
- accepted DS9 coverage remains unchanged at zero accepted batch/coverage records on `main`.

This 129/130 count is a **proposal worker-effort inventory**, not accepted coverage and not an accepted corpus denominator.

| Batch | Preserved branch | PR | Preserved head | Worker-effort state |
|---|---|---:|---|---|
| 001 | `research/ds9/s1-opening-five-staging` | #2 | `114d96b41865eff37a309fea747e8a6404c3a512` | 5 complete |
| 002 | `research/ds9/ds9-s01-b002-staging` | #9 | `84d208dc222117cbf9befdd44bc486013f7811a3` | 5 complete |
| 003 | `research/ds9/ds9-s01-b003-staging` | #20 | `f2b4e74252e9e57913e756495f9a041f92ed99c7` | 5 complete |
| 004 | `research/ds9/ds9-s01-b004-staging` | #30 | `5b93e75cc54fdf84afe30d6d4d9c7db931eb828f` | 5 complete |
| 005 | `research/ds9/ds9-s02-b005-staging` | #35 | `6e964c60a8fca16a1c3e5f74d1f12aba98a5ad0b` | 5 complete |
| 006 | `research/ds9/ds9-s02-b006-staging` | #39 | `4ab3b99ce413fd868d065964f4188d462337994c` | 5 complete |
| 007 | `research/ds9/ds9-s02-b007-staging` | #42 | `e44d78a87fe10e237bce58087162689d62461d20` | 5 complete |
| 008 | `research/ds9/ds9-s02-b008-staging` | #46 | `0fc99a5b8c7f1750557e3370f7485cbab5f81b96` | 5 complete |
| 009 | `research/ds9/ds9-s02-b009-staging` | #48 | `107551e91bb823d591dc857e255d88726a917eba` | 5 complete |
| 010 | `research/ds9/ds9-s03-b010-staging` | #50 | `d53913a539a13465a9848658f14e81e502a54335` | 5 complete |
| 011 | `research/ds9/ds9-s03-b011-staging` | #51 | `7946a10938bec021c92e1f79111bb22c6a1ff455` | 5 complete |
| 012 | `research/ds9/ds9-s03-b012-staging` | #56 | `96a1fa64d1fb5a54655a80973bd1bdf4729bcf4e` | 5 complete |
| 013 | `research/ds9/ds9-s03-b013-staging` | #57 | `a693bd26009aaa522b26673cc3bb485f1950149d` | 5 complete |
| 014 | `research/ds9/ds9-s03-b014-staging` | #60 | `870a947d4b525968a4da51097f6aa8531f07b2d3` | 4 complete + `Shakaar` blocked |
| 015 | `research/ds9/ds9-s04-b015-staging` | #63 | `b01e33caecd1d535a82abbac694372ec281df9d0` | 5 complete |
| 016 | `research/ds9/ds9-s04-b016-staging` | #66 | `03ff6df1afddd47f1470045397158dd992b0e7e6` | 5 complete |
| 017 | `research/ds9/ds9-s04-b017-staging` | #70 | `29b647115f148244d3aa4cfc809b6911ec31babb` | 5 complete |
| 018 | `research/ds9/ds9-s04-b018-staging` | #73 | `4ebb3349967a7cf7170fc3c3d80960a0bf67202f` | 5 complete |
| 019 | `research/ds9/ds9-s04-b019-staging` | #77 | `c560cde832a804b3ea6c7beb0d302e61b818427c` | 5 complete |
| 020 | `research/ds9/ds9-s05-b020-staging` | #79 | `4096b87465c74f018fb4ddce177c4548a4b7e527` | 5 complete; prior `Nor the Battle to the Strong` gap resolved |
| 021 | `research/ds9/ds9-s05-b021-staging` | #81 | `80aa671835636ae3820d77731fd95469c90fcd00` | 5 complete |
| 022 | `research/ds9/ds9-s05-b022-staging` | #83 | `057f52c8ac087aa867703fc256da4548cde1bc4b` | 5 complete |
| 023 | `research/ds9/ds9-s05-b023-staging` | #85 | `341686699413f4e1fe4602bfa61c1c3aa1efb02c` | 5 complete; prior source gaps resolved |
| 024 | `research/ds9/ds9-s05-b024-staging` | #101 | `ae2458e1682c7b5e5e4182780e6647885ee6e0f0` | 5 complete |
| 025 | `research/ds9/ds9-s06-b025-staging` | #102 | `5a0dd8cd28e208d3a7a1cf0cf1cffe5005fa9655` | 5 complete |
| 026 | `research/ds9/ds9-s06-b026-staging` | #103 | `e1869ed8f62d41c15566eeac6f9725cf8d58a53a` | 5 complete |

## Proposal sequence boundary

The preserved proposal sequence now reaches Season 6 through:

- `Behind the Lines`
- `Favor the Bold`
- `Sacrifice of Angels`
- `You Are Cordially Invited`
- `Resurrection`

`Statistical Probabilities` is therefore the next **provisional external sequence title** after the preserved worker-effort frontier.

That is **not** authorization to begin it. Issue #23 requires the lane to stop, and after the admission gate clears the accepted frontier must be recalculated from `main`; proposal sequence does not automatically become accepted sequence.

## Outstanding source/provenance state

### `Shakaar`

`Shakaar` remains the sole known preserved full-source gap in the DS9 proposal chain.

Batch 014 contains partial research only and explicitly records `SOURCE_RETRIEVAL_BLOCKED`. Multiple later DS9 proposal checkpoints continue to carry this historical gap forward rather than silently treating it as complete.

Under the current hold, no fresh source-recovery pass is started here. Once admission resumes, the lane should first re-evaluate the accepted Work/Source binding and then recover/close-read a complete bound research representation for `Shakaar` before claiming continuous close-read coverage through the preserved sequence.

### Springfield season-one metadata/body offset

Auditor PR #41 independently confirmed the Springfield season-one page-heading/URL-numbering offset versus transcript body identity for the opening DS9 source family.

Required normalization invariant:

- preserve provider URL/index/title metadata as observed;
- preserve transcript-body Work identity separately;
- do not silently rewrite source metadata;
- do not count correlated provider metadata as independent corroboration.

### Source representation limits

Across preserved DS9 staging:

- research generally used complete third-party transcript/subtitle representations when available;
- primary audiovisual masters were not directly verified;
- transcript-provider lineage independence remains unresolved/UNKNOWN unless explicitly established;
- repeated analyses of the same upstream representation must not be counted as independent source corroboration;
- no canonical Source/Work IDs or reproducible governed binding hashes were minted by the DS9 worker.

## Topology / normalization debt

Auditor PR #53 found that early corpus research PRs targeting `architecture/v0.1-bootstrap` had unsafe integration topology: merging those PRs into their declared base would couple architecture acceptance to corpus staging history.

Preserved research bytes are not rejected, but historical branches must not be merged through that architecture base.

Later DS9 batches 024, 025, and 026 were deliberately based directly on accepted `main`, avoiding that specific topology defect, but they remain proposal-only and still lack the accepted Source↔Work/admission dependencies.

When normalization becomes legal, the worker should migrate/re-express preserved DS9 records into governed bounded batches from the then-current accepted base rather than rewriting or force-moving the historical proposal branches.

## Current shared blockers

The DS9 lane remains blocked by the same project-wide dependencies recorded in Director issue #23:

1. accepted governance/method contract;
2. accepted usable research schema and predicate contract;
3. Librarian-owned Work/Source inventory and accepted Source↔Work binding for the relevant DS9 Works;
4. governed coverage/admission representation.

Related active dependency surfaces include:

- issue #14 — Librarian Source/Work registry tranche;
- issue #65 — Source↔Work binding and provenance-lineage contract;
- issue #40 — independent coverage-ledger/denominator contract;
- PR #92 — governance/bootstrap alignment proposal;
- PR #82 / PR #33 and successor Consolidator work — admission/projection implementation;
- Auditor re-review/calibration work.

None of those proposal/infrastructure surfaces is treated as accepted merely because it exists or has green CI.

## Resume procedure

When Director issue #23's resume condition is actually satisfied on accepted `main`:

1. refresh accepted `main` and pin the exact accepted governance/schema/predicate/registry/coverage state;
2. read the accepted DS9 Work inventory rather than using this proposal sequence as a denominator;
3. map preserved batch material to accepted Work/Source bindings without rewriting historical proposal branches;
4. preserve source-family lineage, especially the audited Springfield offset case;
5. normalize bounded batches into the governed Source → Work → Local Entity → Evidence → Assertion model;
6. validate each normalized batch under the accepted admission tooling before advancing any accepted coverage ledger;
7. recover and fully process `Shakaar` if it remains unbound/incomplete in accepted state;
8. only then recalculate the exact next new-work frontier from accepted coverage.

If the accepted inventory and normalized preserved sequence still align, `Statistical Probabilities` is the provisional next new title after `Resurrection`. That conclusion must be recomputed, not assumed.

## Authority boundary

This synchronization checkpoint performs no:

- merge;
- branch deletion;
- rebase or force-push;
- credential/permission/protection change;
- deployment/publication;
- canonical Source/Work creation;
- global identity reconciliation;
- accepted coverage advancement;
- new episode close read;
- copyrighted transcript ingestion.

Historical proposal branches remain preserved as migration/normalization inputs.