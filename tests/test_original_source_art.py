"""Hostile boundaries for HELD original source-local illustration proposals."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "validate_original_source_art", BASE / "tools/validate_original_source_art.py"
)
assert spec and spec.loader
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class OriginalSourceArtBoundary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "explorer/original-source-art").mkdir(parents=True)
        for name in ("index.html", "app.js", "app.css", "discovery-catalog.json", "film-catalog.json"):
            shutil.copyfile(BASE / "explorer" / name, self.root / "explorer" / name)
        for file in (BASE / "explorer/original-source-art").iterdir():
            shutil.copyfile(file, self.root / "explorer/original-source-art" / file.name)
        self.original_root = gate.ROOT
        self.original_assets = gate.ASSETS
        gate.ROOT = self.root
        gate.ASSETS = self.root / "explorer/original-source-art"
        self.addCleanup(self.restore_globals)

    def restore_globals(self):
        gate.ROOT = self.original_root
        gate.ASSETS = self.original_assets

    def test_exact_seven_publicly_bounded_original_svg_assets(self):
        self.assertEqual(gate.validate(), 7)

    def test_mutated_image_bytes_fail_even_if_svg_stays_well_formed(self):
        path = gate.ASSETS / "doomsday.svg"
        path.write_bytes(path.read_bytes().replace(b"#121a39", b"#131a39", 1))
        with self.assertRaisesRegex(ValueError, "altered bytes"):
            gate.validate()

    def test_extra_media_or_remote_script_candidate_fails(self):
        (gate.ASSETS / "unreviewed.svg").write_text('<svg><script>alert(1)</script></svg>')
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            gate.validate()

    def test_metadata_identifier_cannot_inherit_another_image(self):
        path = self.root / "explorer/discovery-catalog.json"
        catalog = json.loads(path.read_text())
        target = next(row for row in catalog["rows"] if row["row_id"] == "lead:0000")
        target["source_locator"] = "https://example.com/unrelated-identical-title"
        path.write_text(json.dumps(catalog))
        with self.assertRaisesRegex(ValueError, "identity/locator"):
            gate.validate()

    def test_additional_css_key_without_pinned_code_owned_receipt_fails(self):
        path = self.root / "explorer/app.js"
        script = path.read_text()
        script = script.replace(
            "const proposedOriginalArt = new Map([",
            "const proposedOriginalArt = new Map([\n    ['directory:fake', ['EPISODE', 'Fake', 'https://example.com', 'fake.svg', null]],",
            1,
        )
        path.write_text(script)
        with self.assertRaisesRegex(ValueError, "receipt count"):
            gate.validate()

    def test_css_cannot_swap_in_offsite_or_unreviewed_image(self):
        path = self.root / "explorer/app.css"
        stylesheet = path.read_text().replace(
            "url('./original-source-art/doomsday.svg')",
            "url('https://example.com/official-frame.jpg')", 1,
        )
        path.write_text(stylesheet)
        with self.assertRaisesRegex(ValueError, "safe CSS presentation"):
            gate.validate()

    def test_javascript_cannot_rebind_a_motif_to_similar_title_row(self):
        path = self.root / "explorer/app.js"
        script = path.read_text().replace(
            "'directory:lead:0000', ['EPISODE'",
            "'directory:publisher-paramount-plus:tos-doomsday-machine', ['EPISODE'", 1,
        )
        path.write_text(script)
        with self.assertRaisesRegex(ValueError, "source-locked JS artwork receipt"):
            gate.validate()

    def test_late_javascript_map_set_cannot_crosswire_two_episode_rows(self):
        path = self.root / "explorer/app.js"
        script = path.read_text().replace(
            "  function artworkKey(row) {",
            "  proposedOriginalArt.set('directory:lead:0000', proposedOriginalArt.get('directory:lead:0001'));\n  function artworkKey(row) {", 1,
        )
        path.write_text(script)
        with self.assertRaisesRegex(ValueError, "effective Explorer .* digest"):
            gate.validate()

    def test_late_css_specificity_override_cannot_crosswire_original_art(self):
        path = self.root / "explorer/app.css"
        path.write_text(path.read_text() +
            "\n.artwork-slot.artwork-original-doomsday { background-image: url('./original-source-art/tribbles.svg'); }\n")
        with self.assertRaisesRegex(ValueError, "effective Explorer .* digest"):
            gate.validate()

    def test_early_resolver_return_cannot_reuse_one_artwork_for_all_rows(self):
        path = self.root / "explorer/app.js"
        script = path.read_text().replace(
            "  function sourceLocalOriginalArt(medium, key, row) {",
            "  function sourceLocalOriginalArt(medium, key, row) {\n"
            "    return { assetClass: 'artwork-original-doomsday', thematicSource: null };", 1,
        )
        path.write_text(script)
        with self.assertRaisesRegex(ValueError, "effective Explorer .* digest"):
            gate.validate()


if __name__ == "__main__":
    unittest.main()
