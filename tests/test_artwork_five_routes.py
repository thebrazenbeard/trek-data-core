"""Hostile release-eligibility tests; no image network calls or binaries."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_artwork_five_routes", ROOT / "tools/audit_artwork_five_routes.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class FiveArtworkRoutesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = mod.strict_json(mod.REVIEW.read_bytes())
        cls.accepted = mod.read_accepted_sources()

    def run_review(self, review_mutation=None, source_mutation=None, **flags):
        review = copy.deepcopy(self.review)
        sources = copy.deepcopy(self.accepted)
        if review_mutation:
            review_mutation(review)
        if source_mutation:
            source_mutation(sources)
        return mod.audit(review, sources, **flags)

    def test_actual_portfolio_no_public_license_or_binary_release(self):
        report = self.run_review()
        self.assertEqual(report["status"], "ZERO_LICENSED_IMAGE_BINARIES_AND_ONE_DOCUMENTED_OPT_IN_API_ROUTE")
        self.assertEqual(report["audited_representative_count"], 5)
        self.assertEqual(report["licensed_local_image_count"], 0)
        self.assertEqual(report["underlying_copyright_cleared_count"], 0)
        self.assertEqual(report["accepted_api_cover_sidecar_candidates"], 6)
        self.assertEqual(report["public_release_effect"], "NONE")

    def test_false_public_release_claim_rejected(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "false canonical or public image release"):
            self.run_review(lambda x: x.update(public_licensed_image_release="YES"))

    def test_publisher_metadata_license_escalation_rejected(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "publisher-linked"):
            self.run_review(source_mutation=lambda s: s["primary"]["observations"][0].update(rights_status="PUBLIC_DISPLAY_PERMISSION_VERIFIED"))

    def test_film_header_cannot_be_relabelled_as_verified_poster(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "publisher-linked"):
            self.run_review(source_mutation=lambda s: s["primary"]["observations"][0].update(image_kind="VERIFIED_THEATRICAL_POSTER"))

    def test_cross_medium_image_substitution_rejected(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "identity/route"):
            self.run_review(lambda x: x["representative_cases"][0].update(source_local_asset_id="art-film-wrath-khan-og-20261103"))

    def test_commercial_cover_download_link_cannot_be_called_license(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "rights evidence"):
            self.run_review(lambda x: x["representative_cases"][2].update(rights_evidence="PUBLISHER_OPEN_LICENSE"))

    def test_commons_license_does_not_clear_prop_and_brand_rights(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "Commons photo"):
            self.run_review(source_mutation=lambda s: s["commons"]["commons_photo_candidate"].update(underlying_fictional_prop_design_and_brand_rights="CLEARED"))

    def test_commons_no_image_sha256_from_only_commons_sha1(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "Commons photo"):
            self.run_review(source_mutation=lambda s: s["commons"]["commons_photo_candidate"].update(asset_sha256="a" * 64))

    def test_picard_api_preview_cannot_be_mirrored_or_licensed_by_label(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "Picard"):
            self.run_review(source_mutation=lambda s: s["picard"]["artwork"][0].update(rights_status="PUBLIC_DISPLAY_PERMISSION_VERIFIED"))

    def test_picard_cover_crosswalk_exact_edition(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "Picard"):
            self.run_review(source_mutation=lambda s: s["picard"]["artwork"][0].update(isbn="9781982175207"))

    def test_autobiography_api_routes_not_licensed_image_binaries(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "autobiography"):
            self.run_review(source_mutation=lambda s: s["autobio_api"]["artwork"][0].update(rights_status="PUBLIC_DISPLAY_PERMISSION_VERIFIED"))

    def test_real_licensed_binary_lane_requires_new_review(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "distinct review"):
            self.run_review(licensed_artwork_dir=True)
        with self.assertRaisesRegex(mod.ArtworkAuditError, "distinct review"):
            self.run_review(rights_receipts_dir=True)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(mod.ArtworkAuditError, "duplicate JSON"):
            mod.strict_json(b'{"rights_status":"HELD","rights_status":"CLEARED"}')


if __name__ == "__main__":
    unittest.main()
