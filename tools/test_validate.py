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


class ValidationTests(unittest.TestCase):
    def run_records(self, records):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            research = root / "research"
            research.mkdir()
            (research / "records.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in records),
                encoding="utf-8",
            )
            old_roots = validate.DATA_ROOTS
            validate.DATA_ROOTS = [research]
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    rc = validate.main()
            finally:
                validate.DATA_ROOTS = old_roots
            return rc, stdout.getvalue()

    def test_schema_invalid_source_is_rejected(self):
        rc, output = self.run_records([
            {
                "record_type": "source",
                "source_id": "source-1",
                "source_kind": "transcript"
            }
        ])
        self.assertEqual(rc, 1)
        self.assertIn("locator", output)

    def test_dangling_assertion_evidence_reference_is_rejected(self):
        rc, output = self.run_records([
            {
                "record_type": "assertion",
                "assertion_id": "assertion-1",
                "subject": "local-1",
                "predicate": "CLAIMS",
                "object": "x",
                "evidence": ["evidence-missing"],
                "status": "ACCEPTED"
            }
        ])
        self.assertEqual(rc, 1)
        self.assertIn("evidence-missing", output)

    def test_unregistered_predicate_is_rejected(self):
        rc, output = self.run_records([
            {
                "record_type": "source",
                "source_id": "source-1",
                "source_kind": "transcript",
                "locator": "fixture://source-1"
            },
            {
                "record_type": "work",
                "work_id": "work-1",
                "title": "Fixture Work",
                "medium": "test"
            },
            {
                "record_type": "evidence",
                "evidence_id": "evidence-1",
                "source_id": "source-1",
                "work_id": "work-1",
                "evidence_kind": "depiction",
                "locator": {"line": 1},
                "observed": {"event": "fixture"}
            },
            {
                "record_type": "assertion",
                "assertion_id": "assertion-1",
                "subject": "local-1",
                "predicate": "NOT_REGISTERED",
                "object": "x",
                "evidence": ["evidence-1"],
                "status": "ACCEPTED"
            }
        ])
        self.assertEqual(rc, 1)
        self.assertIn("NOT_REGISTERED", output)


if __name__ == "__main__":
    unittest.main()
