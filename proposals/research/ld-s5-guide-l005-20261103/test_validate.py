"""Hostile source/rights/identity and own-card binding probes for LD S5 L005."""
import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate import HERE, read_json, validate


class LDS5PublisherCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid = read_json(HERE / "observations.json")

    def bad(self, mutation):
        obj = copy.deepcopy(self.valid)
        mutation(obj)
        with self.assertRaises(ValueError):
            validate(obj)

    def test_baseline(self):
        self.assertEqual(validate(self.valid), 10)

    def test_missing_card(self):
        self.bad(lambda x: x["records"].pop())

    def test_duplicate_card_id(self):
        self.bad(lambda x: x["records"][1].update(observation_id=x["records"][0]["observation_id"]))

    def test_order_swap(self):
        self.bad(lambda x: x["records"].reverse())

    def test_slot_forgery(self):
        self.bad(lambda x: x["records"][0].update(episode=2))

    def test_bool_slot_forgery(self):
        self.bad(lambda x: x["records"][0].update(episode=True))

    def test_title_forgery(self):
        self.bad(lambda x: x["records"][0].update(publisher_card_title="Shades of Green"))

    def test_same_publisher_video_swap(self):
        self.bad(lambda x: x["records"][0].update(video_url=x["records"][1]["video_url"]))

    def test_same_host_image_swap(self):
        self.bad(lambda x: x["records"][0].update(thumbnail_url=x["records"][1]["thumbnail_url"]))

    def test_own_card_combined_video_image_swap(self):
        self.bad(lambda x: x["records"][0].update(video_url=x["records"][1]["video_url"],thumbnail_url=x["records"][1]["thumbnail_url"]))

    def test_description_digest_swap(self):
        self.bad(lambda x: x["records"][0].update(publisher_description_sha256=x["records"][1]["publisher_description_sha256"]))

    def test_own_card_media_and_digest_swap(self):
        self.bad(lambda x: x["records"][0].update(video_url=x["records"][1]["video_url"],thumbnail_url=x["records"][1]["thumbnail_url"],publisher_description_sha256=x["records"][1]["publisher_description_sha256"]))

    def test_forged_literal_name(self):
        self.bad(lambda x: x["records"][0]["literal_mentions"].append("Kirk"))

    def test_literal_utterance_promoted(self):
        self.bad(lambda x: x["records"][0].update(literal_mention_scope="VERIFIED_ONSCREEN_ACTION"))

    def test_synopsis_edit(self):
        self.bad(lambda x: x["records"][0].update(synopsis_paraphrase_candidate="Verified full episode confirms this plot."))

    def test_synopsis_publication(self):
        self.bad(lambda x: x["records"][0].update(synopsis_status="APPROVED_PUBLIC_SYNOPSIS"))

    def test_artwork_rights_forgery(self):
        self.bad(lambda x: x["records"][0].update(artwork_rights_status="LICENSED_PUBLIC_DISPLAY"))

    def test_artwork_download_forgery(self):
        self.bad(lambda x: x["records"][0].update(image_bytes_retrieved=True))

    def test_work_binding_forgery(self):
        self.bad(lambda x: x["records"][0].update(accepted_work_id="lower-decks-s5e1"))

    def test_unknown_authenticity_key(self):
        self.bad(lambda x: x["records"][0].update(authenticated_full_video=True))

    def test_false_source_lineage(self):
        self.bad(lambda x: x.update(source_independence_status="TWO_INDEPENDENT_PUBLISHERS"))

    def test_accepted_main_hash_swap(self):
        self.bad(lambda x: x.update(accepted_main_at_selection="0"*40))

    def test_raw_html_stability_forgery(self):
        self.bad(lambda x: x.update(current_raw_html_archived=True))

    def test_source_receipt_forgery(self):
        self.bad(lambda x: x.update(current_raw_html_sha256_observed="0"*64))

    def test_accepted_discovery_digest_swap(self):
        self.bad(lambda x: x.update(historical_s5_csv_sha256="0"*64))

    def test_accepted_work_effect(self):
        self.bad(lambda x: x.update(accepted_work_effect="ADMITTED"))

    def test_coverage_promotion(self):
        self.bad(lambda x: x.update(coverage_effect="CLOSE_READ"))

    def test_public_artwork_promotion(self):
        self.bad(lambda x: x.update(public_artwork_effect="PUBLISH"))

    def test_extra_root_accepted_effect(self):
        self.bad(lambda x: x.update(verified_global_episode_ids=10))

    def test_duplicate_raw_json_key_normal_and_optimized(self):
        raw=(HERE/"observations.json").read_text(encoding="utf-8")
        attack=raw.replace('"coverage_effect": "NONE"','"coverage_effect": "CLOSE_READ", "coverage_effect": "NONE"',1)
        self.assertNotEqual(attack,raw)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"forgery.json"
            path.write_text(attack,encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"duplicate JSON key"):
                read_json(path)
            for optimize in (False,True):
                run=subprocess.run([sys.executable,*(["-O"] if optimize else []),"-c",
                                    "from validate import read_json;import pathlib,sys;read_json(pathlib.Path(sys.argv[1]))",
                                    str(path)],cwd=HERE,capture_output=True,text=True,check=False)
                self.assertNotEqual(run.returncode,0)
                self.assertIn("duplicate JSON key",run.stderr)


if __name__ == "__main__":
    unittest.main()
