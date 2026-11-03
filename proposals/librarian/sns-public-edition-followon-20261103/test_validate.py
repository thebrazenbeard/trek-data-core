"""Optimized-mode hostile regressions for the public-only edition proposal."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class PublicPublisherEditionTests(unittest.TestCase):
    def run_optimized(self, mutation: str | None = None) -> subprocess.CompletedProcess:
        code = "import validate\nproposal = validate.load(validate.ROOT / 'records.json')\n"
        if mutation:
            code += mutation + "\n"
        code += "validate.validate(proposal)\n"
        return subprocess.run(
            [sys.executable, "-O", "-B", "-c", code],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def rejected(self, mutation: str, reason: str) -> None:
        result = self.run_optimized(mutation)
        self.assertNotEqual(result.returncode, 0, "Optimized mode accepted a tampered public-source record")
        self.assertIn("ValueError", result.stderr)
        self.assertIn(reason, result.stderr)

    def test_baseline_accepted_under_optimized_python(self) -> None:
        result = self.run_optimized()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_bad_isbn_rejected(self) -> None:
        self.rejected("proposal['records'][0]['publisher_isbn13'] = '9781668051369'", "Invalid ISBN-13")

    def test_coverage_promotion_rejected(self) -> None:
        self.rejected("proposal['coverage_effect'] = 'SOURCE_BOUND'", "Admission/coverage effects prohibited")

    def test_same_batch_isbn_collision_rejected(self) -> None:
        self.rejected("proposal['records'][1]['publisher_isbn13'] = '9781668051368'", "Unknown or duplicate ISBN")

    def test_same_publisher_wrong_edition_url_rejected(self) -> None:
        self.rejected("proposal['records'][0]['source_url'] = proposal['records'][2]['source_url']", "Publisher edition URL mismatch")

    def test_unverified_page_hash_rejected(self) -> None:
        self.rejected("proposal['records'][0]['source_raw_sha256'] = '0' * 64", "Raw-source hash not verified")

    def test_private_source_field_injection_rejected(self) -> None:
        self.rejected("proposal['records'][0]['owner_private_opf_path'] = 'not-publishable'", "Unexpected edition fields")

    def test_publisher_edition_claim_swap_rejected(self) -> None:
        self.rejected("proposal['records'][3]['format'] = 'EBOOK'", "Publisher edition fields changed")


if __name__ == "__main__":
    unittest.main()
