"""Synthetic ZIP-only tests. Never use Patrick's private books in CI."""

from __future__ import annotations

import importlib.util
import hashlib
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
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "member_intake", ROOT / "tools" / "inventory_ebook_zip_members.py",
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def fixture(path, entries):
    with ZipFile(path, "w") as archive:
        for name, data in entries:
            archive.writestr(name, data)


def package():
    return (b'<package xmlns:dc="http://purl.org/dc/elements/1.1/">'
            b'<metadata><dc:title>Alpha Test</dc:title></metadata></package>')


class EbookMemberIntakeTests(unittest.TestCase):
    def test_opaque_byte_hashes_no_paths_text_or_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "original.zip"
            fixture(path, [("fiction/Alpha.lit", b"fiction text stays private"),
                           ("fiction/Alpha.txt", b"synthetic text stays private"),
                           ("fiction/Beta.txt", b"synthetic prose")])
            result = mod.inventory(path)
            self.assertEqual(result["summary"], {
                "original_members_hashed": 3, "lit_members": 1, "txt_members": 2,
            })
            self.assertEqual(result["source_admission_effect"], "NONE")
            self.assertEqual(result["coverage_effect"], "NONE")
            rows = result["member_receipts"]
            self.assertEqual(len({row["member_id"] for row in rows}), 3)
            expected = {hashlib.sha256(data).hexdigest() for data in
                        (b"fiction text stays private", b"synthetic text stays private",
                         b"synthetic prose")}
            self.assertEqual({row["byte_sha256"] for row in rows}, expected)
            serialized = json.dumps(result)
            for private in ("fiction/", "Alpha.lit", "Beta.txt", "fiction text",
                            "synthetic prose"):
                self.assertNotIn(private, serialized)
            self.assertTrue(all(row["canonical_work_id"] is None for row in rows))

    def test_opf_crosswalk_is_stem_only_not_edition_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            original, converted = folder / "original.zip", folder / "opf.zip"
            fixture(original, [("source/Alpha.lit", b"lit bytes"),
                               ("source/Alpha.txt", b"txt bytes"),
                               ("source/Beta.txt", b"other bytes")])
            fixture(converted, [("opf_books/Alpha/Alpha.opf", package()),
                                ("opf_books/Unmatched/Unmatched.opf", package())])
            result = mod.inventory(original, opf_zip=converted)
            crosswalk = result["conversion_stem_crosswalk"]
            self.assertEqual(crosswalk["opf_count"], 2)
            self.assertEqual(crosswalk["links"][0]["status"],
                             "UNIQUE_STEM_CANDIDATE_UNVERIFIED")
            self.assertIsNotNone(crosswalk["links"][0]["lit_member_id"])
            self.assertIsNotNone(crosswalk["links"][0]["txt_member_id"])
            self.assertEqual(crosswalk["links"][1]["status"], "NO_LIT_STEM_MATCH")
            self.assertNotIn("Alpha", json.dumps(result))

    def test_unsafe_paths_collisions_symlinks_and_types_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.zip"
            for name in ("../escape.txt", "C:/absolute.txt", "/root.txt",
                         "foo\\bar.lit", "segment/./bad.txt", "a//bad.txt",
                         "control/\u202eabc.txt"):
                with self.subTest(case="unsafe-path"):
                    fixture(path, [(name, b"synthetic")])
                    with self.assertRaisesRegex(mod.IntakeError, "unsafe ZIP path"):
                        mod.inventory(path)
            for entries in ([('A.txt', b'a'), ('a.TXT', b'b')],
                            [('same.lit', b'a'), ('same.lit', b'b')],
                            [('cafe\u0301.txt', b'a'), ('caf\u00e9.txt', b'b')]):
                with self.subTest(case="collision"):
                    fixture(path, entries)
                    with self.assertRaisesRegex(mod.IntakeError, "normalization-colliding"):
                        mod.inventory(path)
            link = ZipInfo("link.lit")
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            fixture(path, [(link, b"/no/extraction")])
            with self.assertRaisesRegex(mod.IntakeError, "non-regular"):
                mod.inventory(path)
            fixture(path, [("unexpected.epub", b"bytes")])
            with self.assertRaisesRegex(mod.IntakeError, "unexpected non-LIT/TXT"):
                mod.inventory(path)

    def test_encrypted_flag_corrupt_crc_and_bomb_preflight(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "source.zip"
            fixture(path, [("safe.txt", b"a few bytes")])
            with ZipFile(path) as archive:
                info = archive.infolist()[0]
                with mock.patch.object(info, "flag_bits", 1):
                    with self.assertRaisesRegex(mod.IntakeError, "encrypted"):
                        mod._source_member_index(archive)
                with mock.patch.object(info, "CRC", info.CRC ^ 1):
                    with self.assertRaises(mod.IntakeError):
                        mod._member_receipts(archive, [info])
                with mock.patch.object(info, "file_size", mod.MAX_MEMBER_BYTES + 1):
                    with self.assertRaisesRegex(mod.IntakeError, "per-file"):
                        mod._source_member_index(archive)
                with mock.patch.object(info, "compress_size", 0):
                    with self.assertRaisesRegex(mod.IntakeError, "compression ratio"):
                        mod._source_member_index(archive)

    def test_expected_digest_source_symlink_and_write_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            original = folder / "original.zip"
            fixture(original, [("safe.lit", b"no prose parsed")])
            with self.assertRaisesRegex(mod.IntakeError, "expected custody"):
                mod.inventory(original, expected_sha256="0" * 64)
            alias = folder / "alias.zip"
            alias.symlink_to(original)
            with self.assertRaisesRegex(mod.IntakeError, "not a secure regular input"):
                mod.inventory(alias)
            link_parent = folder / "alias-dir"
            link_parent.symlink_to(folder, target_is_directory=True)
            with self.assertRaisesRegex(mod.IntakeError, "not a secure regular input"):
                mod.inventory(link_parent / "original.zip")
            with self.assertRaisesRegex(mod.IntakeError, "outside the public repo"):
                mod.write_private(ROOT / "accidental-public.json", {"not": "allowed"})

    def test_cli_private_owner_only_no_overwrite_or_leak(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            original, output = folder / "original.zip", folder / "private.json"
            fixture(original, [("secret/book.lit", b"private source bytes")])
            command = [sys.executable, str(ROOT / "tools" / "inventory_ebook_zip_members.py"),
                       "--original-zip", str(original), "--out", str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertNotIn("secret", first.stdout + first.stderr)
            self.assertNotIn("private source bytes", output.read_text())
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(second.returncode, 1)
            self.assertNotIn("secret", second.stdout + second.stderr)


if __name__ == "__main__":
    unittest.main()
