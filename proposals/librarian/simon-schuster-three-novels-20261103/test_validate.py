"""Regression checks for a validator that must fail closed under python -O."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class ProposalValidatorTests(unittest.TestCase):
    def check_optimized_rejects(self, mutation: str, expected_message: str) -> None:
        code = (
            "import validate\n"
            "data = validate.load_strict_json(validate.ROOT / 'records.json')\n"
            f"{mutation}\n"
            "validate.validate(data)\n"
        )
        result = subprocess.run(
            [sys.executable, "-O", "-B", "-c", code],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0, "Optimized Python accepted a tampered proposal")
        self.assertIn("ValueError", result.stderr)
        self.assertIn(expected_message, result.stderr)

    def test_clean_proposal_works_under_optimization(self) -> None:
        result = subprocess.run(
            [sys.executable, "-O", "-B", str(ROOT / "validate.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("zero accepted effects", result.stdout)

    def test_invalid_isbn_rejected_under_optimization(self) -> None:
        self.check_optimized_rejects(
            "data['editions'][0]['isbn13'] = '9781982194834'",
            "Invalid ISBN-13",
        )

    def test_admission_effect_rejected_under_optimization(self) -> None:
        self.check_optimized_rejects(
            "data['accepted_effects']['works'] = 'ACCEPTED'",
            "Admission or coverage effect is forbidden",
        )

    def test_same_work_format_collision_rejected_under_optimization(self) -> None:
        self.check_optimized_rejects(
            "data['editions'][1]['format'] = 'TRADE_PAPERBACK'",
            "Each Work must have a paperback, eBook, and audio edition",
        )


if __name__ == "__main__":
    unittest.main()
