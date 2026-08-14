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
spec = importlib.util.spec_from_file_location("trek_validate_recon", MODULE_PATH)
validate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate)


def base_records():
    return [
        {"record_type": "source", "source_id": "source-1", "source_kind": "transcript", "locator": "fixture://source-1"},
        {"record_type": "work", "work_id": "work-1", "title": "Fixture Work", "medium": "test"},
        {"record_type": "evidence", "evidence_id": "evidence-1", "source_id": "source-1", "work_id": "work-1", "evidence_kind": "depiction", "locator": {"line": 1}, "observed": {"event": "fixture"}},
    ]


def link(decision_id, value, *, subject="local-1", supersedes=None, reason=None, evidence=None):
    record = {
        "record_type": "reconciliation_decision",
        "decision_id": decision_id,
        "decision_type": "ENTITY_LINK",
        "subject_id": subject,
        "value": value,
        "status": "ACCEPTED",
        "evidence": ["evidence-1"] if evidence is None else evidence,
        "method": "manual reconciliation",
    }
    if supersedes is not None:
        record["supersedes"] = supersedes
    if reason is not None:
        record["reason"] = reason
    return record


class ReconciliationValidationTests(unittest.TestCase):
    def run_records(self, records):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "reconciliation"; root.mkdir()
            (root / "records.jsonl").write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
            old_roots = validate.DATA_ROOTS; validate.DATA_ROOTS = [root]
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout): rc = validate.main()
            finally:
                validate.DATA_ROOTS = old_roots
            return rc, stdout.getvalue()

    def test_conflicting_active_entity_links_are_rejected(self):
        rc, output = self.run_records(base_records() + [link("link-1", "global-a"), link("link-2", "global-b")])
        self.assertEqual(rc, 1)
        self.assertIn("multiple active", output)
        self.assertIn("ENTITY_LINK", output)
        self.assertIn("local-1", output)

    def test_accepted_supersession_requires_reason(self):
        rc, output = self.run_records(base_records() + [
            link("link-1", "global-a"),
            link("link-2", "global-b", supersedes="link-1"),
        ])
        self.assertEqual(rc, 1)
        self.assertIn("superseding accepted decision", output)
        self.assertIn("reason", output)


if __name__ == "__main__":
    unittest.main()
