"""Hostile guards for TNG S3 full-guide HELD publisher descriptions."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tng_s3_full_guide_validate", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class TNGSeasonThreeHeldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = validator.accepted_inputs()
        cls.original = validator.read_json(HERE / "observations.json")

    def reject(self, mutate):
        candidate = copy.deepcopy(self.original)
        mutate(candidate)
        with self.assertRaises(ValueError):
            validator.compile_held(candidate, self.catalog)

    def test_all_26_source_local_metadata_cards_and_no_works(self):
        result = validator.compile_held(copy.deepcopy(self.original), self.catalog)
        self.assertEqual(result["source_local_cards_enriched"], 26)
        self.assertEqual([x["publisher_card"]["episode"] for x in result["records"]],
                         list(range(1, 27)))
        self.assertEqual(len({x["source_local_row_id"] for x in result["records"]}), 26)
        self.assertEqual(result["new_works"], 0)
        self.assertEqual(result["governed_research_admissions"], 0)
        self.assertEqual(result["coverage_effect"], "NONE")
        self.assertTrue(all(x["global_work_identity"] == "UNRESOLVED"
                            and x["synopsis_publication_status"] == "PENDING_EDITORIAL_AND_SOURCE_REVIEW"
                            for x in result["records"]))

    def test_publisher_card_identity_and_order_are_exact(self):
        self.reject(lambda d: d["rows"].reverse())
        self.reject(lambda d: d["rows"][0].__setitem__("row_id", "legacy:s3:tng:001"))
        self.reject(lambda d: d["rows"][14].__setitem__("publisher_title", "Yesterday's Enterprise (Remastered)"))
        self.reject(lambda d: d["rows"][25].__setitem__("publisher_card_locator", "S3 E25"))
        self.reject(lambda d: d["rows"][25].__setitem__("episode", True))
        self.reject(lambda d: d["rows"][0].__setitem__("season", 3.0))

    def test_publisher_description_fingerprints_are_pinned(self):
        self.reject(lambda d: d["rows"][0].__setitem__("rendered_description_sha256", "0" * 64))
        self.reject(lambda d: d["rows"][25].__setitem__("rendered_description_sha256", "a" * 64))
        self.reject(lambda d: d["source"].__setitem__("description_fingerprint_method", "RAW_HTML_SHA256"))
        self.reject(lambda d: d["rows"][6].__setitem__("original_short_paraphrase", "The Romulans are evil."))

    def test_epistemic_anomalies_cannot_be_silently_flattened(self):
        expected = {
            4: "ATTRIBUTED_BELIEF_NOT_DIVINITY",
            12: "POLITICAL_GROUP_LABEL",
            14: "ACCUSATION_NOT_GUILT",
            15: "ALTERNATE_HISTORY_IDENTITY_UNRESOLVED",
            16: "PARENTAL_RELATION_NOT_LEGAL_STATUS",
            18: "REPLACEMENT_IDENTITY_UNRESOLVED",
            22: "PRESUMED_DEATH_NOT_VERIFIED_DEATH",
            23: "TITLE_NAME_NOT_PUBLISHER_DESCRIPTION_ASSERTION",
            26: "EVALUATIVE_EVIL_LABEL",
        }
        for ep, anomaly in expected.items():
            self.assertEqual(self.original["rows"][ep - 1]["publisher_framing_anomaly"], anomaly)
            self.reject(lambda d, e=ep: d["rows"][e - 1].__setitem__("publisher_framing_anomaly", "NONE"))

    def test_no_fresh_source_custody_from_prior_discovery_receipt(self):
        self.reject(lambda d: d["source"].__setitem__("fresh_raw_html_sha256", "a" * 64))
        self.reject(lambda d: d["source"].__setitem__("fresh_raw_html_custody", "VERIFIED"))
        self.reject(lambda d: d["source"].__setitem__("prior_receipt_status", "FRESH_AUTHENTICATED"))
        self.reject(lambda d: d["source"].__setitem__("prior_2026_11_02_discovery_receipt_sha256", "b" * 64))
        self.reject(lambda d: d["source"].__setitem__("independent_source_families", 2))

    def test_no_audiovisual_script_or_work_claims(self):
        self.reject(lambda d: d.__setitem__("audiovisual_episodes_watched", True))
        self.reject(lambda d: d.__setitem__("scripts_or_transcripts_read_in_this_batch", True))
        self.reject(lambda d: d.__setitem__("global_work_identity_resolved", True))
        self.reject(lambda d: d.__setitem__("admission_effect", "ACCEPTED"))
        self.reject(lambda d: d.__setitem__("coverage_effect", "CLOSE_READ"))
        self.reject(lambda d: d["rows"][12].__setitem__("global_work_id", "tng-3-13"))
        self.reject(lambda d: d["rows"][0].__setitem__("evidence_frame", "EPISODE_FACT"))

    def test_unaudited_extra_fields_truncation_and_boolean_coercion(self):
        self.reject(lambda d: d["rows"].pop())
        self.reject(lambda d: d["rows"][4].__setitem__("source_verified", True))
        self.reject(lambda d: d.__setitem__("license", "CLEARED"))
        self.reject(lambda d: d["source"].__setitem__("entire_guide_card_count_read", True))

    def test_accepted_row_crosswalk_spoofing_rejected(self):
        altered = copy.deepcopy(self.catalog)
        for row in altered["rows"]:
            if row["row_id"] == "legacy:s3:tng:014":
                row["source_locator"] = "https://example.invalid/not-the-guide"
                break
        with self.assertRaises(ValueError):
            validator.compile_held(copy.deepcopy(self.original), altered)

    def test_duplicate_json_key_and_symlink_source_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "bad.json"
            p.write_text('{"x":1,"x":2}', encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.read_json(p)
            linked = Path(folder) / "linked.json"
            try:
                linked.symlink_to(p)
            except OSError:
                self.skipTest("symlink privilege unavailable")
            with self.assertRaises(ValueError):
                validator.read_json(linked)

    def test_deterministic_projection_matches_committed_record(self):
        one = validator.render(validator.compile_held(copy.deepcopy(self.original), self.catalog))
        two = validator.render(validator.compile_held(copy.deepcopy(self.original), self.catalog))
        self.assertEqual(one, two)
        self.assertEqual((HERE / "records.json").read_bytes(), one)


if __name__ == "__main__":
    unittest.main()
