"""Publisher source ingestion must not create directories through symlinks."""

from __future__ import annotations

import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import (
    build_legacy_s1_discovery as legacy_s1,
    build_legacy_s2_discovery as legacy_s2,
    build_legacy_s3_discovery as legacy_s3,
    build_prodigy_publisher_discovery as prodigy,
    build_publisher_s4_discovery as season4,
    build_publisher_s5_discovery as season5,
    build_publisher_s6_discovery as season6,
    build_publisher_s7_discovery as season7,
    build_tas_publisher_roster as tas,
    build_prodigy_mikros_s1a_discovery as mikros,
    publisher_output_directory as guard,
)


INGESTERS = (legacy_s1, legacy_s2, legacy_s3, prodigy, season4, season5, season6, season7, tas)
REPO = Path(__file__).resolve().parents[1]


class PublisherOutputDirectoryTests(unittest.TestCase):
    def test_creates_legitimate_nested_directories_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "checkout"
            (root / "proposals").mkdir(parents=True)
            relative = Path("proposals/discovery/legitimate/source-bundle")
            guard.ensure_directory(root, relative)
            guard.ensure_directory(root, relative)
            self.assertTrue((root / relative).is_dir())

    def test_legitimate_season_four_ingestion_creates_and_checks_all_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "checkout"
            source = Path(temporary) / "raw"
            (root / "registry").mkdir(parents=True)
            source.mkdir()
            shutil.copy2(REPO / "registry/mission_catalog.json", root / "registry/mission_catalog.json")
            for mission in season4.SLUGS:
                canonical = season4.official_url(mission)
                cards = "".join(
                    f'<div class="episode"><div class="epTitle"><h2>Card {n}</h2></div>'
                    f'<abbr class="seNum">S4</abbr><abbr class="epNum">E{n}</abbr>'
                    for n in range(1, 6)
                )
                body = f'<html><head><link rel="canonical" href="{canonical}"></head>' \
                       f'<body>{cards}{" " * 11000}</body></html>'
                (source / f"{mission}-s4.html").write_text(body, encoding="utf-8")
            with patch.object(season4, "ROOT", root):
                self.assertEqual(season4.ingest(source), 0)
                self.assertEqual(season4.check(), 0)
            self.assertTrue((root / season4.BASE / "index.json").is_file())

    def test_each_ingester_refuses_symlinked_parent_before_outside_mkdir(self) -> None:
        for module in INGESTERS:
            with self.subTest(ingester=module.__name__), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "checkout"
                outside = Path(temporary) / "outside"
                (root / "proposals").mkdir(parents=True)
                outside.mkdir()
                (root / "proposals/discovery").symlink_to(outside, target_is_directory=True)
                with patch.object(module, "ROOT", root):
                    with self.assertRaises((OSError, ValueError)):
                        module.ingest(Path(temporary))
                self.assertEqual(list(outside.iterdir()), [], "symlinked parent gained a directory")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "checkout"
            outside = Path(temporary) / "outside"
            input_file = Path(temporary) / "source.html"
            (root / "proposals").mkdir(parents=True)
            outside.mkdir()
            input_file.write_bytes(b"private")
            (root / "proposals/discovery").symlink_to(outside, target_is_directory=True)
            with patch.object(mikros, "ROOT", root), patch.object(mikros, "extract", return_value=[]):
                with self.assertRaises((OSError, ValueError)):
                    mikros.ingest(input_file)
            self.assertEqual(list(outside.iterdir()), [], "Mikros followed a symlinked parent")

    def test_existing_output_leaf_symlink_refused_without_outside_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "checkout"
            outside = Path(temporary) / "outside"
            (root / "proposals/discovery").mkdir(parents=True)
            outside.mkdir()
            (root / season4.BASE).symlink_to(outside, target_is_directory=True)
            with patch.object(season4, "ROOT", root):
                with self.assertRaises((OSError, ValueError)):
                    season4.ingest(Path(temporary))
            self.assertEqual(list(outside.iterdir()), [])

    def test_checkout_ancestor_symlink_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            actual = Path(temporary) / "actual"
            (actual / "proposals").mkdir(parents=True)
            shortcut = Path(temporary) / "shortcut"
            shortcut.symlink_to(actual, target_is_directory=True)
            with self.assertRaises((OSError, ValueError)):
                guard.ensure_directory(shortcut, Path("proposals/discovery/new"))
            self.assertFalse((actual / "proposals/discovery").exists())

    def test_root_must_exist_and_relative_path_cannot_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "checkout"
            with self.assertRaises((OSError, ValueError)):
                guard.ensure_directory(root, Path("proposals/discovery"))
            self.assertFalse(root.exists(), "a missing checkout root was unexpectedly created")
            root.mkdir()
            for relative in (Path("../outside"), Path("/tmp/outside"), Path(".")):
                with self.subTest(path=str(relative)):
                    with self.assertRaises(ValueError):
                        guard.ensure_directory(root, relative)


if __name__ == "__main__":
    unittest.main()
