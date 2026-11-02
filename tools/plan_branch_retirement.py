#!/usr/bin/env python3
"""Produce a read-only branch-retirement *review plan* from an offline census.

This deliberately has no GitHub API, network, branch-edit, delete, fetch,
checkout, or output-file operation. Its output is an inventory and hold ledger,
not authorization to prune a single ref. Historical Git objects are data only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import unicodedata
from pathlib import Path


MAX_CENSUS_BYTES = 8 * 1024 * 1024
MAX_JSON_NESTING = 256
MAX_PR_NUMBER_DIGITS = 20
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
PR_NUMBER = re.compile(r"[1-9][0-9]*\Z")
BIDI_RIGHT_TO_LEFT = frozenset({"R", "AL", "AN", "RLE", "RLO", "LRE", "LRO",
                                "PDF", "RLI", "LRI", "FSI", "PDI", "BN"})
BRANCH_ROOT = "refs/trek-audit/branch-heads"
PR_ROOT = "refs/trek-audit/pr-heads"
KNOWN_LEGACY_TIPS = frozenset({
    "a9ebf9e4d7e1645e3d9c7be2c6766cd3b04bfc86",
    "e710a8b7d29de8f3afe1c1b91d3ffbb8518c8761",
    "104f0813fe29517e3b8900ad0d8e5f4dfd2bebe6",
    "7b4782f88558b9b9c51a775d4abef159a920252c",
    "e9f1fa806449532b52deea6ad6c6d6956becfa56",
})
SUPERSEDED_TIP_NOTES = {
    "b546c1a69ff8fb0c1602425bf1a8b11664de98ae": "Old Explorer branch; reviewed replacement PR #175",
    "10959de4ffae19de56719990630547ec794b2f97": "Old Research Leads branch; reviewed replacement PR #175",
    "0b12f1e427d004e7968d161b411501441ab31f7e": "Old Pages fifth-asset branch; reviewed replacement PR #174",
    "1f158011e93919e2bed6b29edc3a9b935ff41556": "Old TNG publisher pilot; reviewed replacement PR #176",
}
PER_REF_CHECKS = [
    "Verify this exact branch name is not referenced by an open PR, issue, automation, documentation or collaborator workflow.",
    "Record an immutable branch-name-to-commit receipt and independently verify object recoverability.",
    "Check whether branch-only content contains unmerged evidence or historical unsafe startup artifacts; do not run old code.",
    "Obtain separately recorded human authority for this exact ref and an explicit recovery procedure before deletion.",
]


class Rejected(ValueError):
    """Unsafe, incomplete or internally inconsistent offline census."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Rejected(message)


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for name, value in pairs:
        require(name not in result, f"duplicate JSON key: {name}")
        result[name] = value
    return result


def reject_non_json_constant(value: str) -> object:
    raise Rejected(f"non-JSON numeric constant: {value}")


def reject_excess_nesting(raw: bytes) -> None:
    """Bound JSON nesting before parsing, ignoring delimiters inside strings.

    Some JSON decoders accept very deep arrays without RecursionError. Both
    forms must be rejected before they can exhaust resources downstream.
    Syntax validation (including escape validity) remains json.loads' job.
    """
    depth = 0
    quoted = False
    escaped = False
    for byte in raw:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 0x5C:  # backslash
                escaped = True
            elif byte == 0x22:  # quote
                quoted = False
        elif byte == 0x22:
            quoted = True
        elif byte in (0x5B, 0x7B):  # [ {
            depth += 1
            require(depth <= MAX_JSON_NESTING, "census input JSON nesting exceeds safe limit")
        elif byte in (0x5D, 0x7D):  # ] }
            depth -= 1


def read_json(path: Path) -> dict:
    require(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_NONBLOCK"),
            "safe input flags unavailable")
    try:
        before = path.lstat()
        require(stat.S_ISREG(before.st_mode), "census input must be regular non-symlink file")
        require(before.st_size <= MAX_CENSUS_BYTES, "census input exceeds byte limit")
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as stream:
            opened = os.fstat(stream.fileno())
            require(stat.S_ISREG(opened.st_mode)
                    and (opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino),
                    "census input changed during open")
            require(opened.st_size <= MAX_CENSUS_BYTES, "census input exceeds byte limit")
            raw = stream.read(MAX_CENSUS_BYTES + 1)
    except OSError as exc:
        raise Rejected(f"cannot safely read census input: {exc.strerror}") from exc
    require(len(raw) <= MAX_CENSUS_BYTES, "census input exceeds byte limit")
    reject_excess_nesting(raw)
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
                            parse_constant=reject_non_json_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Rejected("census input is not strict UTF-8 JSON") from exc
    except RecursionError as exc:
        raise Rejected("census input JSON nesting exceeds safe limit") from exc
    require(isinstance(result, dict), "census root must be an object")
    return result


def valid_sha(value: object) -> bool:
    return isinstance(value, str) and bool(SHA40.fullmatch(value))


def valid_branch(name: object) -> bool:
    if not isinstance(name, str) or not name or name == "@" or len(name) > 500:
        return False
    if (name.startswith(("/", ".", "-")) or name.endswith(("/", "."))
            or "//" in name or ".." in name or "@{" in name):
        return False
    if any(ch in "~^:?*[\\" or unicodedata.category(ch)[0] in ("C", "Z")
           or unicodedata.bidirectional(ch) in BIDI_RIGHT_TO_LEFT for ch in name):
        return False
    return all(part not in ("", ".", "..") and not part.startswith(".")
               and not part.endswith(".lock") for part in name.split("/"))


def exact_keys(obj: object, required: set[str], name: str) -> dict:
    require(isinstance(obj, dict) and required <= obj.keys(), f"{name} lacks required fields")
    return obj


def census_groups(census: dict) -> tuple[list[dict], list[dict]]:
    require(census.get("schema_version") == "trek-branch-census-v2",
            "only collision-safe branch census v2 is supported")
    layout = exact_keys(census.get("ref_layout"), {"branch_root", "pr_head_root"}, "ref layout")
    require(layout["branch_root"] == BRANCH_ROOT and layout["pr_head_root"] == PR_ROOT,
            "branch and PR snapshots must use the disjoint audit namespaces")
    require(valid_sha(census.get("base_sha")), "accepted main SHA missing/invalid")
    require(census.get("base_ref") == BRANCH_ROOT + "/main", "main base ref is unexpected")
    summary = exact_keys(census.get("summary"),
                         {"non_main_branches", "total_branches_including_main",
                          "distinct_non_main_heads", "accessible_pr_head_refs"}, "summary")
    heads = census.get("head_groups")
    prs = census.get("pr_head_refs")
    require(isinstance(heads, list) and isinstance(prs, list), "branch/PR lists missing")
    require(len(heads) <= 100_000 and len(prs) <= 100_000, "too many branch/PR groups")
    seen_refs: set[str] = set()
    seen_tips: set[str] = set()
    groups = []
    for index, group in enumerate(heads):
        exact_keys(group, {"sha", "tree_sha", "branch_count", "branches",
                           "contains_folder_open_task", "main_only_commits",
                           "branch_only_commits"}, f"head_groups[{index}]")
        sha = group["sha"]
        require(valid_sha(sha) and valid_sha(group["tree_sha"]), "invalid branch tip/tree SHA")
        require(sha not in seen_tips, "one tip SHA appears in multiple groups")
        seen_tips.add(sha)
        names = group["branches"]
        require(isinstance(names, list) and names, "branch group must be nonempty")
        require(type(group["branch_count"]) is int and group["branch_count"] == len(names),
                "branch count disagrees with group names")
        require(type(group["contains_folder_open_task"]) is bool, "invalid editor task signal")
        for key in ("main_only_commits", "branch_only_commits"):
            require(type(group[key]) is int and group[key] >= 0, "invalid divergence count")
        for name in names:
            require(valid_branch(name) and name != "main", "unsafe or reserved branch name")
            require(name not in seen_refs, "same branch name appears in multiple groups")
            seen_refs.add(name)
        groups.append({
            "sha": sha, "tree_sha": group["tree_sha"], "branches": sorted(names),
            "contains_folder_open_task": group["contains_folder_open_task"],
            "main_only_commits": group["main_only_commits"],
            "branch_only_commits": group["branch_only_commits"],
        })
    require(type(summary["non_main_branches"]) is int
            and summary["non_main_branches"] == len(seen_refs)
            and type(summary["total_branches_including_main"]) is int
            and summary["total_branches_including_main"] == len(seen_refs) + 1
            and type(summary["distinct_non_main_heads"]) is int
            and summary["distinct_non_main_heads"] == len(groups),
            "census summary does not match exact branch names and tip groups")

    seen_prs = set()
    pr_refs = []
    for entry in prs:
        exact_keys(entry, {"number", "sha"}, "PR snapshot")
        number, sha = entry["number"], entry["sha"]
        require(isinstance(number, str) and len(number) <= MAX_PR_NUMBER_DIGITS
                and PR_NUMBER.fullmatch(number) and valid_sha(sha),
                "malformed PR head ref")
        require(number not in seen_prs, "duplicate PR head number")
        seen_prs.add(number)
        pr_refs.append({"number": number, "sha": sha})
    require(type(summary["accessible_pr_head_refs"]) is int
            and summary["accessible_pr_head_refs"] == len(pr_refs),
            "PR head snapshot count mismatch")
    return groups, pr_refs


def inspect_tree(repo: Path | None, sha: str, claimed_tree_sha: str) -> dict:
    if repo is None:
        return {"status": "NOT_INSPECTED", "tree_identity": "NOT_VERIFIED",
                "paths": [], "editor_task_contains_folder_open": None}
    unavailable = {"status": "OBJECT_UNAVAILABLE", "tree_identity": "NOT_VERIFIED",
                   "paths": [], "editor_task_contains_folder_open": None}
    # A census can claim any syntactically valid tree ID. Verify the commit's
    # actual tree before treating path inspection as evidence about that claim.
    # Do not resolve refs, replace objects, fetch, or touch working tree files.
    env = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0",
           "GIT_NO_REPLACE_OBJECTS": "1"}
    try:
        actual = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", "--end-of-options",
             sha + "^{tree}"],
            capture_output=True, timeout=20, check=False, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return unavailable
    if actual.returncode or len(actual.stdout) > 128:
        return unavailable
    actual_tree_sha = actual.stdout.rstrip(b"\n").decode("ascii", errors="replace")
    if not valid_sha(actual_tree_sha):
        return unavailable
    require(actual_tree_sha == claimed_tree_sha,
            f"census tree SHA mismatch for branch tip {sha}")
    # NUL separators preserve literal tabs, newlines and Git's quoted-path
    # settings. Inspect commits as immutable object IDs, never as ref names.
    command = ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", "-z", sha]
    try:
        proc = subprocess.run(command, capture_output=True,
                              timeout=20, check=False, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return {**unavailable, "tree_identity": "VERIFIED"}
    if proc.returncode or len(proc.stdout) > 2_000_000 or (proc.stdout and not proc.stdout.endswith(b"\0")):
        return {**unavailable, "tree_identity": "VERIFIED"}
    # Git paths are byte strings. Exact ASCII security-relevant paths compare
    # correctly without inventing a lossy Unicode interpretation.
    paths = proc.stdout.split(b"\0") if proc.stdout else []
    hazards = []
    if b".vscode/tasks.json" in paths:
        hazards.append(".vscode/tasks.json")
    if any(p == b"public/fonts" or p.startswith(b"public/fonts/") for p in paths):
        hazards.append("public/fonts/")
    # Source-only. The accepted census has already recorded a folderOpen
    # signal. Do not execute or interpret historical task commands here.
    return {"status": "PATHS_INSPECTED", "tree_identity": "VERIFIED", "paths": sorted(hazards),
            "editor_task_contains_folder_open": None}


def plan(census: dict, *, audit_repo: Path | None = None) -> dict:
    groups, prs = census_groups(census)
    pr_by_sha: dict[str, list[str]] = {}
    for p in prs:
        pr_by_sha.setdefault(p["sha"], []).append(p["number"])
    main_sha = census["base_sha"]
    exact_refs = {"refs/heads/main": main_sha}
    output_groups = []
    output_refs = []
    for group in sorted(groups, key=lambda g: (-len(g["branches"]), g["sha"])):
        sha = group["sha"]
        names = group["branches"]
        source_flags = []
        if sha in KNOWN_LEGACY_TIPS:
            source_flags.append("PINNED_LEGACY_TIP_REVIEW")
        if group["contains_folder_open_task"]:
            source_flags.append("HISTORICAL_FOLDER_OPEN_TASK")
        tree = inspect_tree(audit_repo, sha, group["tree_sha"])
        if ".vscode/tasks.json" in tree["paths"]:
            source_flags.append("EDITOR_TASK_PATH_PRESENT")
        if "public/fonts/" in tree["paths"]:
            source_flags.append("HISTORICAL_PUBLIC_FONTS_PATH")
        if tree["status"] != "PATHS_INSPECTED":
            source_flags.append("OBJECT_PATH_INSPECTION_NOT_PROVEN")
        classification = ("HISTORICAL_HAZARD_HOLD" if any(
            flag != "OBJECT_PATH_INSPECTION_NOT_PROVEN" for flag in source_flags)
            else "DUPLICATE_TIP_REVIEW" if len(names) > 1 else "UNIQUE_TIP_RETAIN")
        output_groups.append({
            "tip_sha": sha, "tree_sha": group["tree_sha"], "branch_count": len(names),
            "branch_names": names, "classification": classification,
            "historical_path_inspection": tree["status"],
            "tree_identity_verification": tree["tree_identity"],
            "recoverability": {
                "tree_read_from_local_audit_objects": tree["status"] == "PATHS_INSPECTED",
                "independent_bundle_or_immutable_archive": "NOT_VERIFIED",
                "remote_commit_retention_after_ref_deletion": "NOT_VERIFIED",
                "restore_procedure_tested": False,
            },
            "source_risk_flags": sorted(source_flags),
            "matching_pr_snapshot_numbers_not_open_pr_status":
                sorted(pr_by_sha.get(sha, []), key=int),
            "historical_note_not_approval": SUPERSEDED_TIP_NOTES.get(sha),
            "main_only_commits": group["main_only_commits"],
            "branch_only_commits": group["branch_only_commits"],
        })
        for name in names:
            ref = "refs/heads/" + name
            exact_refs[ref] = sha
            output_refs.append({
                "ref": ref, "tip_sha": sha, "same_tip_names_count": len(names),
                "proposed_effect": "NONE", "retirement_decision": "HOLD_PER_REF_REVIEW",
                "recovery_receipt": {"ref": ref, "commit_sha": sha,
                                     "remote_object_retention": "NOT_VERIFIED"},
                "checks_required_before_any_later_deletion": PER_REF_CHECKS,
            })
    receipt_bytes = "".join(
        f"{name}\t{sha}\n" for name, sha in sorted(exact_refs.items())
    ).encode("utf-8")
    return {
        "schema_version": "trek-branch-retirement-dry-run-v1",
        "effect": "READ_ONLY_NO_REF_MUTATIONS",
        "basis": {"accepted_main_sha_at_census": main_sha,
                  "source_census_schema": census["schema_version"],
                  "branch_snapshot_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
                  "branch_snapshot_name_count": len(exact_refs),
                  "main_head_may_have_moved_since_snapshot": True},
        "summary": {
            "non_main_names": len(output_refs), "distinct_non_main_tips": len(output_groups),
            "duplicate_tip_extra_names": sum(
                max(0, group["branch_count"] - 1) for group in output_groups),
            "retirement_actions_authorized": 0,
            "pr_head_snapshot_refs": len(prs),
        },
        "groups": output_groups,
        "branch_holds": sorted(output_refs, key=lambda row: row["ref"]),
        "removal_policy": "No branch is safe to prune from tip equality alone. Review every exact name, PR and automation references, archived receipt, and recovery path separately.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census", type=Path, required=True,
                        help="Offline JSON from tools/audit_git_topology.py (v2 disjoint refs)")
    parser.add_argument("--audit-repo", type=Path, default=None,
                        help="Optional local object store for READ-ONLY tree path inspection; never fetches")
    args = parser.parse_args(argv)
    try:
        result = plan(read_json(args.census), audit_repo=args.audit_repo)
    except Rejected as exc:
        print(f"RETIREMENT_PLAN_REJECTED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
