"""Adversarial tests for the publisher-edition discovery proposal."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools import build_literary_candidates as literature


ROOT = Path(__file__).resolve().parents[1]


class LiteraryPublisherProposalTests(unittest.TestCase):
    def setUp(self):
        self.proposal = literature.read(ROOT)

    def test_four_editions_are_one_proposed_work(self):
        result = literature.compile_records(self.proposal)
        self.assertEqual(result["work"]["work_id"], literature.WORK_ID)
        self.assertEqual(result["work"]["status"], "PROPOSED")
        self.assertEqual(len(result["edition_candidates"]), 4)
        self.assertEqual(len(result["sources"]), 4)
        self.assertEqual(len(result["bindings"]), 4)
        self.assertEqual({b["mapping_role"] for b in result["bindings"]}, {"METADATA_ONLY"})
        self.assertEqual({b["lifecycle"] for b in result["bindings"]}, {"PROPOSED"})
        self.assertEqual({b["work_id"] for b in result["bindings"]}, {literature.WORK_ID})
        self.assertEqual({s["independence_group"] for s in result["sources"]}, {literature.GROUP})
        self.assertTrue(all(s["content_hash"] is None for s in result["sources"]))
        self.assertEqual(result["accepted_work_effect"], "NONE")
        self.assertEqual(result["accepted_source_binding_effect"], "NONE")
        self.assertEqual(result["coverage_effect"], "NONE")
        self.assertNotIn("canonical_work_id", json.dumps(result))

    def test_isbn_checksum_not_just_length(self):
        self.assertTrue(literature.isbn13_valid("9781668095898"))
        self.assertFalse(literature.isbn13_valid("9781668095899"))
        self.assertFalse(literature.isbn13_valid(True))

    def test_duplicate_isbn_or_format_is_rejected(self):
        bad = copy.deepcopy(self.proposal)
        bad["editions"][1]["isbn13"] = bad["editions"][0]["isbn13"]
        with self.assertRaisesRegex(ValueError, "duplicate ISBN"):
            literature.compile_records(bad)
        bad = copy.deepcopy(self.proposal)
        bad["editions"][1]["format"] = bad["editions"][0]["format"]
        with self.assertRaisesRegex(ValueError, "duplicate product format"):
            literature.compile_records(bad)

    def test_unauthorized_locator_cannot_be_a_publisher_source(self):
        bad_urls = (
            "https://evil.example/books/not-allowed/9781668095898",
            "https://www.simonandschuster.com@evil.example/books/not-allowed/9781668095898",
            "http://www.simonandschuster.com/books/not-allowed/9781668095898",
            self.proposal["editions"][0]["locator"] + "?track=1",
            self.proposal["editions"][0]["locator"] + "#fragment",
            "https://www.simonandschuster.com/books/../private/9781668095898",
        )
        for url in bad_urls:
            with self.subTest(url=url):
                bad = copy.deepcopy(self.proposal)
                bad["editions"][0]["locator"] = url
                with self.assertRaisesRegex(ValueError, "publisher URL"):
                    literature.compile_records(bad)

    def test_work_identity_and_state_are_not_inferred_or_promoted(self):
        for field, value in (
            ("status", "ACCEPTED"),
            ("work_id", "canon-lit-ring-of-fire"),
            ("creator", "Unknown"),
            ("work_type", "TV_EPISODE"),
        ):
            with self.subTest(field=field):
                bad = copy.deepcopy(self.proposal)
                bad["work"][field] = value
                with self.assertRaisesRegex(ValueError, "Work must"):
                    literature.compile_records(bad)
        for name in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect"):
            bad = copy.deepcopy(self.proposal)
            bad[name] = "ACCEPTED"
            with self.assertRaisesRegex(ValueError, "may not modify"):
                literature.compile_records(bad)

    def test_unknown_fields_and_fabricated_evidence_are_rejected(self):
        for scope in ("root", "work", "edition"):
            bad = copy.deepcopy(self.proposal)
            item = bad if scope == "root" else bad["work"] if scope == "work" else bad["editions"][0]
            item["accepted_evidence"] = "claimed verified"
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                literature.compile_records(bad)

    def test_output_is_byte_deterministic_and_matches_committed_view(self):
        expected = literature.build(ROOT)
        self.assertEqual((ROOT / literature.OUTPUT).read_bytes(), expected)
        self.assertEqual(literature.main(["--repo-root", str(ROOT), "--check"]), 0)
        reordered = copy.deepcopy(self.proposal)
        reordered["editions"].reverse()
        self.assertEqual(literature.compile_records(self.proposal), literature.compile_records(reordered))

    def test_checks_detect_modified_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / literature.SOURCE
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps(self.proposal), encoding="utf-8")
            self.assertEqual(literature.main(["--repo-root", folder]), 0)
            self.assertEqual(literature.main(["--repo-root", folder, "--check"]), 0)
            (root / literature.OUTPUT).write_text("{}\n", encoding="utf-8")
            self.assertEqual(literature.main(["--repo-root", folder, "--check"]), 1)

    def test_source_and_output_symlink_directories_are_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            donor = root / "donor"
            donor.mkdir()
            (donor / "bundle.json").write_text(json.dumps(self.proposal), encoding="utf-8")
            partition = root / literature.SOURCE.parent
            partition.parent.mkdir(parents=True)
            partition.symlink_to(donor, target_is_directory=True)
            self.assertEqual(literature.main(["--repo-root", folder]), 1)
            self.assertFalse((donor / "records.json").exists())

    def test_malformed_json_and_duplicate_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / literature.SOURCE
            source.parent.mkdir(parents=True)
            source.write_text('{"proposal_only":true,"proposal_only":false}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON"):
                literature.read(root)


if __name__ == "__main__":
    unittest.main()
