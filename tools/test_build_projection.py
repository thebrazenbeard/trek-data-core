#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).with_name("build_projection.py")
spec = importlib.util.spec_from_file_location("trek_build_projection", MODULE_PATH)
projection = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(projection)


def fixture_records(source_hash="sha256:source-a", projection_status="STABLE"):
    assertion = {
        "record_type": "assertion",
        "assertion_id": "assertion-1",
        "subject": "local-1",
        "predicate": "CLAIMS",
        "object": {"value": "fixture"},
        "evidence": ["evidence-1"],
        "status": "ACCEPTED",
        "scope": {"continuity": "fixture"},
    }
    if projection_status is not None:
        assertion["projection_status"] = projection_status
    return [
        {"record_type": "source", "source_id": "source-1", "source_kind": "transcript", "locator": "fixture://source-1", "content_hash": source_hash},
        {"record_type": "work", "work_id": "work-1", "title": "Fixture Work", "medium": "test"},
        {"record_type": "local_entity", "local_entity_id": "local-1", "work_id": "work-1", "label": "Fixture Entity"},
        {"record_type": "evidence", "evidence_id": "evidence-1", "source_id": "source-1", "work_id": "work-1", "evidence_kind": "depiction", "locator": {"line": 1}, "observed": {"event": "fixture"}},
        assertion,
    ]


def decision(decision_id, decision_type, subject_id, value, supersedes=None):
    record = {
        "record_type": "reconciliation_decision",
        "decision_id": decision_id,
        "decision_type": decision_type,
        "subject_id": subject_id,
        "value": value,
        "status": "ACCEPTED",
        "evidence": ["evidence-1"],
        "method": "fixture",
    }
    if supersedes:
        record["supersedes"] = supersedes
        record["reason"] = "fixture correction"
    return record


def accepted_link(decision_id, value, supersedes=None):
    return decision(decision_id, "ENTITY_LINK", "local-1", value, supersedes=supersedes)


class LogicalProjectionTests(unittest.TestCase):
    def test_provenance_carries_source_hash_and_changes_with_source(self):
        first = projection.build_logical_projection(fixture_records("sha256:source-a"), [])
        second = projection.build_logical_projection(fixture_records("sha256:source-b"), [])
        self.assertEqual(first["provenance"][0]["source_content_hash"], "sha256:source-a")
        self.assertNotEqual(projection.canonical(first["provenance"]), projection.canonical(second["provenance"]))
        self.assertEqual(first["facts"], second["facts"])

    def test_entity_link_is_applied_without_mutating_worker_subject(self):
        result = projection.build_logical_projection(fixture_records(), [accepted_link("link-1", "global:fixture")])
        entity = result["entities"][0]
        fact = result["facts"][0]
        self.assertEqual(entity["local_entity_id"], "local-1")
        self.assertEqual(entity["resolved_entity"], "global:fixture")
        self.assertEqual(entity["reconciliation_decision_id"], "link-1")
        self.assertEqual(fact["subject"], "local-1")
        self.assertEqual(fact["resolved_subject"], "global:fixture")

    def test_missing_projection_status_fails_closed_to_unresolved(self):
        result = projection.build_logical_projection(fixture_records(projection_status=None), [])
        self.assertEqual(result["facts"], [])
        self.assertEqual(len(result["unresolved"]), 1)
        self.assertEqual(result["unresolved"][0]["projection_status"], "UNRESOLVED")
        self.assertEqual(result["unresolved"][0]["projection_reason"], "MISSING_PROJECTION_STATUS")

    def test_superseded_entity_link_is_not_applied(self):
        decisions = [accepted_link("link-1", "global:old"), accepted_link("link-2", "global:new", supersedes="link-1")]
        result = projection.build_logical_projection(fixture_records(), decisions)
        self.assertEqual(result["entities"][0]["resolved_entity"], "global:new")
        self.assertEqual(result["entities"][0]["reconciliation_decision_id"], "link-2")

    def test_assertion_status_reconciliation_controls_partition(self):
        decisions = [decision("status-1", "ASSERTION_STATUS", "assertion-1", "CONTESTED")]
        result = projection.build_logical_projection(fixture_records(projection_status="STABLE"), decisions)
        self.assertEqual(result["facts"], [])
        self.assertEqual(len(result["contested"]), 1)
        self.assertEqual(result["contested"][0]["projection_status"], "CONTESTED")
        self.assertEqual(result["contested"][0]["projection_status_decision_id"], "status-1")

    def test_scope_resolution_is_derived_without_rewriting_original_scope(self):
        resolved = {"continuity": "alternate", "timeline": "branch-a"}
        decisions = [decision("scope-1", "SCOPE_RESOLUTION", "assertion-1", resolved)]
        result = projection.build_logical_projection(fixture_records(), decisions)
        fact = result["facts"][0]
        self.assertEqual(fact["scope"], {"continuity": "fixture"})
        self.assertEqual(fact["resolved_scope"], resolved)
        self.assertEqual(fact["scope_resolution_decision_id"], "scope-1")

    def test_structural_paradox_is_preserved_as_contested_not_stable(self):
        result = projection.build_logical_projection(fixture_records(projection_status="STRUCTURAL_PARADOX"), [])
        self.assertEqual(result["facts"], [])
        self.assertEqual(result["unresolved"], [])
        self.assertEqual(result["contested"][0]["projection_status"], "STRUCTURAL_PARADOX")

    def test_multiple_other_decisions_for_same_subject_do_not_collide(self):
        decisions = [
            decision("other-1", "OTHER", "local-1", {"note": 1}),
            decision("other-2", "OTHER", "local-1", {"note": 2}),
        ]
        result = projection.build_logical_projection(fixture_records(), decisions)
        self.assertEqual(len(result["facts"]), 1)
        self.assertEqual(len(result["accepted_reconciliation"]), 2)

    def test_invalid_reconciled_projection_status_fails_closed(self):
        decisions = [decision("status-1", "ASSERTION_STATUS", "assertion-1", "CERTAIN_BECAUSE_COMPUTER")]
        with self.assertRaises(ValueError):
            projection.build_logical_projection(fixture_records(), decisions)


if __name__ == "__main__":
    unittest.main()
