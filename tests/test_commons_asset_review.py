"""Rights/edition/film and no-hotlink guards for an offline visual review deck."""

import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "proposals/librarian/commons-asset-review-20261103"
SPEC = importlib.util.spec_from_file_location("commons_asset_candidate_validation", FOLDER / "validate.py")
candidate_validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(candidate_validator)


class CommonsAssetReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads((FOLDER / "records.json").read_text(encoding="utf-8"))
        cls.catalog = json.loads((ROOT / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))

    def rejected(self, mutation):
        packet = copy.deepcopy(self.records)
        mutation(packet)
        with self.assertRaises(ValueError):
            candidate_validator.validate(packet, self.catalog, FOLDER)

    def test_pinned_current_packet_and_no_image_release(self):
        candidate_validator.validate(self.records, self.catalog, FOLDER)
        self.assertFalse(self.records["public_display_authorized"])
        self.assertFalse(self.records["artwork_binary_present"])
        self.assertTrue(all(self.records[k]["image_url"] is None for k in
                            ("commons_photo_candidate", "edition_cover_candidate", "film_thumbnail_candidate")))
        self.assertEqual(candidate_validator.main([]), 0)

    def test_all_release_promotions_and_hotlinks_rejected(self):
        for field, value in (("source_effect", "SOURCE_BOUND"), ("work_effect", "ADMITTED"),
                             ("evidence_effect", "ACCEPTED"), ("coverage_effect", "CLOSE_READ"),
                             ("site_release_effect", "PUBLIC"), ("public_display_authorized", True),
                             ("artwork_binary_present", True), ("remote_artwork_url_present", True)):
            with self.subTest(field=field):
                self.rejected(lambda p: p.__setitem__(field, value))
        for section in ("commons_photo_candidate", "edition_cover_candidate", "film_thumbnail_candidate"):
            with self.subTest(section=section):
                self.rejected(lambda p: p[section].__setitem__(
                    "image_url", "https://upload.wikimedia.org/forbidden-preview.jpg"))

    def test_forged_commons_license_and_asset_hash_rejected(self):
        changes = (("author", "Paramount"), ("file_page_license_claim", "PUBLIC DOMAIN"),
                   ("license_url", "https://example.invalid/license"),
                   ("commons_reported_file_sha1", "0" * 40),
                   ("commons_reported_byte_count", 0),
                   ("underlying_fictional_prop_design_and_brand_rights", "CLEARED"),
                   ("public_display_decision", "APPROVED"),
                   ("asset_path", "./licensed-artwork/file.jpg"),
                   ("asset_sha256", "0" * 64),
                   ("license_verified", True))
        for field, value in changes:
            with self.subTest(field=field):
                self.rejected(lambda p: p["commons_photo_candidate"].__setitem__(field, value))

    def test_wrong_book_edition_and_film_source_rejected(self):
        for section, field, value in (
            ("edition_cover_candidate", "isbn13", "9781668095904"),
            ("edition_cover_candidate", "row_id", "literature:prh-autobiography-kirk"),
            ("edition_cover_candidate", "official_product_page", "https://www.simonandschuster.com/elsewhere"),
            ("edition_cover_candidate", "public_display_decision", "APPROVED"),
            ("film_thumbnail_candidate", "row_id", "film:film-motion-picture"),
            ("film_thumbnail_candidate", "official_film_page", "https://www.startrek.com/movies/star-trek-i-the-motion-picture"),
            ("film_thumbnail_candidate", "independent_image_license", "FAIR_USE_GRANTED"),
        ):
            with self.subTest(section=section, field=field):
                self.rejected(lambda p: p[section].__setitem__(field, value))

    def test_synthetic_binary_in_review_packet_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "forged.jpg").write_bytes(b"not an image")
            with self.assertRaisesRegex(ValueError, "contains media bytes"):
                candidate_validator.validate(self.records, self.catalog, folder)

    def test_offline_preview_contains_license_links_without_media_fetch(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "review.html"
            call = subprocess.run([sys.executable, str(FOLDER / "render_preview.py"),
                                   "--output", str(output)], cwd=ROOT,
                                  capture_output=True, text=True)
            self.assertEqual(call.returncode, 0, call.stderr)
            html = output.read_text(encoding="utf-8")
            self.assertIn("VISUAL HELD", html)
            self.assertIn("Joe Ross", html)
            self.assertIn("CC BY-SA 2.0", html)
            self.assertIn("9781668095898", html)
            self.assertIn("Wrath of Khan", html)
            self.assertIn("img-src 'none'", html)
            self.assertNotRegex(html, r"(?i)<\s*(?:img|iframe|script|video|audio|picture|source)\b")
            self.assertNotRegex(html, r"(?i)\b(?:src|srcset)\s*=")
            self.assertNotRegex(html, r"(?i)(?:url\s*\(|@import|<\s*base\b)")
            self.assertEqual(len(re.findall(r'<a\s+href="https://', html)), 5)
            self.assertIn("Commons file and license page", html)
            self.assertNotIn(".jpg?", html)  # no direct CDN image request

    def test_preview_refuses_overwrite_and_repo_path(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "exists.html"
            output.write_text("User data must survive")
            call = subprocess.run([sys.executable, str(FOLDER / "render_preview.py"),
                                   "--output", str(output)], cwd=ROOT,
                                  capture_output=True, text=True)
            self.assertNotEqual(call.returncode, 0)
            self.assertEqual(output.read_text(), "User data must survive")
        call = subprocess.run([sys.executable, str(FOLDER / "render_preview.py"),
                               "--output", str(FOLDER / "never-write-preview.html")], cwd=ROOT,
                              capture_output=True, text=True)
        self.assertNotEqual(call.returncode, 0)
        self.assertFalse((FOLDER / "never-write-preview.html").exists())


if __name__ == "__main__":
    unittest.main()
