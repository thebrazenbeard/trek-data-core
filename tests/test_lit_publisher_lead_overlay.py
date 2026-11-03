"""Fail-closed tests for the *separate* three-edition publisher candidate index."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("trek_lit_overlay_builder", "tools/build_lit_publisher_leads.py")
sys.path.insert(0, str(ROOT / "tools"))
query_module = load_module("trek_lit_overlay_query", "tools/query_lit_publisher_leads.py")


class LiteraryPublisherOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / builder.INPUT).read_text(encoding="utf-8"))
        cls.artifact = json.loads((ROOT / builder.OUTPUT).read_text(encoding="utf-8"))

    def test_exact_pinned_source_projection_and_separate_denominator(self):
        self.assertEqual(builder.encode(builder.build()), (ROOT / builder.OUTPUT).read_bytes())
        self.assertEqual(query_module.validate(self.artifact, sources=True), self.artifact["rows"])
        self.assertEqual(self.artifact["row_count"], 3)
        self.assertEqual(self.artifact["denominator_effect"], "NONE")
        self.assertEqual(json.loads((ROOT / "explorer/discovery-catalog.json").read_text())["row_count"], 1214)

    def test_source_only_private_bytes_and_unreviewed_synopsis_not_published(self):
        public = (ROOT / builder.OUTPUT).read_text(encoding="utf-8")
        self.assertNotIn("private_archive", public)
        self.assertNotIn("original_publisher_description_paraphrase", public)
        self.assertNotIn("owner-private-books", public)
        self.assertNotIn("C:\\\\Users", public)
        for row in self.artifact["rows"]:
            self.assertEqual(row["coverage_effect"], "NONE")
            self.assertEqual(row["admission_effect"], "NONE")
            self.assertEqual(row["synopsis_status"], "UNREVIEWED_PARAPHRASE_HELD_NOT_PUBLIC")
            self.assertEqual(row["identity_scope"], "EDITION_CANDIDATE_SOURCE_LOCAL")
            self.assertTrue(all(tag.startswith(("medium:", "kind:", "format:", "publisher-claim:"))
                                for tag in row["query_tags"]))

    def test_callable_queries_keep_publisher_claim_tags_scoped(self):
        rows = query_module.validate(self.artifact)
        mccoy = query_module.query(rows, q="McCoy", tags=("publisher-claim:character:leonard-mccoy",))
        self.assertEqual(mccoy["total_matches"], 1)
        self.assertEqual(mccoy["rows"][0]["isbn13"], "9780743546744")
        self.assertEqual(query_module.query(rows, isbn="9780743419987")["total_matches"], 1)
        self.assertEqual(query_module.query(rows, tags=("canon:prime",))["total_matches"], 0)
        self.assertEqual(query_module.query(rows, offset=2, limit=1)["next_offset"], None)
        self.assertEqual(query_module.query(rows, offset=1, limit=1)["next_offset"], 2)

    def test_in_memory_source_adversaries_hit_semantic_guards(self):
        # Critically, mutated fixtures are evaluated *after* semantic checks;
        # no stale whole-file digest short-circuits this test.
        def reject(mutate):
            source = copy.deepcopy(self.source)
            mutate(source)
            with self.assertRaises(ValueError):
                builder.verify_source(source)

        reject(lambda s: s.update(coverage_effect="AUDITED"))
        reject(lambda s: s.update(public_synopsis_effect="RELEASED"))
        reject(lambda s: s["candidates"][0].update(private_archive_edition_identity="VERIFIED"))
        reject(lambda s: s["candidates"][1].update(publisher_url="https://attacker.invalid/book/9780743546744"))
        reject(lambda s: s["candidates"][1]["source_relative_query_tags"].append("canon:prime"))
        reject(lambda s: s["candidates"][0].update(publisher_title="Kobayashi\u202e Maru"))
        reject(lambda s: s["candidates"][0].update(publisher_isbn13="9780743419988"))
        reject(lambda s: s["candidates"].append(s["candidates"][0]))

    def test_downloaded_index_adversaries_rejected(self):
        def reject(mutate):
            data = copy.deepcopy(self.artifact)
            mutate(data)
            with self.assertRaises(ValueError):
                query_module.validate(data)

        reject(lambda d: d.update(coverage_effect="YES"))
        reject(lambda d: d["rows"][0].update(synopsis_status="PUBLISHED"))
        reject(lambda d: d["rows"][0].update(source_locator="https://malicious.invalid/"))
        reject(lambda d: d["rows"][0]["query_tags"].append("canon:prime"))
        reject(lambda d: d["rows"][0].update(private_edition_equivalence="VERIFIED"))
        reject(lambda d: d["rows"][0].update(title="Forged Canonical Book"))
        reject(lambda d: d["rows"][0].update(edition_format="HARDCOVER"))
        reject(lambda d: d.update(source_input_sha256="0" * 64))

    def test_invalid_source_bytes_do_not_rebuild(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / builder.INPUT
            path.parent.mkdir(parents=True)
            path.write_bytes((ROOT / builder.INPUT).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "accepted SHA-256"):
                builder.build(root)

    def test_cli_exact_source_and_reproducible_check(self):
        commands = (
            [sys.executable, "tools/build_lit_publisher_leads.py", "--check"],
            [sys.executable, "tools/query_lit_publisher_leads.py", "--validate-sources", "--isbn", "9780743419987"],
        )
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
