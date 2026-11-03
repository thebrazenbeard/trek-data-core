"""DS9 S6 E16–25 publisher-card recheck; E20 previously accepted and excluded."""

import copy
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "proposals/research/ds9-s6-tail-b011-20261103"
functions = runpy.run_path(str(HERE / "validate.py"))
validate = functions["validate"]
read_json = functions["read_json"]
PROBE = (
    "import json,sys\n"
    "sys.path.insert(0,sys.argv[1])\n"
    "from validate import validate,unique_pairs\n"
    "validate(json.load(sys.stdin,object_pairs_hook=unique_pairs))\n"
)


class DS9S6TailSourceCards(unittest.TestCase):
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

    def test_nine_title_slot_cards_exclude_prior_e20_both_modes(self):
        self.assertEqual(validate(self.original), 9)
        self.assertEqual([record["episode"] for record in self.original["records"]],
                         [16, 17, 18, 19, 21, 22, 23, 24, 25])
        self.assertEqual(self.original["excluded_prior_accepted_card"]["omitted_episode"], 20)
        self.assertEqual(self.original["coverage_effect"], "NONE")
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self._run(self.original, optimized)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_forged_scope_admission_custody_and_prior_overlap_rejected(self):
        cases = (
            (("batch_id",), "revised-batch"),
            (("proposal_only",), 1),
            (("accepted_main_at_selection",), "0" * 40),
            (("publisher_guide_url",), "https://untrusted.example/fake"),
            (("publisher_source_family",), "independent_primary"),
            (("source_independence_status",), "INDEPENDENT_CORROBORATION"),
            (("guide_presentation_scope",), "CONFIRMED_BROADCAST_EDITION"),
            (("source_directory_sha256",), "0" * 64),
            (("historical_publisher_csv_sha256",), "0" * 64),
            (("accepted_b006_source_record_sha256",), "0" * 64),
            (("accepted_b010_source_record_sha256",), "0" * 64),
            (("current_raw_html_sha256",), "0" * 64),
            (("current_raw_html_captured",), True),
            (("current_raw_html_captured",), 0),
            (("actual_episode_or_script_read",), True),
            (("accepted_source_work_effect",), "SOURCE_BOUND"),
            (("accepted_work_effect",), "ACCEPTED"),
            (("coverage_effect",), "CLOSE_READ"),
            (("public_synopsis_effect",), "PUBLISHED"),
            (("verified_primary_video",), True),
            (("excluded_prior_accepted_card", "omitted_episode"), 21),
            (("excluded_prior_accepted_card", "publisher_row_id"), "publisher:s6:ds9:020"),
            (("excluded_prior_accepted_card", "prior_accepted_seed_row_id"), "lead:9999"),
            (("excluded_prior_accepted_card", "identity_relation"), "GLOBAL_SAME_AS"),
            (("records", 0, "source_local_row_id"), "publisher:s6:ds9:019"),
            (("records", 0, "episode"), 20),
            (("records", 0, "publisher_card_title"), "His Way"),
            (("records", 0, "accepted_work_id"), "global-ds9-work"),
            (("records", 0, "synopsis_status"), "PUBLISHED"),
            (("records", 0, "viewed_episode"), True),
            (("records", 8, "source_local_row_id"), "publisher:s6:ds9:025"),
        )
        for path, forged in cases:
            changed = copy.deepcopy(self.original)
            target = changed
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = forged
            for optimized in (False, True):
                with self.subTest(path=path, optimized=optimized):
                    result = self._run(changed, optimized)
                    self.assertNotEqual(result.returncode, 0, "forged metadata accepted")
                    self.assertIn("ValueError: DS9 B011 invalid", result.stderr)

    def test_raw_duplicate_key_forgery_rejected_both_modes(self):
        raw = json.dumps(self.original, separators=(",", ":"))
        attacks = (
            ('"coverage_effect":"NONE"',
             '"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"'),
            ('"current_raw_html_captured":false',
             '"current_raw_html_captured":true,"current_raw_html_captured":false'),
            ('"accepted_work_id":null',
             '"accepted_work_id":"fake-global-work","accepted_work_id":null'),
            ('"omitted_episode":20',
             '"omitted_episode":21,"omitted_episode":20'),
        )
        for needle, injected in attacks:
            self.assertIn(needle, raw)
            forged_raw = raw.replace(needle, injected, 1)
            for optimized in (False, True):
                with self.subTest(needle=needle, optimized=optimized):
                    result = self._run_raw(forged_raw, optimized)
                    self.assertNotEqual(result.returncode, 0, "duplicate-key JSON accepted")
                    self.assertIn("ValueError: DS9 B011 invalid: duplicate JSON key",
                                  result.stderr)

    def test_file_bound_raw_parser_is_strict(self):
        raw = json.dumps(self.original, separators=(",", ":"))
        forged_raw = raw.replace('"coverage_effect":"NONE"',
                                 '"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"', 1)
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "forged.json"
            file_path.write_text(forged_raw, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DS9 B011 invalid: duplicate JSON key"):
                read_json(file_path)

    def test_adding_coherent_b006_e20_card_still_fails_closed(self):
        changed = copy.deepcopy(self.original)
        duplicate = copy.deepcopy(changed["records"][0])
        duplicate.update({
            "observation_id": "ds9-b011-p10",
            "source_local_row_id": "publisher:s6:ds9:019",
            "episode": 20,
            "publisher_card_title": "His Way",
            "card_locator": "Season 6 Episode Guide > S6 E20 > His Way",
        })
        changed["records"].append(duplicate)
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self._run(changed, optimized)
                self.assertNotEqual(result.returncode, 0, "pre-rechecked E20 admission passed")
                self.assertIn("ValueError: DS9 B011 invalid: nine held S6 cards", result.stderr)


if __name__ == "__main__":
    unittest.main()
