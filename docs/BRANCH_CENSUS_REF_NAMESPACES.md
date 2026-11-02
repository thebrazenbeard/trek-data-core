# Branch census ref isolation

The original 2026-11-02 branch-census snapshot was pinned from a clone that
fetched both genuine branches and synthetic pull-request heads into the
`refs/remotes/origin/` namespace. A legitimate branch named `pr/82` could
collide with PR-head snapshot #82, so that layout cannot distinguish both
populations reliably. The historic report was valid for its inspected refs;
this is a future-collection robustness fix, **not a retroactive assertion of
incorrect historical counts**.

For future censuses, create a dedicated **disposable audit clone**, fetch the
two populations into disjoint Git ref namespaces, and run the read-only tool:

```bash
git fetch origin '+refs/heads/*:refs/trek-audit/branch-heads/*'
git fetch origin '+refs/pull/*/head:refs/trek-audit/pr-heads/*'
python3 tools/audit_git_topology.py --repo /path/to/disposable-audit-clone > branch-census.json
```

The two refspecs can represent both the genuine branch `pr/82` and the PR
head #82 without collision. The tool itself never runs fetch, checkout, a
hook, a historical script, or any executable file from a historical branch.
Ref snapshots should be captured only in a disposable clone because `git
fetch` *does* update that clone's refs. Do not run these fetches against an
unexamined or dirty working repository.

The CLI defaults to the new disjoint layout and emits schema version
`trek-branch-census-v2` with its ref roots named in the report. It fails if
the selected mainline ref is absent; it does not silently switch to the old
namespace.

To re-read the original 2026-11-02 clone without altering its refs, use:

```bash
python3 tools/audit_git_topology.py --repo /path/to/original-audit-clone --legacy-ref-layout
```

Legacy mode retains the old `trek-branch-census-v1` output shape and the
historical `origin/pr/` filtering behavior. It is for comparison only; it is
not collision-safe. If `origin/main` has advanced, divergence counts will
change even when the five non-main head groups and PR-head path counts remain
stable. To compare historical divergence, supply the original base commit
SHA explicitly via `--base-ref`, and note that the `base_ref` label then
differs from the original snapshot. Never claim a byte-identical replay of
the original report solely from current refs.

This change is bounded to ref collection and classification. It does not
change research admission, branch protections, repository permissions or
merge/delete policies.
