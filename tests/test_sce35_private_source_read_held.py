"""Falsifiers for independent S.C.E. #35 owner-source read; no admission."""

import copy
import json
import unittest

from proposals.research.sce35_private_complete_read_20261104.validate import DATA, validate
from proposals.research.sce35_private_complete_read_20261104.verify_owner_archive import scan_chapters, verify_archive


class SCE35HeldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(DATA.read_text(encoding="utf-8"))

    def test_actual_complete_private_book_one_but_zero_admission(self):
        self.assertEqual((1, 1, 12, 13, 15), validate(self.packet))
        self.assertEqual("HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED", self.packet["status"])
        self.assertFalse(self.packet["private_source_manifestation_authenticated"])
        self.assertEqual("NONE", self.packet["accepted_close_read_effect"])

    def test_fifteen_chapters_stop_at_continuation_marker(self):
        spans = self.packet["chapter_spans"]
        self.assertEqual(list(range(1, 16)), [c["number"] for c in spans])
        self.assertEqual(166726, spans[-1]["byte_end_exclusive"])
        self.assertEqual(15, self.packet["source"]["opf_chaptertour_entries"])
        self.assertEqual(15, self.packet["source"]["html_narrative_chapter_anchors"])
        self.assertFalse(self.packet["source"]["following_book_two_read_as_source"])
        for field, forged in (("opf_chaptertour_entries", 14),
                              ("html_narrative_chapter_anchors", 16),
                              ("following_book_two_read_as_source", True)):
            d = copy.deepcopy(self.packet)
            d["source"][field] = forged
            with self.assertRaises(ValueError):
                validate(d)

    def test_opf_creator_variant_not_silently_reconciled(self):
        source, publisher = self.packet["source"], self.packet["publisher"]
        self.assertEqual("opf-local:0046", source["opf_inventory_id"])
        self.assertEqual("Loren L. Coleman & Randall N. Bills", source["owner_opf_creator_display"])
        self.assertEqual("Loren Coleman", publisher["creator_primary_display"])
        self.assertEqual("Loren L. Coleman", source["owner_opf_creator_primary_display"])
        self.assertEqual("CREATOR_DISPLAY_VARIANT_UNRESOLVED", source["creator_crosswalk_state"])
        for field, forged in (("creator_crosswalk_state", "SAME_PERSON_VERIFIED"),
                              ("opf_inventory_id", "opf-local:0045"),
                              ("owner_opf_creator_primary_display", "Loren Coleman")):
            d = copy.deepcopy(self.packet)
            d["source"][field] = forged
            with self.assertRaises(ValueError):
                validate(d)

    def test_decorated_isbn_and_two_different_opf_identifiers(self):
        src = self.packet["source"]
        self.assertEqual("0-7434-7609-3", src["raw_opf_work_isbn10_literal"])
        self.assertEqual("0-9673008-1-9", src["raw_opf_converter_header_isbn10_literal"])
        self.assertEqual("9780743476096", src["work_isbn13_checksum_conversion"])
        self.assertEqual([], src["opf_inventory_isbn_checksum_valid"])
        self.assertEqual("ISBN_CHECKSUM_ALIGNMENT_ONLY", src["publisher_edition_crosswalk_state"])
        d = copy.deepcopy(self.packet)
        d["source"]["publisher_edition_crosswalk_state"] = "EDITION_AUTHENTICATED"
        with self.assertRaises(ValueError):
            validate(d)

    def test_lit_conversion_not_rights_proof(self):
        src = self.packet["source"]
        self.assertEqual(262020, src["original_lit_member_length_bytes"])
        self.assertFalse(src["conversion_link_independently_reproduced"])
        self.assertFalse(src["ebook_access_rights_verified_for_public_ingestion"])
        for field, forged in (("original_lit_member_sha256", "0" * 64),
                              ("conversion_reported_output_file_count", 14),
                              ("conversion_link_independently_reproduced", True),
                              ("ebook_access_rights_verified_for_public_ingestion", True)):
            d = copy.deepcopy(self.packet)
            d["source"][field] = forged
            with self.assertRaises(ValueError):
                validate(d)

    def test_dream_not_real_world_event_and_sheth_time_is_contested(self):
        e = self.packet["evidence"]
        self.assertEqual("DREAM_AND_CHARACTER_ANXIETY", e[2]["kind"])
        self.assertEqual("CHARACTER_TESTIMONY_WITH_MATERIAL_GAPS", e[9]["kind"])
        self.assertEqual("CONTESTED_PROVISIONAL_TIMING", self.packet["assertions"][3]["status"])
        for idx, forged in ((2, "GRANDDAUGHTER_CONFIRMED_HARM"),
                            (9, "INDEPENDENT_HISTORICAL_FACT")):
            d = copy.deepcopy(self.packet)
            d["evidence"][idx]["kind"] = forged
            with self.assertRaises(ValueError):
                validate(d)

    def test_plague_claim_and_tractor_inference_not_confirmed(self):
        e = self.packet["evidence"]
        self.assertEqual("CHARACTER_CLAIM_UNCORROBORATED", e[8]["kind"])
        self.assertEqual("IN_STORY_TECHNICAL_INFERENCE", e[11]["kind"])
        self.assertEqual("INFERENCE_BY_TEV_NOT_PROVEN", self.packet["assertions"][4]["status"])
        for idx, forged in ((8, "PLAGUE_HISTORICALLY_VERIFIED"),
                            (11, "SABOTAGE_FORENSICALLY_PROVEN")):
            d = copy.deepcopy(self.packet)
            d["evidence"][idx]["kind"] = forged
            with self.assertRaises(ValueError):
                validate(d)

    def test_no_public_book_or_coverage_cross_work_promotion(self):
        for field, forged in (("copyrighted_book_text_exported", True),
                              ("accepted_work_effect", "ADDED"),
                              ("coverage_effect", "CLOSE_READ"),
                              ("public_explorer_effect", "SHOW"),
                              ("cross_work_reconciliation_effect", "SAME_AS_SCE36")):
            d = copy.deepcopy(self.packet)
            d[field] = forged
            with self.assertRaises(ValueError):
                validate(d)
        d = copy.deepcopy(self.packet)
        d["evidence"][0]["full_text"] = "forbidden"
        with self.assertRaises(ValueError):
            validate(d)

    def test_frozen_source_digests_and_ending_scope(self):
        for section, field, forged in (("source", "archive_sha256", "0" * 64),
                                       ("source", "html_sha256", "0" * 64),
                                       ("chapter_spans", "raw_span_sha256", "0" * 64),
                                       ("chapter_spans", "byte_end_exclusive", 170638),
                                       ("publisher", "isbn13", "9780743480840")):
            d = copy.deepcopy(self.packet)
            target = d[section] if section != "chapter_spans" else d[section][-1]
            target[field] = forged
            with self.assertRaises(ValueError):
                validate(d)

    def test_raw_span_scanner_requires_order_and_continuation(self):
        import hashlib
        source = b''.join(f'<section id="ch_{n}">chapter {n}</section>'.encode() for n in range(1, 16)) + b'TO BE CONTINUED'
        spans = scan_chapters(source)
        self.assertEqual(15, len(spans))
        self.assertEqual(hashlib.sha256(source[spans[0][0]:spans[0][1]]).hexdigest(), spans[0][2])
        for forged in (source.replace(b'ch_15', b'ch_x'), source.replace(b'ch_1', b'ch_2'),
                       source.replace(b'TO BE CONTINUED', b'BOOK COMPLETE')):
            with self.assertRaises(ValueError):
                scan_chapters(forged)

    def test_verifier_refuses_missing_private_archive(self):
        from pathlib import Path
        with self.assertRaises(ValueError):
            verify_archive(Path('/nonexistent/trek/private.zip'), self.packet)


if __name__ == "__main__":
    unittest.main()
