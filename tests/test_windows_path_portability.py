"""Exact Git-tree portability regression tests; no unsafe Windows checkout required."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

CHECKER = pathlib.Path(__file__).resolve().parents[1] / "tools" / "check_windows_path_portability.py"


def git(cwd, *args, input_bytes=None):
    return subprocess.run(["git", *args], cwd=cwd, input=input_bytes,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout


def classify(paths):
    with tempfile.TemporaryDirectory(prefix="trek-portability-") as td:
        git(td, "init", "-q")
        blob = git(td, "hash-object", "-w", "--stdin", input_bytes=b"fixture").decode().strip()
        # Raw Git trees bypass native Windows index filename filtering.
        def make_tree(entries):
            groups = {}
            for name, kind in entries:
                first, sep, rest = name.partition("/")
                groups.setdefault(first, []).append((rest if sep else "", kind))
            records = []
            for segment, members in sorted(groups.items()):
                if any(rest == "" for rest, _ in members):
                    assert len(members) == 1, "fixture path conflict"
                    kind = members[0][1]
                    mode, typ, oid = (("160000", "commit", "1" * 40)
                                      if kind == "gitlink" else ("100644", "blob", blob))
                else:
                    mode, typ, oid = "040000", "tree", make_tree(members)
                records.append(f"{mode} {typ} {oid}\t{segment}".encode("utf-8") + b"\0")
            return git(td, "mktree", "-z", "--missing", input_bytes=b"".join(records)).decode().strip()

        tree = make_tree(paths)
        actual = git(td, "ls-tree", "-rz", tree)
        observed = {}
        for entry in actual.split(b"\0"):
            if not entry:
                continue
            metadata, raw_path = entry.split(b"\t", 1)
            mode, kind, oid = metadata.decode().split(" ")
            observed[raw_path.decode("utf-8")] = (mode, kind, oid)
        expected = {name: ("160000", "commit") if kind == "gitlink"
                    else ("100644", "blob") for name, kind in paths}
        assert set(observed) == set(expected), (expected, observed)
        for name, (mode, kind) in expected.items():
            assert observed[name][:2] == (mode, kind), (name, observed[name])
        proc = subprocess.run([sys.executable, str(CHECKER), "--ref", tree],
                              cwd=td, capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout)


class WindowsGitTreePortability(unittest.TestCase):
    def test_safe_blob(self):
        rc, data = classify([("safe/normal.txt", "blob")])
        self.assertEqual(rc, 0)
        self.assertTrue(data["portable"])

    def test_safe_gitlink(self):
        rc, data = classify([("safe/module", "gitlink")])
        self.assertEqual(rc, 0)
        self.assertTrue(data["portable"])
        self.assertEqual(data["blob_count"], 0)

    def test_reserved_devices(self):
        for name in ("CON", "CONIN$", "CONOUT$", "CONIN$.txt",
                     "CONOUT$.txt", "COM¹.txt", "AUX.txt", "CON .txt"):
            with self.subTest(name=name):
                rc, data = classify([(name, "blob")])
                self.assertEqual(rc, 1)
                self.assertIn(name, data["windows_invalid_paths"])

    def test_reserved_gitlink(self):
        rc, data = classify([("CON", "gitlink")])
        self.assertEqual(rc, 1)
        self.assertIn("CON", data["windows_invalid_paths"])

    def test_case_collision_preserves_both_ids(self):
        rc, data = classify([("Case.txt", "blob"), ("case.txt", "blob")])
        self.assertEqual(rc, 1)
        self.assertEqual(len(data["collision_groups"]), 1)
        self.assertEqual({e["path"] for e in data["collision_groups"][0]},
                         {"Case.txt", "case.txt"})

    def test_file_directory_case_prefix_conflict(self):
        for paths in (
            [("Foo", "blob"), ("foo/bar", "blob")],
            [("Foo/bar", "blob"), ("foo/baz", "blob")],
            [("Foo", "gitlink"), ("foo/bar", "blob")],
        ):
            with self.subTest(paths=paths):
                rc, data = classify(paths)
                self.assertEqual(rc, 1)
                self.assertFalse(data["portable"])
                self.assertTrue(data["collision_groups"])

    def test_shared_directory_prefix_is_not_collision(self):
        rc, data = classify([("same/a", "blob"), ("same/b", "blob")])
        self.assertEqual(rc, 0)
        self.assertEqual(data["collision_groups"], [])

    def test_invalid_utf8_git_filename_is_rejected(self):
        # Git accepts raw filename bytes that cannot be decoded as UTF-8.
        # Construct a real tree directly; do not rely on filesystem encoding.
        with tempfile.TemporaryDirectory(prefix="trek-invalid-utf8-") as td:
            git(td, "init", "-q")
            blob = git(td, "hash-object", "-w", "--stdin",
                       input_bytes=b"fixture").decode().strip()
            entry = b"100644 blob " + blob.encode("ascii") + b"\tbad-\xff.txt\0"
            tree = git(td, "mktree", "-z", input_bytes=entry).decode().strip()
            actual = git(td, "ls-tree", "-rz", tree)
            self.assertIn(b"bad-\xff.txt", actual)
            proc = subprocess.run([sys.executable, str(CHECKER), "--ref", tree],
                                  cwd=td, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            data = json.loads(proc.stdout)
            self.assertFalse(data["portable"])
            self.assertEqual(len(data["windows_invalid_paths"]), 1)

    def test_windows_component_utf16_length_boundary(self):
        # NTFS filename components are limited to 255 UTF-16 code units.
        for name, expected_rc in (
            ("a" * 255, 0),
            ("a" * 256, 1),
            ("a" * 300, 1),
            ("😀" * 127, 0),
            ("😀" * 128, 1),
        ):
            with self.subTest(code_units=len(name.encode("utf-16-le")) // 2):
                rc, data = classify([(name, "blob")])
                self.assertEqual(rc, expected_rc)
                self.assertEqual(data["portable"], expected_rc == 0)
                if expected_rc:
                    self.assertIn(name, data["windows_invalid_paths"])

    def test_identical_duplicate_leaf_git_entries_rejected(self):
        # A malformed Git tree can contain duplicate records that the normal
        # index cannot create. Never deduplicate these before validation.
        with tempfile.TemporaryDirectory(prefix="trek-duplicate-leaf-") as td:
            git(td, "init", "-q")
            blob = git(td, "hash-object", "-w", "--stdin",
                       input_bytes=b"fixture").decode().strip()
            record = f"100644 blob {blob}\\tduplicate.txt\\n".encode()
            tree = git(td, "mktree", input_bytes=record * 2).decode().strip()
            actual = git(td, "ls-tree", "-rz", tree)
            self.assertEqual(actual.count(b"\\tduplicate.txt\\0"), 2)
            proc = subprocess.run([sys.executable, str(CHECKER), "--ref", tree],
                                  cwd=td, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            data = json.loads(proc.stdout)
            self.assertFalse(data["portable"])
            self.assertEqual(len(data["collision_groups"]), 1)
            self.assertEqual(len(data["collision_groups"][0]), 2)

    def test_invalid_character(self):
        rc, data = classify([("bad?.txt", "blob")])
        self.assertEqual(rc, 1)
        self.assertIn("bad?.txt", data["windows_invalid_paths"])


if __name__ == "__main__":
    unittest.main()
