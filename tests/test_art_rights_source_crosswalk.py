"""Falsifier tests: rights evidence, edition metadata, and presentation are separate."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("art_rights_crosswalk_check", ROOT / "tools/check_art_rights_source_crosswalk.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
PACKET = json.loads(CHECK.PACKET.read_text(encoding="utf-8"))


class ArtRightsSourceCrosswalkTests(unittest.TestCase):
    def test_all_twelve_records_match_pinned_accepted_sources(self):
        result = CHECK.audit()
        self.assertEqual(result, {"rows_validated": 12, "accepted_source_files_pinned": 7,
                                  "rights_promotion": "NONE", "public_bytes_added": False})

    def reject(self, edit, pattern=None):
        packet = copy.deepcopy(PACKET)
        edit(packet)
        with self.assertRaisesRegex(ValueError, pattern or ""):
            CHECK.audit(packet)

    @staticmethod
    def row(packet, id_):
        return next(row for row in packet["entries"] if row["id"] == id_)

    def test_exact_accepted_source_sha_pin_rejects_mutation(self):
        self.reject(lambda p: p["accepted_input_digests"].__setitem__("explorer/search-catalog.json", "0" * 64),
                    "accepted input drift")

    def test_no_accepted_pin_can_be_omitted(self):
        self.reject(lambda p: p["accepted_input_digests"].pop("explorer/beyond-premiere-release-decision.json"),
                    "input pin set changed")

    def test_no_duplicate_crosswalk_identity(self):
        self.reject(lambda p: p["entries"][1].__setitem__("id", p["entries"][0]["id"]),
                    "duplicate/missing entry id")

    def test_no_row_reclassified_as_source_bound(self):
        self.reject(lambda p: self.row(p, "opf-publisher-0010-isbn-agree-no-cover").__setitem__(
            "lane", "ACCEPTED_SOURCE_BOUND_BOOK"), "source/artwork rights lanes changed")

    def test_no_new_public_release_approval(self):
        self.reject(lambda p: self.row(p, "beyond-premiere-accepted-held").__setitem__(
            "new_public_release_eligible", True), "attempted artwork promotion")

    def test_no_coverage_or_work_admission_fabrication(self):
        for field in ("new_coverage_increment", "new_source_work_admissions"):
            with self.subTest(field=field):
                self.reject(lambda p: p.__setitem__(field, 1), "packet: mismatched")

    def test_original_svg_never_pretends_official_image(self):
        self.reject(lambda p: self.row(p, "original-category-episode").__setitem__(
            "reference_scope", "OFFICIAL_ENTERPRISE_EPISODE_FRAME"), "incorrectly assigned official reference")

    def test_original_sha_is_byte_pinned(self):
        self.reject(lambda p: self.row(p, "original-category-film").__setitem__(
            "asset_sha256", "f" * 64), "original art digest mismatch")

    def test_beyond_license_cannot_be_relabelled_compatible(self):
        self.reject(lambda p: self.row(p, "beyond-premiere-accepted-held").__setitem__(
            "license", "CC BY 4.0"), "Beyond photo: mismatched license")

    def test_beyond_is_not_film_frame(self):
        self.reject(lambda p: self.row(p, "beyond-premiere-accepted-held").__setitem__(
            "reference_scope", "CANON_FILM_STILL"), "Beyond photo: mismatched reference_scope")

    def test_external_jacket_not_rehostable_by_metadata(self):
        self.reject(lambda p: self.row(p, "kirk-autobiography-jacket-api").__setitem__(
            "rights_class", "PERMISSION_TO_REHOST"), "jacket:.*mismatched rights_class")

    def test_open_library_cover_id_is_exact_not_title_heuristic(self):
        self.reject(lambda p: self.row(p, "picard-dark-veil-jacket-api").__setitem__(
            "cover_id", 13083310), "jacket:.*mismatched cover_id")

    def test_cover_id_is_not_private_opf_edition_equivalence(self):
        self.reject(lambda p: self.row(p, "kirk-autobiography-jacket-api").__setitem__(
            "private_source_local_ref", "opf-local:0010"), "disguised as owned bytes/private OPF")

    def test_opf_isbn_agreement_is_not_global_work(self):
        self.reject(lambda p: self.row(p, "opf-publisher-0010-isbn-agree-no-cover").__setitem__(
            "work_identity", "CANONICAL_WORK_VERIFIED"), "OPF:.*mismatched work_identity")

    def test_opf_format_discrepancy_remains_held(self):
        self.reject(lambda p: self.row(p, "opf-publisher-0009-format-discrepancy-no-cover").__setitem__(
            "source_crosscheck_state", "ISBN_IDENTIFIER_AGREEMENT_SOURCE_LOCAL"),
            "OPF:.*mismatched source_crosscheck_state")

    def test_opf_title_discrepancy_cannot_grow_cover_association(self):
        self.reject(lambda p: self.row(p, "opf-publisher-0067-title-discrepancy-no-cover").__setitem__(
            "artwork_catalog_row_id", "directory:literature:unknown"), "falsely bound to cover")

    def test_local_proposal_is_not_an_accepted_source_receipt(self):
        self.reject(lambda p: self.row(p, "nemesis-local-unaccepted-photo").__setitem__(
            "proposed_source_commit", "3028765"), "local-unaccepted:.*mismatched proposed_source_commit")

    def test_picard_head_only_is_not_byte_sha_custody(self):
        self.reject(lambda p: self.row(p, "picard-costume-local-unaccepted-tiff").__setitem__(
            "original_sha256_local_proposal", "a" * 64), "local-unaccepted:.*mismatched original_sha256_local_proposal")

    def test_third_party_personality_rights_are_not_silent_release(self):
        self.reject(lambda p: self.row(p, "discovery-lucca-local-unaccepted-photo").__setitem__(
            "display_state", "APPROVED_FOR_DISPLAY"), "unaccepted media proposal release status changed")

    def test_no_machine_private_path_or_prose_in_public_manifest(self):
        manifest = (CHECK.PACKET.parent / "MANIFEST.md").read_text(encoding="utf-8")
        contents = CHECK.PACKET.read_text(encoding="utf-8")
        for item in (contents, manifest):
            self.assertNotRegex(item, r"(?i)(?:C:\\Users\\|D:\\VERA\\|/mnt/[cd]/|OneDrive\\Documents)")
            self.assertNotRegex(item, r"(?i)source[_ ]text|ebook[_ ]bytes|full transcript")
        self.assertFalse(list(CHECK.PACKET.parent.rglob("*.jpg")))
        self.assertFalse(list(CHECK.PACKET.parent.rglob("*.png")))
        self.assertFalse(list(CHECK.PACKET.parent.rglob("*.tif")))


if __name__ == "__main__":
    unittest.main()
