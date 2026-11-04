"""Fail-closed original art for 22 source-local TNG season-two metadata records."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/build_interpretive_episode_art.py"
SPEC = importlib.util.spec_from_file_location("trek_episode_interpretive", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class OriginalEpisodeArtTests(unittest.TestCase):
    def test_exact_twenty_two_byte_reproducible_assets(self):
        files = MODULE.expected()
        self.assertEqual(len(files), 23)
        self.assertEqual(set(MODULE.ART.iterdir()), set(files))
        self.assertTrue(all(path.is_file() and path.read_bytes() == data
                            for path, data in files.items()))
        manifest = json.loads(files[MODULE.ART / "manifest.json"])
        self.assertEqual(manifest["original_art_count"], 22)
        self.assertEqual(manifest["coverage_effect"], "NONE")
        self.assertEqual(manifest["admission_effect"], "NONE")
        self.assertTrue(all(row["coverage_effect"] == "NONE" and
                            row["admission_effect"] == "NONE" for row in manifest["art"]))

    def test_exact_accepted_discovery_source_tuples_and_sha_links(self):
        files = MODULE.expected()
        catalog = json.loads(MODULE.CATALOG.read_text(encoding="utf-8"))
        by_id = {row["row_id"]: row for row in catalog["rows"]}
        manifest = json.loads(files[MODULE.ART / "manifest.json"])
        for entry in manifest["art"]:
            actual = by_id[entry["source_local_row_id"]]
            self.assertEqual(entry["title"], actual["title"])
            self.assertEqual(entry["source_locator"], actual["source_locator"])
            self.assertEqual(entry["source_group"], actual["source_group"])
            self.assertEqual(entry["context"], actual["context"])
            self.assertEqual(entry["source_input"], actual["source_input"])
            self.assertEqual(entry["art_sha256"], hashlib.sha256(
                files[MODULE.ROOT / "explorer" / entry["art_path"]]).hexdigest())
            self.assertEqual(entry["artwork_status"], "ORIGINAL_TITLE_INTERPRETATION_NOT_SOURCE_IMAGE")
            self.assertEqual(entry["interpretive_basis"], "TITLE_ONLY")
            self.assertTrue(entry["motif_note"].strip())

    def test_all_svg_unique_and_resource_inert_without_visible_text(self):
        files = MODULE.expected()
        svgs = [data for path, data in files.items() if path.suffix == ".svg"]
        self.assertEqual(len({hashlib.sha256(data).hexdigest() for data in svgs}), 22)
        allowed = {"svg", "title", "desc", "defs", "linearGradient", "stop", "rect", "circle", "path"}
        for data in svgs:
            root = ET.fromstring(data)
            self.assertFalse({tag.tag.split("}")[-1] for tag in root.iter()} - allowed)
            for forbidden in (b"<image", b"<script", b"<text", b"<foreignObject", b"https://", b"starfleet"):
                self.assertNotIn(forbidden, data.lower())

    def test_source_tuple_title_swap_and_locator_swap_fail_closed(self):
        catalog = json.loads(MODULE.CATALOG.read_text(encoding="utf-8"))
        rows = [row for row in catalog["rows"] if row["row_id"].startswith("legacy:s2:tng:")]
        self.assertEqual(len(rows), 22)
        for change in ("title", "source_locator", "source_group", "context", "verification_status"):
            tampered = json.loads(json.dumps(catalog))
            row = next(item for item in tampered["rows"] if item["row_id"] == "legacy:s2:tng:000")
            row[change] = "forged-entry"
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "catalog.json"
                path.write_text(json.dumps(tampered), encoding="utf-8")
                with mock.patch.object(MODULE, "CATALOG", path):
                    with self.assertRaises(ValueError):
                        MODULE.expected()

    def test_extra_directory_member_and_symlink_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "episode-art"
            path.mkdir()
            (path / "unreviewed.svg").write_text("not admitted", encoding="utf-8")
            with mock.patch.object(MODULE, "ART", path):
                with self.assertRaises(SystemExit):
                    MODULE.main([])

    def test_independent_rebuild_is_identical(self):
        self.assertEqual(MODULE.expected(), MODULE.expected())


if __name__ == "__main__":
    unittest.main()
