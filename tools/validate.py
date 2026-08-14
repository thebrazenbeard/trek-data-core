#!/usr/bin/env python3
"""Deterministic repository admission validation with no network dependencies."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOTS = [ROOT / "research", ROOT / "reconciliation", ROOT / "external", ROOT / "migrations"]
SCHEMA_ROOT = ROOT / "schema"
PREDICATE_REGISTRY = ROOT / "registry" / "predicates.json"
SCHEMA_FILES = {
    "source": "source.schema.json", "work": "work.schema.json", "local_entity": "local-entity.schema.json",
    "evidence": "evidence.schema.json", "assertion": "assertion.schema.json",
    "batch_manifest": "batch-manifest.schema.json", "reconciliation_decision": "reconciliation-decision.schema.json",
}
ID_FIELDS = {
    "source": "source_id", "work": "work_id", "local_entity": "local_entity_id", "evidence": "evidence_id",
    "assertion": "assertion_id", "batch_manifest": "batch_id", "reconciliation_decision": "decision_id",
}
COUNT_KEYS = {
    "sources": "source", "works": "work", "local_entities": "local_entity", "evidence": "evidence",
    "assertions": "assertion", "reconciliation_decisions": "reconciliation_decision",
}
REQUIRED_BATCH_COUNTS = ("local_entities", "evidence", "assertions")
WORKER_FORBIDDEN_RECORD_TYPES = {"source", "work", "reconciliation_decision"}
RESEARCH_WORKERS = {
    "tos": "TOS", "tas": "TAS", "tng": "TNG", "ds9": "DS9", "voyager": "VOY", "enterprise": "ENT",
    "discovery": "DIS", "short-treks": "SHORT", "picard": "PIC", "lower-decks": "LD", "prodigy": "PRO",
    "strange-new-worlds": "SNW", "starfleet-academy": "SFA", "films": "FILMS", "literature": "LIT",
}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_canonical(value):
    return "sha256:" + hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def physical_path(path: Path) -> Path:
    match = re.match(r"^(.*\.jsonl):\d+$", str(path))
    return Path(match.group(1)) if match else path


def iter_records():
    for base in DATA_ROOTS:
        if not base.exists(): continue
        for path in sorted(base.rglob("*.json")):
            if path.name == "README.json": continue
            try: obj = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc: raise ValueError(f"{path}: invalid JSON: {exc}") from exc
            if not isinstance(obj, dict): raise ValueError(f"{path}: governed JSON artifact must be an object record")
            yield path, obj
        for path in sorted(base.rglob("*.jsonl")):
            for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not raw.strip(): continue
                try: obj = json.loads(raw)
                except Exception as exc: raise ValueError(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
                if not isinstance(obj, dict): raise ValueError(f"{path}:{line_no}: record must be an object")
                yield Path(f"{path}:{line_no}"), obj


def load_schemas():
    return {rt: json.loads((SCHEMA_ROOT / fn).read_text(encoding="utf-8")) for rt, fn in SCHEMA_FILES.items()}


def load_predicates():
    registry = json.loads(PREDICATE_REGISTRY.read_text(encoding="utf-8"))
    return {item["name"] for item in registry.get("predicates", []) if item.get("name")}


def type_matches(value, expected):
    if expected == "null": return value is None
    if expected == "object": return isinstance(value, dict)
    if expected == "array": return isinstance(value, list)
    if expected == "string": return isinstance(value, str)
    if expected == "boolean": return isinstance(value, bool)
    if expected == "integer": return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number": return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def schema_errors(value, schema, location="$"):
    errors = []
    expected_type = schema.get("type")
    if expected_type is not None:
        allowed = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(type_matches(value, item) for item in allowed): return [f"{location}: expected type {allowed}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]: errors.append(f"{location}: expected constant {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]: errors.append(f"{location}: value {value!r} is not in enum {schema['enum']!r}")
    if isinstance(value, str) and "minLength" in schema and len(value) < schema["minLength"]: errors.append(f"{location}: string shorter than minLength {schema['minLength']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]: errors.append(f"{location}: array shorter than minItems {schema['minItems']}")
        if "items" in schema:
            for index, item in enumerate(value): errors.extend(schema_errors(item, schema["items"], f"{location}[{index}]"))
    if isinstance(value, dict):
        for required in schema.get("required", []):
            if required not in value: errors.append(f"{location}: missing required property {required}")
        properties = schema.get("properties", {})
        for key, child in value.items():
            if key in properties: errors.extend(schema_errors(child, properties[key], f"{location}.{key}"))
            elif schema.get("additionalProperties") is False: errors.append(f"{location}: unexpected property {key}")
    return errors


def add_missing_reference(errors, path, field, target_type, target_id, index):
    if target_id and target_id not in index.get(target_type, {}): errors.append(f"{path}: {field} references missing {target_type} {target_id}")


def validate_references(records, index, errors):
    for path, record in records:
        rt = record.get("record_type")
        if rt == "source":
            for source_id in record.get("derived_from", []): add_missing_reference(errors, path, "derived_from", "source", source_id, index)
        elif rt == "work":
            if record.get("parent_work_id"): add_missing_reference(errors, path, "parent_work_id", "work", record["parent_work_id"], index)
        elif rt == "local_entity": add_missing_reference(errors, path, "work_id", "work", record.get("work_id"), index)
        elif rt == "evidence":
            add_missing_reference(errors, path, "source_id", "source", record.get("source_id"), index)
            add_missing_reference(errors, path, "work_id", "work", record.get("work_id"), index)
            if record.get("observer_local_entity_id"): add_missing_reference(errors, path, "observer_local_entity_id", "local_entity", record["observer_local_entity_id"], index)
        elif rt == "assertion":
            for evidence_id in record.get("evidence", []): add_missing_reference(errors, path, "evidence", "evidence", evidence_id, index)
            if record.get("supersedes"): add_missing_reference(errors, path, "supersedes", "assertion", record["supersedes"], index)
        elif rt == "reconciliation_decision":
            for evidence_id in record.get("evidence", []):
                if evidence_id not in index.get("evidence", {}) and evidence_id not in index.get("assertion", {}): errors.append(f"{path}: evidence references missing evidence/assertion {evidence_id}")
            if record.get("supersedes"): add_missing_reference(errors, path, "supersedes", "reconciliation_decision", record["supersedes"], index)


def batch_records_for(manifest_path: Path, records):
    batch_root = physical_path(manifest_path).parent
    selected = []
    for path, record in records:
        if record.get("record_type") == "batch_manifest": continue
        try: physical_path(path).relative_to(batch_root)
        except ValueError: continue
        selected.append(record)
    return sorted(selected, key=canonical)


def compute_batch_hash(manifest, batch_records):
    return sha256_canonical({"manifest": {k: v for k, v in manifest.items() if k != "batch_hash"}, "records": batch_records})


def expected_worker_for_path(path: Path):
    physical = physical_path(path)
    for root in DATA_ROOTS:
        if root.name != "research": continue
        try: relative = physical.relative_to(root)
        except ValueError: continue
        if relative.parts: return RESEARCH_WORKERS.get(relative.parts[0])
    return None


def validate_batch_integrity(records, index, errors):
    known_source_hashes = {r.get("content_hash") for r in index.get("source", {}).values() if r.get("content_hash")}
    for path, manifest in records:
        if manifest.get("record_type") != "batch_manifest": continue
        batch_records = batch_records_for(path, records)
        expected_hash = compute_batch_hash(manifest, batch_records)
        if manifest.get("batch_hash") != expected_hash: errors.append(f"{path}: batch_hash mismatch: declared {manifest.get('batch_hash')}, expected {expected_hash}")
        actual_counts = {}
        for record in batch_records:
            rt = record.get("record_type"); actual_counts[rt] = actual_counts.get(rt, 0) + 1
        declared_counts = manifest.get("record_counts", {})
        for required_key in REQUIRED_BATCH_COUNTS:
            if required_key not in declared_counts: errors.append(f"{path}: record_counts.{required_key} is required for a governed research batch")
        for key, record_type in COUNT_KEYS.items():
            if key in declared_counts and declared_counts[key] != actual_counts.get(record_type, 0): errors.append(f"{path}: record_counts.{key}={declared_counts[key]} but batch contains {actual_counts.get(record_type, 0)}")
        for work_id in manifest.get("works", []): add_missing_reference(errors, path, "works", "work", work_id, index)
        for source_hash in manifest.get("source_hashes", []):
            if source_hash not in known_source_hashes: errors.append(f"{path}: source_hashes references unknown source content_hash {source_hash}")
        expected_worker = expected_worker_for_path(path)
        if expected_worker:
            if manifest.get("worker_id") != expected_worker: errors.append(f"{path}: worker_id {manifest.get('worker_id')} does not match research partition owner {expected_worker}")
            forbidden = sorted({r.get("record_type") for r in batch_records if r.get("record_type") in WORKER_FORBIDDEN_RECORD_TYPES})
            if forbidden: errors.append(f"{path}: worker-owned batch contains Librarian/Consolidator-owned record types: {', '.join(forbidden)}")


def main() -> int:
    seen = {}; index = {record_type: {} for record_type in ID_FIELDS}; errors = []
    schemas = load_schemas(); predicates = load_predicates()
    try: records = list(iter_records())
    except ValueError as exc: records = []; errors.append(str(exc))
    for path, record in records:
        rt = record.get("record_type")
        if not rt: errors.append(f"{path}: missing record_type"); continue
        if rt not in schemas: errors.append(f"{path}: unknown record_type {rt}"); continue
        for error in schema_errors(record, schemas[rt]): errors.append(f"{path}: schema: {error}")
        id_field = ID_FIELDS.get(rt)
        if id_field:
            rid = record.get(id_field)
            if not rid: errors.append(f"{path}: {rt} missing {id_field}")
            elif (rt, rid) in seen: errors.append(f"duplicate {rt} id {rid}: {seen[(rt, rid)]} and {path}")
            else: seen[(rt, rid)] = path; index[rt][rid] = record
        if rt == "assertion":
            if not record.get("evidence"): errors.append(f"{path}: assertion {record.get('assertion_id')} has no evidence")
            predicate = record.get("predicate")
            if predicate and predicate not in predicates: errors.append(f"{path}: assertion {record.get('assertion_id')} uses unregistered predicate {predicate}")
        if rt == "reconciliation_decision" and record.get("status") == "ACCEPTED" and not record.get("method"): errors.append(f"{path}: accepted reconciliation decision missing method")
    validate_references(records, index, errors); validate_batch_integrity(records, index, errors)
    if errors:
        print("VALIDATION FAILED"); print("\n".join(f"- {e}" for e in errors)); return 1
    print(f"VALIDATION PASSED: {len(seen)} identified records"); return 0


if __name__ == "__main__": sys.exit(main())
