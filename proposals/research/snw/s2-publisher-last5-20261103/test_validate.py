"""Adversarial checks for the SNW source-relative proposal contract."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from validate import validate_records


DATA = json.loads((Path(__file__).resolve().parent / "records.json").read_text(encoding="utf-8"))


class ResearchProposalTests(unittest.TestCase):
    def test_real_tranche(self):
        self.assertEqual(validate_records(DATA), 5)

    def test_fabricated_coverage_rejected(self):
        bad = deepcopy(DATA)
        bad["coverage_effect"] = "CLOSE_READ"
        with self.assertRaises(ValueError):
            validate_records(bad)

    def test_source_digest_substitution_rejected(self):
        bad = deepcopy(DATA)
        bad["source"]["response_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            validate_records(bad)

    def test_global_identity_rejected(self):
        bad = deepcopy(DATA)
        bad["local_entities"][0]["global_entity_id"] = "canonical:uhura"
        with self.assertRaises(ValueError):
            validate_records(bad)

    def test_cross_work_evidence_rejected(self):
        bad = deepcopy(DATA)
        bad["assertions"][0]["evidence_id"] = bad["evidence"][1]["evidence_id"]
        with self.assertRaises(ValueError):
            validate_records(bad)

    def test_cross_work_entity_rejected(self):
        bad = deepcopy(DATA)
        bad["assertions"][0]["local_entity_ids"] = [bad["local_entities"][1]["local_entity_id"]]
        with self.assertRaises(ValueError):
            validate_records(bad)

    def test_pub_synopsis_as_depiction_rejected(self):
        bad = deepcopy(DATA)
        bad["evidence"][0]["kind"] = "ONSCREEN_DEPICTION"
        with self.assertRaises(ValueError):
            validate_records(bad)

    def test_publisher_timestamp_mutation_rejected(self):
        bad = deepcopy(DATA)
        bad["works"][1]["source_datetime"] = "2023-07-23T00:00:00+00:00"
        with self.assertRaises(ValueError):
            validate_records(bad)


if __name__ == "__main__":
    unittest.main()
