"""Synthetic adversarial checks for private converted-derivative custody."""

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


MODULE = Path(__file__).resolve().parents[1] / "tools" / "inventory_converted_derivative_members.py"
spec = importlib.util.spec_from_file_location("inventory_converted_derivative_members", MODULE)
custody = importlib.util.module_from_spec(spec)
spec.loader.exec_module(custody)


class ConvertedDerivativeCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.archive = self.base / "converted.zip"
        self.receipt = self.base / "private.json"

    def make_zip(self, members=None):
        if members is None:
            members = [
                ("book/record.opf", b"SYNTHETIC METADATA", None),
                ("book/a.htm", b"", None),
                ("book/cover.jpg", b"", None),
                ("book/style.css", b"", None),
                ("book/b.html", b"SYNTHETIC CONVERSION", None),
            ]
        with ZipFile(self.archive, "w", compression=ZIP_DEFLATED) as zip_file:
            for name, raw, mode in members:
                info = ZipInfo(name)
                info.compress_type = ZIP_DEFLATED
                if mode is not None:
                    info.create_system = 3
                    info.external_attr = mode << 16
                zip_file.writestr(info, raw)

    def cli(self, mode, *, files=5, directories=0, opf=1, css=1, htm=1, jpg=1, extra=()):
        args = [mode, "--converted-zip", str(self.archive),
                "--expect-archive-sha256", hashlib.sha256(self.archive.read_bytes()).hexdigest(),
                "--expect-files", str(files), "--expect-directories", str(directories),
                "--expect-opf", str(opf),
                "--expect-empty-css", str(css), "--expect-empty-htm", str(htm),
                "--expect-empty-jpg", str(jpg)]
        args.extend(["--out", str(self.receipt)] if mode == "capture"
                    else ["--receipt", str(self.receipt)])
        args.extend(extra)
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = custody.main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_capture_replay_keeps_empty_members_explicit_and_private(self):
        self.make_zip()
        self.assertEqual(self.cli("capture")[0], 0)
        receipt = json.loads(self.receipt.read_text(encoding="utf-8"))
        self.assertEqual(stat.S_IMODE(self.receipt.stat().st_mode), 0o600)
        self.assertEqual(receipt["record_type"], "PRIVATE_CONVERTED_DERIVATIVE_MEMBER_CUSTODY")
        self.assertEqual(receipt["empty_file_observations"], 3)
        self.assertEqual(receipt["empty_counts_by_extension"], {".css": 1, ".htm": 1, ".jpg": 1})
        self.assertEqual(receipt["counts_by_extension"][".opf"], 1)
        self.assertEqual(receipt["source_work_binding"], "UNRESOLVED")
        self.assertEqual(receipt["content_completeness"], "NOT_ESTABLISHED")
        self.assertEqual(receipt["coverage_effect"], "NONE")
        self.assertEqual(receipt["work_admission_effect"], "NONE")
        self.assertEqual([m["content_kind"] for m in receipt["members"]].count(
            "CONVERSION_PLACEHOLDER"), 3)
        self.assertTrue(all(m["member_sha256"] == hashlib.sha256(b"").hexdigest()
                            for m in receipt["members"]
                            if m["content_kind"] == "CONVERSION_PLACEHOLDER"))
        self.assertNotIn("SYNTHETIC CONVERSION", self.receipt.read_text(encoding="utf-8"))
        status, stdout, _ = self.cli("verify")
        self.assertEqual(status, 0)
        self.assertIn("VERIFIED", stdout)
        self.assertNotIn("book/", stdout)

    def test_empty_opf_and_unknown_empty_types_fail_closed(self):
        cases = [
            [("book/record.opf", b"", None)],
            [("book/record.opf", b"metadata", None), ("book/manifest.json", b"", None)],
            [("book/record.opf", b"metadata", None), ("book/notes.txt", b"", None)],
        ]
        for members in cases:
            with self.subTest(members=members):
                self.make_zip(members)
                self.assertEqual(self.cli("capture", files=len(members), css=0, htm=0, jpg=0)[0], 1)
                self.assertFalse(self.receipt.exists())

    def test_zero_count_drift_and_hash_mismatch_fail_closed(self):
        self.make_zip()
        for opts in ({"jpg": 2}, {"htm": 0}, {"opf": 2}, {"files": 6},
                     {"directories": 1}):
            with self.subTest(opts=opts):
                self.assertEqual(self.cli("capture", **opts)[0], 1)
                self.assertFalse(self.receipt.exists())
        self.assertEqual(self.cli("capture", extra=("--expect-archive-sha256", "0" * 64))[0], 1)
        self.assertFalse(self.receipt.exists())

    def test_exact_replay_detects_archive_mutation(self):
        self.make_zip()
        self.assertEqual(self.cli("capture")[0], 0)
        self.make_zip([
            ("book/record.opf", b"ALTERED METADATA", None),
            ("book/a.htm", b"", None),
            ("book/cover.jpg", b"", None),
            ("book/style.css", b"", None),
            ("book/b.html", b"SYNTHETIC CONVERSION", None),
        ])
        self.assertEqual(self.cli("verify")[0], 1)

    def test_unsafe_member_names_duplicates_symlinks_and_extensions_rejected(self):
        cases = [
            [("../evil.opf", b"x", None)],
            [("Ｃ：/evil.opf", b"x", None)],
            [("book/record.opf", b"x", None), ("book/record.opf", b"y", None)],
            [("book/CASE.opf", b"x", None), ("book/case.opf", b"y", None)],
            [("book/link.opf", b"x", stat.S_IFLNK | 0o777)],
            [("book/evil.exe", b"x", None)],
        ]
        for members in cases:
            with self.subTest(members=members):
                self.make_zip(members)
                self.assertEqual(self.cli("capture", files=len(members), css=0, htm=0, jpg=0)[0], 1)
                self.assertFalse(self.receipt.exists())

    def test_private_permissions_and_non_overwrite(self):
        self.make_zip()
        self.receipt.write_text("existing", encoding="utf-8")
        self.assertEqual(self.cli("capture")[0], 1)
        self.assertEqual(self.receipt.read_text(encoding="utf-8"), "existing")
        self.receipt.unlink()
        self.assertEqual(self.cli("capture")[0], 0)
        self.receipt.chmod(0o644)
        self.assertEqual(self.cli("verify")[0], 1)

    def test_compression_bomb_and_corrupt_zip_rejected_without_receipt(self):
        self.make_zip([("book/record.opf", b"X" * (2 * 1024 * 1024), None)])
        self.assertEqual(self.cli("capture", files=1, css=0, htm=0, jpg=0)[0], 1)
        self.assertFalse(self.receipt.exists())
        self.archive.write_bytes(b"not a ZIP")
        self.assertEqual(self.cli("capture", files=1, css=0, htm=0, jpg=0)[0], 1)
        self.assertFalse(self.receipt.exists())

    def test_private_parent_must_be_owner_only(self):
        self.make_zip()
        self.base.chmod(0o755)
        self.assertEqual(self.cli("capture")[0], 1)
        self.assertFalse(self.receipt.exists())
        self.base.chmod(0o700)

    def test_symlinked_archive_parent_and_public_output_fail_closed(self):
        self.make_zip()
        link = self.base / "parent-link"
        link.symlink_to(self.base, target_is_directory=True)
        source = self.archive
        self.archive = link / "converted.zip"
        self.assertEqual(self.cli("capture")[0], 1)
        self.assertFalse(self.receipt.exists())
        self.archive = source
        private_path = self.receipt
        self.receipt = MODULE.parent.parent / "do-not-write-converted-receipt.json"
        self.assertEqual(self.cli("capture")[0], 1)
        self.assertFalse(self.receipt.exists())
        self.receipt = private_path

    def test_nonempty_directory_marker_rejected(self):
        self.make_zip([("book/", b"disguised content", None),
                       ("book/record.opf", b"metadata", None)])
        self.assertEqual(self.cli("capture", files=1, directories=1,
                                  css=0, htm=0, jpg=0)[0], 1)
        self.assertFalse(self.receipt.exists())

    def test_dotdot_alias_into_public_repo_is_rejected_before_create(self):
        self.make_zip()
        public_root = self.base / "public_repo"
        public_root.mkdir()
        private_inside_public = public_root / "owner_private"
        private_inside_public.mkdir(mode=0o700)
        unrelated = self.base / "unrelated"
        unrelated.mkdir()
        direct = private_inside_public / "should-not-exist.json"
        through_dotdot = unrelated / ".." / "public_repo" / "owner_private" / direct.name
        with patch.object(custody, "ROOT", public_root):
            self.receipt = direct
            self.assertEqual(self.cli("capture")[0], 1)
            self.receipt = through_dotdot
            self.assertEqual(self.cli("capture")[0], 1)
        self.assertFalse(direct.exists())

    def test_nonregular_unix_entry_types_cannot_masquerade_as_opf(self):
        for mode in (stat.S_IFCHR | 0o666, stat.S_IFDIR | 0o755,
                     stat.S_IFBLK | 0o660, stat.S_IFIFO | 0o600):
            with self.subTest(unix_mode=oct(mode)):
                if self.receipt.exists():
                    self.receipt.unlink()
                self.make_zip([("book/record.opf", b"not-regular", mode)])
                self.assertEqual(self.cli("capture", files=1, opf=1,
                                          css=0, htm=0, jpg=0)[0], 1)
                self.assertFalse(self.receipt.exists())

    def test_file_directory_name_and_parent_component_collisions_rejected(self):
        scenarios = [
            [("book/entry.opf/", b"", None), ("book/entry.opf", b"metadata", None)],
            [("book/entry.opf", b"metadata", None), ("book/entry.opf/", b"", None)],
            [("book/entry.opf", b"metadata", None),
             ("book/entry.opf/nested.htm", b"html", None)],
        ]
        for members in scenarios:
            with self.subTest(members=members):
                if self.receipt.exists():
                    self.receipt.unlink()
                self.make_zip(members)
                dirs = sum(name.endswith("/") for name, _, _ in members)
                files = len(members) - dirs
                self.assertEqual(self.cli("capture", files=files, directories=dirs,
                                          css=0, htm=0, jpg=0)[0], 1)
                self.assertFalse(self.receipt.exists())


if __name__ == "__main__":
    unittest.main()
