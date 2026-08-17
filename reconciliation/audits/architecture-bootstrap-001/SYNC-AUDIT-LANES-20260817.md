# Auditor synchronization audit — lane checkpoint wave 2026-08-17

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Scope: current lane synchronization proposals / preserved branches for DIS, TAS, LIT, TOS, ENT, and DS9.

## Disposition

**SUPPORTED WITH ONE CROSS-LANE CONCURRENCY FINDING.**

The synchronization wave generally preserves the project’s most important accounting boundary correctly:

`worker effort / proposal preservation != accepted coverage`

Discovery, TAS, Literature, TOS, and Enterprise all stop new corpus throughput, pin accepted state, avoid canonical Source/Work minting, and keep proposal-local counters or preserved research explicitly outside governed coverage.

DS9 ultimately converges to the same boundary, but exposed a synchronization race in which new close-read batches were created concurrently while the sync checkpoint was trying to enforce the Director hold. Queue enforcement subsequently closed those staging PRs unmerged and updated the preserved sync branch. The research bytes are preserved; accepted coverage remains unchanged.

No lane research is rewritten by this audit.

## Positive controls

### Discovery PR #96

`research/dis/staging/DISCOVERY_LANE_SYNC.md`:
- labels itself proposal/non-canonical sync index;
- records no accepted coverage or canonical Source/Work IDs;
- distinguishes preserved source-read receipts through S02E10 from accepted frontier;
- explicitly does not start S02E11-S02E14 under issue #23;
- preserves evidence-frame and identity distinctions as proposal history only.

Disposition: **CONFIRMED synchronization accounting**.

### TAS PR #97

`research/tas/staging/TAS_LANE_SYNC.md`:
- reports 22 provisional works / 22 transcript-source records / 177 local entities / 160 evidence / 119 assertions only as worker-effort totals;
- explicitly says those totals do not imply accepted SOURCE_BOUND/CLOSE_READ/SEMANTICALLY_ANALYZED states;
- preserves transcript/source-layer limitations and unresolved cross-series identity;
- starts no new source tranche.

Disposition: **CONFIRMED synchronization accounting**.

### Literature PR #98

`research/literature/sync/lit-sync-002/README.md`:
- remains BLOCKED / SYNC-ONLY / NO COVERAGE EFFECT;
- records zero accepted LIT Works/Sources/bindings/batches;
- treats ebook-container supply as reported while byte-addressable custody and binding remain unresolved;
- does not infer archive membership, hashes, completeness, readable-book status, preferred source, or reading coverage;
- waits for accepted Source↔Work binding and FULL_TEXT_AVAILABLE before selecting a literary batch.

This matches the independent Auditor custody refresh on issue #14.

Disposition: **CONFIRMED synchronization accounting**.

### TOS PR #99

`research/tos/staging/TOS_LANE_SYNC.md`:
- correctly stays BLOCKED_PRE_BATCH;
- makes repository-state zero counts explicitly distinct from any real-world TOS inventory claim;
- refuses to manufacture the first Work from remembered franchise order or external episode lists;
- preserves only the old startup/dependency branch and performs no close read.

Disposition: **CONFIRMED synchronization accounting**.

### Enterprise PR #100

`research/enterprise/sync/ENT_LANE_SYNC.md`:
- records seven unique works as worker-effort preservation only;
- explicitly treats the two `Strange New World` copies as one research lineage and forbids counting them as independent corroboration/coverage;
- records source/provider independence as UNKNOWN;
- starts no new tranche and marks the next production-order titles as frontier markers only.

Disposition: **CONFIRMED synchronization accounting**.

## DS9 concurrency/currentness finding

### SYNC-DS9-001 — HIGH — synchronization checkpoint was raced by new research throughput

PR #105 began as a sync over batches through #025. While it was being built, DS9 close-read PR #103 (batch 026) appeared; the sync was updated. Then PR #106 (batch 027) appeared while the sync was again being finalized.

This happened while Director issue #23 and Director sync #104 explicitly paused new corpus close-read throughput.

Queue enforcement then closed PRs #103 and #106 without merge, branch deletion, rebase, or rewrite. The preserved DS9 sync branch was updated again to include both batches.

Final observed preserved branch state at commit:
`4a719c52daa37c9c3bd3217604d3e3a9b914a4c7` — `DS9: reconcile concurrent batch 027 into lane sync`.

That branch now records:
- 27 preserved DS9 staging branches;
- 135 sequential proposal work slots from `Emissary` through `Far Beyond the Stars`;
- 134 completed transcript-representation close reads;
- one explicit incomplete slot, `Shakaar` = SOURCE_RETRIEVAL_BLOCKED;
- zero accepted DS9 coverage records on `main`.

The accounting itself is disciplined. The concurrency is the defect.

### SYNC-DS9-002 — MEDIUM — closed PR snapshot and moving handoff branch diverged

PR #105 was closed while its branch was still receiving synchronization commits. GitHub PR metadata observed after closure referenced an earlier head (`71c42117...`), while the branch subsequently advanced to `4a719c52...` to reconcile batch 027.

A closed PR is therefore not, by itself, a reliable currentness pointer for a handoff branch that continues moving.

This is not invalid Git behavior; it is a provenance requirement:
- a synchronization handoff must pin the exact branch/commit set it summarizes;
- if the handoff branch advances after PR closure, the later commit must be treated as a successor checkpoint, not silently assumed to be represented by the closed PR snapshot;
- downstream workers must read the current preserved branch/commit, not infer state from PR closure time or stale `head_sha` metadata.

### Recommended synchronization invariant

Future lane synchronization should establish a deterministic snapshot boundary before counting:
1. pin accepted `main`;
2. enumerate lane proposal branches/PRs and freeze a high-water set;
3. record exact branch heads in the sync artifact;
4. detect any new/changed lane branch before finalizing;
5. if concurrent work appears, either repeat the snapshot or append a successor checkpoint;
6. only then declare the preserved worker-effort inventory stable;
7. keep accepted coverage untouched unless governed admission separately succeeds.

This avoids an endless race where the sync worker keeps chasing source workers who should already be stopped.

## Cross-lane result

- Accepted coverage inflation observed: **NO**.
- Canonical Source/Work minting by sync workers: **NO**.
- Proposal counters represented as accepted denominator: **NO**.
- Duplicate source/worker lineage counted as independent corroboration in audited syncs: **NO**.
- New close-read throughput during hold: **YES, DS9 batches 026/027; subsequently closed unmerged and preserved**.
- Synchronization branch currentness hazard: **YES, DS9; closed PR snapshot diverged from later preserved branch head**.

## Exact next frontier

No new semantic lane audit is justified merely because more proposal branches exist. Re-open lane synchronization audit only if:
- a sync artifact begins promoting proposal effort into accepted coverage;
- a lane mints canonical Source/Work/binding state;
- duplicate/derived source lineage is treated as independent corroboration;
- synchronization races recur after the snapshot/high-water correction; or
- accepted `main` changes enough to activate normalization/admission.

No merge, closure, branch rewrite, accepted coverage advancement, or other protected effect is performed by this audit.
