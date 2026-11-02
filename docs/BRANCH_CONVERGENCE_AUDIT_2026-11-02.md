# Trek Data Core branch and proposal topology audit — 2026-11-02

**Evidence:** live GitHub branch enumeration and read-only full Git-history fetch,
including available `refs/pull/*/head` objects. The snapshot base is
`main@4681b637ec9052b704283a83ec5d8d07d3fa6a79`. The companion
[`reports/branch-census-2026-11-02.json`](../reports/branch-census-2026-11-02.json)
records every enumerated branch name/head, PR-head ref, shared tree and
divergence count. SHA-256 of that snapshot:
`f2fc6f0a6a5c9daf774a8108117c19a60d26b97780b9758f744f8d98fdc4604b`.

This is a **source/topology audit**, not a claim that any historical proposal,
research record or deployment is accepted or operational.

## What the branch names conceal

| Finding | Fresh result |
| --- | ---: |
| GitHub branch names, including `main` | 190 |
| Non-`main` branches | 189 |
| Distinct non-`main` commit heads | **5** |
| Research branch names | **152, all pointing to one commit** |
| Accessible historical PR-head refs | 132 |
| Distinct file paths across those PR-head trees | 593 |
| Distinct research paths across PR-head trees | 398 |
| Paths with more than one historical blob variant | 25 |

The non-`main` branches currently group as follows:

| Exact head | Branches | Main-only / branch-only commits | Source-tree startup warning |
| --- | ---: | ---: | --- |
| `a9ebf9e4d7e1645e3d9c7be2c6766cd3b04bfc86` | 170 | 6 / 1 | Contains `folderOpen` task |
| `e710a8b7d29de8f3afe1c1b91d3ffbb8518c8761` | 12 | 6 / 1 | Contains `folderOpen` task |
| `104f0813fe29517e3b8900ad0d8e5f4dfd2bebe6` | 4 | 5 / 0 | Contains `folderOpen` task |
| `7b4782f88558b9b9c51a775d4abef159a920252c` | 2 | 6 / 1 | Contains `folderOpen` task |
| `e9f1fa806449532b52deea6ad6c6d6956becfa56` | 1 | 5 / 6 | No `folderOpen` task detected |

**Security boundary:** 188 stale branch tips contain the known editor-startup
task marker, absent from the accepted `main` remediation. Do not run those
checkouts or merge their workspace configuration. This is a source-tree
finding; it does not establish that any host is compromised or clean.

These branch aliases do **not** establish 152 independent active research
snapshots. Historical research may nevertheless remain in immutable PR
head objects and the shared commit ancestry. Branch deletion, force-push
or bulk merge would destroy useful navigation and is **not authorized** by
this report.

## Recoverable historical proposal material

Of the 398 distinct paths under `research/` across available PR-head trees,
297 have a `tng` prefix, 33 `ds9`, 21 `pro`, 18 `starfleet-academy`,
13 `short`, and smaller numbers belong to other series, literature and films.
These are **file-path counts, not episode coverage or source-admission counts**.
The complete PR-head SHA list lives in the JSON receipt.

The 25 contested paths are primarily architecture and tooling contracts.
Examples include ten variants of `.github/workflows/validate.yml`, five of
`tools/validate.py`, four of `tools/build_projection.py`, and three of
`schema/projection-manifest.schema.json`. A file chosen solely because it is
on the last-named branch can silently replace a later contract.

In particular, integrated architecture PR #82 and successor PR #153 were
merged into proposal branches, **not accepted `main`**. Their head trees are
preservation inputs for a clean convergence candidate. Use exact PR-head
blob SHAs and independent review; the similarly named live branch refs are
not reliable substitutes.

## Acceptance-ready target structure

Keep the conceptual authority layers distinct, regardless of physical folder
layout:

1. **Governance and schemas:** one accepted Source, Work, binding, Evidence,
   assertion, predicate, reconciliation and coverage contract.
2. **Admission:** validate content and references, Source↔Work binding
   eligibility, evidence scope, worker ownership and custody before allowing
   any accepted research effect.
3. **Canonical projection:** deterministic compiler, verified manifest and
   provenance, crash-safe publication, stable semantic diff.
4. **Derived consumers:** SQLite, PostgreSQL, graph/search index and web
   Explorer built only from verified canonical outputs or explicitly labelled
   development fixtures.
5. **Research staging:** immutable PR/source snapshots with per-lane
   candidate status; never backfill them as accepted corpus merely because a
   branch exists.
6. **Validation and delivery:** separate security, schema, integration,
   property/adversarial, and UI checks; reviewed clean-main convergence PR
   and exact-head readback.

### Dependency-ordered convergence path

- Pin the latest accepted `main`, preserving the source-only VS Code
  startup-security remediation and current README/hero.
- Select audited architecture files from the exact PR-head tree, create a
  new candidate branch **from current main**, and record per-file source SHA.
  Do not cherry-pick the entire old stack or import `x`, old workspace tasks,
  stale root README, or proposal research as accepted data.
- Resolve the known Work-schema mismatch (`work_type` versus `medium`) and
  enforce ACCEPTED EVIDENCE_BEARING Source↔Work binding before Evidence can
  qualify for canonical admission.
- Close coverage contract #40 gaps: derive discovery and source binding
  from authoritative roots, enforce typed scope/subjects and accepted
  revocation, and verify denominator/report receipts.
- Run full repository and synthetic adversarial tests **on the combined
  candidate**, then independent Auditor review of the exact tree.
- Accept the candidate into `main` only after the protected governance
  decision. Later decide separately whether to retire duplicate branch names;
  keep PRs, immutable heads and receipts accessible.

## Falsification ledger

| Proposition | Result | Evidence |
| --- | --- | --- |
| Each research branch currently contains distinct research state | **FAILS** | 152 research refs share `a9ebf9e4` |
| Current branch tips can be bulk-merged safely | **FAILS** | 188 tips retain `folderOpen`; five shared heads |
| All historical proposal work is recoverable | **UNKNOWN** | 132 PR heads and 593 historical paths are retrievable, but completeness of the old work is unverified |
| A green old proposal CI run qualifies current `main` | **FAILS** | Different trees and base branches; no combined acceptance test |
| Current registry validator enforces all declared nested schema constraints | **FAILS** | Mutating `source_scope` to a string yielded no validation error |

## Reproduction

Fetch only data, without checking out or executing historical branches:

```bash
git fetch origin '+refs/heads/*:refs/remotes/origin/*'
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'
python3 tools/audit_git_topology.py --repo .
```

The tool is read-only, makes no network calls itself, and emits a current
JSON census. Re-fetch and regenerate when branch refs or PR heads change.
Its snapshot must not be mistaken for current state after later GitHub
mutations. The 2026-11-02 baseline also passed 16 Librarian tests and three
workspace-startup tests, which do not resolve the falsified admission rule.

**Protected actions not performed:** no branch deletion, force push, release,
merge, governance acceptance, corpus admission or hosting configuration.
