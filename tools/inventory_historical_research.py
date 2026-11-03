#!/usr/bin/env python3
"""Inventory historical research proposals without running or admitting them.

Only pre-collected, collision-safe ``refs/trek-audit/pr-heads/<number>`` are
read. Collect them in a disposable audit clone as documented in
``docs/BRANCH_CENSUS_REF_NAMESPACES.md``. This command never fetches, checks
out, modifies refs, reads historical file contents, or executes their code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


PR_REF_ROOT = "refs/trek-audit/pr-heads/"
OID = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
PR_NUMBER = re.compile(r"[1-9][0-9]*\Z")
MAX_PR_REFS = 500
MAX_RESEARCH_ENTRIES = 250_000


class InventoryError(ValueError):
    """Unsafe or unreproducible snapshot input."""


def git_read(repo: Path, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=60,
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0"},
    )
    if proc.returncode:
        raise InventoryError(
            f"read-only git {args[0]} failed: {proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    return proc.stdout


def parse_refs(raw: bytes) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for line in raw.splitlines():
        try:
            ref, oid = line.decode("ascii").split("\t", 1)
        except (UnicodeError, ValueError) as exc:
            raise InventoryError("invalid Git ref listing") from exc
        if not ref.startswith(PR_REF_ROOT):
            raise InventoryError("ref listing contains an unexpected namespace")
        number = ref[len(PR_REF_ROOT) :]
        if not PR_NUMBER.fullmatch(number) or not OID.fullmatch(oid):
            raise InventoryError("PR ref name or object ID is invalid")
        refs.append((number, oid))
    if not refs:
        raise InventoryError("no isolated PR-head refs; collect an audit snapshot first")
    if len(refs) > MAX_PR_REFS or len({n for n, _ in refs}) != len(refs):
        raise InventoryError("PR ref count exceeds limit or contains duplicate numbers")
    return sorted(refs, key=lambda item: int(item[0]))


def parse_research_tree(raw: bytes) -> list[tuple[str, str, str, str]]:
    """Return (path, mode, type, object_id) from Git's NUL-delimited tree.

    Paths are decoded strictly. A proposed invalid path fails the entire
    inventory; unsafe objects are reported with their modes, not followed.
    """
    records: list[tuple[str, str, str, str]] = []
    for entry in raw.split(b"\x00"):
        if not entry:
            continue
        try:
            header, path_bytes = entry.split(b"\t", 1)
            mode, object_type, oid = header.decode("ascii").split(" ", 2)
            path = path_bytes.decode("utf-8")
        except (UnicodeError, ValueError) as exc:
            raise InventoryError("malformed tree entry or non-UTF-8 path") from exc
        if not path.startswith("research/"):
            continue
        components = path.split("/")
        if (
            any(p in ("", ".", "..") for p in components)
            or not re.fullmatch(r"[0-7]{6}", mode)
            or object_type not in ("blob", "commit")
            or not OID.fullmatch(oid)
        ):
            raise InventoryError("invalid historical research tree entry")
        # Historical heads include the root research/README.md, which describes
        # the research partition but is not itself a lane's evidence artifact.
        # Ignore *only* this exact regular documentation file; unsafe modes or
        # other top-level paths must still fail closed.
        if path == "research/README.md":
            if (mode, object_type) != ("100644", "blob"):
                raise InventoryError("unsafe historical root research README")
            continue
        if len(components) < 3:
            raise InventoryError("invalid historical research tree entry")
        records.append((path, mode, object_type, oid))
        if len(records) > MAX_RESEARCH_ENTRIES:
            raise InventoryError("historical research tree exceeds bounded entry limit")
    return records


def inventory(
    expected_main_sha: str,
    main_tree: bytes,
    pr_snapshots: list[tuple[str, str, bytes]],
) -> dict:
    if not OID.fullmatch(expected_main_sha):
        raise InventoryError("expected main SHA must be a full Git object ID")
    pr_snapshots = sorted(pr_snapshots, key=lambda item: int(item[0]))
    accepted_main = {path: (mode, kind, sha) for path, mode, kind, sha in parse_research_tree(main_tree)}
    variants: dict[str, dict[tuple[str, str, str], set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    total_entries = 0
    for number, head_sha, tree in pr_snapshots:
        if not PR_NUMBER.fullmatch(number) or not OID.fullmatch(head_sha):
            raise InventoryError("invalid pinned PR-head snapshot")
        for path, mode, kind, sha in parse_research_tree(tree):
            variants[path][(mode, kind, sha)].add(number)
            total_entries += 1
            if total_entries > MAX_RESEARCH_ENTRIES:
                raise InventoryError("combined historical entries exceed bounded limit")
    paths = []
    for path, groups in sorted(variants.items()):
        proposals = []
        for (mode, kind, sha), prs in sorted(groups.items()):
            proposals.append(
                {
                    "git_object_id": sha,
                    "git_mode": mode,
                    "git_type": kind,
                    "pr_heads": sorted(prs, key=int),
                    "same_bytes_on_main": accepted_main.get(path) == (mode, kind, sha),
                    "unsafe_object_mode": kind != "blob" or mode != "100644",
                }
            )
        paths.append(
            {
                "path": path,
                "has_conflicting_versions": len(proposals) > 1,
                "identity_review": "NOT_PERFORMED",
                "admission": "NONE",
                "versions": proposals,
            }
        )
    report = {
        "schema_version": "trek-historical-research-inventory-v1",
        "expected_main_sha": expected_main_sha,
        "pr_head_refs": [
            {"number": n, "sha": sha} for n, sha, _tree in pr_snapshots
        ],
        "summary": {
            "pr_head_refs": len(pr_snapshots),
            "research_paths": len(paths),
            "contested_paths": sum(p["has_conflicting_versions"] for p in paths),
            "unique_path_object_variants": sum(len(p["versions"]) for p in paths),
            "unsafe_object_variants": sum(
                v["unsafe_object_mode"] for p in paths for v in p["versions"]
            ),
        },
        "data_status": "UNTRUSTED_HISTORICAL_PROPOSALS",
        "admission_effect": "NONE",
        "acceptance_effect": "NONE",
        "coverage_effect": "NONE",
        "denominator_effect": "NONE",
        "paths": paths,
    }
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    report["manifest_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return report


def collect(repo: Path, expected_main_sha: str) -> dict:
    actual_main = git_read(repo, "rev-parse", "--verify", "main^{commit}").decode("ascii").strip()
    if actual_main != expected_main_sha:
        raise InventoryError(f"main moved: expected {expected_main_sha}; actual {actual_main}")
    refs = parse_refs(
        git_read(repo, "for-each-ref", "--format=%(refname)%09%(objectname)", PR_REF_ROOT[:-1])
    )
    main_tree = git_read(repo, "ls-tree", "-r", "-z", "--full-tree", expected_main_sha)
    snapshots = [
        (number, sha, git_read(repo, "ls-tree", "-r", "-z", "--full-tree", sha))
        for number, sha in refs
    ]
    return inventory(expected_main_sha, main_tree, snapshots)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Disposable audit clone")
    parser.add_argument("--expected-main-sha", required=True, help="Pin the exact accepted main commit")
    args = parser.parse_args()
    try:
        report = collect(args.repo.resolve(), args.expected_main_sha)
    except (InventoryError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"HISTORICAL_RESEARCH_INVENTORY_REJECTED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
