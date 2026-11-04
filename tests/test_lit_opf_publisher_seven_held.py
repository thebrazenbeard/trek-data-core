"""Adversarial checks for seven held publisher/owner-OPF metadata crosswalks."""

import copy
import json
import unittest
from pathlib import Path

from proposals.research.lit_opf_publisher_seven_20261104.validate import (
    DATA,
    ORIGINAL_OPF,
    validate,
)


class HeldPublisherOpfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(DATA.read_text(encoding="utf-8"))
        cls.opf = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))

    def test_exact_held_tranche_passes(self):
        self.assertEqual(7, validate(self.packet, self.opf))

    def test_no_existing_held_publisher_isbns_overlap(self):
        earlier = json.loads((Path(__file__).resolve().parents[1] /
                              "proposals/consolidator/held-publisher-ui-preview-20261104/held-publisher-preview.json")
                             .read_text(encoding="utf-8"))
        old = {row["isbn13"] for row in earlier["rows"]}
        self.assertFalse(old.intersection({row["isbn13"] for row in self.packet["rows"]}))

    def test_no_accepted_identity_or_coverage_promotion(self):
        for field, bad in (("coverage_effect", "DISCOVERED"), ("accepted_work_effect", "ADDED"),
                           ("accepted_source_binding_effect", "VERIFIED"),
                           ("accepted_evidence_effect", "ADDED"), ("public_explorer_effect", "YES"),
                           ("copyrighted_text_exported", True), ("full_text_read", True),
                           ("private_manifestation_binding_verified", True),
                           ("synopsis_publication_effect", "ADDED")):
            with self.subTest(field=field):
                bad_doc = copy.deepcopy(self.packet)
                bad_doc[field] = bad
                with self.assertRaises(ValueError):
                    validate(bad_doc, self.opf)

    def test_bogus_isbns_and_edition_swap_rejected(self):
        cases = (
            (0, "isbn13", "9780743420861"),  # bad check digit
            (0, "isbn13", "9780743420877"),  # valid but another row
            (1, "opf_claimed_isbn10", "0743420861"),
            (1, "opf_local_id", "opf-local:0055"),
            (1, "opf_entry_sha256", "0" * 64),
        )
        for idx, field, value in cases:
            with self.subTest(idx=idx, field=field):
                bad_doc = copy.deepcopy(self.packet)
                bad_doc["rows"][idx][field] = value
                with self.assertRaises(ValueError):
                    validate(bad_doc, self.opf)

    def test_publisher_and_metadata_spoofs_rejected(self):
        cases = (
            (0, "publisher_page", "https://www.simonandschuster.com.evil.test/books/x"),
            (0, "publisher_page", "https://www.simonandschuster.com/books/Power-Hungry/x/9780743420860?x=y"),
            (0, "publisher_page", "https://www.simonandschuster.com/books/Power-Hungry/Howard-Weinstein/Star-Trek-The-Next-Generation/9780743420877"),
            (0, "publisher_title", "Masks"),
            (0, "creator_credits", ["Peter David"]),
            (0, "publisher_date_us", "2099-99-99"),
            (0, "publisher_extent_pages", -7),
            (0, "publisher_extent_pages", True),
            (0, "publisher_title", "<img onerror=alert(1)>"),
            (5, "source_anomaly", None),
            (0, "source_anomaly", "CARTER_CARMEN_HEADER_VS_BIO_OPF_UNRESOLVED"),
            (5, "creator_credits", ["Peter David", "Carmen Carter", "Michael Jan Friedman", "Robert Greenberger"]),
        )
        for idx, field, value in cases:
            with self.subTest(idx=idx, field=field):
                bad_doc = copy.deepcopy(self.packet)
                bad_doc["rows"][idx][field] = value
                with self.assertRaises(ValueError):
                    validate(bad_doc, self.opf)

    def test_private_or_raw_content_injection_rejected(self):
        for field, value in (("private_member_path", "D:/private/novel.epub"),
                             ("ebook_excerpt", "A paragraph from the novel"),
                             ("cover_image_url", "https://publisher/cover.jpg"),
                             ("global_work_id", "novel:55")):
            with self.subTest(field=field):
                bad_doc = copy.deepcopy(self.packet)
                bad_doc["rows"][0][field] = value
                with self.assertRaises(ValueError):
                    validate(bad_doc, self.opf)

    def test_reordering_or_dropping_row_is_rejected(self):
        for mutation in (lambda d: d["rows"].reverse(), lambda d: d["rows"].pop()):
            bad_doc = copy.deepcopy(self.packet)
            mutation(bad_doc)
            with self.assertRaises(ValueError):
                validate(bad_doc, self.opf)

    def test_owner_opf_claim_cannot_be_swapped_or_promoted(self):
        for field, changed in (("isbn_checksum_valid", ["074342087X"]),
                               ("parse_status", "NAMESPACE_RECOVERED"),
                               ("opf_entry_sha256", "0" * 64)):
            with self.subTest(field=field):
                opf = copy.deepcopy(self.opf)
                source_row = next(r for r in opf["rows"] if r["source_local_id"] == "opf-local:0055")
                source_row[field] = changed
                with self.assertRaises(ValueError):
                    validate(self.packet, opf)

    def test_provenance_source_hash_and_upstream_independence_are_pinned(self):
        for field, changed in (("opf_metadata_sha256", "0" * 64),
                               ("independent_publisher_families", 7),
                               ("publisher_upstream_family", "independent-seven"),
                               ("publisher_snapshot_bytes_held", True)):
            with self.subTest(field=field):
                packet = copy.deepcopy(self.packet)
                packet[field] = changed
                with self.assertRaises(ValueError):
                    validate(packet, self.opf)


if __name__ == "__main__":
    unittest.main()
