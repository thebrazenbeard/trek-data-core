"""Fail-closed title/slot recheck and provenance admission tests for DS9 S6 B010."""

import copy
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "proposals/research/ds9-s6-middle-b010-20261103"
functions = runpy.run_path(str(HERE / "validate.py"))
validate = functions["validate"]
read_json = functions["read_json"]
PROBE = (
    "import json,sys\n"
    "sys.path.insert(0,sys.argv[1])\n"
    "from validate import validate,unique_pairs\n"
    "validate(json.load(sys.stdin,object_pairs_hook=unique_pairs))\n"
)


class DS9S6MiddleSourceCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = read_json(HERE / "observations.json")

    def _run_raw(self, payload, optimized):
        return subprocess.run(
            [sys.executable, *(["-O"] if optimized else []), "-c", PROBE, str(HERE)],
            input=payload, text=True, capture_output=True, check=False,
        )

    def _run(self, data, optimized):
        return self._run_raw(json.dumps(data), optimized)

    def test_exact_ten_source_cards_pass_both_modes(self):
        self.assertEqual(validate(self.original), 10)
        self.assertEqual(self.original["coverage_effect"], "NONE")
        self.assertEqual(self.original["public_synopsis_effect"], "NONE")
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self._run(self.original, optimized)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_forged_metadata_admission_and_source_custody_rejected(self):
        cases = (
            (("batch_id",), "other-batch"),
            (("proposal_only",), 1),
            (("accepted_main_at_selection",), "0" * 40),
            (("publisher_guide_url",), "https://example.org/forged-guide"),
            (("publisher_source_family",), "other_independent_primary"),
            (("source_independence_status",), "INDEPENDENT_CORROBORATION"),
            (("source_directory_sha256",), "0" * 64),
            (("historical_publisher_csv_sha256",), "0" * 64),
            (("accepted_b006_source_record_sha256",), "0" * 64),
            (("current_raw_html_sha256",), "0" * 64),
            (("current_raw_html_captured",), True),
            (("current_raw_html_captured",), 0),
            (("actual_episode_or_script_read",), True),
            (("accepted_source_work_effect",), "SOURCE_BOUND"),
            (("accepted_work_effect",), "ACCEPTED"),
            (("coverage_effect",), "CLOSE_READ"),
            (("public_synopsis_effect",), "PUBLISHED"),
            (("authenticated_primary_video",), True),
            (("records", 0, "source_local_row_id"), "publisher:s6:ds9:004"),
            (("records", 0, "episode"), 5),
            (("records", 0, "publisher_card_title"), "Untrue Publisher Title"),
            (("records", 0, "accepted_work_id"), "global-ds9-episode"),
            (("records", 0, "synopsis_status"), "PUBLISHED"),
            (("records", 0, "viewed_primary_video"), True),
            (("records", 9, "source_local_row_id"), "publisher:s6:ds9:019"),
            (("records", 9, "publisher_card_title"), "His Way"),
        )
        for path, forged_value in cases:
            changed = copy.deepcopy(self.original)
            item = changed
            for key in path[:-1]:
                item = item[key]
            item[path[-1]] = forged_value
            for optimized in (False, True):
                with self.subTest(path=path, optimized=optimized):
                    result = self._run(changed, optimized)
                    self.assertNotEqual(result.returncode, 0, "forged metadata was accepted")
                    self.assertIn("ValueError: DS9 B010 invalid", result.stderr)

    def test_raw_duplicate_json_keys_rejected(self):
        raw = json.dumps(self.original, separators=(",", ":"))
        attacks = (
            ('"coverage_effect":"NONE"',
             '"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"'),
            ('"current_raw_html_captured":false',
             '"current_raw_html_captured":true,"current_raw_html_captured":false'),
            ('"accepted_work_id":null',
             '"accepted_work_id":"made-up-work","accepted_work_id":null'),
        )
        for needle, injected in attacks:
            self.assertIn(needle, raw)
            forged_raw = raw.replace(needle, injected, 1)
            for optimized in (False, True):
                with self.subTest(needle=needle, optimized=optimized):
                    result = self._run_raw(forged_raw, optimized)
                    self.assertNotEqual(result.returncode, 0, "duplicate-key JSON accepted")
                    self.assertIn("ValueError: DS9 B010 invalid: duplicate JSON key",
                                  result.stderr)

    def test_real_file_bound_reader_rejects_duplicate_keys(self):
        raw = json.dumps(self.original, separators=(",", ":"))
        forged = raw.replace('"coverage_effect":"NONE"',
                             '"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"', 1)
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "attack.json"
            file_path.write_text(forged, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DS9 B010 invalid: duplicate JSON key"):
                read_json(file_path)


if __name__ == "__main__":
    unittest.main()
