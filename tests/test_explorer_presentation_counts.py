"""Cross-lane Explorer *display* numerators, not accepted research denominators.

This test keeps source-local views, opt-in remote cover choices, and the
governed Work/Briefing index separate across optional supplement builds.
"""

import collections
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPLORER = ROOT / "explorer"
PINS = {
    "discovery-catalog.json": "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc",
    "picard-literature-overlay.json": "ab8e5d15f7b33bf1311aec0afb2755322b41bca73978d3c7889f1272dbfe21c8",
    "artwork-catalog-v1.3.json": "f4f51a71e9db95368d03d1db88d07137425c09f7918e4a491c98e0eb6e8cfa2f",
    "picard-jackets-v1.0.json": "85bdc8ebbb348d713d604fb9486c2af091e36d40138587a761ddd93716cd9615",
}


def read(name):
    data = (EXPLORER / name).read_bytes()
    if name in PINS and hashlib.sha256(data).hexdigest() != PINS[name]:
        raise AssertionError(f"Accepted source presentation artifact drift: {name}")
    return json.loads(data)


class ExplorerCountPresentationTests(unittest.TestCase):
    def test_directory_and_literary_view_numerators_are_nonadditive_source_rows(self):
        historical, picard = read("discovery-catalog.json"), read("picard-literature-overlay.json")
        base = historical["rows"]
        supplement = picard["rows"]
        self.assertEqual((historical["row_count"], len(base)), (1214, 1214))
        self.assertEqual((picard["base_directory_row_count"], picard["row_count"], len(supplement)), (1214, 2, 2))
        self.assertEqual(historical["admission_effect"], "NONE")
        self.assertEqual(picard["admission_effect"], "NONE")
        self.assertEqual(picard["coverage_effect"], "NONE")
        self.assertEqual({row["medium"] for row in supplement}, {"LITERATURE"})
        self.assertFalse({row["row_id"] for row in base} & {row["row_id"] for row in supplement})
        self.assertEqual(len(base + supplement), 1216, "a view count only; not 1216 distinct Works")
        self.assertEqual(sum(row["medium"] == "LITERATURE" for row in base), 9)
        self.assertEqual(sum(row["medium"] == "LITERATURE" for row in base + supplement), 11)
        self.assertEqual(collections.Counter(row["candidate_kind"] for row in base
                                             if row["medium"] == "LITERATURE"),
                         {"NOVEL": 4, "FICTIONAL_MEMOIR": 5})

    def test_jacket_options_are_four_historical_plus_two_picard_not_released_local_images(self):
        historic, picard = read("artwork-catalog-v1.3.json"), read("picard-jackets-v1.0.json")
        rows = read("discovery-catalog.json")["rows"] + read("picard-literature-overlay.json")["rows"]
        available_ids = {"directory:" + row["row_id"] for row in rows}
        base_ids = {item["row_id"] for item in historic["artwork"]}
        new_ids = {item["row_id"] for item in picard["artwork"]}
        self.assertEqual((historic["artwork_count"], picard["artwork_count"]), (4, 2))
        self.assertFalse(base_ids & new_ids)
        self.assertEqual(len(base_ids | new_ids), 6)
        self.assertTrue(base_ids | new_ids <= available_ids)
        self.assertEqual(historic["coverage_effect"], picard["coverage_effect"])
        self.assertEqual(picard["work_admission_effect"], "NONE")
        self.assertIs(picard["public_image_bytes_committed"], False)
        self.assertEqual(picard["copyright_status"], "UNDERLYING_JACKET_COPYRIGHT_UNRESOLVED")
        self.assertTrue(all(item["provider"] == "OPEN_LIBRARY_COVERS_API" for item in historic["artwork"] + picard["artwork"]))
        # The fifth historical memoir (Sisko) has no accepted opt-in jacket;
        # the six *options* are not a full literary-cover denominator.
        self.assertNotIn("directory:literature:prh-autobiography-sisko", base_ids | new_ids)

    def test_governed_projection_is_unchanged_and_sidecars_remain_view_only(self):
        index = read("index.json")
        self.assertEqual((len(index["missions"]), len(index["briefings"]), len(index["records"])), (12, 0, 0))
        js = (EXPLORER / "app.js").read_text()
        self.assertIn("[...directoryState.rows, ...picardLiteratureSupplement.rows]", js)
        self.assertIn("for (const row of picardLiteratureSupplement.rows) sourceRows.set(artworkKey(row), row)", js)
        self.assertIn("loadDirectory().then(loadPicardSupplement)", js)
        self.assertIn("loadArtworkCatalog().then(loadPicardJacketCatalog)", js)
        self.assertIn("!artworkState.available || !picardLiteratureSupplement.available", js)
        self.assertIn("No new Works or coverage", js)
        self.assertNotIn("1216", (EXPLORER / "index.json").read_text())


if __name__ == "__main__":
    unittest.main()
