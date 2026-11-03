"""Synthetic fail-closed OPF-cover inventory tests; no user book data."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import warnings
from zipfile import ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("opf_cover_index", ROOT / "tools" / "index_private_opf_covers.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def package(*, manifest="", meta="", guide="", title="Synthetic Example", opf_namespace=""):
    default_xmlns = f' xmlns="{opf_namespace}"' if opf_namespace else ""
    return (f'''<?xml version="1.0" encoding="UTF-8"?>
<package{default_xmlns} xmlns:dc="http://purl.org/dc/elements/1.1/">
<metadata><dc:title>{title}</dc:title>{meta}</metadata>
<manifest>{manifest}</manifest><guide>{guide}</guide></package>''').encode()


def zip_fixture(path, members):
    with ZipFile(path, "w") as out:
        for name, data in members:
            out.writestr(name, data)


class PrivateCoverIndexTests(unittest.TestCase):
    def test_opf2_meta_cover_link_hashes_only_declared_image(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "sample.zip"
            image = b"\xff\xd8\xff\xe0SYNTHETIC JPEG CONTENT"  # Not a redistributed cover.
            secret = b"PRIVATE STORY BODY MUST NOT BE READ OR OUTPUT"
            opf = package(
                meta='<meta name="cover" content="front"/>',
                manifest='<item id="front" href="images/cover.jpg" media-type="image/jpeg"/>'
                         '<item id="chapter" href="chapter.htm" media-type="text/html"/>',
            )
            zip_fixture(archive, [
                ("opf_books/Book/Book.opf", opf),
                ("opf_books/Book/images/cover.jpg", image),
                ("opf_books/Book/chapter.htm", secret),
            ])
            index = mod.build_cover_index(archive)
            row = index["packages"][0]
            self.assertEqual(row["status"], "EXPLICIT_OPF_REFERENCE_UNVERIFIED")
            self.assertEqual(row["selected_cover_member"], "opf_books/Book/images/cover.jpg")
            self.assertEqual(row["candidates"][0]["image_sha256"], hashlib.sha256(image).hexdigest())
            self.assertEqual(row["candidates"][0]["evidence_basis"], ["OPF2_META_COVER_ID"])
            self.assertEqual(index["summary"]["private_images_hashed"], 1)
            output = json.dumps(index)
            self.assertNotIn(secret.decode(), output)
            self.assertNotIn("SYNTHETIC JPEG CONTENT", output)
            self.assertEqual(index["rights_status"], "PRIVATE_POSSESSION_NOT_PUBLIC_DISPLAY_PERMISSION")
            self.assertEqual(index["coverage_effect"], "NONE")

    def test_opf3_property_and_guide_direct_image_are_explicit(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "sample.zip"
            opf = package(
                manifest='<item id="cover" href="Cover.png" media-type="image/png" properties="cover-image"/>',
                guide='<reference type="cover" href="Cover.png"/>',
                opf_namespace="http://www.idpf.org/2007/opf",
            )
            zip_fixture(archive, [("book/Book.opf", opf),
                                  ("book/Cover.png", b"\x89PNG\r\n\x1a\nSYNTHETIC")])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["status"], "EXPLICIT_OPF_REFERENCE_UNVERIFIED")
            self.assertEqual(row["candidates"][0]["evidence_basis"],
                             ["FILENAME_HINT_ONLY", "OPF3_COVER_IMAGE_PROPERTY", "OPF_GUIDE_DIRECT_IMAGE"])

    def test_forged_item_under_metadata_is_not_an_opf_manifest_cover(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "forged-metadata.zip"
            opf = package(meta='<item id="fake" href="forged.jpg" '
                               'media-type="image/jpeg" properties="cover-image"/>')
            zip_fixture(archive, [("Book/Book.opf", opf),
                                  ("Book/forged.jpg", b"\xff\xd8\xffSYNTHETIC")])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["status"], "NO_DIRECT_IMAGE_COVER_REFERENCE")
            self.assertEqual(row["candidates"], [])
            self.assertIsNone(row["selected_cover_member"])

    def test_unrelated_namespace_item_inside_manifest_is_not_opf_item(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "forged-namespace.zip"
            opf = package(manifest='<x:item xmlns:x="urn:unrelated" id="fake" '
                                   'href="forged.jpg" media-type="image/jpeg" '
                                   'properties="cover-image"/>')
            zip_fixture(archive, [("Book/Book.opf", opf),
                                  ("Book/forged.jpg", b"\xff\xd8\xffSYNTHETIC")])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["status"], "NO_DIRECT_IMAGE_COVER_REFERENCE")
            self.assertEqual(row["candidates"], [])
            self.assertIsNone(row["selected_cover_member"])

    def test_forged_meta_and_guide_reference_in_wrong_sections_are_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "forged-sections.zip"
            opf = package(
                meta='<reference type="cover" href="forged.jpg"/>',
                manifest='<item id="normal" href="forged.jpg" media-type="image/jpeg"/>'
                         '<meta name="cover" content="normal"/>',
                guide='<x:reference xmlns:x="urn:unrelated" type="cover" href="forged.jpg"/>',
            )
            zip_fixture(archive, [("Book/Book.opf", opf),
                                  ("Book/forged.jpg", b"\xff\xd8\xffSYNTHETIC")])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["status"], "NO_DIRECT_IMAGE_COVER_REFERENCE")
            self.assertEqual(row["candidates"], [])

    def test_declared_jpeg_with_non_image_payload_is_held_not_selected(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "forged-image.zip"
            opf = package(manifest='<item id="real" href="forged.jpg" '
                                   'media-type="image/jpeg" properties="cover-image"/>')
            zip_fixture(archive, [("Book/Book.opf", opf),
                                  ("Book/forged.jpg", b"NOT-A-JPEG")])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertIsNone(row["selected_cover_member"])
            self.assertEqual(row["candidates"][0]["asset_status"],
                             "IMAGE_SIGNATURE_MISMATCH_REVIEW")
            self.assertTrue(row["review_holds"])

    def test_jpg_extension_with_png_magic_is_not_a_jpeg_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "wrong-image-type.zip"
            opf = package(manifest='<item id="c" href="cover.jpg" '
                                   'media-type="image/jpeg" properties="cover-image"/>')
            zip_fixture(archive, [("Book/Book.opf", opf),
                                  ("Book/cover.jpg", b"\x89PNG\r\n\x1a\nFAKE")])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["candidates"][0]["asset_status"],
                             "IMAGE_SIGNATURE_MISMATCH_REVIEW")
            self.assertIsNone(row["selected_cover_member"])

    def test_filename_hints_do_not_become_explicit_or_rights_cleared(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "sample.zip"
            zip_fixture(archive, [
                ("books/B/B.opf", package()),
                ("books/B/~Cover02.jpg", b"A"),
                ("books/B/MSRCover.jpg", b"B"),
                ("books/B/image003.jpg", b"C"),
            ])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["status"], "AMBIGUOUS_FILENAME_HINTS")
            self.assertIsNone(row["selected_cover_member"])
            self.assertEqual(len(row["candidates"]), 2)
            self.assertTrue(all(c["evidence_basis"] == ["FILENAME_HINT_ONLY"] for c in row["candidates"]))

    def test_missing_manifest_meta_reference_is_review_hold(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "sample.zip"
            zip_fixture(archive, [("books/B/B.opf", package(meta='<meta name="cover" content="ghost"/>'))])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["status"], "NO_DIRECT_IMAGE_COVER_REFERENCE")
            self.assertIn("OPF meta cover id missing from manifest", row["review_holds"])

    def test_explicit_missing_image_not_filled_from_filename_hint(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "sample.zip"
            zip_fixture(archive, [
                ("books/B/B.opf", package(manifest='<item id="c" href="missing.jpg" properties="cover-image"/>')),
                ("books/B/cover.jpg", b"NOT VERIFIED REPLACEMENT"),
            ])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["status"], "EXPLICIT_OPF_REFERENCE_UNVERIFIED")
            self.assertIsNone(row["selected_cover_member"])
            self.assertTrue(any(c["asset_status"] == "MISSING_REFERENCED_IMAGE" for c in row["candidates"]))
            self.assertTrue(row["review_holds"])

    def test_conflicting_explicit_references_cannot_auto_select(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "sample.zip"
            opf = package(
                meta='<meta name="cover" content="one"/>',
                manifest='<item id="one" href="one.jpg"/>'
                         '<item id="two" href="two.jpg" properties="cover-image"/>',
            )
            zip_fixture(archive, [("B/B.opf", opf), ("B/one.jpg", b"A"), ("B/two.jpg", b"B")])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["status"], "AMBIGUOUS_EXPLICIT_REFERENCES")
            self.assertIsNone(row["selected_cover_member"])

    def test_guide_cover_page_is_not_dereferenced_or_misclassified(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "sample.zip"
            zip_fixture(archive, [
                ("B/B.opf", package(guide='<reference type="cover" href="cover.html"/>')),
                ("B/cover.html", b"PRIVATE HTML BODY"),
            ])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["status"], "NO_DIRECT_IMAGE_COVER_REFERENCE")
            self.assertIn("OPF guide points to cover page/non-image; page not opened", row["review_holds"])
            self.assertNotIn("PRIVATE HTML BODY", json.dumps(row))

    def test_unsafe_member_paths_symlinks_and_collisions_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "unsafe.zip"
            for name in ("../escape/book.opf", "/absolute/book.opf", "book\\b.opf", "C:/book.opf",
                         "book//book.opf", "book/./book.opf"):
                zip_fixture(archive, [(name, package())])
                with self.subTest(name=name), self.assertRaises(mod.CoverIntakeError):
                    mod.build_cover_index(archive)
            link = ZipInfo("books/link.jpg")
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            zip_fixture(archive, [("book.opf", package()), (link, b"/tmp/target")])
            with self.assertRaisesRegex(mod.CoverIntakeError, "symbolic-link"):
                mod.build_cover_index(archive)
            zip_fixture(archive, [("Book/book.opf", package()), ("book/book.opf", package())])
            with self.assertRaisesRegex(mod.CoverIntakeError, "colliding"):
                mod.build_cover_index(archive)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                zip_fixture(archive, [("book.opf", package()), ("book.opf", package())])
            with self.assertRaises(mod.CoverIntakeError):
                mod.build_cover_index(archive)

    def test_malicious_xml_entities_and_unapproved_doctype_held(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "xml.zip"
            for raw in (
                b'<!DOCTYPE package [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><package>&xxe;</package>',
                b'<!DOCTYPE package SYSTEM "http://evil.invalid/x.dtd"><package/>',
                b'\xff\xfe<\x00!\x00D\x00O\x00C\x00T\x00Y\x00P\x00E\x00',
            ):
                zip_fixture(archive, [("books/B.opf", raw)])
                row = mod.build_cover_index(archive)["packages"][0]
                self.assertEqual(row["status"], "REVIEW_REQUIRED")
                self.assertIsNone(row["selected_cover_member"])
                self.assertTrue(row["review_holds"])

    def test_unsafe_cover_href_cannot_read_outside_package(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "href.zip"
            for href in ("../secret.jpg", "/absolute.jpg", "https://evil.invalid/cover.jpg",
                         "%2e%2e/secret.jpg", "sub%2F..%2Fsecret.jpg", "C:/outside.jpg"):
                zip_fixture(archive, [("books/B/B.opf", package(
                    manifest=f'<item id="c" href="{href}" properties="cover-image"/>'))])
                with self.subTest(href=href), self.assertRaises(mod.CoverIntakeError):
                    mod.build_cover_index(archive)

    def test_image_size_and_aggregate_limits(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "size.zip"
            zip_fixture(archive, [("B/B.opf", package(
                manifest='<item id="c" href="cover.jpg" properties="cover-image"/>')),
                ("B/cover.jpg", b"TOO BIG")])
            with mock.patch.object(mod, "MAX_IMAGE_BYTES", 3):
                row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["candidates"][0]["asset_status"], "IMAGE_SIZE_LIMIT_REVIEW")
            self.assertIsNone(row["candidates"][0]["image_sha256"])
            with mock.patch.object(mod, "MAX_TOTAL_IMAGE_BYTES", 3):
                with self.assertRaisesRegex(mod.CoverIntakeError, "aggregate"):
                    mod.build_cover_index(archive)
            with mock.patch.object(mod, "MAX_TOTAL_ARCHIVE_BYTES", 3):
                with self.assertRaisesRegex(mod.CoverIntakeError, "archive uncompressed"):
                    mod.build_cover_index(archive)

    def test_misdeclared_manifest_media_type_is_review_hold_not_cover(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "mime.zip"
            zip_fixture(archive, [
                ("B/B.opf", package(manifest='<item id="c" href="cover.jpg" '
                 'media-type="text/html" properties="cover-image"/>')),
                ("B/cover.jpg", b"NOT PROVEN IMAGE"),
            ])
            row = mod.build_cover_index(archive)["packages"][0]
            self.assertEqual(row["candidates"][0]["asset_status"], "OPF_MEDIA_TYPE_CONFLICT_REVIEW")
            self.assertIsNone(row["selected_cover_member"])
            self.assertTrue(row["review_holds"])

    def test_private_output_refuses_other_git_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            checkout = Path(temp) / "another-repo"
            checkout.mkdir()
            (checkout / ".git").write_text("gitdir: elsewhere", encoding="utf-8")
            with self.assertRaisesRegex(mod.CoverIntakeError, "every Git checkout"):
                mod.private_cover_output_path(checkout / "private-cover-index.json")

    def test_source_swap_during_read_refuses_to_receipt_wrong_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, moved = root / "archive.zip", root / "original-open.zip"
            zip_fixture(source, [("B/B.opf", package()), ("B/cover.jpg", b"FIRST")])
            original = mod.classify_package

            def swap(*args):
                source.rename(moved)
                zip_fixture(source, [("B/B.opf", package(title="Replacement")),
                                     ("B/cover.jpg", b"SECOND")])
                return original(*args)

            with mock.patch.object(mod, "classify_package", side_effect=swap):
                with self.assertRaisesRegex(mod.CoverIntakeError, "source ZIP changed"):
                    mod.build_cover_index(source)

    def test_private_cli_owner_only_no_overwrite_or_public_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive, out = root / "books.zip", root / "private.json"
            zip_fixture(archive, [("B/B.opf", package()), ("B/cover.jpg", b"IMG")])
            cmd = [sys.executable, str(ROOT / "tools" / "index_private_opf_covers.py"),
                   "--opf-zip", str(archive), "--out", str(out)]
            first = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o600)
            self.assertNotIn("B/B.opf", first.stdout, "private paths must not leak into logs")
            contents = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(contents["proposal_only"])
            self.assertEqual(contents["public_artwork_release_effect"], "NONE")
            second = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("overwrite", second.stderr)
            bad = subprocess.run(cmd[:-1] + [str(ROOT / "private-report.json")],
                                 capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("outside the public repo", bad.stderr)


if __name__ == "__main__":
    unittest.main()
