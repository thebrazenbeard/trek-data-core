# Branch consolidation: current heads versus accepted work

Observed 2026-11-02 UTC, after merge of official metadata pilot PR #176.
Source of truth: GitHub's public `refs/heads/*` as returned by a read-only
`git ls-remote --heads` of `thebrazenbeard/trek-data-core`, cross-checked with
the GitHub compare endpoint against accepted `main` commit
`d0dc1e599db1a920953f23c62b91202e4087cc89`. This is a **point-in-time
census**, not a permanent branch count or authorization to delete a branch.

## What the names conceal

| Live observation | Count |
| --- | ---: |
| Total branch names, including `main` | **194** |
| Non-main branch names | **193** |
| Distinct non-main tip commits | **9** |
| Duplicate names beyond one name per distinct tip (including `main`) | **184** |
| `research/*` branch names | **153** |

Four legacy tip commits alone account for **188** non-main names. A branch
named for a particular Mission, season, or five-episode batch is therefore
**not evidence that the corresponding episodes were ingested**. A branch ref
is a pointer to a commit, not a record of completed research. The public
Explorer still separates twelve Mission catalog entries and 190 unverified
external metadata leads from **zero accepted non-fixture Mission Briefings**.

| Exact tip commit | Branch names | Relation to `main` | Assessment |
| --- | ---: | --- | --- |
| `a9ebf9e4d7e1645e3d9c7be2c6766cd3b04bfc86` | 170 | Diverged, 1 branch-only / 32 main-only commits | Shared historical placeholder across many research lanes; carries old editor startup task signal. Not a research corpus. |
| `e710a8b7d29de8f3afe1c1b91d3ffbb8518c8761` | 12 | Diverged, 1 / 32 | Legacy governance/architecture aliases with old editor startup task signal. |
| `104f0813fe29517e3b8900ad0d8e5f4dfd2bebe6` | 4 | Ancestor, 0 / 31 | Historical base, not independently unmerged work; old task signal. |
| `7b4782f88558b9b9c51a775d4abef159a920252c` | 2 | Diverged, 1 / 32 | Early architecture variants and old task signal. |
| `e9f1fa806449532b52deea6ad6c6d6956becfa56` | 1 | Diverged, 6 / 31 | Historical editor-startup containment; compare with accepted remediation before any reuse. |
| `b546c1a69ff8fb0c1602425bf1a8b11664de98ae` | 1 | Diverged, 4 / 25 | Old Explorer UI branch; superseded by merged PR #175. |
| `10959de4ffae19de56719990630547ec794b2f97` | 1 | Diverged, 6 / 25 | Old Research Leads UI branch; superseded by merged PR #175. |
| `0b12f1e427d004e7968d161b411501441ab31f7e` | 1 | Diverged, 7 / 25 | Old optional-fifth-asset guard; superseded by merged PR #174. |
| `1f158011e93919e2bed6b29edc3a9b935ff41556` | 1 | Diverged, 1 / 25 | Old official TNG metadata pilot; superseded by merged PR #176. |

The remaining distinct tip is the accepted `main` commit above. The four
superseded feature proposals are still visible as branch names, while their
draft PRs (#164, #170, #171, #172) have been closed. Closure **does not delete
those branches or erase their history**.

## Why not mass-merge or mass-delete?

- Old `.vscode` task and `public/fonts` artifacts appear in historical tree
  comparisons. The current startup-safety guard does **not** authorize running
  scripts, editor tasks, hooks, or binaries recovered from these old heads.
- Historical PR heads are a separate population from `refs/heads/*`. The
  [pinned historical census](../reports/branch-census-2026-11-02.json) observed
  132 accessible PR head refs, 593 distinct historical paths and 25 contested
  paths at its earlier base. These are **not** 132 accepted data batches.
- A shared tip can be safely classified once for code content, but branch
  owners and external references may still depend on each **name**. Equality
  of commit hashes alone is insufficient permission to remove names.
- The public repository's acceptance protocol admits Work/Source/evidence
  records through review. Names, candidate IDs and branch counts never affect
  canon acceptance or an episode-coverage denominator.

## Recommended bounded cleanup sequence

1. **Keep `main` the sole accepted integration state.** New work uses a short
   branch with a unique batch manifest, source receipt, explicit admission
   state, tests and a PR. Avoid creating one branch per episode or maintaining
   dozens of pre-created season pointers.
2. **Treat the 188 four-tip legacy aliases as archival routing labels.** In a
   disposable clone, inventory their names and exact SHAs, check any references
   in open PRs/automation, and preserve an immutable manifest before proposing
   removal. Do not reset or merge them to refresh their appearance.
3. **Inspect historical PR heads separately.** Use the collision-safe ref
   layout in [branch census ref isolation](BRANCH_CENSUS_REF_NAMESPACES.md).
   Reconcile distinct historical files by Source/Work identity and content
   hash; run no historical code. Where two PRs propose incompatible records,
   preserve both proposals and route them to the Auditor.
4. **Retire superseded PRs, keep traceability.** #164/#171/#172/#170 were
   closed after equivalent, tested slices merged via #175/#174/#176. Future
   supersessions should point at the accepted replacement and not claim the
   old branch is now accepted.
5. **Consider branch removal only as a separate, reviewed operation.** Exact
   target names, references, archival receipts, recovery path and affected
   workflows must be enumerated first. This census performs no deletion,
   force-push, permission edit or merge.

## Reproduce the live count safely

The branch listing is a read-only network operation:

```bash
git ls-remote --heads https://github.com/thebrazenbeard/trek-data-core.git
```

For locally repeatable comparisons and PR-head file collision analysis,
follow `docs/BRANCH_CENSUS_REF_NAMESPACES.md` to collect remote heads in a
**disposable audit clone** and run `tools/audit_git_topology.py`. That tool is
read-only and already has synthetic tests. Do not run arbitrary files from
legacy branches and do not fetch audit refs into an active collaborator's
worktree. Always pin the `main` SHA and collection date in published results;
subsequent merges or branch housekeeping will change counts.
