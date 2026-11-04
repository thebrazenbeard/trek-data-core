"""Hostile checks for TNG Season 2 first-five held publisher cards."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("tng_s2_b013_validate", HERE / "validate.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class TngS2PublisherHeldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = validator.accepted_inputs()
        cls.source = validator.read_json(HERE / "observations.json")

    def test_exact_five_source_local_cards_remain_held(self):
        result = validator.compile_held(copy.deepcopy(self.source), self.catalog)
        self.assertEqual(result["source_local_cards_enriched"], 5)
        self.assertEqual(result["new_works"], 0)
        self.assertEqual(result["governed_research_admissions"], 0)
        self.assertEqual(result["coverage_effect"], "NONE")
        self.assertEqual(len({r["source_local_row_id"] for r in result["records"]}), 5)
        self.assertTrue(all(r["publisher_card"]["raw_webpage_sha256"] is None
                            and r["source_custody"] == "NO_RAW_HTML_BYTES"
                            for r in result["records"]))

    def reject_mutation(self, change):
        altered = copy.deepcopy(self.source)
        change(altered)
        with self.assertRaises(ValueError):
            validator.compile_held(altered, self.catalog)

    def test_wrong_ordinal_and_bool_coercion_are_rejected(self):
        self.reject_mutation(lambda d: d["rows"][0].__setitem__("episode", 2))
        self.reject_mutation(lambda d: d["rows"][0].__setitem__("episode", True))
        self.reject_mutation(lambda d: d["rows"][0].__setitem__("season", 2.0))

    def test_title_and_row_binding_cannot_shift(self):
        self.reject_mutation(lambda d: d["rows"][0].__setitem__("row_id", "legacy:s2:tng:001"))
        self.reject_mutation(lambda d: d["rows"][0].__setitem__("publisher_title", "The Children"))
        self.reject_mutation(lambda d: d["rows"].reverse())

    def test_no_source_fingerprint_or_editorial_mutation(self):
        self.reject_mutation(lambda d: d["rows"][3].__setitem__("rendered_description_sha256", "0" * 64))
        self.reject_mutation(lambda d: d["rows"][1].__setitem__("original_short_paraphrase", "The crew discovers an alien."))
        self.reject_mutation(lambda d: d["rows"][4].__setitem__("literal_description_mentions", ["Riva"]))

    def test_no_promotion_to_episode_or_raw_html_custody(self):
        self.reject_mutation(lambda d: d.__setitem__("audiovisual_episodes_watched", True))
        self.reject_mutation(lambda d: d.__setitem__("scripts_or_transcripts_read", True))
        self.reject_mutation(lambda d: d.__setitem__("global_work_identity_resolved", True))
        self.reject_mutation(lambda d: d["source"].__setitem__("raw_html_sha256", "a" * 64))
        self.reject_mutation(lambda d: d["source"].__setitem__("raw_html_custody", "VERIFIED"))

    def test_no_admission_or_corroboration_drift(self):
        self.reject_mutation(lambda d: d.__setitem__("coverage_effect", "ATTAINED"))
        self.reject_mutation(lambda d: d.__setitem__("admission_effect", "SOURCE_BOUND"))
        self.reject_mutation(lambda d: d["source"].__setitem__("independent_source_families", 2))
        self.reject_mutation(lambda d: d["source"].__setitem__("publisher_lineage", "independent:pluto"))

    def test_unknown_fields_and_missing_rows_are_rejected(self):
        self.reject_mutation(lambda d: d.__setitem__("license_status", "CLEARED"))
        self.reject_mutation(lambda d: d["rows"].pop())
        self.reject_mutation(lambda d: d["rows"][2].__setitem__("work_id", "tng-s2e3"))

    def test_accepted_catalog_drift_is_not_reconciled(self):
        altered = copy.deepcopy(self.catalog)
        for row in altered["rows"]:
            if row["row_id"] == "legacy:s2:tng:000":
                row["source_locator"] = "https://example.invalid/changed"
                break
        with self.assertRaises(ValueError):
            validator.compile_held(copy.deepcopy(self.source), altered)

    def test_deterministic_record_bytes(self):
        one = validator.render(validator.compile_held(copy.deepcopy(self.source), self.catalog))
        two = validator.render(validator.compile_held(copy.deepcopy(self.source), self.catalog))
        self.assertEqual(one, two)
        self.assertEqual((HERE / "records.json").read_bytes(), one)


if __name__ == "__main__":
    unittest.main()
