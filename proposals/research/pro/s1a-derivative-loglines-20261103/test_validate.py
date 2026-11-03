"""Adversarial checks for derivative-source and coverage fail-closed behavior."""

import copy
import json
import unittest
from pathlib import Path

from validate import validate_payload


DATA = json.loads((Path(__file__).resolve().parent / "records.json").read_text(encoding="utf-8"))


class ProdigyDerivativeTests(unittest.TestCase):
    def test_valid_batch(self):
        self.assertEqual(validate_payload(copy.deepcopy(DATA)), 4)

    def rejects(self, mutate):
        sample = copy.deepcopy(DATA)
        mutate(sample)
        with self.assertRaises(ValueError):
            validate_payload(sample)

    def test_admission_cannot_be_promoted(self):
        self.rejects(lambda d: d.__setitem__("coverage_effect", "DISCOVERED"))

    def test_derivative_cannot_be_relabeled_primary(self):
        self.rejects(lambda d: d["source"].__setitem__("type", "AUTHENTICATED_PRIMARY_AV"))

    def test_combined_premiere_cannot_be_silently_split(self):
        self.rejects(lambda d: d["work_candidates"][0].__setitem__("printed_slot_labels", [101]))

    def test_line_hash_is_not_replaceable(self):
        self.rejects(lambda d: d["evidence"][0].__setitem__("raw_html_line_sha256", "0" * 64))

    def test_assertion_cannot_cite_another_source_entry(self):
        self.rejects(lambda d: d["assertions"][0].__setitem__("supporting_evidence_ids", ["pro-ev-103"]))

    def test_publisher_cannot_be_independent_witness(self):
        self.rejects(lambda d: d["first_party_boundary_check"].__setitem__("independent_of_claimed_press_upstream", True))

    def test_image_url_cannot_be_added(self):
        self.rejects(lambda d: d.__setitem__("image_url", "https://example.org/art.jpg"))

    def test_unknown_year_must_remain_unknown(self):
        self.rejects(lambda d: d["local_entities"][0].__setitem__("year_in_listing", 2021))

    def test_source_date_labels_are_not_normalized(self):
        self.rejects(lambda d: d["local_entities"][0].__setitem__("source_date_as_written", "2021-10-28"))


if __name__ == "__main__":
    unittest.main()
