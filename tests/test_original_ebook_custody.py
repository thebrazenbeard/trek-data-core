"""Synthetic, rights-neutral checks for original ebook member custody."""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


MODULE = Path(__file__).resolve().parents[1] / "tools" / "inventory_original_ebook_members.py"
spec = importlib.util.spec_from_file_location("inventory_original_ebook_members", MODULE)
custody = importlib.util.module_from_spec(spec)
spec.loader.exec_module(custody)


class OriginalEbookCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.archive = self.base / "synthetic.zip"
        self.receipt = self.base / "private-receipt.json"

    def make_zip(self, members=None):
        if members is None:
            members = [("part/B.lit", b"LIT SYNTHETIC", None),
                       ("part/A.txt", b"TXT SYNTHETIC", None)]
        with ZipFile(self.archive, "w", compression=ZIP_DEFLATED) as archive:
            for name, raw, mode in members:
                info = ZipInfo(name)
                info.compress_type = ZIP_DEFLATED
                if mode is not None:
                    info.create_system = 3
                    info.external_attr = mode << 16
                archive.writestr(info, raw)

    def run_cli(self, *args):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            status = custody.main(list(args))
        return status, output.getvalue(), error.getvalue()

    def test_capture_and_exact_replay_are_private_and_deterministic(self):
        self.make_zip()
        status, output, error = self.run_cli("capture", "--original-zip", str(self.archive),
                                             "--out", str(self.receipt))
        self.assertEqual((status, error), (0, ""))
        self.assertIn("2 file members", output)
        self.assertNotIn("part/A.txt", output)
        self.assertEqual(stat.S_IMODE(self.receipt.stat().st_mode), 0o600)
        observed = json.loads(self.receipt.read_text(encoding="utf-8"))
        self.assertEqual(observed["file_observations"], 2)
        self.assertEqual(observed["counts_by_extension"], {".lit": 1, ".txt": 1})
        self.assertEqual(observed["work_admission_effect"], "NONE")
        self.assertEqual(observed["coverage_effect"], "NONE")
        self.assertEqual([row["member_id"] for row in observed["members"]],
                         ["original-local:lit:0001", "original-local:txt:0001"])
        self.assertEqual(observed["members"][1]["member_sha256"],
                         hashlib.sha256(b"TXT SYNTHETIC").hexdigest())
        self.assertNotIn("LIT SYNTHETIC", self.receipt.read_text(encoding="utf-8"))
        status, output, error = self.run_cli("verify", "--original-zip", str(self.archive),
                                             "--receipt", str(self.receipt))
        self.assertEqual((status, error), (0, ""))
        self.assertIn("VERIFIED", output)
        self.assertEqual(observed, custody.inventory_zip(self.archive))

    def test_archive_mutation_fails_exact_replay(self):
        self.make_zip()
        self.assertEqual(self.run_cli("capture", "--original-zip", str(self.archive),
                                      "--out", str(self.receipt))[0], 0)
        self.make_zip([("part/B.lit", b"ALTERED", None), ("part/A.txt", b"TXT SYNTHETIC", None)])
        self.assertEqual(self.run_cli("verify", "--original-zip", str(self.archive),
                                      "--receipt", str(self.receipt))[0], 1)

    def test_expected_custody_digest_and_member_counts_fail_closed(self):
        self.make_zip()
        for more in (("--expect-archive-sha256", "0" * 64),
                     ("--expect-lit", "2"), ("--expect-txt", "2")):
            with self.subTest(more=more):
                self.assertEqual(self.run_cli("capture", "--original-zip", str(self.archive),
                                              "--out", str(self.receipt), *more)[0], 1)
                self.assertFalse(self.receipt.exists())

    def test_unsafe_traversal_duplicate_symlink_and_casefold_collision_rejected(self):
        scenarios = [
            [("../escape.txt", b"X", None)],
            [("./period.txt", b"X", None)],
            [("C:/drive.txt", b"X", None)],
            [("Ｃ：/drive.txt", b"X", None)],
            [("．．/traversal.txt", b"X", None)],
            [("safe.txt", b"A", None), ("safe.txt", b"B", None)],
            [("Title.txt", b"A", None), ("title.TXT", b"B", None)],
            [("link.txt", b"link", stat.S_IFLNK | 0o777)],
        ]
        for members in scenarios:
            with self.subTest(members=members):
                self.make_zip(members)
                with self.assertRaises(custody.CustodyError):
                    custody.inventory_zip(self.archive)

    def test_directory_and_unknown_member_are_not_silently_counted_as_books(self):
        self.make_zip([("folder/", b"", None), ("folder/a.lit", b"a", None),
                       ("folder/cover.jpg", b"image", None)])
        with self.assertRaises(custody.CustodyError):
            custody.inventory_zip(self.archive)

    def test_compression_bomb_is_rejected_before_decompression(self):
        self.make_zip([("huge.txt", b"X" * (2 * 1024 * 1024), None)])
        with self.assertRaises(custody.CustodyError):
            custody.inventory_zip(self.archive)

    def test_no_existing_or_public_repo_output_overwrite(self):
        self.make_zip()
        self.receipt.write_text("already here", encoding="utf-8")
        self.assertEqual(self.run_cli("capture", "--original-zip", str(self.archive),
                                      "--out", str(self.receipt))[0], 1)
        self.assertEqual(self.receipt.read_text(encoding="utf-8"), "already here")
        public_path = MODULE.parent.parent / "should-never-be-created.json"
        self.assertEqual(self.run_cli("capture", "--original-zip", str(self.archive),
                                      "--out", str(public_path))[0], 1)
        self.assertFalse(public_path.exists())

    def test_archive_symlink_rejected_and_no_private_paths_in_errors(self):
        self.make_zip()
        link = self.base / "source-symlink.zip"
        link.symlink_to(self.archive)
        status, output, error = self.run_cli("capture", "--original-zip", str(link),
                                             "--out", str(self.receipt))
        self.assertEqual(status, 1)
        self.assertNotIn(str(link), output + error)


if __name__ == "__main__":
    unittest.main()
