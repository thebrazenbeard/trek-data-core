"""Hostile checks: four publisher-cue-bound originals, zero rights/coverage elevation."""

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
SPEC = importlib.util.spec_from_file_location("thematic_film_lit", ROOT / "tools/build_thematic_film_literature_art.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class FilmLiteratureThematicArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = mod.bound_inputs()
        cls.expected = mod.expected()

    def test_four_exact_source_local_rows_no_global_admission_or_close_read(self):
        self.assertEqual({r["source_local_row_id"] for r in self.rows}, set(mod.SOURCE_PINS))
        self.assertEqual([r["medium"] for r in self.rows].count("FILM"), 2)
        self.assertEqual([r["medium"] for r in self.rows].count("LITERATURE"), 2)
        for row in self.rows:
            self.assertEqual((row["title"], row["source_reference_url"]), mod.SOURCE_PINS[row["source_local_row_id"]])
            self.assertEqual(row["verification_status"], "UNVERIFIED_METADATA")
            self.assertEqual(row["identity_scope"], "SOURCE_LOCAL")
            self.assertEqual(row["source_text_scope"], "SHORT_EXACT_FIRST_PARTY_PAGE_CUES_NOT_FULL_FILM_OR_BOOK")
            self.assertIsNone(row["publisher_page_full_html_sha256"])
            self.assertIsNone(row["edition_identifier"])
            self.assertFalse(row["film_or_book_close_read"])
            self.assertFalse(row["publisher_edition_listing_admitted"])
            self.assertEqual(row["official_image_rights_grant"], "NONE")
            self.assertEqual((row["admission_effect"], row["coverage_effect"]), ("NONE", "NONE"))
            self.assertEqual(row["art_class"], "ORIGINAL_INTERPRETIVE_GEOMETRY_NOT_SOURCE_IMAGE")

    def test_publisher_selected_listings_pinned_without_edition_equivalence(self):
        for row in self.rows:
            edition = row["publisher_page_edition_listing"]
            if row["medium"] == "FILM":
                self.assertIsNone(edition)
            else:
                self.assertEqual(edition, mod.PAGE_EDITION_LISTINGS[row["source_local_row_id"]])
                self.assertEqual(len(edition["publisher_listed_isbn13"]), 13)
                self.assertIsNone(row["edition_identifier"])
        self.assertEqual(mod.PAGE_EDITION_LISTINGS["literature:prh-autobiography-janeway"]["publisher_listed_isbn13"], "9781789095333")
        self.assertEqual(mod.PAGE_EDITION_LISTINGS["literature:proposed-lit-snw-ring-of-fire"]["publisher_listed_isbn13"], "9781668095898")

    def test_two_exact_publisher_cues_per_motif_with_independent_digests(self):
        for row in self.rows:
            rid = row["source_local_row_id"]
            self.assertEqual(len(row["source_cues"]), 2)
            self.assertEqual(len(row["motif_evidence_links"]), 2)
            self.assertEqual([x["cue_index"] for x in row["motif_evidence_links"]], [0, 1])
            for cue, digest in zip(row["source_cues"], row["source_cue_sha256"]):
                self.assertEqual(hashlib.sha256(cue.encode("utf-8")).hexdigest(), digest)
            self.assertEqual(tuple(row["source_cue_sha256"]), mod.EXCERPT_PINS[rid])
            self.assertTrue(all(link["illustrative_element"] for link in row["motif_evidence_links"]))

    def test_mutated_claims_fail_closed_before_generation(self):
        original = mod.CLAIMS
        for field, value in (
            ("row_id", "literature:unbound-book"),
            ("medium", "FILM"),
            ("excerpts", ("accretion disk of a black hole", "a novel imagined spaceship battle")),
            ("excerpts", ("unverified fake source", "another fake source")),
            ("motif_elements", ("artwork copied from cover",)),
        ):
            forged = copy.deepcopy(original[-1]); forged[field] = value
            try:
                mod.CLAIMS = (*original[:-1], forged)
                with self.subTest(field=field, value=value), self.assertRaises((ValueError, KeyError)):
                    mod.bound_inputs()
            finally:
                mod.CLAIMS = original

    def test_source_kind_section_and_visual_claim_mutations_are_rejected(self):
        original = mod.CLAIMS
        for field, value in (
            ("source_kind", "FILM_SCREENPLAY_FULLY_READ"),
            ("section", "Official movie still file"),
            ("motif_elements", ("an official film poster", "a licensed starship depiction")),
            ("motif_id", "mirror-weapon"),  # valid art ID but wrong source
            ("motif_id", "mystery-unrenderable-theme"),
            ("extra_license_claim", "OFFICIAL_COVER_CLEARED"),
        ):
            forged = copy.deepcopy(original[0]); forged[field] = value
            try:
                mod.CLAIMS = (forged, *original[1:])
                with self.subTest(field=field), self.assertRaises(ValueError):
                    mod.bound_inputs()
            finally:
                mod.CLAIMS = original

    def test_scene_body_cannot_be_reassigned_under_a_pinned_motif(self):
        with patch.dict(mod.SCENES, {"legacy-future": mod._mirror_weapon}):
            with self.assertRaises(ValueError):
                mod.render(self.rows[0])

    def test_public_publisher_page_isbn_cannot_mutate_without_review(self):
        rid = "literature:prh-autobiography-janeway"
        for field, value in (("publisher_listed_isbn13", "9780000000000"),
                             ("publisher_approved_source_image", True)):
            forged = {**mod.PAGE_EDITION_LISTINGS[rid], field: value}
            with self.subTest(field=field), patch.dict(mod.PAGE_EDITION_LISTINGS, {rid: forged}), self.assertRaises(ValueError):
                mod.bound_inputs()

    def test_legacy_label_is_not_occluded_by_lower_footer(self):
        svg = ET.fromstring(mod.render(self.rows[0]))
        captions = [x for x in svg.iter() if x.tag.endswith("}text") and (x.text or "").strip() == "LEGACY"]
        self.assertEqual(len(captions), 1)
        labels = captions[0]
        # SVG text y is baseline; place it above the warm path near x74
        # (approximately y320) as well as well clear of footer y348.
        self.assertLessEqual(float(labels.attrib["y"]), 300)

    def test_mutated_librarian_source_contract_fails_even_if_https(self):
        original = mod.librarian.build_inputs()
        for field, value in (
            ("title", "Art from an unrelated film"),
            ("source_reference_url", "https://www.fake-first-party-site.example/film"),
            ("verification_status", "CLOSE_READ"),
            ("edition_identifier", "9781668095898"),
            ("identity_scope", "GLOBAL"),
            ("coverage_effect", "ADMITTED"),
        ):
            forged = copy.deepcopy(original)
            row = next(x for x in forged if x["source_local_row_id"] == "literature:proposed-lit-snw-ring-of-fire")
            row[field] = value
            with self.subTest(field=field), patch.object(mod.librarian, "build_inputs", return_value=forged), self.assertRaises(ValueError):
                mod.bound_inputs()

    def test_renderer_rejects_payloads_that_claim_licenses_or_an_edition(self):
        for field, value in (
            ("title", "Cited as an official still"),
            ("motif_id", "unknown-cover-copy"),
            ("edition_identifier", "9781789095333"),
            ("official_image_rights_grant", "APPROVED"),
            ("film_or_book_close_read", True),
            ("coverage_effect", "DONE"),
        ):
            forged = copy.deepcopy(self.rows[-1]); forged[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.render(forged)

    def test_four_distinct_nontrivial_safe_svg_motifs(self):
        signatures = set()
        for row in self.rows:
            svg = mod.render(row).decode("utf-8")
            signatures.add(hashlib.sha256(svg.encode()).hexdigest())
            root = ET.fromstring(svg)
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            tags = {node.tag.split("}")[-1] for node in root.iter()}
            self.assertTrue(tags <= {"svg", "rect", "path", "circle", "ellipse", "text"})
            self.assertGreaterEqual(svg.count("<path ") + svg.count("<ellipse "), 4)
            self.assertIn("ORIGINAL THEMATIC INTERPRETATION", svg)
            self.assertIn("NOT OFFICIAL ART", svg)
            self.assertIn("NO FILM/BOOK CLOSE READ", svg)
            for unsafe in ("<image", "<script", "<foreignobject", "href=", "javascript:", "data:", "<use "):
                self.assertNotIn(unsafe, svg.lower())
        self.assertEqual(len(signatures), 4)
        self.assertGreater(mod.render(self.rows[0]).decode().count('stroke="#9bcaf0"'), 0)  # crossing paths
        self.assertIn('fill="#df5b75"', mod.render(self.rows[1]).decode())  # mirrored weapon
        self.assertIn("A JOURNEY RECORDED", mod.render(self.rows[2]).decode())  # journal
        self.assertGreaterEqual(mod.render(self.rows[3]).decode().count("<ellipse "), 2)  # accretion disk

    def test_manifest_images_byte_exact_with_no_untracked_generated_pixels(self):
        self.assertEqual(len(self.expected), 5)
        self.assertEqual({p.name for p in self.expected}, {"manifest.json", *{id + ".svg" for id in mod.SCENES}})
        for p, data in self.expected.items():
            self.assertEqual(p.read_bytes(), data)
        records = json.loads((mod.OUT / "manifest.json").read_text())["records"]
        manifest = json.loads((mod.OUT / "manifest.json").read_text())
        self.assertEqual(len(records), 4)
        for key, expected in (("source_image_bytes", 0), ("admitted_works", 0),
                              ("coverage_effect", "NONE"), ("public_release_effect", "NONE"),
                              ("film_or_book_close_reads", 0), ("edition_equivalence_asserted", False)):
            self.assertEqual(manifest[key], expected)
        self.assertEqual(set((mod.OUT / "art").iterdir()), set(self.expected) - {mod.OUT / "manifest.json"})
        for rec in records:
            p = mod.OUT / rec["art_path"]
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), rec["art_sha256"])
            self.assertEqual(rec["admission_effect"], "NONE")
            self.assertFalse(rec["publisher_edition_listing_admitted"])


if __name__ == "__main__":
    unittest.main()
