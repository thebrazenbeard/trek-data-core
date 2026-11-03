"""Deployment allowlist must preserve HELD photo receipts without widening release."""
from fnmatch import fnmatchcase
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/static.yml"
HELD = (
    "explorer/beyond-premiere-photo.json",
    "explorer/beyond-premiere-release-decision.json",
)


class PagesHeldPhotoArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        start = cls.workflow.index("if find explorer -mindepth 1")
        end = cls.workflow.index("-print -quit | grep -q .; then", start)
        fragment = cls.workflow[start:end]
        pairs = re.findall(r"! -path (?:'([^']+)'|(\S+))", fragment)
        cls.allowed = set(left or right for left, right in pairs)

    def test_only_exact_held_sidecars_join_static_allowlist(self):
        for path in HELD:
            self.assertIn(path, self.allowed)
        self.assertIn("for path in " + " ".join(HELD) + "; do", self.workflow)
        self.assertIn('expected="$(git rev-parse "HEAD:$path")"', self.workflow)
        self.assertIn('actual="$(git hash-object "$path")"', self.workflow)
        self.assertIn('test ! -L "$path"', self.workflow)
        self.assertIn("python3 tools/validate_beyond_documentary_photo.py", self.workflow)
        self.assertIn("public_image_display_authorized", (ROOT / HELD[1]).read_text())

    def test_third_entry_and_unreviewed_binary_remain_rejected(self):
        def permitted(path):
            return any(fnmatchcase(path, pattern) for pattern in self.allowed)

        for file in (
            "explorer/unreviewed-photo.bin",
            "explorer/unreviewed-photo.jpg",
            "explorer/nested/approval.md",
            "explorer/.secret",
            "explorer/__pycache__/image.cpython-312.pyc",
        ):
            with self.subTest(file=file):
                self.assertFalse(permitted(file))
        # Only the pre-existing scoped licensed-artwork path may be wildcarded.
        self.assertEqual({p for p in self.allowed if "*" in p},
                         {"explorer/licensed-artwork/*"})

    def test_all_committed_explorer_entries_are_accounted_for(self):
        def permitted(path):
            return any(fnmatchcase(path, pattern) for pattern in self.allowed)

        for entry in (ROOT / "explorer").rglob("*"):
            rel = entry.relative_to(ROOT).as_posix()
            with self.subTest(path=rel):
                self.assertTrue(permitted(rel), f"unreviewed Explorer artifact: {rel}")

    def test_minimal_fixture_and_partial_photo_pair_fail_closed(self):
        if not shutil.which("bash") or not shutil.which("git"):
            self.skipTest("GitHub Pages artifact shell requires bash and git")
        fragment = self.workflow.split("      - name: Verify final public artifact boundary", 1)[1]
        fragment = fragment.split("      - name: Upload Explorer only", 1)[0]
        script = "\n".join(row[10:] for row in fragment.splitlines()
                           if row.startswith("          "))
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "explorer").mkdir()
            (root / "docs/assets").mkdir(parents=True)
            for file in ("index.html", "index.json", "app.js", "app.css",
                         "trek-data-core-hero.jpg"):
                (root / "explorer" / file).write_bytes(b"accepted\n")
            (root / "docs/assets/trek-data-core-hero.jpg").write_bytes(b"accepted\n")

            def git(*args):
                run = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)

            def check():
                return subprocess.run(["bash", "-e", "-u", "-o", "pipefail", "-c", script],
                                      cwd=root, capture_output=True, text=True)

            git("init", "-q")
            git("add", "--", "explorer", "docs/assets")
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "-qm", "Core only")
            self.assertEqual(check().returncode, 0)
            rogue = root / "explorer/unreviewed-photo.bin"
            rogue.write_bytes(b"\xff\xd8\xff\xe0JFIF")
            self.assertNotEqual(check().returncode, 0)
            rogue.unlink()
            (root / HELD[0]).write_text("{}")
            git("add", "--", HELD[0])
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "-qm", "Only one held receipt")
            self.assertNotEqual(check().returncode, 0)
            (root / HELD[1]).write_text("{}")
            self.assertNotEqual(check().returncode, 0)


if __name__ == "__main__":
    unittest.main()
