"""Adversarial tests for the Section 31 first-party source-local packet."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


HERE = Path(__file__).resolve().parents[1] / "proposals/films/section31-source-art-ledger-20261103"
spec = importlib.util.spec_from_file_location("section31_source_art", HERE / "validate.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Section31SourceArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = v.reviewed()
        cls.discovery = v.load(v.DISCOVERY)
        cls.prior = v.load(v.PRIOR)

    def reject(self, mutator):
        modified = copy.deepcopy(self.packet)
        mutator(modified)
        with self.assertRaises(ValueError):
            v.validate(modified, self.discovery, self.prior)

    def test_exact_source_count_and_prior_overlap(self):
        self.assertEqual(v.validate(self.packet, self.discovery, self.prior), 3)
        self.assertEqual(self.packet["candidate_film_id"], "film-section-31")

    def test_cannot_promote_indexed_runtime_into_source_read(self):
        self.reject(lambda p: p["sources"][2].update(runtime_minutes_verified_directly=95))
        self.reject(lambda p: p["sources"][2].update(source_observed_fields=["film_runtime_minutes:95"]))
        self.reject(lambda p: p["sources"][2].update(reader_receipt="LIVE_FIRST_PARTY_200"))

    def test_cannot_fabricate_artwork_rights_or_publisher_observation(self):
        self.reject(lambda p: p["sources"][0].update(poster_status="LICENSED_FOR_PUBLIC_REUSE"))
        self.reject(lambda p: p["sources"][0].update(poster_page_image_link="https://example.com/poster.png"))
        self.reject(lambda p: p["sources"][0].update(synopsis_status="EDITORIALLY_ADMITTED"))
        self.reject(lambda p: p["sources"][1].update(source_observed_fields=["watched_full_film"]))

    def test_cannot_promote_to_work_or_accepted_coverage(self):
        self.reject(lambda p: p.update(source_work_binding_effect="SOURCE_BOUND"))
        self.reject(lambda p: p.update(accepted_coverage_effect="CLOSE_READ"))
        self.reject(lambda p: p.update(public_synopsis_release_effect="PUBLISHED"))
        self.reject(lambda p: p.update(artwork_publication_effect="GRANTED"))
        self.reject(lambda p: p.update(media_or_artwork_bytes_stored=True))

    def test_url_lineage_and_schema_drift_fail_closed(self):
        self.reject(lambda p: p["sources"][1].update(locator=p["sources"][0]["locator"]))
        self.reject(lambda p: p["sources"].append(copy.deepcopy(p["sources"][0])))
        self.reject(lambda p: p["sources"][2]["withheld_fields"].clear())
        self.reject(lambda p: p.update(auto_merge=True))
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"source":"A","source":"B"}', object_pairs_hook=v.nodupes)

    def test_optimized_python_mode_enforces_rejections(self):
        code = """
import copy,sys
sys.path.insert(0,sys.argv[1]);import validate as v
p=v.reviewed();d=v.load(v.DISCOVERY);o=v.load(v.PRIOR)
for edit in (lambda x:x['sources'][2].update(runtime_minutes_verified_directly=95),
             lambda x:x.update(artwork_publication_effect='GRANTED')):
    b=copy.deepcopy(p);edit(b)
    try:v.validate(b,d,o)
    except ValueError:pass
    else:raise SystemExit('optimization bypass')
"""
        result = subprocess.run([sys.executable, "-O", "-c", code, str(HERE)],
                                capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
