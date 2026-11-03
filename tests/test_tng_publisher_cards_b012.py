"""Hostile gates for TNG S1E23-E26 held first-party cards and B004 overlap."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/build_tng_publisher_cards_b012.py"
SPEC = importlib.util.spec_from_file_location("tng_b012_compiler", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class TNGPublisherCardsB012Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.catalog_raw = MOD.load_json(MOD.CATALOG)
        cls.observations, _ = MOD.load_json(MOD.OBSERVATIONS)
        cls.b004, cls.b004_raw = MOD.load_json(MOD.PRIOR_B004)
        cls.b011_obs, cls.b011_obs_raw = MOD.load_json(MOD.PRIOR_B011_OBS)
        cls.b011_records, cls.b011_records_raw = MOD.load_json(MOD.PRIOR_B011_RECORDS)

    def compile(self, observations=None, catalog=None, catalog_raw=None, b004=None,
                b011_obs=None):
        return MOD.compile_records(
            self.catalog if catalog is None else catalog,
            self.catalog_raw if catalog_raw is None else catalog_raw,
            self.observations if observations is None else observations,
            self.b004 if b004 is None else b004, self.b004_raw,
            self.b011_obs if b011_obs is None else b011_obs, self.b011_obs_raw,
            self.b011_records, self.b011_records_raw,
        )

    def reject(self, mutate):
        forged = copy.deepcopy(self.observations)
        mutate(forged)
        with self.assertRaises(ValueError):
            self.compile(observations=forged)

    def test_exact_four_with_two_prior_same_family_overlaps_no_admission(self):
        result = self.compile()
        self.assertEqual(result["source_local_cards_enriched"], 4)
        self.assertEqual(result["new_title_slot_rechecks"], 2)
        self.assertEqual(result["same_publisher_prior_title_slot_overlaps"], 2)
        self.assertEqual(result["independent_corroborations"], 0)
        self.assertEqual(result["governed_research_admissions"], 0)
        self.assertEqual(result["public_synopses_or_images_published"], 0)
        self.assertEqual(result["admission_effect"], "NONE")
        self.assertEqual(result["coverage_effect"], "NONE")
        self.assertEqual([r["source_local_row_id"] for r in result["rows"]],
                         [f"legacy:s1:tng:{i:03d}" for i in range(21, 25)])
        self.assertEqual([r["publisher_card"]["episode"] for r in result["rows"]],
                         [23, 24, 25, 26])
        self.assertEqual([r["prior_same_family_title_slot_recheck_id"] for r in result["rows"]],
                         ["lead:0043", None, None, "lead:0040"])

    def test_forged_source_work_coverage_publication_or_private_claims_refused(self):
        cases = (
            ("proposal_id", "rewritten"),
            ("baseline_accepted_main", "0" * 40),
            ("source_family", "independent_primary"),
            ("guide_url", "https://malicious.example/season-1"),
            ("read_surface", "FULL_EPISODE_VIEWED"),
            ("raw_html_bytes_archived", True),
            ("audiovisual_episodes_watched", True),
            ("public_synopsis_authorized", True),
            ("artwork_copy_or_publication_authorized", True),
            ("admission_effect", "ACCEPTED"),
            ("coverage_effect", "CLOSE_READ"),
            ("accepted_b004_observations_sha256", "0" * 64),
            ("accepted_b011_observations_sha256", "0" * 64),
            ("accepted_b011_records_sha256", "0" * 64),
        )
        for key, value in cases:
            with self.subTest(key=key):
                self.reject(lambda o, k=key, v=value: o.__setitem__(k, v))
        self.reject(lambda o: o.__setitem__("verified_video_path", "D:/PRIVATE/episode.mkv"))
        self.reject(lambda o: o["rows"][0].update({"viewed_video": True}))

    def test_title_slot_description_synopsis_mentions_and_identity_are_exact(self):
        self.reject(lambda o: o["rows"][0].update(row_id="legacy:s1:tng:020"))
        self.reject(lambda o: o["rows"][1].update(episode=25))
        self.reject(lambda o: o["rows"][2].update(publisher_title="Investigations"))
        self.reject(lambda o: o["rows"][3].update(publisher_description_sha256="0" * 64))
        self.reject(lambda o: o["rows"][0].update(original_synopsis_draft=(
            "Tasha Yar is killed by the alien Armus during an Enterprise rescue mission.")))
        self.reject(lambda o: o["rows"][1].update(entity_mentions_source_relative=[
            "Jean-Luc Picard", "Enterprise"]))
        self.reject(lambda o: o["rows"][3].update(entity_mentions_source_relative=[
            "Romulans", "Ralph Offenhouse"]))
        self.reject(lambda o: o["rows"][2].update(identity_hold="GLOBAL_SAME_AS"))

    def test_same_host_wrong_card_artwork_swaps_rejected(self):
        self.reject(lambda o: o["rows"][0].update(
            publisher_thumbnail_url=o["rows"][1]["publisher_thumbnail_url"]))
        self.reject(lambda o: o["rows"][3].update(
            publisher_thumbnail_url=o["rows"][2]["publisher_thumbnail_url"]))
        self.reject(lambda o: o["rows"][2].update(
            publisher_thumbnail_url="https://thumbnails.cbsig.net/_x/w400/other.jpg"))

    def test_accepted_b004_overlap_must_be_explicit_and_stable(self):
        self.reject(lambda o: o["rows"][0].update(
            prior_same_family_title_slot_recheck_id=None))
        self.reject(lambda o: o["rows"][3].update(
            prior_same_family_title_slot_recheck_id="lead:0043"))
        self.reject(lambda o: o["rows"][1].update(
            prior_same_family_title_slot_recheck_id="lead:0043"))
        changed = copy.deepcopy(self.b004)
        for row in changed["rows"]:
            if row["row_id"] == "lead:0043":
                row["cards"][0]["official_title"] = "Conspiracy"
        with self.assertRaises(ValueError):
            self.compile(b004=changed)

    def test_duplicate_and_reused_local_ids_rejected(self):
        self.reject(lambda o: o["rows"].append(copy.deepcopy(o["rows"][0])))
        self.reject(lambda o: o["rows"][1].update(row_id="legacy:s1:tng:021"))
        changed = copy.deepcopy(self.b011_obs)
        changed["rows"][0]["row_id"] = "legacy:s1:tng:021"
        with self.assertRaises(ValueError):
            self.compile(b011_obs=changed)

    def test_raw_json_duplicate_keys_rejected_by_actual_file_reader(self):
        raw = (ROOT / MOD.OBSERVATIONS).read_text(encoding="utf-8")
        attacks = (
            ('"coverage_effect": "NONE"', '"coverage_effect": "CLOSE_READ", "coverage_effect": "NONE"'),
            ('"raw_html_bytes_archived": false', '"raw_html_bytes_archived": true, "raw_html_bytes_archived": false'),
            ('"identity_hold": "NO_GLOBAL_WORK_IDENTITY_ASSERTED"',
             '"identity_hold": "GLOBAL_SAME_AS", "identity_hold": "NO_GLOBAL_WORK_IDENTITY_ASSERTED"'),
        )
        for needle, forged in attacks:
            self.assertIn(needle, raw)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "attacker.json"
                path.write_text(raw.replace(needle, forged, 1), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                    MOD.load_json(path)
                for optimized in (False, True):
                    with self.subTest(needle=needle, optimized=optimized):
                        probe = subprocess.run(
                            [sys.executable, *(["-O"] if optimized else []), "-c",
                             "import importlib.util,sys; s=importlib.util.spec_from_file_location('v',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.load_json(sys.argv[2])",
                             str(SCRIPT), str(path)],
                            capture_output=True, text=True, check=False,
                        )
                        self.assertNotEqual(probe.returncode, 0)
                        self.assertIn("duplicate JSON key", probe.stderr)

    def test_source_catalog_hash_and_id_enforced(self):
        bad = copy.deepcopy(self.catalog)
        for row in bad["rows"]:
            if row["row_id"] == "legacy:s1:tng:023":
                row["context"] = "TOS S1E25"
                break
        with self.assertRaises(ValueError):
            self.compile(catalog=bad)
        with self.assertRaises(ValueError):
            self.compile(catalog_raw=b"{}")

    def test_generated_records_byte_stable(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--check"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
