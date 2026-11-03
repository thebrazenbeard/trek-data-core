"""Adversarial tests for first-party publisher-only LIT wave, under Python -O too."""

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "proposals/research/lit-lost-era-destiny-publisher-20261103/validate.py"
SPEC = importlib.util.spec_from_file_location("lit_lost_era_destiny_publisher", CHECK)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class LostEraDestinyPublisherTests(unittest.TestCase):
    def reject(self, mutate):
        d = copy.deepcopy(M.EXPECTED)
        mutate(d)
        with self.assertRaises(ValueError):
            M.validate(d, check_prior=False)

    def test_original_and_no_existing_overlap(self):
        self.assertTrue(M.validate(M.EXPECTED))
        titles, isbns = M.prior_titles_and_isbns()
        self.assertFalse({r["publisher_display_title"] for r in M.EXPECTED["candidates"]} & titles)
        self.assertNotIn("9781668290712", isbns)

    def test_future_2027_trade_not_in_2026_book_custody(self):
        r = M.EXPECTED["candidates"][0]
        self.assertEqual(r["edition"]["publisher_date"], "2027-02-13")
        self.assertEqual(r["edition"]["publication_state_as_of_observation"], "FUTURE_PUBLISHER_LISTING_NOT_BOOK_CUSTODY")
        self.assertEqual(r["related_edition"]["content_equivalence"], "UNVERIFIED")
        self.assertFalse(M.EXPECTED["private_book_text_read"])

    def test_reject_unauthorized_global_source_status(self):
        self.reject(lambda d: d.update(accepted_source_work_effect="ADMITTED"))
        self.reject(lambda d: d.update(accepted_coverage_effect="CLOSE_READ"))
        self.reject(lambda d: d.update(accepted_evidence_effect="PROVEN"))
        self.reject(lambda d: d.update(public_site_effect="PUBLISHED"))
        self.reject(lambda d: d.update(private_book_source_bound=True))
        self.reject(lambda d: d.update(private_book_text_read=True))

    def test_reject_raw_page_sha_claim(self):
        self.reject(lambda d: d.update(source_content_byte_sha256="f" * 64))

    def test_reject_private_path_injection(self):
        self.reject(lambda d: d.update(private_zip_path="C:/Users/patri/OneDrive/Documents/Books"))
        self.reject(lambda d: d["candidates"][0].update(private_source_path="D:/ST Books/novel.epub"))
        self.reject(lambda d: d["candidates"][2]["edition"].update(private_source_path="/mnt/d/Books/a"))

    def test_reject_copyrighted_text_injection(self):
        self.reject(lambda d: d["candidates"][1].update(full_book_text="prose " * 2000))

    def test_reject_unauthorized_cover_claims(self):
        self.reject(lambda d: d.update(cover_art_rights_verified=True))
        self.reject(lambda d: d.update(cover_art_bytes_stored=True))
        self.reject(lambda d: d["candidates"][2].update(cover_image_url="https://example.test/image.jpg"))
        self.reject(lambda d: d["candidates"][0].update(artwork_observation="LICENSED_FOR_PUBLIC_DISPLAY"))

    def test_reject_false_four_independent_publishers(self):
        self.reject(lambda d: d.update(independent_upstream_source_family_count=4))

    def test_reject_future_paperback_immediate_release(self):
        self.reject(lambda d: d["candidates"][0]["edition"].update(publication_state_as_of_observation="RELEASED_AND_FULL_TEXT_AVAILABLE"))
        self.reject(lambda d: d["candidates"][0]["edition"].update(publisher_date="2026-02-13"))

    def test_reject_edition_swap_and_bad_isbn(self):
        self.reject(lambda d: d["candidates"][0]["edition"].update(isbn13="9781416537397"))
        self.reject(lambda d: d["candidates"][1]["edition"].update(isbn13="9780000000000"))
        self.assertFalse(M.valid_isbn13("9780000000000"))

    def test_reject_unproved_content_equivalence(self):
        self.reject(lambda d: d["candidates"][0]["related_edition"].update(content_equivalence="IDENTICAL"))
        self.reject(lambda d: d["candidates"][0]["related_edition"].update(format="TRADE_PAPERBACK"))

    def test_reject_publisher_title_normalization(self):
        self.reject(lambda d: d["candidates"][2].update(publisher_display_title="The Art of the Impossible"))
        self.reject(lambda d: d["candidates"][0].update(publisher_display_title="The Buried Age"))

    def test_reject_synopsis_source_promotion_and_swap(self):
        self.reject(lambda d: d["candidates"][1].update(synopsis_basis="FULL_TEXT_CLOSE_READ"))
        self.reject(lambda d: d["candidates"][1].update(original_paraphrase=d["candidates"][2]["original_paraphrase"]))

    def test_reject_oversized_promotional_text(self):
        self.reject(lambda d: d["candidates"][0].update(original_paraphrase="The publisher says " * 500))

    def test_reject_source_url_misrouting(self):
        self.reject(lambda d: d["candidates"][2]["edition"].update(publisher_url="https://unofficial.example/9780743464062"))

    def test_optimized_mode_rejects_admission_mutant(self):
        code = ("import importlib.util,copy; s=importlib.util.spec_from_file_location('v'," + repr(str(CHECK)) + "); "
                "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                "d=copy.deepcopy(m.EXPECTED); d['accepted_coverage_effect']='ADMITTED'; "
                "m.validate(d,check_prior=False)")
        p = subprocess.run([sys.executable, "-O", "-c", code], text=True, capture_output=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ValueError", p.stderr)


if __name__ == "__main__":
    unittest.main()
