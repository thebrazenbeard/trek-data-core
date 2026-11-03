"""Fail-closed DS9 S7E17-E25 source-card and finale presentation holds."""

import copy
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "proposals/research/ds9-s7-tail-b009-20261103"
validate = runpy.run_path(str(HERE / "validate.py"))["validate"]
read_json = runpy.run_path(str(HERE / "validate.py"))["read_json"]
PROBE = (
    "import json,sys\n"
    "sys.path.insert(0,sys.argv[1])\n"
    "from validate import validate,unique_pairs\n"
    "validate(json.load(sys.stdin,object_pairs_hook=unique_pairs))\n"
)


class DS9TailCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = read_json(HERE / "observations.json")

    def _run(self, data, optimized):
        return self._run_raw(json.dumps(data), optimized)

    def _run_raw(self, payload, optimized):
        return subprocess.run(
            [sys.executable, *(["-O"] if optimized else []), "-c", PROBE, str(HERE)],
            input=payload, text=True, capture_output=True, check=False,
        )

    def test_exact_nine_tail_cards_held_in_normal_and_optimized_modes(self):
        self.assertEqual(validate(self.original), 9)
        self.assertEqual(self.original["coverage_effect"], "NONE")
        self.assertEqual(self.original["public_synopsis_effect"], "NONE")
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                run = self._run(self.original, optimized)
                self.assertEqual(run.returncode, 0, run.stderr)

    def test_forged_metadata_source_custody_and_finale_split_rejected(self):
        cases = (
            (("batch_id",), "different-batch"),
            (("accepted_main_at_selection",), "0" * 40),
            (("publisher_guide_url",), "https://example.org/fake-guide"),
            (("publisher_source_family",), "independent_corroboration"),
            (("source_directory_sha256",), "0" * 64),
            (("accepted_s7e7_e11_source_record_sha256",), "0" * 64),
            (("accepted_s7e12_e16_source_record_sha256",), "0" * 64),
            (("current_raw_html_sha256",), "0" * 64),
            (("current_raw_html_captured",), True),
            (("actual_episode_or_script_read",), True),
            (("accepted_source_work_effect",), "ACCEPTED"),
            (("accepted_work_effect",), "ACCEPTED"),
            (("coverage_effect",), "CLOSE_READ"),
            (("public_synopsis_effect",), "PUBLISHED"),
            (("authenticated_source",), True),
            (("records", 0, "source_local_row_id"), "publisher:s7:ds9:011"),
            (("records", 0, "publisher_card_title"), "False Title"),
            (("records", 0, "episode"), 18),
            (("records", 8, "publisher_card_title"), "What You Leave Behind Part II"),
            (("records", 8, "accepted_work_id"), "global-ds9-finale"),
            (("records", 8, "synopsis_status"), "APPROVED"),
            (("records", 8, "episode_body_read"), True),
            (("finale_presentation_hold", "split_episode_or_work_decision"), "TWO_WORKS"),
            (("finale_presentation_hold", "additional_s7e26_inferred"), True),
            (("finale_presentation_hold", "source_relation"), "INDEPENDENT_SOURCES"),
        )
        for path, forged in cases:
            changed = copy.deepcopy(self.original)
            target = changed
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = forged
            for optimized in (False, True):
                with self.subTest(path=path, optimized=optimized):
                    run = self._run(changed, optimized)
                    self.assertNotEqual(run.returncode, 0, "forgery passed")
                    self.assertIn("ValueError: DS9 B009 invalid", run.stderr)

    def test_raw_duplicate_keys_rejected_before_in_memory_validation(self):
        """An already-parsed dict cannot attest whether its raw JSON had duplicate keys."""
        raw = json.dumps(self.original, separators=(",", ":"))
        attacks = (
            ('"coverage_effect":"NONE"',
             '"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"'),
            ('"current_raw_html_captured":false',
             '"current_raw_html_captured":true,"current_raw_html_captured":false'),
            ('"accepted_work_id":null',
             '"accepted_work_id":"forged-work","accepted_work_id":null'),
        )
        for needle, injection in attacks:
            self.assertIn(needle, raw)
            forged_raw = raw.replace(needle, injection, 1)
            for optimized in (False, True):
                with self.subTest(needle=needle, optimized=optimized):
                    result = self._run_raw(forged_raw, optimized)
                    self.assertNotEqual(result.returncode, 0, "duplicate-key forgery passed")
                    self.assertIn("ValueError: DS9 B009 invalid: duplicate JSON key",
                                  result.stderr)

    def test_file_bound_parser_rejects_duplicate_keys(self):
        raw = json.dumps(self.original, separators=(",", ":"))
        forged = raw.replace('"coverage_effect":"NONE"',
                             '"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"', 1)
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "forged-observations.json"
            file_path.write_text(forged, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DS9 B009 invalid: duplicate JSON key"):
                read_json(file_path)


if __name__ == "__main__":
    unittest.main()
