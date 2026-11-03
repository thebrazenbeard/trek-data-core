#!/usr/bin/env python3
"""Adversarial source/corpus publication-gate tests for Picard S2 E6–10."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from validate import HERE, load, validate


class PicardSeason2LastFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = load(HERE / "records.json")

    def test_validated_source_relative_baseline(self):
        self.assertEqual(validate(self.reference), 5)

    def test_duplicate_json_keys_fail_closed(self):
        bad = ('{"episode_number":6,"episode_number":5}',
               '{"source":{"http_status":200,"http_status":404}}',
               '{"media":{"thumbnail_status":"HELD","thumbnail_status":"LICENSED"}}')
        for content in bad:
            with self.subTest(content=content):
                with tempfile.TemporaryDirectory() as directory:
                    file = Path(directory) / "duplicate.json"
                    file.write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                        load(file)

    def test_hostile_scope_and_provenance_forgery(self):
        changes = [
            ("accepted Work", lambda x: x.update({"accepted_work_effect": "CREATE"})),
            ("source binding", lambda x: x.update({"accepted_source_binding_effect": "SOURCE_BOUND"})),
            ("coverage inflation", lambda x: x.update({"coverage_effect": "CLOSE_READ"})),
            ("denominator inflation", lambda x: x.update({"denominator_effect": "5"})),
            ("proposal promotion", lambda x: x.update({"proposal_only": False})),
            ("role forgery", lambda x: x.update({"role": "CONSOLIDATOR"})),
            ("fake full episode read", lambda x: x["source"].update({"full_primary_audiovisual_content_read": True})),
            ("fake immutable page", lambda x: x["source"].update({"publisher_html_stability": "IMMUTABLE"})),
            ("fake archived HTML", lambda x: x["source"].update({"raw_html_retained_in_public_repo": True})),
            ("fake sample hash", lambda x: x["source"]["raw_sample_receipts"][0].update({"sha256": "0" * 64})),
            ("fake sample byte length", lambda x: x["source"]["raw_sample_receipts"][1].update({"bytes": 10})),
            ("Boolean status", lambda x: x["source"].update({"http_status": True})),
            ("fake publisher lineage", lambda x: x["source"].update({"independence_group": "separate sources"})),
            ("fake provider", lambda x: x["source"].update({"provider": "Memory Alpha"})),
            ("source URL drift", lambda x: x["source"].update({"url": "https://example.org/"})),
            ("observation date drift", lambda x: x["source"].update({"retrieval_date_utc": "2020-01-01"})),
            ("promoted Wikidata title lead", lambda x: x["prior_lead_index"].update({"scope": "FULL_SOURCE_CORROBORATION"})),
            ("altered discovery SHA", lambda x: x["prior_lead_index"].update({"sha256": "0" * 64})),
            ("lead lineage laundering", lambda x: x["prior_lead_index"].update({"source_group": "paramountplus.com"})),
            ("lead order switched", lambda x: x["prior_lead_index"]["row_ids"].reverse()),
            ("wrong season", lambda x: x["source_local_episode_cards"][0].update({"season": 1})),
            ("Boolean episode number", lambda x: x["source_local_episode_cards"][0].update({"episode_number": True})),
            ("first-five identity overlap", lambda x: x["source_local_episode_cards"][0].update({"local_id": "pic-s2-e01-pplus-guide"})),
            ("wrong title", lambda x: x["source_local_episode_cards"][0].update({"title": "Twin of One"})),
            ("wrong line", lambda x: x["source_local_episode_cards"][1].update({"guide_line_window": [0, 1]})),
            ("wrong video domain", lambda x: x["source_local_episode_cards"][1].update({"video_url": "https://unknown.example/watch/"})),
            ("same-publisher swapped video", lambda x: x["source_local_episode_cards"][1].update({"video_url": x["source_local_episode_cards"][2]["video_url"]})),
            ("wrong image host", lambda x: x["source_local_episode_cards"][2].update({"thumbnail_url": "https://unknown.example/picard.jpg"})),
            ("same-CDN swapped image", lambda x: x["source_local_episode_cards"][2].update({"thumbnail_url": x["source_local_episode_cards"][3]["thumbnail_url"]})),
            ("invented license", lambda x: x["source_local_episode_cards"][2].update({"thumbnail_status": "LICENSED"})),
            ("public synopsis", lambda x: x["source_local_episode_cards"][3].update({"synopsis_state": "PUBLIC"})),
            ("unreviewed paraphrase", lambda x: x["source_local_episode_cards"][3].update({"synopsis_paraphrase_candidate": "Different theory"})),
            ("invented mention", lambda x: x["source_local_episode_cards"][4]["literal_name_mentions"].append("Borg")),
            ("promoted description into scene fact", lambda x: x["source_local_episode_cards"][4].update({"evidence_scope": "DEPICTED_CANON"})),
            ("copyrighted blurb injection", lambda x: x["source_local_episode_cards"][0].update({"full_description": "BAD"})),
            ("card reorder", lambda x: x["source_local_episode_cards"].reverse()),
            ("card removed", lambda x: x["source_local_episode_cards"].pop()),
            ("duplicate card", lambda x: x["source_local_episode_cards"].append(copy.deepcopy(x["source_local_episode_cards"][0]))),
            ("unexpected public payload", lambda x: x.update({"public_artwork_url": "https://example.org/"})),
        ]
        for name, mutate in changes:
            with self.subTest(forgery=name):
                packet = copy.deepcopy(self.reference)
                mutate(packet)
                with self.assertRaises(ValueError):
                    validate(packet)


if __name__ == "__main__":
    unittest.main()
