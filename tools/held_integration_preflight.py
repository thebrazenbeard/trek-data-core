#!/usr/bin/env python3
"""Read-only, offline preflight for *proposed* Trek draft integration.

This is an advisory fail-closed guard, never a substitute for accepted research,
rights review, CI, owner authorization, or the existing artwork/synopsis gates.
It reads pinned local Git objects, not unverified PR descriptions or live URLs.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{40}\Z")
RASTER = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
PUBLIC_DATA_SUFFIXES = {".json", ".jsonl", ".ndjson", ".csv"}


def _git(root, *args):
    return subprocess.run(["git", "--no-pager", *args], cwd=root,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=False)


def _commit(root, sha):
    result = _git(root, "cat-file", "-t", sha)
    return result.returncode == 0 and result.stdout.strip() == b"commit"


def _ancestor(root, older, newer):
    return _git(root, "merge-base", "--is-ancestor", older, newer).returncode == 0


def _changes(root, base, head):
    result = _git(root, "diff", "--no-ext-diff", "--no-textconv", "--name-only", "-z", base, head)
    if result.returncode:
        raise ValueError("unable to examine pinned Git diff")
    return sorted({p.decode("utf-8", "surrogateescape") for p in result.stdout.split(b"\0") if p})


def _blob(root, head, path):
    result = _git(root, "rev-parse", "--verify", f"{head}:{path}")
    return result.stdout.strip() if result.returncode == 0 else None


def _validate_plan(plan):
    if not isinstance(plan, dict) or set(plan) != {"base_head", "candidate_head", "mode", "selected", "drafts"}:
        raise ValueError("plan needs exactly base_head, candidate_head, mode, selected, drafts")
    for field in ("base_head", "candidate_head"):
        if not isinstance(plan[field], str) or not SHA.fullmatch(plan[field]):
            raise ValueError(f"{field} must be a complete 40-character Git commit ID")
    if plan["mode"] not in ("review", "production"):
        raise ValueError("mode must be review or production")
    if not isinstance(plan["selected"], list) or not all(isinstance(i, str) and i for i in plan["selected"]):
        raise ValueError("selected must be a list of draft IDs")
    if len(plan["selected"]) != len(set(plan["selected"])):
        raise ValueError("selected contains duplicate draft IDs")
    if not isinstance(plan["drafts"], list):
        raise ValueError("drafts must be a list")
    seen = set()
    for draft in plan["drafts"]:
        if not isinstance(draft, dict) or set(draft) != {"id", "head", "depends_on"}:
            raise ValueError("draft needs exactly id, head, depends_on")
        if not isinstance(draft["id"], str) or not draft["id"] or draft["id"] in seen:
            raise ValueError("draft IDs must be unique nonempty strings")
        seen.add(draft["id"])
        if not isinstance(draft["head"], str) or not SHA.fullmatch(draft["head"]):
            raise ValueError("draft head must be a complete 40-character commit ID")
        deps = draft["depends_on"]
        if not isinstance(deps, list) or not all(isinstance(dep, str) and dep for dep in deps) or len(deps) != len(set(deps)):
            raise ValueError("depends_on must list distinct nonempty draft IDs")
    if set(plan["selected"]) - seen:
        raise ValueError("selected references undeclared draft IDs")
    for draft in plan["drafts"]:
        if set(draft["depends_on"]) - seen or draft["id"] in draft["depends_on"]:
            raise ValueError("dependency must name another declared draft")


def evaluate(root, plan):
    """Check pinned object identity and integration hazards without writing."""
    root = Path(root)
    _validate_plan(plan)
    base, candidate = plan["base_head"], plan["candidate_head"]
    blockers = []

    def block(code, detail):
        blockers.append({"code": code, "detail": detail})

    if not _commit(root, base):
        block("UNKNOWN_ACCEPTED_BASE", base)
    if not _commit(root, candidate):
        block("UNKNOWN_CANDIDATE_HEAD", candidate)
    if blockers:
        return {"status": "BLOCKED", "mode": plan["mode"], "blockers": blockers,
                "selected": [], "public_changed_paths": []}
    if not _ancestor(root, base, candidate):
        block("CANDIDATE_NOT_BASE_DESCENDANT", candidate)

    catalog = {draft["id"]: draft for draft in plan["drafts"]}
    chosen = set(plan["selected"])
    # A self-declared dependency list is not independent evidence that the
    # relationship is correct, but cycles within it can always be rejected.
    visiting, visited = set(), set()

    def inspect_dependencies(draft_id, trail):
        if draft_id in visiting:
            block("DRAFT_DEPENDENCY_CYCLE", " -> ".join(trail + [draft_id]))
            return
        if draft_id in visited:
            return
        visiting.add(draft_id)
        for dependency in catalog[draft_id]["depends_on"]:
            if dependency in chosen:
                inspect_dependencies(dependency, trail + [draft_id])
        visiting.remove(draft_id)
        visited.add(draft_id)

    for draft_id in sorted(chosen):
        inspect_dependencies(draft_id, [])
    selected = []
    path_owners = {}
    examined_paths = set(_changes(root, base, candidate))
    for draft_id in plan["selected"]:
        draft = catalog[draft_id]
        head = draft["head"]
        if not _commit(root, head):
            block("UNKNOWN_DRAFT_HEAD", f"{draft_id}:{head}")
            continue
        if not _ancestor(root, base, head):
            block("DRAFT_NOT_BASE_DESCENDANT", draft_id)
            continue
        for dependency in draft["depends_on"]:
            dependency_head = catalog[dependency]["head"]
            if dependency not in chosen and not (
                _commit(root, dependency_head) and _ancestor(root, dependency_head, base)
            ):
                block("MISSING_DRAFT_DEPENDENCY", f"{draft_id} requires {dependency}")
        paths = _changes(root, base, head)
        examined_paths.update(paths)
        for path in paths:
            path_owners.setdefault(path, []).append((draft_id, _blob(root, head, path)))
        if _ancestor(root, head, candidate):
            inclusion = "ANCESTOR"
        elif all(_blob(root, head, path) == _blob(root, candidate, path) for path in paths):
            inclusion = "EXACT_TREE_PATHS"
        else:
            inclusion = "NOT_INCLUDED"
            block("DRAFT_NOT_IN_CANDIDATE", draft_id)
        selected.append({"id": draft_id, "head": head, "integration": inclusion,
                         "changed_paths": paths})

    for path, owners in sorted(path_owners.items()):
        if len({blob for _, blob in owners}) > 1:
            block("DRAFT_PATH_COLLISION", f"{path}: " + ", ".join(id for id, _ in owners))

    public_paths = sorted(path for path in examined_paths if path.startswith("explorer/"))
    if plan["mode"] == "production":
        artwork = [path for path in public_paths if
                   path.startswith("explorer/licensed-artwork/") or Path(path).suffix.lower() in RASTER]
        if artwork:
            block("ARTWORK_RIGHTS_GATE", ", ".join(artwork))
        # Filename keywords are inadequate: public data.json could still
        # falsely promote held literary/episode metadata to accepted status.
        semantic = [path for path in examined_paths if
                    path.startswith(("research/", "coverage/", "registry/", "reconciliation/", "projections/", "database/")) or
                    (path.startswith("explorer/") and Path(path).suffix.lower() in PUBLIC_DATA_SUFFIXES)]
        if semantic:
            block("SEMANTIC_PROJECTION_REVIEW_REQUIRED", ", ".join(sorted(semantic)))
        ui = [path for path in public_paths if Path(path).suffix.lower() in (".html", ".js", ".css")]
        if ui:
            block("PUBLIC_UI_RELEASE_REVIEW", ", ".join(ui))
        compiler = [path for path in examined_paths if path.startswith("tools/") and
                    ("projection" in Path(path).name or "artwork_release" in Path(path).name)]
        if compiler:
            block("PROJECTION_COMPILER_REVIEW", ", ".join(sorted(compiler)))

    blockers.sort(key=lambda row: (row["code"], row["detail"]))
    return {"status": "BLOCKED" if blockers else "NO_PREFLIGHT_BLOCKERS_NOT_AUTHORIZED",
            "mode": plan["mode"], "base_head": base, "candidate_head": candidate,
            "blockers": blockers, "selected": selected,
            "public_changed_paths": public_paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = evaluate(Path(args.root), json.loads(args.plan.read_text(encoding="utf-8")))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, sort_keys=True, indent=2))
    if result["blockers"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
