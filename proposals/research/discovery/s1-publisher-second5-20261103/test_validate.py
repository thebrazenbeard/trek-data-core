"""Negative and boundary checks for one publisher-only Discovery tranche."""

import copy
import json
from pathlib import Path
import unittest

from validate import RECORDS, digest, unique_object, validate, validate_private_source_html


class PublisherSecondFiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(RECORDS.read_text(encoding="utf-8"), object_pairs_hook=unique_object)

    def test_exact_pinned_packet(self):
        self.assertEqual(validate(self.data), 5)

    def test_no_global_identity_promotion(self):
        altered = copy.deepcopy(self.data)
        altered["works"][0]["canonical_work_id"] = "work:discovery:1:6"
        with self.assertRaisesRegex(ValueError, "semantic digest"):
            validate(altered)

    def test_no_simulated_full_work_read(self):
        altered = copy.deepcopy(self.data)
        altered["audiovisual_episodes_watched"] = True
        with self.assertRaisesRegex(ValueError, "semantic digest"):
            validate(altered)

    def test_no_publisher_claim_as_canonical_fact(self):
        altered = copy.deepcopy(self.data)
        altered["assertions"][2]["status"] = "STABLE"
        with self.assertRaisesRegex(ValueError, "semantic digest"):
            validate(altered)

    def test_no_changed_paraphrase_without_review(self):
        altered = copy.deepcopy(self.data)
        altered["works"][4]["original_synopsis"] = "A fabricated episode description."
        with self.assertRaisesRegex(ValueError, "semantic digest"):
            validate(altered)

    def test_no_artwork_publication_without_review(self):
        altered = copy.deepcopy(self.data)
        altered["artwork_candidates"][1]["rights_status"] = "PUBLISHED"
        with self.assertRaisesRegex(ValueError, "semantic digest"):
            validate(altered)

    def test_no_source_byte_substitution(self):
        with self.assertRaisesRegex(ValueError, "exact publisher response"):
            validate_private_source_html(self.data, b"<html><p>synthetic</p></html>")

    def test_reject_duplicate_json_keys(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"duplicate":1,"duplicate":2}', object_pairs_hook=unique_object)

    def test_invalid_inventory_bytes(self):
        altered_inventory = RECORDS.parent / "test_validate.py"
        with self.assertRaisesRegex(ValueError, "inventory has drifted"):
            validate(self.data, inventory_path=altered_inventory)

    def test_digest_stable_after_reload(self):
        before = digest(RECORDS.read_bytes())
        copy_payload = json.loads(RECORDS.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        self.assertEqual(before, digest(RECORDS.read_bytes()))
        self.assertEqual(copy_payload["works"][0]["title"], "Lethe")


if __name__ == "__main__":
    unittest.main()
