"""Exact accepted B001–B004 rechecks projected without Work/evidence admission."""

import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_metadata_recheck_projection as projection  # noqa: E402


class MetadataRecheckProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = projection.build()

    def test_exact_source_local_counts_and_unresolved_cases(self):
        result = self.result
        self.assertEqual((result["source_local_row_count"], result["rendered_metadata_rechecks"],
                          result["unrechecked_source_local_rows"]), (1214, 56, 1158))
        self.assertEqual((result["embedded_research_lead_rows"], result["embedded_research_leads_rechecked"],
                          result["embedded_research_leads_not_rechecked"]), (218, 51, 167))
        self.assertEqual(result["literary_directory_rows_rechecked"], 5)
        self.assertEqual(result["exact_title_matches"], 52)
        self.assertEqual(result["unresolved_title_or_multipart_cases"], 4)
        self.assertEqual([r["row_id"] for r in result["rows"] if r["title_check"] != "EXACT"],
                         ["lead:0006", "lead:0029", "lead:0041", "lead:0042"])

    def test_no_row_admission_or_raw_page_claim(self):
        result = self.result
        self.assertEqual(result["admitted_works_or_evidence"], 0)
        self.assertEqual(result["raw_webpage_bytes_custodied"], 0)
        for row in result["rows"]:
            self.assertIsNone(row["raw_webpage_sha256"])
            self.assertEqual((row["admission_effect"], row["coverage_effect"],
                              row["synopsis_publication_effect"]), ("NONE", "NONE", "NONE"))
            self.assertEqual(row["governed_research_coverage_state"], "NOT_ADMITTED")

    def test_exact_bytes_reproduce_and_receipts_bind_accepted_observations(self):
        expected = (json.dumps(self.result, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
        self.assertEqual((ROOT / projection.OUT).read_bytes(), expected)
        self.assertEqual(len(self.result["input_observation_receipts"]), 5)
        for receipt in self.result["input_observation_receipts"]:
            raw = (ROOT / receipt["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt["sha256"])
        for row in self.result["rows"]:
            raw = (ROOT / row["source_observation_path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["source_observation_sha256"])

    def test_mutated_official_title_fails_compiler_before_badge(self):
        real_read = projection._read_json
        def adversarial_read(path):
            data, raw = real_read(path)
            if path == projection.B004 / "observations.json":
                data["rows"][0]["cards"][0]["official_title"] = "False official title"
            return data, raw
        with patch.object(projection, "_read_json", side_effect=adversarial_read):
            with self.assertRaises(ValueError):
                projection.build()


if __name__ == "__main__":
    unittest.main()
