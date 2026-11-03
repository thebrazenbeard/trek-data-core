"""Hostile tests: Scouts Holodeck 1–5 source-local summary observations."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "proposals/research/short/scouts-holodeck-01to05-descriptions-20261103"
spec = importlib.util.spec_from_file_location("scouts_holodeck_01to05", PACKET / "validate.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
OBS = module.read_pinned()
CATALOG = json.loads((ROOT / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))


class ScoutsHolodeckSourceDescriptionTests(unittest.TestCase):
    def reject(self, modify):
        proposed = copy.deepcopy(OBS)
        modify(proposed)
        with self.assertRaises(ValueError):
            module.validate(proposed)

    def reject_catalog(self, modify):
        proposed = copy.deepcopy(CATALOG)
        modify(proposed)
        with self.assertRaises(ValueError):
            module.validate(OBS, proposed)

    def test_publisher_search_summaries_cover_five_distinct_sources(self):
        self.assertEqual(module.validate(OBS), 5)
        self.assertEqual(len({r["publisher_video_id"] for r in OBS["description_paraphrases"]}), 5)

    def test_direct_media_or_page_access_never_fabricated(self):
        for key in ("animations_viewed", "video_pages_opened", "source_bound", "close_read"):
            with self.subTest(key=key):
                self.reject(lambda d, k=key: d.update({k: True}))
        self.reject(lambda d: d.update(source_access="DIRECT_EPISODE_WATCHED"))

    def test_no_fabricated_independent_sources(self):
        self.reject(lambda d: d.update(independent_upstream_families=5))

    def test_no_fabricated_raw_youtube_page_bytes(self):
        self.reject(lambda d: d.update(raw_source_page_sha256="0" * 64))

    def test_no_unapproved_admission_coverage_publication_artwork(self):
        for key in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                    "accepted_coverage_effect", "public_synopsis_release_effect", "artwork_release_effect"):
            with self.subTest(key=key):
                self.reject(lambda d, k=key: d.update({k: "ACCEPTED"}))
        self.reject(lambda d: d.update(proposal_only=False))

    def test_no_unreviewed_plot_addition(self):
        self.reject(lambda d: d["description_paraphrases"][3].update(
            synopsis="The Scouts conclusively observe ancient whale temporal mechanics and rescue the universe."))

    def test_no_wrong_youtube_video_id(self):
        self.reject(lambda d: d["description_paraphrases"][2].update(publisher_video_id="M02cKstXmjo"))

    def test_no_spoofed_source_url(self):
        self.reject(lambda d: d["description_paraphrases"][0].update(
            youtube_video_locator="https://www.youtube.com@evil.invalid/watch?v=69jkEMz87co"))

    def test_no_unreviewed_title_alias_equation(self):
        self.reject(lambda d: d["description_paraphrases"][0].update(
            publisher_video_title="Scouts Save a Baby Animal from Hot Lava! 🌋🫐  | Star Trek: Scouts | Holodeck Rescues Episode #1"))
        self.reject(lambda d: d["description_paraphrases"][3].update(
            publisher_video_title="Holodeck Rescues #4 | Star Trek Scouts Save a Space Whale From a Black Hole! 🐋🚀 | Star Trek: Scouts"))

    def test_no_discovery_promotion_or_wrong_lineage(self):
        self.reject_catalog(lambda d: d.update(data_status="SOURCE_BOUND"))
        self.reject_catalog(lambda d: next(r for r in d["rows"] if
            r["row_id"] == "short:scouts:holodeck_rescues:02").update(
                source_locator="https://youtu.be/fybF9xOzXs4"))


if __name__ == "__main__":
    unittest.main()
