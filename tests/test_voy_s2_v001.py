"""Source-relative Voyager Season 2 title/slot records, held artwork and synopsis."""

import copy
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "proposals/research/voy-s2-middle-v001-20261103"
functions = runpy.run_path(str(HERE / "validate.py"))
validate = functions["validate"]
read_json = functions["read_json"]
PROBE = (
    "import json,sys\n"
    "sys.path.insert(0,sys.argv[1])\n"
    "from validate import validate,unique_pairs\n"
    "validate(json.load(sys.stdin,object_pairs_hook=unique_pairs))\n"
)


class VoyagerSeasonTwoSourceCards(unittest.TestCase):
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

    def test_ten_nonduplicate_held_metadata_cards_both_modes(self):
        self.assertEqual(validate(self.original), 10)
        self.assertEqual([r["episode"] for r in self.original["records"]], list(range(6, 16)))
        self.assertEqual(self.original["coverage_effect"], "NONE")
        self.assertEqual(self.original["public_artwork_effect"], "NONE")
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self._run(self.original, optimized)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_forged_source_admission_and_artwork_rights_rejected(self):
        cases = (
            (("batch_id",), "wrong-batch"),
            (("proposal_only",), 1),
            (("accepted_main_at_selection",), "0" * 40),
            (("publisher_guide_url",), "https://example.com/fake"),
            (("publisher_source_family",), "independent_primary"),
            (("source_independence_status",), "INDEPENDENT_CORROBORATION"),
            (("source_directory_sha256",), "0" * 64),
            (("historical_publisher_csv_sha256",), "0" * 64),
            (("accepted_voy_b006_source_record_sha256",), "0" * 64),
            (("current_raw_html_sha256",), "0" * 64),
            (("current_raw_html_captured",), True),
            (("actual_episode_or_script_read",), True),
            (("synopsis_artwork_policy",), "PUBLICATION_AUTHORIZED"),
            (("accepted_source_work_effect",), "SOURCE_BOUND"),
            (("accepted_work_effect",), "ACCEPTED"),
            (("coverage_effect",), "CLOSE_READ"),
            (("public_synopsis_effect",), "PUBLISHED"),
            (("public_artwork_effect",), "PUBLISHED"),
            (("license_verified",), True),
            (("records", 0, "source_local_row_id"), "legacy:s2:voy:001"),
            (("records", 0, "episode"), 2),
            (("records", 0, "publisher_card_title"), "Invented Title"),
            (("records", 0, "local_entity_id"), "global-voy-episode"),
            (("records", 0, "evidence_kind"), "PRIMARY_VIDEO_CLOSE_READ"),
            (("records", 0, "synopsis_status"), "APPROVED"),
            (("records", 0, "artwork_asset_url"), "https://example.org/borrowed.jpg"),
            (("records", 0, "artwork_rights_status"), "LICENSED"),
            (("records", 0, "artwork_candidate_page_url"), "https://thirdparty.com"),
            (("records", 0, "accepted_work_id"), "global-voy-001"),
            (("records", 0, "rights_statement"), "PUBLIC_DOMAIN"),
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
                    self.assertNotEqual(result.returncode, 0, "forged provenance or rights passed")
                    self.assertIn("ValueError: VOY V001 invalid", result.stderr)

    def test_raw_duplicate_json_keys_rejected_both_modes(self):
        raw = json.dumps(self.original, separators=(",", ":"))
        attacks = (
            ('"coverage_effect":"NONE"',
             '"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"'),
            ('"current_raw_html_captured":false',
             '"current_raw_html_captured":true,"current_raw_html_captured":false'),
            ('"artwork_rights_status":"UNKNOWN_HELD"',
             '"artwork_rights_status":"LICENSED","artwork_rights_status":"UNKNOWN_HELD"'),
            ('"accepted_work_id":null',
             '"accepted_work_id":"fake-work","accepted_work_id":null'),
        )
        for needle, injected in attacks:
            self.assertIn(needle, raw)
            forged_raw = raw.replace(needle, injected, 1)
            for optimized in (False, True):
                with self.subTest(needle=needle, optimized=optimized):
                    result = self._run_raw(forged_raw, optimized)
                    self.assertNotEqual(result.returncode, 0, "duplicate-key raw payload passed")
                    self.assertIn("ValueError: VOY V001 invalid: duplicate JSON key",
                                  result.stderr)

    def test_real_file_reader_rejects_duplicate_key(self):
        raw = json.dumps(self.original, separators=(",", ":"))
        forged = raw.replace('"public_artwork_effect":"NONE"',
                             '"public_artwork_effect":"PUBLISHED","public_artwork_effect":"NONE"', 1)
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "forged.json"
            file_path.write_text(forged, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "VOY V001 invalid: duplicate JSON key"):
                read_json(file_path)

    def test_coherent_prior_s2e2_card_injection_rejected(self):
        changed = copy.deepcopy(self.original)
        injected = copy.deepcopy(changed["records"][0])
        injected.update({"observation_id": "voy-v001-o11", "local_entity_id": "voy-v001-card-11",
                         "source_local_row_id": "legacy:s2:voy:001", "episode": 2,
                         "publisher_card_title": "Initiations",
                         "card_locator": "Season 2 Episode Guide > S2 E2 > Initiations"})
        changed["records"].append(injected)
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self._run(changed, optimized)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ValueError: VOY V001 invalid: ten VOY S2 records",
                              result.stderr)


if __name__ == "__main__":
    unittest.main()
