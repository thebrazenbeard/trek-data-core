"""Adversarial checks for one complete privately read, HELD S.C.E. #34 source."""

import copy
import json
import unittest

from proposals.research.sce34_private_complete_read_20261104.validate import DATA, validate
from proposals.research.sce34_private_complete_read_20261104.verify_owner_archive import scan_chapters, verify_archive


class SCE34ReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(DATA.read_text(encoding="utf-8"))

    def test_complete_private_source_is_held_not_accepted(self):
        self.assertEqual((1, 1, 8, 10, 7), validate(self.packet))
        self.assertEqual("HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED", self.packet["status"])
        self.assertEqual("NONE", self.packet["accepted_work_effect"])
        self.assertEqual("NONE", self.packet["accepted_close_read_effect"])

    def test_seven_chapters_end_before_about_and_next_story(self):
        src = self.packet["source"]
        self.assertEqual(7, src["opf_chaptertour_entries"])
        self.assertEqual(7, src["html_narrative_chapter_anchors"])
        spans = self.packet["chapter_spans"]
        self.assertEqual([1, 2, 3, 4, 5, 6, 7], [c["number"] for c in spans])
        self.assertEqual(113016, spans[-1]["byte_end_exclusive"])
        self.assertFalse(src["following_book_three_teaser_read_as_source"])
        for field, forged in (("opf_chaptertour_entries", 8), ("html_narrative_chapter_anchors", 6),
                              ("following_book_three_teaser_read_as_source", True)):
            document = copy.deepcopy(self.packet)
            document["source"][field] = forged
            with self.assertRaises(ValueError):
                validate(document)

    def test_isbn_inventory_omission_does_not_authenticate_copy(self):
        src = self.packet["source"]
        self.assertEqual("opf-local:0045", src["opf_inventory_id"])
        self.assertEqual([], src["opf_inventory_isbn_checksum_valid"])
        self.assertEqual("0-7434-8084-8", src["raw_opf_isbn10_literal"])
        self.assertEqual("9780743480840", src["raw_opf_isbn10_checksum_conversion"])
        self.assertEqual("ISBN_CHECKSUM_ALIGNMENT_ONLY", src["publisher_edition_crosswalk_state"])
        for field, forged in (("opf_inventory_isbn_checksum_valid", ["0743480848"]),
                              ("publisher_edition_crosswalk_state", "EDITION_AUTHENTICATED"),
                              ("raw_opf_isbn10_checksum_conversion", "9780743480833")):
            document = copy.deepcopy(self.packet)
            document["source"][field] = forged
            with self.assertRaises(ValueError):
                validate(document)

    def test_original_lit_conversion_is_not_a_license_proof(self):
        src = self.packet["source"]
        self.assertFalse(src["ebook_access_rights_verified_for_public_ingestion"])
        self.assertFalse(src["conversion_link_independently_reproduced"])
        self.assertEqual(236948, src["original_lit_member_length_bytes"])
        for field, forged in (("conversion_reported_status", "skipped"),
                              ("original_lit_member_sha256", "0" * 64),
                              ("conversion_link_independently_reproduced", True),
                              ("ebook_access_rights_verified_for_public_ingestion", True)):
            document = copy.deepcopy(self.packet)
            document["source"][field] = forged
            with self.assertRaises(ValueError):
                validate(document)

    def test_no_cross_work_identity_reconciliation_with_book_one(self):
        work = self.packet["work_candidate"]
        self.assertEqual("work-local:sce34-collective-hindsight-book-two", work["local_work_id"])
        self.assertFalse(work["global_work_identity_resolved"])
        self.assertEqual("NONE", self.packet["cross_work_reconciliation_effect"])
        self.assertEqual("UNRESOLVED", self.packet["assertions"][-1]["status"])
        for field, forged in (("cross_work_reconciliation_effect", "SAME_AS_SCE33"),
                              ("accepted_work_effect", "ADDED"), ("coverage_effect", "ADVANCED")):
            document = copy.deepcopy(self.packet)
            document[field] = forged
            with self.assertRaises(ValueError):
                validate(document)

    def test_narrated_theories_not_promoted_into_world_state(self):
        evidence = self.packet["evidence"]
        self.assertEqual("IN_STORY_CREW_HYPOTHESIS", evidence[4]["kind"])
        self.assertEqual("IN_STORY_COMPUTER_DIRECTIVE_REPORT", evidence[5]["kind"])
        self.assertEqual("IN_STORY_SENSOR_LIMIT", evidence[7]["kind"])
        for idx, value in ((4, "OBJECTIVE_PHYSICS_FACT"), (5, "CERTIFIED_WORLD_TRUTH"),
                           (7, "DESTROYED_SHIP_CONFIRMED")):
            document = copy.deepcopy(self.packet)
            document["evidence"][idx]["kind"] = value
            with self.assertRaises(ValueError):
                validate(document)

    def test_no_private_prose_or_coverage_smuggling(self):
        for field, forged in (("copyrighted_book_text_exported", True),
                              ("public_explorer_effect", "ADDED"),
                              ("accepted_source_binding_effect", "SOURCE_BOUND"),
                              ("private_source_manifestation_authenticated", True)):
            document = copy.deepcopy(self.packet)
            document[field] = forged
            with self.assertRaises(ValueError):
                validate(document)
        document = copy.deepcopy(self.packet)
        document["evidence"][0]["book_passage"] = "forbidden"
        with self.assertRaises(ValueError):
            validate(document)

    def test_fingerprint_and_locator_falsifiers(self):
        for section, field, forged in (("source", "html_sha256", "0" * 64),
                                       ("source", "opf_sha256", "0" * 64),
                                       ("publisher", "isbn13", "9780743480833"),
                                       ("chapter_spans", "byte_end_exclusive", 115388)):
            document = copy.deepcopy(self.packet)
            target = document[section] if section != "chapter_spans" else document[section][-1]
            target[field] = forged
            with self.assertRaises(ValueError):
                validate(document)

    def test_byte_scanner_requires_all_ordered_chapters_and_end_marker(self):
        import hashlib
        raw = b''.join(f'<section id="ch_{n}">chapter {n}</section>'.encode() for n in range(1, 8)) + b'>END<'
        spans = scan_chapters(raw)
        self.assertEqual(7, len(spans))
        self.assertEqual(hashlib.sha256(raw[spans[1][0]:spans[1][1]]).hexdigest(), spans[1][2])
        for forged in (raw.replace(b'ch_7', b'ch_x'), raw.replace(b'ch_1', b'ch_2'),
                       raw.replace(b'>END<', b'>MORE<')):
            with self.assertRaises(ValueError):
                scan_chapters(forged)

    def test_local_archive_verifier_fails_closed(self):
        from pathlib import Path
        with self.assertRaises(ValueError):
            verify_archive(Path('/nonexistent/owner/archive.zip'), self.packet)


if __name__ == "__main__":
    unittest.main()
