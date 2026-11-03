"""Adversarial source-only gates for Enterprise S2 E1–E10 first-party cards."""

import copy
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/build_ent_publisher_cards_s2_b001.py"
SPEC = importlib.util.spec_from_file_location("ent_s2_b001", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class EnterprisePublisherS2B001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.catalog_raw = MOD.load_json(MOD.CATALOG)
        cls.bundle, cls.bundle_raw = MOD.load_json(MOD.BUNDLE)
        cls.s1_b001_obs, cls.s1_b001_obs_raw = MOD.load_json(MOD.ACCEPTED_S1_B001_OBS)
        cls.s1_b001_records, cls.s1_b001_records_raw = MOD.load_json(MOD.ACCEPTED_S1_B001_RECORDS)
        cls.s1_b002_obs, cls.s1_b002_obs_raw = MOD.load_json(MOD.ACCEPTED_S1_B002_OBS)
        cls.s1_b002_records, cls.s1_b002_records_raw = MOD.load_json(MOD.ACCEPTED_S1_B002_RECORDS)
        cls.observations, _ = MOD.load_json(MOD.OBS)

    def compiled(self, observations=None, catalog=None, catalog_raw=None,
                 bundle=None, bundle_raw=None, s1_b001_obs=None, s1_b001_obs_raw=None,
                 s1_b002_obs=None, s1_b002_obs_raw=None):
        return MOD.compile_records(
            self.catalog if catalog is None else catalog,
            self.catalog_raw if catalog_raw is None else catalog_raw,
            self.bundle if bundle is None else bundle,
            self.bundle_raw if bundle_raw is None else bundle_raw,
            self.s1_b001_obs if s1_b001_obs is None else s1_b001_obs,
            self.s1_b001_obs_raw if s1_b001_obs_raw is None else s1_b001_obs_raw,
            self.s1_b001_records, self.s1_b001_records_raw,
            self.s1_b002_obs if s1_b002_obs is None else s1_b002_obs,
            self.s1_b002_obs_raw if s1_b002_obs_raw is None else s1_b002_obs_raw,
            self.s1_b002_records, self.s1_b002_records_raw,
            self.observations if observations is None else observations,
        )

    def rejects(self, mutate):
        forged = copy.deepcopy(self.observations)
        mutate(forged)
        with self.assertRaises(ValueError):
            self.compiled(observations=forged)

    def test_ten_exact_source_local_cards_and_no_episode_promotions(self):
        out = self.compiled()
        self.assertEqual(len(out["rows"]), 10)
        self.assertEqual(out["source_local_cards_enriched"], 10)
        self.assertEqual(out["governed_research_admissions"], 0)
        self.assertEqual(out["independent_corroborations"], 0)
        self.assertEqual(out["public_synopses_or_images_published"], 0)
        self.assertEqual(out["admission_effect"], "NONE")
        self.assertEqual(out["coverage_effect"], "NONE")
        self.assertEqual([r["source_local_row_id"] for r in out["rows"]],
                         [f"legacy:s2:ent:{i:03d}" for i in range(10)])
        self.assertEqual([r["publisher_card"]["episode"] for r in out["rows"]],
                         list(range(1, 11)))
        self.assertEqual(out["combined_multipart_cards_preserved_as_single_source_slot"], 0)
        self.assertEqual(out["cross_season_shockwave_work_links_resolved"], 0)
        self.assertEqual(out["publisher_narrated_tales_treated_as_historical_truth"], 0)
        self.assertEqual(out["publisher_apparent_deaths_treated_as_confirmed_deaths"], 0)
        self.assertEqual(out["identity_doubts_promoted_to_identity_changes"], 0)
        self.assertEqual(out["rows"][0]["identity_resolution"],
                         "PUBLISHER_SHOCKWAVE_PART_II_S1_PART_I_LINK_UNRESOLVED_NO_GLOBAL_WORK_IDENTITY")
        self.assertEqual(out["rows"][1]["publisher_description_claim_frame"],
                         "PUBLISHER_REPORTS_CHARACTER_NARRATED_TALE_NOT_AUTHENTICATED_HISTORY")
        self.assertEqual(out["rows"][3]["publisher_description_claim_frame"],
                         "PUBLISHER_APPARENT_DEATH_NOT_AUTHENTICATED_CHARACTER_DEATH")
        self.assertEqual(out["rows"][9]["publisher_description_claim_frame"],
                         "PUBLISHER_CHARACTER_IDENTITY_DOUBT_NOT_IDENTITY_CHANGE")
        for card in out["rows"]:
            self.assertEqual(card["assertion_frame"],
                             "LITERAL_PUBLISHER_DESCRIPTION_TEXT_ONLY_NOT_UTTERANCE_OR_DEPICTION")
            self.assertEqual(card["governed_coverage_state"], "NOT_ADMITTED")

    def test_no_forged_episode_custody_or_publication(self):
        for key, value in (
            ("baseline_accepted_main", "0" * 40),
            ("source_family", "independent_publisher"),
            ("guide_url", "https://example.net/episodes/1/"),
            ("read_surface", "ACTUAL_EPISODE_CLOSE_READ"),
            ("raw_html_bytes_archived", True),
            ("audiovisual_episodes_watched", True),
            ("public_synopsis_authorized", True),
            ("artwork_copy_or_publication_authorized", True),
            ("admission_effect", "SOURCE_ADMITTED"),
            ("coverage_effect", "CLOSE_READ"),
            ("accepted_ent_bundle_sha256", "0" * 64),
            ("accepted_s1_b001_observations_sha256", "0" * 64),
            ("accepted_s1_b002_observations_sha256", "0" * 64),
            ("accepted_s1_b001_records_sha256", "0" * 64),
            ("accepted_s1_b002_records_sha256", "0" * 64),
        ):
            with self.subTest(field=key):
                self.rejects(lambda o, k=key, v=value: o.__setitem__(k, v))
        self.rejects(lambda o: o["rows"][0].update({"private_video_path": "D:/media/ent.mkv"}))
        self.rejects(lambda o: o.update({"full_text_episodes": 10}))

    def test_exact_title_slot_digest_and_synopsis_binding(self):
        self.rejects(lambda o: o["rows"][0].update(episode=26))
        self.rejects(lambda o: o["rows"][1].update(episode=1))
        self.rejects(lambda o: o["rows"][5].update(publisher_title="The Marauders"))
        self.rejects(lambda o: o["rows"][7].update(publisher_description_sha256="0" * 64))
        self.rejects(lambda o: o["rows"][4].update(original_synopsis_draft=
                     "An authenticated scene read confirms the crew really witnessed the ship explode."))
        self.rejects(lambda o: o["rows"][0].update(identity_hold="SAME_AS_S1_SHOCKWAVE"))
        self.rejects(lambda o: o["rows"][3].update(mention_frame="DEPICTED_ACTIONS"))
        self.rejects(lambda o: o["rows"][1].update(source_claim_frame="PROVEN_HISTORICAL_FIRST_CONTACT"))
        self.rejects(lambda o: o["rows"][3].update(source_claim_frame="CHARACTER_DEAD"))
        self.rejects(lambda o: o["rows"][9].update(source_claim_frame="DUPLICATED_PERSON"))
        self.rejects(lambda o: o["rows"][6].update(entity_mentions_source_relative=
                     ["T'Pol", "Archer", "Mayweather"]))

    def test_same_host_episode_artwork_swaps_rejected(self):
        self.rejects(lambda o: o["rows"][0].update(
            publisher_thumbnail_url=o["rows"][1]["publisher_thumbnail_url"]))
        self.rejects(lambda o: o["rows"][7].update(
            publisher_thumbnail_url=o["rows"][8]["publisher_thumbnail_url"]))
        self.rejects(lambda o: o["rows"][3].update(
            publisher_thumbnail_url="https://thumbnails.cbsig.net/_x/w400/other.jpg"))

    def test_duplicate_and_source_drift_rejected(self):
        self.rejects(lambda o: o["rows"].append(copy.deepcopy(o["rows"][0])))
        self.rejects(lambda o: o["rows"][5].update(row_id="legacy:s2:ent:004"))
        self.rejects(lambda o: o["rows"][3].update(row_id="legacy:s1:ent:003"))
        bad = copy.deepcopy(self.catalog)
        for row in bad["rows"]:
            if row["row_id"] == "legacy:s2:ent:007":
                row["context"] = "ENT S1E8"
                break
        with self.assertRaises(ValueError):
            self.compiled(catalog=bad)
        with self.assertRaises(ValueError):
            self.compiled(catalog_raw=b"{}")
        with self.assertRaises(ValueError):
            self.compiled(bundle_raw=b"{}")
        with self.assertRaises(ValueError):
            self.compiled(s1_b001_obs_raw=b"{}")
        with self.assertRaises(ValueError):
            self.compiled(s1_b002_obs_raw=b"{}")
        changed = copy.deepcopy(self.s1_b002_obs)
        changed["rows"][0]["row_id"] = "legacy:s2:ent:000"
        with self.assertRaises(ValueError):
            self.compiled(s1_b002_obs=changed)

    def test_raw_duplicate_json_keys_fail_in_normal_and_optimized_python(self):
        raw = (ROOT / MOD.OBS).read_text(encoding="utf-8")
        for needle, substitute in (
            ('"coverage_effect": "NONE"', '"coverage_effect": "CLOSE_READ", "coverage_effect": "NONE"'),
            ('"raw_html_bytes_archived": false', '"raw_html_bytes_archived": true, "raw_html_bytes_archived": false'),
            ('"identity_hold": "NO_GLOBAL_WORK_IDENTITY_ASSERTED"',
             '"identity_hold": "GLOBAL_WORK_ASSERTED", "identity_hold": "NO_GLOBAL_WORK_IDENTITY_ASSERTED"'),
        ):
            self.assertIn(needle, raw)
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "attacker.json"
                path.write_text(raw.replace(needle, substitute, 1), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                    MOD.load_json(path)
                for optimize in (False, True):
                    run = subprocess.run([
                        sys.executable, *(["-O"] if optimize else []), "-c",
                        "import importlib.util,sys;s=importlib.util.spec_from_file_location('x',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.load_json(sys.argv[2])",
                        str(SCRIPT), str(path),
                    ], capture_output=True, text=True, check=False)
                    self.assertNotEqual(run.returncode, 0)
                    self.assertIn("duplicate JSON key", run.stderr)

    def test_reproducible_generated_json(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--check"],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
