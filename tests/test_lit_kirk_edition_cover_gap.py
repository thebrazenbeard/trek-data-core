"""Negative admission and jacket-crosswalk regressions for Kirk format observations."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "proposals" / "research" / "lit" / "kirk-edition-cover-metadata-20261103"
SPEC = importlib.util.spec_from_file_location("lit_kirk_cover_gap", BATCH / "validate.py")
assert SPEC is not None and SPEC.loader is not None  # test-loader invariant, not an admission gate
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class KirkEditionCoverGapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((BATCH / "records.json").read_text(encoding="utf-8"))

    def changed(self):
        return copy.deepcopy(self.source)

    def assert_reject(self, change):
        data = self.changed()
        change(data)
        with self.assertRaises((ValueError, KeyError)):
            MODULE.validate_records(data)

    def test_valid_source_local_gap(self):
        MODULE.validate_records(self.source)
        MODULE.validate_directory(self.source)

    def test_cover_cannot_cross_formatted_isbn(self):
        self.assert_reject(lambda d: d["edition_observations"][0].update(
            cover_link_locator=d["edition_observations"][1]["cover_link_locator"]))

    def test_hardcover_is_not_the_paperback_directory_row(self):
        self.assert_reject(lambda d: d["candidate_directory_row"].update(isbn13="9781783297467"))

    def test_no_public_display_rights_promotion(self):
        self.assert_reject(lambda d: d["edition_observations"][0].update(
            cover_display_rights="PUBLIC_DISPLAY_PERMISSION_VERIFIED"))

    def test_no_content_read_promotion(self):
        self.assert_reject(lambda d: d.update(book_content_read=True))

    def test_no_coverage_or_binding_promotion(self):
        for field in ("coverage_effect", "accepted_source_work_binding_effect", "public_artwork_release_effect"):
            self.subTest(field=field)
            self.assert_reject(lambda d, f=field: d.update({f: "ADMITTED"}))

    def test_no_fake_open_library_cover_id(self):
        self.assert_reject(lambda d: d["catalog_crosscheck"].update(cover_id=12345))

    def test_no_marketing_year_as_narrative_truth(self):
        self.assert_reject(lambda d: d["promotional_description_discrepancy"][0].update(
            narrative_truth_effect="FACT"))

    def test_reject_url_with_credentials(self):
        self.assert_reject(lambda d: d["edition_observations"][0].update(
            cover_link_locator="https://secret@images1.penguinrandomhouse.com/cover/9781783297481"))

    def test_reject_extra_public_fields_at_every_record_level(self):
        mutants = [
            lambda d: d.update(private_source_path=r"C:\Users\Example\Private\book.lit"),
            lambda d: d["candidate_directory_row"].update(image_url="https://example.org/cover.jpg"),
            lambda d: d["catalog_crosscheck"].update(rights_basis="RIGHTS_HOLDER_PERMISSION"),
            lambda d: d["promotional_description_discrepancy"][0].update(
                private_source_path="/home/example/books/book.epub"),
            lambda d: d["edition_observations"][0].update(image_bytes="data:image/jpeg;base64,AAAA"),
        ]
        for mutate in mutants:
            with self.subTest(mutate=mutate.__code__.co_firstlineno):
                self.assert_reject(mutate)

    def test_provider_must_be_exact_observed_label(self):
        self.assert_reject(lambda d: d["edition_observations"][0].update(
            edition_metadata_provider=r"C:\Users\Example\Private\metadata"))
        self.assert_reject(lambda d: d["edition_observations"][1].update(
            edition_metadata_provider="Publisher permission verified"))

    def test_unresolved_gates_cannot_be_substituted(self):
        self.assert_reject(lambda d: d["unresolved_gates"].__setitem__(0, "RIGHTS_CLEARED"))
        self.assert_reject(lambda d: d["unresolved_gates"].append("PUBLISHED"))

    def test_catalog_notes_cannot_carry_private_paths(self):
        self.assert_reject(lambda d: d["catalog_crosscheck"].update(
            note=r"C:\Users\Example\OneDrive\Books\book.lit"))

    def test_optimized_python_executes_all_gates(self):
        result = subprocess.run(
            [sys.executable, "-O", str(BATCH / "validate.py")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("LIT_EDITION_COVER_GAP_OK", result.stdout)

    def test_optimized_python_rejects_coverage_tamper(self):
        code = (
            "import importlib.util,json,pathlib; "
            f"p=pathlib.Path({str(BATCH / 'validate.py')!r}); "
            "s=importlib.util.spec_from_file_location('kirk_gap',p); "
            "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
            "d=json.loads((p.parent/'records.json').read_text()); "
            "d['coverage_effect']='ADMITTED'; "
            "m.validate_records(d)"
        )
        result = subprocess.run(
            [sys.executable, "-O", "-c", code], cwd=ROOT,
            capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(result.returncode, 0, "optimized mode disabled the admission gate")
        self.assertIn("ValueError: forbidden effect coverage_effect", result.stderr)

    def test_optimized_python_rejects_private_path_rights_provider_and_hold_mutants(self):
        mutants = [
            "d['private_source_path']='C:/Users/Example/Private/book.lit'",
            "d['candidate_directory_row']['image_url']='https://example.org/cover.jpg'",
            "d['catalog_crosscheck']['rights_basis']='PUBLIC_DISPLAY_PERMISSION_VERIFIED'",
            "d['promotional_description_discrepancy'][0]['private_source_path']='/private/book.epub'",
            "d['edition_observations'][0]['edition_metadata_provider']='Publisher rights cleared'",
            "d['unresolved_gates'][0]='RIGHTS_CLEARED'",
        ]
        prefix = (
            "import importlib.util,json,pathlib; "
            f"p=pathlib.Path({str(BATCH / 'validate.py')!r}); "
            "s=importlib.util.spec_from_file_location('kirk_gap',p); "
            "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
            "d=json.loads((p.parent/'records.json').read_text()); "
        )
        for mutant in mutants:
            with self.subTest(mutant=mutant):
                result = subprocess.run(
                    [sys.executable, "-O", "-c", prefix + mutant + "; m.validate_records(d)"],
                    cwd=ROOT, capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(result.returncode, 0, mutant)
                self.assertIn("ValueError:", result.stderr, mutant)


if __name__ == "__main__":
    unittest.main()
