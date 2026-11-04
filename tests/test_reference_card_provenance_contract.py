import copy
import hashlib
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET

from tools.build_reference_card_inputs import (
    CATALOG_PATH,
    PACKET_PATH,
    build_inputs,
)


ROOT = CATALOG_PATH.parent.parent
RENDERER_PATH = ROOT / "proposals/librarian/original-nasa-fallback-20261103/tools/render_original_abstract_art.py"
RENDERER_SPEC = importlib.util.spec_from_file_location("trek_reference_art_renderer_test", RENDERER_PATH)
RENDERER = importlib.util.module_from_spec(RENDERER_SPEC)
RENDERER_SPEC.loader.exec_module(RENDERER)


class ReferenceCardProvenanceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    def test_six_bounded_source_local_inputs(self):
        inputs = build_inputs()
        self.assertEqual(len(inputs), 6)
        self.assertEqual({m: sum(row["medium"] == m for row in inputs) for m in ("EPISODE", "FILM", "LITERATURE")},
                         {"EPISODE": 2, "FILM": 2, "LITERATURE": 2})

    def test_exact_directory_digest_is_pinned(self):
        self.assertEqual(hashlib.sha256(CATALOG_PATH.read_bytes()).hexdigest(), self.packet["accepted_source_catalog_sha256"])

    def test_source_local_not_global_identity(self):
        inputs = build_inputs()
        self.assertTrue(all(x["identity_scope"] == "SOURCE_LOCAL" for x in inputs))
        self.assertTrue(all(x["verification_status"] == "UNVERIFIED_METADATA" for x in inputs))
        self.assertTrue(all(x["admission_effect"] == x["coverage_effect"] == "NONE" for x in inputs))

    def test_narrow_recheck_does_not_promote_to_verified(self):
        inputs = build_inputs()
        rechecked = [r for r in inputs if r["metadata_recheck_status"] == "rechecked_exact"]
        self.assertTrue(rechecked)
        self.assertTrue(all(r["verification_status"] == "UNVERIFIED_METADATA" for r in rechecked))

    def test_edition_identifier_not_parsed_from_publisher_url(self):
        literary = [r for r in build_inputs() if r["medium"] == "LITERATURE"]
        self.assertEqual(len(literary), 2)
        self.assertTrue(any("978" in r["source_reference_url"] for r in literary))
        self.assertTrue(all(r["edition_identifier"] is None for r in literary))

    def test_repeat_execution_is_bytewise_deterministic(self):
        first = json.dumps(build_inputs(), sort_keys=True, ensure_ascii=False).encode()
        second = json.dumps(build_inputs(), sort_keys=True, ensure_ascii=False).encode()
        self.assertEqual(first, second)

    def test_same_title_new_source_id_must_get_different_visual_seed(self):
        self.assertNotEqual(RENDERER.render_card("lead:0000", "EPISODE", "A Title"),
                            RENDERER.render_card("lead:0050", "EPISODE", "A Title"))

    def test_visual_differentiation_and_safe_svg(self):
        images = [RENDERER.render_card(row["source_local_row_id"], row["medium"], row["title"]) for row in build_inputs()]
        self.assertEqual(len(images), len(set(images)))
        for art in images:
            self.assertIn("ABSTRACT PLACEHOLDER", art)
            self.assertIn("NOT OFFICIAL ART", art)
            self.assertNotIn("<image", art.lower())
            self.assertNotIn("<script", art.lower())
            self.assertNotIn("href=", art.lower())
            self.assertNotIn("url(", art.lower())
            parsed = ET.fromstring(art)
            self.assertEqual(parsed.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertEqual({node.tag.split("}")[-1] for node in parsed.iter()}, {"svg", "rect", "circle", "path", "text"})

    def test_renderer_xml_escaping_is_safe(self):
        art = RENDERER.render_card("fixture:0001", "FILM", "Title <script>alert('x')</script>")
        ET.fromstring(art)
        self.assertNotIn("<script", art)

    def test_public_effect_rejected(self):
        packet = copy.deepcopy(self.packet)
        packet["public_release_eligible"] = True
        with self.assertRaises(ValueError):
            build_inputs(packet=packet, catalog=self.catalog)

    def test_fabricated_coverage_rejected(self):
        packet = copy.deepcopy(self.packet)
        packet["accepted_coverage_increment"] = 6
        with self.assertRaises(ValueError):
            build_inputs(packet=packet, catalog=self.catalog)

    def test_source_catalog_claims_canonical_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["identity_scope"] = "CANONICAL_GLOBAL"
        with self.assertRaises(ValueError):
            build_inputs(packet=self.packet, catalog=catalog)

    def test_url_scheme_injection_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        next(row for row in catalog["rows"] if row["row_id"] == "lead:0000")["source_locator"] = "javascript:alert(1)"
        with self.assertRaises(ValueError):
            build_inputs(packet=self.packet, catalog=catalog)

    def test_source_recheck_does_not_authorize_global_verified(self):
        catalog = copy.deepcopy(self.catalog)
        next(row for row in catalog["rows"] if row["row_id"] == "lead:0050")["verification_status"] = "VERIFIED_CANONICAL"
        with self.assertRaises(ValueError):
            build_inputs(packet=self.packet, catalog=catalog)

    def test_duplicate_card_source_ids_rejected(self):
        packet = copy.deepcopy(self.packet)
        packet["sample_source_local_row_ids"][1] = packet["sample_source_local_row_ids"][0]
        with self.assertRaises(ValueError):
            build_inputs(packet=packet, catalog=self.catalog)

    def test_unknown_source_id_rejected(self):
        packet = copy.deepcopy(self.packet)
        packet["sample_source_local_row_ids"][0] = "not-in-accepted:999"
        with self.assertRaises(ValueError):
            build_inputs(packet=packet, catalog=self.catalog)

    def test_genui_artwork_rights_must_stay_separate_from_source_metadata(self):
        packet = copy.deepcopy(self.packet)
        packet["image_or_media_bytes_downloaded"] = True
        with self.assertRaises(ValueError):
            build_inputs(packet=packet, catalog=self.catalog)


if __name__ == "__main__":
    unittest.main()
