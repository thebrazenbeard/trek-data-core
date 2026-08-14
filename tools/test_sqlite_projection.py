#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("build_sqlite.py")
spec = importlib.util.spec_from_file_location("trek_build_sqlite", MODULE_PATH)
sqlite_projection = importlib.util.module_from_spec(spec)
if spec.loader is not None:
    spec.loader.exec_module(sqlite_projection)


def write_jsonl(root, filename, rows):
    (root / filename).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def write_projection(root, projection_hash="sha256:projection-a"):
    manifest = {
        "record_type": "projection_manifest",
        "projection_version": "0.1.0",
        "schema_version": "0.1.0",
        "methodology_version": "0.1.0",
        "compiler_commit": "fixture",
        "research_head": "research-fixture",
        "reconciliation_head": "recon-fixture",
        "predicate_registry_hash": "sha256:predicate",
        "input_hash": "sha256:input",
        "projection_hash": projection_hash,
        "outputs": {},
    }
    (root / "manifest.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")
    write_jsonl(root, "entities.jsonl", [
        {"record_type": "local_entity", "local_entity_id": "local-1", "work_id": "work-1", "label": "Fixture", "resolved_entity": "global:one", "reconciliation_decision_id": "link-1"},
    ])
    write_jsonl(root, "facts.jsonl", [
        {"record_type": "assertion", "assertion_id": "a-stable", "subject": "local-1", "resolved_subject": "global:one", "predicate": "CLAIMS", "object": {"value": "stable"}, "projection_status": "STABLE", "scope": {"continuity": "prime"}},
    ])
    write_jsonl(root, "contested.jsonl", [
        {"record_type": "assertion", "assertion_id": "a-paradox", "subject": "local-1", "predicate": "CLAIMS", "object": {"value": "paradox"}, "projection_status": "STRUCTURAL_PARADOX"},
    ])
    write_jsonl(root, "unresolved.jsonl", [
        {"record_type": "assertion", "assertion_id": "a-unresolved", "subject": "local-1", "predicate": "CLAIMS", "object": {"value": "unknown"}, "projection_status": "UNRESOLVED", "projection_reason": "MISSING_PROJECTION_STATUS"},
    ])
    write_jsonl(root, "relations.jsonl", [])
    write_jsonl(root, "provenance.jsonl", [
        {"provenance_id": "a-stable::e1", "assertion_id": "a-stable", "evidence_id": "e1", "source_id": "source-1", "work_id": "work-1", "evidence_kind": "depiction", "source_content_hash": "sha256:source"},
    ])
    write_jsonl(root, "accepted_reconciliation.jsonl", [
        {"record_type": "reconciliation_decision", "decision_id": "link-1", "decision_type": "ENTITY_LINK", "subject_id": "local-1", "value": "global:one", "status": "ACCEPTED", "evidence": ["e1"], "method": "fixture"},
    ])


class SQLiteProjectionTests(unittest.TestCase):
    def test_database_pins_logical_projection_hash_and_partitions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "projection"; root.mkdir()
            db = Path(td) / "query.db"
            write_projection(root)
            sqlite_projection.build_database(root, db)
            with sqlite3.connect(db) as con:
                self.assertEqual(con.execute("select value from metadata where key='projection_hash'").fetchone()[0], "sha256:projection-a")
                rows = con.execute("select assertion_id, projection_status, partition from assertions order by assertion_id").fetchall()
                self.assertEqual(rows, [
                    ("a-paradox", "STRUCTURAL_PARADOX", "contested"),
                    ("a-stable", "STABLE", "facts"),
                    ("a-unresolved", "UNRESOLVED", "unresolved"),
                ])

    def test_structural_paradox_remains_structural_paradox(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "projection"; root.mkdir(); db = Path(td) / "query.db"
            write_projection(root)
            sqlite_projection.build_database(root, db)
            with sqlite3.connect(db) as con:
                row = con.execute("select projection_status, partition from assertions where assertion_id='a-paradox'").fetchone()
                self.assertEqual(row, ("STRUCTURAL_PARADOX", "contested"))

    def test_rebuild_is_query_deterministic_not_byte_hash_based(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "projection"; root.mkdir()
            first = Path(td) / "first.db"; second = Path(td) / "second.db"
            write_projection(root)
            sqlite_projection.build_database(root, first)
            sqlite_projection.build_database(root, second)
            self.assertEqual(sqlite_projection.query_snapshot(first), sqlite_projection.query_snapshot(second))
            self.assertEqual(sqlite_projection.query_snapshot(first)["projection_hash"], "sha256:projection-a")

    def test_rebuild_replaces_prior_database_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "projection"; root.mkdir(); db = Path(td) / "query.db"
            write_projection(root, "sha256:projection-a")
            sqlite_projection.build_database(root, db)
            write_projection(root, "sha256:projection-b")
            sqlite_projection.build_database(root, db)
            with sqlite3.connect(db) as con:
                self.assertEqual(con.execute("select value from metadata where key='projection_hash'").fetchone()[0], "sha256:projection-b")
                self.assertEqual(con.execute("select count(*) from assertions").fetchone()[0], 3)


if __name__ == "__main__":
    unittest.main()
