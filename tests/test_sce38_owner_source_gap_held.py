"""Negative regressions for the #38 owner-private source gap, not a close read."""

import copy
import json
import unittest

from proposals.research.sce38_owner_source_gap_20261105 import validate as packet


class Sce38HeldSourceGapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical = json.loads(packet.DATA.read_text(encoding="utf-8"))

    def test_frozen_gap_packet_is_valid(self):
        self.assertEqual((2, 0, 0), packet.validate(self.canonical))

    def assert_rejected(self, mutate):
        data = copy.deepcopy(self.canonical)
        mutate(data)
        with self.assertRaises(ValueError):
            packet.validate(data)

    def test_cannot_claim_full_source_read(self):
        self.assert_rejected(lambda d: d["literary_processing"].update(full_private_source_read_done=True))

    def test_cannot_claim_sce38_member_present(self):
        self.assert_rejected(lambda d: d["owner_archive_scan"]["converted_opf_zip"].update(matched_sce38_or_orphans_member_names=1))

    def test_cannot_insert_fabricated_chapter_evidence(self):
        self.assert_rejected(lambda d: d["literary_processing"]["evidence"].append({"chapter": 1, "observation": "unsupported"}))

    def test_cannot_promote_coverage(self):
        self.assert_rejected(lambda d: d["effects"].update(coverage_effect="ADMITTED"))

    def test_cannot_forge_ebook_fingerprint(self):
        self.assert_rejected(lambda d: d["owner_archive_scan"]["original_lit_zip"].update(zip_sha256="0" * 64))

    def test_cannot_conflate_publisher_metadata_with_edition(self):
        self.assert_rejected(lambda d: d["public_metadata_candidate"].update(source_edition_identity_authenticated=True))

    def test_cannot_broaden_absence_claim_to_entire_cloud(self):
        self.assert_rejected(lambda d: d["owner_archive_scan"]["books_tree_name_search"].update(search_scope="ALL_CLOUD_DRIVES"))

    def test_cannot_export_source_text(self):
        self.assert_rejected(lambda d: d.update(full_text="copyrighted novel"))

    def test_unreviewed_packet_extension_fails_closed(self):
        self.assert_rejected(lambda d: d.update(unreviewed_extra_source_claim="new thing"))


if __name__ == "__main__":
    unittest.main()
