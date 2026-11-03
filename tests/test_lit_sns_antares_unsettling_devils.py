"""Hostile gates for three publisher-only literature observations."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "proposals/research/lit-sns-antares-unsettling-devils-20261103/validate.py"
SPEC = importlib.util.spec_from_file_location("lit_sns_three_more", VALIDATOR)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class LiteratureSourceLocalPublisherTests(unittest.TestCase):
    def reject(self, mutation):
        candidate = copy.deepcopy(module.EXPECTED)
        mutation(candidate)
        with self.assertRaises(ValueError):
            module.validate(candidate, check_prior=False)

    def test_exact_observations_match_accepted_noncollision_frontier(self):
        self.assertTrue(module.validate(module.EXPECTED))
        known_titles, known_isbns = module.accepted_other_titles_and_isbns()
        self.assertFalse(known_titles.intersection(r["publisher_title"].casefold() for r in module.EXPECTED["candidates"]))
        self.assertFalse(known_isbns.intersection(r["edition"]["isbn13"] for r in module.EXPECTED["candidates"]))

    def test_no_close_read_source_binding_or_public_coverage_claims(self):
        d = module.EXPECTED
        for field in ("raw_page_bytes_custodied", "full_book_text_read", "full_text_available", "close_read", "cover_use_rights_verified"):
            self.assertFalse(d[field])
        for field in ("source_work_binding_effect", "identity_reconciliation_effect", "accepted_coverage_effect", "public_explorer_effect"):
            self.assertEqual(d[field], "NONE")

    def test_one_publisher_is_one_lineage(self):
        self.assertEqual(module.EXPECTED["distinct_upstream_sources"], 1)
        self.reject(lambda d: d.update(distinct_upstream_sources=3))

    def test_reject_book_or_page_custody_escalation(self):
        self.reject(lambda d: d.update(full_book_text_read=True))
        self.reject(lambda d: d.update(full_text_available=True))
        self.reject(lambda d: d.update(raw_page_bytes_custodied=True))
        self.reject(lambda d: d.update(close_read=True))

    def test_reject_coverage_identity_and_publication_escalation(self):
        self.reject(lambda d: d.update(accepted_coverage_effect="CLOSE_READ"))
        self.reject(lambda d: d.update(source_work_binding_effect="ADMITTED"))
        self.reject(lambda d: d.update(public_explorer_effect="PUBLISHED"))
        self.reject(lambda d: d["candidates"][1].update(text_equivalence_and_global_identity="SAME_AS"))

    def test_reject_wrong_edition_and_bad_isbn(self):
        self.reject(lambda d: d["candidates"][1]["edition"].update(isbn13="9780000000000"))
        self.reject(lambda d: d["candidates"][2]["edition"].update(format="EBOOK"))
        self.reject(lambda d: d["candidates"][0]["edition"].update(release_date="2013-02-26"))
        self.assertFalse(module.isbn13_valid("9780000000000"))

    def test_reject_source_linkage_and_invented_publisher(self):
        self.reject(lambda d: d["candidates"][2]["edition"].update(source_url="https://memory-alpha.fandom.com/wiki/Devils_Bargain"))
        self.reject(lambda d: d["candidates"][0].update(publisher_title="Invented Canon"))
        self.reject(lambda d: d["candidates"][0]["evidence"][1].update(supports="OBJECTIVE_FICTIONAL_FACT"))
        self.reject(lambda d: d["candidates"][1]["assertions"][0].update(status="CANON_CONFIRMED"))
        self.reject(lambda d: d["candidates"][1]["assertions"][0].update(evidence_id="unknown-source"))

    def test_reject_unreviewed_private_bytes_and_image_rights(self):
        self.reject(lambda d: d["candidates"][0].update(private_host_path="D:/VERA/Books"))
        self.reject(lambda d: d["candidates"][1].update(full_novel_text="copyrighted novel" * 300))
        self.reject(lambda d: d["candidates"][0].update(cover_publication_state="RELEASED"))
        self.reject(lambda d: d["candidates"][0]["edition"].update(artwork_license="CC0"))

    def test_reject_unanchored_synopsis_and_swapped_continuity(self):
        self.reject(lambda d: d["candidates"][1].update(original_publisher_description_paraphrase="No references to the observed setting or the publisher's described people exist in this ungrounded text, although it remains approximately one full sentence long."))
        self.reject(lambda d: d["candidates"][1].update(description_anchor_terms=["Prime", "Spock", "Universe"]))

    def test_optimized_mode_cannot_skip_guards(self):
        code = (
            "import copy,importlib.util; s=importlib.util.spec_from_file_location('v'," + repr(str(VALIDATOR)) + ");"
            "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
            "d=copy.deepcopy(m.EXPECTED);d['public_explorer_effect']='PUBLISHED';m.validate(d,check_prior=False)"
        )
        result = subprocess.run([sys.executable, "-O", "-c", code], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError", result.stderr)


if __name__ == "__main__":
    unittest.main()
