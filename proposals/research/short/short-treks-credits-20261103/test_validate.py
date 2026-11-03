"""Adversarial unit tests for the 10 publisher-article credit observations."""

from __future__ import annotations

import copy
import json
import unittest

try:
    from .validate import HERE, pairs_no_duplicates, strict_file, validate
except ImportError:
    from validate import HERE, pairs_no_duplicates, strict_file, validate


class StrictPublisherCreditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical = json.loads(strict_file(HERE / "observations.json"), object_pairs_hook=pairs_no_duplicates)

    def altered(self, change):
        data = copy.deepcopy(self.canonical)
        change(data)
        with self.assertRaises(ValueError):
            validate(data)

    def test_original(self):
        self.assertEqual(validate(copy.deepcopy(self.canonical)), 10)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"source_bound":false,"source_bound":true}', object_pairs_hook=pairs_no_duplicates)

    def test_added_unknown_root(self):
        self.altered(lambda d: d.update({"work_id": "short-work-01"}))

    def test_source_family_inflation(self):
        self.altered(lambda d: d.update({"independent_upstream_families": 3}))

    def test_claims_video_watched(self):
        self.altered(lambda d: d.update({"audiovisual_viewed": True}))

    def test_claims_source_bound(self):
        self.altered(lambda d: d.update({"source_bound": True}))

    def test_false_public_synopsis(self):
        self.altered(lambda d: d.update({"synopsis_release_effect": "PUBLISHED"}))

    def test_false_explorer_update(self):
        self.altered(lambda d: d.update({"explorer_effect": "UPDATED"}))

    def test_false_coverage(self):
        self.altered(lambda d: d.update({"coverage_effect": "10_WORKS_ADMITTED"}))

    def test_false_work_binding(self):
        self.altered(lambda d: d.update({"work_identity_effect": "RESOLVED"}))

    def test_accepted_source_pin_changed(self):
        self.altered(lambda d: d.update({"accepted_description_observations_sha256": "0" * 64}))

    def test_new_unverified_source(self):
        self.altered(lambda d: d["sources"].append(copy.deepcopy(d["sources"][0])))

    def test_swap_2018_2020_urls(self):
        self.altered(lambda d: d["sources"][0].update({"url": d["sources"][1]["url"]}))

    def test_source_date_swap(self):
        self.altered(lambda d: d["sources"][0].update({"article_published": "2020-08-17"}))

    def test_source_locator_forgery(self):
        self.altered(lambda d: d["sources"][0].update({"read_locator": "article credit lines 41-61; 2026-11-03 web retrieval"}))

    def test_false_raw_html_custody(self):
        self.altered(lambda d: d["sources"][0].update({"raw_html_archived": True}))

    def test_publisher_source_rights(self):
        self.altered(lambda d: d["page_level_artwork_leads"][0].update({"display_rights": "PUBLIC_DOMAIN"}))

    def test_art_bytes_false_claim(self):
        self.altered(lambda d: d["page_level_artwork_leads"][0].update({"bytes_retrieved": True}))

    def test_image_swap(self):
        self.altered(lambda d: d["page_level_artwork_leads"][0].update({"url": d["page_level_artwork_leads"][2]["url"]}))

    def test_image_scope_promotion(self):
        self.altered(lambda d: d["page_level_artwork_leads"][0].update({"scope": "EPISODE_POSTER"}))

    def test_bluray_no_same_as_work(self):
        self.altered(lambda d: d["edition_container_lead"].update({"work_binding": "short:short-treks-01"}))

    def test_bluray_disc_list_not_all_ten(self):
        self.altered(lambda d: d["edition_container_lead"]["publisher_article_nine_titles"].append("Children of Mars"))

    def test_edition_date_swap(self):
        self.altered(lambda d: d["edition_container_lead"].update({"publisher_announced_us_date": "2020-06-03"}))

    def test_title_swap(self):
        self.altered(lambda d: d["credits"][0].update({"title": "Calypso"}))

    def test_duplicate_directory_id(self):
        self.altered(lambda d: d["credits"][1].update({"directory_row_id": d["credits"][0]["directory_row_id"]}))

    def test_credit_source_swap(self):
        self.altered(lambda d: d["credits"][5].update({"source_id": d["credits"][0]["source_id"]}))

    def test_credit_locator_forgery(self):
        self.altered(lambda d: d["credits"][0].update({"credit_locator": "Runaway credit follows page heading"}))

    def test_teleplay_misattributed_to_written(self):
        self.altered(lambda d: d["credits"][1].update({"written_by": ["Michael Chabon"], "teleplay_by": []}))

    def test_story_credit_order_swap(self):
        self.altered(lambda d: d["credits"][1].update({"story_by": ["Michael Chabon", "Sean Cochran"]}))

    def test_director_swap(self):
        self.altered(lambda d: d["credits"][6].update({"directed_by": ["Daniel Gray Longino"]}))

    def test_credited_name_typo(self):
        self.altered(lambda d: d["credits"][3].update({"written_by": ["Mike McMahan"]}))

    def test_synopsis_unheld(self):
        self.altered(lambda d: d["credits"][0].update({"synopsis_status": "PUBLIC"}))

    def test_new_episode_image_claim(self):
        self.altered(lambda d: d["credits"][8].update({"episode_artwork_status": "PUBLISHED_POSTER"}))


if __name__ == "__main__":
    unittest.main()
