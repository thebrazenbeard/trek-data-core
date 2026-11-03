"""Structural search and non-admission contract regression tests."""

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_source_local_search import build, encoded, normalized  # noqa: E402
from query_trek_index import query, validate  # noqa: E402


class SourceLocalSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = build()
        cls.rows = validate(cls.index, root=ROOT)

    def test_committed_index_is_exact_rebuild(self):
        self.assertEqual((ROOT / "explorer/search-catalog.json").read_bytes(), encoded(self.index))
        self.assertEqual(self.index["row_count"], 1214)
        self.assertEqual(self.index["denominator_status"], "NOT_ESTABLISHED")
        self.assertEqual(self.index["facet_counts"]["synopsis_status"]["reviewed_publisher_paraphrase"], 37)
        self.assertEqual(sum(count for key, count in self.index["facet_counts"]["metadata_recheck_status"].items() if key != "not_rechecked"), 56)
        self.assertEqual(sum(self.index["facet_counts"]["medium"].values()), 1214)

    def test_exact_source_local_ids_preserve_duplicate_leads(self):
        result = query(self.rows, text="Doomsday Machine", series="TOS")
        self.assertEqual(result["total_matches"], 2)
        self.assertEqual([r["row_id"] for r in result["rows"]], ["lead:0000", "legacy:s2:tos:005"])
        self.assertTrue(all(r["admission_effect"] == "NONE" for r in result["rows"]))

    def test_status_tags_and_cross_facet_queries(self):
        self.assertEqual(query(self.rows, tags=("synopsis:reviewed_publisher_paraphrase",))["total_matches"], 37)
        self.assertEqual(query(self.rows, verification="rechecked_exact")["total_matches"], 52)
        self.assertEqual(query(self.rows, verification="rechecked_unresolved")["total_matches"], 4)
        self.assertEqual(query(self.rows, medium="AUDIO")["total_matches"], 1)
        self.assertEqual(query(self.rows, medium="LITERATURE", synopsis="reviewed_publisher_paraphrase")["total_matches"], 9)
        for row in query(self.rows, tags=("series:ds9", "medium:episode"), limit=100)["rows"]:
            self.assertEqual(row["series_code"], "DS9")

    def test_stable_bounded_paging(self):
        first = query(self.rows, medium="EPISODE", limit=37)
        second = query(self.rows, medium="EPISODE", limit=37, offset=first["next_offset"])
        self.assertEqual(first["total_matches"], second["total_matches"])
        self.assertEqual(first["next_offset"], 37)
        self.assertEqual(second["offset"], 37)
        self.assertEqual(set(r["row_id"] for r in first["rows"]) & set(r["row_id"] for r in second["rows"]), set())
        self.assertEqual(query(self.rows, offset=1000000)["rows"], [])

    def test_normalization_and_nonsemantic_tags(self):
        self.assertEqual(normalized("ÉTOILE"), normalized("étoile"))
        self.assertGreaterEqual(query(self.rows, text="TROUBLE WITH TRIBBLES")["total_matches"], 2)
        self.assertEqual(query(self.rows, tags=("theme:hope",))["total_matches"], 0)
        self.assertFalse(any(tag.startswith(("theme:", "ethic:", "canon:", "entity:", "work:"))
                             for row in self.rows for tag in row["tags"]))

    def test_reject_promoted_malformed_duplicate_and_source_drift(self):
        for mutate in (
            lambda d: d.update(admission_effect="ADMITTED"),
            lambda d: d["rows"][0].update(identity_scope="GLOBAL"),
            lambda d: d["rows"][1].update(row_id=d["rows"][0]["row_id"]),
            lambda d: d["source_input_sha256"][0].update(sha256="0" * 64),
            lambda d: d["rows"][0].update(source_locator="javascript:alert(1)"),
            lambda d: d["rows"][0].update(tags=sorted(d["rows"][0]["tags"] + ["canon:prime-timeline", "work:verified"])),
            lambda d: d["rows"][0].update(tags=sorted(d["rows"][0]["tags"] + ["theme:hope"])),
            lambda d: d["rows"][0].update(series_code="TNG"),
            lambda d: d["facet_counts"]["medium"].update(EPISODE=100000),
        ):
            altered = copy.deepcopy(self.index)
            mutate(altered)
            with self.assertRaises(ValueError):
                validate(altered, root=ROOT)

    def test_html_like_payload_is_json_not_dom_or_execution(self):
        # CLI always uses JSON encoding; never embeds into HTML or unsafe innerHTML.
        query_result = query(self.rows, text="<script>alert('x')</script>")
        self.assertEqual(query_result["rows"], [])
        self.assertEqual(json.loads(json.dumps(query_result))["total_matches"], 0)

    def test_standalone_cli_and_negative_bounds(self):
        cli = ROOT / "tools/query_trek_index.py"
        okay = subprocess.run([sys.executable, str(cli), "--q", "Doomsday Machine", "--limit", "1"],
                              text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(okay.stdout)["next_offset"], 1)
        denied = subprocess.run([sys.executable, str(cli), "--limit", "10000000"],
                                text=True, capture_output=True)
        self.assertNotEqual(denied.returncode, 0)


if __name__ == "__main__":
    unittest.main()
