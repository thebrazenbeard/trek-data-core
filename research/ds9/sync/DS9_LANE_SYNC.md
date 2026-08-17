# DS9 lane synchronization — 2026-08-17

## Scope

This is a Deep Space Nine (`DS9`) research-lane synchronization checkpoint only.

It does **not** perform new episode close reading, mint canonical Source/Work identities, advance accepted coverage, reconcile global identities, or modify any non-DS9 research partition.

The purpose is to reconcile preserved DS9 proposal work against current accepted `main`, obey Director issue #23, close corpus PR surfaces while preserving branches, record source/provenance changes, and define the exact resume procedure.

## Accepted state pin

Accepted `main` remains authoritative at:

- commit: `007641c57933dda222489fff56555f6968ff2a53`
- tree: `eb662d3dab7b47c26162a041bd315499be9385b0`
- visible top-level contents: `README.md` and one-byte path `x`

The `x` path remains unresolved accepted-state drift and is assigned no DS9 meaning here.

Current accepted `main` exposes:

- accepted DS9 Work records: 0
- accepted DS9 Source records: 0
- accepted DS9 Source↔Work bindings: 0
- accepted governed DS9 batches: 0
- accepted DS9 coverage-ledger entries: 0

These are repository-state observations only, not a claim that DS9 has zero real-world works. No accepted denominator exists, so no percentage is asserted.

## Active queue control

Director issue #23 remains active. New corpus close-read tranches are paused until accepted governance, usable schema/predicate contracts, Librarian-owned binding for the relevant Works, and governed coverage/admission machinery exist on `main`.

The Director's enforcement requires corpus workers to preserve completed proposal bytes, close research/staging PR surfaces, leave branches/commits unchanged, and avoid creating local canonical registry or coverage semantics to bypass the shared gate.

Previously closed under this disposition:

- #81 batch 021
- #83 batch 022
- #85 batch 023
- #101 batch 024
- #102 batch 025
- #103 batch 026
- #106 batch 027

This synchronization refresh additionally closed, unmerged and without changing their branches:

- #120 batch 028
- #122 batch 029
- #123 batch 030
- #124 batch 031
- #126 batch 032

Auditor PRs #41 and #53 remain outside this disposition. Synchronization PR #105 remains closed; this branch is the durable DS9 handoff.

## Preserved worker-effort inventory

There are now 32 preserved DS9 staging batches representing 160 sequential proposal work slots from `Emissary` through `The Emperor's New Cloak`.

All 160 slots now have a complete transcript-, subtitle-, or production-script research representation close-read preserved on proposal branches. This is **proposal worker effort**, not accepted coverage and not an accepted corpus denominator.

| Batch | Preserved branch | PR | Preserved/current head | Worker-effort state |
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
| 014 | `research/ds9/ds9-s03-b014-staging` | #60 | `1937091ed5df5881694a2d3b2f490adec92539a3` | 5 complete; `Shakaar` gap closed by production-script read |
| 015 | `research/ds9/ds9-s04-b015-staging` | #63 | `b01e33caecd1d535a82abbac694372ec281df9d0` | 5 complete |
| 016 | `research/ds9/ds9-s04-b016-staging` | #66 | `03ff6df1afddd47f1470045397158dd992b0e7e6` | 5 complete |
| 017 | `research/ds9/ds9-s04-b017-staging` | #70 | `29b647115f148244d3aa4cfc809b6911ec31babb` | 5 complete |
| 018 | `research/ds9/ds9-s04-b018-staging` | #73 | `4ebb3349967a7cf7170fc3c3d80960a0bf67202f` | 5 complete |
| 019 | `research/ds9/ds9-s04-b019-staging` | #77 | `c560cde832a804b3ea6c7beb0d302e61b818427c` | 5 complete |
| 020 | `research/ds9/ds9-s05-b020-staging` | #79 | `4096b87465c74f018fb4ddce177c4548a4b7e527` | 5 complete; prior source gap resolved |
| 021 | `research/ds9/ds9-s05-b021-staging` | #81 | `80aa671835636ae3820d77731fd95469c90fcd00` | 5 complete |
| 022 | `research/ds9/ds9-s05-b022-staging` | #83 | `057f52c8ac087aa867703fc256da4548cde1bc4b` | 5 complete |
| 023 | `research/ds9/ds9-s05-b023-staging` | #85 | `341686699413f4e1fe4602bfa61c1c3aa1efb02c` | 5 complete; prior source gaps resolved |
| 024 | `research/ds9/ds9-s05-b024-staging` | #101 | `ae2458e1682c7b5e5e4182780e6647885ee6e0f0` | 5 complete |
| 025 | `research/ds9/ds9-s06-b025-staging` | #102 | `5a0dd8cd28e208d3a7a1cf0cf1cffe5005fa9655` | 5 complete |
| 026 | `research/ds9/ds9-s06-b026-staging` | #103 | `e1869ed8f62d41c15566eeac6f9725cf8d58a53a` | 5 complete |
| 027 | `research/ds9/ds9-s06-b027-staging` | #106 | `a03a34918ebfec12a4119532239f59c09a79b82a` | 5 complete |
| 028 | `research/ds9/ds9-s06-b028-staging` | #120 | `5ff1e78056145a3375890959544c3b5ef9cfbd95` | 5 complete production-script reads |
| 029 | `research/ds9/ds9-s06-b029-staging` | #122 | `6919cac91273b2c3a22a480193906cbbcd684d3c` | 5 complete production-script reads |
| 030 | `research/ds9/ds9-s07-b030-staging` | #123 | `495fbb66bd32ecdf14e7d991265b856b76ed5740` | 5 complete production-script reads |
| 031 | `research/ds9/ds9-s07-b031-staging` | #124 | `e3a46e8a3d5a4c8693c39e1af596d7514b21aa02` | 5 complete production-script reads |
| 032 | `research/ds9/ds9-s07-b032-staging` | #126 | `c3e26cfe89522045912e5a56ca19321362d66bb4` | 5 complete production-script reads |

## Source-gap update: `Shakaar`

The previous `Shakaar` full-source blocker is closed at the proposal-worker layer.

The batch-014 branch now carries `SOURCE_GAP_CLOSURE.md` and records a complete close read of Paramount production script `#40513-470` from Star Trek Minutiae. This supersedes the stale `SOURCE_RETRIEVAL_BLOCKED` status in the original batch README without rewriting that historical record.

The source-variant distinction remains important: this is a production script and is **not** asserted byte-identical to the final broadcast transcript or audiovisual master.

There is therefore no known historical full-research-representation gap in the preserved 160-work-slot sequence through batch 032.

## Proposal sequence boundary

The preserved sequence currently reaches Season 7 through:

- `The Siege of AR-558`
- `Covenant`
- `It's Only a Paper Moon`
- `Prodigal Daughter`
- `The Emperor's New Cloak`

`Field of Fire` is the next **provisional external-sequence title** after this preserved worker-effort frontier.

That is not authorization to begin it. Under issue #23 the lane remains stopped, and the accepted frontier must later be recomputed from accepted `main` rather than inherited from proposal chronology.

## Source/provenance limits

The preserved DS9 research now spans multiple research-representation kinds, including third-party transcript/subtitle representations and Paramount production scripts surfaced through Star Trek Minutiae.

Do not flatten those into one source type or assume production-script wording equals the final aired audiovisual work. Primary audiovisual masters were not directly verified by this worker unless explicitly recorded in an individual packet.

Provider lineage/independence remains Librarian work. Repeated analyses or derivative copies of one upstream representation add zero independent corroboration merely because another worker read them.

The audited Springfield season-one page-heading/body offset remains a required normalization fixture: provider metadata must be preserved separately from body-supported Work identity.

## Topology / normalization debt

Auditor PR #53 found the early architecture-stacked research topology unsafe for integration. Historical branches must remain preserved rather than merged through the architecture proposal.

Later batches were created directly from accepted `main`, avoiding that specific topology defect, but they still remain unaccepted proposal bytes.

When admission becomes legal, preserved DS9 work should be migrated/re-expressed into governed bounded batches from the then-current accepted base. Historical proposal branches must not be rewritten or force-moved merely to make integration prettier.

## Current shared blockers and dependency progress

The Director hold remains active because accepted `main` still lacks the required governance/schema/binding/coverage admission state.

There has been real proposal progress: Librarian draft PR #125 now implements a bounded Source / Work / `source_work_binding` contract with provenance-family and independence semantics plus adversarial fixtures, including the audited DS9 metadata/body mismatch case. It is explicitly proposal-only and creates no accepted corpus Source, Work, binding, or coverage state.

Therefore PR #125 does **not** clear the DS9 resume gate by existing. Accepted `main` still needs the required contracts and accepted DS9 bindings before normalization or new throughput resumes.

Related dependency surfaces include issue #23, issue #14, issue #65, issue #40, Director PR #104, Librarian PR #125, and the current integrated architecture/Consolidator line plus Auditor re-review.

## Resume procedure

When issue #23's conditions are actually satisfied on accepted `main`:

1. refresh and pin accepted governance/schema/predicate/registry/coverage state;
2. read the accepted DS9 Work inventory rather than using this proposal sequence as the denominator;
3. map preserved research to accepted Source↔Work bindings, preserving source variants and lineage;
4. preserve the Springfield metadata/body mismatch and the production-script-versus-aired distinction;
5. normalize the preserved batches into governed Source → Work → Local Entity → Evidence → Assertion records without rewriting historical proposal branches;
6. validate each normalized batch under accepted admission tooling before advancing any coverage ledger;
7. only then recalculate the exact next new-work frontier from accepted state.

If the accepted inventory and normalized sequence still align, `Field of Fire` is the provisional next title after `The Emperor's New Cloak`. That must be recomputed, not assumed.

## Authority boundary

This synchronization performs no merge, branch deletion, rebase, force-push, credential/permission/protection change, deployment, canonical Source/Work creation, global identity reconciliation, accepted coverage advancement, or new episode close read.

Historical proposal branches remain preserved as migration/normalization inputs.