"""Fail-closed, source-local lead qualification tests."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_lead_source_crosswalk as crosswalk


class LeadSourceCrosswalkTest(unittest.TestCase):
    def setUp(self) -> None:
        self.selection = json.loads((crosswalk.BATCH / "selection.json").read_text(encoding="utf-8"))

    def test_generated_artifact_and_count_boundaries(self) -> None:
        generated = crosswalk.canonical_bytes(crosswalk.build())
        self.assertEqual((crosswalk.BATCH / "crosswalk.json").read_bytes(), generated)
        payload = json.loads(generated)
        self.assertEqual(payload["source_local_crosswalk_count"], 5)
        self.assertEqual(payload["total_research_leads_unchanged"], 218)
        self.assertEqual(payload["publisher_raw_html_new_capture"], "NOT_CAPTURED")
        self.assertEqual(payload["proposal_status"], "SOURCE_RELATIVE_METADATA_CROSSWALK_ONLY")
        for effect in ("source_work_binding_admission", "briefing_admission_effect", "denominator_effect", "coverage_effect"):
            self.assertEqual(payload[effect], "NONE")

    def test_source_receipts_and_lineage_are_preserved(self) -> None:
        output = crosswalk.build()
        self.assertEqual(len({x["candidate_qid"] for x in output["matches"]}), 5)
        self.assertEqual(len({(x["publisher_season"], x["publisher_episode_number"]) for x in output["matches"]}), 5)
        for row in output["matches"]:
            self.assertEqual(row["candidate_title"], row["publisher_title"])
            self.assertEqual(row["candidate_mission"], "tos")
            self.assertEqual(row["status"], "PROPOSED_TITLE_AND_SERIES_CROSSWALK")
            self.assertEqual(row["candidate_independence_group"], "wikidata:wdqs")
            self.assertEqual(row["publisher_independence_group"], "publisher:paramount")
            self.assertRegex(row["publisher_prior_html_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(row["publisher_observation_csv_sha256"], r"^[0-9a-f]{64}$")
            self.assertIsNone(row["canonical_work_id"])
            self.assertIsNone(row["accepted_source_work_binding"])
            self.assertEqual(row["coverage_effect"], "NONE")

    def _mutated_selection_fails(self, mutate) -> None:
        modified = copy.deepcopy(self.selection)
        mutate(modified)
        with tempfile.TemporaryDirectory(prefix="trek-lead-crosswalk-test-") as folder:
            temp = Path(folder)
            (temp / "selection.json").write_text(json.dumps(modified), encoding="utf-8")
            with patch.object(crosswalk, "BATCH", temp):
                with self.assertRaises(crosswalk.CrosswalkValidationError):
                    crosswalk.build()

    def test_title_or_ordinal_swap_fails_closed(self) -> None:
        self._mutated_selection_fails(lambda x: x["selected"][0].update(publisher_episode_number=3))
        self._mutated_selection_fails(lambda x: x["selected"][0].update(publisher_rendered_heading_locator="Unrelated Heading"))

    def test_unknown_or_duplicate_identifier_fails_closed(self) -> None:
        self._mutated_selection_fails(lambda x: x["selected"][0].update(qid="Q999999999999999999"))
        self._mutated_selection_fails(lambda x: x["selected"][1].update(qid=x["selected"][0]["qid"]))

    def test_archive_selection_has_no_new_html_hash(self) -> None:
        reader = self.selection["publisher_page_rendered_recheck"]
        self.assertEqual(reader["retrieved_by"], "PUBLIC_WEB_READER")
        self.assertFalse(reader["raw_html_retrieved_in_this_batch"])
        self.assertIsNone(reader["new_raw_response_sha256"])
        self.assertFalse(reader["web_reader_line_numbers_are_durable_source_locators"])
        selection_bytes = (crosswalk.BATCH / "selection.json").read_bytes()
        self.assertEqual(crosswalk.build()["selection_sha256"], hashlib.sha256(selection_bytes).hexdigest())

    def test_python_optimized_mode_rejects_bad_ordinal(self) -> None:
        poisoned = copy.deepcopy(self.selection)
        poisoned["selected"][0]["publisher_episode_number"] = 3
        with tempfile.TemporaryDirectory(prefix="trek-lead-opt-test-") as folder:
            temp = Path(folder)
            (temp / "selection.json").write_text(json.dumps(poisoned), encoding="utf-8")
            probe = (
                "from pathlib import Path; "
                "from tools import build_lead_source_crosswalk as m; "
                f"m.BATCH = Path({str(temp)!r}); "
                "m.build()"
            )
            result = subprocess.run(
                [sys.executable, "-O", "-c", probe],
                cwd=crosswalk.ROOT,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CrosswalkValidationError", result.stderr)


if __name__ == "__main__":
    unittest.main()
