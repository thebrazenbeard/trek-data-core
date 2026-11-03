"""Source-local TOS S2 publisher-guide quarantine and replay regressions."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "proposals/research/tos/s2-publisher-first5-20261103"
spec = importlib.util.spec_from_file_location("tos_s2_first5_validator", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class TosS2FirstFivePublisherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = validator.read_records()

    def test_exact_held_publisher_batch_has_five_local_cards(self):
        self.assertEqual(validator.validate(self.packet), 5)
        self.assertEqual([x["title"] for x in self.packet["works"]], [
            "Amok Time", "Who Mourns for Adonais?", "The Changeling", "Mirror, Mirror", "The Apple",
        ])
        self.assertFalse(self.packet["audiovisual_episodes_watched"])
        self.assertFalse(self.packet["full_episode_text_read"])
        self.assertEqual(self.packet["coverage_effect"], "NONE")
        self.assertTrue(all(x["canonical_work_id"] is None for x in self.packet["works"]))

    def test_undetected_synopsis_or_identity_promotion_is_refused(self):
        for edit in (
            lambda p: p["works"][0].update(original_synopsis="A canonically verified fact."),
            lambda p: p["works"][1].update(canonical_work_id="tos-s2-ep2-canonical"),
            lambda p: p["assertions"][2].update(status="STABLE"),
            lambda p: p.update(coverage_effect="CLOSE_READ"),
            lambda p: p["source"].update(raw_html_sha256="0" * 64),
        ):
            with self.subTest(edit=edit):
                packet = copy.deepcopy(self.packet)
                edit(packet)
                with self.assertRaises(ValueError):
                    validator.validate(packet)

    def test_legacy_title_crosswalk_cannot_be_replaced(self):
        with tempfile.TemporaryDirectory() as scratch:
            wrong = Path(scratch) / "inventory.json"
            wrong.write_text('{"episode_slots": []}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inventory changed"):
                validator.validate(self.packet, inventory_path=wrong)

    def test_mismatched_source_bytes_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "snapshot mismatch"):
            validator.validate_private_source_html(self.packet, b"fake source bytes")

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as scratch:
            bad = Path(scratch) / "duplicates.json"
            bad.write_text('{"batch_id":"x", "batch_id":"y"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                validator.read_records(bad)


if __name__ == "__main__":
    unittest.main()
