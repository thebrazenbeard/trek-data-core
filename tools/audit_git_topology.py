#!/usr/bin/env python3
"""Read-only, reproducible census of local Git branch and PR-head refs.

Fetch remote refs before running; this tool never fetches, checks out, or mutates
the repository. Historical objects are inspected as data, never executed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def git(repo: Path, *args: str, allow_missing: bool = False) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
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
        if not name.startswith(prefix) or name == "origin/HEAD":
            continue
        refs.append((name[len(prefix) :], sha))
    return sorted(refs)


def has_folder_open_task(contents: str | None) -> bool:
    return contents is not None and "folderOpen" in contents


def parse_blob_tree(raw: str) -> list[tuple[str, str]]:
    result = []
    for line in raw.splitlines():
        match = re.fullmatch(r"[0-7]{6} blob ([0-9a-f]{40})\t(.+)", line)
        if match:
            result.append((match.group(2), match.group(1)))
    return result


def census(repo: Path, base_ref: str = "refs/remotes/origin/main") -> dict:
    base_sha = git(repo, "rev-parse", "--verify", base_ref + "^{commit}")
    branch_raw = git(
        repo,
        "for-each-ref",
        "--format=%(refname:short)%09%(objectname)",
        "refs/remotes/origin",
    )
    # PR-head snapshots live beneath origin/pr/ in this audit clone, but are
    # not actual GitHub branch refs. Count them only in the separate PR ledger.
    branches = [
        (name, sha)
        for name, sha in parse_ref_lines(branch_raw or "", "origin/")
        if not name.startswith("pr/")
    ]
    if not any(name == "main" for name, _ in branches):
        raise RuntimeError("origin/main is missing; fetch branch refs first")

    pr_raw = git(
        repo,
        "for-each-ref",
        "--format=%(refname:short)%09%(objectname)",
        "refs/remotes/origin/pr",
    )
    pr_refs = parse_ref_lines(pr_raw or "", "origin/pr/")
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
    return {
        "schema_version": "trek-branch-census-v1",
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--base-ref", default="refs/remotes/origin/main")
    args = parser.parse_args()
    result = census(args.repo.resolve(), args.base_ref)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
