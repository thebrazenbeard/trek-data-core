"""Adversarial regression checks for owner-private S.C.E. #36 HELD packet."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from proposals.research.sce36_private_complete_read_20261105.validate import DATA, validate
from proposals.research.sce36_private_complete_read_20261105.verify_owner_archive import scan_chapters, verify_archive


class SCE36PrivateHeldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(DATA.read_text(encoding="utf-8"))

    def _reject(self, scope, key, value):
        packet = copy.deepcopy(self.packet)
        scope(packet)[key] = value
        with self.assertRaises(ValueError):
            validate(packet)

    def test_complete_fourteen_chapters_and_zero_admissions(self):
        self.assertEqual((1, 1, 15, 14, 14), validate(self.packet))
        self.assertEqual("HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED", self.packet["status"])
        self.assertFalse(self.packet["private_source_manifestation_authenticated"])
        for key in ("accepted_work_effect", "accepted_source_binding_effect", "accepted_evidence_effect",
                    "accepted_close_read_effect", "coverage_effect", "public_explorer_effect",
                    "cross_work_reconciliation_effect"):
            with self.subTest(key=key):
                self._reject(lambda p: p, key, "ADDED")

    def test_narrative_boundary_excludes_authors_and_advertising(self):
        chapters = self.packet["chapter_spans"]
        self.assertEqual(list(range(1, 15)), [x["number"] for x in chapters])
        self.assertEqual(7427, chapters[0]["byte_start_inclusive"])
        self.assertEqual(16829, chapters[1]["byte_start_inclusive"])
        self.assertEqual(166413, chapters[-1]["byte_end_exclusive"])
        self.assertEqual(14, self.packet["source"]["opf_chaptertour_entries"])
        self.assertFalse(self.packet["source"]["following_about_authors_and_promo_read_as_novel"])
        self._reject(lambda p: p["chapter_spans"][-1], "byte_end_exclusive", 170292)
        self._reject(lambda p: p["chapter_spans"][0], "byte_start_inclusive", 7448)
        self._reject(lambda p: p["source"], "opf_chaptertour_entries", 15)
        self._reject(lambda p: p["source"], "following_about_authors_and_promo_read_as_novel", True)

    def test_hashes_source_and_edition_frozen_not_accepted(self):
        source = self.packet["source"]
        self.assertEqual("opf-local:0047", source["opf_inventory_id"])
        self.assertEqual("0-7434-7610-7", source["raw_opf_work_isbn10_literal"])
        self.assertEqual("0-9673008-1-9", source["raw_opf_converter_header_isbn10_literal"])
        self.assertEqual("9780743476102", self.packet["publisher"]["isbn13"])
        self.assertEqual("CREATOR_DISPLAY_VARIANT_UNRESOLVED", source["creator_crosswalk_state"])
        self.assertEqual("ISBN_CHECKSUM_ALIGNMENT_ONLY", source["publisher_edition_crosswalk_state"])
        for key, bad in (("archive_sha256", "0" * 64), ("html_sha256", "0" * 64),
                         ("original_lit_member_sha256", "0" * 64),
                         ("creator_crosswalk_state", "SAME_PERSON_VERIFIED"),
                         ("publisher_edition_crosswalk_state", "PUBLISHER_EDITION_AUTHENTICATED"),
                         ("conversion_link_independently_reproduced", True),
                         ("ebook_access_rights_verified_for_public_ingestion", True)):
            with self.subTest(key=key):
                self._reject(lambda p: p["source"], key, bad)

    def test_identity_is_local_and_attached_evidence_is_chapter_relative(self):
        self.assertTrue(all(e["identity_scope"] == "THIS_SOURCE_ONLY" for e in self.packet["local_entities"]))
        self.assertEqual(list(range(1, 15)), [e["chapter"] for e in self.packet["evidence"]])
        self._reject(lambda p: p["local_entities"][0], "identity_scope", "GLOBAL")
        self._reject(lambda p: p["evidence"][2], "chapter", 8)
        self._reject(lambda p: p["assertions"][0], "evidence_refs", ["sce35:e07"])
        self._reject(lambda p: p["assertions"][0], "subject", "global:resauria")

    def test_epistemic_falsifiers_prohibit_overclaim(self):
        assertions = {a["predicate"]: a for a in self.packet["assertions"]}
        self.assertEqual("OPTICAL_EXPLANATION_NOT_DUPLICATE_IDENTITY",
                         assertions["SECOND_SHIP_SEEN_NEAR_BLACK_HOLE"]["status"])
        self.assertEqual("NON_PROPHETIC_CHARACTER_EXPERIENCE",
                         assertions["DREAM_PROPHECY_OR_GRANDDAUGHTER_HARM"]["status"])
        self.assertEqual("MIXED_DEPICTED_ACT_AND_REVISED_INFERENCE",
                         assertions["TRACTOR_INTERFERENCE_AGENT_AND_MOTIVE"]["status"])
        self.assertEqual("DEPICTED_IN_BOOK_TWO_SOURCE_SCOPE_ONLY",
                         assertions["MULTIVESSEL_EXTRACTION_OUTCOME"]["status"])
        self._reject(lambda p: p["assertions"][2], "status", "SECOND_SHIP_PROVEN")
        self._reject(lambda p: p["assertions"][5], "status", "PREMONITION_VERIFIED")
        self._reject(lambda p: p["assertions"][3], "status", "SCE35_AND_SCE36_GLOBAL_IDENTITY_LINKED")

    def test_no_copyrighted_prose_field(self):
        self._reject(lambda p: p, "copyrighted_book_text_exported", True)
        self._reject(lambda p: p["evidence"][0], "full_text", "forbidden")
        self._reject(lambda p: p["chapter_spans"][0], "quote", "forbidden")

    def test_archive_scanner_requires_all_narrative_chapters_and_backmatter_boundary(self):
        prefix = b'<html><body>prologue structural wrapper\n'
        html = prefix + b"".join(f'<div class="chapter" id="ch_{i}">chapter data {i}</div>'.encode()
                        for i in range(1, 15)) + b'<div class="backMatterPage">advertising</div>'
        spans = scan_chapters(html)
        self.assertEqual(14, len(spans))
        self.assertEqual(html.find(b'<div class="chapter" id="ch_1">'), spans[0][0])
        self.assertEqual(html.find(b'<div class="chapter" id="ch_2">'), spans[0][1])
        self.assertEqual(prefix.__len__(), spans[0][0])
        self.assertNotEqual(html.find(b'ch_1'), spans[0][0])
        self.assertEqual(html.find(b'<div class="backMatterPage">'), spans[-1][1])
        for bad in (html.replace(b'ch_14', b'ch_13'),
                    html.replace(b'ch_7', b'ch_17'),
                    html.replace(b'backMatterPage', b'chapter')):
            with self.assertRaises(ValueError):
                scan_chapters(bad)

    def test_verifier_refuses_non_owner_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                verify_archive(Path(tmp) / "Star_Trek_OPF_Converted.zip", self.packet)


if __name__ == "__main__":
    unittest.main()
