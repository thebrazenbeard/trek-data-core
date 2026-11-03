"""Adversarial metadata, source, rights and identity custody tests for LD L002."""
import copy
import tempfile
import unittest
from pathlib import Path

from validate import HERE, read_json, validate


class LDS2SourceGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = read_json(HERE / "observations.json")

    def reject(self, change):
        packet = copy.deepcopy(self.baseline)
        change(packet)
        with self.assertRaises(ValueError):
            validate(packet)

    def test_baseline(self):
        self.assertEqual(validate(self.baseline), 10)

    def test_duplicate_raw_key(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "attack.json"
            p.write_text('{"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                read_json(p)

    def test_extra_acceptance_claim(self):
        self.reject(lambda p: p.update(verified_primary_episode_viewed=True))

    def test_extra_accepted_global_work(self):
        self.reject(lambda p: p["records"][0].update(global_work_id="ld-s2e1"))

    def test_false_accepted_source_work(self):
        self.reject(lambda p: p.update(accepted_source_work_effect="SOURCE_BOUND"))

    def test_false_accepted_work(self):
        self.reject(lambda p: p.update(accepted_work_effect="WORK_ADMITTED"))

    def test_false_coverage(self):
        self.reject(lambda p: p.update(coverage_effect="CLOSE_READ"))

    def test_false_public_art(self):
        self.reject(lambda p: p.update(public_artwork_effect="PUBLISH"))

    def test_false_public_synopsis(self):
        self.reject(lambda p: p.update(public_synopsis_effect="PUBLISH"))

    def test_false_own_episode_read(self):
        self.reject(lambda p: p.update(actual_episode_or_script_read=True))

    def test_forged_independent_publisher(self):
        self.reject(lambda p: p.update(source_independence_status="INDEPENDENT_SECOND_SOURCE"))

    def test_source_url_replaced(self):
        self.reject(lambda p: p.update(publisher_guide_url="https://example.com/"))

    def test_historical_digest_changed(self):
        self.reject(lambda p: p.update(historical_s2_first5_csv_sha256="0"*64))

    def test_fake_immutable_html(self):
        self.reject(lambda p: p.update(current_raw_html_archived=True))

    def test_forged_raw_digest(self):
        self.reject(lambda p: p.update(current_raw_html_sha256_observed="0"*64))

    def test_reordered_cards(self):
        self.reject(lambda p: p["records"].reverse())

    def test_missing_card(self):
        self.reject(lambda p: p["records"].pop())

    def test_duplicated_card(self):
        self.reject(lambda p: p["records"].__setitem__(1, copy.deepcopy(p["records"][0])))

    def test_title_swap(self):
        self.reject(lambda p: p["records"][0].update(publisher_card_title="No Small Parts"))

    def test_episode_slot_changed(self):
        self.reject(lambda p: p["records"][0].update(episode=2))

    def test_forged_mentions(self):
        self.reject(lambda p: p["records"][0]["literal_mentions"].append("Q"))

    def test_episode_story_claim(self):
        self.reject(lambda p: p["records"][0].update(evidence_scope="VERIFIED_DEPICTED_EVENT"))

    def test_identity_promoted(self):
        self.reject(lambda p: p["records"][0].update(accepted_work_id="LD-2-1"))

    def test_hidden_synopsis(self):
        self.reject(lambda p: p["records"][0].update(synopsis_text="The show depicts a fact."))

    def test_forged_art_rights(self):
        self.reject(lambda p: p["records"][0].update(artwork_rights_status="PUBLIC_DISPLAY_GRANTED"))

    def test_unreviewed_art_asset(self):
        self.reject(lambda p: p["records"][0].update(artwork_asset_url="https://thumbnails.cbsig.net/a.jpg"))

    def test_bad_source_page(self):
        self.reject(lambda p: p["records"][0].update(artwork_candidate_page_url="https://example.com/"))

    def test_boolean_episode_number(self):
        self.reject(lambda p: p["records"][0].update(episode=True))


if __name__ == "__main__":
    unittest.main()
