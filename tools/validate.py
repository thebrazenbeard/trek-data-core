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
SCOPE_KEY_REGISTRY = ROOT / "registry" / "scope_keys.json"
SCHEMA_FILES = {
    "source": "source.schema.json", "work": "work.schema.json", "local_entity": "local-entity.schema.json",
    "evidence": "evidence.schema.json", "assertion": "assertion.schema.json",
    "batch_manifest": "batch-manifest.schema.json", "reconciliation_decision": "reconciliation-decision.schema.json",
}
ID_FIELDS = {
    "source": "source_id", "work": "work_id", "local_entity": "local_entity_id", "evidence": "evidence_id",
    "assertion": "assertion_id", "batch_manifest": "batch_id", "reconciliation_decision": "decision_id",
}
REFERENCE_TYPES = {
    "SOURCE": "source", "WORK": "work", "LOCAL_ENTITY": "local_entity", "EVIDENCE": "evidence",
    "ASSERTION": "assertion", "RECONCILIATION_DECISION": "reconciliation_decision",
}
COUNT_KEYS = {
    "sources": "source", "works": "work", "local_entities": "local_entity", "evidence": "evidence",
    "assertions": "assertion", "reconciliation_decisions": "reconciliation_decision",
}
REQUIRED_BATCH_COUNTS = ("local_entities", "evidence", "assertions")
WORKER_FORBIDDEN_RECORD_TYPES = {"source", "work", "reconciliation_decision"}
APPLIED_DECISION_TYPES = {"ENTITY_LINK", "ASSERTION_DISPOSITION", "ASSERTION_PROJECTION_STATUS", "SCOPE_RESOLUTION"}
PROJECTION_STATUSES = {"STABLE", "CONTESTED", "UNRESOLVED", "STRUCTURAL_PARADOX"}
DISPOSITIONS = {"PROPOSED", "ACCEPTED", "REJECTED"}
PREDICATE_METADATA_REQUIRED = {
    "name", "status", "definition", "semantic_class", "subject_types", "object_mode", "object_ref_types",
    "symmetry", "inverse", "transitive", "projection_eligibility", "examples", "near_miss",
    "supersedes", "superseded_by", "methodology_version", "introduced_in_registry",
}
RESEARCH_WORKERS = {
    "tos": "TOS", "tas": "TAS", "tng": "TNG", "ds9": "DS9", "voyager": "VOY", "enterprise": "ENT",
    "discovery": "DIS", "short-treks": "SHORT", "picard": "PIC", "lower-decks": "LD", "prodigy": "PRO",
    "strange-new-worlds": "SNW", "starfleet-academy": "SFA", "films": "FILMS", "literature": "LIT",
}


def canonical(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def sha256_canonical(value): return "sha256:" + hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()
def physical_path(path: Path) -> Path:
    match = re.match(r"^(.*\.jsonl):\d+$", str(path)); return Path(match.group(1)) if match else path


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


def load_schemas(): return {rt: json.loads((SCHEMA_ROOT / fn).read_text(encoding="utf-8")) for rt, fn in SCHEMA_FILES.items()}


def load_predicate_registry():
    registry = json.loads(PREDICATE_REGISTRY.read_text(encoding="utf-8"))
    entries = {}; errors = []
    if not registry.get("registry_version"): errors.append("predicate registry missing registry_version")
    if not registry.get("schema_version"): errors.append("predicate registry missing schema_version")
    for item in registry.get("predicates", []):
        missing = sorted(PREDICATE_METADATA_REQUIRED - set(item)); name = item.get("name")
        if not name: errors.append("predicate registry entry missing name"); continue
        if name in entries: errors.append(f"duplicate predicate registry entry {name}"); continue
        if missing: errors.append(f"predicate {name} missing metadata: {', '.join(missing)}")
        if item.get("status") not in {"CANDIDATE", "EXPERIMENTAL", "ACCEPTED", "DEPRECATED"}: errors.append(f"predicate {name} has invalid lifecycle status {item.get('status')!r}")
        if item.get("object_mode") not in {"LITERAL", "REFERENCE_ONLY", "LITERAL_OR_REFERENCE"}: errors.append(f"predicate {name} has invalid object_mode {item.get('object_mode')!r}")
        if not isinstance(item.get("subject_types"), list) or not item.get("subject_types"): errors.append(f"predicate {name} requires subject_types")
        if not isinstance(item.get("object_ref_types"), list): errors.append(f"predicate {name} requires object_ref_types array")
        if not isinstance(item.get("examples"), list) or not item.get("examples"): errors.append(f"predicate {name} requires a positive example")
        if not isinstance(item.get("near_miss"), str) or not item.get("near_miss", "").strip(): errors.append(f"predicate {name} requires near_miss")
        if not item.get("methodology_version") or not item.get("introduced_in_registry"): errors.append(f"predicate {name} requires methodology/registry provenance")
        if item.get("status") == "ACCEPTED" and item.get("projection_eligibility") != "ACCEPTED_ASSERTION_ALLOWED": errors.append(f"accepted predicate {name} must declare ACCEPTED_ASSERTION_ALLOWED")
        if item.get("status") == "EXPERIMENTAL" and item.get("projection_eligibility") != "EXPERIMENTAL_ONLY": errors.append(f"experimental predicate {name} must declare EXPERIMENTAL_ONLY")
        entries[name] = item
    for name, item in entries.items():
        inverse = item.get("inverse")
        if inverse and inverse not in entries: errors.append(f"predicate {name} inverse references unknown predicate {inverse}")
        predecessor = item.get("supersedes")
        successor = item.get("superseded_by")
        if predecessor and predecessor not in entries: errors.append(f"predicate {name} supersedes unknown predicate {predecessor}")
        if successor and successor not in entries: errors.append(f"predicate {name} superseded_by unknown predicate {successor}")
    return entries, errors


def load_scope_key_registry():
    registry = json.loads(SCOPE_KEY_REGISTRY.read_text(encoding="utf-8")); entries = {}; errors = []
    if not registry.get("registry_version"): errors.append("scope-key registry missing registry_version")
    if not registry.get("methodology_version"): errors.append("scope-key registry missing methodology_version")
    for item in registry.get("scope_keys", []):
        key = item.get("key")
        if not isinstance(key, str) or not key.strip(): errors.append("scope-key entry missing key"); continue
        if key in entries: errors.append(f"duplicate scope key {key}"); continue
        subject_types = item.get("subject_types")
        if not isinstance(subject_types, list) or not subject_types: errors.append(f"scope key {key} requires subject_types")
        elif any(value not in {"WORK", "LOCAL_ENTITY", "ASSERTION"} for value in subject_types): errors.append(f"scope key {key} has unsupported subject type")
        if not isinstance(item.get("definition"), str) or not item.get("definition", "").strip(): errors.append(f"scope key {key} requires definition")
        entries[key] = item
    return entries, errors


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
    errors = []; expected_type = schema.get("type")
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
    record_type = REFERENCE_TYPES.get(target_type, target_type.lower() if isinstance(target_type, str) else None)
    if record_type and target_id and target_id not in index.get(record_type, {}): errors.append(f"{path}: {field} references missing {target_type} {target_id}")


def typed_ref(value):
    if not isinstance(value, dict): return None
    if "ref_type" not in value and "ref_id" not in value: return None
    return value.get("ref_type"), value.get("ref_id")


def validate_predicate_assertion(path, assertion, registry, index, errors):
    name = assertion.get("predicate"); entry = registry.get(name)
    if entry is None: errors.append(f"{path}: assertion {assertion.get('assertion_id')} uses unregistered predicate {name}"); return
    lifecycle = entry.get("status"); record_status = assertion.get("status")
    if lifecycle == "CANDIDATE": errors.append(f"{path}: candidate predicate {name} may not be used in research records")
    elif lifecycle == "EXPERIMENTAL" and record_status != "PROPOSED": errors.append(f"{path}: experimental predicate {name} may only be used on PROPOSED assertions")
    elif lifecycle == "DEPRECATED": errors.append(f"{path}: deprecated predicate {name} may not be used for new assertion admission")
    if record_status == "ACCEPTED" and entry.get("projection_eligibility") != "ACCEPTED_ASSERTION_ALLOWED": errors.append(f"{path}: predicate {name} is not eligible for accepted assertion projection")
    subject_type = assertion.get("subject_type"); allowed_subjects = set(entry.get("subject_types", []))
    if "ANY" not in allowed_subjects and subject_type not in allowed_subjects: errors.append(f"{path}: predicate {name} does not allow subject_type {subject_type}")
    object_value = assertion.get("object"); ref = typed_ref(object_value); mode = entry.get("object_mode")
    if isinstance(object_value, dict) and ("ref_type" in object_value or "ref_id" in object_value) and set(object_value) != {"ref_type", "ref_id"}: errors.append(f"{path}: typed assertion object may contain only ref_type and ref_id")
    if mode == "REFERENCE_ONLY" and ref is None: errors.append(f"{path}: predicate {name} requires a typed object reference")
    if mode == "LITERAL" and ref is not None: errors.append(f"{path}: predicate {name} requires a literal object")
    if ref is not None:
        ref_type, ref_id = ref
        if not ref_type or not ref_id: errors.append(f"{path}: typed assertion object requires both ref_type and ref_id")
        elif ref_type not in REFERENCE_TYPES: errors.append(f"{path}: typed assertion object has unsupported ref_type {ref_type}")
        else:
            if ref_type not in set(entry.get("object_ref_types", [])): errors.append(f"{path}: predicate {name} does not allow object ref_type {ref_type}")
            add_missing_reference(errors, path, "object", ref_type, ref_id, index)


def validate_assertion_references(path, assertion, index, errors):
    subject_type = assertion.get("subject_type"); subject_id = assertion.get("subject")
    if subject_type in REFERENCE_TYPES: add_missing_reference(errors, path, "subject", subject_type, subject_id, index)
    evidence_ids = assertion.get("evidence", [])
    if len(evidence_ids) != len(set(evidence_ids)): errors.append(f"{path}: assertion evidence support set contains duplicates")
    for evidence_id in evidence_ids: add_missing_reference(errors, path, "evidence", "EVIDENCE", evidence_id, index)
    if assertion.get("supersedes"): add_missing_reference(errors, path, "supersedes", "ASSERTION", assertion["supersedes"], index)


def validate_references(records, index, errors):
    for path, record in records:
        rt = record.get("record_type")
        if rt == "source":
            for source_id in record.get("derived_from", []): add_missing_reference(errors, path, "derived_from", "SOURCE", source_id, index)
        elif rt == "work":
            if record.get("parent_work_id"): add_missing_reference(errors, path, "parent_work_id", "WORK", record["parent_work_id"], index)
        elif rt == "local_entity": add_missing_reference(errors, path, "work_id", "WORK", record.get("work_id"), index)
        elif rt == "evidence":
            add_missing_reference(errors, path, "source_id", "SOURCE", record.get("source_id"), index); add_missing_reference(errors, path, "work_id", "WORK", record.get("work_id"), index)
            if record.get("observer_local_entity_id"): add_missing_reference(errors, path, "observer_local_entity_id", "LOCAL_ENTITY", record["observer_local_entity_id"], index)
        elif rt == "assertion": validate_assertion_references(path, record, index, errors)
        elif rt == "reconciliation_decision":
            for evidence_id in record.get("evidence", []):
                if evidence_id not in index.get("evidence", {}) and evidence_id not in index.get("assertion", {}): errors.append(f"{path}: evidence references missing EVIDENCE/ASSERTION {evidence_id}")
            if record.get("supersedes"): add_missing_reference(errors, path, "supersedes", "RECONCILIATION_DECISION", record["supersedes"], index)
            subject_type = record.get("subject_type")
            if subject_type in REFERENCE_TYPES: add_missing_reference(errors, path, "subject", subject_type, record.get("subject_id"), index)


def batch_records_for(manifest_path: Path, records):
    batch_root = physical_path(manifest_path).parent; selected = []
    for path, record in records:
        if record.get("record_type") == "batch_manifest": continue
        try: physical_path(path).relative_to(batch_root)
        except ValueError: continue
        selected.append(record)
    return sorted(selected, key=canonical)


def compute_batch_hash(manifest, batch_records): return sha256_canonical({"manifest": {k: v for k, v in manifest.items() if k != "batch_hash"}, "records": batch_records})


def research_lane_for_path(path: Path):
    physical = physical_path(path)
    for root in DATA_ROOTS:
        if root.name != "research": continue
        try: relative = physical.relative_to(root)
        except ValueError: continue
        if relative.parts and relative.parts[0] in RESEARCH_WORKERS: return relative.parts[0]
    return None


def expected_worker_for_path(path: Path):
    lane = research_lane_for_path(path); return RESEARCH_WORKERS.get(lane) if lane else None


def validate_partition_ownership(records, errors):
    for path, record in records:
        lane = research_lane_for_path(path)
        if lane and record.get("record_type") in WORKER_FORBIDDEN_RECORD_TYPES: errors.append(f"{path}: authoritative {record.get('record_type')} record is not allowed under worker research partition {lane}")


def validate_batch_integrity(records, index, errors):
    known_source_hashes = {r.get("content_hash") for r in index.get("source", {}).values() if r.get("content_hash")}
    for path, manifest in records:
        if manifest.get("record_type") != "batch_manifest": continue
        batch_records = batch_records_for(path, records); expected_hash = compute_batch_hash(manifest, batch_records)
        if manifest.get("batch_hash") != expected_hash: errors.append(f"{path}: batch_hash mismatch: declared {manifest.get('batch_hash')}, expected {expected_hash}")
        actual_counts = {}
        for record in batch_records: rt = record.get("record_type"); actual_counts[rt] = actual_counts.get(rt, 0) + 1
        declared_counts = manifest.get("record_counts", {})
        for required_key in REQUIRED_BATCH_COUNTS:
            if required_key not in declared_counts: errors.append(f"{path}: record_counts.{required_key} is required for a governed research batch")
        for key, record_type in COUNT_KEYS.items():
            if key in declared_counts and declared_counts[key] != actual_counts.get(record_type, 0): errors.append(f"{path}: record_counts.{key}={declared_counts[key]} but batch contains {actual_counts.get(record_type, 0)}")
        for work_id in manifest.get("works", []): add_missing_reference(errors, path, "works", "WORK", work_id, index)
        for source_hash in manifest.get("source_hashes", []):
            if source_hash not in known_source_hashes: errors.append(f"{path}: source_hashes references unknown source content_hash {source_hash}")
        expected_worker = expected_worker_for_path(path)
        if expected_worker and manifest.get("worker_id") != expected_worker: errors.append(f"{path}: worker_id {manifest.get('worker_id')} does not match research partition owner {expected_worker}")


def validate_payload(path, decision, registry, scope_keys, index, errors):
    dtype = decision.get("decision_type"); payload = decision.get("payload") or {}; status = decision.get("status"); subject_type = decision.get("subject_type")
    if dtype == "ENTITY_LINK":
        if subject_type != "LOCAL_ENTITY": errors.append(f"{path}: ENTITY_LINK requires subject_type LOCAL_ENTITY")
        required = {"relation_predicate", "target_type", "target_id"}; missing = sorted(required - set(payload))
        if missing: errors.append(f"{path}: ENTITY_LINK payload missing {', '.join(missing)}"); return
        if set(payload) != required: errors.append(f"{path}: ENTITY_LINK payload may contain only {', '.join(sorted(required))}")
        if payload.get("target_type") != "LOCAL_ENTITY": errors.append(f"{path}: ENTITY_LINK target_type must be LOCAL_ENTITY until a global-entity schema is governed")
        predicate = registry.get(payload.get("relation_predicate"))
        if predicate is None: errors.append(f"{path}: ENTITY_LINK uses unregistered relation predicate {payload.get('relation_predicate')}"); return
        if predicate.get("semantic_class") != "IDENTITY_RELATION": errors.append(f"{path}: ENTITY_LINK predicate {predicate.get('name')} is not governed as IDENTITY_RELATION")
        if status == "ACCEPTED" and predicate.get("status") != "ACCEPTED": errors.append(f"{path}: accepted ENTITY_LINK may not use {predicate.get('status')} predicate {predicate.get('name')}")
        if status == "PROPOSED" and predicate.get("status") not in {"ACCEPTED", "EXPERIMENTAL"}: errors.append(f"{path}: proposed ENTITY_LINK may not use {predicate.get('status')} predicate {predicate.get('name')}")
        if subject_type not in set(predicate.get("subject_types", [])): errors.append(f"{path}: identity predicate {predicate.get('name')} does not allow subject_type {subject_type}")
        target_type = payload.get("target_type")
        if target_type not in set(predicate.get("object_ref_types", [])): errors.append(f"{path}: identity predicate {predicate.get('name')} does not allow target_type {target_type}")
        if target_type in REFERENCE_TYPES: add_missing_reference(errors, path, "payload.target_id", target_type, payload.get("target_id"), index)
    elif dtype == "ASSERTION_DISPOSITION":
        if subject_type != "ASSERTION": errors.append(f"{path}: ASSERTION_DISPOSITION requires subject_type ASSERTION")
        if set(payload) != {"disposition"} or payload.get("disposition") not in DISPOSITIONS: errors.append(f"{path}: ASSERTION_DISPOSITION payload must contain only disposition in {sorted(DISPOSITIONS)}")
    elif dtype == "ASSERTION_PROJECTION_STATUS":
        if subject_type != "ASSERTION": errors.append(f"{path}: ASSERTION_PROJECTION_STATUS requires subject_type ASSERTION")
        if set(payload) != {"projection_status"} or payload.get("projection_status") not in PROJECTION_STATUSES: errors.append(f"{path}: ASSERTION_PROJECTION_STATUS payload must contain only a governed projection_status")
    elif dtype == "SCOPE_RESOLUTION":
        if subject_type not in {"ASSERTION", "WORK", "LOCAL_ENTITY"}: errors.append(f"{path}: SCOPE_RESOLUTION subject_type must be ASSERTION, WORK, or LOCAL_ENTITY")
        if set(payload) != {"resolution_key", "resolution"} or not isinstance(payload.get("resolution_key"), str) or not payload.get("resolution_key").strip(): errors.append(f"{path}: SCOPE_RESOLUTION payload requires non-empty resolution_key and resolution")
        else:
            key = payload.get("resolution_key"); entry = scope_keys.get(key)
            if entry is None: errors.append(f"{path}: SCOPE_RESOLUTION uses ungoverned resolution_key {key}")
            elif subject_type not in set(entry.get("subject_types", [])): errors.append(f"{path}: scope key {key} does not allow subject_type {subject_type}")
    elif dtype == "OTHER":
        if status == "ACCEPTED": errors.append(f"{path}: OTHER reconciliation decisions are proposal/staging only and may not be ACCEPTED")


def decision_active_key(decision):
    dtype = decision.get("decision_type"); base = (dtype, decision.get("subject_type"), decision.get("subject_id")); payload = decision.get("payload") or {}
    if dtype == "ENTITY_LINK": return base + (payload.get("relation_predicate"),)
    if dtype == "SCOPE_RESOLUTION": return base + (payload.get("resolution_key"),)
    if dtype in {"ASSERTION_DISPOSITION", "ASSERTION_PROJECTION_STATUS"}: return base
    return None


def validate_assertion_lineage(index, errors):
    assertions = index.get("assertion", {})
    for start in assertions:
        seen = set(); current = start
        while current:
            if current in seen: errors.append(f"assertion: supersession cycle detected at {current}"); break
            seen.add(current); record = assertions.get(current); current = record.get("supersedes") if record else None


def validate_reconciliation_integrity(index, registry, scope_keys, errors):
    decisions = index.get("reconciliation_decision", {}); accepted = [d for d in decisions.values() if d.get("status") == "ACCEPTED"]
    for decision_id, decision in decisions.items():
        validate_payload(f"reconciliation:{decision_id}", decision, registry, scope_keys, index, errors)
        predecessor_id = decision.get("supersedes")
        if not predecessor_id: continue
        reason = decision.get("reason")
        if decision.get("status") == "ACCEPTED" and (not isinstance(reason, str) or not reason.strip()): errors.append(f"reconciliation: superseding accepted decision {decision_id} requires non-empty reason")
        predecessor = decisions.get(predecessor_id)
        if predecessor and decision_active_key(predecessor) != decision_active_key(decision): errors.append(f"reconciliation: {decision_id} supersedes predecessor with different active key {predecessor_id}")
    for start in decisions:
        seen = set(); current = start
        while current:
            if current in seen: errors.append(f"reconciliation: supersession cycle detected at {current}"); break
            seen.add(current); record = decisions.get(current); current = record.get("supersedes") if record else None
    superseded_ids = {d.get("supersedes") for d in accepted if d.get("supersedes")}; active = [d for d in accepted if d.get("decision_id") not in superseded_ids]
    groups = {}
    for decision in active:
        key = decision_active_key(decision)
        if key is not None: groups.setdefault(key, []).append(decision.get("decision_id"))
    for key, ids in sorted(groups.items(), key=lambda item: repr(item[0])):
        if len(ids) > 1: errors.append(f"reconciliation: multiple active decisions for key {key}: {', '.join(sorted(ids))}")
    dispositions = {d.get("subject_id"): d for d in active if d.get("decision_type") == "ASSERTION_DISPOSITION" and d.get("subject_type") == "ASSERTION"}
    superseded_assertions = {a.get("supersedes") for a in index.get("assertion", {}).values() if a.get("supersedes")}
    for decision in active:
        if decision.get("decision_type") != "ASSERTION_PROJECTION_STATUS" or decision.get("subject_type") != "ASSERTION": continue
        assertion_id = decision.get("subject_id"); assertion = index.get("assertion", {}).get(assertion_id)
        if not assertion: continue
        effective = assertion.get("status")
        override = dispositions.get(assertion_id)
        if override: effective = (override.get("payload") or {}).get("disposition")
        if assertion_id in superseded_assertions: effective = "SUPERSEDED"
        if effective != "ACCEPTED": errors.append(f"reconciliation:{decision.get('decision_id')}: projection-status decision targets effectively {effective} assertion {assertion_id}")


def main() -> int:
    seen = {}; index = {record_type: {} for record_type in ID_FIELDS}; errors = []; schemas = load_schemas(); registry, registry_errors = load_predicate_registry(); scope_keys, scope_errors = load_scope_key_registry(); errors.extend(registry_errors); errors.extend(scope_errors)
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
    validate_partition_ownership(records, errors); validate_references(records, index, errors)
    for path, record in records:
        if record.get("record_type") == "assertion": validate_predicate_assertion(path, record, registry, index, errors)
    validate_assertion_lineage(index, errors); validate_batch_integrity(records, index, errors); validate_reconciliation_integrity(index, registry, scope_keys, errors)
    if errors: print("VALIDATION FAILED"); print("\n".join(f"- {e}" for e in errors)); return 1
    print(f"VALIDATION PASSED: {len(seen)} identified records"); return 0


if __name__ == "__main__": sys.exit(main())
