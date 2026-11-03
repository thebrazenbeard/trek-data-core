"""Independent synthetic release-gate regressions for first-party Lore code.

All test inputs are synthetic temporary copies. They grant no artwork rights and
do not publish, download, or execute an external model.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import validate_artwork_release as release


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LoreStaticReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        folder = self.root / "explorer"
        folder.mkdir()
        for name in ("app.css", "app.js", "index.html", "lore-public-chat.js", "lore-semantic-chat.js"):
            shutil.copyfile(ROOT / "explorer" / name, folder / name)
        # Construct a valid, fully fingerprinted startup baseline independent
        # of whether the integration team's in-progress pins have been updated.
        public = (folder / "lore-public-chat.js").read_text(encoding="utf-8")
        public = re.sub(
            r"(['\"])\./lore-semantic-chat\.js(?:\?v=[a-f0-9]{64})?\1",
            lambda match: f"{match.group(1)}./lore-semantic-chat.js?v={digest(folder / 'lore-semantic-chat.js')}{match.group(1)}",
            public,
            count=1,
        )
        (folder / "lore-public-chat.js").write_text(public, encoding="utf-8")
        html = (folder / "index.html").read_text(encoding="utf-8")
        for name in ("app.js", "lore-public-chat.js"):
            html = re.sub(
                rf"\./{re.escape(name)}\?v=[a-f0-9]{{64}}",
                f"./{name}?v={digest(folder / name)}",
                html,
                count=1,
            )
        (folder / "index.html").write_text(html, encoding="utf-8")

    def _replace_html(self, before: str, after: str):
        target = self.root / "explorer/index.html"
        raw = target.read_text(encoding="utf-8")
        self.assertIn(before, raw)
        target.write_text(raw.replace(before, after, 1), encoding="utf-8")

    def test_valid_pinned_public_lore_bundle_passes_startup_gate(self):
        release.check_static_startup(self.root)

    def test_public_lore_byte_drift_fails_closed(self):
        target = self.root / "explorer/lore-public-chat.js"
        target.write_bytes(target.read_bytes() + b"\n// synthetically changed after fingerprint\n")
        with self.assertRaisesRegex(release.ArtworkRejected, "script fingerprint"):
            release.check_static_startup(self.root)

    def test_semantic_lore_byte_drift_fails_closed(self):
        target = self.root / "explorer/lore-semantic-chat.js"
        target.write_bytes(target.read_bytes() + b"\n// synthetically changed after import pin\n")
        with self.assertRaisesRegex(release.ArtworkRejected, "semantic module import integrity"):
            release.check_static_startup(self.root)

    def test_unpinned_semantic_import_fails_closed(self):
        semantic = self.root / "explorer/lore-semantic-chat.js"
        target = self.root / "explorer/lore-public-chat.js"
        public = target.read_text(encoding="utf-8")
        pinned = f"./lore-semantic-chat.js?v={digest(semantic)}"
        self.assertIn(pinned, public)
        target.write_text(public.replace(pinned, "./lore-semantic-chat.js", 1), encoding="utf-8")
        html = self.root / "explorer/index.html"
        old = html.read_text(encoding="utf-8")
        old = re.sub(r"(\./lore-public-chat\.js\?v=)[a-f0-9]{64}",
                     lambda m: m.group(1) + digest(target), old, count=1)
        html.write_text(old, encoding="utf-8")
        with self.assertRaisesRegex(release.ArtworkRejected, "semantic module import must be pinned"):
            release.check_static_startup(self.root)

    def test_remote_module_script_fails_closed(self):
        self._replace_html("</head>", '<script type="module" src="https://example.org/lore.js"></script>\n</head>')
        with self.assertRaisesRegex(release.ArtworkRejected, "unexpected script URL"):
            release.check_static_startup(self.root)

    def test_inline_script_fails_closed(self):
        self._replace_html("</head>", "<script>alert(1)</script>\n</head>")
        with self.assertRaisesRegex(release.ArtworkRejected, "unexpected script URL"):
            release.check_static_startup(self.root)

    def test_duplicate_hero_src_is_rejected_before_browser_disagreement(self):
        # HTML parsers/browsers may preserve the first duplicate attribute,
        # whereas dict(attrs) preserves the last; external cover origins are
        # permitted only after a visitor makes the documented opt-in.
        html = (self.root / "explorer/index.html").read_text(encoding="utf-8")
        match = re.search(r'<img class="masthead-art" src="([^"]+)"', html)
        self.assertIsNotNone(match)
        self._replace_html(
            f'<img class="masthead-art" src="{match.group(1)}"',
            f'<img class="masthead-art" src="https://covers.openlibrary.org/b/id/999-S.jpg" src="{match.group(1)}"',
        )
        with self.assertRaises(release.ArtworkRejected):
            release.check_static_startup(self.root)

    def test_pages_guard_checks_committed_bytes_of_public_lore_modules(self):
        # Publication checks must detect generator/post-checkout tampering of
        # both new source files, not merely certify their internal hash links.
        workflow = (ROOT / ".github/workflows/static.yml").read_text(encoding="utf-8")
        match = re.search(r"for path in (explorer/index\.html .*?); do", workflow)
        self.assertIsNotNone(match, "Pages committed-byte gate not found")
        checked = match.group(1).split()
        for path in ("explorer/lore-public-chat.js", "explorer/lore-semantic-chat.js"):
            self.assertIn(path, checked, f"Pages release did not verify committed bytes: {path}")


if __name__ == "__main__":
    unittest.main()
