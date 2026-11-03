"""Negative gates for the bounded VOY source-local discovery proposal."""

import copy
import json
import unittest
from pathlib import Path

from validate import validate_payload


HERE = Path(__file__).resolve().parent


class VoyagerRegionalBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads((HERE / "records.json").read_text(encoding="utf-8"))

    def modified(self):
        return copy.deepcopy(self.base)

    def test_valid_bounded_discovery(self):
        validate_payload(self.modified())

    def test_no_admission(self):
        item = self.modified()
        item["coverage_effect"] = "SOURCE_BOUND"
        with self.assertRaises(ValueError):
            validate_payload(item)

    def test_no_fabricated_full_source_read(self):
        item = self.modified()
        item["full_av_or_transcript_read"] = True
        with self.assertRaises(ValueError):
            validate_payload(item)

    def test_regional_mirrors_not_independent(self):
        item = self.modified()
        item["sources"][2]["lineage_group"] = "INDEPENDENT_AU"
        with self.assertRaises(ValueError):
            validate_payload(item)

    def test_no_unobserved_ordinal(self):
        item = self.modified()
        item["local_entities"][1]["ordinal"] = 27
        with self.assertRaises(ValueError):
            validate_payload(item)

    def test_broken_evidence_links_fail(self):
        item = self.modified()
        item["assertions"][0]["evidence_ids"].append("no-such-evidence")
        with self.assertRaises(ValueError):
            validate_payload(item)

    def test_off_origin_source_refused(self):
        item = self.modified()
        item["sources"][3]["url"] = "https://evil.example/forged-guide"
        with self.assertRaises(ValueError):
            validate_payload(item)


if __name__ == "__main__":
    unittest.main()
