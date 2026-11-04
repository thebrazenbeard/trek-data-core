"""Adversarial gates for HELD TNG S2E6–E22 publisher metadata."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tng_s2_b014_validate", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class RemainingSeventeenHeldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = validator.accepted_inputs()
        cls.original = validator.read_json(HERE / "observations.json")

    def reject(self, mutate):
        candidate = copy.deepcopy(self.original)
        mutate(candidate)
        with self.assertRaises(ValueError):
            validator.compile_held(candidate, self.catalog)

    def test_seventeen_held_enrichments_not_global_works(self):
        result = validator.compile_held(copy.deepcopy(self.original), self.catalog)
        self.assertEqual(result["source_local_cards_enriched"], 17)
        self.assertEqual(result["new_works"], 0)
        self.assertEqual(result["governed_research_admissions"], 0)
        self.assertEqual(result["coverage_effect"], "NONE")
        self.assertEqual([r["publisher_card"]["episode"] for r in result["records"]], list(range(6, 23)))
        self.assertEqual(len({r["source_local_row_id"] for r in result["records"]}), 17)

    def test_wrong_card_ordinal_and_boolean_coercion(self):
        self.reject(lambda d: d["rows"][0].__setitem__("episode", 7))
        self.reject(lambda d: d["rows"][0].__setitem__("episode", True))
        self.reject(lambda d: d["rows"][0].__setitem__("season", 2.0))

    def test_no_reordered_or_renamed_source_local_identity(self):
        self.reject(lambda d: d["rows"].reverse())
        self.reject(lambda d: d["rows"][0].__setitem__("row_id", "legacy:s2:tng:006"))
        self.reject(lambda d: d["rows"][4].__setitem__("publisher_title", "Dauphin"))

    def test_rendered_description_fingerprint_cannot_change(self):
        self.reject(lambda d: d["rows"][2].__setitem__("rendered_description_sha256", "0" * 64))
        self.reject(lambda d: d["rows"][16].__setitem__("rendered_description_sha256", "0" * 64))
        self.reject(lambda d: d["source"].__setitem__("description_fingerprint_method", "RAW_HTML_SHA256"))

    def test_original_paraphrase_and_mentions_are_pinned(self):
        self.reject(lambda d: d["rows"][3].__setitem__("original_short_paraphrase", "Data is a person."))
        self.reject(lambda d: d["rows"][4].__setitem__("literal_description_mentions", ["Salia"]))
        self.reject(lambda d: d["rows"][0].__setitem__("literal_description_mentions", ["Data", "Ira Graves"]))
        self.reject(lambda d: d["rows"][9].__setitem__("literal_description_mentions", ["Data", "Sarjenka"]))
        self.reject(lambda d: d["rows"][11].__setitem__("original_short_paraphrase", "The Borg are inherently evil."))

    def test_no_raw_custody_or_primary_video_read_spoofing(self):
        self.reject(lambda d: d["source"].__setitem__("raw_html_sha256", "a" * 64))
        self.reject(lambda d: d["source"].__setitem__("raw_html_custody", "VERIFIED"))
        self.reject(lambda d: d.__setitem__("audiovisual_episodes_watched", True))
        self.reject(lambda d: d.__setitem__("scripts_or_transcripts_read_in_this_batch", True))

    def test_no_admission_identity_or_independent_corroboration(self):
        self.reject(lambda d: d.__setitem__("admission_effect", "ACCEPTED"))
        self.reject(lambda d: d.__setitem__("coverage_effect", "CLOSE_READ"))
        self.reject(lambda d: d.__setitem__("global_work_identity_resolved", True))
        self.reject(lambda d: d["source"].__setitem__("independent_source_families", 2))

    def test_derivative_transcript_cannot_be_silent_primary_witness(self):
        self.reject(lambda d: d["rows"][3].pop("prior_derivative_read_relationship"))
        self.reject(lambda d: d["rows"][3].__setitem__(
            "prior_derivative_read_relationship", "INDEPENDENT_PRIMARY_SOURCE_CORROBORATION"))
        self.reject(lambda d: d["rows"][4].__setitem__(
            "prior_derivative_read_relationship", validator.DERIVATIVE_RELATION))

    def test_unreviewed_extra_fields_and_truncated_batch_fail(self):
        self.reject(lambda d: d.__setitem__("license", "CLEARED"))
        self.reject(lambda d: d["rows"].pop())
        self.reject(lambda d: d["rows"][1].__setitem__("global_work_id", "tng-s02e07"))
        self.reject(lambda d: d["rows"][15].__setitem__("license", "CLEARED"))

    def test_later_episode_card_order_cannot_be_silently_replaced(self):
        self.reject(lambda d: d["rows"][5].__setitem__("publisher_title", "The Royale"))
        self.reject(lambda d: d["rows"][10].__setitem__("publisher_card_locator", "Season 2 / Q-Who? / S2 E15"))
        self.reject(lambda d: d["rows"][16].__setitem__("row_id", "legacy:s2:tng:022"))

    def test_accepted_source_catalog_cannot_be_rebased_silently(self):
        altered = copy.deepcopy(self.catalog)
        for row in altered["rows"]:
            if row["row_id"] == "legacy:s2:tng:008":
                row["source_locator"] = "https://example.invalid/other"
                break
        with self.assertRaises(ValueError):
            validator.compile_held(copy.deepcopy(self.original), altered)

    def test_generated_held_projection_is_deterministic(self):
        one = validator.render(validator.compile_held(copy.deepcopy(self.original), self.catalog))
        two = validator.render(validator.compile_held(copy.deepcopy(self.original), self.catalog))
        self.assertEqual(one, two)
        self.assertEqual((HERE / "records.json").read_bytes(), one)


if __name__ == "__main__":
    unittest.main()
