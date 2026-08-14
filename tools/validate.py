#!/usr/bin/env python3
"""Lightweight repository validation with no network dependencies."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOTS = [ROOT / "research", ROOT / "reconciliation", ROOT / "external", ROOT / "migrations"]
ID_FIELDS = {
    "source": "source_id",
    "work": "work_id",
    "local_entity": "local_entity_id",
    "evidence": "evidence_id",
    "assertion": "assertion_id",
    "batch_manifest": "batch_id",
    "reconciliation_decision": "decision_id",
}


def iter_records():
    for base in DATA_ROOTS:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.json")):
            if path.name == "README.json":
                continue
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                raise ValueError(f"{path}: invalid JSON: {exc}") from exc
            if isinstance(obj, dict) and "record_type" in obj:
                yield path, obj
        for path in sorted(base.rglob("*.jsonl")):
            for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not raw.strip():
                    continue
                try:
                    obj = json.loads(raw)
                except Exception as exc:
                    raise ValueError(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
                if not isinstance(obj, dict):
                    raise ValueError(f"{path}:{line_no}: record must be an object")
                yield path, obj


def main() -> int:
    seen = {}
    errors = []
    for path, record in iter_records():
        rt = record.get("record_type")
        if not rt:
            errors.append(f"{path}: missing record_type")
            continue
        id_field = ID_FIELDS.get(rt)
        if id_field:
            rid = record.get(id_field)
            if not rid:
                errors.append(f"{path}: {rt} missing {id_field}")
            elif (rt, rid) in seen:
                errors.append(f"duplicate {rt} id {rid}: {seen[(rt, rid)]} and {path}")
            else:
                seen[(rt, rid)] = path
        if rt == "assertion" and not record.get("evidence"):
            errors.append(f"{path}: assertion {record.get('assertion_id')} has no evidence")
        if rt == "reconciliation_decision" and record.get("status") == "ACCEPTED" and not record.get("method"):
            errors.append(f"{path}: accepted reconciliation decision missing method")
    if errors:
        print("VALIDATION FAILED")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    print(f"VALIDATION PASSED: {len(seen)} identified records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
