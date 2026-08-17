#!/usr/bin/env python3
"""Deterministic repository record validation with no network dependencies."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOTS = [ROOT / "research", ROOT / "reconciliation", ROOT / "external", ROOT / "migrations"]
SCHEMA_FILES = {
    "source": "source.schema.json",
    "work": "work.schema.json",
    "local_entity": "local-entity.schema.json",
    "evidence": "evidence.schema.json",
    "assertion": "assertion.schema.json",
    "batch_manifest": "batch-manifest.schema.json",
    "reconciliation_decision": "reconciliation-decision.schema.json",
}
ID_FIELDS = {
    "source": "source_id",
    "work": "work_id",
    "local_entity": "local_entity_id",
    "evidence": "evidence_id",
    "assertion": "assertion_id",
    "batch_manifest": "batch_id",
    "reconciliation_decision": "decision_id",
}


def load_schemas():
    schemas = {}
    for record_type, filename in SCHEMA_FILES.items():
        path = ROOT / "schema" / filename
        schemas[record_type] = json.loads(path.read_text(encoding="utf-8"))
    return schemas


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
                yield Path(f"{path}:{line_no}"), obj


def matches_type(value, expected):
    if expected == "null":
        return value is None
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    return True


def validate_value(value, schema, location, errors):
    expected = schema.get("type")
    if expected is not None:
        allowed = expected if isinstance(expected, list) else [expected]
        if not any(matches_type(value, item) for item in allowed):
            errors.append(f"{location}: expected type {allowed}, got {type(value).__name__}")
            return

    if "const" in schema and value != schema["const"]:
        errors.append(f"{location}: expected constant {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: value {value!r} not in enum {schema['enum']!r}")
    if isinstance(value, str) and "minLength" in schema and len(value) < schema["minLength"]:
        errors.append(f"{location}: string shorter than minLength {schema['minLength']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{location}: array shorter than minItems {schema['minItems']}")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_value(item, schema["items"], f"{location}[{index}]", errors)
    if isinstance(value, dict):
        for required in schema.get("required", []):
            if required not in value:
                errors.append(f"{location}: missing required property {required}")
        for key, subschema in schema.get("properties", {}).items():
            if key in value:
                validate_value(value[key], subschema, f"{location}.{key}", errors)


def main() -> int:
    schemas = load_schemas()
    seen = {}
    errors = []
    record_count = 0
    try:
        records = list(iter_records())
    except ValueError as exc:
        print("VALIDATION FAILED")
        print(f"- {exc}")
        return 1

    for path, record in records:
        record_count += 1
        rt = record.get("record_type")
        if not rt:
            errors.append(f"{path}: missing record_type")
            continue
        schema = schemas.get(rt)
        if schema is None:
            errors.append(f"{path}: unsupported record_type {rt!r}; no governed schema")
            continue
        validate_value(record, schema, str(path), errors)

        id_field = ID_FIELDS[rt]
        rid = record.get(id_field)
        if rid:
            if (rt, rid) in seen:
                errors.append(f"duplicate {rt} id {rid}: {seen[(rt, rid)]} and {path}")
            else:
                seen[(rt, rid)] = path

        if rt == "reconciliation_decision" and record.get("status") == "ACCEPTED" and not record.get("method"):
            errors.append(f"{path}: accepted reconciliation decision missing method")

    if errors:
        print("VALIDATION FAILED")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    print(f"VALIDATION PASSED: {record_count} records; {len(seen)} identified records; schemas enforced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
