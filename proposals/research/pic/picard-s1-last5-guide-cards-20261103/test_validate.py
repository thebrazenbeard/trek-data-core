#!/usr/bin/env python3
"""Adversarial source/identity/synopsis/artwork admission probes for PIC P002."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from validate import HERE, load, validate


class PicardLastFiveGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load(HERE / "records.json")

    def rejected(self, edit):
        packet = copy.deepcopy(self.baseline)
        edit(packet)
        with self.assertRaises(ValueError):
            validate(packet)

    def test_exact_retrieved_source_cards(self):
        self.assertEqual(validate(self.baseline), 5)

    def test_duplicate_json_keys_fail_closed(self):
        for bad in ('{"a":1,"a":2}', '{"outer":{"video_url":"safe","video_url":"bad"}}'):
            with self.subTest(raw=bad):
                with tempfile.TemporaryDirectory() as folder:
                    source = Path(folder) / "forged.json"
                    source.write_text(bad, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                        load(source)

    def test_adversarial_mutations_rejected(self):
        cases = [
            ("new global work", lambda d: d.update({"accepted_work_effect": "PROMOTE"})),
            ("coverage assertion", lambda d: d.update({"coverage_effect": "CLOSE_READ"})),
            ("denominator inflation", lambda d: d.update({"denominator_effect": "FIVE"})),
            ("accepted source binding", lambda d: d.update({"accepted_source_binding_effect": "SOURCE_BOUND"})),
            ("fake actual episode read", lambda d: d["source"].update({"full_primary_audiovisual_content_read": True})),
            ("fake raw HTML stable", lambda d: d["source"].update({"publisher_html_stability": "IMMUTABLE"})),
            ("forge raw hash", lambda d: d["source"]["raw_sample_receipts"][0].update({"sha256": "0" * 64})),
            ("publisher domain swap", lambda d: d["source"].update({"url": "https://memory-alpha.fandom.com/"})),
            ("independence laundering", lambda d: d["source"].update({"independence_group": "independent"})),
            ("unreviewed title", lambda d: d["source_local_episode_cards"][0].update({"title": "Another title"})),
            ("Boolean episode", lambda d: d["source_local_episode_cards"][0].update({"episode_number": True})),
            ("first five overlap", lambda d: d["source_local_episode_cards"][0].update({"local_id": "pic-s1-e01-pplus-guide"})),
            ("fake publisher video", lambda d: d["source_local_episode_cards"][1].update({"video_url": "https://paramountplus.com/watch/"})),
            ("swapped episode video", lambda d: d["source_local_episode_cards"][1].update({"video_url": d["source_local_episode_cards"][0]["video_url"]})),
            ("same-host swapped image", lambda d: d["source_local_episode_cards"][2].update({"thumbnail_url": d["source_local_episode_cards"][3]["thumbnail_url"]})),
            ("false image clearance", lambda d: d["source_local_episode_cards"][2].update({"thumbnail_status": "LICENSED"})),
            ("injected depiction fact", lambda d: d["source_local_episode_cards"][1].update({"evidence_scope": "EPISODE_FACT"})),
            ("name not in description", lambda d: d["source_local_episode_cards"][3]["literal_name_mentions"].append("Q")),
            ("unreviewed synopsis", lambda d: d["source_local_episode_cards"][4].update({"synopsis_paraphrase_candidate": "New interpretation"})),
            ("public synopsis promotion", lambda d: d["source_local_episode_cards"][4].update({"synopsis_state": "PUBLIC"})),
            ("unexpected copyrighted blurb", lambda d: d["source_local_episode_cards"][2].update({"full_publisher_blurb": "not allowed"})),
            ("duplicated card", lambda d: d["source_local_episode_cards"].append(copy.deepcopy(d["source_local_episode_cards"][4]))),
            ("dropped card", lambda d: d["source_local_episode_cards"].pop()),
            ("reordered card", lambda d: d["source_local_episode_cards"].reverse()),
            ("wrong source locator lines", lambda d: d["source_local_episode_cards"][1].update({"guide_line_window": [0, 1]})),
            ("injected source field", lambda d: d["source"].update({"license": "granted"})),
            ("changed upstream SHA", lambda d: d["upstream_discovery"].update({"sha256": "0" * 64})),
        ]
        for label, edit in cases:
            with self.subTest(forgery=label):
                self.rejected(edit)


if __name__ == "__main__":
    unittest.main()
