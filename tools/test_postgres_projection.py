#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("build_postgres.py")
spec = importlib.util.spec_from_file_location("trek_build_postgres", MODULE_PATH)
postgres_projection = importlib.util.module_from_spec(spec)
if spec.loader is not None:
    spec.loader.exec_module(postgres_projection)


def write_jsonl(root, filename, rows):
    (root / filename).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def write_projection(root):
    (root / "manifest.json").write_text(json.dumps({
        "record_type": "projection_manifest",
        "projection_version": "0.1.0",
        "schema_version": "0.1.0",
        "methodology_version": "0.1.0",
        "compiler_commit": "fixture",
        "research_head": "research-fixture",
        "reconciliation_head": "recon-fixture",
        "predicate_registry_hash": "sha256:predicate",
        "input_hash": "sha256:input",
        "projection_hash": "sha256:projection-fixture",
        "outputs": {},
    }) + "\n", encoding="utf-8")
    write_jsonl(root, "entities.jsonl", [
        {"record_type": "local_entity", "local_entity_id": "local-1", "work_id": "work-1", "label": "O'Brien", "resolved_entity": "global:one"},
    ])
    write_jsonl(root, "facts.jsonl", [
        {"record_type": "assertion", "assertion_id": "a1", "subject": "local-1", "predicate": "CLAIMS", "object": {"text": "It's a fixture"}, "projection_status": "STABLE"},
    ])
    write_jsonl(root, "contested.jsonl", [
        {"record_type": "assertion", "assertion_id": "a2", "subject": "local-1", "predicate": "CLAIMS", "object": {"text": "paradox"}, "projection_status": "STRUCTURAL_PARADOX"},
    ])
    write_jsonl(root, "unresolved.jsonl", [])
    write_jsonl(root, "relations.jsonl", [])
    write_jsonl(root, "provenance.jsonl", [
        {"provenance_id": "a1::e1", "assertion_id": "a1", "evidence_id": "e1", "source_id": "source-1", "work_id": "work-1", "evidence_kind": "dialogue", "source_content_hash": "sha256:source"},
    ])
    write_jsonl(root, "accepted_reconciliation.jsonl", [])


class PostgresProjectionTests(unittest.TestCase):
    def test_generated_sql_is_deterministic_and_projection_pinned(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "projection"; root.mkdir(); write_projection(root)
            first = postgres_projection.generate_sql(root)
            second = postgres_projection.generate_sql(root)
            self.assertEqual(first, second)
            self.assertIn("sha256:projection-fixture", first)
            self.assertIn("CREATE SCHEMA trek_projection_v0_1", first)

    def test_generated_sql_preserves_projection_states_and_partitions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "projection"; root.mkdir(); write_projection(root)
            sql = postgres_projection.generate_sql(root)
            self.assertIn("STRUCTURAL_PARADOX", sql)
            self.assertIn("'contested'", sql)
            self.assertIn("'facts'", sql)

    def test_sql_literal_escaping_is_safe_and_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "projection"; root.mkdir(); write_projection(root)
            sql = postgres_projection.generate_sql(root)
            self.assertIn("O''Brien", sql)
            self.assertIn("It''s a fixture", sql)

    def test_bundle_manifest_hashes_generated_sql_not_database_storage(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "projection"; root.mkdir(); write_projection(root)
            out = Path(td) / "bundle"
            manifest = postgres_projection.write_bundle(root, out)
            self.assertEqual(manifest["projection_hash"], "sha256:projection-fixture")
            self.assertTrue(manifest["sql_hash"].startswith("sha256:"))
            self.assertEqual((out / "projection.sql").read_text(encoding="utf-8"), postgres_projection.generate_sql(root))


if __name__ == "__main__":
    unittest.main()
