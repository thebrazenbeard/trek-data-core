"""Adversarial Q Continuum publisher/OPF edition and omnibus uncertainty tests."""

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "proposals/research/lit-q-continuum-publisher-20261103/validate.py"
SPEC = importlib.util.spec_from_file_location("lit_q_continuum_publisher", P)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class QContinuumPublisherTests(unittest.TestCase):
    def reject(self, mutate):
        d = copy.deepcopy(M.EXPECTED)
        mutate(d)
        with self.assertRaises(ValueError):
            M.validate(d, check_prior=False)

    def test_source_packet_and_three_opf_holds(self):
        self.assertTrue(M.validate(M.EXPECTED))
        opf = M.accepted_opf_leads()
        self.assertEqual([x["source_local_id"] for x in opf], list(M.OPF_IDS))
        self.assertEqual(opf[2]["creator"], ["William C. Deets &Dean Williams"])

    def test_unnumbered_not_assumed_omnibus(self):
        d = M.EXPECTED
        self.assertEqual(d["adjacent_unnumbered_publisher_product"]["publisher_pages"], 368)
        self.assertTrue(all(x["publisher_pages"] == 288 for x in d["numbered_books"]))
        self.assertFalse(d["adjacent_unnumbered_publisher_product"]["publisher_page_contains_explicit_complete_trilogy_claim"])
        self.assertFalse(d["full_text_read"])

    def test_reject_injected_private_data_all_levels(self):
        self.reject(lambda d: d.update(private_archive_path="C:/Users/patri/OneDrive/Documents/Books"))
        self.reject(lambda d: d["numbered_books"][0].update(private_member="D:/Books/Q-Space.epub"))
        self.reject(lambda d: d["adjacent_unnumbered_publisher_product"].update(raw_cover_url="https://image.example/cover.jpg"))
        self.reject(lambda d: d["accepted_opf_candidate_lead_context"][1].update(private_ebook_path="/mnt/d/Books/Q-Zone"))

    def test_reject_copyrighted_text_injected(self):
        self.reject(lambda d: d["numbered_books"][2].update(full_book_text="some text " * 2000))

    def test_reject_source_and_coverage_claims(self):
        self.reject(lambda d: d.update(private_book_custody_verified=True))
        self.reject(lambda d: d.update(full_text_read=True))
        self.reject(lambda d: d.update(accepted_work_effect="THREE"))
        self.reject(lambda d: d.update(accepted_coverage_effect="CLOSE_READ"))
        self.reject(lambda d: d.update(public_site_effect="RELEASED"))

    def test_reject_page_html_custody_overclaim(self):
        self.reject(lambda d: d.update(raw_html_sha256="0" * 64))

    def test_reject_cover_rights_escalation(self):
        self.reject(lambda d: d.update(cover_art_public_rights_verified=True))
        self.reject(lambda d: d.update(cover_art_bytes_committed=True))

    def test_reject_omnibus_from_publisher_label(self):
        self.reject(lambda d: d["adjacent_unnumbered_publisher_product"].update(relationship_to_numbered_books="COMPLETE_TRILOGY_OMNIBUS"))
        self.reject(lambda d: d["adjacent_unnumbered_publisher_product"].update(publisher_page_contains_explicit_complete_trilogy_claim=True))

    def test_reject_unnumbered_page_count_as_three_book_sum(self):
        self.reject(lambda d: d["adjacent_unnumbered_publisher_product"].update(publisher_pages=864))

    def test_reject_sequence_swaps_and_bad_isbn(self):
        self.reject(lambda d: d["numbered_books"][0].update(publisher_sequence_number=3))
        self.reject(lambda d: d["numbered_books"][2].update(isbn13="9780000000000"))
        self.assertFalse(M.isbn13_valid("9780000000000"))

    def test_reject_publisher_isbn_url_swap(self):
        self.reject(lambda d: d["numbered_books"][1].update(publisher_url=d["numbered_books"][0]["publisher_url"]))

    def test_reject_opf_isbn_fabrication(self):
        self.reject(lambda d: d["accepted_opf_candidate_lead_context"][0].update(opf_isbn_present=True))
        self.reject(lambda d: d["accepted_opf_candidate_lead_context"][1].update(identity_link_state="CONFIRMED_SAME_WORK"))

    def test_reject_opf_creator_mismatch_erasure(self):
        self.reject(lambda d: d["accepted_opf_candidate_lead_context"][2].pop("opf_creator_mismatch"))
        self.reject(lambda d: d["accepted_opf_candidate_lead_context"][2].update(opf_creator_mismatch="GREG_COX_MATCH"))

    def test_reject_unsupported_synopsis_source(self):
        self.reject(lambda d: d["numbered_books"][0].update(synopsis_basis="CLOSE_READ_FULL_BOOK"))
        self.reject(lambda d: d["numbered_books"][1].update(original_publisher_description_paraphrase="invented marketing scene " * 200))

    def test_optimized_interpreter_still_rejects_omnibus_claim(self):
        code = ("import importlib.util,copy; s=importlib.util.spec_from_file_location('v'," + repr(str(P)) + "); "
                "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                "d=copy.deepcopy(m.EXPECTED); d['adjacent_unnumbered_publisher_product']['relationship_to_numbered_books']='VERIFIED_OMNIBUS'; "
                "m.validate(d,check_prior=False)")
        p = subprocess.run([sys.executable, "-O", "-c", code], text=True, capture_output=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ValueError", p.stderr)


if __name__ == "__main__":
    unittest.main()
