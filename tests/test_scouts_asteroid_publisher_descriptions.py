"""Hostile source-boundary tests for Scouts Asteroid Blasters #1-#5 descriptions."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/research/short/scouts-asteroid-descriptions-20261103"
spec = importlib.util.spec_from_file_location("scouts_asteroid_descriptions", PROPOSAL / "validate.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
OBS = module.read_pinned()
DISCOVERY = json.loads((ROOT / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))


class ScoutsAsteroidPublisherDescriptionTests(unittest.TestCase):
    def reject(self, fn):
        bad = copy.deepcopy(OBS)
        fn(bad)
        with self.assertRaises(ValueError):
            module.validate(bad)

    def reject_catalog(self, fn):
        bad = copy.deepcopy(DISCOVERY)
        fn(bad)
        with self.assertRaises(ValueError):
            module.validate(OBS, bad)

    def test_five_publisher_description_rows(self):
        self.assertEqual(module.validate(OBS), 5)
        self.assertEqual(len({r["publisher_video_id"] for r in OBS["description_paraphrases"]}), 5)

    def test_no_video_or_direct_page_open_fabrication(self):
        for key in ("animations_viewed", "video_pages_opened", "source_bound", "close_read"):
            with self.subTest(key=key):
                self.reject(lambda d: d.update({key: True}))
        self.reject(lambda d: d.update(source_access="DIRECTLY_PLAYED_YOUTUBE_VIDEO"))

    def test_not_five_independent_publisher_sources(self):
        self.reject(lambda d: d.update(independent_upstream_families=5))

    def test_no_fake_response_hash(self):
        self.reject(lambda d: d.update(raw_source_page_sha256="0" * 64))

    def test_no_accepted_coverage_or_publication(self):
        for key in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                    "accepted_coverage_effect", "public_synopsis_release_effect", "artwork_release_effect"):
            with self.subTest(key=key):
                self.reject(lambda d: d.update({key: "ACCEPTED"}))
        self.reject(lambda d: d.update(proposal_only=False))

    def test_no_unreviewed_summary_edit(self):
        self.reject(lambda d: d["description_paraphrases"][0].update(
            synopsis="The asteroid was harmless but the children destroyed an alien warship."))

    def test_no_wrong_youtube_video_id(self):
        self.reject(lambda d: d["description_paraphrases"][1].update(
            publisher_video_id="PfaNbFeRCm4"))

    def test_no_spoofed_source_host(self):
        self.reject(lambda d: d["description_paraphrases"][2].update(
            youtube_video_locator="https://www.youtube.com@evil.invalid/watch?v=PfaNbFeRCm4"))

    def test_no_hidden_youtube_display_date_revision(self):
        self.reject(lambda d: d["description_paraphrases"][1].update(
            publisher_video_display_date="2025-09-09"))

    def test_no_discovery_metadata_promotion(self):
        self.reject_catalog(lambda d: d.update(data_status="SOURCE_BOUND"))
        self.reject_catalog(lambda d: next(r for r in d["rows"] if
            r["row_id"] == "short:scouts:asteroid_blasters:01").update(
                admission_effect="WORK_ADMITTED"))


if __name__ == "__main__":
    unittest.main()
