"""Adversarial checks for first-party release-source availability distinctions."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


HERE = Path(__file__).resolve().parents[1] / "proposals/films/release-primary-access-ledger-20261103"
spec = importlib.util.spec_from_file_location("release_source_access", HERE / "validate.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class SourceAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = v.reviewed()
        cls.discovery = v.load(v.DISCOVERY)
        cls.prior = v.load(v.PR329)

    def reject(self, edit):
        bad = copy.deepcopy(self.packet)
        edit(bad)
        with self.assertRaises(ValueError):
            v.validate(bad, self.discovery, self.prior)

    def test_two_direct_html_and_three_blocked_source_locs(self):
        self.assertEqual(v.validate(self.packet, self.discovery, self.prior), 5)

    def test_cannot_promote_cached_snippet_to_direct_source(self):
        self.reject(lambda p: p["source_access_observations"][1].update(access_class="DIRECT_FIRST_PARTY_HTML_READ"))
        self.reject(lambda p: p["source_access_observations"][3].update(reliably_source_observed_fields=["runtime_131_verified"]))
        self.reject(lambda p: p["source_access_observations"][4].update(web_reader_status="RETRIEVED_CONTENT_READ"))
        self.reject(lambda p: p["source_access_observations"][1].update(web_reader_status="HTTP_200"))

    def test_cannot_swap_sources_film_or_targets(self):
        self.reject(lambda p: p["source_access_observations"][2].update(candidate_film_id="film-2009"))
        self.reject(lambda p: p["source_access_observations"][0].update(source_locator=p["source_access_observations"][1]["source_locator"]))
        self.reject(lambda p: p["related_held_proposals"][0].update(pr=325))
        self.reject(lambda p: p.update(accepted_film_page_overlap="independent synopsis"))

    def test_cannot_publish_media_or_make_unsupported_cut_claim(self):
        self.reject(lambda p: p.update(accepted_coverage_effect="SOURCE_BOUND"))
        self.reject(lambda p: p.update(source_work_binding_effect="ACCEPTED"))
        self.reject(lambda p: p.update(public_synopsis_release_effect="RELEASED"))
        self.reject(lambda p: p.update(artwork_release_effect="LICENSED"))
        self.reject(lambda p: p.update(media_or_artwork_bytes_stored=True))
        self.reject(lambda p: p["source_access_observations"][2]["withheld_fields"].remove("audiovisual_cut_or_copy_hash"))

    def test_duplicate_key_and_extra_fields(self):
        self.reject(lambda p: p["source_access_observations"][0].update(public_image_url="https://example.com/poster.jpg"))
        self.reject(lambda p: p.update(auto_merge=True))
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"access_class":"DIRECT","access_class":"INDEX_ONLY"}', object_pairs_hook=v.nodupes)

    def test_optimized_mode_rejects_forgery(self):
        code = """
import copy,sys
sys.path.insert(0,sys.argv[1]); import validate as v
p=v.reviewed();d=v.load(v.DISCOVERY);o=v.load(v.PR329)
for edit in (lambda x:x['source_access_observations'][3].update(access_class='DIRECT_FIRST_PARTY_HTML_READ'),
             lambda x:x.update(accepted_coverage_effect='CLOSE_READ')):
    b=copy.deepcopy(p);edit(b)
    try:v.validate(b,d,o)
    except ValueError:pass
    else:raise SystemExit('optimized bypass')
"""
        result = subprocess.run([sys.executable, "-O", "-c", code, str(HERE)],
                                capture_output=True, text=True, check=False, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
