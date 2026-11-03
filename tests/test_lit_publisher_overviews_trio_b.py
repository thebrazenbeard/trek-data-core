"""Hostile tests of 3 publisher synopsis candidates and four *distinct* editions."""

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "proposals/research/lit-publisher-overviews-trio-b-20261103/validate.py"
SPEC = importlib.util.spec_from_file_location("lit_publisher_overviews_trio_b", P)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class PublisherOverviewTrioBTests(unittest.TestCase):
    def reject(self, mutate, *, check_prior=False):
        clone = copy.deepcopy(module.EXPECTED)
        mutate(clone)
        with self.assertRaises(ValueError):
            module.validate(clone, check_prior=check_prior)

    def test_unmodified_batch_and_prior_inventory(self):
        self.assertTrue(module.validate(module.EXPECTED))
        titles, isbns = module.accepted_other_titles_and_isbns()
        for row in module.EXPECTED["candidates"]:
            self.assertNotIn(row["publisher_display_title"], titles)
            self.assertNotIn(row["edition"]["isbn13"], isbns)

    def test_2018_and_2026_editions_remain_separate(self):
        pair = module.EXPECTED["candidates"][2]
        self.assertEqual(pair["edition"]["isbn13"], "9781668282182")
        self.assertEqual(pair["other_publisher_edition"]["isbn13"], "9781501138768")
        self.assertEqual(pair["other_publisher_edition"]["text_equivalence"], "UNVERIFIED")

    def test_no_source_work_coverage_or_artwork_promotion(self):
        d = module.EXPECTED
        self.assertFalse(d["full_book_text_inspected"])
        self.assertFalse(d["source_bound"])
        self.assertFalse(d["close_read"])
        self.assertFalse(d["artwork_rights_verified"])
        self.assertEqual(d["public_site_effect"], "NONE")

    def test_reject_private_host_path_root(self):
        self.reject(lambda d: d.update(private_host_path="C:/Users/patri/OneDrive/Documents/Books"))

    def test_reject_private_host_path_candidate(self):
        self.reject(lambda d: d["candidates"][0].update(private_source_path="D:/Books/epub"))

    def test_reject_embedded_book_bytes(self):
        self.reject(lambda d: d["candidates"][0].update(full_book_text="copyrighted book " * 1000))

    def test_reject_image_url_and_false_cover_rights(self):
        self.reject(lambda d: d["candidates"][2].update(image_url="https://publisher.example/test.jpg"))
        self.reject(lambda d: d["candidates"][0].update(rights_to_republish_cover="GRANTED"))

    def test_reject_nested_edition_claims(self):
        self.reject(lambda d: d["candidates"][2]["edition"].update(artwork_license="FREE"))
        self.reject(lambda d: d["candidates"][2]["other_publisher_edition"].update(source_path="C:/private.epub"))

    def test_reject_cover_rights_escalation(self):
        self.reject(lambda d: d.update(artwork_rights_verified=True))
        self.reject(lambda d: d["candidates"][0].update(cover_public_use_state="RELEASED"))

    def test_reject_coverage_and_custody_escalation(self):
        self.reject(lambda d: d.update(accepted_coverage_effect="ADMITTED"))
        self.reject(lambda d: d.update(full_book_text_inspected=True))
        self.reject(lambda d: d.update(source_bound=True))
        self.reject(lambda d: d.update(close_read=True))
        self.reject(lambda d: d.update(public_site_effect="PUBLISHED"))

    def test_reject_invented_independent_corroborators(self):
        self.reject(lambda d: d.update(distinct_upstream_sources=4))

    def test_reject_wrong_edition_and_bad_checksum(self):
        self.reject(lambda d: d["candidates"][2]["edition"].update(isbn13="9781501138768"))
        self.reject(lambda d: d["candidates"][1]["edition"].update(isbn13="9780000000000"))
        self.assertFalse(module.isbn13_valid("9780000000000"))

    def test_reject_2018_sibling_overclaim(self):
        self.reject(lambda d: d["candidates"][2]["other_publisher_edition"].update(text_equivalence="IDENTICAL"))
        self.reject(lambda d: d["candidates"][2]["other_publisher_edition"].update(format="TRADE_PAPERBACK"))

    def test_reject_title_and_series_swaps(self):
        self.reject(lambda d: d["candidates"][0].update(publisher_display_title="The Higher Frontier"))
        self.reject(lambda d: d["candidates"][1].update(series="Star Trek: Voyager"))

    def test_reject_source_unanchored_paraphrase(self):
        self.reject(lambda d: d["candidates"][0].update(publisher_description_paraphrase="This is a completely made up summary about an imaginary artifact with nobody or any anchored information from the source that was read in this publisher candidate."))

    def test_optimized_python_still_enforces_admission_protection(self):
        code = ("import importlib.util,copy; s=importlib.util.spec_from_file_location('v'," + repr(str(P)) + "); "
                "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                "d=copy.deepcopy(m.EXPECTED); d['accepted_coverage_effect']='ADMITTED'; "
                "m.validate(d,check_prior=False)")
        result = subprocess.run([sys.executable, "-O", "-c", code], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError", result.stderr)


if __name__ == "__main__":
    unittest.main()
