"""Adversarial checks that metadata never becomes governed episode evidence."""

import copy
import json
import unittest

import validate as candidate


RECORDS = json.loads((candidate.HERE / "records.json").read_text(encoding="utf-8"))
PRIOR = json.loads(candidate.PRIOR_ROSTER.read_text(encoding="utf-8"))


class PublisherRefreshTests(unittest.TestCase):
    def test_exact_candidate(self):
        self.assertEqual(candidate.validate(copy.deepcopy(RECORDS), PRIOR), (10, 2, 3))

    def test_no_canonical_work_injection(self):
        data = copy.deepcopy(RECORDS)
        data["local_entities"][0]["canonical_work_id"] = "sfa-episode-1"
        with self.assertRaises(ValueError):
            candidate.validate(data, PRIOR)

    def test_no_s2_media_promotion(self):
        data = copy.deepcopy(RECORDS)
        data["local_entities"][10]["kind"] = "PUBLISHER_EPISODE_SLOT_REFERENCE"
        with self.assertRaises(ValueError):
            candidate.validate(data, PRIOR)

    def test_no_claimed_accepted_coverage(self):
        data = copy.deepcopy(RECORDS)
        data["coverage_effect"] = "SOURCE_BOUND"
        with self.assertRaises(ValueError):
            candidate.validate(data, PRIOR)

    def test_no_off_origin_source(self):
        data = copy.deepcopy(RECORDS)
        data["source_snapshots"][0]["url"] = "https://example.com/fake"
        with self.assertRaises(ValueError):
            candidate.validate(data, PRIOR)

    def test_no_false_independent_publisher(self):
        data = copy.deepcopy(RECORDS)
        data["source_snapshots"][1]["independence_group"] = "independent:second-witness"
        with self.assertRaises(ValueError):
            candidate.validate(data, PRIOR)

    def test_no_image_rights_promotion(self):
        data = copy.deepcopy(RECORDS)
        data["photo_metadata_observations"][0]["rights_status"] = "PUBLIC_DISPLAY_PERMISSION_VERIFIED"
        with self.assertRaises(ValueError):
            candidate.validate(data, PRIOR)

    def test_no_signed_image_url_release(self):
        data = copy.deepcopy(RECORDS)
        data["photo_metadata_observations"][0]["image_url"] = "https://private-assets.example/"
        with self.assertRaises(ValueError):
            candidate.validate(data, PRIOR)

    def test_no_forged_s1_reordering(self):
        data = copy.deepcopy(RECORDS)
        data["local_entities"][0]["title"] = data["local_entities"][1]["title"]
        with self.assertRaises(ValueError):
            candidate.validate(data, PRIOR)

    def test_no_unlocated_assertion(self):
        data = copy.deepcopy(RECORDS)
        data["assertions"][1]["support_evidence_ids"] = ["invented"]
        with self.assertRaises(ValueError):
            candidate.validate(data, PRIOR)


if __name__ == "__main__":
    unittest.main()
