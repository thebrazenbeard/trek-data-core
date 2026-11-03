"""Regression: literary admission gates must survive Python -O and normal CI."""

import copy
import json
import runpy
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "proposals/research/lit/slings-arrows-04-20261103"
validate = runpy.run_path(str(HERE / "validate.py"))["validate"]
PROBE = (
    "import json, sys\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "from validate import validate\n"
    "validate(json.load(sys.stdin))\n"
)


class OptimizedModeGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((HERE / "records.json").read_text(encoding="utf-8"))

    def _check_process(self, data: dict, optimized: bool) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, *(["-O"] if optimized else []), "-c", PROBE, str(HERE)],
            input=json.dumps(data), capture_output=True, text=True, check=False,
        )

    def test_original_records_valid_under_both_modes(self):
        self.assertEqual(validate(self.original), (8, 14, 6))
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self._check_process(self.original, optimized)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_tampered_acceptance_rights_and_coverage_fail_with_optimization(self):
        for location, illegal in (
            (("accepted_coverage_effect",), "ADMITTED"),
            (("accepted_source_binding_effect",), "ACCEPTED"),
            (("artwork_release_effect",), "PUBLIC"),
            (("source", "source_bytes_committed"), True),
            (("source", "rights_to_publicly_redistribute_text"), "GRANTED"),
            (("work_candidate", "canonical_identity"), "ACCEPTED_WORK_ID"),
            (("coverage", "accepted_work_coverage_level"), "CLOSE_READ"),
            (("coverage", "independently_audited"), True),
        ):
            altered = copy.deepcopy(self.original)
            target = altered
            for key in location[:-1]:
                target = target[key]
            target[location[-1]] = illegal
            for optimized in (False, True):
                with self.subTest(path=location, optimized=optimized):
                    result = self._check_process(altered, optimized)
                    self.assertNotEqual(result.returncode, 0, "invalid proposal passed")
                    self.assertIn("ValueError: invalid LIT proposal", result.stderr)

    def test_source_and_publisher_identity_cannot_drift_silently(self):
        for location, replacement in (
            (("batch_id",), "other-batch"),
            (("source", "verified_primary_source"), True),
            (("work_candidate", "authenticated_edition"), True),
            (("coverage", "accepted_full_text"), True),
            (("evidence", 0, "authenticated_source"), True),
            (("assertions", 0, "accepted_truth"), True),
            (("source", "member_path"), "ST ebooks txt/Next Generation/Unrelated Book.txt"),
            (("source", "member_sha256"), "0" * 64),
            (("source", "container_sha256"), "0" * 64),
            (("source", "member_size_bytes"), 1234),
            (("work_candidate", "title"), "Unrelated Book"),
            (("work_candidate", "creator"), "Unrelated Author"),
            (("work_candidate", "publisher_metadata_status"), "TEXT_EQUIVALENCE_VERIFIED"),
            (("coverage", "source_representation"), "AUTHENTICATED_PUBLISHER_EDITION"),
            (("work_candidate", "publisher_product_url"),
             "https://www.simonandschuster.com/books/Unrelated/Other/Star-Trek/9781416550242"),
            (("source", "structural_markers", "whitespace_token_count"), 99999),
            (("source", "structural_markers", "narrative_paragraph_counts_by_chapter"),
             [99] * 8),
        ):
            altered = copy.deepcopy(self.original)
            target = altered
            for key in location[:-1]:
                target = target[key]
            target[location[-1]] = replacement
            for optimized in (False, True):
                with self.subTest(path=location, optimized=optimized):
                    result = self._check_process(altered, optimized)
                    self.assertNotEqual(result.returncode, 0, "source identity drift passed")
                    self.assertIn("ValueError: invalid LIT proposal", result.stderr)


if __name__ == "__main__":
    unittest.main()
