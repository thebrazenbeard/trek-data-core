#!/usr/bin/env python3
"""Adversarial source/corpus publication-gate tests for Picard S2 E6–10."""
from __future__ import annotations

import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from validate import HERE, load, source_card_bindings, validate


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
            ("changed description fingerprint algorithm", lambda x: x["source"].update({"description_digest_method": "SHA1"})),
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
            ("same-source crossrow description digest 6/7", lambda x: x["source_local_episode_cards"][0].update({"publisher_description_sha256": x["source_local_episode_cards"][1]["publisher_description_sha256"]})),
            ("same-source crossrow digest and length", lambda x: x["source_local_episode_cards"][1].update({"publisher_description_sha256": x["source_local_episode_cards"][2]["publisher_description_sha256"], "publisher_description_codepoints": x["source_local_episode_cards"][2]["publisher_description_codepoints"]})),
            ("same-source length reassignment", lambda x: x["source_local_episode_cards"][3].update({"publisher_description_codepoints": x["source_local_episode_cards"][4]["publisher_description_codepoints"]})),
            ("plausible but unsourced digest", lambda x: x["source_local_episode_cards"][2].update({"publisher_description_sha256": "f" * 64})),
            ("wrong digest length type", lambda x: x["source_local_episode_cards"][4].update({"publisher_description_codepoints": True})),
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

    def test_optional_actual_html_card_parser_and_rebind_falsifier(self):
        """Synthetic HTML checks the parser; actual publisher prose is not copied."""
        cards = []
        for episode in range(1, 11):
            if episode > 5:
                source = self.reference["source_local_episode_cards"][episode - 6]
                title = source["title"]
                video = source["video_url"].replace("https://www.paramountplus.com", "")
                image = source["thumbnail_url"]
            else:
                title = f"Synthetic {episode}"
                video = f"/shows/video/Synthetic{episode:02d}/"
                image = f"https://thumbnails.cbsig.net/fixtures/{episode}.jpg"
            description = f"Synthetic episode {episode} test marker only, no publisher copy"
            cards.append(
                '<div class="episode"><a href="' + video + '" aa-link="episodes||Star Trek: Picard - ' +
                title + '|' + str(episode) + '|"><img src="' + image + '"></a><h2>' + title +
                '</h2><div id="js-episode-copy">' + description + '</div></div>'
            )
        fake_page = "".join(cards)
        observed = source_card_bindings(fake_page)
        self.assertEqual(len(observed), 10)
        self.assertEqual(observed[5]["publisher_description_sha256"],
                         hashlib.sha256(b"Synthetic episode 6 test marker only, no publisher copy").hexdigest())
        with self.assertRaisesRegex(ValueError, "primary HTML card 6 rebind"):
            validate(self.reference, source_html=fake_page)
        # Reassigning a same-host description across two otherwise correct
        # card anchors must not be accepted as verified first-party binding.
        swapped_page = fake_page.replace(
            "Synthetic episode 6 test marker only, no publisher copy",
            "Synthetic episode 7 test marker only, no publisher copy",
            1,
        )
        with self.assertRaises(ValueError):
            validate(self.reference, source_html=swapped_page)


if __name__ == "__main__":
    unittest.main()
