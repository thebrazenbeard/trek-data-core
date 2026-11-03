"""Held Picard jacket crosswalk: source-local, never a cover-release grant."""
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
import validate_picard_cover_candidates as mod


class PicardJacketCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for path in (mod.PACKET, mod.OVERLAY, mod.PUBLISHER):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)

    def packet(self):
        return json.loads((self.root / mod.PACKET).read_text(encoding="utf-8"))

    def reject(self, mutate, message):
        packet = self.packet()
        mutate(packet)
        (self.root / mod.PACKET).write_text(json.dumps(packet), encoding="utf-8")
        with self.assertRaisesRegex(mod.Rejected, message):
            mod.validate(self.root)
        shutil.copyfile(ROOT / mod.PACKET, self.root / mod.PACKET)

    def test_accepted_exact_source_local_covers_are_still_held(self):
        result = mod.validate(ROOT)
        self.assertEqual(result["source_local_jackets"], 2)
        self.assertEqual(result["status"], "HELD_FOR_INDEPENDENT_REVIEW")
        self.assertEqual(result["public_release_effect"], "NONE")

    def test_publisher_crosswalk_and_protected_effect_mutations_fail_closed(self):
        for label, change, message in (
            ("wrong ISBN", lambda x: x["candidates"][0].update(isbn="9781982154074"), "exact publisher"),
            ("publisher title", lambda x: x["candidates"][0].update(publisher_title="Rogue Elements"), "exact publisher"),
            ("wrong source", lambda x: x["candidates"][1].update(source_locator="https://example.com"), "exact publisher"),
            ("release flag", lambda x: x.update(public_artwork_release_effect="PUBLISHED"), "held status"),
            ("new coverage", lambda x: x.update(coverage_effect="CLOSE_READ"), "held status"),
            ("copyright claim", lambda x: x.update(underlying_cover_copyright="CLEARED"), "held status"),
            ("external fetch", lambda x: x.update(image_bytes_committed=True), "held status"),
        ):
            with self.subTest(label=label):
                self.reject(change, message)

    def test_image_and_authority_mutations_fail_closed(self):
        for label, change, message in (
            ("cover substituted", lambda x: x["candidates"][1].update(cover_id=10691195), "exact publisher"),
            ("wrong size", lambda x: x["candidates"][1].update(medium_width=160), "image rights"),
            ("image URL switched", lambda x: x["candidates"][0].update(medium_preview_url="https://bad.test/c.jpg"), "unreviewed preview"),
            ("missing image hash", lambda x: x["candidates"][0].update(large_preview_sha256="f" * 63), "preview digest"),
            ("forged plausible hash", lambda x: x["candidates"][0].update(medium_preview_sha256="f" * 64), "preview digest"),
            ("rights upgraded", lambda x: x["candidates"][1].update(rights_status="PUBLIC_DOMAIN"), "image rights"),
            ("wrong status", lambda x: x["candidates"][1].update(release_status="PUBLIC"), "image rights"),
            ("duplicate", lambda x: x["candidates"].__setitem__(1, copy.deepcopy(x["candidates"][0])), "unknown/duplicate"),
        ):
            with self.subTest(label=label):
                self.reject(change, message)

    def test_baseline_publisher_overlay_drift_rejected(self):
        path = self.root / mod.OVERLAY
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(mod.Rejected, "bytes drifted"):
            mod.validate(self.root)

    def test_extra_unknown_fields_and_duplicate_json_keys_rejected(self):
        self.reject(lambda x: x["candidates"][0].update(image_data="data:image/jpeg;base64,bad"),
                    "field contract")
        path = self.root / mod.PACKET
        raw = path.read_text(encoding="utf-8")
        path.write_text(raw.replace('"candidate_count": 2,', '"candidate_count": 2, "candidate_count": 2,'),
                        encoding="utf-8")
        with self.assertRaisesRegex(mod.Rejected, "duplicate JSON key"):
            mod.validate(self.root)


if __name__ == "__main__":
    unittest.main()
