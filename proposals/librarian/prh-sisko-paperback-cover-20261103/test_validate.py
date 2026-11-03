"""Hostile cases for the held paperback jacket crosswalk."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
import unittest

from validate import DIRECTORY, PACKET, ROOT, validate


class SiskoSourceOnlyTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / PACKET, self.root / PACKET,
                        ignore=shutil.ignore_patterns("__pycache__"))
        (self.root / DIRECTORY).parent.mkdir(parents=True)
        shutil.copy2(ROOT / DIRECTORY, self.root / DIRECTORY)

    def assert_rejects(self, explanation: str):
        with self.assertRaises(ValueError, msg=explanation):
            validate(self.root)

    def alter_record(self, key: str, value):
        path = self.root / PACKET / "records.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data[key] = value
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def test_pristine_source_only_packet(self):
        result = validate(self.root)
        self.assertEqual(result["status"], "HELD_SOURCE_ONLY")
        self.assertEqual(result["image_bytes_published"], 0)

    def test_forged_public_release_rejected(self):
        self.alter_record("public_image_display_authorized", True)
        self.assert_rejects("rights cannot be self-certified")

    def test_forged_projected_hardcover_cover_rejected(self):
        path = self.root / PACKET / "records.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["candidate"]["isbn_13"] = "9781803366234"
        data["candidate"]["publisher_image_url"] = "https://covers.openlibrary.org/b/id/14433753-M.jpg"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assert_rejects("different hardcover is not matching paperback")

    def test_accepted_row_drift_rejected(self):
        path = self.root / DIRECTORY
        data = json.loads(path.read_text(encoding="utf-8"))
        row = next(r for r in data["rows"] if r.get("row_id") == "literature:prh-autobiography-sisko")
        row["details"] = ["Hardcover ISBN 9781803366234"]
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assert_rejects("unreviewed source row change")

    def test_unlisted_jpeg_disguised_as_bin_rejected(self):
        (self.root / PACKET / "unreviewed-photo.bin").write_bytes(b"\xff\xd8\xff" + b"pretend")
        self.assert_rejects("no disguised extra binary in a source-only packet")

    def test_nested_approval_claim_rejected(self):
        nested = self.root / PACKET / "owner-approval"
        nested.mkdir()
        (nested / "approved.md").write_text("Cleared for everyone!", encoding="utf-8")
        self.assert_rejects("no nested auto-approval")

    def test_duplicate_json_field_rejected(self):
        path = self.root / PACKET / "records.json"
        raw = path.read_text(encoding="utf-8")
        path.write_text(raw.replace('"batch_id":', '"batch_id": "forged", "batch_id":', 1),
                        encoding="utf-8")
        self.assert_rejects("duplicate key must not be accepted")


if __name__ == "__main__":
    unittest.main()
