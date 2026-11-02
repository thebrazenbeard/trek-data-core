"""Candidate-only offline publisher CSV normalization regression tests."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "normalize_episode_roster.py"
VALIDATOR = ROOT / "tools" / "validate_publisher_episode_roster.py"


class NormalizePublisherRosterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "proposals" / "review").mkdir(parents=True)
        self.csv = self.root / "slots.csv"
        self.receipt = self.root / "receipt.json"
        self.output = self.root / "proposals" / "review" / "bundle.json"
        self.content = b"season,episode_number,title\n2,2,Later\n1,2,Second\n1,1,First\n"
        self.csv.write_bytes(self.content)
        self.metadata = {
            "batch_id": "tng-official-synthetic-001",
            "mission_id": "tng",
            "publisher": "Example publisher (synthetic)",
            "independence_group": "publisher:example",
            "observed_on": "2026-11-02",
            "primary_locator": "https://example.org/series/tng/episodes",
            "crosscheck_locator": "https://example.org/series/tng/catalog",
            "csv_sha256": hashlib.sha256(self.content).hexdigest(),
        }
        self.save_receipt()

    def save_receipt(self):
        self.receipt.write_text(json.dumps(self.metadata), encoding="utf-8")

    def run_tool(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOL), "--csv", str(self.csv), "--receipt", str(self.receipt),
             "--output", "proposals/review/bundle.json", *args],
            cwd=self.root, capture_output=True, text=True, timeout=10,
        )

    def assert_rejected(self, fragment):
        result = self.run_tool()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(fragment, result.stderr)
        self.assertFalse(self.output.exists(), "rejected input must not write output")

    def test_usable_candidate_proposal_and_existing_validator_agree(self):
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"mode": "NEW_PROPOSAL"', result.stdout)
        payload = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual([tuple((r["season"], r["episode_number"]))
                          for r in payload["episode_slots"]], [(1, 1), (1, 2), (2, 2)])
        self.assertEqual(payload["mission_id"], "tng")
        self.assertEqual(payload["listed_slot_count"], 3)
        self.assertEqual(payload["roster_completeness"], "UNRESOLVED")
        self.assertEqual(payload["series_qid_redirect"], None)
        self.assertEqual(payload["observation"]["response_sha256"], None)
        self.assertFalse(payload["observation"]["audiovisual_content_inspected"])
        for key in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
            self.assertEqual(payload[key], "NONE")
        for item in payload["episode_slots"]:
            self.assertEqual(item["status"], "CANDIDATE")
            self.assertIsNone(item["canonical_work_id"])
            self.assertIsNone(item["source_binding_id"])
        checked = subprocess.run([sys.executable, str(VALIDATOR), "--input", str(self.output)],
                                 cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertIn('"accepted_effect": "NONE"', checked.stdout)

    def test_check_mode_does_not_write(self):
        result = self.run_tool("--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"mode": "CHECK_ONLY"', result.stdout)
        self.assertFalse(self.output.exists())

    def test_identical_input_produces_identical_result_not_duplicate_writes(self):
        first = self.run_tool()
        self.assertEqual(first.returncode, 0, first.stderr)
        output = self.output.read_bytes()
        second = self.run_tool()
        self.assertEqual(second.returncode, 1)
        self.assertEqual(self.output.read_bytes(), output)

    def test_sha_receipt_mismatch_rejected_before_write(self):
        self.metadata["csv_sha256"] = "a" * 64
        self.save_receipt()
        self.assert_rejected("SHA-256 does not match")

    def test_unknown_mission_and_unauthorized_extra_receipt_fields_fail_closed(self):
        self.metadata["mission_id"] = "fake"
        self.save_receipt()
        self.assert_rejected("absent from current catalog")
        self.metadata["mission_id"] = "tng"
        self.metadata["accepted_work_effect"] = "ACCEPTED"
        self.save_receipt()
        self.assert_rejected("unexpected fields")

    def test_bad_header_and_numeric_slots_are_rejected(self):
        for raw in (b"series,season,episode\ntng,1,1\n", b"season,episode_number,title\n0,1,First\n",
                    b"season,episode_number,title\n1,01,First\n", b"season,episode_number,title\n1,yes,First\n"):
            self.csv.write_bytes(raw)
            self.metadata["csv_sha256"] = hashlib.sha256(raw).hexdigest()
            self.save_receipt()
            self.assert_rejected("CSV")

    def test_duplicate_slot_or_title_rejected_after_sorting(self):
        for raw in (b"season,episode_number,title\n1,1,First\n1,1,Other\n",
                    b"season,episode_number,title\n1,1,First\n2,1,First\n"):
            self.csv.write_bytes(raw)
            self.metadata["csv_sha256"] = hashlib.sha256(raw).hexdigest()
            self.save_receipt()
            self.assert_rejected("strictly sorted" if b"Other" in raw else "duplicate publisher title")

    def test_markup_or_multiline_title_rejected(self):
        for raw in (b"season,episode_number,title\n1,1,<script>alert(1)</script>\n",
                    b'season,episode_number,title\n1,1,"First\nSecond"\n'):
            self.csv.write_bytes(raw)
            self.metadata["csv_sha256"] = hashlib.sha256(raw).hexdigest()
            self.save_receipt()
            self.assert_rejected("single-line")

    def test_symlink_and_oversized_input_rejected(self):
        self.csv.unlink()
        external = self.root / "real.csv"
        external.write_bytes(self.content)
        self.csv.symlink_to(external)
        self.assert_rejected("non-symlink")
        self.csv.unlink()
        raw = b" " * (128 * 1024 + 1)
        self.csv.write_bytes(raw)
        self.assert_rejected("128 KiB")

    def test_invalid_https_locator_rejected(self):
        self.metadata["primary_locator"] = "https://example.org/path?token=secret"
        self.save_receipt()
        self.assert_rejected("locator")

    def test_duplicate_json_keys_rejected(self):
        self.receipt.write_text('{"mission_id":"tng","mission_id":"sfa"}', encoding="utf-8")
        self.assert_rejected("duplicate JSON key")

    def test_invalid_output_location_is_rejected(self):
        result = subprocess.run([sys.executable, str(TOOL), "--csv", str(self.csv),
                                 "--receipt", str(self.receipt), "--output", "../outside.json"],
                                cwd=self.root, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertIn("relative proposals", result.stderr)
        self.assertFalse((self.root.parent / "outside.json").exists())


if __name__ == "__main__":
    unittest.main()
