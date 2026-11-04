import copy
import json
import unittest

from tools.check_three_media_sources_held import PACKET_PATH, validate


class ThreeMediaSourceHeldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))

    def changed(self, row, key, value):
        proposal = copy.deepcopy(self.packet)
        proposal["candidates"][row][key] = value
        return proposal

    def test_current_packet_passes(self):
        self.assertEqual([], validate(self.packet))

    def test_public_promotion_denied(self):
        packet = copy.deepcopy(self.packet)
        packet["public_release_eligible"] = True
        self.assertTrue(validate(packet))

    def test_coverage_inflation_denied(self):
        packet = copy.deepcopy(self.packet)
        packet["accepted_coverage_increment"] = 3
        self.assertTrue(validate(packet))

    def test_download_and_publication_effect_denied(self):
        packet = copy.deepcopy(self.packet)
        packet["image_downloaded"] = True
        self.assertTrue(validate(packet))

    def test_distinct_creators_required(self):
        self.assertTrue(validate(self.changed(2, "creator", "Niccolò Caranti")))

    def test_distinct_source_families_required(self):
        self.assertTrue(validate(self.changed(2, "source_family_id", self.packet["candidates"][1]["source_family_id"])))

    def test_fixed_revision_required(self):
        self.assertTrue(validate(self.changed(1, "fixed_description_revision_oldid", 15)))

    def test_url_revision_matches_identity(self):
        self.assertTrue(validate(self.changed(0, "fixed_description_url", "https://commons.wikimedia.org/wiki/File:Glenn_Cote_Brent_Spiner.jpg")))

    def test_gfdl_not_reclassified_as_cc(self):
        self.assertTrue(validate(self.changed(0, "license_id", "CC_BY_SA_4_0_INTERNATIONAL")))

    def test_gfdl_not_directly_allowlisted(self):
        self.assertTrue(validate(self.changed(0, "license_allowlist_state", "NOMINALLY_RECOGNIZED_BUT_NOT_RELEASE_APPROVAL")))

    def test_vrt_private_ticket_not_claimed_seen(self):
        self.assertTrue(validate(self.changed(0, "license_evidence", "VRT ticket independently inspected and approved")))

    def test_cc_license_version_not_downgraded(self):
        self.assertTrue(validate(self.changed(1, "license_url", "https://creativecommons.org/licenses/by-sa/2.0/")))

    def test_reported_sha1_not_independent_sha256(self):
        self.assertTrue(validate(self.changed(1, "independent_binary_sha256", "a" * 64)))

    def test_reported_sha1_validity(self):
        self.assertTrue(validate(self.changed(1, "reported_original_sha1", "123")))

    def test_large_tiff_no_fabricated_checksum(self):
        self.assertTrue(validate(self.changed(2, "reported_original_sha1", "a" * 40)))

    def test_episode_misrepresentation_rejected(self):
        self.assertTrue(validate(self.changed(1, "asset_kind", "OFFICIAL_DISCOVERY_EPISODE_STILL")))

    def test_no_missing_rights_holds(self):
        self.assertTrue(validate(self.changed(2, "rights_holds", [])))


if __name__ == "__main__":
    unittest.main()
