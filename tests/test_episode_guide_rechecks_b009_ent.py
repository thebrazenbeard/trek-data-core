"""B009 Enterprise: source-relative first-party card acceptance must fail closed."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/build_episode_guide_rechecks_b009_ent.py"
SPEC = importlib.util.spec_from_file_location("b009_ent_compiler", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class B009EnterpriseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.raw = MOD.load(MOD.CATALOG)
        cls.source, _ = MOD.load(MOD.SOURCE)

    def outcome(self, mutate):
        source = copy.deepcopy(self.source)
        mutate(source)
        with self.assertRaises(ValueError):
            MOD.compile_records(self.catalog, self.raw, source)

    def test_deterministic_source_only_compiler(self):
        output = MOD.compile_records(self.catalog, self.raw, self.source)
        self.assertEqual(output["summary"]["source_local_rows_rechecked"], 9)
        self.assertEqual(output["summary"]["literal_title_card_matches"], 3)
        self.assertEqual(output["summary"]["combined_card_split_rows_unresolved"], 2)
        self.assertEqual(output["summary"]["public_synopses_approved"], 0)
        self.assertEqual(output["summary"]["governed_source_or_work_admissions"], 0)
        self.assertTrue(all(x["admission_effect"] == x["coverage_effect"] == "NONE" for x in output["rows"]))
        self.assertEqual([x["source_local_row_id"] for x in output["rows"]], [f"lead:{i:04d}" for i in range(99, 108)])
        self.assertTrue(all(x["original_synopsis_draft"] is None for x in output["rows"][3:]))

    def test_combined_broken_bow_is_not_two_distinct_publisher_cards(self):
        output = MOD.compile_records(self.catalog, self.raw, self.source)
        a, b = output["rows"][-2:]
        self.assertEqual((a["official_card"]["season"], a["official_card"]["episode"]), (1, 1))
        self.assertEqual((b["official_card"]["season"], b["official_card"]["episode"]), (1, 1))
        self.assertEqual(a["title_resolution"], "COMBINED_CARD_SPLIT_UNRESOLVED")
        self.assertEqual(b["title_resolution"], "COMBINED_CARD_SPLIT_UNRESOLVED")

    def test_malicious_admission_or_coverage_rejected(self):
        self.outcome(lambda x: x.update(admission_effect="ADMITTED"))
        self.outcome(lambda x: x.update(coverage_effect="CLOSE_READ"))
        self.outcome(lambda x: x.update(public_synopsis_authorized=True))

    def test_false_full_episode_or_raw_html_claim_rejected(self):
        self.outcome(lambda x: x.update(episode_video_or_transcript_read=True))
        self.outcome(lambda x: x.update(raw_webpage_bytes_custodied=True))

    def test_identity_style_is_not_normalized_silently(self):
        self.outcome(lambda x: x["rows"][3].update(title_resolution="EXACT_OFFICIAL_CARD_TITLE"))
        self.outcome(lambda x: x["rows"][6].update(title_resolution="EXACT_OFFICIAL_CARD_TITLE"))
        self.outcome(lambda x: x["rows"][7].update(title_resolution="EXACT_OFFICIAL_CARD_TITLE"))
        self.outcome(lambda x: x["rows"][8].update(episode=2))

    def test_held_variants_cannot_publish_synopsis(self):
        self.outcome(lambda x: x["rows"][3].update(original_synopsis_draft="Invented identity-resolved synopsis."))

    def test_exact_synopsis_fidelity_is_pinned(self):
        self.outcome(lambda x: x["rows"][0].update(original_synopsis_draft="A different story with plausible words added."))
        self.outcome(lambda x: x["rows"][2].update(original_synopsis_draft="Unverified plot from a recap."))

    def test_source_local_id_and_publisher_slot_guard(self):
        self.outcome(lambda x: x["rows"][0].update(row_id="lead:0098"))
        self.outcome(lambda x: x["rows"][1].update(episode=23))
        self.outcome(lambda x: x["rows"][4].update(official_card_title="Storm Front, Part I"))

    def test_parser_rejects_duplicate_keys(self):
        with self.assertRaises(ValueError):
            json.loads('{"row_id":"lead:0099","row_id":"lead:0100"}', object_pairs_hook=MOD.unique_keys)

    def test_stale_output_fails_closed(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
