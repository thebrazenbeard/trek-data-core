"""Lower Decks S1 source-local guide cards: provenance, literal mentions and holds."""

import copy
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "proposals/research/ld-s1-guide-l001-20261103"
functions = runpy.run_path(str(HERE / "validate.py"))
validate = functions["validate"]
read_json = functions["read_json"]
PROBE = (
    "import json,sys\n"
    "sys.path.insert(0,sys.argv[1])\n"
    "from validate import validate,unique_pairs\n"
    "validate(json.load(sys.stdin,object_pairs_hook=unique_pairs))\n"
)


class LowerDecksS1Cards(unittest.TestCase):
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

    def test_exact_ten_cards_and_held_scope(self):
        self.assertEqual(validate(self.original), 10)
        self.assertEqual([r["episode"] for r in self.original["records"]], list(range(1, 11)))
        self.assertEqual(self.original["coverage_effect"], "NONE")
        self.assertEqual(self.original["public_artwork_effect"], "NONE")
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                run = self._run(self.original, optimized)
                self.assertEqual(run.returncode, 0, run.stderr)

    def test_forged_provenance_rights_identity_and_plot_admission_rejected(self):
        cases = (
            (("batch_id",), "different-batch"),
            (("proposal_only",), 1),
            (("accepted_main_at_selection",), "0" * 40),
            (("publisher_guide_url",), "https://example.org/fake"),
            (("source_scope",), "FULL_EPISODE_CLOSE_READ"),
            (("publisher_source_family",), "independent_witnesses"),
            (("source_independence_status",), "INDEPENDENT_CORROBORATION"),
            (("source_directory_sha256",), "0" * 64),
            (("historical_publisher_csv_sha256",), "0" * 64),
            (("historical_observation_receipt_sha256",), "0" * 64),
            (("current_raw_html_sha256",), "0" * 64),
            (("current_raw_html_captured",), True),
            (("actual_episode_or_script_read",), True),
            (("description_source_policy",), "EPISODE_SCRIPT_QUOTED"),
            (("synopsis_policy",), "PUBLIC_STORY_EVENTS"),
            (("artwork_policy",), "LICENSED_ASSET"),
            (("accepted_source_work_effect",), "BOUND"),
            (("accepted_work_effect",), "ACCEPTED"),
            (("coverage_effect",), "CLOSE_READ"),
            (("public_synopsis_effect",), "PUBLISHED"),
            (("public_artwork_effect",), "PUBLISHED"),
            (("primary_source_verified",), True),
            (("records", 0, "source_local_row_id"), "roster:modern-s1:ld:001"),
            (("records", 0, "publisher_card_title"), "Different Episode"),
            (("records", 0, "evidence_kind"), "EPISODE_DEPICTION"),
            (("records", 0, "evidence_scope"), "PLOT_TRUTH"),
            (("records", 0, "literal_mentions"), ["Picard"]),
            (("records", 0, "synopsis_status"), "APPROVED"),
            (("records", 0, "artwork_asset_url"), "https://example.org/image.png"),
            (("records", 0, "artwork_rights_status"), "LICENSED"),
            (("records", 0, "accepted_work_id"), "global-ld-001"),
            (("records", 0, "depicted_action_verified"), True),
        )
        for path, value in cases:
            changed = copy.deepcopy(self.original)
            node = changed
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = value
            for optimized in (False, True):
                with self.subTest(path=path, optimized=optimized):
                    run = self._run(changed, optimized)
                    self.assertNotEqual(run.returncode, 0, "forged metadata accepted")
                    self.assertIn("ValueError: LD L001 invalid", run.stderr)

    def test_raw_duplicate_key_forgery_rejected(self):
        raw = json.dumps(self.original, separators=(",", ":"))
        attacks = (
            ('"coverage_effect":"NONE"',
             '"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"'),
            ('"actual_episode_or_script_read":false',
             '"actual_episode_or_script_read":true,"actual_episode_or_script_read":false'),
            ('"artwork_rights_status":"UNKNOWN_HELD"',
             '"artwork_rights_status":"LICENSED","artwork_rights_status":"UNKNOWN_HELD"'),
            ('"literal_mentions":["Ensign Tendi"',
             '"literal_mentions":["Picard"],"literal_mentions":["Ensign Tendi"'),
        )
        for needle, injected in attacks:
            self.assertIn(needle, raw)
            forged = raw.replace(needle, injected, 1)
            for optimized in (False, True):
                with self.subTest(needle=needle, optimized=optimized):
                    run = self._run_raw(forged, optimized)
                    self.assertNotEqual(run.returncode, 0, "duplicate-key raw payload accepted")
                    self.assertIn("ValueError: LD L001 invalid: duplicate JSON key", run.stderr)

    def test_file_bound_json_reader_strict(self):
        raw = json.dumps(self.original, separators=(",", ":"))
        forged = raw.replace('"public_synopsis_effect":"NONE"',
                             '"public_synopsis_effect":"PUBLISHED","public_synopsis_effect":"NONE"', 1)
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "raw.json"
            file_path.write_text(forged, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "LD L001 invalid: duplicate JSON key"):
                read_json(file_path)


if __name__ == "__main__":
    unittest.main()
