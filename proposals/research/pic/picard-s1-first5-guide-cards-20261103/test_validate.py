#!/usr/bin/env python3
"""Hostile source/identity/coverage/thumbnail/synopsis mutation probes."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from validate import HERE, load, validate


class PicardSourceGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load(HERE / "records.json")

    def rejected(self, change):
        packet = copy.deepcopy(self.baseline)
        change(packet)
        with self.assertRaises(ValueError):
            validate(packet)

    def test_source_bound_baseline(self):
        validate(self.baseline)

    def test_duplicate_json_key_fails(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "x.json"
            path.write_text('{"coverage_effect":"NONE","coverage_effect":"CLOSE_READ"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                load(path)

    def test_extra_reconciled_global_work_id(self):
        self.rejected(lambda p: p["source_local_episode_cards"][0].update({"global_work_id": "PICARD_S1E1"}))

    def test_coverage_promotion(self):
        self.rejected(lambda p: p.update({"coverage_effect": "CLOSE_READ"}))

    def test_source_binding_promotion(self):
        self.rejected(lambda p: p.update({"accepted_source_binding_effect": "BOUND"}))

    def test_false_episode_full_content(self):
        self.rejected(lambda p: p["source"].update({"full_primary_audiovisual_content_read": True}))

    def test_false_html_stability(self):
        self.rejected(lambda p: p["source"].update({"publisher_html_stability": "IMMUTABLE"}))

    def test_false_html_hash(self):
        self.rejected(lambda p: p["source"]["raw_sample_receipts"][0].update({"sha256": "0" * 64}))

    def test_missing_external_discovery(self):
        self.rejected(lambda p: p["upstream_discovery"].update({"sha256": "0" * 64}))

    def test_same_host_card_image_substitution(self):
        self.rejected(lambda p: p["source_local_episode_cards"][0].update({"thumbnail_url": p["source_local_episode_cards"][1]["thumbnail_url"]}))

    def test_same_publisher_video_swap(self):
        self.rejected(lambda p: p["source_local_episode_cards"][0].update({"video_url": p["source_local_episode_cards"][1]["video_url"]}))

    def test_duplicate_episode_id(self):
        self.rejected(lambda p: p["source_local_episode_cards"][1].update({"local_id": p["source_local_episode_cards"][0]["local_id"]}))

    def test_episode_title_swap(self):
        self.rejected(lambda p: p["source_local_episode_cards"][0].update({"title": p["source_local_episode_cards"][1]["title"]}))

    def test_forged_entity_mention(self):
        self.rejected(lambda p: p["source_local_episode_cards"][0]["literal_name_mentions"].append("Spock"))

    def test_unreviewed_synopsis_change(self):
        self.rejected(lambda p: p["source_local_episode_cards"][0].update({"synopsis_paraphrase_candidate": "A secret admission is proven."}))

    def test_synopsis_promotion(self):
        self.rejected(lambda p: p["source_local_episode_cards"][0].update({"synopsis_state": "VERIFIED_FULL_EPISODE"}))

    def test_image_rights_forgery(self):
        self.rejected(lambda p: p["source_local_episode_cards"][0].update({"thumbnail_status": "DISPLAY_APPROVED"}))

    def test_invented_image_binary(self):
        self.rejected(lambda p: p["source_local_episode_cards"][0].update({"image_bytes": "aW1hZ2U="}))

    def test_removed_card(self):
        self.rejected(lambda p: p["source_local_episode_cards"].pop())

    def test_reordered_cards(self):
        self.rejected(lambda p: p["source_local_episode_cards"].reverse())


if __name__ == "__main__":
    unittest.main()
