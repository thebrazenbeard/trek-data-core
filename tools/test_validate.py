#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("validate.py")
spec = importlib.util.spec_from_file_location("trek_validate", MODULE_PATH)
validate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate)

VALID_BATCH_HASH = "sha256:0fcdb523d4915ff92673fd3492b1f23876088f1b9e610d16959713a035f7afd2"
TOS_NAMED_BATCH_HASH = "sha256:2a799c7ea7f595858bcd2cf50c6635118f08dc2cb53e2c919148577388bfdf0a"
MISSING_ASSERTION_COUNT_HASH = "sha256:c0d39b7e8189ef573556da8eec328a1a7796e84f7866bf44edfeba2b602de216"
ILLEGAL_SOURCE_WORK_BATCH_HASH = "sha256:40ca469fdf56fab55a88717f6f5098199ecf3951ca9ed212dc3d34dde83019e0"


class ValidationTests(unittest.TestCase):
    def run_research_root(self, research):
        old_roots = validate.DATA_ROOTS
        validate.DATA_ROOTS = [research]
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                rc = validate.main()
        finally:
            validate.DATA_ROOTS = old_roots
        return rc, stdout.getvalue()

    def run_records(self, records):
        with tempfile.TemporaryDirectory() as td:
            research = Path(td) / "research"
            research.mkdir()
            (research / "records.jsonl").write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
            return self.run_research_root(research)

    def write_batch_fixture(self, research, batch_hash, worker_id="TNG", record_counts=None, source_work_in_batch=False):
        source_work = [
            {"record_type": "source", "source_id": "source-1", "source_kind": "transcript", "locator": "fixture://source-1", "content_hash": "sha256:source"},
            {"record_type": "work", "work_id": "work-1", "title": "Fixture Work", "medium": "test"},
        ]
        worker_records = [
            {"record_type": "local_entity", "local_entity_id": "local-1", "work_id": "work-1", "label": "Fixture Entity"},
            {"record_type": "evidence", "evidence_id": "evidence-1", "source_id": "source-1", "work_id": "work-1", "evidence_kind": "depiction", "locator": {"line": 1}, "observed": {"event": "fixture"}},
            {"record_type": "assertion", "assertion_id": "assertion-1", "subject": "local-1", "predicate": "CLAIMS", "object": "x", "evidence": ["evidence-1"], "status": "ACCEPTED"},
        ]
        batch = research / "tng" / "batches" / "batch-1"
        batch.mkdir(parents=True)
        if source_work_in_batch:
            batch_records = source_work + worker_records
            default_counts = {"sources": 1, "works": 1, "local_entities": 1, "evidence": 1, "assertions": 1}
        else:
            registry = research / "_registry"
            registry.mkdir(parents=True)
            (registry / "records.jsonl").write_text("".join(json.dumps(record) + "\n" for record in source_work), encoding="utf-8")
            batch_records = worker_records
            default_counts = {"local_entities": 1, "evidence": 1, "assertions": 1}
        (batch / "records.jsonl").write_text("".join(json.dumps(record) + "\n" for record in batch_records), encoding="utf-8")
        if record_counts is None:
            record_counts = default_counts
        manifest = {
            "record_type": "batch_manifest", "batch_id": "batch-1", "schema_version": "0.1.0",
            "worker_id": worker_id, "works": ["work-1"], "source_hashes": ["sha256:source"],
            "record_counts": record_counts, "batch_hash": batch_hash,
        }
        (batch / "manifest.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")

    def test_schema_invalid_source_is_rejected(self):
        rc, output = self.run_records([{"record_type": "source", "source_id": "source-1", "source_kind": "transcript"}])
        self.assertEqual(rc, 1); self.assertIn("locator", output)

    def test_dangling_assertion_evidence_reference_is_rejected(self):
        rc, output = self.run_records([{"record_type": "assertion", "assertion_id": "assertion-1", "subject": "local-1", "predicate": "CLAIMS", "object": "x", "evidence": ["evidence-missing"], "status": "ACCEPTED"}])
        self.assertEqual(rc, 1); self.assertIn("evidence-missing", output)

    def test_unregistered_predicate_is_rejected(self):
        rc, output = self.run_records([
            {"record_type": "source", "source_id": "source-1", "source_kind": "transcript", "locator": "fixture://source-1"},
            {"record_type": "work", "work_id": "work-1", "title": "Fixture Work", "medium": "test"},
            {"record_type": "evidence", "evidence_id": "evidence-1", "source_id": "source-1", "work_id": "work-1", "evidence_kind": "depiction", "locator": {"line": 1}, "observed": {"event": "fixture"}},
            {"record_type": "assertion", "assertion_id": "assertion-1", "subject": "local-1", "predicate": "NOT_REGISTERED", "object": "x", "evidence": ["evidence-1"], "status": "ACCEPTED"},
        ])
        self.assertEqual(rc, 1); self.assertIn("NOT_REGISTERED", output)

    def test_batch_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            research = Path(td) / "research"; self.write_batch_fixture(research, "sha256:wrong")
            rc, output = self.run_research_root(research)
            self.assertEqual(rc, 1); self.assertIn("batch_hash", output)

    def test_canonical_batch_hash_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            research = Path(td) / "research"; self.write_batch_fixture(research, VALID_BATCH_HASH)
            rc, output = self.run_research_root(research)
            self.assertEqual(rc, 0, output)

    def test_worker_id_must_match_research_partition(self):
        with tempfile.TemporaryDirectory() as td:
            research = Path(td) / "research"; self.write_batch_fixture(research, TOS_NAMED_BATCH_HASH, worker_id="TOS")
            rc, output = self.run_research_root(research)
            self.assertEqual(rc, 1); self.assertIn("worker_id", output); self.assertIn("TNG", output)

    def test_core_batch_count_keys_are_required(self):
        with tempfile.TemporaryDirectory() as td:
            research = Path(td) / "research"
            self.write_batch_fixture(research, MISSING_ASSERTION_COUNT_HASH, record_counts={"local_entities": 1, "evidence": 1})
            rc, output = self.run_research_root(research)
            self.assertEqual(rc, 1); self.assertIn("record_counts.assertions", output)

    def test_untyped_json_in_governed_data_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            research = Path(td) / "research"
            artifact = research / "tng" / "coverage_update.json"
            artifact.parent.mkdir(parents=True)
            artifact.write_text(json.dumps({"coverage": "SEMANTICALLY_ANALYZED"}) + "\n", encoding="utf-8")
            rc, output = self.run_research_root(research)
            self.assertEqual(rc, 1); self.assertIn("missing record_type", output); self.assertIn("coverage_update.json", output)

    def test_worker_batch_cannot_own_source_or_work_records(self):
        with tempfile.TemporaryDirectory() as td:
            research = Path(td) / "research"
            self.write_batch_fixture(research, ILLEGAL_SOURCE_WORK_BATCH_HASH, source_work_in_batch=True)
            rc, output = self.run_research_root(research)
            self.assertEqual(rc, 1)
            self.assertIn("Librarian-owned", output)
            self.assertIn("source", output)
            self.assertIn("work", output)


if __name__ == "__main__":
    unittest.main()
