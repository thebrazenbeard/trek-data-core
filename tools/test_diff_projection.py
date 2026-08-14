#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("diff_projection.py")
spec = importlib.util.spec_from_file_location("trek_diff_projection", MODULE_PATH)
diff = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(diff)


def write_jsonl(root, filename, rows):
    (root / filename).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def assertion(assertion_id="a1", *, status="STABLE", value="v1", resolved_subject="global:one", scope=None):
    row = {
        "record_type": "assertion",
        "assertion_id": assertion_id,
        "subject": "local-1",
        "resolved_subject": resolved_subject,
        "predicate": "CLAIMS",
        "object": {"value": value},
        "projection_status": status,
        "scope": {"continuity": "prime"} if scope is None else scope,
    }
    return row


class SemanticDiffTests(unittest.TestCase):
    def run_diff(self, old_files, new_files):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            old = base / "old"; new = base / "new"; old.mkdir(); new.mkdir()
            for filename, rows in old_files.items(): write_jsonl(old, filename, rows)
            for filename, rows in new_files.items(): write_jsonl(new, filename, rows)
            return diff.semantic_diff(old, new)

    def classes(self, changes):
        return [change["class"] for change in changes]

    def test_added_and_removed_fact(self):
        added = self.run_diff({}, {"facts.jsonl": [assertion()]})
        removed = self.run_diff({"facts.jsonl": [assertion()]}, {})
        self.assertEqual(self.classes(added), ["ADDED_FACT"])
        self.assertEqual(self.classes(removed), ["REMOVED_FACT"])

    def test_value_change(self):
        changes = self.run_diff(
            {"facts.jsonl": [assertion(value="v1")]},
            {"facts.jsonl": [assertion(value="v2")]},
        )
        self.assertIn("VALUE_CHANGED", self.classes(changes))

    def test_stable_to_contested_is_demotion_and_conflict_introduced(self):
        changes = self.run_diff(
            {"facts.jsonl": [assertion(status="STABLE")]},
            {"contested.jsonl": [assertion(status="CONTESTED")]},
        )
        self.assertIn("STATUS_DEMOTED", self.classes(changes))
        self.assertIn("CONFLICT_INTRODUCED", self.classes(changes))

    def test_contested_to_stable_is_promotion_and_conflict_resolved(self):
        changes = self.run_diff(
            {"contested.jsonl": [assertion(status="CONTESTED")]},
            {"facts.jsonl": [assertion(status="STABLE")]},
        )
        self.assertIn("STATUS_PROMOTED", self.classes(changes))
        self.assertIn("CONFLICT_RESOLVED", self.classes(changes))

    def test_entity_link_change(self):
        changes = self.run_diff(
            {"entities.jsonl": [{"local_entity_id": "local-1", "resolved_entity": "global:one"}]},
            {"entities.jsonl": [{"local_entity_id": "local-1", "resolved_entity": "global:two"}]},
        )
        self.assertEqual(self.classes(changes), ["ENTITY_LINK_CHANGED"])

    def test_assertion_resolved_subject_change_is_entity_link_change(self):
        changes = self.run_diff(
            {"facts.jsonl": [assertion(resolved_subject="global:one")]},
            {"facts.jsonl": [assertion(resolved_subject="global:two")]},
        )
        self.assertIn("ENTITY_LINK_CHANGED", self.classes(changes))

    def test_scope_change(self):
        changes = self.run_diff(
            {"facts.jsonl": [assertion(scope={"continuity": "prime"})]},
            {"facts.jsonl": [assertion(scope={"continuity": "alternate"})]},
        )
        self.assertIn("SCOPE_CHANGED", self.classes(changes))

    def test_provenance_change(self):
        old = [{"provenance_id": "a1::e1", "assertion_id": "a1", "evidence_id": "e1", "source_content_hash": "sha256:a"}]
        new = [{"provenance_id": "a1::e1", "assertion_id": "a1", "evidence_id": "e1", "source_content_hash": "sha256:b"}]
        changes = self.run_diff({"provenance.jsonl": old}, {"provenance.jsonl": new})
        self.assertEqual(self.classes(changes), ["PROVENANCE_CHANGED"])

    def test_contested_to_structural_paradox_is_value_change_not_fake_rank(self):
        changes = self.run_diff(
            {"contested.jsonl": [assertion(status="CONTESTED")]},
            {"contested.jsonl": [assertion(status="STRUCTURAL_PARADOX")]},
        )
        self.assertIn("VALUE_CHANGED", self.classes(changes))
        self.assertNotIn("STATUS_PROMOTED", self.classes(changes))
        self.assertNotIn("STATUS_DEMOTED", self.classes(changes))


if __name__ == "__main__":
    unittest.main()
