#!/usr/bin/env python3
"""Read-only, deterministic Windows path-portability guard for a Git tree.

Uses Git objects rather than the working directory, so colliding paths remain
visible even when a case-insensitive checkout cannot materialize both.
"""
import argparse
import json
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict

RESERVED = re.compile(r"^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?$", re.I)
INVALID = re.compile(r'[<>:"\\|?*\x00-\x1f]')


def inspect(ref):
    raw = subprocess.check_output(["git", "ls-tree", "-rz", "--full-tree", ref])
    groups = defaultdict(list)
    invalid = []
    count = 0
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, path_bytes = record.split(b"\t", 1)
        mode, kind, oid = metadata.decode("ascii").split()
        if kind != "blob":
            continue
        count += 1
        path = path_bytes.decode("utf-8", "surrogateescape")
        key = unicodedata.normalize("NFKC", path).casefold()
        groups[key].append({"path": path, "blob": oid, "mode": mode})
        if any(INVALID.search(s) or s.endswith((" ", ".")) or RESERVED.match(s)
               for s in path.split("/")):
            invalid.append(path)
    collisions = [sorted(v, key=lambda x: x["path"]) for v in groups.values() if len(v) > 1]
    collisions.sort(key=lambda v: v[0]["path"])
    return {"ref": ref, "blob_count": count, "collision_groups": collisions,
            "windows_invalid_paths": sorted(invalid), "portable": not collisions and not invalid}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="HEAD", help="Git tree-ish to inspect (default HEAD)")
    args = parser.parse_args()
    result = inspect(args.ref)
    print(json.dumps(result, indent=2, ensure_ascii=True, sort_keys=True))
    return 0 if result["portable"] else 1


if __name__ == "__main__":
    sys.exit(main())
