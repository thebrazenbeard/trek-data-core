"""Offline rights and ZIP/XML safety tests for private OPF metadata intake."""

from __future__ import annotations

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
from zipfile import ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("opf_intake", ROOT / "tools" / "inventory_opf_metadata.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def package(*, namespace="http://purl.org/dc/elements/1.1/", legacy_unbound=False):
    xmlns = "" if legacy_unbound else f' xmlns:dc="{namespace}"'
    return (f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE package PUBLIC "+//ISBN 0-9673008-1-9//DTD OEB 1.0.1 Package//EN" "http://openebook.org/dtds/oeb-1.0.1/oebpkg101.dtd">
<package><metadata><dc-metadata{xmlns}>
<dc:Title>Sample &amp; Test</dc:Title><dc:Creator>Author A</dc:Creator>
<dc:Identifier scheme="ISBN">978-1-2345</dc:Identifier>
<dc:Description>Private copyrighted description MUST NEVER EXPORT.</dc:Description>
</dc-metadata></metadata><manifest><item href="chapter1.html"/></manifest></package>''').encode()


def zip_fixture(path, members):
    with ZipFile(path, "w") as out:
        for name, data in members:
            out.writestr(name, data)


class PrivateOpfIntakeTests(unittest.TestCase):
    def test_namespaced_metadata_only_and_no_chapter_or_description(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "converted.zip"
            zip_fixture(path, [
                ("opf_books/Book A/Book A.opf", package()),
                ("opf_books/Book A/chapter1.html", b"COPYRIGHTED STORY BODY"),
                ("opf_books/Book A/cover.jpg", b"FAKE IMAGE BYTES"),
            ])
            item = mod.build_inventory(path)["candidates"][0]
            self.assertEqual(item["metadata"]["title"], "Sample & Test")
            self.assertEqual(item["metadata"]["creators"], ["Author A"])
            self.assertEqual(item["metadata_status"], "PARSED_UNVERIFIED")
            record = json.dumps(item)
            for private in ("COPYRIGHTED STORY BODY", "FAKE IMAGE BYTES", "MUST NEVER EXPORT"):
                self.assertNotIn(private, record)
            self.assertIsNone(item["canonical_work_id"])
            self.assertEqual(item["accepted_corpus_effect"], "NONE")

    def test_legacy_readerworks_dc_namespace_parses(self):
        metadata = mod.opf_metadata(package(namespace="http://purl.org/metadata/dublin_core"))
        self.assertEqual(metadata["title"], "Sample & Test")

    def test_unbound_legacy_prefix_is_not_silently_forged(self):
        with self.assertRaises(mod.IntakeError):
            mod.opf_metadata(package(legacy_unbound=True))
        metadata, repaired = mod.opf_metadata_with_legacy_review(package(legacy_unbound=True))
        self.assertTrue(repaired)
        self.assertEqual(metadata["title"], "Sample & Test")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "old.zip"
            zip_fixture(path, [("opf_books/Old/Old.opf", package(legacy_unbound=True))])
            row = mod.build_inventory(path)["candidates"][0]
            self.assertEqual(row["metadata_status"], "PARSED_LEGACY_REVIEW_REQUIRED")
            self.assertIn("review_hold", row)
            self.assertEqual(row["accepted_corpus_effect"], "NONE")

    def test_entity_declarations_and_dtd_subset_fail_closed(self):
        danger = b'<!DOCTYPE package [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><package>&xxe;</package>'
        with self.assertRaisesRegex(mod.IntakeError, "entity declarations"):
            mod.opf_metadata(danger)

    def test_unknown_simple_external_doctype_is_not_silently_approved(self):
        xml = (b'<!DOCTYPE package SYSTEM "file:///synthetic-unknown.dtd">'
               b'<package xmlns:dc="http://purl.org/dc/elements/1.1/">'
               b'<metadata><dc:title>Candidate</dc:title></metadata></package>')
        with self.assertRaisesRegex(mod.IntakeError, "unsupported document type"):
            mod.opf_metadata(xml)

    def test_utf16_utf32_entity_declaration_cannot_bypass_dtd_check(self):
        for encoding in ("UTF-16", "UTF-32"):
            xml = (f'''<?xml version="1.0" encoding="{encoding}"?>
<!DOCTYPE package [<!ENTITY injected "SYNTHETIC_ENTITY_VALUE">]>
<package xmlns:dc="http://purl.org/dc/elements/1.1/">
<metadata><dc:title>&injected;</dc:title></metadata></package>''')
            with self.subTest(encoding=encoding):
                with self.assertRaisesRegex(mod.IntakeError, "unsupported XML encoding"):
                    mod.opf_metadata(xml.encode(encoding.lower()))

    def test_unsafe_zip_paths_and_symlinks_rejected_without_extraction(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "unsafe.zip"
            for name in ("../escape/Book.opf", "/absolute/Book.opf", "dir\\Book.opf"):
                zip_fixture(path, [(name, package())])
                with self.subTest(name=name), self.assertRaisesRegex(mod.IntakeError, "unsafe member path"):
                    mod.build_inventory(path)
            link = ZipInfo("opf_books/Link/Link.opf")
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            zip_fixture(path, [("opf_books/Book A/Book.opf", package()), (link, b"/tmp/target")])
            with self.assertRaisesRegex(mod.IntakeError, "symbolic-link"):
                mod.build_inventory(path)

    def test_duplicate_zip_paths_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicates.zip"
            zip_fixture(path, [("Book.opf", package()), ("Book.opf", package())])
            with self.assertRaisesRegex(mod.IntakeError, "duplicate member paths"):
                mod.build_inventory(path)

    def test_lit_stem_matches_are_a_hint_not_a_work_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            opf, original = root / "converted.zip", root / "original.zip"
            zip_fixture(opf, [("opf_books/Book A/Book A.opf", package())])
            zip_fixture(original, [("source/BOOK A.lit", b"not read"), ("source/Unmatched.txt", b"not read")])
            result = mod.build_inventory(opf, original)
            self.assertEqual(result["summary"]["matched_lit_stems"], 1)
            self.assertEqual(result["summary"]["source_asset_extensions"], {".lit": 1, ".txt": 1})
            self.assertTrue(result["proposal_only"])
            self.assertEqual(result["accepted_work_effect"], "NONE")
            self.assertEqual(result["coverage_effect"], "NONE")

    def test_private_output_refuses_public_checkout_and_overwrite(self):
        with self.assertRaisesRegex(mod.IntakeError, "outside the public repo"):
            mod.private_output_path(ROOT / "proposals" / "books.json")
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "metadata.json"
            self.assertEqual(mod.private_output_path(out), out)
            out.write_text("existing", encoding="utf-8")
            with self.assertRaisesRegex(mod.IntakeError, "overwrite"):
                mod.private_output_path(out)

    def test_parent_symlink_swap_cannot_redirect_output_into_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            outer = Path(temp)
            archive = outer / "converted.zip"
            zip_fixture(archive, [("books/Book.opf", package())])
            output_parent = outer / "private-output"
            output_parent.mkdir()
            moved = outer / "moved-output"
            leaf = f"synthetic-race-{outer.name}.json"
            target = output_parent / leaf
            escaped = ROOT / leaf

            def race(*args):
                output_parent.rename(moved)
                output_parent.symlink_to(ROOT, target_is_directory=True)
                return original_build(*args)

            original_build = mod.build_inventory
            try:
                with mock.patch.object(mod, "build_inventory", side_effect=race):
                    with mock.patch.object(sys, "argv", ["opf-intake", "--opf-zip", str(archive), "--out", str(target)]):
                        exit_code = mod.main()
                self.assertEqual(exit_code, 1, "output path was redirected through a swapped parent")
                self.assertFalse(escaped.exists(), "private metadata was written to the public checkout")
            finally:
                escaped.unlink(missing_ok=True)

    def test_private_output_is_owner_only_with_normal_umask(self):
        with tempfile.TemporaryDirectory() as temp:
            outer = Path(temp)
            archive, output = outer / "converted.zip", outer / "inventory.json"
            zip_fixture(archive, [("books/Book.opf", package())])
            previous_umask = os.umask(0o022)
            try:
                result = subprocess.run(
                    [sys.executable, str(ROOT / "tools" / "inventory_opf_metadata.py"),
                     "--opf-zip", str(archive), "--out", str(output)],
                    capture_output=True, text=True,
                )
            finally:
                os.umask(previous_umask)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)

    def test_cli_emits_no_public_source_bytes_or_accepted_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive, output = root / "opf.zip", root / "private-inventory.json"
            zip_fixture(archive, [("opf_books/Book A/Book A.opf", package())])
            command = [sys.executable, str(ROOT / "tools" / "inventory_opf_metadata.py"),
                       "--opf-zip", str(archive), "--out", str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            value = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(value["summary"]["opf_packages"], 1)
            self.assertEqual(value["rights_status"], "USER_SUPPLIED_FILES_RIGHTS_NOT_VERIFIED")
            self.assertEqual(value["accepted_source_binding_effect"], "NONE")
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(second.returncode, 1)
            self.assertIn("overwrite", second.stderr)


if __name__ == "__main__":
    unittest.main()
