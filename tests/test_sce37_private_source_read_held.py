"""Negative and positive boundary probes for HELD private S.C.E. #37 research."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from proposals.research.sce37_private_complete_read_20261105.validate import DATA, validate
from proposals.research.sce37_private_complete_read_20261105.verify_owner_archive import scan_chapters, verify_archive


class SCE37PrivateSourceReadHeldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(DATA.read_text(encoding="utf-8"))

    def reject(self, scope, field, value):
        packet = copy.deepcopy(self.packet)
        scope(packet)[field] = value
        with self.assertRaises(ValueError):
            validate(packet)

    def test_full_read_with_zero_accepted_effects(self):
        self.assertEqual((1, 1, 15, 10, 10), validate(self.packet))
        self.assertFalse(self.packet["private_source_manifestation_authenticated"])
        for key in ("accepted_work_effect", "accepted_source_binding_effect", "accepted_evidence_effect",
                    "accepted_close_read_effect", "coverage_effect", "public_explorer_effect",
                    "cross_work_reconciliation_effect"):
            with self.subTest(key=key):
                self.reject(lambda p: p, key, "ADDED")

    def test_exact_private_book_and_author_not_stale_sce36(self):
        src = self.packet["source"]
        self.assertEqual("opf-local:0048", src["opf_inventory_id"])
        self.assertEqual("Allyn Gibson", src["owner_opf_creator_display"])
        self.assertEqual("Ring Around the Sky", self.packet["work_candidate"]["owner_opf_title"])
        self.assertEqual("9780743476119", self.packet["publisher"]["isbn13"])
        self.assertEqual(37, self.packet["publisher"]["series_number"])
        self.reject(lambda p: p["source"], "opf_inventory_id", "opf-local:0047")
        self.reject(lambda p: p["source"], "owner_opf_creator_display", "Loren L. Coleman")
        self.reject(lambda p: p["publisher"], "isbn13", "9780743476102")

    def test_full_chapter_tag_starts_and_author_biography_ends(self):
        spans = self.packet["chapter_spans"]
        self.assertEqual(list(range(1, 11)), [c["number"] for c in spans])
        self.assertEqual(7250, spans[0]["byte_start_inclusive"])
        self.assertEqual(22282, spans[1]["byte_start_inclusive"])
        self.assertEqual(197110, spans[-1]["byte_end_exclusive"])
        self.assertEqual("FIRST_BYTE_OF_FULL_DIV_CLASS_CHAPTER_ID_TAG",
                         self.packet["source"]["chapter_span_start_rule"])
        for scope, field, forged in (
            (lambda p: p["chapter_spans"][0], "byte_start_inclusive", 7275),
            (lambda p: p["chapter_spans"][1], "byte_start_inclusive", 22307),
            (lambda p: p["chapter_spans"][-1], "byte_end_exclusive", 197975),
            (lambda p: p["source"], "novel_about_author_start_byte", 197975),
            (lambda p: p["source"], "chapter_span_start_rule", "EMBEDDED_ID_TOKEN_START"),
            (lambda p: p["source"], "following_author_biography_or_next_work_promo_read_as_novel", True),
        ):
            with self.subTest(field=field):
                self.reject(scope, field, forged)

    def test_scanner_matches_full_tag_and_refuses_bio_as_chapter(self):
        head = b'<!doctype html><html><body>\n'
        narrative = b''.join(f'<div class="chapter" id="ch_{i}">example {i}</div>'.encode()
                             for i in range(1, 11))
        biography = b'<div class="aboutAuthorPage" id="bm_1">author biography</div>'
        after = b'<div class="backMatterPage">next book advertisement</div>'
        html = head + narrative + biography + after
        actual = scan_chapters(html)
        self.assertEqual(10, len(actual))
        self.assertEqual(len(head), actual[0][0])
        self.assertEqual(html.index(b'<div class="chapter" id="ch_2">'), actual[0][1])
        self.assertNotEqual(html.index(b'ch_1'), actual[0][0])
        self.assertEqual(html.index(b'<div class="aboutAuthorPage"'), actual[-1][1])
        self.assertEqual(hashlib.sha256(html[actual[0][0]:actual[0][1]]).hexdigest(), actual[0][2])
        for forged in (html.replace(b'ch_1', b'ch_2'),
                       html.replace(b'ch_10', b'ch_9'),
                       html.replace(b'aboutAuthorPage', b'backMatterPage')):
            with self.subTest(forged=forged[:30]):
                with self.assertRaises(ValueError):
                    scan_chapters(forged)

    def test_source_provenance_not_a_public_distribution_license(self):
        src = self.packet["source"]
        self.assertEqual("0-7434-7611-5", src["raw_opf_work_isbn10_literal"])
        self.assertEqual("0-9673008-1-9", src["raw_opf_converter_header_isbn10_literal"])
        self.assertEqual("ISBN_CHECKSUM_ALIGNMENT_ONLY", src["publisher_edition_crosswalk_state"])
        self.assertEqual("DISPLAY_NAME_ALIGNMENT_ONLY", src["creator_crosswalk_state"])
        for field, forged in (("archive_sha256", "0" * 64), ("html_sha256", "0" * 64),
                              ("original_lit_member_sha256", "0" * 64),
                              ("conversion_link_independently_reproduced", True),
                              ("ebook_access_rights_verified_for_public_ingestion", True),
                              ("publisher_edition_crosswalk_state", "SAME_EDITION_VERIFIED"),
                              ("creator_crosswalk_state", "GLOBAL_IDENTITY_RESOLVED")):
            with self.subTest(field=field):
                self.reject(lambda p: p["source"], field, forged)

    def test_dream_fury_origin_and_authorship_disambiguation(self):
        typed = {a["predicate"]: a for a in self.packet["assertions"]}
        self.assertEqual("HYPOTHESIS_NOT_AUTHENTICATED_HISTORY", typed["ORIGINAL_BUILDER_IDENTITY"]["status"])
        self.assertEqual("PAST_EVENT_WITH_DREAM_AND_TESTIMONY_SEPARATED", typed["MOTHERS_ACCIDENT_AND_RECURRING_DREAM"]["status"])
        self.assertEqual("LINGUISTIC_ANALYSIS_PLUS_CHARACTER_ADMISSION", typed["DISSERTATION_AUTHORSHIP"]["status"])
        self.assertEqual("DEPICTED_PLAN_ATTRIBUTION_VERSUS_PUBLIC_CLAIM", typed["CONTROLLED_COLLAPSE_PLAN_CREDIT"]["status"])
        self.reject(lambda p: p["assertions"][0], "status", "FURIES_PROVEN_EVOLVED_HERE")
        self.reject(lambda p: p["assertions"][2], "status", "OPENING_DREAM_REAL_TIME_DISASTER")
        self.reject(lambda p: p["assertions"][5], "status", "AUTHORSHIP_LEGALLY_ADJUDICATED")

    def test_source_local_entities_and_chapter_bound_evidence_only(self):
        self.assertTrue(all(x["identity_scope"] == "THIS_SOURCE_ONLY" for x in self.packet["local_entities"]))
        self.assertEqual(list(range(1, 11)), [e["chapter"] for e in self.packet["evidence"]])
        self.reject(lambda p: p["local_entities"][0], "identity_scope", "GLOBAL")
        self.reject(lambda p: p["evidence"][0], "chapter", 2)
        self.reject(lambda p: p["assertions"][0], "evidence_refs", ["sce36:e02"])

    def test_copyrighted_prose_and_cover_content_excluded(self):
        self.assertFalse(self.packet["copyrighted_book_text_exported"])
        self.reject(lambda p: p, "copyrighted_book_text_exported", True)
        self.reject(lambda p: p["evidence"][0], "full_text", "forbidden")
        self.reject(lambda p: p["chapter_spans"][0], "quote", "forbidden")

    def test_private_verifier_fails_closed_on_absent_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                verify_archive(Path(tmp) / "Star_Trek_OPF_Converted.zip", self.packet)


if __name__ == "__main__":
    unittest.main()
