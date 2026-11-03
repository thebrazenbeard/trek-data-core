"""Negative tests for Short Treks proposal-only source and identity gates."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("short_2019_validator", HERE / "validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
BASE = json.loads((HERE / "records.json").read_text(encoding="utf-8"))


class ShortSourceGateTests(unittest.TestCase):
    def test_clean_proposal(self):
        MODULE.validate(BASE)

    def reject(self, mutate):
        candidate = copy.deepcopy(BASE)
        mutate(candidate)
        with self.assertRaises(ValueError):
            MODULE.validate(candidate)

    def test_no_admission(self):
        self.reject(lambda d: d.__setitem__("coverage_effect", "CLOSE_READ"))

    def test_no_primary_av_claim(self):
        self.reject(lambda d: d.__setitem__("primary_audiovisual_processed", True))

    def test_no_other_medium(self):
        self.reject(lambda d: d["work_candidates"][0].__setitem__("type", "FILM"))

    def test_no_global_identity(self):
        self.reject(lambda d: d["assertions"][0].__setitem__("global_identity_effect", "SAME_AS"))

    def test_no_silent_slot_renumbering(self):
        self.reject(lambda d: d["evidence"][1].__setitem__("source_local_slot", "S2E1"))

    def test_no_silent_schedule_rewrite(self):
        self.reject(lambda d: d["evidence"][2].__setitem__("announced_date", "2019-10-09"))

    def test_no_hidden_year_inference(self):
        self.reject(lambda d: d["evidence"][10].__setitem__("date_basis", "EXPLICIT_SCHEDULE"))

    def test_no_fake_independence(self):
        self.reject(lambda d: d["sources"][1].__setitem__("independence_group", "publisher:other"))

    def test_no_unlicensed_artwork_injection(self):
        self.reject(lambda d: d["work_candidates"][0].__setitem__("image_url", "https://example.com/still.jpg"))

    def test_no_unpinned_source_substitution(self):
        self.reject(lambda d: d["sources"][0].__setitem__("url", "https://example.org/recap"))

    def test_no_forged_content_read(self):
        self.reject(lambda d: d["evidence"][0].__setitem__("kind", "DEPICTION_ACTION"))

    def test_no_source_relabeling(self):
        self.reject(lambda d: d["local_entities"][0].__setitem__("source_id", "short-current-paramount-guide"))

    def test_no_duplicate_assertions(self):
        self.reject(lambda d: d["assertions"][1].__setitem__("assertion_id", "as-qa"))


if __name__ == "__main__":
    unittest.main()
