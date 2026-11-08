#!/usr/bin/env python3
"""Read-only, deterministic Git-object audit of PR #604's HELD path proposal.

Runs on a clean POSIX checkout or CI; never changes the index or working tree.
Git-object SHA-256 is NOT independent source/read custody or Windows qualification.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

DEFAULT_MANIFEST = "reconciliation/audits/architecture-bootstrap-001/PR82-WINDOWS-COLLISION-CROSSWALK-PROPOSED.md"
ROW = re.compile(r"^\| `([^`]+)` \| `([^`]+)` \| `([0-9a-f]{40})` \| (100[0-7]{3}|120000|160000) \| ([0-9]+) \|$")
BASE = re.compile(r"main@([0-9a-f]{40})`, root tree `([0-9a-f]{40})`")
WINDOWS_RESERVED = re.compile(r"^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?$", re.I)
WINDOWS_FORBIDDEN = set('<>:"\\\\|?*')

def git(*args, data=None):
    return subprocess.run(["git", *args], input=data, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=True).stdout

def norm(path):
    return "/".join(unicodedata.normalize("NFKC", s).casefold().rstrip(" .")
                    for s in path.split("/"))

def validate_windows_path(path):
    if not path or path.startswith("/") or "\\x00" in path:
        raise ValueError("Invalid candidate path: " + repr(path))
    for part in path.split("/"):
        if (not part or part in (".", "..") or part.endswith((" ", "."))
                or WINDOWS_RESERVED.fullmatch(part)
                or any(ch in WINDOWS_FORBIDDEN or ord(ch) < 32 for ch in part)):
            raise ValueError("Windows-invalid candidate path segment: " + repr(part))


def audit(manifest):
    text = Path(manifest).read_text(encoding="utf-8")
    match = BASE.search(text)
    if not match:
        raise ValueError("Missing pinned base commit and root tree")
    commit, expected_tree = match.groups()
    actual_tree = git("rev-parse", commit + "^{tree}").decode().strip()
    if actual_tree != expected_tree:
        raise ValueError("Pinned root tree does not match commit object")
    entries = {}
    for entry in git("ls-tree", "-rz", "--full-tree", commit).split(b"\0"):
        if not entry:
            continue
        header, path = entry.split(b"\t", 1)
        mode, kind, oid = header.decode("ascii").split()
        if kind != "blob":
            raise ValueError("Unexpected nonblob recursive tree entry")
        entries[path.decode("utf-8", "surrogateescape")] = (mode, oid)
    rows = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Original path | Proposed unique destination |"):
            if in_table:
                raise ValueError("Duplicate mapping table")
            in_table = True
            continue
        if in_table and line.startswith("| ---"):
            continue
        if in_table and line.startswith("|"):
            match_row = ROW.fullmatch(line)
            if not match_row:
                raise ValueError("Malformed mapping row: " + line)
            p, d, oid, mode, size = match_row.groups()
            rows.append((p, d, oid, mode, int(size)))
        elif in_table and rows:
            in_table = False
    if not rows:
        raise ValueError("Missing mapping table")
    if len(rows) != 16 or len({r[0] for r in rows}) != 16:
        raise ValueError("Expected 16 unique source rows")
    if len({r[1] for r in rows}) != 16:
        raise ValueError("Duplicate destination")
    changed = dict(entries)
    custody = []
    for src, dest, oid, mode, size in rows:
        if src not in entries or entries[src] != (mode, oid):
            raise ValueError("Original Git object or mode mismatch: " + src)
        raw = git("cat-file", "blob", oid)
        if len(raw) != size:
            raise ValueError("Original byte size mismatch: " + src)
        if hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() != oid:
            raise ValueError("Git blob SHA-1 mismatch: " + src)
        custody.append({"original": src, "destination": dest, "blob_sha1": oid,
                        "git_object_sha256": hashlib.sha256(raw).hexdigest(),
                        "size": size, "mode": mode})
        changed.pop(src)
    for src, dest, oid, mode, size in rows:
        if dest in changed:
            raise ValueError("Destination already occupied: " + dest)
        changed[dest] = (mode, oid)
    seen = {}
    files = set()
    directories = set()
    for path in changed:
        validate_windows_path(path)
        key = norm(path)
        if key in seen:
            raise ValueError("Normalized path collision: " + seen[key] + " / " + path)
        seen[key] = path
        files.add(key)
        parts = key.split("/")
        for i in range(1, len(parts)):
            directories.add("/".join(parts[:i]))
    if files & directories:
        raise ValueError("File versus implied directory collision")
    if len(changed) != len(entries):
        raise ValueError("File count changed")
    return {"status": "HELD_GIT_OBJECT_AUDIT_ONLY", "base_commit": commit,
            "base_tree": actual_tree, "original_file_count": len(entries),
            "candidate_file_count": len(changed), "mappings": custody,
            "migration_executed": False, "native_windows_qualified": False,
            "independent_source_custody": False, "research_coverage_admitted": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    try:
        result = audit(args.manifest)
        print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True))
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
