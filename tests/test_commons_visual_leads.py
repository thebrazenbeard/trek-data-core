"""Fail-closed Commons license/source observation and non-release tests."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("commons_visual_leads", ROOT / "tools/validate_commons_visual_leads.py")
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class CommonsVisualLeadsTests(unittest.TestCase):
    def setUp(self):
        self.packet = copy.deepcopy(validator.expected_packet())

    def _reject(self, edit):
        packet = copy.deepcopy(self.packet)
        edit(packet)
        with self.assertRaises(validator.CommonsLeadRejected):
            validator.validate(packet)

    def test_checked_in_exact_source_license_observations(self):
        checked = validator._strict_json(validator.RECORD_PATH.read_bytes())
        validator.validate(checked)
        self.assertEqual(len(checked["candidates"]), 3)
        self.assertEqual(checked["independently_approved_for_trek_explorer"], 0)
        self.assertTrue(all(not row["public_display_eligible"] and not row["public_rehost_eligible"]
                            for row in checked["candidates"]))

    def test_file_page_license_not_underlying_trek_rights(self):
        self.assertTrue(all(row["license_not_covering_other_rights"] for row in self.packet["candidates"]))
        self.assertTrue(all(row["candidate_status"].startswith("HELD_") for row in self.packet["candidates"]))
        self.assertTrue(all(row["exact_explorer_work_binding"] is None for row in self.packet["candidates"]))

    def test_false_rights_approval_denied(self):
        self._reject(lambda p: p.update(independently_approved_for_trek_explorer=3))

    def test_false_release_list_denied(self):
        self._reject(lambda p: p.update(released_artwork_assets=["commons-2011-nimoy-convention-photo"]))

    def test_no_public_display_on_license_label_alone(self):
        self._reject(lambda p: p["candidates"][0].update(public_display_eligible=True))

    def test_no_rehost_on_license_label_alone(self):
        self._reject(lambda p: p["candidates"][0].update(public_rehost_eligible=True))

    def test_no_fake_independent_reviewer(self):
        self._reject(lambda p: p["candidates"][0].update(independent_license_reviewer="Model Consensus"))

    def test_no_image_sha_without_bytes(self):
        self._reject(lambda p: p["candidates"][0].update(image_sha256="1" * 64))

    def test_no_duplicate_file(self):
        self._reject(lambda p: p["candidates"].append(copy.deepcopy(p["candidates"][0])))

    def test_no_wrong_file_page_or_revision(self):
        self._reject(lambda p: p["candidates"][0].update(file_page_revision_url="https://commons.wikimedia.org/w/index.php?title=File:Other.jpg&oldid=1"))

    def test_no_non_commons_license_claim_injected(self):
        self._reject(lambda p: p["candidates"][0].update(license_identifier_observed="CC0-1.0"))

    def test_no_attribution_drop(self):
        self._reject(lambda p: p["candidates"][0].update(attribution_requirements=[]))

    def test_no_sharealike_removed(self):
        self._reject(lambda p: p["candidates"][1]["attribution_requirements"].remove("SHAREALIKE_IF_ADAPTED"))

    def test_no_flickr_source_switch(self):
        self._reject(lambda p: p["candidates"][1].update(original_creator_source_url="https://www.flickr.com/photos/other/1"))

    def test_no_actor_equated_to_character(self):
        self._reject(lambda p: p["candidates"][0].update(proposed_context="SPOCK_CANONICAL_CHARACTER_STILL"))

    def test_no_fan_convention_mislabeled_as_episode(self):
        self._reject(lambda p: p["candidates"][1].update(exact_explorer_work_binding="TOS.S01E01"))

    def test_no_file_bytes(self):
        self._reject(lambda p: p.update(retrieved_image_bytes=True))

    def test_no_file_payload_addition(self):
        self._reject(lambda p: p["candidates"][0].update(inline_png_base64="AA=="))

    def test_no_hidden_trademark_clearance_claim(self):
        self._reject(lambda p: p["candidates"][2].update(license_not_covering_other_rights=False))

    def test_nonfinite_json_rejected(self):
        with self.assertRaises(validator.CommonsLeadRejected):
            validator._strict_json(b'{"foo":Infinity}')

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(validator.CommonsLeadRejected):
            validator._strict_json(b'{"foo":1,"foo":2}')


if __name__ == "__main__":
    unittest.main()
