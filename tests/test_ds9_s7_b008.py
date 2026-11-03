"""Hostile source-relative DS9 S7E12-E16 nonduplicate publisher-card validation."""

import copy
import json
import runpy
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "proposals/research/ds9-s7-publisher-cards-b008-20261103"
validate = runpy.run_path(str(HERE / "validate.py"))["validate"]
PROBE = (
    "import json, sys\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "from validate import validate\n"
    "validate(json.load(sys.stdin))\n"
)


class DS9PublisherCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads((HERE / "observations.json").read_text(encoding="utf-8"))

    def test_exact_five_held_records_pass_without_admission(self):
        self.assertEqual(validate(self.base), 5)
        self.assertEqual(self.base["coverage_effect"], "NONE")
        self.assertEqual(self.base["public_synopsis_effect"], "NONE")
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                run = subprocess.run(
                    [sys.executable, *( ["-O"] if optimized else []), "-c", PROBE, str(HERE)],
                    input=json.dumps(self.base), text=True, capture_output=True, check=False,
                )
                self.assertEqual(run.returncode, 0, run.stderr)

    def test_forged_source_identity_release_and_variant_rejected(self):
        cases = (
            (("publisher_guide_url",), "https://example.org/fake"),
            (("publisher_independence_group",), "independent_observer"),
            (("fresh_raw_html_sha256",), "0" * 64),
            (("fresh_raw_html_captured",), True),
            (("full_episode_or_script_read",), True),
            (("accepted_source_work_binding_effect",), "ACCEPTED"),
            (("coverage_effect",), "CLOSE_READ"),
            (("public_synopsis_effect",), "APPROVED"),
            (("new_accepted_work_id",), "ds9-global-work-001"),
            (("records", 0, "accepted_work_id"), "ds9-global-work-001"),
            (("records", 1, "publisher_card_title"), "The Siege of AR-558"),
            (("records", 1, "title_slot_status"), "CANONICAL_CORRECTED"),
            (("records", 1, "synopsis_status"), "APPROVED_FOR_PUBLICATION"),
            (("records", 1, "source_local_row_id"), "publisher:s7:ds9:006"),
            (("records", 1, "source_body_verified"), True),
            (("unaccepted_overlap_hold", "prior_draft_pr"), 0),
            (("unaccepted_overlap_hold", "new_records_from_excluded_rows"), 1),
            (("unaccepted_overlap_hold", "excluded_source_local_row_ids"),
             ["publisher:s7:ds9:011"]),
            (("unaccepted_overlap_hold", "prior_draft_status"), "ACCEPTED_EVIDENCE"),
        )
        for path, replacement in cases:
            mutated = copy.deepcopy(self.base)
            target = mutated
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = replacement
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    validate(mutated)


if __name__ == "__main__":
    unittest.main()
