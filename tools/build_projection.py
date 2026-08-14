#!/usr/bin/env python3
"""Deterministically compile accepted records into a canonical logical projection."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def read_jsonl(paths):
    out = []
    for path in sorted(paths):
        for raw in path.read_text(encoding="utf-8").splitlines():
            if raw.strip():
                out.append(json.loads(raw))
    return out


def write_jsonl(path: Path, records, id_key: str):
    ordered = sorted(records, key=lambda r: (str(r.get(id_key, "")), canonical(r)))
    payload = "".join(canonical(r) + "\n" for r in ordered).encode("utf-8")
    path.write_bytes(payload)
    return sha256_bytes(payload), len(ordered)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--projection-version", default="0.1.0")
    ap.add_argument("--methodology-version", default="0.1.0")
    ap.add_argument("--compiler-commit", default="UNPINNED")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    assertions = [r for r in read_jsonl(ROOT.glob("research/**/assertions.jsonl")) if r.get("status") == "ACCEPTED"]
    decisions = [r for r in read_jsonl(ROOT.glob("reconciliation/**/*.jsonl")) if r.get("record_type") == "reconciliation_decision" and r.get("status") == "ACCEPTED"]

    a_hash, a_count = write_jsonl(out / "accepted_assertions.jsonl", assertions, "assertion_id")
    d_hash, d_count = write_jsonl(out / "accepted_reconciliation.jsonl", decisions, "decision_id")

    input_material = canonical({"assertions": a_hash, "reconciliation": d_hash}).encode("utf-8")
    input_hash = sha256_bytes(input_material)
    projection_hash = sha256_bytes((a_hash + "\n" + d_hash + "\n").encode("utf-8"))
    manifest = {
        "record_type": "projection_manifest",
        "projection_version": args.projection_version,
        "methodology_version": args.methodology_version,
        "compiler_commit": args.compiler_commit,
        "research_head": None,
        "reconciliation_head": None,
        "predicate_registry_hash": None,
        "input_hash": input_hash,
        "projection_hash": projection_hash,
        "outputs": {
            "accepted_assertions.jsonl": {"hash": a_hash, "count": a_count},
            "accepted_reconciliation.jsonl": {"hash": d_hash, "count": d_count}
        }
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(projection_hash)


if __name__ == "__main__":
    main()
