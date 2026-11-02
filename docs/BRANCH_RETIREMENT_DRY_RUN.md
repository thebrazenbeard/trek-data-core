# Branch retirement dry-run: exact refs, recovery and review gates

**Status: inventory only. No branch retirement is approved by this tool.**

`docs/BRANCH_CONSOLIDATION_2026-11-02.md` records a historical point-in-time
branch census. Several old branch names share commit hashes, but a duplicate
commit does not make the **name** disposable: an open PR, a contributor, an
issue, an automation or a documentation link could still depend on it.
Neither the historical branch count nor an old PR-head census should be
quoted as the current population without collecting fresh refs.

`tools/plan_branch_retirement.py` converts a **fresh** collision-safe v2
local audit census to a deterministic, named, review-only retirement plan.
It reads JSON and optionally performs read-only `git ls-tree` lookups. It
cannot perform a fetch, branch deletion, reset, force-update, push, merge or
deployment. Its output authorizes **zero** retirement actions.

## Collect a snapshot without altering a working checkout

Use a **disposable audit clone**. The two fetches below are deliberately
separate from day-to-day working repositories because they do change *local*
refs in that disposable clone. Consult
[`BRANCH_CENSUS_REF_NAMESPACES.md`](BRANCH_CENSUS_REF_NAMESPACES.md) for the
full ref-isolation rationale.

```bash
# Run these two fetches with the disposable audit clone as the working directory.
git fetch origin '+refs/heads/*:refs/trek-audit/branch-heads/*'
git fetch origin '+refs/pull/*/head:refs/trek-audit/pr-heads/*'

# Run the scripts from this repository's accepted main source tree.
python3 tools/audit_git_topology.py \
  --repo /path/to/disposable-audit-clone > /tmp/trek-branch-census.json
python3 tools/plan_branch_retirement.py \
  --census /tmp/trek-branch-census.json \
  --audit-repo /path/to/disposable-audit-clone > /tmp/trek-branch-holds.json
```

An offline plan can also be built from a previously saved v2 census without
the `--audit-repo` option. In that case, tree identity is explicitly
`NOT_VERIFIED`, tree path inspection stays `NOT_INSPECTED`, and no hazard is
implicitly cleared. With `--audit-repo`, the planner resolves each commit's
actual tree without lazy fetching, compares it with the census's claimed
`tree_sha`, and rejects a mismatched claim before inspecting its paths.
Missing local objects remain `OBJECT_UNAVAILABLE` / `NOT_VERIFIED`, not
successful inspection. The planner refuses legacy v1 censuses whose
`origin/pr/*` names may collide with real branch
names. It rejects malformed, inconsistent, duplicate, symlinked and oversized
census input, overlong PR numbers, invisible/spoofing branch characters and
excessively nested JSON rather than quietly issuing partial retirement
instructions.

For deterministic results, archive the census input alongside the output,
note the UTC collection time and the `basis.accepted_main_sha_at_census`, and
record the plan's `basis.branch_snapshot_sha256`. Re-running the planner on
the *same input and local object evidence* produces identical output.
The hash covers every exact `refs/heads/<name> → SHA` pair **including main**;
it is a snapshot integrity marker, not proof that live GitHub refs have not
moved since the snapshot.

## Read the result correctly

| Output | Meaning |
| --- | --- |
| `groups[].tip_sha`, `tree_sha`, `branch_names` | Commit and *census-claimed* tree grouping; branch names remain distinct. The tree claim is not automatically attested. |
| `groups[].tree_identity_verification` | `VERIFIED` only when the local commit's actual tree ID matches the claimed `tree_sha`; otherwise `NOT_VERIFIED` or plan rejection on mismatch. |
| `groups[].historical_path_inspection`, `recoverability` | Whether Git paths were inspected after tree verification; independent archive, remote retention and restore test remain **unverified**. |
| `groups[].source_risk_flags` | Known historical legacy tip and `.vscode/tasks.json` / `public/fonts/` path signals. Do not execute any old content. |
| `groups[].matching_pr_snapshot_numbers_not_open_pr_status` | Historical PR-head objects with the **same SHA**, not current open-PR status or branch ownership. |
| `branch_holds[].ref` and `.recovery_receipt` | One named immutable receipt per candidate branch, preserving the exact original ref and target SHA. |
| `branch_holds[].retirement_decision` | Always `HOLD_PER_REF_REVIEW`. Even duplicate-tip aliases are not marked safe to delete. |
| `summary.retirement_actions_authorized` | Always `0`. |

PR heads are read from `refs/trek-audit/pr-heads/<number>` and branches from
`refs/trek-audit/branch-heads/<name>`; they are never merged into the same
namespace. For example, a real branch `refs/heads/pr/82` is **not** PR #82.

The following historical heads require extra care because old `.vscode`
editor-startup task and `public/fonts` artifacts were observed in prior
comparisons. The tool recognizes the exact documented legacy SHA group and
uses read-only path inspection for fresh heads, but the presence of a path
alone does not prove active executable behavior. Treat this as a triage
signal; never run scripts, tasks, hooks or binaries from old trees.

## Exact-name retirement gate (not automated)

No branch name should be proposed for deletion unless **all** of the
following have been performed for that **exact ref**, on a new fresh snapshot:

1. **Reference and owner review:** inventory current open PR bases/heads,
   issues, CI workflow triggers, automation, links, collaborators and owner
   commitments. Record a reviewer and timestamp. A shared commit tree is
   insufficient to pass this gate.
2. **Evidence and safety review:** compare the branch-only commits against
   accepted `main` as *data*, confirm research or rights evidence is not
   unique and unreviewed, and inspect historical editor-task/font paths
   without executing historical code. Superseded PR notes point to follow-up
   acceptance, but do not independently prove a branch has no unique value.
3. **Independent archive:** create a protected immutable receipt or Git bundle
   that includes the commit history, exact ref-to-SHA mapping, date and
   verification hash; confirm the archive remains available independently of
   the candidate ref. Do not rely on unspecified GitHub garbage-collection
   retention. Protect the archive from accidental public disclosure if it
   contains unreviewed/private or infringing source bytes.
4. **Recovery rehearsal:** on a disposable repository, prove the archived
   object can be inspected and that the exact name **could** be restored to
   its original SHA under the repository's then-current branch permissions.
   Record the recovery instructions and outcome. No restore test should
   force-update a live remote ref.
5. **Fresh signoff:** check the ref name and SHA again immediately before a
   separately authorized, reviewed change. If either moved or a dependency
   was discovered, stop and repeat the review. Changes to branch permissions,
   remote deletion and pruning are explicitly **outside this planner**.

**Safe next action:** collect a fresh namespaced census in a disposable clone,
save the resulting hold manifest, then hand the highest-multiplicity legacy
tip group to a reviewer for **per-name dependency and recoverability checks**.
Until those checks have individual receipts, the list of names that can be
certified safe for pruning is **empty**. That is a review status, not an
assertion that none will ever be removable.
