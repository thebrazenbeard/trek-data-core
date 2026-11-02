"""Discovery-only film catalog integrity and non-admission regression tests."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools import build_film_catalog as films


ROOT = Path(__file__).resolve().parents[1]


class FilmDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.source = films.read_proposal(ROOT)

    def test_real_proposal_is_discovery_only(self):
        data = films.validate(self.source)
        self.assertEqual(data["film_count"], 14)
        self.assertEqual(data["coverage_effect"], "NONE")
        self.assertEqual({row["verification_status"] for row in data["films"]}, {"UNVERIFIED_METADATA"})
        self.assertNotIn("canonical_work_id", json.dumps(data))
        self.assertEqual([row["discovery_source"] for row in data["films"]].count("OFFICIAL_ANNOUNCEMENT"), 1)

    def test_emitted_view_matches_builder(self):
        self.assertEqual((ROOT / films.OUTPUT).read_bytes(), films.build(ROOT))

    def test_duplicate_ids_rejected(self):
        bad = copy.deepcopy(self.source)
        bad["films"][1]["id"] = bad["films"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            films.validate(bad)

    def test_duplicate_official_locator_rejected(self):
        bad = copy.deepcopy(self.source)
        bad["films"][1]["source_locator"] = bad["films"][0]["source_locator"]
        with self.assertRaisesRegex(ValueError, "duplicate official publisher locator"):
            films.validate(bad)

    def test_fabricated_admission_rejected(self):
        bad = copy.deepcopy(self.source)
        bad["films"][0]["admission_status"] = "ACCEPTED"
        with self.assertRaisesRegex(ValueError, "admission-like"):
            films.validate(bad)
        bad = copy.deepcopy(self.source)
        bad["coverage_effect"] = "SOURCE_BOUND"
        with self.assertRaisesRegex(ValueError, "coverage"):
            films.validate(bad)

    def test_external_locator_rejected(self):
        bad = copy.deepcopy(self.source)
        bad["films"][0]["source_locator"] = "https://evil.example/movies/star-trek"
        with self.assertRaisesRegex(ValueError, "permitted official"):
            films.validate(bad)
        bad["films"][0]["source_locator"] = "https://www.startrek.com@evil.example/movies/star-trek"
        with self.assertRaisesRegex(ValueError, "permitted official"):
            films.validate(bad)

    def test_section31_must_be_supplementary(self):
        bad = copy.deepcopy(self.source)
        bad["films"][-1]["discovery_source"] = "OFFICIAL_DIRECTORY"
        with self.assertRaisesRegex(ValueError, "permitted official"):
            films.validate(bad)

    def test_conflicted_search_for_spock_year_is_not_assigned(self):
        data = films.validate(self.source)
        item = next(row for row in data["films"] if row["id"] == "film-search-for-spock")
        self.assertNotIn("release_year", item)
        manifest = (ROOT / films.INPUT.parent / "MANIFEST.md").read_text(encoding="utf-8")
        self.assertIn("1982", manifest)
        self.assertIn("1984", manifest)

    def test_bad_publisher_lineage_rejected(self):
        bad = copy.deepcopy(self.source)
        bad["source_group"] = "independent:verified"
        with self.assertRaisesRegex(ValueError, "lineage"):
            films.validate(bad)

    def test_check_fails_on_modified_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            proposal = root / films.INPUT
            proposal.parent.mkdir(parents=True)
            proposal.write_text(json.dumps(self.source), encoding="utf-8")
            output = root / films.OUTPUT
            output.parent.mkdir()
            output.write_bytes(films.build(root))
            self.assertEqual(films.main(["--repo-root", folder, "--check"]), 0)
            output.write_bytes(b"{}\n")
            self.assertEqual(films.main(["--repo-root", folder, "--check"]), 1)

    def test_builder_refuses_symlinked_output_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            proposal = root / films.INPUT
            proposal.parent.mkdir(parents=True)
            proposal.write_text(json.dumps(self.source), encoding="utf-8")
            escaped = root / "elsewhere"
            escaped.mkdir()
            (root / "explorer").symlink_to(escaped, target_is_directory=True)
            self.assertEqual(films.main(["--repo-root", folder]), 1)
            self.assertFalse((escaped / "film-catalog.json").exists())
            self.assertEqual(films.main(["--repo-root", folder, "--check"]), 1)


if __name__ == "__main__":
    unittest.main()
