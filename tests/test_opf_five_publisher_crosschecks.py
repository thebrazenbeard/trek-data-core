"""Adversarial five-source OPF ↔ direct-publisher edition metadata proposal tests."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("opf_publisher_five", ROOT / "tools/build_opf_five_publisher_crosschecks.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class PublisherFiveOPFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = builder.read_pinned(ROOT, builder.INPUT, builder.INPUT_SHA)
        cls.opf = builder.read_pinned(ROOT, builder.OPF, builder.OPF_SHA)
        cls.held = builder.read_pinned(ROOT, builder.HELD)
        cls.older_publisher = builder.read_pinned(ROOT, builder.OLDER_PUB, builder.OLDER_PUB_SHA)
        cls.result = builder.build(ROOT)

    def test_exact_pinned_five_row_projection_and_no_coverage(self):
        self.assertEqual(builder.encode(self.result), (ROOT / builder.OUTPUT).read_bytes())
        self.assertEqual(self.result["row_count"], 5)
        self.assertEqual(self.result["historic_directory_rows"], 1214)
        self.assertIsNone(self.result["distinct_work_count"])
        self.assertEqual(self.result["verified_private_edition_bindings"], 0)
        self.assertEqual(self.result["source_family_count"], 1)
        self.assertEqual(self.result["public_explorer_release"], "HELD")
        self.assertEqual(self.result["work_admission_effect"], "NONE")
        self.assertEqual(self.result["coverage_effect"], "NONE")
        self.assertEqual(self.result["artwork_release_effect"], "NONE")
        self.assertEqual(self.result["public_synopsis_effect"], "NONE")
        self.assertEqual([row["opf_source_local_id"] for row in self.result["rows"]], list(builder.IDS))

    def test_original_xml_receipts_and_publisher_edition_isbn_stay_separate(self):
        for record in self.result["rows"]:
            ident = record["opf_source_local_id"]
            self.assertEqual(record["opf_xml_uncompressed_bytes_read_only_rehashed"], builder.OPF_BYTES[ident])
            self.assertEqual(record["source_opf_zip_sha256"], builder.OPF_ZIP_SHA)
            self.assertEqual(record["publisher_ebook_isbn13"], builder.ISBN[ident])
            self.assertEqual(record["work_identity"], "NOT_RECONCILED")
            self.assertEqual(record["private_edition_equivalence"], "NOT_VERIFIED")
            self.assertFalse(record["publisher_page_archived"])
        self.assertEqual(self.source["owner_private_opf_archive_members_independently_rehashed"], True)
        self.assertEqual(self.source["publisher_raw_html_archived"], False)
        self.assertTrue(all(row["opf_isbn_candidates"] == [] for row in self.source["rows"]))

    def test_existing_final_reflection_publisher_observation_is_not_second_witness(self):
        existing = [row for row in self.result["rows"] if row["prior_same_family_publisher_candidate"]]
        self.assertEqual(len(existing), 1)
        self.assertEqual(existing[0]["opf_source_local_id"], "opf-local:0155")
        self.assertEqual(existing[0]["prior_same_family_publisher_candidate"],
                         "TOS-FINAL-REFLECTION-EBOOK-9780743419673")
        self.assertEqual(self.result["source_family_count"], 1)

    def test_semantic_forgeries_fail_even_if_source_hash_were_repinned(self):
        mutators = [
            lambda s: s.update(work_admission_effect="ADMITTED"),
            lambda s: s.update(publisher_source_independence="FIVE_INDEPENDENT_SOURCES"),
            lambda s: s.update(owner_private_opf_archive_members_independently_rehashed=False),
            lambda s: s["rows"][0].update(opf_entry_sha256="0" * 64),
            lambda s: s["rows"][0].update(opf_title_literal="Invented Trek title"),
            lambda s: s["rows"][0].update(publisher_title="Invented publisher listing"),
            lambda s: s["rows"][0].update(publisher_isbn13="9780743419506"),
            lambda s: s["rows"][0].update(publisher_url="https://attacker.invalid/books/a"),
            lambda s: s["rows"][0].update(publisher_product_date="2000-09-22"),
            lambda s: s["rows"][0].update(publisher_pages=999),
            lambda s: s["rows"][0].update(publisher_series_ordinal=99),
            lambda s: s["rows"][0].update(opf_entry_uncompressed_bytes=0),
            lambda s: s["rows"][1].update(existing_publisher_candidate_id=None),
            lambda s: s["rows"][4].update(existing_publisher_candidate_id="FORGED-ACCEPTED-CANDIDATE"),
            lambda s: s["rows"][2].update(edition_equivalence="VERIFIED"),
            lambda s: s["rows"][2].update(work_identity="RECONCILED"),
        ]
        for index, mutate in enumerate(mutators):
            changed = copy.deepcopy(self.source)
            mutate(changed)
            with self.subTest(index=index), self.assertRaises(ValueError):
                builder.verify_observations(changed, self.opf, self.held, self.older_publisher)

    def test_byte_receipt_and_historic_catalog_tampering_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = Path(temp)
            for path in (builder.INPUT, builder.OPF, builder.HELD, builder.OLDER_PUB, builder.BASE):
                dest = fake / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / path).read_bytes())
            (fake / builder.INPUT).write_bytes((fake / builder.INPUT).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "receipt changed"):
                builder.build(fake)
            (fake / builder.INPUT).write_bytes((ROOT / builder.INPUT).read_bytes())
            (fake / builder.BASE).write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError, "receipt changed"):
                builder.build(fake)

    def test_public_proposal_has_no_private_paths_or_copyrighted_media(self):
        raw = (ROOT / builder.OUTPUT).read_text(encoding="utf-8")
        for forbidden in ("OneDrive", "C:\\Users", "file://", "OverDriveGUID", "/mnt/c/",
                          "cloudfront.net", "cover.jpg", "Private_ZIP_Member_Path"):
            self.assertNotIn(forbidden, raw)
        self.assertEqual(hashlib.sha256((ROOT / builder.BASE).read_bytes()).hexdigest(), builder.BASE_SHA)
        self.assertEqual(hashlib.sha256((ROOT / builder.OPF).read_bytes()).hexdigest(), builder.OPF_SHA)


if __name__ == "__main__":
    unittest.main()
