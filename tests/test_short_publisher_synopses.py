"""Hostile tests for SHORT publisher copy paraphrases, not audiovisual evidence."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/research/short/publisher-synopses-20261103"
spec = importlib.util.spec_from_file_location("short_publisher_synopses", PROPOSAL / "validate.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
OBS = module.read_pinned()
CATALOG = json.loads((ROOT / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))


class ShortPublisherDescriptionTests(unittest.TestCase):
    def reject(self, mutate):
        altered = copy.deepcopy(OBS)
        mutate(altered)
        with self.assertRaises(ValueError):
            module.validate(altered)

    def reject_catalog(self, mutate):
        altered = copy.deepcopy(CATALOG)
        mutate(altered)
        with self.assertRaises(ValueError):
            module.validate(OBS, altered)

    def test_ten_distinct_publisher_descriptions(self):
        self.assertEqual(module.validate(OBS), 10)
        self.assertEqual({row["directory_row_id"] for row in OBS["description_paraphrases"]},
                         {f"short:short-treks-{i:02d}" for i in range(1, 11)})

    def test_no_claim_to_have_watched_video(self):
        for name in ("full_short_viewed", "source_bound", "close_read"):
            with self.subTest(name=name):
                self.reject(lambda data: data.update({name: True}))
        self.reject(lambda data: data.update(verification_class="VIDEO_CLOSE_READ"))

    def test_proposals_do_not_admit_or_publish(self):
        for name in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                     "accepted_coverage_effect", "public_synopsis_release_effect",
                     "artwork_release_effect"):
            with self.subTest(name=name):
                self.reject(lambda data: data.update({name: "ACCEPTED"}))
        self.reject(lambda data: data.update(proposal_only=False))

    def test_publisher_family_cannot_be_forged_into_independent_witnesses(self):
        self.reject(lambda data: data.update(independent_upstream_families=4))
        self.reject(lambda data: data.update(source_family="publisher:memory-alpha"))

    def test_raw_custody_digest_cannot_be_fabricated(self):
        self.reject(lambda data: data.update(raw_source_page_sha256="a" * 64))

    def test_no_unreviewed_summary_edit(self):
        self.reject(lambda data: data["description_paraphrases"][0].update(
            synopsis="Tilly single-handedly conquers an alien army aboard the Enterprise."))

    def test_short_discovery_identity_cannot_be_swapped(self):
        self.reject(lambda data: data["description_paraphrases"][0].update(
            directory_row_id="short:short-treks-02"))
        self.reject(lambda data: data["description_paraphrases"][9].update(
            publisher_guide_slot="S2E6"))
        self.reject_catalog(lambda data: next(row for row in data["rows"]
            if row["row_id"] == "short:short-treks-01").update(medium="EPISODE"))

    def test_no_unreviewed_cross_new_year_schedule_inference(self):
        self.assertEqual(OBS["description_paraphrases"][3]["publisher_announced_date"],
                         "2019-01-03")
        self.assertEqual(OBS["description_paraphrases"][9]["publisher_announced_date"],
                         "2020-01-09")
        self.assertTrue(OBS["description_paraphrases"][3]["announcement_year_inferred"])
        self.assertTrue(OBS["description_paraphrases"][9]["announcement_year_inferred"])
        self.reject(lambda data: data["description_paraphrases"][9].update(
            announcement_year_inferred=False))

    def test_no_spoofed_first_party_url(self):
        self.reject(lambda data: data.update(
            source_guide="https://www.paramountplus.com@evil.invalid/shows/star-trek-short-treks/episodes/"))
        self.reject_catalog(lambda data: next(row for row in data["rows"]
            if row["row_id"] == "short:short-treks-02").update(
                source_locator="https://www.paramountplus.com@evil.invalid/episodes/"))

    def test_no_premature_discovery_coverage_promotion(self):
        self.reject_catalog(lambda data: data.update(data_status="CLOSE_READ"))
        self.reject_catalog(lambda data: next(row for row in data["rows"]
            if row["row_id"] == "short:short-treks-04").update(
                verification_status="FULL_TEXT_AVAILABLE"))


if __name__ == "__main__":
    unittest.main()
