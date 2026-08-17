#!/usr/bin/env python3
"""Deterministic repository admission validation with no network dependencies."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOTS = [ROOT / "research", ROOT / "registry", ROOT / "reconciliation", ROOT / "external", ROOT / "migrations"]
ID_FIELDS = {
    "source": "source_id",
    "work": "work_id",
    "local_entity": "local_entity_id",
    "evidence": "evidence_id",
    "assertion": "assertion_id",
    "batch_manifest": "batch_id",
    "reconciliation_decision": "decision_id",
    "source_work_binding": "binding_id",
    "coverage_state": "coverage_id",
}
SCHEMA_FILES = {
    "source": "source.schema.json",
    "work": "work.schema.json",
    "local_entity": "local-entity.schema.json",
    "evidence": "evidence.schema.json",
    "assertion": "assertion.schema.json",
    "batch_manifest": "batch-manifest.schema.json",
    "reconciliation_decision": "reconciliation-decision.schema.json",
    "source_work_binding": "source-work-binding.schema.json",
    "coverage_state": "coverage-state.schema.json",
}


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def iter_records():
    for base in DATA_ROOTS:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.json")):
            if "tests/fixtures" in path.as_posix():
                continue
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict) and "record_type" in obj:
                yield path, obj
        for path in sorted(base.rglob("*.jsonl")):
            for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not raw.strip():
                    continue
                obj = json.loads(raw)
                if not isinstance(obj, dict):
                    raise ValueError(f"{path}:{line_no}: record must be an object")
                yield path, obj


def type_ok(value, expected):
    names = expected if isinstance(expected, list) else [expected]
    for name in names:
        if name == "null" and value is None:
            return True
        if name == "string" and isinstance(value, str):
            return True
        if name == "object" and isinstance(value, dict):
            return True
        if name == "array" and isinstance(value, list):
            return True
        if name == "boolean" and isinstance(value, bool):
            return True
        if name == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if name == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
    return False


def validate_schema(record, schema, label, errors):
    for key in schema.get("required", []):
        if key not in record:
            errors.append(f"{label}: missing required field {key}")
    for key, rule in schema.get("properties", {}).items():
        if key not in record:
            continue
        value = record[key]
        if "const" in rule and value != rule["const"]:
            errors.append(f"{label}: {key} must equal {rule['const']!r}")
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{label}: {key} has ungoverned value {value!r}")
        if "type" in rule and not type_ok(value, rule["type"]):
            errors.append(f"{label}: {key} has wrong type")
        if isinstance(value, str) and rule.get("minLength", 0) > len(value):
            errors.append(f"{label}: {key} is too short")
        if isinstance(value, dict) and rule.get("type") == "object":
            validate_schema(value, rule, f"{label}.{key}", errors)
        if isinstance(value, list) and rule.get("type") == "array" and isinstance(rule.get("items"), dict):
            for i, item in enumerate(value):
                irule = rule["items"]
                if "type" in irule and not type_ok(item, irule["type"]):
                    errors.append(f"{label}: {key}[{i}] has wrong type")
    if schema.get("additionalProperties") is False:
        allowed = set(schema.get("properties", {}))
        extra = sorted(set(record) - allowed)
        if extra:
            errors.append(f"{label}: unexpected fields {extra}")


def batch_payload_hash(batch_dir: Path, manifest_path: Path) -> str:
    rows = []
    for path in sorted(batch_dir.rglob("*")):
        if not path.is_file() or path == manifest_path or path.suffix not in {".json", ".jsonl"}:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rel = path.relative_to(batch_dir).as_posix()
        rows.append(f"{rel}\0sha256:{digest}\n")
    return "sha256:" + hashlib.sha256("".join(rows).encode("utf-8")).hexdigest()


def main() -> int:
    errors = []
    schemas = {}
    for rt, name in SCHEMA_FILES.items():
        schemas[rt] = json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))
    predicates = {p["name"] for p in json.loads((ROOT / "registry" / "predicates.json").read_text(encoding="utf-8"))["predicates"]}

    records = []
    seen = {}
    try:
        records = list(iter_records())
    except Exception as exc:
        print("VALIDATION FAILED")
        print(f"- {exc}")
        return 1

    by_type = {rt: {} for rt in ID_FIELDS}
    for path, record in records:
        rt = record.get("record_type")
        label = str(path.relative_to(ROOT))
        if rt not in ID_FIELDS:
            errors.append(f"{label}: unknown record_type {rt!r}")
            continue
        validate_schema(record, schemas[rt], label, errors)
        id_field = ID_FIELDS[rt]
        rid = record.get(id_field)
        if rid:
            if (rt, rid) in seen:
                errors.append(f"duplicate {rt} id {rid}: {seen[(rt, rid)]} and {label}")
            else:
                seen[(rt, rid)] = label
                by_type[rt][rid] = (path, record)

    def require(rt, rid, owner):
        if rid and rid not in by_type[rt]:
            errors.append(f"{owner}: dangling {rt} reference {rid}")

    for path, record in records:
        rt = record.get("record_type")
        label = str(path.relative_to(ROOT))
        if rt == "local_entity":
            require("work", record.get("work_id"), label)
        elif rt == "evidence":
            require("source", record.get("source_id"), label)
            require("work", record.get("work_id"), label)
            if record.get("observer_local_entity_id"):
                require("local_entity", record["observer_local_entity_id"], label)
        elif rt == "assertion":
            for eid in record.get("evidence", []):
                require("evidence", eid, label)
            predicate = record.get("predicate")
            if predicate and predicate not in predicates:
                errors.append(f"{label}: predicate {predicate!r} is not in registry/predicates.json")
        elif rt == "source_work_binding":
            require("source", record.get("source_id"), label)
            require("work", record.get("work_id"), label)
        elif rt == "coverage_state":
            require("work", record.get("work_id"), label)
            if not record.get("transition_evidence") and any(record.get("states", {}).values()):
                errors.append(f"{label}: positive coverage state lacks transition_evidence")
            if "done" in {k.lower() for k in record.get("states", {})}:
                errors.append(f"{label}: coverage must not collapse to done")
        elif rt == "reconciliation_decision" and record.get("status") == "ACCEPTED" and not record.get("method"):
            errors.append(f"{label}: accepted reconciliation decision missing method")
        elif rt == "batch_manifest":
            if "research" not in path.parts or "batches" not in path.parts:
                errors.append(f"{label}: batch manifest must live under research/<lane>/.../batches/<batch-id>/")
            batch_dir = path.parent
            expected_hash = batch_payload_hash(batch_dir, path)
            if record.get("batch_hash") != expected_hash:
                errors.append(f"{label}: batch_hash mismatch; expected {expected_hash}")
            counts = {}
            for p2, r2 in records:
                if p2 != path and batch_dir in p2.parents:
                    key = r2.get("record_type")
                    counts[key] = counts.get(key, 0) + 1
            declared = record.get("record_counts", {})
            if declared != counts:
                errors.append(f"{label}: record_counts mismatch; declared {declared}, actual {counts}")
            for wid in record.get("works", []):
                require("work", wid, label)

    if errors:
        print("VALIDATION FAILED")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    print(f"VALIDATION PASSED: {len(seen)} identified records; schemas, references, predicates, coverage, and batch integrity checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
