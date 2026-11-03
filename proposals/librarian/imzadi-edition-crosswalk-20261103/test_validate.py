"""Adversarial source/edition crosswalk tests; preserve no-admission boundary."""

from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest


HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("imzadi_edition_validator", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class EditionCrosswalkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(validator.PACKET.read_text(encoding="utf-8"))
        cls.catalog = validator.CATALOG.read_bytes()
        cls.opf = validator.OPF_OBSERVATIONS.read_bytes()

    def reject(self, change, reason: str):
        packet = copy.deepcopy(self.good)
        change(packet)
        with self.assertRaisesRegex(ValueError, reason):
            validator.validate(packet, self.catalog, self.opf)

    def test_clean_page_read_metadata_only(self):
        self.assertEqual(validator.validate(self.good, self.catalog, self.opf), 4)

    def test_no_false_edition_bridge_from_private_opf(self):
        self.reject(lambda d: d["private_opf_title_lead"].update(exact_publisher_edition_binding="ISBN_9780743485104"), "private OPF")
        self.reject(lambda d: d["private_opf_title_lead"].update(isbn_present=True), "private OPF")
        self.reject(lambda d: d["private_opf_title_lead"].update(opf_isbn="9780743485104"), "closed schema")

    def test_no_unverified_container_claim(self):
        self.reject(lambda d: d["crosswalk_decisions"].update(imzadi_forever_to_triangle_imzadi_ii="CONTAINS_BOTH_WORKS"), "crosswalk")
        self.reject(lambda d: d["crosswalk_decisions"].update(two_title_families_are_one_canonical_work="ACCEPTED"), "crosswalk")

    def test_no_copyrighted_text_or_rights_release(self):
        self.reject(lambda d: d.update(prose_or_audio_custody_effect="FULL_TEXT_AVAILABLE"), "must remain NONE")
        self.reject(lambda d: d.update(image_download_or_display_effect="PUBLISHED"), "must remain NONE")
        self.reject(lambda d: d["records"][0].update(rights_status="PUBLIC_REUSE_CLEARED"), "rights or source custody")
        self.reject(lambda d: d["records"][0].update(full_book_text="copyrighted"), "closed schema")

    def test_no_accepted_work_or_coverage_claim(self):
        self.reject(lambda d: d.update(source_work_binding_effect="ACCEPTED"), "must remain NONE")
        self.reject(lambda d: d.update(literary_coverage_effect="CLOSE_READ"), "must remain NONE")
        self.reject(lambda d: d.update(corpus_admission_effect="SOURCE_BOUND"), "must remain NONE")

    def test_paperback_and_ebook_isbn_swap_fails(self):
        def swap(d):
            a, b = d["records"][:2]
            a["isbn13"], b["isbn13"] = b["isbn13"], a["isbn13"]
        self.reject(swap, "unreviewed publisher product")

    def test_audio_to_ebook_format_swap_fails(self):
        self.reject(lambda d: d["records"][3].update(edition_format="EBOOK"), "unreviewed publisher product")
        self.reject(lambda d: d["records"][3].update(reader=None), "unreviewed publisher product")
        self.reject(lambda d: d["records"][3].update(extent_unit="PAGES"), "unreviewed publisher product")

    def test_same_host_but_wrong_product_page_fails(self):
        self.reject(lambda d: d["records"][0].update(publisher_product_url=d["records"][1]["publisher_product_url"]), "unreviewed publisher product")

    def test_metadata_time_imprint_and_line_provenance_pinned(self):
        self.reject(lambda d: d["records"][2].update(publisher_product_date="1998-10-01"), "unreviewed publisher product")
        self.reject(lambda d: d["records"][3].update(publisher_imprint="Pocket Books/Star Trek"), "unreviewed publisher product")
        self.reject(lambda d: d["records"][0].update(product_details_line_anchor=400), "unreviewed publisher product")
        self.reject(lambda d: d["records"][0].update(publisher_creator="Someone Else"), "creator drift")

    def test_edition_set_and_baseline_are_closed(self):
        self.reject(lambda d: d["records"].pop(), "four exact editions")
        self.reject(lambda d: d.update(baseline_accepted_main="0" * 40), "baseline drift")
        self.reject(lambda d: d.update(observed_date_utc="2027-01-01"), "observation date")
        self.reject(lambda d: d.update(rights_to_republish_books=True), "closed schema")
        self.reject(lambda d: d["records"][0].update(exact_canonical_work_id="Imzadi"), "closed schema")

    def test_duplicate_json_key_cannot_hide_conflicting_rights_claim(self):
        original = validator.PACKET.read_text(encoding="utf-8")
        existing = '"rights_status": "METADATA_ONLY_NO_SOURCE_OR_IMAGE_REUSE_RIGHTS_ESTABLISHED"'
        malicious = original.replace(existing, '"rights_status": "PUBLIC_REUSE_APPROVED", ' + existing, 1)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key: rights_status"):
            validator.parse_json_no_duplicates(malicious)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            validator.parse_json_no_duplicates('{"records":[], "records":[1]}')

    def test_gap_catalog_forgery_rejected_with_updated_claimed_digest(self):
        packet = copy.deepcopy(self.good)
        catalog = json.loads(self.catalog)
        lit = next(r for r in catalog["rows"] if r.get("medium") == "LITERATURE")
        lit["title"] = "Imzadi Forever"
        forged = json.dumps(catalog, sort_keys=True).encode()
        import hashlib
        packet["catalog_gap_snapshot"]["sha256"] = hashlib.sha256(forged).hexdigest()
        with self.assertRaisesRegex(ValueError, "reviewed catalog path/digest"):
            validator.validate(packet, forged, self.opf)

    def test_private_opf_record_cannot_be_made_isbn_bound_by_fixture_edit(self):
        private = json.loads(self.opf)
        hit = next(r for r in private["rows"] if r.get("source_local_id") == "opf-local:0128")
        hit["isbn_checksum_valid"] = ["9780743485104"]
        with self.assertRaisesRegex(ValueError, "OPF bytes drift"):
            validator.validate(self.good, self.catalog, json.dumps(private).encode())

    def test_optimized_python_maintains_hard_gates(self):
        script = '''
import copy, json, pathlib, sys
sys.path.insert(0, sys.argv[1])
from validate import validate, parse_json_no_duplicates, PACKET, CATALOG, OPF_OBSERVATIONS
raw = PACKET.read_text(encoding="utf-8")
needle = '"rights_status": "METADATA_ONLY_NO_SOURCE_OR_IMAGE_REUSE_RIGHTS_ESTABLISHED"'
forged = raw.replace(needle, '"rights_status": "PUBLIC_REUSE_APPROVED", ' + needle, 1)
try:
    parse_json_no_duplicates(forged)
except ValueError:
    pass
else:
    raise SystemExit("optimized parser accepted duplicate hidden rights claim")
base = parse_json_no_duplicates(raw)
cat, opf = CATALOG.read_bytes(), OPF_OBSERVATIONS.read_bytes()
changes = (
    ("records", 0, "isbn13", "9780743492645"),
    ("records", 3, "edition_format", "EBOOK"),
    ("records", 0, "rights_status", "PUBLIC_REUSE_CLEARED"),
    ("records", 0, "full_text_verified", True),
    ("private_opf_title_lead", None, "exact_publisher_edition_binding", "ISBN_9780743485104"),
    ("crosswalk_decisions", None, "imzadi_forever_to_triangle_imzadi_ii", "CONTAINS_BOTH_WORKS"),
    ("root", None, "rights_to_republish_books", True),
)
for section, index, field, value in changes:
    p = copy.deepcopy(base)
    target = p if section == "root" else p[section] if index is None else p[section][index]
    target[field] = value
    try:
        validate(p, cat, opf)
    except ValueError:
        continue
    raise SystemExit("optimized validator accepted forged " + field)
'''
        run = subprocess.run([sys.executable, "-O", "-c", script, str(HERE)],
                             text=True, capture_output=True, timeout=20, check=False)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
