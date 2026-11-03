"""Adversarial authenticity/rights/source-custody tests for Ortiz print leads."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate import P, qualify, unique_pairs


class OrtizArtPrintCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(P.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)

    def reject(self, mutation):
        forged = copy.deepcopy(self.packet)
        mutation(forged)
        with self.assertRaises(ValueError):
            qualify(forged)

    def test_unmodified_packet(self):
        self.assertTrue(qualify(self.packet))

    def test_independent_reviewer_exact_combined_falsifier(self):
        def forge(p):
            p["source_class"] = "LICENSED_PUBLIC_IMAGE_SET"
            p["limitations"] = []
            p["records"][0]["source_published"] = "2099-01-01"
            p["records"][0]["evidence"] = "Publisher grants unconditional reuse of artwork in every country for any purpose"
        self.reject(forge)

    def test_source_class_forgery_alone(self):
        self.reject(lambda p: p.update(source_class="LICENSED_PUBLIC_IMAGE_SET"))

    def test_limitation_removal_alone(self):
        self.reject(lambda p: p.update(limitations=[]))

    def test_limitations_malicious_append(self):
        self.reject(lambda p: p["limitations"].append("Art licensed for all display"))

    def test_source_date_forgery(self):
        self.reject(lambda p: p["records"][0].update(source_published="2099-01-01"))

    def test_license_evidence_forgery(self):
        self.reject(lambda p: p["records"][0].update(evidence="Publisher grants unlimited public image display rights for this artwork."))

    def test_unsupported_assertion_forgery(self):
        self.reject(lambda p: p["records"][1].update(assertion="The episode footage proves global identity, display license, and screen accuracy."))

    def test_summary_semantic_promotion(self):
        self.reject(lambda p: p["records"][1].update(original_short_synopsis="A verified full audiovisual close-read proves the depicted events are objectively true."))

    def test_publisher_title_or_url_swap(self):
        self.reject(lambda p: p["records"][0].update(source_url=p["records"][1]["source_url"]))

    def test_records_reordered(self):
        self.reject(lambda p: p["records"].reverse())

    def test_extra_authenticity_field(self):
        self.reject(lambda p: p["records"][0].update(verified_public_license=True))

    def test_false_image_release(self):
        self.reject(lambda p: p["records"][0].update(artwork_rights="DISPLAY_APPROVED"))

    def test_false_work_admission(self):
        self.reject(lambda p: p["records"][0].update(work_identity="CANONICAL_WORK"))

    def test_false_coverage(self):
        self.reject(lambda p: p.update(coverage_effect="CLOSE_READ"))

    def test_duplicate_raw_key_normal_and_optimized(self):
        raw = P.read_text(encoding="utf-8")
        for existing, forged in (
            ('"source_class": "FIRST_PARTY_EDITORIAL_ARTWORK_PRODUCT_ANNOUNCEMENT"',
             '"source_class": "LICENSED_PUBLIC_IMAGE_SET", "source_class": "FIRST_PARTY_EDITORIAL_ARTWORK_PRODUCT_ANNOUNCEMENT"'),
            ('"artwork_rights": "HELD_NO_PUBLIC_DISPLAY_LICENSE"',
             '"artwork_rights": "DISPLAY_APPROVED", "artwork_rights": "HELD_NO_PUBLIC_DISPLAY_LICENSE"'),
        ):
            self.assertIn(existing, raw)
            with tempfile.TemporaryDirectory() as d:
                f = Path(d) / "attack.json"
                f.write_text(raw.replace(existing, forged, 1), encoding="utf-8")
                for optimized in (False, True):
                    code = "import json,sys;from validate import qualify,unique_pairs;qualify(json.loads(open(sys.argv[1]).read(),object_pairs_hook=unique_pairs))"
                    run = subprocess.run([sys.executable, *(["-O"] if optimized else []), "-c", code, str(f)],
                                         cwd=P.parent, capture_output=True, text=True, check=False)
                    self.assertNotEqual(run.returncode, 0)
                    self.assertIn("duplicate JSON key", run.stderr)


if __name__ == "__main__":
    unittest.main()
