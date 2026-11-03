"""Fail-closed Scouts first-party video metadata discovery and projection tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import build_scouts_publisher_discovery as scouts

ROOT = Path(__file__).resolve().parents[1]


class ScoutsPublisherTests(unittest.TestCase):
    def fixture(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        parent = Path(temp.name)
        root = parent / "checkout"
        root.mkdir()
        raw = parent / "raw"
        raw.mkdir()
        announcement = ('<html><head><link rel="canonical" href="' + scouts.ANNOUNCEMENT_URL +
                        '" /></head><body>Star Trek: Scouts has a 20-episode order.' +
                        (" " * 101_000) + '</body></html>')
        (raw / scouts.ANNOUNCEMENT_FILE).write_text(announcement, encoding="utf-8")
        captured = json.loads((ROOT / scouts.SOURCE).read_text(encoding="utf-8"))
        for name in scouts.SECONDARY:
            parts = [f'<iframe src="https://www.youtube.com/embed/{ident}"></iframe>'
                     for strand, number, ident, key in scouts.VIDEO_IDS if key == name]
            (raw / f"trek-scouts-trekcore-{name}.html").write_text(
                '<html>' + ''.join(parts) + (' ' * 11_000) + '</html>', encoding="utf-8")
        for old, (_, _, ident, _) in zip(captured["videos"], scouts.VIDEO_IDS):
            blob = {"title": old["title"], "author_name": scouts.AUTHOR,
                    "author_url": scouts.AUTHOR_URL, "provider_name": "YouTube",
                    "provider_url": "https://www.youtube.com/",
                    "html": f'<iframe src="https://www.youtube.com/embed/{ident}?x=1"></iframe>'}
            (raw / f"trek-scouts-oembed-{ident}.json").write_text(json.dumps(blob), encoding="utf-8")
        return root, raw

    def test_real_snapshot_receipts_remain_candidate_only(self):
        self.assertEqual(scouts.check(), 0)
        sources = json.loads((ROOT / scouts.SOURCE).read_text(encoding="utf-8"))
        rows = json.loads((ROOT / scouts.OUTPUT).read_text(encoding="utf-8"))
        self.assertEqual(len(sources["videos"]), 20)
        self.assertEqual(rows["short_candidate_count"], 20)
        self.assertEqual(rows["source_sha256"], scouts._digest((ROOT / scouts.SOURCE).read_bytes()))
        self.assertTrue(all(r["accepted_work_id"] is None and
                            r["verification_status"] == "UNVERIFIED_METADATA" for r in rows["short_candidates"]))
        self.assertEqual({r["strand"] for r in rows["short_candidates"]},
                         {"ASTEROID_BLASTERS", "HOLODECK_RESCUES"})
        self.assertTrue(all(r["watch_url"].startswith("https://www.youtube.com/watch?v=")
                            for r in sources["videos"]))
        self.assertTrue(all(len(r["sha256"]) == 64 and r["byte_count"] >= 100
                            for r in sources["videos"]))
        self.assertEqual(sources["admission_effect"], "NONE")
        self.assertEqual(sources["coverage_effect"], "NONE")

    def test_synthetic_offline_replay_and_tamper_detected(self):
        root, raw = self.fixture()
        self.assertEqual(scouts.ingest(raw, root), 0)
        output = root / scouts.OUTPUT
        output.write_bytes(output.read_bytes().replace(b'"DISCOVERY_ONLY"', b'"ACCEPTED"'))
        with self.assertRaisesRegex(ValueError, "differ"):
            scouts.check(root)

    def test_spoofed_publisher_oembed_rejected(self):
        root, raw = self.fixture()
        path = raw / f"trek-scouts-oembed-{scouts.VIDEO_IDS[0][2]}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["author_name"] = "Impersonator"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "first-party publisher"):
            scouts.ingest(raw, root)
        self.assertFalse((root / scouts.BASE).exists())

    def test_forged_official_canonical_link_rejected(self):
        root, raw = self.fixture()
        path = raw / scouts.ANNOUNCEMENT_FILE
        page = path.read_text(encoding="utf-8")
        path.write_text(page.replace(scouts.ANNOUNCEMENT_URL, "https://evil.example/"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "canonical"):
            scouts.ingest(raw, root)

    def test_symlinked_output_directory_refused_without_outside_write(self):
        root, raw = self.fixture()
        external = root.parent / "external"
        external.mkdir()
        (root / "proposals/discovery").mkdir(parents=True)
        (root / scouts.BASE).symlink_to(external, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            scouts.ingest(raw, root)
        self.assertEqual(list(external.iterdir()), [])

    def test_source_symlink_refused_without_output(self):
        root, raw = self.fixture()
        first = raw / f"trek-scouts-oembed-{scouts.VIDEO_IDS[0][2]}.json"
        other = raw / "other.json"
        first.rename(other)
        first.symlink_to(other)
        with self.assertRaisesRegex(ValueError, "symlink source"):
            scouts.ingest(raw, root)
        self.assertFalse((root / scouts.BASE).exists())


if __name__ == "__main__":
    unittest.main()
