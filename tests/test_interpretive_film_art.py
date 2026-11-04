"""Fail-closed checks for the 14 original source-keyed film illustrations."""

import hashlib
import importlib.util
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/build_interpretive_film_art.py"
SPEC = importlib.util.spec_from_file_location("trek_film_interpretive", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class OriginalFilmArtTests(unittest.TestCase):
    def test_exact_fourteen_reproducible_svg_assets_and_manifest(self):
        files = MODULE.expected()
        self.assertEqual(len(files), 15)
        self.assertEqual(set(MODULE.ART.iterdir()), set(files))
        self.assertTrue(all(path.is_file() and path.read_bytes() == data
                            for path, data in files.items()))
        manifest = json.loads(files[MODULE.ART / "manifest.json"])
        self.assertEqual(manifest["original_art_count"], 14)
        self.assertEqual({row["source_local_film_id"] for row in manifest["art"]},
                         set(MODULE.DESIGNS))
        self.assertTrue(all(row["coverage_effect"] == "NONE" for row in manifest["art"]))
        self.assertEqual(manifest["admission_effect"], "NONE")

    def test_exact_publisher_metadata_and_asset_hash_linkage(self):
        files = MODULE.expected()
        records = json.loads(files[MODULE.ART / "manifest.json"])["art"]
        original = json.loads(MODULE.FILMS.read_text(encoding="utf-8"))
        by_id = {row["id"]: row for row in original["films"]}
        for row in records:
            film = by_id[row["source_local_film_id"]]
            self.assertEqual(row["title"], film["title"])
            self.assertEqual(row["metadata_source"], film["source_locator"])
            artifact = MODULE.ROOT / "explorer" / row["art_path"]
            self.assertEqual(row["art_sha256"], hashlib.sha256(files[artifact]).hexdigest())
            self.assertEqual(row["rights_class"], "ORIGINAL_AUTHOR_CREATED_GEOMETRIC_ART")
            self.assertEqual(row["artwork_status"], "ORIGINAL_INTERPRETATION_NOT_SOURCE_IMAGE")

    def test_svg_has_no_remote_fetch_executable_mark_or_visible_text(self):
        files = MODULE.expected()
        allowed = {"svg", "title", "desc", "defs", "linearGradient", "stop",
                   "rect", "circle", "path"}
        for path, data in files.items():
            if path.suffix != ".svg":
                continue
            root = ET.fromstring(data)
            self.assertEqual({el.tag.split("}")[-1] for el in root.iter()} - allowed, set(), path)
            self.assertNotIn(b"<image", data)
            self.assertNotIn(b"<script", data)
            self.assertNotIn(b"<text", data)
            self.assertNotIn(b"http://", data.replace(b'http://www.w3.org/2000/svg', b''))
            self.assertNotIn(b"https://", data)
            self.assertNotIn(b"starfleet", data.lower())

    def test_rejects_changed_catalog_count_or_identity_without_guessing(self):
        catalog = json.loads(MODULE.FILMS.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            altered = Path(directory) / "films.json"
            catalog["films"][0]["id"] = "new-unreviewed-film"
            altered.write_text(json.dumps(catalog), encoding="utf-8")
            with mock.patch.object(MODULE, "FILMS", altered):
                with self.assertRaises(ValueError):
                    MODULE.expected()

    def test_rejects_unexpected_art_directory_member(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "art"
            target.mkdir()
            (target / "unreviewed.svg").write_text("not allowed", encoding="utf-8")
            with mock.patch.object(MODULE, "ART", target):
                with self.assertRaises(SystemExit):
                    MODULE.main([])

    def test_identical_art_bytes_across_independent_runs(self):
        first = MODULE.expected()
        second = MODULE.expected()
        self.assertEqual(first, second)
        self.assertEqual(len({hashlib.sha256(data).hexdigest() for path, data in first.items()
                              if path.suffix == ".svg"}), 14)


if __name__ == "__main__":
    unittest.main()
