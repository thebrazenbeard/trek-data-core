"""Hostile checks for accepted source-local Paramount distributor film candidate packet."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "proposals/films/paramount-six-source-pages-20261103"
spec = importlib.util.spec_from_file_location("paramount_six_guard", HERE / "validate.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class ParamountSixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = guard.load_reviewed()
        cls.discovery = guard.load(guard.DISCOVERY)
        cls.prior = guard.load(guard.SYNOPSES)
        cls.beyond = guard.load(guard.BEYOND)

    def reject(self, mutate) -> None:
        bad = copy.deepcopy(self.packet)
        mutate(bad)
        with self.assertRaises(ValueError):
            guard.validate(bad, self.discovery, self.prior, self.beyond)

    def test_observations_are_source_local(self) -> None:
        self.assertEqual(guard.validate(self.packet, self.discovery, self.prior, self.beyond), 6)

    def test_cannot_claim_coverage_or_publication(self) -> None:
        for key, forged in (
            ("full_film_viewed", True),
            ("accepted_source_work_binding_effect", "ADMITTED"),
            ("accepted_coverage_effect", "CLOSE_READ"),
            ("public_synopsis_release_effect", "APPROVED"),
            ("public_artwork_release_effect", "APPROVED"),
            ("poster_bytes_stored", True),
            ("source_page_sha256", "a" * 64),
            ("source_lineage", "independently confirmed"),
        ):
            with self.subTest(key=key):
                self.reject(lambda x, k=key, v=forged: x.update({k: v}))

    def test_cannot_substitute_film_or_artwork(self) -> None:
        self.reject(lambda x: x["records"][0].update(candidate_film_id="film-beyond"))
        self.reject(lambda x: x["records"][1].update(candidate_film_id="film-motion-picture"))
        self.reject(lambda x: x["records"][2].update(source_locator="https://www.paramount.com/movies/other"))
        self.reject(lambda x: x["records"][4].update(poster_asset_locator=x["records"][5]["poster_asset_locator"]))
        self.reject(lambda x: x["records"][3].update(poster_status="DISPLAY_APPROVED"))
        self.reject(lambda x: x["records"][3].update(source_anomaly=None))
        self.reject(lambda x: x["records"][3].update(selected_creative_roles_as_listed=[]))
        self.reject(lambda x: x["records"][3].update(rating_as_listed="PG"))
        self.reject(lambda x: x["records"][0].update(runtime_as_listed_minutes=100))
        self.reject(lambda x: x["records"].append(copy.deepcopy(x["records"][0])))

    def test_cannot_inject_extra_fields_or_duplicate_json_keys(self) -> None:
        self.reject(lambda x: x["records"][0].update(licensed_image_url="https://example.org/1.jpg"))
        self.reject(lambda x: x.update(public_page_effect=True))
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"poster_status":"HELD","poster_status":"APPROVED"}',
                       object_pairs_hook=guard.pairs_no_dupes)

    def test_prior_lineage_changes_are_rejected(self) -> None:
        before = copy.deepcopy(self.prior)
        before["records"][0]["source_locator"] = self.packet["records"][0]["source_locator"]
        with self.assertRaises(ValueError):
            guard.validate(self.packet, self.discovery, before, self.beyond)

    def test_optimized_python_keeps_enforcing_guards(self) -> None:
        code = """
import copy,sys
sys.path.insert(0,sys.argv[1]); import validate as g
p=g.load_reviewed(); d=g.load(g.DISCOVERY); b=g.load(g.BEYOND); s=g.load(g.SYNOPSES)
for field,value in [('poster_status','DISPLAY_APPROVED'),('runtime_as_listed_minutes',999)]:
    x=copy.deepcopy(p); x['records'][0][field]=value
    try: g.validate(x,d,s,b)
    except ValueError: pass
    else: raise SystemExit('guard bypassed')
"""
        run = subprocess.run([sys.executable, "-O", "-c", code, str(HERE)],
                             capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
