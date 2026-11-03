"""Unresolved source-local *proposal* query, never accepted identity or coverage."""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from query_source_local_unresolved import INPUTS, TRUSTED_SHA256, _compile, build, query  # noqa: E402


class UnresolvedProposalQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build(ROOT)

    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        for assertion_path, evidence_path, *_ in INPUTS:
            for relative in (assertion_path, evidence_path):
                source = ROOT / relative
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        return temporary, root

    def test_exact_unresolved_frontier_is_source_local_not_admitted(self):
        report = self.report
        self.assertEqual(report["data_status"], "ACCEPTED_FILES_WITH_UNADMITTED_PROPOSALS_ONLY")
        self.assertEqual(report["unresolved_proposal_count"], 22)
        self.assertEqual(report["total_proposal_assertions_observed"], 27)
        self.assertEqual(report["plain_proposals_not_in_unresolved_report"], 5)
        self.assertEqual(report["source_file_count"], 6)
        self.assertEqual(report["kind_counts"], {
            "PROPOSED_UNRESOLVED": 6, "PROPOSED_PROJECTED_CONTESTED": 1,
            "PROPOSED_PROJECTED_UNRESOLVED": 15,
        })
        self.assertEqual(report["admission_effect"], "NONE")
        self.assertEqual(report["coverage_effect"], "NONE")
        self.assertEqual(report["identity_resolution_effect"], "NONE")
        self.assertEqual(len(report["source_sha256"]), 12)
        self.assertEqual(len({r["source_path"] + ":" + r["assertion_id"] for r in report["rows"]}), 22)
        self.assertTrue(all(r["evidence_ids"] and r["falsifier"] for r in report["rows"]))
        self.assertTrue(all(r["truth_status"] == "PROPOSED_NOT_ADMITTED" for r in report["rows"]))
        self.assertEqual(report, build(ROOT), "same exact accepted files must yield byte-identical projection structure")

    def test_filtering_never_infers_cross_source_identity(self):
        report = self.report
        self.assertEqual(query(report, kind="PROPOSED_UNRESOLVED")["total_matches"], 6)
        self.assertEqual(query(report, kind="PROPOSED_PROJECTED_CONTESTED")["total_matches"], 1)
        self.assertEqual(query(report, batch="ds9-source-custody-gap-20261103")["total_matches"], 3)
        self.assertEqual(query(report, predicate="SOURCE_VERSION_RECONCILIATION_REQUIRED")["total_matches"], 1)
        self.assertEqual(query(report, text="date labels")["total_matches"], 1)
        self.assertEqual(query(report, text="canonical same work")["total_matches"], 0)
        self.assertEqual(query(report, kind="FICTITIOUS_ACCEPTED")["total_matches"], 0)
        page = query(report, limit=4)
        following = query(report, offset=page["next_offset"], limit=4)
        self.assertEqual(page["total_matches"], 22)
        self.assertEqual(set(r["source_key"] for r in page["rows"]) &
                         set(r["source_key"] for r in following["rows"]), set())

    def test_closed_envelopes_refuse_promotions_global_ids_forgery_and_broken_evidence(self):
        for modify in (
            lambda d: d.update(projection_effect="ADMIT"),
            lambda d: d.update(accepted_assertions=1),
            lambda d: d.update(unknown_authoritative_status="AUDITED"),
            lambda d: d["assertions"][0].update(status="ACCEPTED"),
            lambda d: d["assertions"][0].update(canonical_work_id="global:fake"),
            lambda d: d["assertions"][0].update(evidence_ids=["invented-evidence"]),
            lambda d: d["assertions"][0].update(subject_source_local_row_id="global:fake"),
            lambda d: d["assertions"].append(copy.deepcopy(d["assertions"][0])),
        ):
            temp, root = self.fixture()
            try:
                target = root / INPUTS[1][0]  # DS9 B006 positive proposal source
                data = json.loads(target.read_text())
                modify(data)
                target.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    build(root)
                with self.assertRaises(ValueError, msg="closed schema rejects mutant independent of SHA pins"):
                    _compile(root, enforce_pins=False)
            finally:
                temp.cleanup()

    def test_derivative_tos_stable_state_and_duplicate_json_key_are_rejected(self):
        temp, root = self.fixture()
        try:
            target = root / INPUTS[-1][0]
            data = json.loads(target.read_text())
            data["assertions"][0]["proposed_projection_status"] = "STABLE"
            target.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                build(root)
            with self.assertRaises(ValueError):
                _compile(root, enforce_pins=False)
        finally:
            temp.cleanup()
        temp, root = self.fixture()
        try:
            target = root / INPUTS[1][0]
            target.write_text(target.read_text().replace('"projection_effect": "NONE"',
                                                         '"projection_effect": "NONE", "projection_effect": "NONE"'))
            with self.assertRaises(ValueError):
                build(root)
            with self.assertRaises(ValueError):
                _compile(root, enforce_pins=False)
        finally:
            temp.cleanup()

    def test_symlink_file_and_ancestor_fail_closed(self):
        for ancestor in (False, True):
            temp, root = self.fixture()
            try:
                source = root / INPUTS[0][0]
                if ancestor:
                    folder = source.parent
                    alias = folder.with_name(folder.name + "-safe-copy")
                    folder.rename(alias)
                    folder.symlink_to(alias, target_is_directory=True)
                else:
                    real = source.with_suffix(".backup")
                    source.rename(real)
                    source.symlink_to(real)
                with self.assertRaises(ValueError):
                    build(root)
                with self.assertRaises(ValueError):
                    _compile(root, enforce_pins=False)
            finally:
                temp.cleanup()

    def test_hash_receipts_block_plausible_fabricated_statement_and_cross_local_work(self):
        self.assertEqual(len(TRUSTED_SHA256), 12)
        temp, root = self.fixture()
        try:
            target = root / INPUTS[1][0]
            data = json.loads(target.read_text())
            data["assertions"][0]["statement"] = "Invented but structurally plausible publisher claim."
            target.write_text(json.dumps(data))
            # A shape-valid forged assertion must not become a trusted report.
            _compile(root, enforce_pins=False)
            with self.assertRaisesRegex(ValueError, "bytes drifted"):
                build(root)
        finally:
            temp.cleanup()
        temp, root = self.fixture()
        try:
            target = root / INPUTS[-1][0]
            data = json.loads(target.read_text())
            item = next(row for row in data["assertions"] if row["subject_type"] == "WORK")
            item["subject"] = "tos-charlie-x-candidate-20261103"
            target.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                _compile(root, enforce_pins=False)
        finally:
            temp.cleanup()

    def test_cli_machine_json_and_bounds(self):
        cli = ROOT / "tools/query_source_local_unresolved.py"
        output = subprocess.run([sys.executable, cli, "--kind", "PROPOSED_PROJECTED_CONTESTED", "--limit", "1"],
                                capture_output=True, text=True, check=True)
        data = json.loads(output.stdout)
        self.assertEqual(data["total_matches"], 1)
        self.assertEqual(data["rows"][0]["truth_status"], "PROPOSED_NOT_ADMITTED")
        for args in (("--limit", "101"), ("--offset", "-1")):
            denied = subprocess.run([sys.executable, cli, *args], capture_output=True, text=True)
            self.assertNotEqual(denied.returncode, 0)


if __name__ == "__main__":
    unittest.main()
