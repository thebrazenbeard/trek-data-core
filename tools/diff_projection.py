#!/usr/bin/env python3
"""Semantically diff canonical logical projections by stable record identity."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ASSERTION_FILES = ("facts.jsonl", "contested.jsonl", "unresolved.jsonl")
CONFLICT_STATUSES = {"CONTESTED", "STRUCTURAL_PARADOX"}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_rows(path: Path):
    if not path.exists():
        return []
    return [json.loads(raw) for raw in path.read_text(encoding="utf-8").splitlines() if raw.strip()]


def load_index(path: Path, key: str):
    indexed = {}
    for row in load_rows(path):
        rid = str(row.get(key, ""))
        if not rid:
            raise ValueError(f"{path}: row missing {key}")
        if rid in indexed:
            raise ValueError(f"{path}: duplicate {key} {rid}")
        indexed[rid] = row
    return indexed


def load_assertions(root: Path):
    indexed = {}
    for filename in ASSERTION_FILES:
        for assertion_id, row in load_index(root / filename, "assertion_id").items():
            if assertion_id in indexed:
                raise ValueError(f"{root}: assertion {assertion_id} appears in multiple projection partitions")
            indexed[assertion_id] = row
    return indexed


def load_provenance(root: Path):
    grouped = {}
    for row in load_rows(root / "provenance.jsonl"):
        assertion_id = str(row.get("assertion_id", ""))
        if not assertion_id:
            raise ValueError(f"{root / 'provenance.jsonl'}: row missing assertion_id")
        grouped.setdefault(assertion_id, []).append(row)
    return {assertion_id: sorted(rows, key=canonical) for assertion_id, rows in grouped.items()}


def change(change_class, record_type, record_id, **details):
    row = {"class": change_class, "record_type": record_type, "record_id": record_id}
    if details:
        row["details"] = details
    return row


def semantic_diff(old_root: Path, new_root: Path):
    old_root, new_root = Path(old_root), Path(new_root)
    changes = []

    old_assertions = load_assertions(old_root)
    new_assertions = load_assertions(new_root)

    for assertion_id in sorted(new_assertions.keys() - old_assertions.keys()):
        changes.append(change("ADDED_FACT", "assertion", assertion_id))
    for assertion_id in sorted(old_assertions.keys() - new_assertions.keys()):
        changes.append(change("REMOVED_FACT", "assertion", assertion_id))

    for assertion_id in sorted(old_assertions.keys() & new_assertions.keys()):
        old = old_assertions[assertion_id]
        new = new_assertions[assertion_id]
        old_status = old.get("projection_status")
        new_status = new.get("projection_status")

        if old_status != new_status:
            if new_status == "STABLE" and old_status != "STABLE":
                changes.append(change("STATUS_PROMOTED", "assertion", assertion_id, old_status=old_status, new_status=new_status))
            elif old_status == "STABLE" and new_status != "STABLE":
                changes.append(change("STATUS_DEMOTED", "assertion", assertion_id, old_status=old_status, new_status=new_status))
            else:
                changes.append(change("VALUE_CHANGED", "assertion", assertion_id, fields=["projection_status"], old_status=old_status, new_status=new_status))

            old_conflict = old_status in CONFLICT_STATUSES
            new_conflict = new_status in CONFLICT_STATUSES
            if not old_conflict and new_conflict:
                changes.append(change("CONFLICT_INTRODUCED", "assertion", assertion_id, old_status=old_status, new_status=new_status))
            elif old_conflict and not new_conflict:
                changes.append(change("CONFLICT_RESOLVED", "assertion", assertion_id, old_status=old_status, new_status=new_status))

        value_fields = [field for field in ("subject", "predicate", "object") if old.get(field) != new.get(field)]
        if value_fields:
            changes.append(change("VALUE_CHANGED", "assertion", assertion_id, fields=value_fields))

        if old.get("resolved_subject") != new.get("resolved_subject"):
            changes.append(change(
                "ENTITY_LINK_CHANGED",
                "assertion",
                assertion_id,
                old_resolved_subject=old.get("resolved_subject"),
                new_resolved_subject=new.get("resolved_subject"),
            ))

        if old.get("scope") != new.get("scope") or old.get("resolved_scope") != new.get("resolved_scope"):
            changes.append(change("SCOPE_CHANGED", "assertion", assertion_id))

    old_entities = load_index(old_root / "entities.jsonl", "local_entity_id")
    new_entities = load_index(new_root / "entities.jsonl", "local_entity_id")
    for entity_id in sorted(old_entities.keys() & new_entities.keys()):
        old_link = old_entities[entity_id].get("resolved_entity")
        new_link = new_entities[entity_id].get("resolved_entity")
        if old_link != new_link:
            changes.append(change("ENTITY_LINK_CHANGED", "local_entity", entity_id, old_resolved_entity=old_link, new_resolved_entity=new_link))

    old_provenance = load_provenance(old_root)
    new_provenance = load_provenance(new_root)
    for assertion_id in sorted(old_provenance.keys() & new_provenance.keys()):
        if canonical(old_provenance[assertion_id]) != canonical(new_provenance[assertion_id]):
            changes.append(change("PROVENANCE_CHANGED", "assertion", assertion_id))

    # Accepted reconciliation history remains part of the canonical projection even when
    # a history-only decision has no executable projection effect.
    old_reconciliation = load_index(old_root / "accepted_reconciliation.jsonl", "decision_id")
    new_reconciliation = load_index(new_root / "accepted_reconciliation.jsonl", "decision_id")
    for decision_id in sorted(new_reconciliation.keys() - old_reconciliation.keys()):
        changes.append(change("VALUE_CHANGED", "reconciliation_decision", decision_id, operation="ADDED_HISTORY"))
    for decision_id in sorted(old_reconciliation.keys() - new_reconciliation.keys()):
        changes.append(change("VALUE_CHANGED", "reconciliation_decision", decision_id, operation="REMOVED_HISTORY"))
    for decision_id in sorted(old_reconciliation.keys() & new_reconciliation.keys()):
        if old_reconciliation[decision_id] != new_reconciliation[decision_id]:
            changes.append(change("VALUE_CHANGED", "reconciliation_decision", decision_id, operation="HISTORY_RECORD_CHANGED"))

    return sorted(changes, key=lambda row: (row["record_type"], row["record_id"], row["class"], canonical(row.get("details", {}))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    args = ap.parse_args()
    changes = semantic_diff(Path(args.old), Path(args.new))
    for row in changes:
        print(canonical(row))
    print(f"changes={len(changes)}")


if __name__ == "__main__":
    main()
