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
            "EPISODE": 608, "FILM": 14, "LITERATURE": 1,
            "SHORT_FORM": 15, "AUDIO": 1,
        })
        self.assertEqual(len({r["row_id"] for r in catalog["rows"]}), 639)
        self.assertTrue(all(r["identity_scope"] == "SOURCE_LOCAL" and
                            r["verification_status"] == "UNVERIFIED_METADATA" and
                            r["admission_effect"] == r["coverage_effect"] == "NONE"
                            for r in catalog["rows"]))
        self.assertEqual(len(catalog["source_digests"]), 72)
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
            "PUBLISHER_EPISODE_SLOT": 385,
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
        for season in (2, 3):
            legacy = [r for r in rows if r["row_id"].startswith(f"legacy:s{season}:")]
            self.assertEqual(len(legacy), 126)
            self.assertTrue(all(f" S{season}E" in r["context"] for r in legacy))
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
