"""Hostile source, packaging, rights and optimized-mode regressions."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("star_trek_2009_guard", HERE / "validate.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class Film2009PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = guard.read_pinned()
        cls.registry = json.loads(guard.DISCOVERY.read_text())

    def reject(self, mutation):
        sample = copy.deepcopy(self.data)
        mutation(sample)
        with self.assertRaises(ValueError):
            guard.validate(sample, self.registry)

    def test_source_local_four_formats(self):
        self.assertEqual(guard.validate(self.data, self.registry), 4)

    def test_film_and_corporate_lineage_pinned(self):
        self.reject(lambda s: s.update(candidate_film_id="film-into-darkness"))
        self.reject(lambda s: s.update(source_group="three-independent-publishers"))
        self.reject(lambda s: s.update(independence_note="independent confirmation"))
        self.reject(lambda s: s["sources"].update(home_release_2009_pdf="https://fan.example/guess.pdf"))
        self.reject(lambda s: s.update(baseline_accepted_main="0" * 40))

    def test_packaging_is_not_interchangeable(self):
        self.reject(lambda s: s["cards"][0].update(edition_type="SINGLE_DISC_DVD"))
        self.reject(lambda s: s["cards"][1].update(local_id="phe-2009-dvd-single-disc"))
        self.reject(lambda s: s["cards"][2].update(publisher_media_description="Includes a Blu-ray disc"))
        self.reject(lambda s: s["cards"][3].update(source_key="home_release_2009_pdf"))
        self.reject(lambda s: s["cards"].pop())

    def test_no_claim_of_actual_media_art_or_current_rights(self):
        self.reject(lambda s: s["cards"][3].update(artwork_lead="PUBLIC_LICENSED_KEY_ART"))
        self.reject(lambda s: s["cards"][3].update(display_eligible=True))
        self.reject(lambda s: s["cards"][3].update(image_url="https://cdn.example/poster.jpg"))
        self.reject(lambda s: s.update(media_bytes_fetched=True))
        self.reject(lambda s: s.update(artwork_bytes_fetched=True))
        self.reject(lambda s: s.update(artwork_release_effect="APPROVED"))
        self.reject(lambda s: s.update(accepted_coverage_effect="CLOSE_READ"))

    def test_claims_not_automatically_edition_specific(self):
        self.reject(lambda s: s["source_observations"].update(runtime_scope="ALL_EDITION_BITSTREAMS_VERIFIED"))
        self.reject(lambda s: s["source_observations"].update(home_sheet_runtime_as_listed_minutes=128))
        self.reject(lambda s: s["cards"][3].update(historical_release_date="2026-11-03"))

    def test_source_relative_synopsis_not_publication(self):
        self.reject(lambda s: s["source_observations"].update(source_relative_synopsis_candidate="Unrelated fabricated story"))
        self.reject(lambda s: s.update(public_synopsis_release_effect="RELEASED"))
        self.reject(lambda s: s["source_observations"].update(synopsis_status="FULL_FILM_CLOSE_READ"))

    def test_json_duplicate_key_and_pin(self):
        self.assertEqual(len(guard.PINNED_SHA256), 64)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"role":"FILMS","role":"LIBRARIAN"}', object_pairs_hook=guard.no_dupes)

    def test_optimized_mode_mutations_fail(self):
        code = """
import copy,json,sys
sys.path.insert(0,sys.argv[1]); import validate as g
p=g.read_pinned(); r=json.loads(g.DISCOVERY.read_text())
for m in (lambda x:x['cards'][3].update(display_eligible=True),
          lambda x:x['cards'][2].update(edition_type='THREE_DISC_BLURAY_WITH_DIGITAL_COPY'),
          lambda x:x.update(accepted_coverage_effect='CLOSE_READ')):
    z=copy.deepcopy(p);m(z)
    try:g.validate(z,r)
    except ValueError:pass
    else:raise SystemExit('optimized bypass')
"""
        result = subprocess.run([sys.executable, "-O", "-c", code, str(HERE)],
                                capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
