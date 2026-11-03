"""Keep Explorer cache-busting URLs tied to the actual published asset bytes."""

from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "explorer"
ASSET_PATTERNS = {
    "app.js": r'<script src="\./app\.js\?v=([0-9a-f]{64})" defer></script>',
    "app.css": r'<link rel="stylesheet" href="\./app\.css\?v=([0-9a-f]{64})">',
    "trek-data-core-hero.jpg": r'<img class="masthead-art" src="\./trek-data-core-hero\.jpg\?v=([0-9a-f]{64})"',
}


def verify_asset_fingerprints(html: str) -> None:
    for filename, pattern in ASSET_PATTERNS.items():
        matches = re.findall(pattern, html)
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one SHA-256 pin for {filename}")
        actual = hashlib.sha256((PUBLIC / filename).read_bytes()).hexdigest()
        if matches[0] != actual:
            raise ValueError(f"Stale asset fingerprint for {filename}")


class ExplorerAssetFingerprintTests(unittest.TestCase):
    def test_published_asset_references_match_exact_committed_bytes(self):
        verify_asset_fingerprints((PUBLIC / "index.html").read_text(encoding="utf-8"))

    def test_stale_or_missing_asset_pin_is_rejected(self):
        html = (PUBLIC / "index.html").read_text(encoding="utf-8")
        for filename, pattern in ASSET_PATTERNS.items():
            digest = re.search(pattern, html).group(1)
            with self.subTest(filename=filename), self.assertRaisesRegex(ValueError, filename):
                verify_asset_fingerprints(html.replace(digest, "0" * 64, 1))


if __name__ == "__main__":
    unittest.main()
