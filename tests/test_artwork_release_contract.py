"""Synthetic-only, fail-closed release tests. No Trek image/license is admitted."""
from __future__ import annotations

import base64
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import validate_artwork_release as art

# Plain, synthetic 1-pixel fixture; never published as a Star Trek picture.
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=")
FILM_LOCATOR = "https://www.startrek.com/movies/star-trek-2009"
BOOK_LOCATOR = ("https://www.penguinrandomhouse.com/books/250795/"
                "the-autobiography-of-james-t-kirk-by-david-a-goodman/")
FILM_ID = "film:film-2009"
BOOK_ID = "directory:literature:prh-autobiography-kirk"
ISBN = "9781783297481"
RIGHTS_URL = "https://commons.wikimedia.org/wiki/File:Synthetic_artwork.png"
RIGHTS_REV = "https://commons.wikimedia.org/wiki/File:Synthetic_artwork.png?oldid=12345"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class ArtworkReleaseContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "explorer").mkdir()
        shutil.copyfile(ROOT / "explorer/app.css", self.root / "explorer/app.css")
        shutil.copyfile(ROOT / "explorer/index.html", self.root / "explorer/index.html")
        self._json("explorer/discovery-catalog.json", {
            "data_status": "DISCOVERY_ONLY", "coverage_effect": "NONE", "admission_effect": "NONE",
            "row_count": 1, "rows": [{"row_id": "literature:prh-autobiography-kirk", "medium": "LITERATURE",
                                    "candidate_kind": "FICTIONAL_MEMOIR",
                                    "source_group": "distributor:penguinrandomhouse.com:titan-books",
                                    "source_locator": BOOK_LOCATOR, "details": [f"Paperback ISBN {ISBN}"]}]})
        self._json("explorer/film-catalog.json", {
            "data_status": "DISCOVERY_ONLY", "coverage_effect": "NONE", "film_count": 1,
            "films": [{"id": "film-2009", "source_locator": FILM_LOCATOR}]})
        self.local, self.local_pin = self._make_local()
        self.library, self.library_pin = self._make_library()
        self._make_source_packet()

    def _json(self, relative: str, value):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")), encoding="utf-8")

    def _make_local(self):
        image = "./licensed-artwork/synthetic-film-still.png"
        image_file = self.root / "explorer/licensed-artwork/synthetic-film-still.png"
        image_file.parent.mkdir(parents=True, exist_ok=True)
        image_file.write_bytes(PNG)
        item = {"row_id": FILM_ID, "source_locator": FILM_LOCATOR, "image_path": image,
                "image_sha256": digest(PNG), "alt_text": "Synthetic fixture image, not licensed Trek artwork",
                "rights_status": "PUBLIC_DISPLAY_PERMISSION_VERIFIED", "artwork_kind": "PUBLICITY_STILL",
                "attribution_text": "Synthetic image fixture, independent credit example",
                "attribution_url": RIGHTS_URL}
        receipt = {"schema_version": "1.0.0", "review_status": "INDEPENDENT_SOURCE_AND_RIGHTS_REVIEW",
                   "row_id": FILM_ID, "source_locator": FILM_LOCATOR, "image_path": image,
                   "image_sha256": digest(PNG), "rights_page_snapshot_sha256": digest(b"synthetic rights snapshot"),
                   "rights_evidence_url": RIGHTS_REV, "license_identifier": "PD-US-no-notice",
                   "artwork_kind": item["artwork_kind"], "attribution_text": item["attribution_text"],
                   "attribution_url": RIGHTS_URL, "rights_reviewer": "fixture-rights-reviewer",
                   "source_reviewer": "fixture-source-reviewer", "reviewed_on": "2026-11-03"}
        receipt_path = "registry/artwork-rights-receipts/synthetic-film.json"
        self._json(receipt_path, receipt)
        receipt_hash = digest((self.root / receipt_path).read_bytes())
        item["rights_receipt_sha256"] = receipt_hash
        pin = {**item, "rights_receipt_path": receipt_path,
               "rights_page_snapshot_sha256": receipt["rights_page_snapshot_sha256"],
               "rights_evidence_url": RIGHTS_REV, "license_identifier": "PD-US-no-notice"}
        return item, pin

    def _make_library(self):
        item = {"row_id": BOOK_ID, "provider": "OPEN_LIBRARY_COVERS_API", "cover_id": 13083310,
                "isbn": ISBN, "image_size": "M", "alt_text": "Synthetic Open Library edition fixture",
                "source_locator": BOOK_LOCATOR,
                "rights_status": "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED",
                "edition_metadata_sha256": digest(b"synthetic Open Library edition metadata"),
                "attribution_url": f"https://openlibrary.org/isbn/{ISBN}"}
        metadata_locator = "https://openlibrary.org/books/OL28813033M.json"
        preview_sha = digest(b"synthetic inspected front-jacket bytes")
        medium_sha = digest(b"synthetic medium jacket preview bytes")
        medium_tuple = {
            "medium_preview_sha256": medium_sha, "medium_preview_bytes": 12800,
            "medium_preview_width": 180, "medium_preview_height": 273,
            "medium_preview_mime": "image/jpeg",
            "medium_preview_locator": "https://covers.openlibrary.org/b/id/13083310-M.jpg?default=false",
            "medium_provider_doc_url": "https://openlibrary.org/dev/docs/api/covers",
        }
        receipt = {"schema_version": "1.1.0", "review_status": "INDEPENDENT_EDITION_CROSSWALK_REVIEW",
                   "row_id": BOOK_ID, "source_locator": BOOK_LOCATOR, "isbn": ISBN,
                   "cover_id": item["cover_id"], "edition_metadata_sha256": item["edition_metadata_sha256"],
                   "edition_metadata_locator": metadata_locator,
                   "edition_reviewer": "fixture-edition-reviewer", "source_reviewer": "fixture-source-reviewer",
                   "image_reviewer": "fixture-image-reviewer", "image_preview_sha256": preview_sha,
                   "image_review_status": "COVER_IMAGE_VISUALLY_REVIEWED",
                   "image_review_observation": "Synthetic fixture: a front jacket, not an interior title page",
                   "reviewed_on": "2026-11-03", "image_size": "M", **medium_tuple,
                   "medium_visual_reviewer": "fixture-medium-reviewer",
                   "medium_visual_status": "COVER_IMAGE_VISUALLY_REVIEWED",
                   "medium_visual_observation": "Synthetic medium image has the same title jacket and is not an inside page",
                   "medium_reviewed_on": "2026-11-03"}
        receipt_path = "registry/artwork-edition-receipts/synthetic-kirk.json"
        self._json(receipt_path, receipt)
        pin = {**item, "edition_metadata_locator": metadata_locator,
               "image_preview_sha256": preview_sha, **medium_tuple,
               "edition_review_receipt_path": receipt_path,
               "edition_review_receipt_sha256": digest((self.root / receipt_path).read_bytes())}
        return item, pin

    def _make_source_packet(self):
        """Proposal lineage is separately required; the proposal is never an art license."""
        publisher_file = "proposals/librarian/synthetic-edition/records.json"
        self._json(publisher_file, {"synthetic_publisher_source": True})
        self._json(art.OL_SOURCE_PACKET, {
            "data_status": "PROPOSAL_ONLY_INDEPENDENT_ARTWORK_REVIEW_REQUIRED",
            "accepted_work_effect": "NONE", "accepted_source_effect": "NONE",
            "accepted_binding_effect": "NONE", "coverage_effect": "NONE",
            "public_artwork_release_effect": "NONE", "image_bytes_committed": False,
            "copyright_status": "UNDERLYING_COVER_COPYRIGHT_UNRESOLVED",
            "source_catalog_path": "explorer/discovery-catalog.json",
            "source_catalog_sha256": digest((self.root / "explorer/discovery-catalog.json").read_bytes()),
            "candidate_count": 1, "held_count": 0, "held": [],
            "candidates": [{
                "row_id": BOOK_ID.removeprefix("directory:"),
                "source_locator": self.library["source_locator"],
                "isbn": ISBN, "cover_id": self.library["cover_id"],
                "edition_metadata_sha256": self.library["edition_metadata_sha256"],
                "attribution_url": self.library["attribution_url"],
                "rights_status": self.library["rights_status"],
                "openlibrary_edition_json_url": self.library_pin["edition_metadata_locator"],
                "release_status": "HELD_FOR_INDEPENDENT_REVIEW",
                "publisher_source_input": publisher_file,
                "publisher_source_sha256": digest((self.root / publisher_file).read_bytes()),
            }],
        })

    def _manifest(self, entries):
        self._json("explorer/artwork-catalog-v1.3.json", {
            "schema_version": "1.3.0", "data_status": "PROVENANCE_REVIEWED_ARTWORK",
            "coverage_effect": "NONE", "rights_policy": "PER_ENTRY_DISPLAY_GATE",
            "artwork_count": len(entries), "artwork": entries})

    def _check(self, *, local_pins=None, library_pins=None):
        return art.validate_manifest(self.root, local_pins=local_pins, library_pins=library_pins)

    def test_no_public_artwork_absent_manifest_is_a_safe_404_contract(self):
        # The synthetic image must be removed to model the actual accepted
        # repository, which has no licensed-artwork directory.
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        self.assertEqual(self._check()["status"], "ARTWORK_UNAVAILABLE")
        art.check_static_startup(self.root)

    def test_unreviewed_v13_sidecar_rejected_by_strict_schema_and_symlink_gate(self):
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        self._json("explorer/artwork-catalog-v1.3.json", {
            "schema_version": "1.3.0", "artwork_count": 0, "artwork": []})
        with self.assertRaisesRegex(art.ArtworkRejected, "unexpected or missing keys"):
            self._check()
        (self.root / "explorer/artwork-catalog-v1.3.json").unlink()
        (self.root / "explorer/artwork-catalog-v1.3.json").symlink_to("missing")
        with self.assertRaisesRegex(art.ArtworkRejected, "symlink"):
            self._check()

    def test_synthetic_license_review_receipt_and_actual_bytes_can_be_verified(self):
        self._manifest([self.local])
        report = self._check(local_pins={FILM_ID: self.local_pin})
        self.assertEqual(report["status"], "REVIEWED_ARTWORK_READY_FOR_SEPARATE_UI_RELEASE")
        self.assertEqual(report["coverage_effect"], "NONE")

    def test_synthetic_open_library_crosswalk_can_be_verified_without_mirroring_cover(self):
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        self._manifest([self.library])
        self.assertEqual(self._check(library_pins={BOOK_ID: self.library_pin})["artwork_count"], 1)

    def test_local_rights_receipts_stay_empty_and_sidecar_cannot_self_certify(self):
        self._manifest([self.local])
        self.assertEqual(art.REVIEWED_LOCAL_ARTWORK_PINS, {})
        with self.assertRaisesRegex(art.ArtworkRejected, "separately reviewed"):
            self._check()

    def test_open_library_cannot_self_certify_a_credible_isbn_cover_and_hash(self):
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        self._manifest([self.library])
        with self.assertRaisesRegex(art.ArtworkRejected, "not independently pinned"):
            self._check()

    def test_four_reviewed_autobiography_covers_only_and_title_page_explicitly_held(self):
        exact = {
            "directory:literature:prh-autobiography-kirk": 13083310,
            "directory:literature:prh-autobiography-picard": 10694457,
            "directory:literature:prh-autobiography-janeway": 12097815,
            "directory:literature:prh-autobiography-spock": 11945787,
        }
        self.assertEqual({k: v["cover_id"] for k, v in art.REVIEWED_OPEN_LIBRARY_COVER_PINS.items()}, exact)
        self.assertNotIn(12857937, [pin["cover_id"] for pin in art.REVIEWED_OPEN_LIBRARY_COVER_PINS.values()])
        self.assertEqual(art.validate_manifest(ROOT)["artwork_count"], 4)

    def test_medium_candidate_preserves_immutable_v12_fallback_and_exact_row_crosswalk(self):
        v12 = ROOT / art.LEGACY_MANIFEST
        v13 = ROOT / art.MANIFEST
        self.assertEqual(digest(v12.read_bytes()), art.LEGACY_MANIFEST_SHA256)
        old = json.loads(v12.read_text())
        medium = json.loads(v13.read_text())
        self.assertEqual(old["schema_version"], "1.2.0")
        self.assertEqual(medium["schema_version"], "1.3.0")
        self.assertEqual(old["artwork"], [
            {k: v for k, v in item.items() if k != "image_size"} for item in medium["artwork"]])
        self.assertTrue(all(item["image_size"] == "M" for item in medium["artwork"]))

    def test_medium_sidecar_rejects_missing_duplicate_reordered_and_small_substitutions(self):
        # A synthetic mixed batch probes the v1.2/v1.3 pair and its order,
        # including a mutation that keeps the public v1.2 projection identical.
        legacy_art = [self.local, {k: v for k, v in self.library.items() if k != "image_size"}]
        legacy = {
            "schema_version": "1.2.0", "data_status": "PROVENANCE_REVIEWED_ARTWORK",
            "coverage_effect": "NONE", "rights_policy": "PER_ENTRY_DISPLAY_GATE",
            "artwork_count": 2, "artwork": legacy_art,
        }
        self._json(art.LEGACY_MANIFEST, legacy)
        self._manifest([self.local, self.library])
        self.assertEqual(self._check(local_pins={FILM_ID: self.local_pin},
                                     library_pins={BOOK_ID: self.library_pin})["artwork_count"], 2)

        attacks = (
            ("dropped", [self.local], "v1.3 medium sidecar diverges"),
            ("duplicate", [self.local, self.library, self.library], "v1.3 medium sidecar diverges"),
            ("reordered", [self.library, self.local], "v1.3 medium sidecar diverges"),
            ("small rendition", [self.local, {**self.library, "image_size": "S"}],
             "not independently pinned"),
            ("cover ID replacement", [self.local, {**self.library, "cover_id": 999}],
             "v1.3 medium sidecar diverges"),
        )
        for label, entries, message in attacks:
            with self.subTest(label=label):
                self._manifest(entries)
                with self.assertRaisesRegex(art.ArtworkRejected, message):
                    self._check(local_pins={FILM_ID: self.local_pin},
                                library_pins={BOOK_ID: self.library_pin})

        # The *real* release gate pins the old S fallback by exact file SHA,
        # not merely semantic JSON equality. Reproduce the project-root check
        # on this synthetic copy and ensure a whitespace-only change fails.
        self._manifest([self.local, self.library])
        legacy_file = self.root / art.LEGACY_MANIFEST
        baseline_sha = digest(legacy_file.read_bytes())
        legacy_file.write_bytes(legacy_file.read_bytes() + b"\n")
        with patch.object(art, "ROOT", self.root), patch.object(
                art, "LEGACY_MANIFEST_SHA256", baseline_sha):
            with self.assertRaisesRegex(art.ArtworkRejected, "previously published v1.2 artwork bytes"):
                self._check(local_pins={FILM_ID: self.local_pin},
                            library_pins={BOOK_ID: self.library_pin})

    def test_malicious_medium_sidecar_may_not_replace_or_mutate_old_small_fallback(self):
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        self._manifest([self.library])
        self._json("explorer/artwork-catalog.json", {
            "schema_version": "1.2.0", "data_status": "PROVENANCE_REVIEWED_ARTWORK",
            "coverage_effect": "NONE", "rights_policy": "PER_ENTRY_DISPLAY_GATE",
            "artwork_count": 1, "artwork": [
                {k: (9 if k == "cover_id" else v) for k, v in self.library.items() if k != "image_size"}]})
        with self.assertRaisesRegex(art.ArtworkRejected, "v1.3 medium sidecar diverges"):
            self._check(library_pins={BOOK_ID: self.library_pin})

    def test_valid_edition_metadata_and_image_digest_do_not_certify_title_page_as_cover(self):
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        self._manifest([self.library])
        receipt_path = self.root / self.library_pin["edition_review_receipt_path"]
        receipt = json.loads(receipt_path.read_text())
        # A perfect ISBN, cover ID, JSON hash, HTTP 200 and JPEG digest can
        # identify an *interior title page*. Human visual review is separate.
        receipt["image_review_status"] = "IMAGE_VISUALLY_REJECTED_TITLE_PAGE"
        receipt["image_review_observation"] = "Synthetic interior title page, not a cover"
        self._json(self.library_pin["edition_review_receipt_path"], receipt)
        pin = {**self.library_pin, "edition_review_receipt_sha256": digest(receipt_path.read_bytes())}
        with self.assertRaisesRegex(art.ArtworkRejected, "cover image not independently visually reviewed"):
            self._check(library_pins={BOOK_ID: pin})

    def test_open_library_requires_exact_independently_pinned_visual_preview_digest(self):
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        self._manifest([self.library])
        forged_pin = {**self.library_pin, "image_preview_sha256": "f" * 64}
        with self.assertRaisesRegex(art.ArtworkRejected, "review receipt diverges"):
            self._check(library_pins={BOOK_ID: forged_pin})

    def test_medium_size_cannot_be_downgraded_or_claimed_by_sidecar(self):
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        for illegal in ("S", "L", "XL", None):
            with self.subTest(illegal=illegal):
                self._manifest([{**self.library, "image_size": illegal}])
                with self.assertRaisesRegex(art.ArtworkRejected, "not independently pinned"):
                    self._check(library_pins={BOOK_ID: self.library_pin})

    def test_medium_provider_image_digest_dimensions_and_url_are_code_pinned(self):
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        self._manifest([self.library])
        attacks = (
            ("medium_preview_sha256", "f" * 64, "review receipt diverges"),
            ("medium_preview_bytes", 12500, "review receipt diverges"),
            ("medium_preview_width", 38, "medium rendition"),
            ("medium_preview_height", 600, "medium rendition"),
            ("medium_preview_mime", "image/svg+xml", "medium rendition"),
            ("medium_preview_locator", "https://covers.openlibrary.org/b/id/9-S.jpg?default=false",
             "medium rendition"),
            ("medium_provider_doc_url", "https://evil.invalid/cover-policy", "medium rendition"),
        )
        for key, changed, message in attacks:
            with self.subTest(key=key):
                pin = {**self.library_pin, key: changed}
                with self.assertRaisesRegex(art.ArtworkRejected, message):
                    self._check(library_pins={BOOK_ID: pin})

    def test_medium_cover_requires_separate_visual_review_not_just_http200(self):
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        self._manifest([self.library])
        receipt_path = self.root / self.library_pin["edition_review_receipt_path"]
        receipt = json.loads(receipt_path.read_text())
        receipt["medium_visual_status"] = "IMAGE_VISUALLY_REJECTED_TITLE_PAGE"
        self._json(self.library_pin["edition_review_receipt_path"], receipt)
        pin = {**self.library_pin, "edition_review_receipt_sha256": digest(receipt_path.read_bytes())}
        with self.assertRaisesRegex(art.ArtworkRejected, "medium jacket not independently inspected"):
            self._check(library_pins={BOOK_ID: pin})

    def test_local_path_hash_media_rights_and_source_attacks_fail_closed(self):
        attacks = [
            ("remote hotlink", lambda x: x.update(image_path="https://covers.openlibrary.org/b/id/1-S.jpg")),
            ("traversal", lambda x: x.update(image_path="./licensed-artwork/../private.png")),
            ("data URL", lambda x: x.update(image_path="data:image/png;base64,AAAA")),
            ("scriptable SVG", lambda x: x.update(image_path="./licensed-artwork/untrusted.svg")),
            ("forged image SHA", lambda x: x.update(image_sha256="0" * 64)),
            ("forged rights receipt SHA", lambda x: x.update(rights_receipt_sha256="f" * 64)),
            ("wrong source locator", lambda x: x.update(source_locator="https://www.startrek.com@evil.invalid/")),
            ("spoofed license", lambda x: x.update(rights_status="CLAIMED_PUBLIC_DOMAIN")),
            ("false credit", lambda x: x.update(attribution_text="Copyright owned by attacker")),
            ("offsite credit", lambda x: x.update(attribution_url="https://evil.invalid/stolen")),
            ("misclassified kind", lambda x: x.update(artwork_kind="COVER")),
            ("inject accepted coverage", lambda x: x.update(coverage_effect="ACCEPTED")),
            ("unknown row", lambda x: x.update(row_id="film:other")),
        ]
        for label, alter in attacks:
            with self.subTest(attack=label):
                item = copy.deepcopy(self.local)
                alter(item)
                self._manifest([item])
                with self.assertRaises(art.ArtworkRejected):
                    self._check(local_pins={FILM_ID: self.local_pin})

    def test_actual_byte_drift_and_unsupported_media_rejected_even_with_matching_string_pin(self):
        self._manifest([self.local])
        image = self.root / "explorer/licensed-artwork/synthetic-film-still.png"
        image.write_bytes(PNG + b"trailing tamper")
        with self.assertRaisesRegex(art.ArtworkRejected, "digest"):
            self._check(local_pins={FILM_ID: self.local_pin})
        image.write_bytes(b"<svg onload='fetch(\"https://evil.invalid\")'></svg>")
        with self.assertRaisesRegex(art.ArtworkRejected, "media type"):
            self._check(local_pins={FILM_ID: self.local_pin})

    def test_missing_mutated_or_recredited_review_receipt_rejected(self):
        self._manifest([self.local])
        receipt = self.root / self.local_pin["rights_receipt_path"]
        original = receipt.read_bytes()
        receipt.write_bytes(original.replace(b"fixture-rights-reviewer", b"forged-rights-actor"))
        with self.assertRaisesRegex(art.ArtworkRejected, "receipt SHA-256"):
            self._check(local_pins={FILM_ID: self.local_pin})
        receipt.unlink()
        with self.assertRaises(art.ArtworkRejected):
            self._check(local_pins={FILM_ID: self.local_pin})

    def test_unlisted_art_and_duplicate_artwork_rows_rejected(self):
        self._manifest([self.local])
        (self.root / "explorer/licensed-artwork/unreviewed.webp").write_bytes(b"RIFF00WEBP")
        with self.assertRaisesRegex(art.ArtworkRejected, "unlisted"):
            self._check(local_pins={FILM_ID: self.local_pin})
        (self.root / "explorer/licensed-artwork/unreviewed.webp").unlink()
        self._manifest([self.local, copy.deepcopy(self.local)])
        with self.assertRaisesRegex(art.ArtworkRejected, "duplicate artwork"):
            self._check(local_pins={FILM_ID: self.local_pin})

    def test_symlink_image_cannot_launder_unreviewed_bytes(self):
        self._manifest([self.local])
        image = self.root / "explorer/licensed-artwork/synthetic-film-still.png"
        image.unlink()
        try:
            image.symlink_to(self.root / "explorer/app.css")
        except OSError:
            self.skipTest("symlink creation unavailable")
        with self.assertRaisesRegex(art.ArtworkRejected, "symlink"):
            self._check(local_pins={FILM_ID: self.local_pin})

    def test_missing_manifest_with_orphaned_images_is_rejected(self):
        with self.assertRaisesRegex(art.ArtworkRejected, "orphaned"):
            self._check()

    def test_manifest_duplicate_key_and_false_count_fail_closed(self):
        self._manifest([self.local])
        path = self.root / art.MANIFEST
        path.write_text(path.read_text().replace('"artwork_count":1', '"artwork_count":1,"artwork_count":1'))
        with self.assertRaisesRegex(art.ArtworkRejected, "duplicate JSON key"):
            self._check(local_pins={FILM_ID: self.local_pin})
        self._manifest([self.local])
        path.write_text(path.read_text().replace('"artwork_count":1', '"artwork_count":100'))
        with self.assertRaisesRegex(art.ArtworkRejected, "envelope"):
            self._check(local_pins={FILM_ID: self.local_pin})

    def test_open_library_cross_row_isbn_and_source_spoofing_fail_even_with_review_pin(self):
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        attacks = [
            ("wrong edition", {"isbn": "9781785659409", "attribution_url": "https://openlibrary.org/isbn/9781785659409"}),
            ("wrong cover", {"cover_id": 99999}),
            ("wrong metadata", {"edition_metadata_sha256": "0" * 64}),
            ("fake right", {"rights_status": "PUBLIC_DOMAIN"}),
            ("hotlink", {"attribution_url": "https://evil.invalid/ISBN"}),
            ("wrong source", {"source_locator": FILM_LOCATOR}),
            ("wrong row", {"row_id": FILM_ID}),
        ]
        for label, changes in attacks:
            with self.subTest(attack=label):
                item = {**self.library, **changes}
                self._manifest([item])
                with self.assertRaises(art.ArtworkRejected):
                    self._check(library_pins={BOOK_ID: self.library_pin})

    def test_open_library_crosswalk_fails_on_absent_edition_and_mismatched_publisher_url(self):
        shutil.rmtree(self.root / "explorer/licensed-artwork")
        self._manifest([self.library])
        catalog = self.root / "explorer/discovery-catalog.json"
        source = json.loads(catalog.read_text())
        source["rows"][0]["details"] = ["Paperback ISBN 9781785659409"]
        self._json("explorer/discovery-catalog.json", source)
        packet = json.loads((self.root / art.OL_SOURCE_PACKET).read_text())
        packet["source_catalog_sha256"] = digest(catalog.read_bytes())
        self._json(art.OL_SOURCE_PACKET, packet)
        with self.assertRaisesRegex(art.ArtworkRejected, "not in publisher"):
            self._check(library_pins={BOOK_ID: self.library_pin})
        source["rows"][0]["details"] = [f"Paperback ISBN {ISBN}"]
        source["rows"][0]["source_group"] = "publisher:simonandschuster.com"
        self._json("explorer/discovery-catalog.json", source)
        packet["source_catalog_sha256"] = digest(catalog.read_bytes())
        self._json(art.OL_SOURCE_PACKET, packet)
        with self.assertRaisesRegex(art.ArtworkRejected, "URL does not identify"):
            self._check(library_pins={BOOK_ID: self.library_pin})

    def test_css_remote_url_import_image_set_and_escape_are_pre_opt_in_rejections(self):
        art.check_css_no_pre_opt_in_network(".x{background:url('./art-original-episode.svg')}")
        for film_id in (
            "film-2009", "film-beyond", "film-final-frontier", "film-first-contact",
            "film-generations", "film-insurrection", "film-into-darkness",
            "film-motion-picture", "film-nemesis", "film-search-for-spock",
            "film-section-31", "film-undiscovered-country", "film-voyage-home",
            "film-wrath-of-khan",
        ):
            art.check_css_no_pre_opt_in_network(
                f".x{{background:url('./interpretive-film/{film_id}.svg')}}"
            )
        with self.assertRaises(art.ArtworkRejected):
            art.check_css_no_pre_opt_in_network(
                ".x{background:url('./interpretive-film/film-fake.svg')}"
            )
        for css in (
            ".x{background:url('https://covers.openlibrary.org/b/id/123-S.jpg')}",
            ".x{background:url(//covers.openlibrary.org/b/id/123-S.jpg)}",
            "@import url('https://example.invalid/a.css');",
            ".x{background:image-set('https://covers.openlibrary.org/b/id/1-S.jpg')}",
            ".x{background:u\\72l(https://covers.openlibrary.org/b/id/1-S.jpg)}",
            ".x{background:url/*comment*/('https://covers.openlibrary.org/b/id/1-S.jpg')}",
        ):
            with self.subTest(css=css), self.assertRaises(art.ArtworkRejected):
                art.check_css_no_pre_opt_in_network(css)

    def test_html_external_startup_resources_and_inline_css_are_pre_opt_in_rejections(self):
        for bad in (
            '<img src="https://covers.openlibrary.org/b/id/123-S.jpg">',
            '<link rel="preload" as="image" href="https://covers.openlibrary.org/b/id/123-S.jpg">',
            '<style>.x{background:url(https://covers.openlibrary.org/b/id/123-S.jpg)}</style>',
            '<div style="background:url(https://covers.openlibrary.org/b/id/123-S.jpg)"></div>',
            '<svg><image href="https://covers.openlibrary.org/b/id/123-S.jpg"/></svg>',
        ):
            with self.subTest(tag=bad):
                html = (ROOT / "explorer/index.html").read_text()
                (self.root / "explorer/index.html").write_text(html.replace("</body>", bad + "</body>"))
                with self.assertRaises(art.ArtworkRejected):
                    art.check_static_startup(self.root)

    def test_first_party_hero_cannot_be_laundered_as_episode_screenshot(self):
        # Literal-compliance falsifier: the current startup allowlist admits
        # the hero URL anywhere, regardless of how the image is described.
        html = (ROOT / "explorer/index.html").read_text()
        hero_start = html.index('<img class="masthead-art"')
        hero_end = html.index('>', hero_start) + 1
        hero = html[hero_start:hero_end]
        fake_episode = hero.replace('class="masthead-art"', 'class="episode-screenshot"').replace(
            'alt="Panoramic starship bridge facing a luminous celestial navigation chart"',
            'alt="Official episode screenshot"')
        for attack in (
            html.replace('</body>', f'<article class="episode-card">{hero}</article></body>'),
            html.replace(hero, '').replace('</body>',
                f'<article class="episode-card">{fake_episode}</article></body>'),
            # Hostile QA: exact permitted hero under a forged episode card,
            # nested *within* masthead, defeated the boolean in_masthead gate.
            html.replace(hero, '<article class="episode-card"><h2>Official episode screenshot</h2>'
                         + hero + '</article>'),
        ):
            with self.subTest(attack=attack[-300:]):
                (self.root / "explorer/index.html").write_text(attack)
                with self.assertRaisesRegex(art.ArtworkRejected, "masthead|hero"):
                    art.check_static_startup(self.root)
        shutil.copyfile(ROOT / "explorer/index.html", self.root / "explorer/index.html")
        art.check_static_startup(self.root)

    def test_masthead_cannot_be_reparented_inside_any_forged_media_card(self):
        # Independent hostile QA found that direct-child hero checks alone
        # accepted an <article> wrapping the *whole* legitimate masthead.
        # Exercise several ancestor labels/HTML container types so the gate
        # enforces actual parentage, not a class-name blacklist.
        html = (ROOT / "explorer/index.html").read_text()
        start = html.index('<header class="masthead">')
        end = html.index('</header>', start) + len('</header>')
        masthead = html[start:end]
        wrappers = (
            ('article', 'episode-card'),
            ('article', 'film-card'),
            ('div', 'episode-screenshot'),
            ('div', 'unrecognized-image-host'),
            ('section', 'publisher-cover'),
            ('aside', 'visual-gallery'),
            ('figure', 'artwork-frame'),
            ('main', 'masquerade'),
        )
        for tag, kind in wrappers:
            with self.subTest(parent=tag, class_name=kind):
                attack = (f'<{tag} class="{kind}">'
                          '<h2>Official episode screenshot</h2>'
                          + masthead + f'</{tag}>')
                (self.root / "explorer/index.html").write_text(
                    html.replace(masthead, attack, 1))
                with self.assertRaisesRegex(art.ArtworkRejected, "masthead|body"):
                    art.check_static_startup(self.root)
        shutil.copyfile(ROOT / "explorer/index.html", self.root / "explorer/index.html")
        art.check_static_startup(self.root)

    def test_svg_descendant_href_cannot_fetch_or_launder_remote_art_before_opt_in(self):
        # A clean outer <svg> is not evidence that nested SVG tags are inert.
        # SVG <textPath> and <a> can carry external href references.
        for bad in (
            '<svg><textPath href="https://covers.openlibrary.org/b/id/13083310-S.jpg">x</textPath></svg>',
            '<svg><g><textPath xlink:href="https://covers.openlibrary.org/b/id/13083310-S.jpg">x</textPath></g></svg>',
            '<svg><a href="https://covers.openlibrary.org/b/id/13083310-S.jpg"><path d="M1 2"/></a></svg>',
            '<svg><g><a xlink:href="https://covers.openlibrary.org/b/id/13083310-S.jpg">x</a></g></svg>',
            '<svg><g><textPath href="./art-original-episode.svg">x</textPath></g></svg>',
        ):
            with self.subTest(svg=bad):
                html = (ROOT / "explorer/index.html").read_text()
                (self.root / "explorer/index.html").write_text(html.replace("</body>", bad + "</body>"))
                with self.assertRaisesRegex(art.ArtworkRejected, "SVG descendant external"):
                    art.check_static_startup(self.root)
        # Existing decorative, href-free Starfleet mark stays admitted.
        shutil.copyfile(ROOT / "explorer/index.html", self.root / "explorer/index.html")
        art.check_static_startup(self.root)

    def test_svg_presentation_url_attributes_cannot_fetch_art_before_opt_in(self):
        remote = "https://covers.openlibrary.org/b/id/13083310-S.jpg"
        for attr in ("fill", "stroke", "mask", "clip-path", "filter", "marker-start",
                     "marker-mid", "marker-end", "cursor", "shape-outside"):
            with self.subTest(attribute=attr):
                payload = f'<svg><path {attr}="url({remote})" d="M1 2"/></svg>'
                html = (ROOT / "explorer/index.html").read_text()
                (self.root / "explorer/index.html").write_text(
                    html.replace("</body>", payload + "</body>"))
                with self.assertRaisesRegex(art.ArtworkRejected, "SVG attribute resource"):
                    art.check_static_startup(self.root)
        for payload in (
            '<svg fill="url(https://covers.openlibrary.org/b/id/1-S.jpg)"></svg>',
            '<svg><path fill="&#117;rl(&#104;ttps://covers.openlibrary.org/b/id/1-S.jpg)"/></svg>',
            '<svg><path fill="u\\72l(https://covers.openlibrary.org/b/id/1-S.jpg)"/></svg>',
            '<svg><path fill="url(./art-original-episode.svg)"/></svg>',
            '<svg><path fill="image-set(https://covers.openlibrary.org/b/id/1-S.jpg)"/></svg>',
            '<svg><path fill="u/**/rl(https://covers.openlibrary.org/b/id/1-S.jpg)"/></svg>',
        ):
            with self.subTest(payload=payload):
                html = (ROOT / "explorer/index.html").read_text()
                (self.root / "explorer/index.html").write_text(
                    html.replace("</body>", payload + "</body>"))
                with self.assertRaisesRegex(art.ArtworkRejected, "SVG attribute resource"):
                    art.check_static_startup(self.root)
        shutil.copyfile(ROOT / "explorer/index.html", self.root / "explorer/index.html")
        art.check_static_startup(self.root)

    def test_page_css_remote_art_is_blocked_by_the_actual_startup_artifact_gate(self):
        css_file = self.root / "explorer/app.css"
        css_file.write_text(css_file.read_text() +
                            "\n.card{background-image:url(https://covers.openlibrary.org/b/id/13083310-S.jpg)}")
        with self.assertRaisesRegex(art.ArtworkRejected, "pre-opt-in"):
            art.check_static_startup(self.root)


if __name__ == "__main__":
    unittest.main()
