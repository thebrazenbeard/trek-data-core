#!/usr/bin/env python3
"""Read-only, reproducible census of local Git branch and PR-head refs.

Fetch branch and pull-request refs into disjoint namespaces before running;
this tool never fetches, checks out, or mutates the repository. Historical
objects are inspected as data, never executed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


AUDIT_BRANCH_ROOT = "refs/trek-audit/branch-heads"
AUDIT_PR_ROOT = "refs/trek-audit/pr-heads"
LEGACY_BRANCH_ROOT = "refs/remotes/origin"
LEGACY_PR_ROOT = "refs/remotes/origin/pr"


def git(repo: Path, *args: str, allow_missing: bool = False) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
        timeout=30,
    )
    if proc.returncode:
        if allow_missing:
            return None
        raise RuntimeError(f"git {args[0]} failed: {proc.stderr.strip()}")
    return proc.stdout.rstrip("\n")


def parse_ref_lines(raw: str, prefix: str) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if not line:
            continue
        name, sha = line.split("\t", 1)
        if not name.startswith(prefix) or name == prefix + "HEAD":
            continue
        refs.append((name[len(prefix) :], sha))
    return sorted(refs)


def parse_pr_snapshots(raw: str, prefix: str) -> list[tuple[str, str]]:
    refs = parse_ref_lines(raw, prefix)
    invalid = [name for name, _ in refs if not re.fullmatch(r"[1-9][0-9]*", name)]
    if invalid:
        raise ValueError(f"PR-head snapshot names must be numeric: {invalid}")
    return refs


def ref_layout(legacy_ref_layout: bool) -> tuple[str, str, str]:
    if legacy_ref_layout:
        return (LEGACY_BRANCH_ROOT, LEGACY_PR_ROOT, LEGACY_BRANCH_ROOT + "/main")
    return (AUDIT_BRANCH_ROOT, AUDIT_PR_ROOT, AUDIT_BRANCH_ROOT + "/main")


def has_folder_open_task(contents: str | None) -> bool:
    return contents is not None and "folderOpen" in contents


def parse_blob_tree(raw: str) -> list[tuple[str, str]]:
    result = []
    for line in raw.splitlines():
        match = re.fullmatch(r"[0-7]{6} blob ([0-9a-f]{40})\t(.+)", line)
        if match:
            result.append((match.group(2), match.group(1)))
    return result


def census(repo: Path, base_ref: str | None = None, *, legacy_ref_layout: bool = False) -> dict:
    branch_root, pr_root, default_base = ref_layout(legacy_ref_layout)
    base_ref = base_ref or default_base
    base_sha = git(repo, "rev-parse", "--verify", base_ref + "^{commit}")
    branch_raw = git(
        repo,
        "for-each-ref",
        "--format=%(refname)%09%(objectname)",
        branch_root,
    )
    # The default branch and PR roots are disjoint: a legitimate branch named
    # pr/82 cannot be mistaken for synthetic pull request #82. The legacy root
    # is supported only to reproduce the pinned PR #156 snapshot, where those
    # two populations were indistinguishable by name alone.
    branches = [
        (name, sha)
        for name, sha in parse_ref_lines(branch_raw or "", branch_root + "/")
        if not legacy_ref_layout or not name.startswith("pr/")
    ]
    if not any(name == "main" for name, _ in branches):
        raise RuntimeError(f"{branch_root}/main is missing; fetch the selected branch-ref layout first")

    pr_raw = git(
        repo,
        "for-each-ref",
        "--format=%(refname)%09%(objectname)",
        pr_root,
    )
    pr_refs = parse_pr_snapshots(pr_raw or "", pr_root + "/")
    head_members: dict[str, list[str]] = defaultdict(list)
    for name, sha in branches:
        if name != "main":
            head_members[sha].append(name)

    heads = []
    for sha, names in sorted(
        head_members.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        counts = git(repo, "rev-list", "--left-right", "--count", f"{base_sha}...{sha}")
        main_only, branch_only = (int(n) for n in (counts or "").split())
        task = git(repo, "show", f"{sha}:.vscode/tasks.json", allow_missing=True)
        heads.append(
            {
                "sha": sha,
                "tree_sha": git(repo, "rev-parse", sha + "^{tree}"),
                "branch_count": len(names),
                "main_only_commits": main_only,
                "branch_only_commits": branch_only,
                "contains_folder_open_task": has_folder_open_task(task),
                "branches": sorted(names),
            }
        )

    by_family = Counter(name.split("/")[0] for name, _ in branches if name != "main")
    historical_paths: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for pr_number, sha in pr_refs:
        tree = git(repo, "ls-tree", "-r", sha) or ""
        for path, blob_sha in parse_blob_tree(tree):
            historical_paths[path][blob_sha].append(pr_number)
    contested_paths = {
        path: [
            {"blob_sha": blob_sha, "pr_heads": sorted(numbers, key=int)}
            for blob_sha, numbers in sorted(variants.items())
        ]
        for path, variants in sorted(historical_paths.items())
        if len(variants) > 1
    }
    research_lanes = Counter(
        path.split("/")[1]
        for path in historical_paths
        if path.startswith("research/") and len(path.split("/")) > 1
    )
    report = {
        "schema_version": "trek-branch-census-v1" if legacy_ref_layout else "trek-branch-census-v2",
        "base_ref": base_ref,
        "base_sha": base_sha,
        "summary": {
            "total_branches_including_main": len(branches),
            "non_main_branches": len(branches) - 1,
            "distinct_non_main_heads": len(heads),
            "accessible_pr_head_refs": len(pr_refs),
            "distinct_historical_pr_paths": len(historical_paths),
            "contested_historical_pr_paths": len(contested_paths),
            "research_paths_in_pr_heads": sum(
                path.startswith("research/") for path in historical_paths
            ),
            "by_family": dict(sorted(by_family.items())),
            "historical_research_paths_by_lane": dict(sorted(research_lanes.items())),
        },
        "head_groups": heads,
        "pr_head_refs": [{"number": name, "sha": sha} for name, sha in pr_refs],
        "contested_historical_pr_paths": contested_paths,
    }
    if not legacy_ref_layout:
        report["ref_layout"] = {"branch_root": branch_root, "pr_head_root": pr_root}
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--base-ref", help="Override the selected layout's mainline comparison ref")
    parser.add_argument("--legacy-ref-layout", action="store_true", help="Reproduce pinned PR #156 using the old, potentially colliding origin/pr namespace")
    args = parser.parse_args()
    result = census(args.repo.resolve(), args.base_ref, legacy_ref_layout=args.legacy_ref_layout)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
