"""Offline checks for the read-only branch census helper."""

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "audit_git_topology.py"
SPEC = importlib.util.spec_from_file_location("audit_git_topology", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class RefParsingTests(unittest.TestCase):
    def test_drops_symbolic_origin_head_and_keeps_exact_shas(self):
        refs = audit.parse_ref_lines(
            "origin/main\tabc\norigin/HEAD\tabc\norigin/research/tng\tdef\n",
            "origin/",
        )
        self.assertEqual(refs, [("main", "abc"), ("research/tng", "def")])

    def test_does_not_treat_pr_namespace_as_a_branch(self):
        refs = audit.parse_ref_lines(
            "origin/pr/82\t123\norigin/main\t456\n", "origin/pr/"
        )
        self.assertEqual(refs, [("82", "123")])

    def test_pr_head_filter_for_branch_census(self):
        refs = audit.parse_ref_lines(
            "origin/pr/82\t123\norigin/main\t456\norigin/research/tng\t789\n",
            "origin/",
        )
        branch_refs = [(name, sha) for name, sha in refs if not name.startswith("pr/")]
        self.assertEqual(branch_refs, [("main", "456"), ("research/tng", "789")])

    def test_legacy_task_is_only_a_source_inspection_signal(self):
        self.assertTrue(audit.has_folder_open_task('{"runOn":"folderOpen"}'))
        self.assertFalse(audit.has_folder_open_task('{"tasks": []}'))
        self.assertFalse(audit.has_folder_open_task(None))

    def test_tree_parser_uses_blob_hash_and_exact_path(self):
        sha = "a" * 40
        raw = f"100644 blob {sha}\tresearch/tng/a.json\n040000 tree {'b'*40}\tresearch\n"
        self.assertEqual(audit.parse_blob_tree(raw), [("research/tng/a.json", sha)])

    def test_non_numeric_pr_snapshot_ref_is_rejected_before_counting(self):
        raw = "refs/trek-audit/pr-heads/surprise\t" + "a" * 40 + "\n"
        with self.assertRaisesRegex(ValueError, "must be numeric"):
            audit.parse_pr_snapshots(raw, "refs/trek-audit/pr-heads/")

    def test_ref_layouts_are_disjoint_and_legacy_is_explicit(self):
        branches, prs, base = audit.ref_layout(False)
        self.assertEqual(branches, "refs/trek-audit/branch-heads")
        self.assertEqual(prs, "refs/trek-audit/pr-heads")
        self.assertEqual(base, "refs/trek-audit/branch-heads/main")
        self.assertFalse(prs.startswith(branches + "/"))
        self.assertEqual(audit.ref_layout(True), (
            "refs/remotes/origin", "refs/remotes/origin/pr", "refs/remotes/origin/main"
        ))

    def test_real_pr_named_branch_is_counted_separately_from_pr_snapshot(self):
        base_sha, branch_sha, pr_sha = (c * 40 for c in "abc")

        def fake_git(repo, *args, allow_missing=False):
            if args[0] == "rev-parse" and args[1] == "--verify":
                return base_sha
            if args[0] == "for-each-ref":
                if args[-1] == audit.AUDIT_BRANCH_ROOT:
                    return (f"{audit.AUDIT_BRANCH_ROOT}/main\t{base_sha}\n"
                            f"{audit.AUDIT_BRANCH_ROOT}/pr/82\t{branch_sha}\n")
                if args[-1] == audit.AUDIT_PR_ROOT:
                    return f"{audit.AUDIT_PR_ROOT}/82\t{pr_sha}\n"
            if args[0] == "rev-list":
                return "1\t1"
            if args[0] == "show":
                return None
            if args[0] == "rev-parse":
                return "d" * 40
            if args[0] == "ls-tree":
                return "100644 blob " + "e" * 40 + "\tresearch/tng/sample.json\n"
            raise AssertionError(f"Unexpected Git read: {args}")

        with mock.patch.object(audit, "git", side_effect=fake_git):
            result = audit.census(Path("/unused"))
        self.assertEqual(result["schema_version"], "trek-branch-census-v2")
        self.assertEqual(result["summary"]["total_branches_including_main"], 2)
        self.assertEqual(result["summary"]["accessible_pr_head_refs"], 1)
        self.assertEqual(result["summary"]["by_family"], {"pr": 1})
        self.assertEqual(result["head_groups"][0]["branches"], ["pr/82"])
        self.assertEqual(result["pr_head_refs"], [{"number": "82", "sha": pr_sha}])

    def test_legacy_mode_preserves_prior_origin_pr_exclusion(self):
        root, pr_root, _ = audit.ref_layout(True)
        raw = f"{root}/main\t{'a'*40}\n{pr_root}/82\t{'b'*40}\n"
        refs = audit.parse_ref_lines(raw, root + "/")
        legacy_branches = [name for name, _ in refs if not name.startswith("pr/")]
        self.assertEqual(legacy_branches, ["main"])

    def test_git_inspection_disables_promisor_lazy_fetch(self):
        result = SimpleNamespace(returncode=0, stdout="sha\n", stderr="")
        with mock.patch.object(audit.subprocess, "run", return_value=result) as call:
            self.assertEqual(audit.git(Path("/audit"), "rev-parse", "HEAD"), "sha")
        self.assertEqual(call.call_args.kwargs["env"]["GIT_NO_LAZY_FETCH"], "1")
        self.assertEqual(call.call_args.kwargs["timeout"], 30)


if __name__ == "__main__":
    unittest.main()
