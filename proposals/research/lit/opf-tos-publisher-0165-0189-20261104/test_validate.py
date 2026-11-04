"""Adversarial mutation fixtures for held TOS 0165–0189 publisher edition cards."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

import validate as subject


class TOSPublisherHeldSecondWaveTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(subject.PACKET.read_text(encoding="utf-8"))
        self.accepted = json.loads(subject.SOURCE.read_text(encoding="utf-8"))

    def reject(self, mutate, pattern):
        report, source = deepcopy(self.report), deepcopy(self.accepted)
        mutate(report, source)
        with self.assertRaisesRegex(ValueError, pattern):
            subject.validate_packet(report, source)

    def test_full_24_card_packet(self):
        self.assertEqual(subject.validate(), (24, 0))

    def test_held_semantics_cannot_be_silently_upgraded(self):
        self.reject(lambda r, _: r.update(close_reads=24), "drift: close_reads")
        self.reject(lambda r, _: r.update(work_admissions=24), "drift: work_admissions")
        self.reject(lambda r, _: r.update(public_explorer_release="RELEASED"), "drift: public_explorer_release")
        self.reject(lambda r, _: r.update(coverage_effect="SOURCE_BOUND"), "drift: coverage_effect")

    def test_one_publisher_family_is_not_24_independent_sources(self):
        self.reject(lambda r, _: r.update(independent_source_families=24), "drift: independent_source_families")

    def test_missing_owner_isbn_cannot_be_claimed_matched(self):
        self.reject(lambda r, _: r["rows"][3].update(source_isbn10_to_publisher_isbn13="MATCH"), "unreviewed publisher row fields")

    def test_duplicate_source_id_and_entry_fingerprint_tampering(self):
        self.reject(lambda r, _: r["rows"][7].update(opf_source_local_id="opf-local:0166"), "OPF local IDs")
        self.reject(lambda r, _: r["rows"][7].update(opf_entry_sha256="a" * 64), "fingerprint mismatch")

    def test_isbn_checksum_url_source_lineage(self):
        self.reject(lambda r, _: r["rows"][0].update(publisher_isbn13="9780743419818"), "ISBN13")
        self.reject(lambda r, _: r["rows"][0].update(publisher_url="https://evil.invalid/books/Demons/9780743419819"), "first-party")
        self.reject(lambda r, _: r["rows"][0].update(publisher_url="https://www.simonandschuster.com/books/Demons/9780743419826"), "first-party")

    def test_author_name_order_inversion_not_normalized(self):
        self.reject(lambda r, _: r["rows"][4].update(publisher_byline=["Carmen Carter"]), "Carter Carmen")
        self.reject(lambda r, _: r["rows"][4].update(hold="PRIVATE_EDITION_UNVERIFIED"), "Carter Carmen")

    def test_rihannsu_and_tos_nested_series_are_compatible(self):
        self.reject(lambda r, _: r["rows"][5].update(hold="RIHANNSU_VS_TOS_TAXONOMY_HELD"), "compatible nested")
        self.reject(lambda r, _: r["rows"][5].update(publisher_subtitle=None), "compatible nested")

    def test_idic_plan_title_is_not_silently_equated_to_epidemic(self):
        self.reject(lambda r, _: r["rows"][8].update(hold="PRIVATE_EDITION_UNVERIFIED"), "IDIC")
        self.reject(lambda r, _: r["rows"][8].update(publisher_title="IDIC Plan"), "IDIC")

    def test_disinherited_source_three_creators_vs_publisher_one(self):
        self.reject(lambda r, _: r["rows"][23].update(publisher_byline=["Peter David", "Michael Jan Friedman", "Robert Greenberger"]), "three creators")
        self.reject(lambda r, _: r["rows"][23].update(hold="PRIVATE_EDITION_UNVERIFIED"), "three creators")

    def test_truncated_official_title_not_silently_fixed(self):
        self.reject(lambda r, _: r["rows"][19].update(publisher_title="A Flag Full of Stars"), "truncated")

    def test_opf_duplicate_number_preserved_as_disagreement(self):
        self.reject(lambda r, _: r["rows"][18].update(hold="PRIVATE_EDITION_UNVERIFIED"), "duplicate OPF #53")

    def test_2006_ebook_is_not_2010_paperback(self):
        self.reject(lambda r, _: r["rows"][12].update(publisher_date="2010-12-01"), "2006 eBook")
        self.reject(lambda r, _: r["rows"][12].update({
            "publisher_isbn13": "9781451623345",
            "publisher_url": "https://www.simonandschuster.com/books/Star-Trek-The-Original-Series-Vulcans-Glory/D-C-Fontana/Star-Trek-The-Original-Series/9781451623345"}), "2006 eBook")

    def test_short_paraphrase_and_receipt_guard(self):
        self.reject(lambda r, _: r["rows"][1].update(publisher_blurb_paraphrase="published marketing copy " * 100), "short original")
        self.assertEqual(subject.validate(), (24, 0))


if __name__ == "__main__":
    unittest.main()
