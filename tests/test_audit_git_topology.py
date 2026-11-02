"""Offline checks for the read-only branch census helper."""

import importlib.util
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
