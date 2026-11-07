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

RESERVED = re.compile(r"^(?:CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|COM[1-9¹²³]|LPT[1-9¹²³])$", re.I)
INVALID = re.compile(r'[<>:"\\|?*\x00-\x1f]')


def reserved_device(segment):
    """Windows ignores trailing spaces/dots in the device-name stem."""
    stem = segment.split(".", 1)[0].rstrip(" .")
    return bool(RESERVED.fullmatch(stem))


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
        # Gitlinks (mode 160000) are tracked paths too: an unsafe submodule
        # name can break a Windows checkout even though it has no blob payload.
        if kind not in ("blob", "commit"):
            raise ValueError(f"unexpected tracked Git object kind: {kind}")
        if kind == "blob":
            count += 1
        path = path_bytes.decode("utf-8", "surrogateescape")
        # Git permits arbitrary filename bytes, but a surrogateescaped byte
        # is not a valid UTF-8 pathname and must never pass portability.
        undecodable = any(0xDC80 <= ord(ch) <= 0xDCFF for ch in path)
        key = unicodedata.normalize("NFKC", path).casefold()
        groups[key].append({"path": path, "blob": oid if kind == "blob" else None,
                            "mode": mode, "kind": kind, "oid": oid})
        if undecodable or any(INVALID.search(s) or s.endswith((" ", ".")) or reserved_device(s)
                            or len(s.encode("utf-16-le", "surrogatepass")) // 2 > 255
                            for s in path.split("/")):
            invalid.append(path)
    # A Windows checkout also has to materialize every implied directory.
    # Git records leaf paths, so compare all normalized prefixes as well.
    # Deduplicate shared directory prefixes without erasing case variants.
    for entries in list(groups.values()):
        for entry in entries:
            parts = entry["path"].split("/")
            for depth in range(1, len(parts)):
                prefix = "/".join(parts[:depth])
                key = unicodedata.normalize("NFKC", prefix).casefold()
                directory = {"path": prefix, "blob": None, "mode": "040000",
                             "kind": "tree", "oid": None}
                if not any(e["path"] == prefix and e["kind"] == "tree"
                           for e in groups[key]):
                    groups[key].append(directory)
    # Preserve multiplicity: malformed Git trees can contain duplicate leaf
    # entries with identical path, mode and object ID. A set would erase them.
    # Implied directory prefixes are deduplicated above, not leaf entries.
    collisions = [
        sorted(v, key=lambda x: (x["path"], x["kind"], x["oid"] or ""))
        for v in groups.values()
        if len(v) > 1
    ]
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
