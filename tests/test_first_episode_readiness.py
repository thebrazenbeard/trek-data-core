"""Synthetic adversarial tests for the read-only first-episode diagnostic.

No fixture from this module is a real or accepted Star Trek episode.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location("episode_pilot_readiness", TOOLS / "check_episode_pilot_readiness.py")
assert SPEC and SPEC.loader
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)

HASH = "sha256:" + "a" * 64
SERIES = "fixture-series"
EPISODE = "fixture-episode"
SOURCE = "fixture-source"
BINDING = "fixture-binding"


def fixture():
    works = {
        SERIES: {"record_type": "work", "work_id": SERIES, "status": "ACCEPTED",
                 "fixture_only": False, "title": "Example Catalog Series", "work_type": "SERIES",
                 "parent_work_id": None},
        EPISODE: {"record_type": "work", "work_id": EPISODE, "status": "ACCEPTED",
                  "fixture_only": False, "title": "Synthetic Test Installment",
                  "work_type": "EPISODE", "parent_work_id": SERIES},
    }
    sources = {SOURCE: {"source_id": SOURCE, "status": "ACCEPTED", "fixture_only": False,
                        "content_hash": HASH}}
    bindings = {BINDING: {"binding_id": BINDING, "source_id": SOURCE, "work_id": EPISODE,
                          "lifecycle": "ACCEPTED", "mapping_role": "EVIDENCE_BEARING",
                          "fixture_only": False, "basis": [{"kind": "BYTE_HASH", "value": HASH}],
                          "method": "synthetic test", "source_scope": {"scope_type": "WHOLE", "locator": None},
                          "work_scope": {"scope_type": "WHOLE", "component_label": None}}}
    records = [
        {"record_type": "evidence", "evidence_id": "fixture-evidence", "source_id": SOURCE,
         "work_id": EPISODE, "fixture_only": False},
        {"record_type": "assertion", "assertion_id": "fixture-assertion", "status": "ACCEPTED",
         "fixture_only": False, "work_id": EPISODE, "evidence": ["fixture-evidence"]},
        {"record_type": "coverage_event", "coverage_event_id": "fixture-event",
         "status": "ACCEPTED", "effect": "ATTAINED", "coverage_state": "SOURCE_BOUND",
         "work_id": EPISODE, "binding_id": BINDING, "source_id": SOURCE},
    ]
    missions = [{"id": "fixture-mission", "title": "Example Catalog Series", "focus": "synthetic"}]
    return works, sources, bindings, records, missions


def report(*data, work_id=None):
    return pilot.summarize(*data, approved_hash_count=0, requested_work_id=work_id)


class PilotReadinessTests(unittest.TestCase):
    def test_empty_registry_is_blocked_without_promoting_discovery_candidates(self):
        result = report({}, {}, {}, [], fixture()[-1])
        self.assertEqual(result["overall_status"], "TECHNICAL_PREREQUISITES_BLOCKED")
        self.assertEqual(result["accepted_nonfixture_episode_works"], 0)
        self.assertEqual(result["automated_prerequisite_complete_works"], 0)
        self.assertEqual(result["discovery_candidate_rows_counted_as_evidence"], 0)

    def test_all_structural_gates_still_require_human_source_review(self):
        result = report(*fixture())
        self.assertEqual(result["accepted_nonfixture_episode_works"], 1)
        self.assertEqual(result["automated_prerequisite_complete_works"], 1)
        self.assertEqual(result["overall_status"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(result["episodes"][0]["mission_id"], "fixture-mission")
        self.assertEqual(result["episodes"][0]["human_source_review"], "REQUIRED_NOT_MACHINE_VERIFIABLE")
        self.assertEqual(result["complete_mission_denominator"], "NOT_ESTABLISHED_BY_THIS_REPORT")

    def test_cross_work_assertion_cannot_complete_episode_readiness(self):
        data = list(fixture())
        other = "fixture-other-episode"
        data[0][other] = {"record_type": "work", "work_id": other,
                          "status": "ACCEPTED", "fixture_only": False,
                          "work_type": "EPISODE", "title": "Other Synthetic Installment",
                          "parent_work_id": SERIES}
        # An accepted assertion for another Work must not count toward this Work,
        # even when it references an otherwise eligible evidence ID.
        data[3][1]["work_id"] = other
        result = report(*data, work_id=EPISODE)
        gates = result["episodes"][0]["technical_gates"]
        self.assertTrue(gates["binding_grounded_nonfixture_evidence"])
        self.assertFalse(gates["accepted_assertion_referencing_evidence"])
        self.assertEqual(result["automated_prerequisite_complete_works"], 0)

    def test_external_title_candidate_is_never_an_accepted_episode(self):
        data = list(fixture())
        data[0]["candidate-episode"] = {"record_type": "work", "work_id": "candidate-episode",
                                        "status": "PROPOSED", "fixture_only": False,
                                        "work_type": "EPISODE", "title": "Candidate Only",
                                        "parent_work_id": SERIES}
        data[3].append({"record_type": "external_crosswalk", "target_id": "candidate-episode",
                        "mapping_status": "CANDIDATE"})
        result = report(*data)
        self.assertEqual(result["accepted_nonfixture_episode_works"], 1)
        self.assertEqual(result["discovery_candidate_rows_counted_as_evidence"], 0)

    def test_metadata_only_source_work_mapping_does_not_unlock_evidence(self):
        data = list(fixture())
        data[2][BINDING]["mapping_role"] = "METADATA_ONLY"
        result = report(*data)
        self.assertFalse(result["episodes"][0]["technical_gates"]["accepted_byte_hash_source_binding"])
        self.assertFalse(result["episodes"][0]["technical_gates"]["binding_grounded_nonfixture_evidence"])
        self.assertEqual(result["automated_prerequisite_complete_works"], 0)

    def test_forged_or_missing_content_hash_blocks_binding(self):
        data = list(fixture())
        data[1][SOURCE]["content_hash"] = "sha256:" + "0" * 64
        result = report(*data)
        self.assertFalse(result["episodes"][0]["technical_gates"]["accepted_byte_hash_source_binding"])

    def test_fixture_only_episode_is_never_counted(self):
        data = list(fixture())
        data[0][EPISODE]["fixture_only"] = True
        result = report(*data)
        self.assertEqual(result["accepted_nonfixture_episode_works"], 0)

    def test_accepted_work_without_unambiguous_series_ancestor_does_not_resolve(self):
        data = list(fixture())
        data[0][SERIES]["title"] = "Unknown Catalog Series"
        result = report(*data)
        self.assertIsNone(result["episodes"][0]["mission_id"])
        self.assertFalse(result["episodes"][0]["automated_prerequisites_present"])

    def test_broken_parent_reference_fails_mission_association(self):
        data = list(fixture())
        data[0][EPISODE]["parent_work_id"] = "missing-parent"
        result = report(*data)
        self.assertIsNone(result["episodes"][0]["mission_id"])

    def test_missing_evidence_assertion_and_event_are_distinct_gates(self):
        data = list(fixture())
        data[3] = []
        result = report(*data)
        gates = result["episodes"][0]["technical_gates"]
        self.assertTrue(gates["accepted_byte_hash_source_binding"])
        self.assertFalse(gates["binding_grounded_nonfixture_evidence"])
        self.assertFalse(gates["accepted_assertion_referencing_evidence"])
        self.assertFalse(gates["accepted_source_bound_coverage_event"])

    def test_work_id_filter_excludes_unrelated_episodes(self):
        result = report(*fixture(), work_id="not-the-episode")
        self.assertEqual(result["episodes"], [])
        self.assertEqual(result["automated_prerequisite_complete_works"], 0)

    def test_real_main_smoke_is_read_only_and_structured(self):
        run = subprocess.run([sys.executable, str(TOOLS / "check_episode_pilot_readiness.py")],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        payload = json.loads(run.stdout)
        self.assertEqual(payload["schema_version"], "1.0.0")
        self.assertIn(payload["overall_status"],
                      {"TECHNICAL_PREREQUISITES_BLOCKED", "HUMAN_REVIEW_REQUIRED"})
        self.assertEqual(payload["rights_and_source_inspection"], "REQUIRES_INDEPENDENT_HUMAN_REVIEW")
        self.assertEqual(payload["discovery_candidate_rows_counted_as_evidence"], 0)


if __name__ == "__main__":
    unittest.main()
