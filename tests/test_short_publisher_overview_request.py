"""No Short Trek publisher premise can bypass exact source-local review custody."""

import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_short_publisher_overview_request as request  # noqa: E402


class ShortPublisherOverviewRequestTests(unittest.TestCase):
    def test_accepts_only_14_source_relative_promotional_paraphrases(self):
        data = request.build()
        self.assertEqual(data["reviewed_publisher_promotional_candidates"], 14)
        self.assertEqual(len(data["entries"]), 14)
        self.assertEqual(data["held_premise_free_row_id"], "directory:short:very-short-treks-04")
        self.assertEqual(data["raw_webpage_sha256"], None)
        self.assertFalse(data["full_shorts_viewed"])
        self.assertEqual(data["accepted_works_or_evidence"], 0)
        self.assertTrue(all(item["medium"] == "SHORT_FORM" for item in data["entries"]))
        self.assertTrue(all(item["admission_effect"] == "NONE" for item in data["entries"]))
        self.assertTrue(all(item["source_local_row_id"] != "short:very-short-treks-04" for item in data["entries"]))

    def test_derived_request_matches_exact_committed_bytes_and_source_shas(self):
        data = request.build()
        encoded = (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
        self.assertEqual((ROOT / request.OUTPUT).read_bytes(), encoded)
        for item in data["source_observations"]:
            self.assertEqual(item["sha256"], hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest())
        for entry in data["entries"]:
            self.assertEqual(entry["original_paraphrase_sha256"],
                             hashlib.sha256(entry["overview_text"].encode()).hexdigest())

    def test_fabricated_fifteenth_or_changed_short_plot_is_rejected(self):
        read = request.read
        def altered(path):
            doc, raw = read(path)
            if path == request.VERY:
                doc["description_paraphrases"][3]["synopsis"] = "Invented plot ending."
            return doc, raw
        with patch.object(request, "read", side_effect=altered):
            with self.assertRaisesRegex(ValueError, "premise-free"):
                request.build()


if __name__ == "__main__":
    unittest.main()
