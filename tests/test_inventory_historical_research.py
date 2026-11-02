"""Safety and determinism tests for untrusted historical PR-tree inventory."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "inventory_historical_research", ROOT / "tools" / "inventory_historical_research.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

MAIN = "a" * 40
ONE = "1" * 40
TWO = "2" * 40
THREE = "3" * 40


def tree(*entries: tuple[str, str, str, str]) -> bytes:
    return b"".join(
        f"{mode} {kind} {sha}\t{path}".encode("utf-8") + b"\x00"
        for mode, kind, sha, path in entries
    )


class InventoryTest(unittest.TestCase):
    def test_root_research_readme_is_documentation_not_a_lane_record(self):
        snapshot = tree(
            ("100644", "blob", ONE, "research/README.md"),
            ("100644", "blob", TWO, "research/tng/batches/s01/manifest.json"),
        )
        self.assertEqual(
            MODULE.parse_research_tree(snapshot),
            [("research/tng/batches/s01/manifest.json", "100644", "blob", TWO)],
        )
        report = MODULE.inventory(
            MAIN,
            tree(("100644", "blob", ONE, "research/README.md")),
            [("17", THREE, snapshot)],
        )
        self.assertEqual(report["summary"]["research_paths"], 1)
        self.assertEqual(report["paths"][0]["path"], "research/tng/batches/s01/manifest.json")
        self.assertEqual(report["acceptance_effect"], "NONE")

    def test_root_research_exception_does_not_hide_unsafe_or_unknown_entries(self):
        for entry in (
            ("120000", "blob", ONE, "research/README.md"),
            ("100755", "blob", ONE, "research/README.md"),
            ("160000", "commit", ONE, "research/README.md"),
            ("100644", "blob", ONE, "research/README.json"),
            ("100644", "blob", ONE, "research/other.md"),
            ("100644", "blob", ONE, "research/"),
            ("100644", "blob", ONE, "research/./README.md"),
        ):
            with self.subTest(entry=entry), self.assertRaises(MODULE.InventoryError):
                MODULE.parse_research_tree(tree(entry))

    def test_deduplicates_same_blob_but_keeps_contested_proposals(self):
        original = tree(
            ("100644", "blob", ONE, "research/tos/episode.json"),
            ("100644", "blob", TWO, "research/ds9/batch.json"),
            ("100644", "blob", THREE, "README.md"),
        )
        revised = tree(
            ("100644", "blob", ONE, "research/tos/episode.json"),
            ("100644", "blob", THREE, "research/ds9/batch.json"),
        )
        prs = [("17", TWO, revised), ("2", ONE, original)]
        report = MODULE.inventory(MAIN, tree(("100644", "blob", ONE, "research/tos/episode.json")), prs)
        self.assertEqual(report["summary"]["research_paths"], 2)
        self.assertEqual(report["summary"]["unique_path_object_variants"], 3)
        self.assertEqual(report["summary"]["contested_paths"], 1)
        self.assertEqual(report["pr_head_refs"][0]["number"], "2")
        tos, ds9 = (next(p for p in report["paths"] if p["path"] == name) for name in
                    ("research/tos/episode.json", "research/ds9/batch.json"))
        self.assertEqual(tos["versions"][0]["pr_heads"], ["2", "17"])
        self.assertTrue(tos["versions"][0]["same_bytes_on_main"])
        self.assertTrue(ds9["has_conflicting_versions"])
        self.assertTrue(all(not v["same_bytes_on_main"] for v in ds9["versions"]))
        self.assertEqual(report["admission_effect"], "NONE")
        self.assertEqual(report["coverage_effect"], "NONE")
        self.assertEqual(report["denominator_effect"], "NONE")
        self.assertEqual(report["data_status"], "UNTRUSTED_HISTORICAL_PROPOSALS")

    def test_deterministic_even_if_snapshot_order_changes(self):
        one = ("4", ONE, tree(("100644", "blob", TWO, "research/tos/x.json")))
        two = ("9", TWO, tree(("100644", "blob", THREE, "research/tos/x.json")))
        a = MODULE.inventory(MAIN, b"", [one, two])
        b = MODULE.inventory(MAIN, b"", [two, one])
        self.assertEqual(a, b)
        receipt = a.pop("manifest_sha256")
        payload = json.dumps(a, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        import hashlib
        self.assertEqual(receipt, hashlib.sha256(payload.encode()).hexdigest())

    def test_never_follows_or_admits_symlinks_gitlinks_or_executable_modes(self):
        historical = tree(
            ("120000", "blob", ONE, "research/tos/symlink"),
            ("160000", "commit", TWO, "research/tos/nested-repo"),
            ("100755", "blob", THREE, "research/tos/program.sh"),
        )
        report = MODULE.inventory(MAIN, b"", [("8", ONE, historical)])
        self.assertEqual(report["summary"]["unsafe_object_variants"], 3)
        self.assertTrue(all(v["unsafe_object_mode"] for p in report["paths"] for v in p["versions"]))
        self.assertTrue(all(p["admission"] == "NONE" for p in report["paths"]))

    def test_rejects_ambiguous_refs(self):
        listing = f"{MODULE.PR_REF_ROOT}7\t{ONE}\n".encode()
        self.assertEqual(MODULE.parse_refs(listing), [("7", ONE)])
        for invalid in (
            f"{MODULE.PR_REF_ROOT}007\t{ONE}\n",
            f"refs/remotes/origin/pr/7\t{ONE}\n",
            f"{MODULE.PR_REF_ROOT}7\t{ONE}\n{MODULE.PR_REF_ROOT}7\t{TWO}\n",
        ):
            with self.subTest(invalid=invalid), self.assertRaises(MODULE.InventoryError):
                MODULE.parse_refs(invalid.encode())

    def test_rejects_malformed_paths_and_non_utf8(self):
        for historical in (
            tree(("100644", "blob", ONE, "research/tos/../escape.json")),
            tree(("100644", "blob", ONE, "research//bad.json")),
            b"100644 blob " + ONE.encode() + b"\tresearch/tos/\xff\x00",
        ):
            with self.subTest(raw=historical), self.assertRaises(MODULE.InventoryError):
                MODULE.parse_research_tree(historical)

    def test_collect_is_read_only_and_requires_pinned_main(self):
        raw_refs = f"{MODULE.PR_REF_ROOT}12\t{TWO}\n".encode()
        calls = []

        def fake_git(_repo, *args):
            calls.append(args)
            if args[0] == "rev-parse":
                return MAIN.encode() + b"\n"
            if args[0] == "for-each-ref":
                return raw_refs
            if args[0] == "ls-tree":
                return tree(("100644", "blob", ONE, "research/tng/pilot.json"))
            raise AssertionError(f"Unexpected Git command: {args}")

        with patch.object(MODULE, "git_read", fake_git):
            result = MODULE.collect(Path("/tmp/disposable-audit-clone"), MAIN)
            self.assertEqual(result["summary"]["research_paths"], 1)
            with self.assertRaisesRegex(MODULE.InventoryError, "main moved"):
                MODULE.collect(Path("/tmp/disposable-audit-clone"), THREE)
        self.assertEqual(sum(args[0] == "ls-tree" for args in calls), 2)
        self.assertFalse(any(args[0] in ("fetch", "checkout", "update-ref", "reset") for args in calls))


if __name__ == "__main__":
    unittest.main()
