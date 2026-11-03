"""Hostile mutation checks, including optimized-mode execution."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("beyond_metadata_guard", HERE / "validate.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class BeyondMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = guard.read_pinned()
        cls.discovery = json.loads(guard.DISCOVERY_PATH.read_text())
        cls.prior = json.loads(guard.PRIOR_PATH.read_text())

    def reject(self, mutation):
        bad = copy.deepcopy(self.packet)
        mutation(bad)
        with self.assertRaises(ValueError):
            guard.validate(bad, self.discovery, self.prior)

    def test_exact_source_observation(self):
        self.assertEqual(guard.validate(self.packet, self.discovery, self.prior), 1)

    def test_cannot_forge_film_coverage_or_publication(self):
        for key, value in (
            ("film_viewed", True), ("full_text_available", True),
            ("accepted_coverage_effect", "CLOSE_READ"),
            ("accepted_source_work_binding_effect", "ACCEPTED"),
            ("public_synopsis_release_effect", "RELEASED"),
            ("artwork_release_effect", "DISPLAY_APPROVED"),
            ("image_bytes_fetched", True),
        ):
            with self.subTest(key=key):
                self.reject(lambda b: b.update({key: value}))

    def test_cannot_swap_film_or_publisher_source(self):
        self.reject(lambda b: b.update(candidate_film_id="film-2009"))
        self.reject(lambda b: b.update(source_locator="https://www.startrek.com/movies/star-trek-beyond"))
        self.reject(lambda b: b.update(source_group="independent-review"))
        self.reject(lambda b: b.update(provenance_family="independently verified"))
        self.reject(lambda b: b.update(source_page_sha256="0" * 64))
        self.reject(lambda b: b.update(baseline_accepted_main="0" * 40))

    def test_cannot_invent_or_swap_cast_and_runtime(self):
        self.reject(lambda b: b["observation"].update(running_time_as_listed_minutes=132))
        self.reject(lambda b: b["observation"].update(runtime_scope="ALL_EDITION_RUNTIME"))
        self.reject(lambda b: b["observation"]["cast_as_listed"][0].update(role="Kirk"))
        self.reject(lambda b: b["observation"].update(director_as_listed="J. J. Abrams"))
        self.reject(lambda b: b["observation"].update(writers_as_listed=["Simon Pegg"]))

    def test_cannot_erase_editorial_boundary_or_invent_synopsis(self):
        self.reject(lambda b: b["observation"].update(synopsis_publication_status="APPROVED"))
        self.reject(lambda b: b["observation"].update(synopsis_candidate="A new film synopsis without observation"))
        self.reject(lambda b: b["observation"].update(poster_url="https://example.com/image.jpg"))
        self.reject(lambda b: b.update(extra_approval=True))

    def test_prior_source_is_not_independent_corroboration(self):
        prior = copy.deepcopy(self.prior)
        next(r for r in prior["records"] if r["candidate_film_id"] == "film-beyond")["source_locator"] = guard.PARAMOUNT
        with self.assertRaises(ValueError):
            guard.validate(self.packet, self.discovery, prior)

    def test_source_bytes_pin_and_duplicate_key(self):
        self.assertEqual(len(guard.PINNED_BYTES_SHA256), 64)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"role":"FILMS","role":"AUDITOR"}', object_pairs_hook=guard.no_duplicate_keys)

    def test_optimized_mode_fails_closed(self):
        code = """
import copy,json,sys
sys.path.insert(0,sys.argv[1]); import validate as g
one=g.read_pinned(); d=json.loads(g.DISCOVERY_PATH.read_text()); p=json.loads(g.PRIOR_PATH.read_text())
for kind, fake in [('running_time_as_listed_minutes',123),('director_as_listed','Somebody Else')]:
    x=copy.deepcopy(one); x['observation'][kind]=fake
    try:g.validate(x,d,p)
    except ValueError:pass
    else:raise SystemExit('optimized bypass '+kind)
"""
        result = subprocess.run([sys.executable, "-O", "-c", code, str(HERE)],
                                capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
