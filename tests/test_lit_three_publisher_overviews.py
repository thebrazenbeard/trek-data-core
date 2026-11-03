"""Hostile metadata and admission checks for three publisher-overview observations."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "proposals/research/lit-three-publisher-overviews-20261103"
SPEC = importlib.util.spec_from_file_location("lit_three_overviews", BATCH / "validate.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("source-local validator is unavailable")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ThreePublisherOverviewsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((BATCH / "observations.json").read_text(encoding="utf-8"))

    def assert_rejected(self, mutate):
        data = copy.deepcopy(self.original)
        mutate(data)
        with self.assertRaises((ValueError, KeyError)):
            MODULE.validate(data)

    def test_exact_source_local_proposal_and_accepted_snapshot(self):
        MODULE.validate(self.original)
        titles, isbn = MODULE.accepted_title_and_isbn_snapshot()
        self.assertEqual(len(self.original["candidates"]), 3)
        for row in self.original["candidates"]:
            self.assertNotIn(row["publisher_title"].casefold(), titles)
            self.assertNotIn(row["edition_isbn13"], isbn)

    def test_new_work_candidate_identity_and_edition_uniqueness(self):
        rows = self.original["candidates"]
        self.assertEqual(len({r["candidate_id"] for r in rows}), 3)
        self.assertEqual(len({r["edition_isbn13"] for r in rows}), 3)
        for row in rows:
            self.assertTrue(MODULE.isbn13(row["edition_isbn13"]))
            self.assertTrue(row["publisher_edition_url"].endswith("/" + row["edition_isbn13"]))

    def test_reject_extra_private_or_copyright_fields_at_all_levels(self):
        self.assert_rejected(lambda d: d.update(private_book_path="/private/source.epub"))
        self.assert_rejected(lambda d: d["candidates"][0].update(
            full_book_text="A full copyrighted novel" * 500))
        self.assert_rejected(lambda d: d["candidates"][1].update(
            rights_to_republish_cover="GRANTED"))
        self.assert_rejected(lambda d: d["candidates"][2]["alternate_edition_observation"].update(
            private_source_path=r"C:\Users\Example\Books\book.lit"))

    def test_reject_source_and_research_admission_promotions(self):
        for field in ("source_bound", "full_text_available", "close_read", "semantically_analyzed",
                      "image_or_ebook_bytes_retrieved", "publisher_edition_family_complete"):
            with self.subTest(field=field):
                self.assert_rejected(lambda d, f=field: d.update({f: True}))
        for field in ("accepted_work_effect", "accepted_evidence_effect", "accepted_coverage_effect",
                      "public_synopsis_publication_effect", "public_artwork_release_effect"):
            with self.subTest(field=field):
                self.assert_rejected(lambda d, f=field: d.update({f: "ADMITTED"}))

    def test_reject_synopsis_claimed_as_direct_book_events(self):
        self.assert_rejected(lambda d: d["candidates"][0].update(
            overview_scope="VERIFIED_BOOK_PLOT"))
        self.assert_rejected(lambda d: d["candidates"][1].update(
            overview_basis="FULL_TEXT_CLOSE_READ"))

    def test_reject_unverified_named_returning_character(self):
        self.assert_rejected(lambda d: d["candidates"][2].update(
            original_overview="The publisher says Admiral Janeway returns and solves the threat."))

    def test_2012_and_2026_eternal_tide_editions_remain_distinct(self):
        self.assert_rejected(lambda d: d["candidates"][2]["alternate_edition_observation"].update(
            isbn13="9781668288559"))
        self.assert_rejected(lambda d: d["candidates"][2]["alternate_edition_observation"].update(
            text_equivalence="CONFIRMED_SAME_TEXT"))
        self.assert_rejected(lambda d: d["candidates"][2].update(
            publisher_publication_date="2012-08-28"))

    def test_wrong_isbn_checksum_rejected(self):
        self.assertFalse(MODULE.isbn13("9780000000000"))
        self.assert_rejected(lambda d: d["candidates"][0].update(edition_isbn13="9780000000000"))

    def test_optimized_mode_rejects_mutants_and_accepts_exact_proposal(self):
        validate_script = str(BATCH / "validate.py")
        success = subprocess.run([sys.executable, "-O", validate_script], cwd=ROOT,
                                 capture_output=True, text=True, check=False)
        self.assertEqual(success.returncode, 0, success.stdout + success.stderr)
        self.assertIn("LIT_THREE_OVERVIEWS_OK", success.stdout)
        prefix = (
            "import json,importlib.util,pathlib; "
            f"p=pathlib.Path({validate_script!r}); "
            "s=importlib.util.spec_from_file_location('overviews',p); "
            "m=importlib.util.module_from_spec(s);s.loader.exec_module(m); "
            "d=json.loads((p.parent/'observations.json').read_text()); "
        )
        mutants = (
            "d['private_host_path']='C:/Users/Example/Books/private.epub'",
            "d['candidates'][0]['rights_to_republish_cover']='GRANTED'",
            "d['candidates'][1]['close_read']=True",
            "d['candidates'][2]['alternate_edition_observation']['text_equivalence']='VERIFIED'",
        )
        for mutant in mutants:
            with self.subTest(mutant=mutant):
                result = subprocess.run([sys.executable, "-O", "-c", prefix + mutant + "; m.validate(d)"],
                                        cwd=ROOT, capture_output=True, text=True, check=False)
                self.assertNotEqual(result.returncode, 0, mutant)
                self.assertIn("ValueError:", result.stderr)


if __name__ == "__main__":
    unittest.main()
