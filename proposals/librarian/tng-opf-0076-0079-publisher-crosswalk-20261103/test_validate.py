"""Adversarial checks for held TNG OPF0076–0079 publisher crosswalk."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tng_opf_7679_validator", HERE / "validate.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class CrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = v.parse_json_strict(v.PACKET.read_text(encoding="utf-8"))
        cls.opf = v.OPF.read_bytes()
        cls.catalog = v.CATALOG.read_bytes()

    def reject(self, change, message):
        d = copy.deepcopy(self.good)
        change(d)
        with self.assertRaisesRegex(ValueError, message):
            v.validate(d, self.opf, self.catalog)

    def test_original_four(self):
        self.assertEqual(v.validate(self.good, self.opf, self.catalog), 4)

    def test_all_four_checked_conversion(self):
        conversions = {
            "0743421116": "9780743421119",
            "0743421124": "9780743421126",
            "0743421132": "9780743421133",
            "0743421140": "9780743421140",
        }
        for ten, thirteen in conversions.items():
            self.assertEqual(v.isbn10_to_13(ten), thirteen)
        with self.assertRaisesRegex(ValueError, "checksum"):
            v.isbn10_to_13("0743421110")

    def test_swap_same_publisher_pages_without_local_ids_fails(self):
        def swap(d):
            a, b = d["records"][:2]
            for field in ("publisher_product_url", "publisher_isbn13", "publisher_title"):
                a[field], b[field] = b[field], a[field]
        self.reject(swap, "unreviewed source/edition tuple")

    def test_wrong_opf_binding_fails(self):
        self.reject(lambda d: d["records"][0].update(opf_id="opf-local:0079"), "unreviewed source/edition tuple")
        self.reject(lambda d: d["records"][1].update(opf_isbn10="0743421132"), "unreviewed source/edition tuple")

    def test_publisher_ordinals_extents_and_titles_fixed(self):
        self.reject(lambda d: d["records"][0].update(publisher_series_ordinal=29), "unreviewed source/edition tuple")
        self.reject(lambda d: d["records"][2].update(publisher_page_count=288), "unreviewed source/edition tuple")
        self.reject(lambda d: d["records"][1].update(publisher_title="Sins of Commission"), "unreviewed source/edition tuple")

    def test_dates_not_reconciled_by_fiat(self):
        self.reject(lambda d: d["records"][1].update(opf_date_raw="2000-09-22"), "unreviewed source/edition tuple")
        self.reject(lambda d: d["records"][3].update(opf_date_raw="2000-07-29"), "unreviewed source/edition tuple")
        self.reject(lambda d: d["records"][3].update(date_relation="SAME_RELEASE_DATE"), "unreviewed source/edition tuple")

    def test_rights_and_custody_never_promoted(self):
        self.reject(lambda d: d.update(accepted_source_work_effect="ACCEPTED"), "forbidden promotion")
        self.reject(lambda d: d.update(literary_coverage_effect="FULL_TEXT_AVAILABLE"), "forbidden promotion")
        self.reject(lambda d: d.update(public_text_image_effect="DISPLAY"), "forbidden promotion")
        self.reject(lambda d: d["records"][0].update(private_edition_verified=True), "unreviewed source/edition tuple")
        self.reject(lambda d: d["records"][1].update(rights_status="PUBLIC_REUSE_GRANTED"), "unreviewed source/edition tuple")

    def test_closed_schema_blocks_hidden_reuse_fields(self):
        self.reject(lambda d: d.update(public_ebook_license="CLEARED"), "unknown or missing keys")
        self.reject(lambda d: d["records"][0].update(ebook_text="excerpt"), "unknown or missing keys")

    def test_source_family_and_snapshot_claims_fixed(self):
        self.reject(lambda d: d.update(source_family="publisher:independent.com"), "unreviewed publisher acquisition")
        self.reject(lambda d: d.update(source_snapshots_available=True), "unreviewed publisher acquisition")

    def test_sha_and_directory_denominator_pins(self):
        self.reject(lambda d: d["opf_input"].update(path="somewhere/else.json"), "OPF path/hash/scope substitution")
        self.reject(lambda d: d["directory_baseline"].update(literature_rows=10), "directory denominator")

    def test_private_opf_byte_mutation_rejected(self):
        source = json.loads(self.opf)
        opf_row = next(r for r in source["rows"] if r["source_local_id"] == "opf-local:0079")
        opf_row["date"] = ["2000-09-22"]
        with self.assertRaisesRegex(ValueError, "OPF source bytes changed"):
            v.validate(self.good, json.dumps(source).encode(), self.catalog)

    def test_duplicate_json_key_conflicting_rights_rejected(self):
        raw = v.PACKET.read_text(encoding="utf-8")
        needle = '"rights_status": "METADATA_ONLY_NO_PUBLIC_TEXT_IMAGE_RIGHTS"'
        forged = raw.replace(needle, '"rights_status": "CLEARED", ' + needle, 1)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key: rights_status"):
            v.parse_json_strict(forged)

    def test_python_optimized_rejects_injected_editions(self):
        script = '''
import copy, sys
sys.path.insert(0, sys.argv[1])
from validate import PACKET, OPF, CATALOG, parse_json_strict, validate
raw = PACKET.read_text(encoding="utf-8")
needle = '"rights_status": "METADATA_ONLY_NO_PUBLIC_TEXT_IMAGE_RIGHTS"'
try:
    parse_json_strict(raw.replace(needle, '"rights_status": "CLEARED", '+needle, 1))
except ValueError:
    pass
else:
    raise SystemExit("optimized parser accepted duplicate rights")
base = parse_json_strict(raw)
opf, cat = OPF.read_bytes(), CATALOG.read_bytes()
for section, index, field, value in (
    ("records", 0, "publisher_product_url", base["records"][1]["publisher_product_url"]),
    ("records", 0, "private_edition_verified", True),
    ("records", 3, "opf_date_raw", "2000-07-29"),
    ("records", 1, "publisher_isbn13", "9780743421133"),
    ("records", 0, "rights_status", "PUBLIC_REUSE_GRANTED"),
    ("root", 0, "literary_coverage_effect", "CLOSE_READ"),
    ("root", 0, "public_text_image_license", True),
):
    d = copy.deepcopy(base)
    target = d if section == "root" else d[section][index]
    target[field] = value
    try:
        validate(d, opf, cat)
    except ValueError:
        continue
    raise SystemExit("optimized validator accepted " + field)
'''
        proc = subprocess.run([sys.executable, "-O", "-c", script, str(HERE)],
                              text=True, capture_output=True, timeout=25, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)


if __name__ == "__main__":
    unittest.main()
