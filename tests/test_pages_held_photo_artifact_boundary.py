"""Deployment allowlist must preserve HELD photo receipts without widening release."""
from fnmatch import fnmatchcase
from pathlib import Path
import re
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


if __name__ == "__main__":
    unittest.main()
