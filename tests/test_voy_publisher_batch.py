"""Candidate-only contract for the bounded Voyager publisher-slot observation."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "proposals" / "discovery" / "voy-publisher-s01-b001-20261102"


class VoyagerPublisherBatchTests(unittest.TestCase):
    def test_observation_is_reproducible_and_unadmitted(self):
        receipt = json.loads((BATCH / "observation.json").read_text(encoding="utf-8"))
        bundle = json.loads((BATCH / "bundle.json").read_text(encoding="utf-8"))
        csv_bytes = (BATCH / "observed_slots.csv").read_bytes()

        self.assertEqual(receipt["csv_sha256"], hashlib.sha256(csv_bytes).hexdigest())
        self.assertEqual(receipt["mission_id"], "voy")
        self.assertEqual(receipt["independence_group"], "paramount-franchise-publishing")
        self.assertEqual(bundle["observation"]["response_sha256"], None)
        self.assertFalse(bundle["observation"]["audiovisual_content_inspected"])
        self.assertIsNone(bundle["series_qid_redirect"])
        for field in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
            self.assertEqual(bundle[field], "NONE")
        self.assertEqual(bundle["roster_completeness"], "UNRESOLVED")
        self.assertEqual(bundle["listed_slot_count"], 5)
        self.assertEqual(
            [(r["season"], r["episode_number"], r["title"]) for r in bundle["episode_slots"]],
            [
                (1, 1, "Caretaker, Part 1 & 2"),
                (1, 3, "Parallax"),
                (1, 4, "Time And Again"),
                (1, 5, "Phage"),
                (1, 6, "The Cloud"),
            ],
        )
        self.assertTrue(all(r["canonical_work_id"] is None and r["source_binding_id"] is None
                            for r in bundle["episode_slots"]))

        check = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "normalize_episode_roster.py"),
                "--csv", str(BATCH / "observed_slots.csv"),
                "--receipt", str(BATCH / "observation.json"),
                "--output", "proposals/discovery/voy-publisher-s01-b001-20261102/bundle.json",
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertIn("CHECK_ONLY", check.stdout)

        validate = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "validate_publisher_episode_roster.py"),
             "--input", str(BATCH / "bundle.json")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(validate.returncode, 0, validate.stderr)
        self.assertIn("PUBLISHER_ROSTER_CANDIDATE", validate.stdout)


if __name__ == "__main__":
    unittest.main()
