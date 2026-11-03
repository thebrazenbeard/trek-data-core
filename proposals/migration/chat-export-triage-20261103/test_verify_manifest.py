"""Tampering tests for the proposal-only chat history intake gate."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from verify_manifest import verify


ROOT = Path(__file__).resolve().parent


class ChatExportTriageTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))

    def check_rejected(self, mutate):
        value = copy.deepcopy(self.data)
        mutate(value)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "MANIFEST.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(ValueError):
                verify(path)

    def test_manifest_is_valid(self):
        verify(ROOT / "MANIFEST.json")

    def test_cannot_promote_chat_to_admitted_research(self):
        self.check_rejected(lambda value: value.update(admission="ADMITTED"))

    def test_cannot_advance_coverage(self):
        self.check_rejected(lambda value: value.update(coverage_effect="SOURCE_BOUND"))

    def test_cannot_impersonate_source_inspection(self):
        self.check_rejected(lambda value: value["review_queue"][0].update(
            claimant="PRIMARY_SOURCE_READER"))

    def test_duplicate_lead_rejected(self):
        self.check_rejected(lambda value: value["review_queue"].append(
            copy.deepcopy(value["review_queue"][0])))

    def test_invalid_source_locator_rejected(self):
        self.check_rejected(lambda value: value["review_queue"][0].update(
            rendered_text_lines=[200, 100]))


if __name__ == "__main__":
    unittest.main()
