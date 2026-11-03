"""Source-only checks for the proposed, non-admitted Explorer directory."""

import copy
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
            "EPISODE": 1155, "FILM": 14, "LITERATURE": 4,
            "SHORT_FORM": 35, "AUDIO": 1,
        })
        self.assertEqual(len({r["row_id"] for r in catalog["rows"]}), 1209)
        self.assertTrue(all(r["identity_scope"] == "SOURCE_LOCAL" and
                            r["verification_status"] == "UNVERIFIED_METADATA" and
                            r["admission_effect"] == r["coverage_effect"] == "NONE"
                            for r in catalog["rows"]))
        self.assertEqual(len(catalog["source_digests"]), 138)
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
            "PUBLISHER_EPISODE_SLOT": 932,
            "PUBLISHER_REFERENCE": 15,
            "FEATURE_FILM": 13,
            "STREAMING_FILM": 1,
            "NOVEL": 4,
            "SCRIPTED_SHORT": 30,
            "PROMOTIONAL_ANIMATION": 5,
            "SCRIPTED_AUDIO_SERIES": 1,
        })
        # These are separate source-local attestations, not a deduplicated Work count.
        self.assertEqual(len({r["source_group"] for r in rows}) < len(rows), True)
        novel = next(r for r in rows if r["row_id"] == "literature:proposed-lit-snw-ring-of-fire")
        self.assertEqual(len(novel["details"]), 4)
        self.assertEqual(len({part.split("ISBN ", 1)[1] for part in novel["details"]}), 4)
        new_novels = [r for r in rows if r["source_input"].endswith("simon-schuster-three-novels-20261103/records.json")]
        self.assertEqual({r["row_id"] for r in new_novels}, {
            "literature:proposed-lit-picard-second-self",
            "literature:proposed-lit-snw-high-country",
            "literature:proposed-lit-discovery-enterprise-war",
        })
        self.assertTrue(all(r["candidate_kind"] == "NOVEL" and len(r["details"]) == 3 and
                            r["coverage_effect"] == r["admission_effect"] == "NONE"
                            for r in new_novels))
        self.assertEqual(len({detail.split("ISBN ", 1)[1]
                              for novel in new_novels for detail in novel["details"]}), 9)
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
        season6 = [r for r in rows if r["row_id"].startswith("publisher:s6:")]
        self.assertEqual(len(season6), 78)
        for mission in ("tng", "ds9", "voy"):
            observed = [r for r in season6 if r["row_id"].startswith(f"publisher:s6:{mission}:")]
            self.assertEqual(len(observed), 26)
            self.assertEqual({r["context"] for r in observed},
                             {f"{mission.upper()} S6E{episode}" for episode in range(1, 27)})
            self.assertTrue(all(r["source_group"] == "publisher:paramount" for r in observed))
        self.assertFalse(any(r["row_id"].startswith("publisher:s6:ent:") for r in season6))
        season7 = [r for r in rows if r["row_id"].startswith("publisher:s7:")]
        self.assertEqual(len(season7), 74)
        for mission, count in (("tng", 25), ("ds9", 25), ("voy", 24)):
            observed = [r for r in season7 if r["row_id"].startswith(f"publisher:s7:{mission}:")]
            self.assertEqual(len(observed), count)
            expected = (set(range(1, 26)) if mission != "voy"
                        else set(range(1, 26)) - {10})
            self.assertEqual({r["context"] for r in observed},
                             {f"{mission.upper()} S7E{episode}" for episode in expected})
            self.assertTrue(all(r["source_group"] == "publisher:paramount" for r in observed))
        self.assertFalse(any(r["context"] == "VOY S7E10" for r in season7))
        self.assertFalse(any(r["row_id"].startswith("publisher:s7:ent:") for r in season7))
        tas = [r for r in rows if r["row_id"].startswith("publisher:tas:")]
        self.assertEqual(len(tas), 22)
        self.assertEqual(len([r for r in tas if r["context"].startswith("TAS S1E")]), 16)
        self.assertEqual(len([r for r in tas if r["context"].startswith("TAS S2E")]), 6)
        self.assertEqual({r["context"] for r in tas if r["context"].startswith("TAS S1E")}.intersection(
            {r["context"] for r in rows if r["row_id"].startswith("roster:tas:")}),
            {f"TAS S1E{i}" for i in range(1, 6)})
        studio = [r for r in rows if r["row_id"].startswith("studio:mikros-s1a:")]
        self.assertEqual(len(studio), 10)
        self.assertTrue(all("(inferred)" in r["context"] and r["admission_effect"] == "NONE"
                            for r in studio))
        self.assertFalse(any(" S1E" in r["context"] for r in studio),
                         "inferred positions must not masquerade as publisher-numbered slots")
        self.assertEqual([r["title"] for r in studio][:3],
                         ["Lost and Found, Part I", "Lost and Found, Part II", "Starstruck"])
        starstruck = next(r for r in studio if r["title"] == "Starstruck")
        self.assertTrue(any("Ep#103 (same source)" in detail for detail in starstruck["details"]))
        self.assertEqual(len([r for r in rows if r["medium"] == "AUDIO"]), 1,
                         "one container, no invented audio episodes")
        scouts = [r for r in rows if r["row_id"].startswith("short:scouts:")]
        self.assertEqual(len(scouts), 20)
        self.assertEqual(len([r for r in scouts if "ASTEROID BLASTERS" in r["context"]]), 10)
        self.assertEqual(len([r for r in scouts if "HOLODECK RESCUES" in r["context"]]), 10)
        self.assertTrue(all(r["medium"] == "SHORT_FORM" and r["source_group"] == "publisher:paramount"
                            and r["source_locator"].startswith("https://youtu.be/")
                            and r["admission_effect"] == r["coverage_effect"] == "NONE"
                            for r in scouts))

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
        self.assertEqual(discovery._checked_url("https://youtu.be/j-KvjtSgfJs"),
                         "https://youtu.be/j-KvjtSgfJs")
        for forged in ("https://youtu.be/j-KvjtSgfJs/extra", "https://youtu.be/j-KvjtSgfJs?redirect=evil",
                       "https://youtu.be.evil.example/j-KvjtSgfJs", "https://youtu.be/../bad"):
            with self.subTest(forged=forged):
                with self.assertRaises(ValueError):
                    discovery._checked_url(forged)

    def test_stale_input_rejected_without_corroborating_generator(self):
        with patch.object(discovery.films, "build", return_value=b"{}"):
            with self.assertRaisesRegex(ValueError, "stale discovery source derivative"):
                discovery.build_bytes(ROOT)

    def test_three_novel_source_promotion_and_cross_edition_forgery_rejected(self):
        path = ROOT / "proposals/librarian/simon-schuster-three-novels-20261103/records.json"
        source = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(discovery._three_novel_rows(source)), 3)
        changes = (
            lambda d: d["accepted_effects"].__setitem__("works", "ACCEPTED"),
            lambda d: d["works"][1].__setitem__("status", "ACCEPTED"),
            lambda d: d["editions"][0].__setitem__("isbn13", "9781982194834"),
            lambda d: d["editions"][0].__setitem__("candidate_work_id", d["works"][1]["candidate_work_id"]),
            lambda d: d["editions"][3].__setitem__("format", "EBOOK"),
            lambda d: d["editions"][2].__setitem__("raw_response_sha256", "0" * 64),
            lambda d: d["editions"][0].__setitem__("publisher_product_url",
                                                       d["editions"][1]["publisher_product_url"]),
            lambda d: d["works"][1].__setitem__("title", "Star Trek: Strange New Worlds: False Title"),
        )
        for mutate in changes:
            with self.subTest(mutate=mutate.__code__.co_firstlineno):
                altered = copy.deepcopy(source)
                mutate(altered)
                with self.assertRaises(ValueError):
                    discovery._three_novel_rows(altered)

    def test_accepted_picard_and_new_three_novel_metadata_share_one_source_lineage(self):
        new_source = json.loads((ROOT / discovery.INPUTS[4]).read_text(encoding="utf-8"))
        accepted_source = json.loads((ROOT / discovery.PICARD_COMPANIONS).read_text(encoding="utf-8"))
        discovery._check_picard_publisher_overlap(new_source, accepted_source)

        # This product was already proposed on accepted main. A conflicting
        # title, publisher family, or Work/ISBN pairing must fail closed.
        changes = (
            lambda d: d["sources"][2]["provider_metadata"].__setitem__("title", "Wrong novel"),
            lambda d: d.__setitem__("source_group", "publisher:unrelated.example"),
            lambda d: d["edition_candidates"][2].__setitem__("work_id", "proposed-lit-picard-the-dark-veil"),
            lambda d: d["bindings"][2].__setitem__("source_id", "proposed-picard-publisher-source-9781982154073"),
            lambda d: d.__setitem__("accepted_work_effect", "ACCEPTED"),
        )
        for mutate in changes:
            with self.subTest(mutate=mutate.__code__.co_firstlineno):
                altered = copy.deepcopy(accepted_source)
                mutate(altered)
                with self.assertRaises(ValueError):
                    discovery._check_picard_publisher_overlap(new_source, altered)

        wrong_new = copy.deepcopy(new_source)
        wrong_new["editions"][0]["publisher_extent"] = "999 pages"
        with self.assertRaises(ValueError):
            discovery._check_picard_publisher_overlap(wrong_new, accepted_source)

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
