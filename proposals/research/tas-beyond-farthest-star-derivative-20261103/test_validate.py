"""Adversarial boundary checks for one complete derivative-text TAS proposal."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tas_proposal_validator", HERE / "validate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
BASE = json.loads((HERE / "records.json").read_text(encoding="utf-8"))


class TASProposalValidation(unittest.TestCase):
    def test_baseline(self):
        self.assertEqual(module.validate(BASE), (12, 15, 7))

    def test_cannot_promote_coverage(self):
        data = copy.deepcopy(BASE)
        data["coverage_effect"] = "CLOSE_READ"
        with self.assertRaisesRegex(ValueError, "coverage_effect"):
            module.validate(data)

    def test_cannot_promote_primary_av(self):
        data = copy.deepcopy(BASE)
        data["source"]["authenticated_primary_audiovisual"] = True
        with self.assertRaisesRegex(ValueError, "authenticated_primary_audiovisual"):
            module.validate(data)

    def test_cannot_invent_upstream_lineage(self):
        data = copy.deepcopy(BASE)
        data["source"]["lineage_status"] = "INDEPENDENT_CONFIRMED"
        with self.assertRaisesRegex(ValueError, "lineage"):
            module.validate(data)

    def test_rejects_foreign_global_entity(self):
        data = copy.deepcopy(BASE)
        data["local_entities"][0]["id"] = "global:kirk"
        with self.assertRaisesRegex(ValueError, "nonlocal entity"):
            module.validate(data)

    def test_rejects_out_of_bounds_locator(self):
        data = copy.deepcopy(BASE)
        data["evidence"][-1]["fragment_range"] = [263, 264]
        with self.assertRaisesRegex(ValueError, "fragment locator"):
            module.validate(data)

    def test_rejects_fabricated_evidence_reference(self):
        data = copy.deepcopy(BASE)
        data["assertions"][0]["support_evidence_ids"] = ["ev:tas001:absent"]
        with self.assertRaisesRegex(ValueError, "foreign or fabricated"):
            module.validate(data)

    def test_rejects_artwork_release_field(self):
        data = copy.deepcopy(BASE)
        data["image_url"] = "https://example.net/artwork.jpg"
        with self.assertRaisesRegex(ValueError, "forbidden release"):
            module.validate(data)

    def test_rejects_same_host_wrong_episode(self):
        data = copy.deepcopy(BASE)
        data["source"]["url"] = data["source"]["url"].replace("episode=s01e01", "episode=s01e02")
        with self.assertRaisesRegex(ValueError, "source URL identity mismatch"):
            module.validate(data)

    def test_rejects_raw_receipt_substitution(self):
        data = copy.deepcopy(BASE)
        data["source"]["raw_html_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "invalid raw-source receipt"):
            module.validate(data)

    def test_rejects_fragment_receipt_substitution(self):
        data = copy.deepcopy(BASE)
        data["source"]["normalized_fragment_stream_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "invalid fragment receipt"):
            module.validate(data)


if __name__ == "__main__":
    unittest.main()
