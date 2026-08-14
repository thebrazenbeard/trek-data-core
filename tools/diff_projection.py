#!/usr/bin/env python3
"""Diff canonical projection JSONL by stable record identity."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

FILES = {
    "accepted_assertions.jsonl": "assertion_id",
    "accepted_reconciliation.jsonl": "decision_id",
}


def load(path: Path, key: str):
    if not path.exists():
        return {}
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    return {str(r.get(key)): r for r in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    args = ap.parse_args()
    old_root, new_root = Path(args.old), Path(args.new)
    changes = []
    for filename, key in FILES.items():
        old, new = load(old_root / filename, key), load(new_root / filename, key)
        for rid in sorted(new.keys() - old.keys()):
            changes.append(("ADDED", filename, rid))
        for rid in sorted(old.keys() - new.keys()):
            changes.append(("REMOVED", filename, rid))
        for rid in sorted(old.keys() & new.keys()):
            if old[rid] != new[rid]:
                changes.append(("CHANGED", filename, rid))
    for kind, filename, rid in changes:
        print(f"{kind}\t{filename}\t{rid}")
    print(f"changes={len(changes)}")


if __name__ == "__main__":
    main()
