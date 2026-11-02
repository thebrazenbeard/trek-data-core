"""Adversarial, offline contracts for branch retirement planning.

The planner must never infer deletion authority from a shared Git tip or a
historical PR-head snapshot. No remote service or branch mutation is used.
"""

import copy
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "plan_branch_retirement.py"
SPEC = importlib.util.spec_from_file_location("plan_branch_retirement", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
planner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(planner)


def fixture():
    return {
        "schema_version": "trek-branch-census-v2",
        "base_ref": "refs/trek-audit/branch-heads/main",
        "base_sha": "a" * 40,
        "ref_layout": {
            "branch_root": "refs/trek-audit/branch-heads",
            "pr_head_root": "refs/trek-audit/pr-heads",
        },
        "summary": {
            "non_main_branches": 3,
            "total_branches_including_main": 4,
            "distinct_non_main_heads": 2,
            "accessible_pr_head_refs": 2,
        },
        "head_groups": [
            {
                "sha": "b" * 40,
                "tree_sha": "d" * 40,
                "branch_count": 2,
                "branches": ["research/tng", "pr/82"],
                "contains_folder_open_task": False,
                "main_only_commits": 9,
                "branch_only_commits": 1,
            },
            {
                "sha": "c" * 40,
                "tree_sha": "e" * 40,
                "branch_count": 1,
                "branches": ["review/strange-new-worlds"],
                "contains_folder_open_task": False,
                "main_only_commits": 2,
                "branch_only_commits": 0,
            },
        ],
        "pr_head_refs": [
            {"number": "82", "sha": "c" * 40},
            {"number": "91", "sha": "b" * 40},
        ],
    }


class RetirementPlanTests(unittest.TestCase):
    def test_all_names_held_and_receipts_are_exact(self):
        result = planner.plan(fixture())
        self.assertEqual(result["effect"], "READ_ONLY_NO_REF_MUTATIONS")
        self.assertEqual(result["summary"], {
            "non_main_names": 3,
            "distinct_non_main_tips": 2,
            "duplicate_tip_extra_names": 1,
            "retirement_actions_authorized": 0,
            "pr_head_snapshot_refs": 2,
        })
        self.assertEqual([hold["ref"] for hold in result["branch_holds"]], [
            "refs/heads/pr/82", "refs/heads/research/tng", "refs/heads/review/strange-new-worlds"
        ])
        for hold in result["branch_holds"]:
            self.assertEqual(hold["proposed_effect"], "NONE")
            self.assertEqual(hold["retirement_decision"], "HOLD_PER_REF_REVIEW")
            self.assertEqual(hold["recovery_receipt"]["ref"], hold["ref"])
            self.assertEqual(hold["recovery_receipt"]["commit_sha"], hold["tip_sha"])
            self.assertEqual(hold["recovery_receipt"]["remote_object_retention"], "NOT_VERIFIED")
            self.assertEqual(len(hold["checks_required_before_any_later_deletion"]), 4)
        self.assertEqual(result["groups"][0]["branch_names"], ["pr/82", "research/tng"])
        self.assertEqual(result["groups"][0]["matching_pr_snapshot_numbers_not_open_pr_status"], ["91"])
        self.assertEqual(result["groups"][1]["matching_pr_snapshot_numbers_not_open_pr_status"], ["82"])
        self.assertEqual(result["basis"]["branch_snapshot_name_count"], 4)
        for group in result["groups"]:
            self.assertEqual(group["tree_identity_verification"], "NOT_VERIFIED")
            self.assertEqual(group["historical_path_inspection"], "NOT_INSPECTED")
            self.assertFalse(group["recoverability"]["tree_read_from_local_audit_objects"])

    def test_order_does_not_change_hash_or_receipts(self):
        census = fixture()
        baseline = planner.plan(census)
        census["head_groups"].reverse()
        census["head_groups"][1]["branches"].reverse()
        census["pr_head_refs"].reverse()
        self.assertEqual(planner.plan(census), baseline)

    def test_legacy_tip_and_task_signal_prevent_any_optimistic_label(self):
        census = fixture()
        census["head_groups"][0]["sha"] = "a9ebf9e4d7e1645e3d9c7be2c6766cd3b04bfc86"
        census["head_groups"][0]["contains_folder_open_task"] = True
        group = planner.plan(census)["groups"][0]
        self.assertEqual(group["classification"], "HISTORICAL_HAZARD_HOLD")
        self.assertIn("PINNED_LEGACY_TIP_REVIEW", group["source_risk_flags"])
        self.assertIn("HISTORICAL_FOLDER_OPEN_TASK", group["source_risk_flags"])
        self.assertEqual(planner.plan(census)["summary"]["retirement_actions_authorized"], 0)

    def test_superseded_head_note_does_not_claim_merged(self):
        census = fixture()
        census["head_groups"][1]["sha"] = "b546c1a69ff8fb0c1602425bf1a8b11664de98ae"
        group = planner.plan(census)["groups"][1]
        self.assertIn("#175", group["historical_note_not_approval"])
        self.assertEqual(group["classification"], "UNIQUE_TIP_RETAIN")

    def test_rejects_invalid_census_and_conflicting_refs(self):
        changes = [
            (lambda x: x.update(schema_version="trek-branch-census-v1"), "collision-safe"),
            (lambda x: x["ref_layout"].update(branch_root="refs/remotes/origin"), "disjoint"),
            (lambda x: x.update(base_ref="refs/remotes/origin/main"), "main base ref"),
            (lambda x: x.update(base_sha="fake"), "main SHA"),
            (lambda x: x["head_groups"][1].update(sha="b" * 40), "tip SHA appears"),
            (lambda x: x["head_groups"][1]["branches"].__setitem__(0, "research/tng"),
             "same branch name"),
            (lambda x: x["head_groups"][0].update(branch_count=3), "branch count"),
            (lambda x: x["head_groups"][0].update(branch_count=True), "branch count"),
            (lambda x: x["head_groups"][0].update(tree_sha="junk"), "branch tip/tree"),
            (lambda x: x["head_groups"][0].update(contains_folder_open_task="no"), "editor task"),
            (lambda x: x["head_groups"][0].update(branch_only_commits=-1), "divergence"),
            (lambda x: x["head_groups"][0]["branches"].__setitem__(1, "main"), "reserved"),
            (lambda x: x["head_groups"][0]["branches"].__setitem__(1, "evil\nref"), "unsafe"),
            (lambda x: x["head_groups"][0]["branches"].__setitem__(1, "evil.lock"), "unsafe"),
            (lambda x: x["summary"].update(non_main_branches=999), "summary"),
            (lambda x: x["pr_head_refs"].append({"number": "82", "sha": "f" * 40}),
             "duplicate PR"),
            (lambda x: x["pr_head_refs"][0].update(number="refs/heads/82"), "malformed PR"),
            (lambda x: x["summary"].update(accessible_pr_head_refs=10), "snapshot count"),
        ]
        for edit, message in changes:
            with self.subTest(message=message):
                census = copy.deepcopy(fixture())
                edit(census)
                with self.assertRaisesRegex(planner.Rejected, message):
                    planner.plan(census)

    def test_branch_name_validation_rejects_git_specials(self):
        for name in ["", "@", "-x", ".hidden", "abc/", "a//b", "a..b", "a@{b", "a.lock",
                     "hi\tthere", "has space", "a:b", "a\\b", "a^b", "a?b",
                     "a\ud800b", "a\u202eb", "a\u200bb", "a\u200db",
                     "a\u2060b", "a\u00a0b", "a\u2028b", "a\u2007b",
                     "a\u0590b", "a\u05d0b", "a\u0627b"]:
            with self.subTest(name=name):
                self.assertFalse(planner.valid_branch(name))
        self.assertTrue(planner.valid_branch("pr/82"))
        self.assertTrue(planner.valid_branch("research/tng/season-1"))
        self.assertTrue(planner.valid_branch("research/caf\u00e9"))

    def test_invisible_branch_name_is_rejected_in_census(self):
        census = fixture()
        census["head_groups"][0]["branches"][0] = "research/\u200bhidden"
        with self.assertRaisesRegex(planner.Rejected, "unsafe or reserved"):
            planner.plan(census)

    def test_pr_numbers_are_bounded_before_numeric_sort(self):
        census = fixture()
        census["pr_head_refs"][0]["number"] = "9" * planner.MAX_PR_NUMBER_DIGITS
        self.assertEqual(planner.plan(census)["summary"]["pr_head_snapshot_refs"], 2)
        census["pr_head_refs"][0]["number"] = "9" * 5000
        with self.assertRaisesRegex(planner.Rejected, "malformed PR head ref"):
            planner.plan(census)


class InspectOnlyTests(unittest.TestCase):
    def test_git_is_read_only_and_disables_lazy_fetch_and_replacements(self):
        verified = SimpleNamespace(returncode=0, stdout=b"d" * 40 + b"\n")
        paths = SimpleNamespace(returncode=0, stdout=(
            b".vscode/tasks.json\0public/fonts/pixel.woff2\0research/title with\nnewline.json\0"))
        with mock.patch.object(planner.subprocess, "run", side_effect=[verified, paths]) as call:
            inspection = planner.inspect_tree(Path("/audit-clone"), "a" * 40, "d" * 40)
        self.assertEqual(inspection["status"], "PATHS_INSPECTED")
        self.assertEqual(inspection["tree_identity"], "VERIFIED")
        self.assertEqual(inspection["paths"], [".vscode/tasks.json", "public/fonts/"])
        self.assertEqual(call.call_count, 2)
        self.assertEqual(call.call_args_list[0].args[0], [
            "git", "-C", "/audit-clone", "rev-parse", "--verify", "--end-of-options",
            "a" * 40 + "^{tree}"])
        self.assertEqual(call.call_args_list[1].args[0], [
            "git", "-C", "/audit-clone", "ls-tree", "-r", "--name-only", "-z", "a" * 40])
        for invocation in call.call_args_list:
            env = invocation.kwargs["env"]
            self.assertEqual(env["GIT_NO_LAZY_FETCH"], "1")
            self.assertEqual(env["GIT_OPTIONAL_LOCKS"], "0")
            self.assertEqual(env["GIT_NO_REPLACE_OBJECTS"], "1")
            self.assertEqual(invocation.kwargs["timeout"], 20)

    def test_missing_broken_or_too_large_object_is_never_silent_success(self):
        responses = [
            SimpleNamespace(returncode=128, stdout=b""),
            SimpleNamespace(returncode=0, stdout=b"unterminated"),
            SimpleNamespace(returncode=0, stdout=b"x" * 2_000_001),
        ]
        for response in responses:
            with self.subTest(response=response.returncode):
                with mock.patch.object(planner.subprocess, "run", side_effect=[
                        SimpleNamespace(returncode=0, stdout=b"d" * 40 + b"\n"), response]):
                    result = planner.inspect_tree(Path("/audit"), "a" * 40, "d" * 40)
                    self.assertEqual(result["status"], "OBJECT_UNAVAILABLE")
                    self.assertEqual(result["tree_identity"], "VERIFIED")
        with mock.patch.object(planner.subprocess, "run", return_value=responses[0]) as call:
            result = planner.inspect_tree(Path("/audit"), "a" * 40, "d" * 40)
            self.assertEqual(result["status"], "OBJECT_UNAVAILABLE")
            self.assertEqual(result["tree_identity"], "NOT_VERIFIED")
            self.assertEqual(call.call_count, 1)
        with mock.patch.object(planner.subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 20)):
            self.assertEqual(planner.inspect_tree(Path("/audit"), "a" * 40, "d" * 40)["status"],
                             "OBJECT_UNAVAILABLE")

    def test_mismatched_claim_never_triggers_path_inspection(self):
        with mock.patch.object(planner.subprocess, "run", return_value=SimpleNamespace(
                returncode=0, stdout=b"f" * 40 + b"\n")) as call:
            with self.assertRaisesRegex(planner.Rejected, "tree SHA mismatch"):
                planner.inspect_tree(Path("/audit"), "a" * 40, "d" * 40)
            self.assertEqual(call.call_count, 1)

    def test_path_checks_influence_group_but_no_retirement_authorized(self):
        def response(command, **_kwargs):
            if command[3] == "rev-parse":
                tree_sha = b"d" if command[-1].startswith("b" * 40) else b"e"
                return SimpleNamespace(returncode=0, stdout=tree_sha * 40 + b"\n")
            return SimpleNamespace(returncode=0, stdout=b".vscode/tasks.json\0public/fonts/logo.ttf\0")

        with mock.patch.object(planner.subprocess, "run", side_effect=response):
            result = planner.plan(fixture(), audit_repo=Path("/audit"))
        for group in result["groups"]:
            self.assertEqual(group["tree_identity_verification"], "VERIFIED")
            self.assertIn("EDITOR_TASK_PATH_PRESENT", group["source_risk_flags"])
            self.assertIn("HISTORICAL_PUBLIC_FONTS_PATH", group["source_risk_flags"])
            self.assertEqual(group["classification"], "HISTORICAL_HAZARD_HOLD")
        self.assertEqual(result["summary"]["retirement_actions_authorized"], 0)

    def test_real_git_commit_tree_matches_only_its_actual_tree_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "audit"
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            task = repo / ".vscode" / "tasks.json"
            task.parent.mkdir()
            task.write_text('{"tasks":[]}', encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", ".vscode/tasks.json"], check=True)
            subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test",
                            "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false",
                            "commit", "-qm", "test object"], check=True)

            def git_sha(argument):
                return subprocess.check_output(["git", "-C", str(repo), "rev-parse", argument],
                                               text=True).strip()

            tip_sha, tree_sha = git_sha("HEAD"), git_sha("HEAD^{tree}")
            census = fixture()
            census["head_groups"][0]["sha"] = tip_sha
            census["head_groups"][0]["tree_sha"] = tree_sha
            inspected = planner.plan(census, audit_repo=repo)["groups"][0]
            self.assertEqual(inspected["tree_identity_verification"], "VERIFIED")
            self.assertEqual(inspected["historical_path_inspection"], "PATHS_INSPECTED")
            self.assertTrue(inspected["recoverability"]["tree_read_from_local_audit_objects"])
            self.assertIn("EDITOR_TASK_PATH_PRESENT", inspected["source_risk_flags"])

            census["head_groups"][0]["tree_sha"] = "0" * 40
            with self.assertRaisesRegex(planner.Rejected, "tree SHA mismatch"):
                planner.plan(census, audit_repo=repo)


class SafeInputAndCliTests(unittest.TestCase):
    def test_json_input_rejects_duplicate_keys_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "census.json"
            original.write_text('{"x":1,"x":2}', encoding="utf-8")
            with self.assertRaisesRegex(planner.Rejected, "duplicate JSON key"):
                planner.read_json(original)
            link = Path(tmp) / "alias.json"
            link.symlink_to(original)
            with self.assertRaisesRegex(planner.Rejected, "non-symlink"):
                planner.read_json(link)

    def test_census_size_is_bounded_and_non_json_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "census.json"
            path.write_bytes(b"{" + b" " * planner.MAX_CENSUS_BYTES)
            with self.assertRaisesRegex(planner.Rejected, "byte limit"):
                planner.read_json(path)
            path.write_bytes(b"\xff")
            with self.assertRaisesRegex(planner.Rejected, "UTF-8 JSON"):
                planner.read_json(path)
            path.write_bytes(b'{"not_json":NaN}')
            with self.assertRaisesRegex(planner.Rejected, "non-JSON numeric"):
                planner.read_json(path)

    def test_deeply_nested_json_is_rejected_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested.json"
            census = fixture()
            census["annotation"] = ('\\"[[{{' * 2000) + "not nesting"
            path.write_text(json.dumps(census), encoding="utf-8")
            self.assertEqual(planner.read_json(path)["schema_version"], "trek-branch-census-v2")
            path.write_bytes(b'{"x":' + b"[" * 5000 + b"0" + b"]" * 5000 + b"}")
            with self.assertRaisesRegex(planner.Rejected, "nesting exceeds safe limit"):
                planner.read_json(path)
            command = [os.environ.get("PYTHON", "python3"), str(SCRIPT), "--census", str(path)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("RETIREMENT_PLAN_REJECTED", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_overlong_pr_number_is_rejected_by_cli_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "huge-pr.json"
            census = fixture()
            census["pr_head_refs"][0]["number"] = "9" * 5000
            path.write_text(json.dumps(census), encoding="utf-8")
            command = [os.environ.get("PYTHON", "python3"), str(SCRIPT), "--census", str(path)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("malformed PR head ref", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_cli_repeated_offline_dry_runs_are_identical_and_do_not_touch_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "census.json"
            path.write_text(json.dumps(fixture()), encoding="utf-8")
            original = path.read_bytes()
            command = [os.environ.get("PYTHON", "python3"), str(SCRIPT), "--census", str(path)]
            first = subprocess.run(command, capture_output=True, check=True, text=True)
            second = subprocess.run(command, capture_output=True, check=True, text=True)
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(json.loads(first.stdout)["summary"]["retirement_actions_authorized"], 0)
            self.assertEqual(list(Path(tmp).iterdir()), [path])


if __name__ == "__main__":
    unittest.main()
