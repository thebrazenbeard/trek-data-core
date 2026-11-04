"""Hostile falsifiers for one privately read SCE novella, not accepted research."""

import copy
import json
import unittest

from proposals.research.sce33_private_complete_read_20261104.validate import (
    DATA, validate,
)
from proposals.research.sce33_private_complete_read_20261104.verify_owner_archive import (
    scan_chapters, verify_archive,
)


class SCE33PrivateReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(DATA.read_text(encoding="utf-8"))

    def test_local_complete_source_not_accepted(self):
        self.assertEqual((1, 1, 7, 8, 5), validate(self.packet))
        self.assertEqual("HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED", self.packet["status"])
        self.assertEqual("NONE", self.packet["accepted_close_read_effect"])
        self.assertEqual("NONE", self.packet["accepted_work_effect"])

    def test_five_chapters_vs_four_opf_tour_entries(self):
        chapters = self.packet["chapter_spans"]
        self.assertEqual([1, 2, 3, 4, 5], [r["number"] for r in chapters])
        self.assertEqual(4, self.packet["source"]["opf_chaptertour_entries"])
        self.assertEqual(5, self.packet["source"]["html_narrative_chapter_anchors"])
        self.assertEqual(111428, chapters[-1]["byte_end_exclusive"])
        self.assertFalse(self.packet["source"]["continuation_book_two_read"])
        for field, value in (("opf_chaptertour_entries", 5),
                             ("html_narrative_chapter_anchors", 4),
                             ("continuation_book_two_read", True)):
            d = copy.deepcopy(self.packet)
            d["source"][field] = value
            with self.assertRaises(ValueError):
                validate(d)

    def test_raw_opf_decorated_isbn_not_silently_backfilled(self):
        source = self.packet["source"]
        self.assertEqual("opf-local:0044", source["opf_inventory_id"])
        self.assertEqual([], source["opf_inventory_isbn_checksum_valid"])
        self.assertEqual("0-7434-8083-X", source["raw_opf_isbn10_literal"])
        self.assertEqual("9780743480833", source["raw_opf_isbn10_checksum_conversion"])
        self.assertEqual("ISBN_CHECKSUM_ALIGNMENT_ONLY", source["publisher_edition_crosswalk_state"])
        for field, value in (("opf_inventory_isbn_checksum_valid", ["074348083X"]),
                             ("publisher_edition_crosswalk_state", "PRIVATE_EDITION_VERIFIED"),
                             ("raw_opf_isbn10_checksum_conversion", "9780743480840")):
            d = copy.deepcopy(self.packet)
            d["source"][field] = value
            with self.assertRaises(ValueError):
                validate(d)

    def test_owner_lit_conversion_provenance_not_equated_to_license(self):
        src = self.packet["source"]
        self.assertEqual("success", src["conversion_reported_status"])
        self.assertEqual(238466, src["original_lit_member_length_bytes"])
        self.assertFalse(src["conversion_link_independently_reproduced"])
        self.assertFalse(src["ebook_access_rights_verified_for_public_ingestion"])
        for field, value in (("conversion_reported_exit_code", 255),
                             ("conversion_link_independently_reproduced", True),
                             ("original_lit_member_sha256", "0" * 64),
                             ("conversion_manifest_sha256", "0" * 64)):
            d = copy.deepcopy(self.packet)
            d["source"][field] = value
            with self.assertRaises(ValueError):
                validate(d)

    def test_in_story_evidence_not_canonical_fact(self):
        e = self.packet["evidence"]
        self.assertEqual("CHARACTER_REPORTED_COMPUTER_LOG", e[3]["kind"])
        self.assertEqual("INFERENCE_BY_CHARACTER", e[4]["kind"])
        self.assertEqual("UNRESOLVED", self.packet["assertions"][-1]["status"])
        for idx, field, value in ((3, "kind", "NARRATOR_FACT"),
                                  (4, "kind", "OBJECTIVE_FACT"),
                                  (6, "chapter", 2)):
            d = copy.deepcopy(self.packet)
            d["evidence"][idx][field] = value
            with self.assertRaises(ValueError):
                validate(d)

    def test_source_hash_and_boundaries_falsifiers(self):
        for loc, field, value in (("source", "archive_sha256", "0" * 64),
                                  ("source", "html_sha256", "0" * 64),
                                  ("chapter_spans", "raw_span_sha256", "0" * 64),
                                  ("chapter_spans", "byte_end_exclusive", 113659),
                                  ("publisher", "isbn13", "9780743480840")):
            with self.subTest(loc=loc, field=field):
                d = copy.deepcopy(self.packet)
                target = d[loc] if loc != "chapter_spans" else d[loc][0]
                target[field] = value
                with self.assertRaises(ValueError):
                    validate(d)

    def test_private_prose_and_promotion_rejected(self):
        for field, value in (("accepted_work_effect", "ADDED"),
                             ("accepted_close_read_effect", "CLOSE_READ"),
                             ("coverage_effect", "ADVANCED"),
                             ("public_explorer_effect", "ADDED"),
                             ("copyrighted_book_text_exported", True),
                             ("private_source_manifestation_authenticated", True)):
            d = copy.deepcopy(self.packet)
            d[field] = value
            with self.assertRaises(ValueError):
                validate(d)

    def test_chapter_span_scanner_handles_five_anchors_and_falsifiers(self):
        import hashlib
        raw = b''.join(f'<section id="ch_{n}">part {n}</section>'.encode() for n in range(1, 6)) + b'TO BE CONTINUED'
        spans = scan_chapters(raw)
        self.assertEqual(5, len(spans))
        self.assertEqual(hashlib.sha256(raw[spans[0][0]:spans[0][1]]).hexdigest(), spans[0][2])
        for bad in (raw.replace(b'ch_5', b'ch_x'), raw.replace(b'ch_1', b'ch_2'),
                    raw.replace(b'TO BE CONTINUED', b'TO BE MORE')):
            with self.assertRaises(ValueError):
                scan_chapters(bad)

    def test_source_probe_refuses_missing_owner_zip_without_leak(self):
        from pathlib import Path
        with self.assertRaises(ValueError):
            verify_archive(Path('/nonexistent/private/copyrighted-input.zip'), self.packet)
        for field in ("full_text", "passage", "source_private_path", "canonical_work_id"):
            d = copy.deepcopy(self.packet)
            d["evidence"][0][field] = "forbidden"
            with self.assertRaises(ValueError):
                validate(d)


if __name__ == "__main__":
    unittest.main()
