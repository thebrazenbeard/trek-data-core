"""Hostile path/rights/authorization falsifiers for held photo decision proposal."""

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("beyond_release_proposal_validate", HERE / "validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PhotoReleaseProposalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for relative in [*MODULE.HELD_CONTRACTS, *[str(MODULE.FOLDER / leaf) for leaf in
                          ("decision.json", "MANIFEST.md", "validate.py", "test_validate.py")]]:
            source = MODULE.ROOT / relative
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    def tearDown(self):
        self.temp.cleanup()

    def _decision(self):
        return self.root / MODULE.FOLDER / "decision.json"

    def _mutate(self, mutation):
        path = self._decision()
        record = json.loads(path.read_text(encoding="utf-8"))
        mutation(record)
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def test_valid_candidate_is_explicitly_not_approved(self):
        self.assertEqual(MODULE.validate(self.root),
                         "TEXT_ONLY_AFFIRMATIVE_PROPOSAL_PENDING_REVIEW_NO_IMAGE_RELEASE")

    def test_prior_false_contract_missing_or_tampered(self):
        path = self.root / next(iter(MODULE.HELD_CONTRACTS))
        original = path.read_text(encoding="utf-8")
        path.unlink()
        with self.assertRaises(MODULE.ReleaseProposalRejected):
            MODULE.validate(self.root)
        path.write_text(original.replace('"public_image_display_authorized": false',
                                         '"public_image_display_authorized": true'), encoding="utf-8")
        with self.assertRaises(MODULE.ReleaseProposalRejected):
            MODULE.validate(self.root)

    def test_prior_decision_laundered_approved(self):
        self._mutate(lambda r: r.update(public_image_display_authorized=True))
        with self.assertRaises(MODULE.ReleaseProposalRejected):
            MODULE.validate(self.root)

    def test_new_positive_approval_forged(self):
        self._mutate(lambda r: r["required_new_dispositions"].update(owner_release_acceptance="RELEASE_AUTHORIZED"))
        with self.assertRaises(MODULE.ReleaseProposalRejected):
            MODULE.validate(self.root)

    def test_wrong_photo_or_modified_image_receipt(self):
        self._mutate(lambda r: r["release_rendition"].update(sha256="0" * 64))
        with self.assertRaises(MODULE.ReleaseProposalRejected):
            MODULE.validate(self.root)

    def test_rights_or_false_credit_changed(self):
        self._mutate(lambda r: r["copyright_and_other_rights"].update(license_url="https://creativecommons.org/publicdomain/zero/1.0/"))
        with self.assertRaises(MODULE.ReleaseProposalRejected):
            MODULE.validate(self.root)

    def test_forged_commons_url_with_matching_suffix_fails(self):
        self._mutate(lambda r: r["photo_identity"].update(
            commons_file="https://evil.example/irrelevant%2831784488840%29.jpg"))
        with self.assertRaises(MODULE.ReleaseProposalRejected):
            MODULE.validate(self.root)

    def test_forged_thumbnail_path_with_matching_suffix_fails(self):
        self._mutate(lambda r: r["release_rendition"].update(
            upstream_thumbnail="https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a4/forged-image-unrelated/%2831784488840%29.jpg"))
        with self.assertRaises(MODULE.ReleaseProposalRejected):
            MODULE.validate(self.root)

    def test_false_public_domain_license_label_fails(self):
        self._mutate(lambda r: r["copyright_and_other_rights"].update(
            photographer_license="Public Domain / CC0"))
        with self.assertRaises(MODULE.ReleaseProposalRejected):
            MODULE.validate(self.root)

    def test_unrelated_asset_publication_request_fails(self):
        self._mutate(lambda r: r.update(requested_effect="PUBLISH_ALL_NONRELATED_PIXELS"))
        with self.assertRaises(MODULE.ReleaseProposalRejected):
            MODULE.validate(self.root)

    def test_unreviewed_public_image_file_fails(self):
        destination = self.root / MODULE.ASSET_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"not even a real JPEG")
        with self.assertRaises(MODULE.ReleaseProposalRejected):
            MODULE.validate(self.root)

    def test_missing_manifest_or_tests_fails(self):
        for leaf in ("MANIFEST.md", "test_validate.py"):
            target = self.root / MODULE.FOLDER / leaf
            original = target.read_bytes()
            target.unlink()
            with self.assertRaises(MODULE.ReleaseProposalRejected):
                MODULE.validate(self.root)
            target.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
