"""Adversarial checks: salvage cannot become metadata verification or publication."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "proposals/research/voyager/b006-publisher-synopsis-drafts-20261103"
SPEC = importlib.util.spec_from_file_location("voy_b006_draft_validate", BASE / "validate.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class VoyagerSynopsisDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads((BASE / "records.json").read_text(encoding="utf-8"))

    def invalid(self, edit):
        data = copy.deepcopy(self.packet)
        edit(data)
        with self.assertRaises(ValueError):
            MOD.validate(data)

    def test_original_valid(self):
        self.assertEqual(MOD.validate(), 12)

    def test_source_hash_required(self):
        self.invalid(lambda d: d.__setitem__("accepted_metadata_sha256", "0" * 64))

    def test_source_path_cannot_be_retconned(self):
        self.invalid(lambda d: d.__setitem__("accepted_metadata_source", "explorer/research-leads.json"))

    def test_no_coverage_or_work_admission(self):
        for field, value in (("work_admission_effect", "ADMIT"), ("coverage_effect", "CLOSE_READ"),
                             ("verification_counter_effect", "INCREMENT"), ("publication_approval", "APPROVED")):
            with self.subTest(field=field):
                self.invalid(lambda d, f=field, v=value: d.__setitem__(f, v))

    def test_no_fake_video_viewing_or_page_custody(self):
        self.invalid(lambda d: d.__setitem__("episodes_viewed", 13))
        self.invalid(lambda d: d.__setitem__("raw_webpage_bytes_custodied", True))

    def test_caretaker_multipart_is_not_silently_resolved(self):
        self.invalid(lambda d: d["rows"][4].__setitem__("synopsis", "Janeway reaches the Delta Quadrant."))
        self.invalid(lambda d: d["rows"][4].__setitem__("title_resolution", "EXACT"))

    def test_title_variant_remains_visible(self):
        self.invalid(lambda d: d["rows"][3].__setitem__("title_resolution", "EXACT"))

    def test_no_relabeling_as_published(self):
        self.invalid(lambda d: d["rows"][0].__setitem__("synopsis_status", "EDITORIALLY_REVIEWED"))

    def test_no_extra_metadata_or_unreviewed_ids(self):
        self.invalid(lambda d: d["rows"].append(copy.deepcopy(d["rows"][0])))
        self.invalid(lambda d: d["rows"][1].__setitem__("row_id", "lead:9999"))

    def test_no_unreviewed_prose_rewrite(self):
        self.invalid(lambda d: d["rows"][0].__setitem__("synopsis", "x"))

    def test_two_independently_narrowed_cards_cannot_regress(self):
        self.invalid(lambda d: d["rows"][2].__setitem__("synopsis", "A dangerous particle detected near Voyager forces the crew to confront a threat to the surrounding space."))
        self.invalid(lambda d: d["rows"][8].__setitem__("synopsis", "The Doctor's growing musical ambitions begin to reshape his relationships and personal life."))


if __name__ == "__main__":
    unittest.main()
