"""Source-only checks for the proposed, non-admitted Explorer directory."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_unified_discovery as discovery


ROOT = Path(__file__).resolve().parents[1]


class UnifiedDiscoveryTests(unittest.TestCase):
    def test_human_facing_directory_counts_track_the_exact_artifact(self):
        artifact = json.loads((ROOT / discovery.OUTPUT).read_bytes())
        rows = artifact["row_count"]
        episodes = artifact["counts_by_medium"]["EPISODE"]
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        contract = (ROOT / "docs/UNIFIED_DISCOVERY_DIRECTORY.md").read_text(encoding="utf-8")
        explorer_contract = (ROOT / "docs/EXPLORER_INDEX.md").read_text(encoding="utf-8")
        self.assertIn(f"**{rows} source-local metadata observations ({episodes} episode-related", readme)
        self.assertIn(f"**{rows} source observations** ({episodes} episode-related", readme)
        self.assertIn("not necessarily been published to Pages", readme)
        self.assertIn(f"**{rows} source-local rows**: {episodes} episode-related metadata", contract)
        self.assertIn(f"expanded {rows} rows consist of {episodes} episode-related observations", explorer_contract)

    def test_projection_is_deterministic_and_source_attributed(self):
        actual = (ROOT / discovery.OUTPUT).read_bytes()
        self.assertEqual(actual, discovery.build_bytes(ROOT))
        self.assertEqual(discovery.main(["--repo-root", str(ROOT), "--check"]), 0)
        catalog = json.loads(actual)
        self.assertEqual(catalog["data_status"], "DISCOVERY_ONLY")
        self.assertEqual(catalog["identity_scope"], "SOURCE_LOCAL_NOT_DEDUPLICATED")
        self.assertEqual(catalog["denominator_status"], "NOT_ESTABLISHED")
        self.assertEqual(catalog["coverage_effect"], "NONE")
        self.assertEqual(catalog["admission_effect"], "NONE")
        self.assertEqual(catalog["row_count"], len(catalog["rows"]))
        self.assertEqual(catalog["counts_by_medium"], {
            "EPISODE": 971, "FILM": 14, "LITERATURE": 1,
            "SHORT_FORM": 15, "AUDIO": 1,
        })
        self.assertEqual(len({r["row_id"] for r in catalog["rows"]}), 1002)
        self.assertTrue(all(r["identity_scope"] == "SOURCE_LOCAL" and
                            r["verification_status"] == "UNVERIFIED_METADATA" and
                            r["admission_effect"] == r["coverage_effect"] == "NONE"
                            for r in catalog["rows"]))
        self.assertEqual(len(catalog["source_digests"]), 112)
        for record in catalog["source_digests"]:
            source = ROOT / record["path"]
            self.assertEqual(record["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())

    def test_source_local_duplicates_not_collapsed_or_promoted(self):
        catalog = json.loads((ROOT / discovery.OUTPUT).read_bytes())
        rows = catalog["rows"]
        kinds = {kind: sum(r["candidate_kind"] == kind for r in rows)
                 for kind in discovery.KINDS}
        self.assertEqual(kinds, {
            "WIKIDATA_EPISODE": 208,
            "PUBLISHER_EPISODE_SLOT": 748,
            "PUBLISHER_REFERENCE": 15,
            "FEATURE_FILM": 13,
            "STREAMING_FILM": 1,
            "NOVEL": 1,
            "SCRIPTED_SHORT": 10,
            "PROMOTIONAL_ANIMATION": 5,
            "SCRIPTED_AUDIO_SERIES": 1,
        })
        # These are separate source-local attestations, not a deduplicated Work count.
        self.assertEqual(len({r["source_group"] for r in rows}) < len(rows), True)
        novel = next(r for r in rows if r["medium"] == "LITERATURE")
        self.assertEqual(len(novel["details"]), 4)
        self.assertEqual(len({part.split("ISBN ", 1)[1] for part in novel["details"]}), 4)
        for show in ("DS9", "VOY"):
            observed = [r["context"] for r in rows if r["row_id"].startswith(f"roster:{show.lower()}:")]
            self.assertIn(f"{show} S1E1", observed)
            self.assertIn(f"{show} S1E3", observed)
            self.assertNotIn(f"{show} S1E2", observed)
        self.assertGreater(catalog["counts_by_medium"]["EPISODE"], 218)
        modern = [r for r in rows if r["row_id"].startswith("roster:modern-s")]
        self.assertEqual(len(modern), 108)
        self.assertEqual(len([r for r in modern if r["row_id"].startswith("roster:modern-s3:")]), 43)
        for season, expected in ((1, 114), (2, 126), (3, 126)):
            legacy = [r for r in rows if r["row_id"].startswith(f"legacy:s{season}:")]
            self.assertEqual(len(legacy), expected)
            self.assertTrue(all(f" S{season}E" in r["context"] for r in legacy))
        prodigy = [r for r in rows if r["row_id"].startswith("prodigy:")]
        self.assertEqual(len(prodigy), 30)
        self.assertEqual(len([r for r in prodigy if r["context"].startswith("PRO S1E")]), 10)
        self.assertEqual(len([r for r in prodigy if r["context"].startswith("PRO S2E")]), 20)
        self.assertNotIn("PRO S1E10", {r["context"] for r in prodigy})
        self.assertIn("PRO S1E11", {r["context"] for r in prodigy})
        self.assertIn("PRO S2E20", {r["context"] for r in prodigy})
        self.assertTrue(all(r["source_group"] == "publisher:paramount" for r in prodigy))
        self.assertEqual({r["source_input"].split("/")[-2] for r in prodigy}, {"s1b", "s2"})
        season4 = [r for r in rows if r["row_id"].startswith("publisher:s4:")]
        self.assertEqual(len(season4), 122)
        for mission, count in (("tng", 26), ("ds9", 25), ("voy", 26),
                               ("ent", 22), ("dis", 13), ("ld", 10)):
            observed = [r for r in season4 if r["row_id"].startswith(f"publisher:s4:{mission}:")]
            self.assertEqual(len(observed), count)
            self.assertTrue(all(f"{mission.upper()} S4E" in r["context"] for r in observed))
            self.assertTrue(all(r["source_group"] == "publisher:paramount" for r in observed))
        ds9_contexts = {r["context"] for r in season4 if r["row_id"].startswith("publisher:s4:ds9:")}
        self.assertIn("DS9 S4E1", ds9_contexts)
        self.assertNotIn("DS9 S4E2", ds9_contexts)
        self.assertIn("DS9 S4E3", ds9_contexts)
        season5 = [r for r in rows if r["row_id"].startswith("publisher:s5:")]
        self.assertEqual(len(season5), 97)
        for mission, count in (("tng", 26), ("ds9", 26), ("voy", 25),
                               ("dis", 10), ("ld", 10)):
            observed = [r for r in season5 if r["row_id"].startswith(f"publisher:s5:{mission}:")]
            self.assertEqual(len(observed), count)
            self.assertTrue(all(f"{mission.upper()} S5E" in r["context"] for r in observed))
            self.assertTrue(all(r["source_group"] == "publisher:paramount" for r in observed))
        voy_s5_contexts = {r["context"] for r in season5 if r["row_id"].startswith("publisher:s5:voy:")}
        self.assertIn("VOY S5E15", voy_s5_contexts)
        self.assertNotIn("VOY S5E16", voy_s5_contexts)
        self.assertIn("VOY S5E17", voy_s5_contexts)
        self.assertFalse(any(r["row_id"].startswith("publisher:s5:ent:") for r in season5))
        self.assertEqual(len([r for r in rows if r["medium"] == "AUDIO"]), 1,
                         "one container, no invented audio episodes")

    def test_invalid_url_and_field_rejected(self):
        with self.assertRaises(ValueError):
            discovery._checked_url("https://evil.example/mission")
        with self.assertRaises(ValueError):
            discovery._checked_url("https://www.startrek.com@evil.example/mission")
        with self.assertRaises(ValueError):
            discovery._row("hello", "EPISODE", "NOVEL", "Title", "Context",
                           "lineage", "explorer/index.json", "https://evil.example/a")
        with self.assertRaises(ValueError):
            discovery._checked_title(" <script>\n")

    def test_stale_input_rejected_without_corroborating_generator(self):
        with patch.object(discovery.films, "build", return_value=b"{}"):
            with self.assertRaisesRegex(ValueError, "stale discovery source derivative"):
                discovery.build_bytes(ROOT)

    def test_output_symlink_parent_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            escape = root / "elsewhere"
            escape.mkdir()
            (root / "explorer").symlink_to(escape, target_is_directory=True)
            with self.assertRaises((OSError, ValueError)):
                discovery.publisher.safe_write(root, discovery.OUTPUT, b"untrusted")
            self.assertFalse((escape / "discovery-catalog.json").exists())


if __name__ == "__main__":
    unittest.main()
