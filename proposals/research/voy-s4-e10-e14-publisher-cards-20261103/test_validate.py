"""Adversarial checks for the immutable HELD VOY publisher-card tranche."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("voy_s4_e10e14_validator", HERE / "validate.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class SourceCardValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clean = json.loads((HERE / "records.json").read_text(encoding="utf-8"), object_pairs_hook=MOD.strict_pairs)

    def rejected(self, mutate):
        altered = copy.deepcopy(self.clean)
        mutate(altered)
        with self.assertRaises(ValueError):
            MOD.validate(altered)

    def test_valid(self):
        MOD.validate(self.clean)

    def test_all_source_rows_content_pinned(self):
        for index in range(5):
            self.rejected(lambda x, i=index: x["source_local_cards"][i].__setitem__("original_synopsis", "Invented statement about lore and source scene " * 2))
            self.rejected(lambda x, i=index: x["source_local_cards"][i].__setitem__("blurb_sha256", "0" * 64))

    def test_cross_row_blurb_swaps(self):
        for i in range(5):
            for j in range(5):
                if i == j:
                    continue
                self.rejected(lambda x, i=i, j=j: x["source_local_cards"][i].__setitem__("blurb_sha256", x["source_local_cards"][j]["blurb_sha256"]))

    def test_title_and_source_ordinal_forgery(self):
        self.rejected(lambda x: x["source_local_cards"][0].__setitem__("source_title", "False title"))
        self.rejected(lambda x: x["source_local_cards"][0].__setitem__("source_ordinal", 11))
        self.rejected(lambda x: x["source_local_cards"][0].__setitem__("source_ordinal", True))

    def test_publisher_typo_not_silently_reconciled(self):
        self.rejected(lambda x: x["source_local_cards"][3].__setitem__("source_title", "Waking Moments"))
        self.rejected(lambda x: x["source_local_cards"][3].__setitem__("title_reconciliation", "GLOBAL_EQUIVALENCE_VERIFIED"))

    def test_unapproved_coverage(self):
        self.rejected(lambda x: x["coverage_update"].__setitem__("new_episode_discoveries", 5))
        self.rejected(lambda x: x["coverage_update"].__setitem__("accepted_work_bindings", 1))
        self.rejected(lambda x: x.__setitem__("coverage_effect", "ADVANCED"))

    def test_unapproved_publishing_and_editorial(self):
        self.rejected(lambda x: x["source_local_cards"][2].__setitem__("synopsis_status", "APPROVED_PUBLIC"))
        self.rejected(lambda x: x.__setitem__("rights_or_publication_effect", "GRANTED"))

    def test_unread_media_links_rejected(self):
        self.rejected(lambda x: x["source_local_cards"][2].__setitem__("publisher_image_locator", "https://images.prismic.io/synthetic.png"))
        self.rejected(lambda x: x["source_local_cards"][2].__setitem__("publisher_video_locator", "https://www.paramountplus.com/shows/video/anything"))

    def test_unapproved_work_identity(self):
        self.rejected(lambda x: x["source_local_cards"][0].__setitem__("work_id", "voy:s4e10"))
        self.rejected(lambda x: x.__setitem__("global_work_identity_effect", "VERIFIED"))

    def test_source_lineage_and_url_changed(self):
        self.rejected(lambda x: x["source"].__setitem__("url", "https://www.paramountplus.com/shows/star_trek_voyager/episodes/3/"))
        self.rejected(lambda x: x["source"].__setitem__("lineage_group", "TWO_INDEPENDENT_SOURCES"))
        self.rejected(lambda x: x["source"].__setitem__("independent_corroboration", True))

    def test_false_raw_custody_source_read(self):
        self.rejected(lambda x: x["source"].__setitem__("raw_page_sha256", "e" * 64))
        self.rejected(lambda x: x.__setitem__("episode_source_read", True))
        self.rejected(lambda x: x.__setitem__("images_or_videos_retrieved", True))
        self.rejected(lambda x: x["source"].__setitem__("direct_lappy_http_result", "HTTP_200"))

    def test_duplicate_key_and_schema_poisoning(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            json.loads('{"status":"HELD_PROPOSAL_ONLY","status":"ADMITTED"}', object_pairs_hook=MOD.strict_pairs)
        self.rejected(lambda x: x.__setitem__("episode_airdate", "1997-01-01"))
        self.rejected(lambda x: x["source_local_cards"][0].__setitem__("full_description", "copyrighted blurb"))

    def test_upstream_source_snapshot_drift(self):
        self.rejected(lambda x: x["source"].__setitem__("upstream_discovery_sha256", "0" * 64))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / MOD.UPSTREAM_CSV
            p.parent.mkdir(parents=True)
            p.write_text('season,episode_number,title\n4,10,Fake\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                MOD.validate(self.clean, repo=root)


if __name__ == "__main__":
    unittest.main()
