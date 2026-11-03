#!/usr/bin/env python3
"""Source-first hostile mutation tests for held Picard Season 2 guide cards."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from validate import HERE, load, validate


class PicardS2GuideCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load(HERE / "records.json")

    def test_exact_source_local_baseline(self):
        self.assertEqual(validate(self.baseline), 5)

    def test_duplicate_json_keys_rejected(self):
        for raw in ('{"rights":"HELD","rights":"LICENSED"}',
                    '{"card":{"episode_number":2,"episode_number":1}}'):
            with self.subTest(raw=raw):
                with tempfile.TemporaryDirectory() as folder:
                    target = Path(folder) / "duplicate.json"
                    target.write_text(raw, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                        load(target)

    def test_authority_and_source_adversarial_cases(self):
        probes = [
            ("accepted Work", lambda d: d.update({"accepted_work_effect": "CREATE"})),
            ("accepted Source–Work binding", lambda d: d.update({"accepted_source_binding_effect": "SOURCE_BOUND"})),
            ("coverage promotion", lambda d: d.update({"coverage_effect": "FULL_TEXT_AVAILABLE"})),
            ("denominator growth", lambda d: d.update({"denominator_effect": "5"})),
            ("audio-visual close read forged", lambda d: d["source"].update({"full_primary_audiovisual_content_read": True})),
            ("raw page stability forged", lambda d: d["source"].update({"publisher_html_stability": "IMMUTABLE"})),
            ("raw page capture forged", lambda d: d["source"].update({"raw_html_retained_in_public_repo": True})),
            ("raw HTML digest tampered", lambda d: d["source"]["raw_sample_receipts"][0].update({"sha256": "0" * 64})),
            ("raw HTML 200 bool masquerade", lambda d: d["source"].update({"http_status": True})),
            ("false source independence", lambda d: d["source"].update({"independence_group": "third_party"})),
            ("publisher URL substituted", lambda d: d["source"].update({"url": "https://memory-alpha.fandom.com/wiki/Picard"})),
            ("source date falsified", lambda d: d["source"].update({"retrieval_date_utc": "2020-01-01"})),
            ("incorrect season", lambda d: d["source_local_episode_cards"][0].update({"season": 1})),
            ("Boolean episode number", lambda d: d["source_local_episode_cards"][0].update({"episode_number": True})),
            ("global identity claim", lambda d: d["source_local_episode_cards"][1].update({"local_id": "picard:global:ep02"})),
            ("publisher slot title false", lambda d: d["source_local_episode_cards"][2].update({"title": "The Watcher"})),
            ("guide line locator false", lambda d: d["source_local_episode_cards"][2].update({"guide_line_window": [1, 2]})),
            ("video URL external host", lambda d: d["source_local_episode_cards"][3].update({"video_url": "https://example.com/stream"})),
            ("video swapped", lambda d: d["source_local_episode_cards"][1].update({"video_url": d["source_local_episode_cards"][2]["video_url"]})),
            ("same-CDN image swapped", lambda d: d["source_local_episode_cards"][1].update({"thumbnail_url": d["source_local_episode_cards"][2]["thumbnail_url"]})),
            ("copyright clearance invented", lambda d: d["source_local_episode_cards"][4].update({"thumbnail_status": "LICENSED"})),
            ("source text mention fabricated", lambda d: d["source_local_episode_cards"][4]["literal_name_mentions"].append("Morn")),
            ("publisher utterance elevated to plot fact", lambda d: d["source_local_episode_cards"][3].update({"evidence_scope": "ONSCREEN_CANON"})),
            ("synopsis rewritten without evidence", lambda d: d["source_local_episode_cards"][4].update({"synopsis_paraphrase_candidate": "Q wins"})),
            ("synopsis publicly published", lambda d: d["source_local_episode_cards"][2].update({"synopsis_state": "PUBLIC"})),
            ("whole copyrighted publisher description injected", lambda d: d["source_local_episode_cards"][2].update({"full_description": "COPY"})),
            ("missing card", lambda d: d["source_local_episode_cards"].pop()),
            ("duplicate card", lambda d: d["source_local_episode_cards"].append(copy.deepcopy(d["source_local_episode_cards"][0]))),
            ("misordered cards", lambda d: d["source_local_episode_cards"].reverse()),
            ("upstream discovery hash tampered", lambda d: d["upstream_discovery"].update({"sha256": "0" * 64})),
        ]
        for label, mutate in probes:
            with self.subTest(forgery=label):
                packet = copy.deepcopy(self.baseline)
                mutate(packet)
                with self.assertRaises(ValueError):
                    validate(packet)


if __name__ == "__main__":
    unittest.main()
