"""Cross-artifact public index audit; no network, evidence promotion or writes."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from tools import audit_research_leads as audit


ROOT = Path(__file__).resolve().parents[1]


class ResearchLeadsCrossArtifactTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / "registry/mission_catalog.json").read_text())
        self.index = json.loads((ROOT / "explorer/index.json").read_text())
        self.leads = json.loads((ROOT / "explorer/research-leads.json").read_text())

    def run_audit(self):
        return audit.audit_artifacts(self.catalog, self.index, self.leads)

    def test_current_public_artifacts_have_consistent_distinct_tiers(self):
        report = self.run_audit()
        self.assertEqual(report["missions"], 12)
        self.assertEqual(report["unverified_research_leads"], 218)
        self.assertEqual(report["projected_records"], 0)
        self.assertEqual(sum(m["unverified_leads"] for m in report["per_mission"]), 218)
        self.assertEqual(sum(m["admitted_briefings"] for m in report["per_mission"]), 0)
        self.assertEqual(report["admission_effect"], "NONE")
        self.assertEqual(report["coverage_effect"], "NONE")

    def test_display_catalog_cannot_hide_admitted_briefing(self):
        self.index["briefings"].append({"id": "w1", "work_id": "w1", "mission_id": "tos",
                                         "admission_status": "EVIDENCED_IN_PROJECTION"})
        with self.assertRaisesRegex(ValueError, "display-only Explorer"):
            self.run_audit()

    def test_public_mission_catalog_drift_is_rejected(self):
        self.index["missions"][0]["title"] = "Different Mission Title"
        with self.assertRaisesRegex(ValueError, "catalog drift"):
            self.run_audit()

    def test_cross_mission_and_orphan_record_links_are_rejected(self):
        self.index["build"] = {"data_status": "GOVERNED_PROJECTION", "projection_hash": "sha256:" + "a" * 64}
        self.index["briefings"] = [{"id": "w1", "work_id": "w1", "mission_id": "tos",
                                     "admission_status": "EVIDENCED_IN_PROJECTION"}]
        self.index["records"] = [{"id": "r1", "mission_id": "tng", "briefing_id": "w1"}]
        with self.assertRaisesRegex(ValueError, "orphan or cross-Mission"):
            self.run_audit()
        self.index["records"][0]["mission_id"] = None
        with self.assertRaisesRegex(ValueError, "orphan or cross-Mission"):
            self.run_audit()
        self.index["records"][0]["mission_id"] = "tos"
        self.assertEqual(self.run_audit()["per_mission"][0]["admitted_briefings"], 1)

    def test_duplicate_or_wrongly_verified_research_identity_is_rejected(self):
        first = deepcopy(self.leads["leads"][0])
        self.leads["leads"].append(first)
        self.leads["lead_count"] += 1
        with self.assertRaisesRegex(ValueError, "duplicate research candidate"):
            self.run_audit()
        self.leads["leads"].pop()
        self.leads["lead_count"] -= 1
        self.leads["leads"][0]["verification_status"] = "METADATA_VERIFIED"
        with self.assertRaisesRegex(ValueError, "false verification"):
            self.run_audit()

    def test_candidate_counts_and_held_arcs_fail_closed(self):
        self.leads["lead_count"] += 1
        with self.assertRaisesRegex(ValueError, "lead count"):
            self.run_audit()
        self.leads["lead_count"] -= 1
        self.leads["held_candidate_count"] = 0
        with self.assertRaisesRegex(ValueError, "Enterprise arc"):
            self.run_audit()

    def test_rejects_mission_reference_not_in_catalog(self):
        self.leads["leads"][0]["mission_id"] = "not-a-mission"
        with self.assertRaisesRegex(ValueError, "unknown Mission"):
            self.run_audit()

    def test_safe_file_boundary_rejects_symlinked_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "registry").mkdir()
            (root / "explorer").mkdir()
            (root / "registry/mission_catalog.json").write_text(json.dumps(self.catalog))
            (root / "explorer/index.json").write_text(json.dumps(self.index))
            (root / "elsewhere.json").write_text(json.dumps(self.leads))
            (root / "explorer/research-leads.json").symlink_to(root / "elsewhere.json")
            with self.assertRaisesRegex(ValueError, "symlink"):
                audit.audit_directory(root)


if __name__ == "__main__":
    unittest.main()
