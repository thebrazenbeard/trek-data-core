"""DS9 B012: fail-closed primary-source and publisher-card scope checks."""

import copy
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "proposals/research/ds9-s6-gaps-b012-20261103"
scope = runpy.run_path(str(HERE / "validate.py"))
validate = scope["validate"]
read_json = scope["read_json"]
PROBE = (
    "import json,sys\n"
    "sys.path.insert(0,sys.argv[1])\n"
    "from validate import validate,unique_pairs\n"
    "validate(json.load(sys.stdin,object_pairs_hook=unique_pairs))\n"
)


class DS9Season6GapCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = read_json(HERE / "observations.json")

    def run_raw(self, payload, optimized):
        return subprocess.run(
            [sys.executable, *(["-O"] if optimized else []), "-c", PROBE, str(HERE)],
            input=payload, text=True, capture_output=True, check=False,
        )

    def test_five_explicit_nonduplicate_gap_cards_both_modes(self):
        self.assertEqual(validate(self.original), 5)
        self.assertEqual([r["episode"] for r in self.original["records"]],
                         [1, 2, 3, 4, 26])
        self.assertEqual(self.original["coverage_effect"], "NONE")
        self.assertFalse(self.original["actual_episode_or_script_read"])
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                process = self.run_raw(json.dumps(self.original), optimized)
                self.assertEqual(process.returncode, 0, process.stderr)

    def test_forged_source_work_coverage_and_custody_rejected(self):
        for path, fake in (
            (("role",), "CONSOLIDATOR"),
            (("proposal_only",), 1),
            (("accepted_main_at_selection",), "0" * 40),
            (("publisher_guide_url",), "https://example.org/untrusted"),
            (("source_independence_status",), "INDEPENDENT_WITNESS"),
            (("source_directory_sha256",), "0" * 64),
            (("historical_publisher_csv_sha256",), "0" * 64),
            (("accepted_b006_source_record_sha256",), "0" * 64),
            (("accepted_b010_source_record_sha256",), "0" * 64),
            (("accepted_b011_source_record_sha256",), "0" * 64),
            (("current_raw_html_sha256",), "0" * 64),
            (("current_raw_html_captured",), True),
            (("actual_episode_or_script_read",), True),
            (("synopsis_policy",), "PUBLISHED"),
            (("accepted_source_work_effect",), "SOURCE_BOUND"),
            (("accepted_work_effect",), "ACCEPTED"),
            (("coverage_effect",), "CLOSE_READ"),
            (("public_synopsis_effect",), "PUBLISHED"),
            (("records", 0, "episode"), 5),
            (("records", 4, "episode"), 25),
            (("records", 0, "source_local_row_id"), "lead:0001"),
            (("records", 0, "publisher_card_title"), "Different Title"),
            (("records", 0, "description_block_read"), False),
            (("records", 0, "publisher_claim_paraphrase_draft"), "Invented plot"),
            (("records", 0, "synopsis_status"), "APPROVED"),
            (("records", 0, "accepted_work_id"), "global-work"),
            (("records", 0, "viewed_episode"), True),
        ):
            changed = copy.deepcopy(self.original)
            value = changed
            for key in path[:-1]:
                value = value[key]
            value[path[-1]] = fake
            for optimized in (False, True):
                with self.subTest(path=path, optimized=optimized):
                    process = self.run_raw(json.dumps(changed), optimized)
                    self.assertNotEqual(process.returncode, 0, "forgery accepted")
                    self.assertIn("ValueError: DS9 B012 invalid", process.stderr)

    def test_duplicate_key_forgery_rejected_both_modes_and_file_parser(self):
        raw = json.dumps(self.original, separators=(",", ":"))
        attacks = (
            ('"coverage_effect":"NONE"',
             '"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"'),
            ('"current_raw_html_captured":false',
             '"current_raw_html_captured":true,"current_raw_html_captured":false'),
            ('"accepted_work_id":null',
             '"accepted_work_id":"global-work","accepted_work_id":null'),
            ('"episode":26', '"episode":25,"episode":26'),
        )
        for needle, injection in attacks:
            self.assertIn(needle, raw)
            injected_raw = raw.replace(needle, injection, 1)
            for optimized in (False, True):
                with self.subTest(needle=needle, optimized=optimized):
                    process = self.run_raw(injected_raw, optimized)
                    self.assertNotEqual(process.returncode, 0)
                    self.assertIn("DS9 B012 invalid: duplicate JSON key", process.stderr)
            with tempfile.TemporaryDirectory() as temp:
                filename = Path(temp) / "forged.json"
                filename.write_text(injected_raw, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                    read_json(filename)

    def test_no_sixth_new_work_or_extra_fields(self):
        for mutation in ("sixth", "remove", "extra"):
            changed = copy.deepcopy(self.original)
            if mutation == "sixth":
                duplicate = copy.deepcopy(changed["records"][0])
                duplicate.update({"observation_id": "ds9-b012-p06", "episode": 5,
                                  "source_local_row_id": "publisher:s6:ds9:004",
                                  "publisher_card_title": "Favor The Bold"})
                changed["records"].append(duplicate)
            elif mutation == "remove":
                changed["records"].pop()
            else:
                changed["verified_primary_script"] = True
            with self.assertRaisesRegex(ValueError, "DS9 B012 invalid"):
                validate(changed)


if __name__ == "__main__":
    unittest.main()
