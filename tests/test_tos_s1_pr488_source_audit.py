"""Deterministic and hostile checks on a narrow external metadata-source audit."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_tos_s1_pr488", ROOT / "tools/audit_tos_s1_pr488.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class Pr488SourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = mod.parse_json(mod.REVIEW.read_bytes())
        cls.leads = mod.parse_json(mod.hash_accepted(mod.LEADS, mod.LEADS_SHA))
        cls.csv_bytes = mod.hash_accepted(mod.PUBLISHER, mod.PUBLISHER_SHA)

    def check(self, change=None):
        audit = copy.deepcopy(self.audit)
        if change:
            change(audit)
        return mod.analyze(audit, self.leads, self.csv_bytes)

    def test_five_live_guide_title_slots_match_and_ordinal_namespaces_disagree(self):
        report = self.check()
        self.assertEqual(report["status"], "ORDINAL_NAMESPACE_DIVERGENCE_OBSERVED")
        self.assertEqual(report["exact_live_publisher_title_slot_matches"], 5)
        self.assertEqual(report["independent_publisher_guide_families"], 1)
        self.assertEqual(report["independent_wdqs_snapshot_families"], 1)
        self.assertFalse(report["raw_live_page_hash_available"])
        self.assertEqual(report["accepted_source_work_coverage_effect"], "NONE")
        self.assertEqual({(row["qid"], row["publisher_slot"] - row["wikidata_ordinal"])
                          for row in report["ordinal_namespace_differences"]},
                         {(qid, 1) for qid in ["Q2664096", "Q2984502", "Q3107459", "Q3178411", "Q3487125"]})

    def test_mutated_publisher_ordinal_rejected(self):
        with self.assertRaisesRegex(mod.AuditError, "publisher title/slot"):
            self.check(lambda a: a["rows"][0].update(paramount_slot=9))

    def test_mutated_title_rejected(self):
        with self.assertRaisesRegex(mod.AuditError, "QID/title"):
            self.check(lambda a: a["rows"][0].update(title="The Cage"))

    def test_qid_crossing_rejected(self):
        with self.assertRaisesRegex(mod.AuditError, "QID/title"):
            self.check(lambda a: a["rows"][0].update(qid="Q3107459", wikidata_item_url="https://www.wikidata.org/wiki/Q3107459"))

    def test_duplicate_candidate_rejected(self):
        with self.assertRaisesRegex(mod.AuditError, "repeated candidate"):
            self.check(lambda a: a["rows"][1].update(qid=a["rows"][0]["qid"]))

    def test_forged_custody_and_coverage_claims_rejected(self):
        for mutation, expected in (
            (lambda a: a["publisher_observation"].update(raw_body_sha256="sha256:" + "a"*64), "custody"),
            (lambda a: a.update(coverage_effect="SOURCE_BOUND"), "admission"),
            (lambda a: a["publisher_observation"].update(full_episode_content_read=True), "custody"),
        ):
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(mod.AuditError, expected):
                    self.check(mutation)

    def test_forged_independent_wdqs_snapshot_rejected(self):
        with self.assertRaisesRegex(mod.AuditError, "custody"):
            self.check(lambda a: a["wikidata_observation"].update(historical_discovery_independence_group="independent:five"))

    def test_selection_matches_exact_pr_rows_and_mutation_rejects(self):
        rows = [{"qid": r["qid"], "season": r["season"], "publisher_episode_number": r["paramount_slot"], "publisher_title": r["title"]} for r in self.audit["rows"]]
        selection = {"source_custody": {"publisher_page": mod.GUIDE, "live_page_rechecked": False}, "selected": rows}
        mod.validate_pr_selection(selection, self.audit)
        selection["selected"][0]["publisher_episode_number"] += 1
        with self.assertRaisesRegex(mod.AuditError, "disagrees"):
            mod.validate_pr_selection(selection, self.audit)

    def test_optimized_python_does_not_bypass_checks(self):
        child = subprocess.run(["python3", "-O", "tools/audit_tos_s1_pr488.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertIn("ORDINAL_NAMESPACE_DIVERGENCE_OBSERVED", child.stdout)


if __name__ == "__main__":
    unittest.main()
