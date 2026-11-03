"""Hostile review fixtures for first-party Scouts Holodeck 6–9 search descriptions."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "proposals/research/short/scouts-holodeck-06to09-descriptions-20261103"
spec = importlib.util.spec_from_file_location("scouts_holodeck_06to09", PACKET / "validate.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
OBS = module.read_pinned()
CATALOG = json.loads((ROOT / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))


class ScoutsHolodeckSixToNineTests(unittest.TestCase):
    def reject(self, modify):
        data = copy.deepcopy(OBS)
        modify(data)
        with self.assertRaises(ValueError):
            module.validate(data)

    def reject_catalog(self, modify):
        data = copy.deepcopy(CATALOG)
        modify(data)
        with self.assertRaises(ValueError):
            module.validate(OBS, data)

    def test_four_read_descriptions_and_fifth_held(self):
        self.assertEqual(module.validate(OBS), 4)
        self.assertEqual(len({r["publisher_video_id"] for r in OBS["description_paraphrases"]}), 4)
        self.assertIsNone(OBS["held_following_row"]["synopsis"])

    def test_held_fifth_cannot_gain_unsourced_summary(self):
        self.reject(lambda d: d["held_following_row"].update(synopsis="A farmer's crops are saved."))
        self.reject(lambda d: d["held_following_row"].update(status="OFFICIAL_SOURCE_READ"))

    def test_no_full_video_or_open_page_fabrication(self):
        for key in ("animations_viewed", "video_pages_opened", "source_bound", "close_read"):
            with self.subTest(key=key):
                self.reject(lambda d, k=key: d.update({k: True}))

    def test_no_independent_upstream_inflation(self):
        self.reject(lambda d: d.update(independent_upstream_families=4))

    def test_no_fake_raw_bytes_or_page_hash(self):
        self.reject(lambda d: d.update(raw_source_page_sha256="f" * 64))
        self.reject(lambda d: d.update(source_access="DIRECT_YOUTUBE_VIDEO_PAGE_OPENED"))

    def test_protected_effects_frozen(self):
        for key in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                    "accepted_coverage_effect", "public_synopsis_release_effect", "artwork_release_effect"):
            with self.subTest(key=key):
                self.reject(lambda d, k=key: d.update({k: "ACCEPTED"}))

    def test_no_unreviewed_paraphrase_edit(self):
        self.reject(lambda d: d["description_paraphrases"][0].update(
            synopsis="The Scouts discover a canonical moonchuck technological civilization."))

    def test_no_youtube_host_spoof_or_id_rewrite(self):
        self.reject(lambda d: d["description_paraphrases"][0].update(
            youtube_video_locator="https://www.youtube.com@evil.invalid/watch?v=-m7ISEuAhac"))
        self.reject(lambda d: d["description_paraphrases"][2].update(publisher_video_id="TbZFOtuHpxk"))

    def test_no_derivative_or_discovery_title_substitution(self):
        self.reject(lambda d: d["description_paraphrases"][0].update(
            publisher_video_title="Star Trek Scouts Go to the Moon to Fight ROBOTS! 🤖| Star Trek: Scouts | Holodeck Rescues Episode #6"))

    def test_no_catalog_admission_or_crosswalk_change(self):
        self.reject_catalog(lambda d: d.update(data_status="SOURCE_BOUND"))
        self.reject_catalog(lambda d: next(r for r in d["rows"] if
            r["row_id"] == "short:scouts:holodeck_rescues:09").update(
                source_locator="https://youtu.be/vlez2Dtu95E"))


if __name__ == "__main__":
    unittest.main()
