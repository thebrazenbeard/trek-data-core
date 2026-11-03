"""Hostile invariant tests for publisher-described film summaries, not watched films."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/research/films/publisher-synopses-20261103"
spec = importlib.util.spec_from_file_location("film_publisher_synopsis_validator", PROPOSAL / "validate.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
OBS = module.read_pinned()
FILMS = json.loads((ROOT / "explorer/film-catalog.json").read_text(encoding="utf-8"))


class PublisherFilmSynopsisProposalTests(unittest.TestCase):
    def test_fourteen_source_local_publisher_descriptions_validate(self):
        self.assertEqual(module.validate(OBS), 14)
        self.assertEqual(len({r["directory_row_id"] for r in OBS["records"]}), 14)

    def reject(self, mutate):
        bad = copy.deepcopy(OBS)
        mutate(bad)
        with self.assertRaises(ValueError):
            module.validate(bad)

    def reject_film_catalog(self, mutate):
        bad = copy.deepcopy(FILMS)
        mutate(bad)
        with self.assertRaises(ValueError):
            module.validate(OBS, bad)

    def test_not_full_film_or_evidence_admission(self):
        for key, value in (("full_film_viewed", True), ("source_bound", True),
                           ("close_read", True), ("accepted_evidence_effect", "ACCEPTED"),
                           ("accepted_coverage_effect", "CLOSE_READ")):
            with self.subTest(key=key):
                self.reject(lambda d: d.update({key: value}))

    def test_not_public_synopsis_or_artwork_release(self):
        for key in ("public_synopsis_release_effect", "artwork_release_effect",
                    "accepted_source_work_binding_effect"):
            with self.subTest(key=key):
                self.reject(lambda d: d.update({key: "RELEASED"}))

    def test_no_fabricated_raw_web_page_digest(self):
        self.reject(lambda d: d.update(raw_source_page_sha256="0" * 64))

    def test_no_forged_independent_upstream_witness_count(self):
        self.reject(lambda d: d.update(upstream_source_families=14))

    def test_no_swapped_film_or_unrelated_source(self):
        self.reject(lambda d: d["records"][0].update(candidate_film_id="film-nemesis"))
        self.reject(lambda d: d["records"][0].update(source_locator="https://startrek.com.evil.example/movies/x"))

    def test_publisher_catalog_change_or_source_host_spoof_rejected(self):
        self.reject_film_catalog(lambda d: d["films"][0].update(source_group="publisher:memory-alpha"))
        self.reject_film_catalog(lambda d: d["films"][0].update(
            source_locator="https://www.startrek.com@evil.invalid/movies/star-trek-i-the-motion-picture"))

    def test_no_unreviewed_synopsis_or_source_section_edit(self):
        self.reject(lambda d: d["records"][0].update(
            synopsis="The title is changed to a new and unsupported story about an imaginary battle."))
        self.reject(lambda d: d["records"][13].update(source_section="Complete film transcript"))

    def test_section_31_remains_publisher_announcement_not_movie_synopsis(self):
        row = next(r for r in OBS["records"] if r["candidate_film_id"] == "film-section-31")
        self.assertIsNone(row["publisher_display_year"])
        self.assertTrue(row["source_locator"].startswith("https://www.startrek.com/news/"))
        self.reject(lambda d: d["records"][13].update(publisher_display_year="2025"))

    def test_search_for_spock_factual_conflict_is_retained(self):
        row = next(r for r in OBS["records"] if r["candidate_film_id"] == "film-search-for-spock")
        self.assertEqual(row["publisher_display_year"], "1982")
        self.assertEqual(OBS["source_year_conflict"]["catalog_lists_release_date"], "1984-06-01")
        self.reject(lambda d: d["records"][2].update(publisher_display_year="1984"))
        self.reject(lambda d: d["source_year_conflict"].update(disposition="RECONCILED_1984"))


if __name__ == "__main__":
    unittest.main()
