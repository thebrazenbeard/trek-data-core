"""Held artwork source/license audit: synthetic tampering, no image downloads."""

from __future__ import annotations

import copy
import runpy
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = runpy.run_path(str(ROOT / "proposals/librarian/artwork-source-rights-audit-20261104/validate.py"))


class ArtworkSourceRightsAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = MODULE["read_json"](MODULE["LEDGER"])
        cls.catalogs = {path: MODULE["read_json"](ROOT / path) for path in MODULE["SOURCE_PATHS"]}
        cls.hashes = {path: MODULE["sha256"](ROOT / path) for path in MODULE["SOURCE_PATHS"]}

    def _reject(self, mutate, modify_sources=None, modify_hashes=None):
        packet = copy.deepcopy(self.ledger)
        catalogs = copy.deepcopy(self.catalogs)
        hashes = copy.deepcopy(self.hashes)
        mutate(packet)
        if modify_sources:
            modify_sources(catalogs)
        if modify_hashes:
            modify_hashes(hashes)
        with self.assertRaises(MODULE["ArtworkRightsAuditError"]):
            MODULE["validate"](packet, catalogs, hashes)

    def test_six_optin_api_previews_and_zero_copyright_licensing(self):
        self.assertEqual(MODULE["validate"](self.ledger, self.catalogs, self.hashes), {
            "core_display_candidates": 4, "supplement_display_candidates": 2,
            "licensed_self_hosted_assets": 0, "episode_actual_thumbnail_mappings": 0,
            "film_actual_thumbnail_mappings": 0, "research_coverage_effect": "NONE",
        })

    def test_reject_claim_underlying_copyright_is_cleared(self):
        self._reject(lambda p: p["images"][0].update(copyright_status="PUBLIC_DISPLAY_PERMISSION_VERIFIED"))

    def test_reject_claim_open_library_api_allows_rehosting(self):
        self._reject(lambda p: p["images"][0].update(self_hosting_rights_status="LICENSED_AND_AUTHORIZED"))

    def test_reject_optin_bypass(self):
        self._reject(lambda p: p["images"][0].update(display_route="REMOTE_API_ALWAYS_ON"))

    def test_reject_swapped_cover_id_for_same_publisher(self):
        self._reject(lambda p: p["images"][0].update(cover_id=p["images"][1]["cover_id"]))

    def test_reject_swapped_publisher_source_for_same_corporate_family(self):
        self._reject(lambda p: p["images"][0].update(publisher_locator=p["images"][1]["publisher_locator"]))

    def test_reject_forged_corporate_url_with_valid_edition(self):
        self._reject(lambda p: p["images"][4].update(publisher_locator="https://example.net/books/9781982154073"))

    def test_reject_episode_artwork_still_claim(self):
        self._reject(lambda p: p.update(actual_episode_thumbnail_mappings=4))

    def test_reject_film_artwork_poster_claim(self):
        self._reject(lambda p: p.update(actual_film_thumbnail_mappings=3))

    def test_reject_licensed_binary_claim_without_receipts(self):
        self._reject(lambda p: p.update(rights_verified_self_hosted_assets=1))

    def test_reject_unreviewed_extra_image(self):
        self._reject(lambda p: p["images"].append({"row_id": "film:film-wrath-of-khan"}))

    def test_reject_false_coverage(self):
        self._reject(lambda p: p.update(research_coverage_effect="CLOSE_READ"))

    def test_reject_source_digest_drift(self):
        self._reject(lambda p: p["source_catalog_sha256"].update({"explorer/artwork-catalog-v1.3.json": "0" * 64}))

    def test_reject_upstream_rights_status_escalation(self):
        source_path = "explorer/artwork-catalog-v1.3.json"
        self._reject(lambda p: None, modify_sources=lambda s: s[source_path]["artwork"][0].update(rights_status="PUBLIC_DOMAIN"))

    def test_reject_preexisting_local_rights_artifact_without_separate_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "explorer/licensed-artwork"
            path.mkdir(parents=True)
            with self.assertRaises(MODULE["ArtworkRightsAuditError"]):
                MODULE["validate"](self.ledger, self.catalogs, self.hashes, root=Path(tmp))

    def test_reject_inserted_publisher_license_claim_field(self):
        self._reject(lambda p: p["images"][0].update(rights_to_republish="yes"))


if __name__ == "__main__":
    unittest.main()
