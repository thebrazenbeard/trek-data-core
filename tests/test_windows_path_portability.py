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
        records = []
        for name, kind in paths:
            mode, oid = ("160000", "1" * 40) if kind == "gitlink" else ("100644", blob)
            records.append(f"{mode} {oid}\t{name}".encode("utf-8") + b"\0")
        git(td, "update-index", "-z", "--index-info", input_bytes=b"".join(records))
        tree = git(td, "write-tree").decode().strip()
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

    def test_invalid_character(self):
        rc, data = classify([("bad?.txt", "blob")])
        self.assertEqual(rc, 1)
        self.assertIn("bad?.txt", data["windows_invalid_paths"])


if __name__ == "__main__":
    unittest.main()
