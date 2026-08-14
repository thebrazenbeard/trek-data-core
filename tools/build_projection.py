#!/usr/bin/env python3
"""Deterministically compile accepted Git records into canonical logical projections."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREDICATE_REGISTRY = ROOT / "registry" / "predicates.json"
DATA_ROOTS = (ROOT / "research", ROOT / "external", ROOT / "migrations")
PROJECTION_STATUSES = {"STABLE", "CONTESTED", "UNRESOLVED", "STRUCTURAL_PARADOX"}


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_json_hash(path: Path) -> str:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return sha256_bytes(canonical(obj).encode("utf-8"))


def iter_typed_records(roots):
    """Read typed JSON/JSONL records deterministically; validation owns schema admission."""
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.json")):
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict) and obj.get("record_type"):
                yield obj
        for path in sorted(root.rglob("*.jsonl")):
            for raw in path.read_text(encoding="utf-8").splitlines():
                if not raw.strip():
                    continue
                obj = json.loads(raw)
                if not isinstance(obj, dict):
                    raise ValueError(f"{path}: JSONL record must be an object")
                if obj.get("record_type"):
                    yield obj


def index_unique(records, record_type, id_key):
    indexed = {}
    for record in records:
        if record.get("record_type") != record_type:
            continue
        rid = record.get(id_key)
        if not rid:
            continue
        if rid in indexed:
            raise ValueError(f"duplicate {record_type} id {rid}")
        indexed[rid] = record
    return indexed


def active_accepted_decisions(decisions):
    accepted = [d for d in decisions if d.get("record_type") == "reconciliation_decision" and d.get("status") == "ACCEPTED"]
    superseded = {d.get("supersedes") for d in accepted if d.get("supersedes")}
    return [d for d in accepted if d.get("decision_id") not in superseded]


def decision_index(decisions):
    indexed = {}
    for decision in active_accepted_decisions(decisions):
        decision_type = decision.get("decision_type")
        subject_id = decision.get("subject_id")
        key = (decision_type, subject_id)
        if key in indexed:
            raise ValueError(f"multiple active {decision_type} decisions for {subject_id}")
        indexed[key] = decision
    return indexed


def projection_status_for(assertion, decisions):
    decision = decisions.get(("ASSERTION_STATUS", assertion.get("assertion_id")))
    if decision is not None:
        value = decision.get("value")
        if value not in PROJECTION_STATUSES:
            raise ValueError(f"invalid reconciled projection status {value!r} for {assertion.get('assertion_id')}")
        return value, decision.get("decision_id"), "RECONCILIATION_DECISION"

    value = assertion.get("projection_status")
    if value is None:
        return "UNRESOLVED", None, "MISSING_PROJECTION_STATUS"
    if value not in PROJECTION_STATUSES:
        raise ValueError(f"invalid assertion projection status {value!r} for {assertion.get('assertion_id')}")
    return value, None, "ASSERTION"


def build_logical_projection(records, reconciliation_decisions):
    """Pure deterministic transform. No semantic inference is performed here."""
    records = [copy.deepcopy(record) for record in records]
    reconciliation_decisions = [copy.deepcopy(record) for record in reconciliation_decisions]

    sources = index_unique(records, "source", "source_id")
    works = index_unique(records, "work", "work_id")
    local_entities = index_unique(records, "local_entity", "local_entity_id")
    evidence = index_unique(records, "evidence", "evidence_id")
    assertions = index_unique(records, "assertion", "assertion_id")
    accepted_assertions = [record for record in assertions.values() if record.get("status") == "ACCEPTED"]
    decisions = decision_index(reconciliation_decisions)

    entity_links = {
        subject_id: decision
        for (decision_type, subject_id), decision in decisions.items()
        if decision_type == "ENTITY_LINK"
    }

    entities = []
    for local_id, entity in sorted(local_entities.items()):
        row = copy.deepcopy(entity)
        link = entity_links.get(local_id)
        if link is not None:
            row["resolved_entity"] = copy.deepcopy(link.get("value"))
            row["reconciliation_decision_id"] = link.get("decision_id")
        entities.append(row)

    facts = []
    contested = []
    unresolved = []
    provenance = []

    for assertion in sorted(accepted_assertions, key=lambda item: item.get("assertion_id", "")):
        row = copy.deepcopy(assertion)
        status, status_decision_id, status_reason = projection_status_for(assertion, decisions)
        row["projection_status"] = status
        if status_decision_id:
            row["projection_status_decision_id"] = status_decision_id
        if status_reason == "MISSING_PROJECTION_STATUS":
            row["projection_reason"] = status_reason

        link = entity_links.get(assertion.get("subject"))
        if link is not None:
            row["resolved_subject"] = copy.deepcopy(link.get("value"))
            row["entity_link_decision_id"] = link.get("decision_id")

        scope_decision = decisions.get(("SCOPE_RESOLUTION", assertion.get("assertion_id")))
        if scope_decision is not None:
            row["resolved_scope"] = copy.deepcopy(scope_decision.get("value"))
            row["scope_resolution_decision_id"] = scope_decision.get("decision_id")

        if status == "STABLE":
            facts.append(row)
        elif status in {"CONTESTED", "STRUCTURAL_PARADOX"}:
            contested.append(row)
        else:
            unresolved.append(row)

        for evidence_id in assertion.get("evidence", []):
            ev = evidence.get(evidence_id)
            provenance_row = {
                "provenance_id": f"{assertion.get('assertion_id')}::{evidence_id}",
                "assertion_id": assertion.get("assertion_id"),
                "evidence_id": evidence_id,
            }
            if ev is not None:
                provenance_row.update({
                    "source_id": ev.get("source_id"),
                    "work_id": ev.get("work_id"),
                    "evidence_kind": ev.get("evidence_kind"),
                    "evidence_locator": copy.deepcopy(ev.get("locator")),
                })
                source = sources.get(ev.get("source_id"))
                if source is not None:
                    provenance_row["source_content_hash"] = source.get("content_hash")
                    provenance_row["source_locator"] = copy.deepcopy(source.get("locator"))
                work = works.get(ev.get("work_id"))
                if work is not None:
                    provenance_row["work_title"] = work.get("title")
            else:
                provenance_row["provenance_state"] = "MISSING_EVIDENCE_RECORD"
            provenance.append(provenance_row)

    accepted_reconciliation = sorted(
        [copy.deepcopy(d) for d in reconciliation_decisions if d.get("record_type") == "reconciliation_decision" and d.get("status") == "ACCEPTED"],
        key=lambda item: item.get("decision_id", ""),
    )

    return {
        "entities": entities,
        "facts": facts,
        "relations": [],
        "contested": contested,
        "unresolved": unresolved,
        "provenance": sorted(provenance, key=lambda item: item.get("provenance_id", "")),
        "accepted_assertions": sorted([copy.deepcopy(a) for a in accepted_assertions], key=lambda item: item.get("assertion_id", "")),
        "accepted_reconciliation": accepted_reconciliation,
    }


def write_jsonl(path: Path, records, id_key: str):
    ordered = sorted(records, key=lambda r: (str(r.get(id_key, "")), canonical(r)))
    payload = "".join(canonical(r) + "\n" for r in ordered).encode("utf-8")
    path.write_bytes(payload)
    return sha256_bytes(payload), len(ordered)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--projection-version", default="0.1.0")
    ap.add_argument("--schema-version", required=True)
    ap.add_argument("--methodology-version", required=True)
    ap.add_argument("--research-head", required=True)
    ap.add_argument("--reconciliation-head", required=True)
    ap.add_argument("--compiler-commit", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    records = list(iter_typed_records(DATA_ROOTS))
    decisions = list(iter_typed_records((ROOT / "reconciliation",)))
    logical = build_logical_projection(records, decisions)

    output_specs = {
        "entities.jsonl": (logical["entities"], "local_entity_id"),
        "facts.jsonl": (logical["facts"], "assertion_id"),
        "relations.jsonl": (logical["relations"], "relation_id"),
        "contested.jsonl": (logical["contested"], "assertion_id"),
        "unresolved.jsonl": (logical["unresolved"], "assertion_id"),
        "provenance.jsonl": (logical["provenance"], "provenance_id"),
        "accepted_assertions.jsonl": (logical["accepted_assertions"], "assertion_id"),
        "accepted_reconciliation.jsonl": (logical["accepted_reconciliation"], "decision_id"),
    }

    outputs = {}
    for filename, (rows, id_key) in output_specs.items():
        row_hash, count = write_jsonl(out / filename, rows, id_key)
        outputs[filename] = {"hash": row_hash, "count": count}

    predicate_registry_hash = canonical_json_hash(PREDICATE_REGISTRY)
    logical_input_records = [
        record for record in records
        if record.get("record_type") in {"source", "work", "local_entity", "evidence"}
        or (record.get("record_type") == "assertion" and record.get("status") == "ACCEPTED")
    ]
    logical_input_hash = sha256_bytes(
        ("".join(canonical(record) + "\n" for record in sorted(logical_input_records, key=canonical))).encode("utf-8")
    )
    accepted_reconciliation_hash = outputs["accepted_reconciliation.jsonl"]["hash"]

    input_identity = {
        "research_head": args.research_head,
        "reconciliation_head": args.reconciliation_head,
        "schema_version": args.schema_version,
        "methodology_version": args.methodology_version,
        "predicate_registry_hash": predicate_registry_hash,
        "compiler_commit": args.compiler_commit,
        "logical_input_records_hash": logical_input_hash,
        "accepted_reconciliation_hash": accepted_reconciliation_hash,
    }
    input_hash = sha256_bytes(canonical(input_identity).encode("utf-8"))

    projection_material = canonical({filename: metadata["hash"] for filename, metadata in sorted(outputs.items())}).encode("utf-8")
    projection_hash = sha256_bytes(projection_material)

    manifest = {
        "record_type": "projection_manifest",
        "projection_version": args.projection_version,
        "schema_version": args.schema_version,
        "methodology_version": args.methodology_version,
        "compiler_commit": args.compiler_commit,
        "research_head": args.research_head,
        "reconciliation_head": args.reconciliation_head,
        "predicate_registry_hash": predicate_registry_hash,
        "input_hash": input_hash,
        "projection_hash": projection_hash,
        "outputs": outputs,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(projection_hash)


if __name__ == "__main__":
    main()
