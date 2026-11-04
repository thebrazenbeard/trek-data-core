"""Adversarial regression cases for the unadmitted VOY S4 E15–E19 proposal."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("voy_s4e15e19", HERE / "validate.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class HeldCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clean = json.loads((HERE / "records.json").read_text(encoding="utf-8"), object_pairs_hook=MOD.strict_pairs)

    def rejects(self, edit):
        changed = copy.deepcopy(self.clean)
        edit(changed)
        with self.assertRaises(ValueError):
            MOD.validate(changed)

    def test_valid_packet(self):
        MOD.validate(self.clean)

    def test_all_five_rows_immutable(self):
        for index in range(5):
            self.rejects(lambda data, i=index: data["source_local_cards"][i].__setitem__("original_synopsis", "Unverified lore was proved and the canon changed in this full episode."))
            self.rejects(lambda data, i=index: data["source_local_cards"][i].__setitem__("blurb_sha256", "0" * 64))

    def test_blurb_cross_attachment(self):
        for i in range(5):
            for j in range(5):
                if i != j:
                    self.rejects(lambda data, i=i, j=j: data["source_local_cards"][i].__setitem__("blurb_sha256", data["source_local_cards"][j]["blurb_sha256"]))

    def test_publisher_inverted_titles_remain_held(self):
        self.rejects(lambda data: data["source_local_cards"][3].__setitem__("source_title", "The Killing Game, Part 1"))
        self.rejects(lambda data: data["source_local_cards"][4].__setitem__("title_reconciliation", "SAME_GLOBAL_WORK"))

    def test_source_ordinals_and_types(self):
        self.rejects(lambda data: data["source_local_cards"][1].__setitem__("source_ordinal", 18))
        self.rejects(lambda data: data["source_local_cards"][1].__setitem__("source_ordinal", 16.0))
        self.rejects(lambda data: data["source_local_cards"][1].__setitem__("season", True))

    def test_source_and_lineage_changes(self):
        self.rejects(lambda data: data["source"].__setitem__("url", "https://www.paramountplus.com/shows/star_trek_voyager/episodes/5/"))
        self.rejects(lambda data: data["source"].__setitem__("url", "https://www.paramountplus.com/shows/star_trek_voyager/episodes/4/\n"))
        self.rejects(lambda data: data["source"].__setitem__("lineage_group", "INDEPENDENT_FIVE_SOURCES"))
        self.rejects(lambda data: data["source"].__setitem__("independent_corroboration", True))

    def test_fake_raw_source_custody(self):
        self.rejects(lambda data: data["source"].__setitem__("raw_page_sha256", "c" * 64))
        self.rejects(lambda data: data.__setitem__("episode_source_read", True))
        self.rejects(lambda data: data.__setitem__("transcript_or_full_text_read", 0))

    def test_no_work_or_publication_upgrade(self):
        self.rejects(lambda data: data["source_local_cards"][0].__setitem__("work_id", "voy:s4e15"))
        self.rejects(lambda data: data.__setitem__("source_binding_effect", "ACCEPTED"))
        self.rejects(lambda data: data["source_local_cards"][0].__setitem__("synopsis_status", "PUBLISHED"))

    def test_no_unread_media_or_coverage(self):
        self.rejects(lambda data: data["source_local_cards"][0].__setitem__("publisher_image_locator", "https://example.com/still.jpg"))
        self.rejects(lambda data: data["coverage_update"].__setitem__("new_episode_discoveries", 5))
        self.rejects(lambda data: data["coverage_update"].__setitem__("close_reads", False))
        self.rejects(lambda data: data["coverage_update"].__setitem__("released_synopses", 0.0))

    def test_unknown_fields_and_duplicate_json(self):
        self.rejects(lambda data: data.__setitem__("episode_airdate", "1998-02-11"))
        self.rejects(lambda data: data["source_local_cards"][0].__setitem__("publisher_full_blurb", "copied source"))
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"coverage_effect":"NONE","coverage_effect":"ATTAINED"}', object_pairs_hook=MOD.strict_pairs)

    def test_upstream_drift_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture = root / MOD.CSV
            fixture.parent.mkdir(parents=True)
            fixture.write_text("season,episode_number,title\n4,15,Fake\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                MOD.validate(self.clean, repo=root)


if __name__ == "__main__":
    unittest.main()
