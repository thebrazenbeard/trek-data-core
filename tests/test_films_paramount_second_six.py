"""Hostile regressions for source-bound six-film Paramount publisher packet."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


HERE = Path(__file__).resolve().parents[1] / "proposals/films/paramount-second-six-pages-20261103"
spec = importlib.util.spec_from_file_location("paramount_second_six", HERE / "validate.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class PublisherSecondSixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = v.reviewed()
        cls.registry = v.load(v.REGISTRY)
        cls.previous = v.load(v.PREVIOUS)
        cls.prior = v.load(v.STAR_TREK_PRIOR)

    def reject(self, mutate):
        data = copy.deepcopy(self.packet)
        mutate(data)
        with self.assertRaises(ValueError):
            v.validate(data, self.registry, self.previous, self.prior)

    def test_six_distinct_publisher_source_local_rows(self):
        self.assertEqual(v.validate(self.packet, self.registry, self.previous, self.prior), 6)

    def test_no_acceptance_or_artwork_release_inflation(self):
        for field, forged in (
            ("full_film_viewed", True), ("accepted_coverage_effect", "CLOSE_READ"),
            ("accepted_source_work_binding_effect", "ACCEPTED"),
            ("public_synopsis_release_effect", "APPROVED"),
            ("public_artwork_release_effect", "APPROVED"), ("poster_bytes_stored", True),
            ("source_page_sha256", "0" * 64),
            ("source_lineage", "Independent primary film witnesses"),
        ):
            with self.subTest(field=field):
                self.reject(lambda p, k=field, x=forged: p.update({k: x}))

    def test_exact_source_and_local_film_binding(self):
        self.reject(lambda p: p["records"][0].update(candidate_film_id="film-motion-picture"))
        self.reject(lambda p: p["records"][1].update(candidate_film_id="film-search-for-spock"))
        self.reject(lambda p: p["records"][4].update(source_locator="https://www.paramount.com/movies/star-trek-x-nemesis"))
        self.reject(lambda p: p["records"][3].update(local_id="paramount-nemesis-page-20261103"))
        self.reject(lambda p: p["records"][4].update(poster_asset_locator=p["records"][5]["poster_asset_locator"]))
        self.reject(lambda p: p["records"][5].update(poster_status="DISPLAY_ELIGIBLE"))
        self.reject(lambda p: p["records"][2].update(runtime_as_listed_minutes=132))
        self.reject(lambda p: p["records"][0].update(year_as_listed=1982))

    def test_unresolved_publisher_disagreements_remain_visible(self):
        self.reject(lambda p: p["records"][0].update(source_anomaly=None))
        self.reject(lambda p: p["records"][4].update(source_anomaly=None))
        self.reject(lambda p: p["records"][4]["selected_creative_roles_as_listed"][1].update(person="Michael Piller"))
        self.reject(lambda p: p["records"][4]["selected_cast_as_listed"][1].update(role="Ru'afo"))

    def test_no_duplicate_keys_or_new_public_image_fields(self):
        self.reject(lambda p: p["records"][3].update(public_poster_url="https://example.org/poster.jpg"))
        self.reject(lambda p: p.update(auto_publish=True))
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"poster_status":"HELD","poster_status":"PUBLISHED"}', object_pairs_hook=v.nodupes)

    def test_prior_accepted_paramount_overlap_rejected(self):
        other = copy.deepcopy(self.previous)
        other["records"].append({"candidate_film_id": "film-voyage-home"})
        with self.assertRaises(ValueError):
            v.validate(self.packet, self.registry, other, self.prior)

    def test_optimized_mode_guards_are_real(self):
        code = """
import copy,sys
sys.path.insert(0,sys.argv[1]); import validate as v
d=v.reviewed(); r=v.load(v.REGISTRY);a=v.load(v.PREVIOUS);p=v.load(v.STAR_TREK_PRIOR)
for key,val in [('poster_status','APPROVED'),('runtime_as_listed_minutes',0)]:
    x=copy.deepcopy(d);x['records'][0][key]=val
    try:v.validate(x,r,a,p)
    except ValueError:pass
    else:raise SystemExit('optimized bypass')
"""
        result = subprocess.run([sys.executable, "-O", "-c", code, str(HERE)],
                                capture_output=True, text=True, check=False, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
