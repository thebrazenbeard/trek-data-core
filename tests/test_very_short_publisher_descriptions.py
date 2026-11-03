"""Hostile tests for five official promotional short landing-page descriptions."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/research/short/very-short-treks-descriptions-20261103"
spec = importlib.util.spec_from_file_location("very_short_descriptions", PROPOSAL / "validate.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
OBS = module.read_pinned()
DISCOVERY = json.loads((ROOT / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))


class VeryShortPublisherDescriptionTests(unittest.TestCase):
    def reject(self, mutation):
        bad = copy.deepcopy(OBS)
        mutation(bad)
        with self.assertRaises(ValueError):
            module.validate(bad)

    def reject_catalog(self, mutation):
        bad = copy.deepcopy(DISCOVERY)
        mutation(bad)
        with self.assertRaises(ValueError):
            module.validate(OBS, bad)

    def test_four_premises_one_explicitly_pending_synopsis(self):
        self.assertEqual(module.validate(OBS), 5)
        self.assertEqual(sum(x["synopsis"] is not None for x in OBS["description_paraphrases"]), 4)
        self.assertIsNone(OBS["description_paraphrases"][3]["synopsis"])

    def test_do_not_invent_holograms_plot(self):
        self.reject(lambda d: d["description_paraphrases"][3].update(
            synopsis="A simulation produces many nested holographic versions of the crew."))
        self.reject(lambda d: d["description_paraphrases"][3].update(
            description_class="PUBLISHER_PREMISE_PARAPHRASE"))

    def test_no_source_video_close_read_claim(self):
        for key in ("animated_shorts_viewed", "source_bound", "close_read"):
            with self.subTest(key=key):
                self.reject(lambda d: d.update({key: True}))
        self.reject(lambda d: d.update(verification_class="WATCHED_ANIMATION"))

    def test_no_unapproved_admission_publication_or_artwork(self):
        for key in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                    "accepted_coverage_effect", "public_synopsis_release_effect", "artwork_release_effect"):
            with self.subTest(key=key):
                self.reject(lambda d: d.update({key: "RELEASED"}))
        self.reject(lambda d: d.update(proposal_only=False))

    def test_no_second_independent_witness_from_same_publisher(self):
        self.reject(lambda d: d.update(independent_upstream_families=5))

    def test_no_made_up_page_hash(self):
        self.reject(lambda d: d.update(raw_source_page_sha256="0" * 64))

    def test_title_variations_do_not_silently_merge(self):
        self.reject(lambda d: d["description_paraphrases"][0].update(
            publisher_video_title="Skin a Cat"))
        self.reject(lambda d: d["description_paraphrases"][3].update(
            publisher_title_variation="NONE"))

    def test_no_unreviewed_premise_edits(self):
        self.reject(lambda d: d["description_paraphrases"][2].update(
            synopsis="Riker defeats a hostile empire during first contact."))

    def test_no_spoofed_or_swapped_publisher_video_url(self):
        self.reject(lambda d: d["description_paraphrases"][0].update(
            publisher_video_locator="https://www.startrek.com@evil.invalid/videos/very-short-treks-skin-a-cat"))
        self.reject(lambda d: d["description_paraphrases"][4].update(
            publisher_video_locator=OBS["description_paraphrases"][2]["publisher_video_locator"]))

    def test_no_canonical_promotion_in_discovery(self):
        self.reject_catalog(lambda d: d.update(data_status="ADMITTED"))
        self.reject_catalog(lambda d: next(x for x in d["rows"] if
            x["row_id"] == "short:very-short-treks-01").update(
                verification_status="CLOSE_READ"))


if __name__ == "__main__":
    unittest.main()
