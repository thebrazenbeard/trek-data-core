"""Mutation-based falsifiers for held TOS OPF publisher page metadata."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

import validate as subject


class TOSPublisherHeldTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(subject.PACKET.read_text(encoding="utf-8"))
        self.accepted = json.loads(subject.SOURCE.read_text(encoding="utf-8"))

    def reject(self, mutate, label):
        report, accepted = deepcopy(self.report), deepcopy(self.accepted)
        mutate(report, accepted)
        with self.assertRaisesRegex(ValueError, label):
            subject.validate_packet(report, accepted)

    def test_original_23_publisher_source_rows_validate(self):
        self.assertEqual(subject.validate(), (23, 5))

    def test_known_isbn10_alignment_not_mapped_to_2019_reissue(self):
        self.reject(lambda r, _: r["rows"][0].update({
            "publisher_isbn13": "9781982139193",
            "publisher_url": "https://www.simonandschuster.com/books/Star-Trek/Gene-Roddenberry/Star-Trek/9781982139193"}),
            "source ISBN10/publisher ISBN13")

    def test_same_publisher_family_cannot_be_claimed_independent(self):
        self.reject(lambda r, _: r.update(independent_source_families=23), "drift: independent_source_families")

    def test_work_admission_and_release_fail_closed(self):
        self.reject(lambda r, _: r.update(work_admissions=23), "drift: work_admissions")
        self.reject(lambda r, _: r.update(public_explorer_release="RELEASED"), "drift: public_explorer_release")
        self.reject(lambda r, _: r.update(coverage_effect="CLOSE_READ"), "drift: coverage_effect")

    def test_source_fingerprint_and_duplicate_id_mutations_rejected(self):
        self.reject(lambda r, _: r["rows"][1].update(opf_entry_sha256="f" * 64), "fingerprint mismatch")
        self.reject(lambda r, _: r["rows"][3].update(opf_source_local_id="opf-local:0142"), "IDs changed")

    def test_isbn_checksum_and_offsite_locator_mutations_rejected(self):
        self.reject(lambda r, _: r["rows"][6].update(publisher_isbn13="9780743419582"), "checksum-invalid")
        self.reject(lambda r, _: r["rows"][6].update(
            publisher_url="https://publisher.example/books/The-Wrath-of-Khan/9780743419581"), "not exact first-party")

    def test_mindshadow_creator_contradiction_cannot_be_resolved(self):
        self.reject(lambda r, _: r["rows"][21].update(publisher_byline=["Kevin Underwood"]),
                    "Mindshadow.*contradiction")
        self.reject(lambda r, a: a["rows"][162].update(creator=["J.M. Dillard"]),
                    "Mindshadow.*contradiction")
        self.reject(lambda r, _: r["rows"][21].update(hold="PRIVATE_EDITION_UNVERIFIED"),
                    "Mindshadow.*contradiction")

    def test_rihannsu_vs_tos_classification_disagreement_retained(self):
        self.reject(lambda r, _: r["rows"][15].update(hold="PRIVATE_EDITION_UNVERIFIED"),
                    "Rihannsu/TOS")

    def test_source_absent_creator_does_not_become_publisher_creator(self):
        self.reject(lambda r, _: r["rows"][5].update(hold="PRIVATE_EDITION_UNVERIFIED"),
                    "absent source OPF creator")

    def test_prometheus_creator_order_is_source_relative(self):
        self.reject(lambda r, _: r["rows"][4].update(publisher_byline=["Sondra Marshak", "Myrna Culbreath"]),
                    "Prometheus Design byline order")

    def test_short_blurb_cannot_expand_to_copyrighted_passage(self):
        self.reject(lambda r, _: r["rows"][0].update(publisher_blurb_paraphrase="long text " * 100),
                    "unbounded original short")

    def test_report_receipt_is_byte_pinned(self):
        self.assertEqual(subject.validate(), (23, 5))
        self.assertFalse(self.report["publisher_page_raw_bytes_snapshotted"])
        self.assertFalse(self.report["owner_private_opf_xml_or_ebook_prose_read_this_batch"])


if __name__ == "__main__":
    unittest.main()
