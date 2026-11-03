"""Adversarial source, description, rights and Work-custody probes for LD L003."""
import copy
import tempfile
import unittest
from pathlib import Path

from validate import HERE, read_json, validate


class LDS3SourceGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = read_json(HERE / "observations.json")

    def reject(self, mutation):
        obj = copy.deepcopy(self.baseline)
        mutation(obj)
        with self.assertRaises(ValueError):
            validate(obj)

    def test_baseline(self):
        self.assertEqual(validate(self.baseline), 10)

    def test_raw_duplicate_key(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "attack.json"
            p.write_text('{"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                read_json(p)

    def test_accepted_source_forgery(self):
        self.reject(lambda p: p.update(accepted_source_work_effect="SOURCE_BOUND"))

    def test_accepted_work_forgery(self):
        self.reject(lambda p: p.update(accepted_work_effect="ADMITTED"))

    def test_close_read_forgery(self):
        self.reject(lambda p: p.update(coverage_effect="CLOSE_READ"))

    def test_episode_view_forgery(self):
        self.reject(lambda p: p.update(actual_episode_or_script_read=True))

    def test_source_lineage_forgery(self):
        self.reject(lambda p: p.update(source_independence_status="INDEPENDENT_PUBLISHER"))

    def test_source_url_swap(self):
        self.reject(lambda p: p.update(publisher_guide_url="https://example.com/"))

    def test_new_unrecognized_authenticity_field(self):
        self.reject(lambda p: p.update(verified_full_episodes=True))

    def test_fake_accepted_main(self):
        self.reject(lambda p: p.update(accepted_main_at_selection="0"*40))

    def test_changed_historical_digest(self):
        self.reject(lambda p: p.update(historical_s3_bundle_sha256="0"*64))

    def test_fake_raw_html_archive(self):
        self.reject(lambda p: p.update(current_raw_html_archived=True))

    def test_changed_current_html_receipt(self):
        self.reject(lambda p: p.update(current_raw_html_sha256_observed="0"*64))

    def test_public_synopsis_promotion(self):
        self.reject(lambda p: p.update(public_synopsis_effect="PUBLISH"))

    def test_public_image_promotion(self):
        self.reject(lambda p: p.update(public_artwork_effect="PUBLISH"))

    def test_wrong_count(self):
        self.reject(lambda p: p["records"].pop())

    def test_duplicate_row(self):
        self.reject(lambda p: p["records"].__setitem__(1,copy.deepcopy(p["records"][0])))

    def test_reordered_rows(self):
        self.reject(lambda p: p["records"].reverse())

    def test_episode_number_swap(self):
        self.reject(lambda p: p["records"][0].update(episode=2))

    def test_boolean_episode_number(self):
        self.reject(lambda p: p["records"][0].update(episode=True))

    def test_source_title_swap(self):
        self.reject(lambda p: p["records"][0].update(publisher_card_title="Reflections"))

    def test_description_fingerprint_forgery(self):
        self.reject(lambda p: p["records"][0].update(publisher_description_sha256="0"*64))

    def test_false_literal_mention(self):
        self.reject(lambda p: p["records"][0]["literal_mentions"].append("Kirk"))

    def test_episode_depiction_promotion(self):
        self.reject(lambda p: p["records"][0].update(evidence_scope="VERIFIED_SCENE"))

    def test_global_work_forgery(self):
        self.reject(lambda p: p["records"][0].update(accepted_work_id="LD-S3-1"))

    def test_unapproved_synopsis(self):
        self.reject(lambda p: p["records"][0].update(synopsis_text="Full episode truth."))

    def test_asset_forgery(self):
        self.reject(lambda p: p["records"][0].update(artwork_asset_url="https://thumbnails.cbsig.net/a.jpg"))

    def test_rights_forgery(self):
        self.reject(lambda p: p["records"][0].update(artwork_rights_status="DISPLAY_LICENSED"))

    def test_unauthorized_page_swap(self):
        self.reject(lambda p: p["records"][0].update(artwork_candidate_page_url="https://example.org/"))


if __name__ == "__main__":
    unittest.main()
