"""Hostile regression tests for held, exact-edition Trek eBook jacket records."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import validate_two_ebook_cover_candidates as candidate
import validate_picard_cover_candidates as utilities


class PublisherEbookJacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for path in (candidate.PACKET, candidate.DIRECTORY):
            dest = self.root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, dest)

    def original(self):
        return json.loads((self.root / candidate.PACKET).read_text(encoding="utf-8"))

    def reject(self, change, message):
        current = self.original()
        change(current)
        (self.root / candidate.PACKET).write_text(json.dumps(current), encoding="utf-8")
        with self.assertRaisesRegex(utilities.Rejected, message):
            candidate.validate(self.root)
        shutil.copyfile(ROOT / candidate.PACKET, self.root / candidate.PACKET)

    def test_two_genuine_jackets_remain_held_and_do_not_change_six_live_covers(self):
        receipt = candidate.validate(ROOT)
        self.assertEqual(receipt["status"], "HELD_FOR_INDEPENDENT_REVIEW")
        self.assertEqual(receipt["source_local_ebook_jackets"], 2)
        self.assertEqual(receipt["public_release_effect"], "NONE")
        self.assertEqual(receipt["coverage_effect"], "NONE")
        self.assertEqual(len(json.loads((ROOT / "explorer/picard-jackets-v1.0.json").read_bytes())["artwork"]), 2)

    def test_edition_format_publisher_url_source_row_and_protected_effects_cannot_drift(self):
        for name, change, message in [
            ("replace target ISBN", lambda p: p["candidates"][0].update(isbn="9781982194833"), "exact public publisher"),
            ("trade instead of ebook", lambda p: p["candidates"][0].update(publisher_ebook_format="Trade Paperback"), "exact public publisher"),
            ("false ISBN in source detail", lambda p: p["candidates"][0].update(public_row_edition_detail="Ebook · ISBN 9781982194833"), "exact public publisher"),
            ("cross-title jacket", lambda p: p["candidates"][0].update(public_row_title="Star Trek Discovery Enterprise War"), "exact public publisher"),
            ("hostile publisher URL", lambda p: p["candidates"][1].update(publisher_ebook_locator="https://evil.invalid/9781668002407"), "exact public publisher"),
            ("copyright cleared", lambda p: p.update(underlying_cover_copyright="PUBLIC_DOMAIN"), "held-only"),
            ("publish", lambda p: p.update(public_artwork_release_effect="APPROVED"), "held-only"),
            ("Work", lambda p: p.update(source_work_admission_effect="ACCEPTED"), "held-only"),
            ("full text", lambda p: p.update(coverage_effect="FULL_TEXT_AVAILABLE"), "held-only"),
            ("mirror bytes", lambda p: p.update(image_bytes_committed=True), "held-only"),
        ]:
            with self.subTest(name=name):
                self.reject(change, message)

    def test_actual_pixel_id_hash_dimensions_and_visual_observation_pinned(self):
        for name, change, message in [
            ("audio square substitute", lambda p: p["candidates"][0].update(cover_id=13195854), "reviewer observation|decoded image"),
            ("old interior title page", lambda p: p["candidates"][1].update(cover_id=12857937), "reviewer observation|decoded image"),
            ("cover changed", lambda p: p["candidates"][0].update(medium_preview_url="https://example.com/a.jpg"), "decoded image"),
            ("SHA changed", lambda p: p["candidates"][1].update(large_preview_sha256="f" * 64), "decoded image"),
            ("length changed", lambda p: p["candidates"][1].update(medium_preview_bytes=1), "decoded image"),
            ("dimensions changed", lambda p: p["candidates"][0].update(large_height=500), "decoded image"),
            ("unreviewed OL edition", lambda p: p["candidates"][1].update(openlibrary_edition_id="OL28720619M"), "exact public publisher"),
            ("rights claim", lambda p: p["candidates"][0].update(rights_status="PUBLIC_DISPLAY_PERMISSION_VERIFIED"), "reviewer observation"),
            ("observer fabricated", lambda p: p["candidates"][0].update(image_observer="some-human"), "reviewer observation"),
            ("live release", lambda p: p["candidates"][1].update(release_status="PUBLIC"), "reviewer observation"),
        ]:
            with self.subTest(name=name):
                self.reject(change, message)

    def test_duplicate_unknown_and_unbound_edition_records_rejected(self):
        self.reject(lambda p: p["candidates"].__setitem__(1, copy.deepcopy(p["candidates"][0])),
                    "unknown/duplicate")
        self.reject(lambda p: p["candidates"][0].update(hidden_jpeg="data:image/jpeg;base64,a"),
                    "field contract")
        self.reject(lambda p: p.update(candidate_count=3), "exact two")

    def test_original_public_directory_drift_and_duplicate_json_keys_rejected(self):
        path = self.root / candidate.DIRECTORY
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(utilities.Rejected, "directory bytes drifted"):
            candidate.validate(self.root)
        shutil.copyfile(ROOT / candidate.DIRECTORY, path)
        packet_path = self.root / candidate.PACKET
        packet_path.write_bytes(packet_path.read_bytes().replace(
            b'"candidate_count": 2,', b'"candidate_count": 2, "candidate_count": 2,'))
        with self.assertRaisesRegex(utilities.Rejected, "duplicate JSON key"):
            candidate.validate(self.root)


if __name__ == "__main__":
    unittest.main()
