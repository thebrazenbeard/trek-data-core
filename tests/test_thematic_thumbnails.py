"""Adversarial source custody and small-format motif-only art invariants."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("thematic_thumb", ROOT / "tools/build_thematic_thumbnails.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class PictorialThumbnailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = mod.exact_sources()
        cls.expected = mod.expected()

    def test_exact_six_source_local_ids_split_across_three_media(self):
        self.assertEqual(set(mod.REVIEWED), {r["source_local_row_id"] for r in self.rows})
        self.assertEqual({m: [r["medium"] for r in self.rows].count(m) for m in ("EPISODE", "FILM", "LITERATURE")},
                         {"EPISODE": 2, "FILM": 2, "LITERATURE": 2})
        self.assertEqual(mod.frozen_digest(mod.REVIEWED), mod.REVIEWED_BINDINGS_SHA256)
        self.assertEqual(mod.frozen_digest(mod.DRAFT_595_FULL_SIZE), mod.DRAFT_595_FILENAMES_SHA256)
        for r in self.rows:
            self.assertEqual((r["medium"], r["motif_id"], r["thumbnail_name"]), mod.REVIEWED[r["source_local_row_id"]])
            self.assertEqual(r["draft_595_full_size_filename"], mod.DRAFT_595_FULL_SIZE[r["source_local_row_id"]])
            self.assertEqual(r["accepted_metadata_status"], "UNVERIFIED_METADATA")
            self.assertEqual(r["identity_scope"], "SOURCE_LOCAL")
            self.assertEqual((r["admission_effect"], r["coverage_effect"]), ("NONE", "NONE"))
            self.assertEqual(r["official_image_rights_grant"], "NONE")
            self.assertFalse(r["full_media_close_read"])
            self.assertEqual(r["source_image_bytes"], 0)
            self.assertEqual(len(r["source_cue_sha256"]), 1 if r["medium"] == "EPISODE" else 2)
            self.assertTrue(r["source_reference_url"].startswith("https://www."))

    def test_source_metadata_and_scene_mappings_fail_closed_under_alias_swaps(self):
        original = mod.REVIEWED
        for rid, changed in (
            ("lead:0000", ("EPISODE", "tribbles", "doomsday-thumb.svg")),
            ("film:film-2009", ("FILM", "legacy-future", "film-nemesis-thumb.svg")),
            ("film:film-nemesis", ("LITERATURE", "mirror-weapon", "film-nemesis-thumb.svg")),
        ):
            with self.subTest(rid=rid), patch.dict(mod.REVIEWED, {rid: changed}), self.assertRaises(ValueError):
                mod.exact_sources()
        self.assertEqual(original, mod.REVIEWED)

    def test_renamed_595_file_or_injected_record_is_rejected(self):
        with patch.dict(mod.DRAFT_595_FULL_SIZE, {"lead:0000": "tribbles.svg"}), self.assertRaises(ValueError):
            mod.exact_sources()
        with patch.dict(mod.REVIEWED, {"directory:missing": ("FILM", "mirror-weapon", "missing.svg")}), self.assertRaises(ValueError):
            mod.exact_sources()

    def test_mutated_parent_svg_digest_is_rejected_before_any_derivation(self):
        with patch.dict(mod.REVIEWED_PARENT_ART_SHA256, {"lead:0000": "0" * 64}), self.assertRaises(ValueError):
            mod.exact_sources()

    def test_monkeypatched_parent_metadata_only_forgeries_must_fail_closed(self):
        """Frozen SVG pixels must not launder substituted upstream citations."""
        attack_cases = (
            ("episode", "official_publisher_url", "https://evil.example/fake-episode"),
            ("episode", "description_utf8_sha256", "0" * 64),
            ("episode", "publisher_source_scope", "UNVERIFIED_RUMOR"),
            ("film_lit", "source_reference_url", "https://evil.example/fake-film"),
            ("film_lit", "source_cue_sha256", ["0" * 64, "0" * 64]),
            ("film_lit", "source_kind", "UNVERIFIED_RUMOR"),
            ("film_lit", "official_image_rights_grant", "APPROVED_FOR_REHOST"),
            ("film_lit", "public_rights_release_approved", True),
        )
        for origin, field, value in attack_cases:
            if origin == "episode":
                upstream, method, target = mod.episodes, "exact_source_rows", "lead:0000"
            else:
                upstream, method, target = mod.film_lit, "bound_inputs", "film:film-2009"
            rows = copy.deepcopy(getattr(upstream, method)())
            next(row for row in rows if row["source_local_row_id"] == target)[field] = value
            with self.subTest(origin=origin, field=field), patch.object(upstream, method, return_value=rows):
                with self.assertRaises(ValueError):
                    mod.exact_sources()
                with self.assertRaises(ValueError):
                    mod.expected()  # actual generator must not emit forged manifest

    def test_forged_source_rights_title_or_cue_digest_rejected_before_thumb(self):
        original = self.rows[3]
        for field, value in (("title", "Official poster"),
                             ("source_cue_sha256", ["0" * 64]),
                             ("official_image_rights_grant", "GRANTED"),
                             ("coverage_effect", "ADMITTED"),
                             ("source_local_row_id", "film:film-2009")):
            forged = copy.deepcopy(original); forged[field] = value
            raw = (ROOT / original["source_full_art_path"]).read_bytes()
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.thumbnail(raw, forged)

    def test_wrong_full_size_pixels_cannot_be_borrowed_by_another_record(self):
        first, second = self.rows[:2]
        alien_bytes = (ROOT / second["source_full_art_path"]).read_bytes()
        with self.assertRaises(ValueError):
            mod.thumbnail(alien_bytes, first)
        source_bytes = (ROOT / first["source_full_art_path"]).read_bytes()
        with self.assertRaises(ValueError):
            mod.thumbnail(source_bytes.replace(b"#ffbf63", b"#ffbf64"), first)

    def test_thumbnails_preserve_original_geometry_except_poster_text_footer(self):
        for rec in self.rows:
            with self.subTest(motif=rec["motif_id"]):
                old = ET.fromstring((ROOT / rec["source_full_art_path"]).read_bytes())
                new = ET.fromstring(mod.thumbnail((ROOT / rec["source_full_art_path"]).read_bytes(), rec))
                self.assertEqual(new.tag, mod.Q + "svg")
                self.assertEqual(new.attrib["viewBox"], "0 0 800 450")
                self.assertEqual(len(list(new)), 1)
                layer = list(new)[0]
                self.assertEqual(layer.tag, mod.Q + "g")
                self.assertEqual(layer.attrib["transform"], "translate(-100 -9) scale(1.25)")
                expected_shapes = [ET.tostring(ch) for ch in old if ch.tag != mod.Q + "text" and not mod._is_footer(ch)]
                actual_shapes = [ET.tostring(ch) for ch in layer]
                self.assertEqual(expected_shapes, actual_shapes)
                self.assertFalse(any(child.tag == mod.Q + "text" for child in new.iter()))

    def test_no_tiny_title_or_footer_and_no_active_external_media(self):
        allowed = {mod.Q + v for v in ("svg", "g", "defs", "linearGradient", "radialGradient", "stop", "rect", "path", "circle", "ellipse")}
        for rec in self.rows:
            raw = mod.thumbnail((ROOT / rec["source_full_art_path"]).read_bytes(), rec)
            root = ET.fromstring(raw)
            self.assertTrue({node.tag for node in root.iter()} <= allowed)
            self.assertFalse(any(mod._is_footer(ch) for ch in root.iter()))
            self.assertNotIn(b"<text", raw)
            lower = raw.lower()
            for unsafe in (b"<image", b"<script", b"<foreignobject", b"<use ", b"href=", b"javascript:", b"data:"):
                self.assertNotIn(unsafe, lower)

    def test_original_specific_motif_differences_survive_small_format(self):
        motifs = {r["motif_id"]: mod.thumbnail((ROOT / r["source_full_art_path"]).read_bytes(), r).decode() for r in self.rows}
        self.assertEqual(len({hashlib.sha256(v.encode()).hexdigest() for v in motifs.values()}), 6)
        self.assertIn('id="planet"', motifs["doomsday"])
        self.assertGreater(motifs["tribbles"].count("<circle"), 50)
        self.assertIn("#9bcaf0", motifs["legacy-future"])
        self.assertIn("#df5b75", motifs["mirror-weapon"])
        self.assertIn("#f0dbb3", motifs["delta-journal"])
        self.assertGreaterEqual(motifs["accretion-station"].count("<ellipse"), 2)

    def test_manifest_and_art_generated_bytes_exact_not_published(self):
        self.assertEqual(len(self.expected), 7)
        for path, blob in self.expected.items():
            self.assertEqual(path.read_bytes(), blob)
        manifest = json.loads((mod.OUT / "manifest.json").read_text())
        self.assertEqual(manifest["status"], "HELD_ONLY_NO_EXPLORER_PUBLICATION")
        self.assertEqual(manifest["source_parent_art_commit"], "0a14381a01b77966f6c2d1be9b805aaf025d58b4")
        self.assertEqual(manifest["intended_css_slot_widths_px"], [132, 190])
        self.assertEqual(manifest["source_image_bytes"], manifest["admitted_works"])
        self.assertEqual(manifest["admitted_works"], manifest["full_episode_film_or_book_close_reads"])
        self.assertEqual(manifest["full_episode_film_or_book_close_reads"], 0)
        self.assertEqual(manifest["public_release_effect"], "NONE")
        self.assertEqual(manifest["coverage_effect"], "NONE")
        self.assertEqual(len(manifest["records"]), 6)
        self.assertEqual(set((mod.OUT / "art").iterdir()), set(self.expected) - {mod.OUT / "manifest.json"})
        for row in manifest["records"]:
            self.assertEqual(hashlib.sha256((mod.OUT / row["thumbnail_path"]).read_bytes()).hexdigest(), row["thumbnail_sha256"])
            self.assertEqual(hashlib.sha256((ROOT / row["source_full_art_path"]).read_bytes()).hexdigest(), row["source_full_art_sha256"])


if __name__ == "__main__":
    unittest.main()
