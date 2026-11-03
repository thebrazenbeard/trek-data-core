"""Hostile invariants on first-party search descriptions of Scouts #6–#10."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "proposals/research/short/scouts-asteroid-06to10-descriptions-20261103"
spec = importlib.util.spec_from_file_location("scouts_06to10_validate", PACKET / "validate.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
OBS = module.read_pinned()
CATALOG = json.loads((ROOT / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))


class ScoutsAsteroidSixToTenTests(unittest.TestCase):
    def reject(self, mutate):
        bad = copy.deepcopy(OBS)
        mutate(bad)
        with self.assertRaises(ValueError):
            module.validate(bad)

    def reject_catalog(self, mutate):
        bad = copy.deepcopy(CATALOG)
        mutate(bad)
        with self.assertRaises(ValueError):
            module.validate(OBS, bad)

    def test_five_unique_source_local_descriptions(self):
        self.assertEqual(module.validate(OBS), 5)
        self.assertEqual({r["directory_row_id"] for r in OBS["description_paraphrases"]},
                         {f"short:scouts:asteroid_blasters:{i:02d}" for i in range(6, 11)})

    def test_video_and_direct_web_page_remain_unviewed(self):
        for key in ("animations_viewed", "video_pages_opened", "source_bound", "close_read"):
            with self.subTest(key=key):
                self.reject(lambda data: data.update({key: True}))

    def test_do_not_fabricate_custody_hash(self):
        self.reject(lambda data: data.update(raw_source_page_sha256="a" * 64))

    def test_one_corporate_publisher_family(self):
        self.reject(lambda data: data.update(independent_upstream_families=5))

    def test_no_accepted_or_publication_effects(self):
        for key in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                    "accepted_coverage_effect", "public_synopsis_release_effect", "artwork_release_effect"):
            with self.subTest(key=key):
                self.reject(lambda data: data.update({key: "ACCEPTED"}))
        self.reject(lambda data: data.update(proposal_only=False))

    def test_unreviewed_horta_narrative_is_rejected(self):
        self.reject(lambda data: data["description_paraphrases"][4].update(
            synopsis="The Horta devours the Gorgonite asteroid and defeats Shadowtrix."))

    def test_no_swapped_number_or_video_id(self):
        self.reject(lambda data: data["description_paraphrases"][0].update(
            directory_row_id="short:scouts:asteroid_blasters:07"))
        self.reject(lambda data: data["description_paraphrases"][3].update(
            publisher_video_id="GtJpqUH3gTA"))

    def test_no_forged_youtube_url(self):
        self.reject(lambda data: data["description_paraphrases"][1].update(
            youtube_video_locator="https://www.youtube.com@malicious.invalid/watch?v=GtJpqUH3gTA"))

    def test_no_source_date_falsification(self):
        self.reject(lambda data: data["description_paraphrases"][4].update(
            publisher_video_display_date="2025-12-07"))

    def test_discovery_source_status_must_remain_local(self):
        self.reject_catalog(lambda data: data.update(data_status="SOURCE_BOUND"))
        self.reject_catalog(lambda data: next(r for r in data["rows"] if
            r["row_id"] == "short:scouts:asteroid_blasters:10").update(
                coverage_effect="CLOSE_READ"))


if __name__ == "__main__":
    unittest.main()
