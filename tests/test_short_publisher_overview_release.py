"""A distinct model review plus exact source tuple gates 14 Short Trek public blurbs."""

import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_short_publisher_overview_release as release  # noqa: E402


class ShortOverviewReleaseTests(unittest.TestCase):
    def test_exact_14_short_overviews_and_unchanged_23_primary(self):
        short = release.build()
        main = json.loads((ROOT / "explorer/synopsis-catalog.json").read_text())
        self.assertEqual(short["synopsis_count"], 14)
        self.assertEqual(main["synopsis_count"], 23)
        self.assertEqual(short["synopsis_count"] + main["synopsis_count"], 37)
        self.assertEqual(len({r["row_id"] for r in short["synopses"]}), 14)
        self.assertEqual({r["medium"] for r in short["synopses"]}, {"SHORT_FORM"})
        self.assertNotIn("directory:short:very-short-treks-04", {r["row_id"] for r in short["synopses"]})
        self.assertTrue(all(r["admission_effect"] == "NONE" and r["coverage_effect"] == "NONE" for r in short["synopses"]))

    def test_source_and_model_review_sha_of_every_displayed_text(self):
        short = release.build()
        review_bytes = (ROOT / release.REVIEW).read_bytes()
        self.assertEqual(hashlib.sha256(review_bytes).hexdigest(), release.PINNED_REVIEW_SHA256)
        for row in short["synopses"]:
            self.assertIsNone(row["raw_webpage_sha256"])
            self.assertEqual(row["editorial_receipt_sha256"], release.PINNED_REVIEW_SHA256)
            self.assertEqual(row["research_observation_sha256"], hashlib.sha256((ROOT / row["research_observation_path"]).read_bytes()).hexdigest())
        expected = (json.dumps(short, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()
        self.assertEqual((ROOT / release.OUTPUT).read_bytes(), expected)

    def test_an_editorially_self_attested_edited_row_fails(self):
        real_read = release.read
        def tamper(path):
            data, raw = real_read(path)
            if path == release.REVIEW:
                data["reviewed_paraphrases"][0][1] = "f" * 64
            return data, raw
        with patch.object(release, "read", side_effect=tamper):
            with self.assertRaisesRegex(ValueError, "reviewer did not approve"):
                release.build()

    def test_missing_review_or_changed_review_bytes_fail_closed(self):
        real_read = release.read
        def tamper_bytes(path):
            data, raw = real_read(path)
            if path == release.REVIEW:
                raw += b"\n"
            return data, raw
        with patch.object(release, "read", side_effect=tamper_bytes):
            with self.assertRaisesRegex(ValueError, "receipt bytes changed"):
                release.build()


if __name__ == "__main__":
    unittest.main()
