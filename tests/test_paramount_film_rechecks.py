"""Source-local Paramount film page projection, release and adversarial tests."""

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_paramount_film_rechecks as builder  # noqa: E402
import query_paramount_film_rechecks as search  # noqa: E402


class ParamountFilmRechecksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = builder.build()

    def test_exact_thirteen_records_source_local_counts_and_sha(self):
        a = self.artifact
        self.assertEqual((a["row_count"], a["source_anomaly_held_count"]), (13, 3))
        self.assertEqual(len(a["accepted_source_input_receipts"]), 3)
        self.assertEqual({r["source_local_candidate_id"] for r in a["rows"]}, builder.EXPECTED_IDS)
        self.assertEqual(sum(r["recheck_status"] == "HELD_UNRESOLVED_SOURCE_ANOMALY" for r in a["rows"]), 3)
        self.assertEqual((ROOT / builder.OUTPUT).read_bytes(), builder.encode(a))
        for receipt in a["accepted_source_input_receipts"]:
            self.assertEqual(hashlib.sha256((ROOT / receipt["path"]).read_bytes()).hexdigest(),
                             receipt["sha256"])

    def test_rights_source_and_unknown_identity_boundaries(self):
        a = self.artifact
        self.assertEqual((a["full_films_viewed"], a["distinct_works_admitted"],
                          a["synopses_released"], a["artwork_released"]), (0, 0, 0, 0))
        for r in a["rows"]:
            self.assertEqual((r["coverage_effect"], r["work_admission_effect"],
                              r["synopsis_release_effect"], r["artwork_release_effect"]),
                             ("NONE", "NONE", "NONE", "NONE"))
            self.assertEqual(r["source_identity_scope"], "SOURCE_LOCAL_CANDIDATE")
            self.assertTrue(r["source_locator"].startswith("https://www.paramount.com/movies/"))
            self.assertEqual(r["film_viewed"], False)
            self.assertIn("publisher:paramount.com", r["tags"])
            self.assertNotIn("verified_work", r["tags"])
            self.assertEqual(len(set(r["tags"])), len(r["tags"]))
        raw = builder.encode(a).decode("utf-8")
        for forbidden in ("original_synopsis_candidate", "synopsis_candidate", "poster_asset_locator",
                          "poster_bytes", "poster_medium", ".jpg", ".png", "image_data",
                          "C:\\Users", "/mnt/d/", "OneDrive/", "work_identity"):
            self.assertNotIn(forbidden, raw)

    def test_callable_exact_tag_year_source_status_search(self):
        rows = self.artifact["rows"]
        self.assertEqual(len(search.query(rows)), 13)
        self.assertEqual(len(search.query(rows, status="HELD_UNRESOLVED_SOURCE_ANOMALY")), 3)
        self.assertEqual([r["source_local_candidate_id"] for r in search.query(rows, text="khan")],
                         ["film-wrath-of-khan"])
        self.assertEqual(len(search.query(rows, tag="publisher:paramount.com", year=2016)), 1)
        self.assertEqual(len(search.query(rows, tag="anomaly:held")), 3)
        with self.assertRaises(ValueError):
            search.query(rows, limit=9999999)
        with self.assertRaises(ValueError):
            search.query(rows, text="x" * 151)

    def test_outside_publisher_or_forged_admission_fails(self):
        real = builder.read_reviewed
        for kind in ("foreign_url", "admission", "lost_anomaly"):
            def corrupt(path, pin_name):
                data, raw, pin = real(path, pin_name)
                if path == builder.INPUTS[1][1]:
                    data = copy.deepcopy(data)
                    if kind == "foreign_url":
                        data["records"][0]["source_locator"] = "https://evil.example/movies/star-trek"
                    elif kind == "admission":
                        data["accepted_coverage_effect"] = "CLOSE_READ"
                    else:
                        data["records"][0]["source_anomaly"] = None
                return data, raw, pin
            with self.subTest(kind=kind), patch.object(builder, "read_reviewed", side_effect=corrupt):
                with self.assertRaises(ValueError):
                    builder.build()

    def test_original_source_byte_pin_rejects_changed_status_or_url_on_disk(self):
        paths = [p for _, p, _, _ in builder.INPUTS]
        for kind in ("status", "same_host_page_rebinding"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                for path in paths:
                    (root / path.parent).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(ROOT / path.parent, root / path.parent)
                for dependency in (
                    "proposals/librarian/films-official-index-20261102/bundle.json",
                    "proposals/research/films/publisher-synopses-20261103/observations.json",
                ):
                    (root / dependency).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / dependency, root / dependency)
                path = root / paths[0]
                data = json.loads(path.read_text(encoding="utf-8"))
                a, b = data["records"][:2]
                if kind == "status":
                    data["accepted_coverage_effect"] = "CLOSE_READ"
                else:
                    for key in ("source_locator", "year_as_listed", "rating_as_listed",
                                "runtime_as_listed_minutes"):
                        a[key], b[key] = b[key], a[key]
                path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                with patch.object(builder, "ROOT", root):
                    with self.assertRaisesRegex(ValueError, "Unreviewed official film-page source bytes"):
                        builder.build()

    def test_cli_queries_verify_committed_compiler_output(self):
        script = ROOT / "tools/query_paramount_film_rechecks.py"
        completed = subprocess.run([sys.executable, str(script), "--tag", "anomaly:held",
                                    "--limit", "3"], text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(completed.stdout)["match_count"], 3)


if __name__ == "__main__":
    unittest.main()
