"""Adversarial source-only gates for Enterprise S1 B003 final five cards."""

import copy
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/build_ent_publisher_cards_b003.py"
SPEC = importlib.util.spec_from_file_location("ent_b003", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class EnterprisePublisherB003Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.catalog_raw = MOD.load_json(MOD.CATALOG)
        cls.bundle, cls.bundle_raw = MOD.load_json(MOD.BUNDLE)
        cls.b001_obs, cls.b001_obs_raw = MOD.load_json(MOD.ACCEPTED_B001_OBS)
        cls.b001_records, cls.b001_records_raw = MOD.load_json(MOD.ACCEPTED_B001_RECORDS)
        cls.observations, _ = MOD.load_json(MOD.OBS)

    def compiled(self, observations=None, catalog=None, catalog_raw=None,
                 bundle=None, bundle_raw=None, b001_obs=None, b001_obs_raw=None):
        return MOD.compile_records(
            self.catalog if catalog is None else catalog,
            self.catalog_raw if catalog_raw is None else catalog_raw,
            self.bundle if bundle is None else bundle,
            self.bundle_raw if bundle_raw is None else bundle_raw,
            self.b001_obs if b001_obs is None else b001_obs,
            self.b001_obs_raw if b001_obs_raw is None else b001_obs_raw,
            self.b001_records, self.b001_records_raw,
            self.observations if observations is None else observations,
        )

    def rejects(self, mutate):
        forged = copy.deepcopy(self.observations)
        mutate(forged)
        with self.assertRaises(ValueError):
            self.compiled(observations=forged)

    def test_five_exact_source_local_cards_and_no_episode_promotions(self):
        out = self.compiled()
        self.assertEqual(len(out["rows"]), 5)
        self.assertEqual(out["source_local_cards_enriched"], 5)
        self.assertEqual(out["governed_research_admissions"], 0)
        self.assertEqual(out["independent_corroborations"], 0)
        self.assertEqual(out["public_synopses_or_images_published"], 0)
        self.assertEqual(out["admission_effect"], "NONE")
        self.assertEqual(out["coverage_effect"], "NONE")
        self.assertEqual([r["source_local_row_id"] for r in out["rows"]],
                         [f"legacy:s1:ent:{i:03d}" for i in range(20, 25)])
        self.assertEqual([r["publisher_card"]["episode"] for r in out["rows"]],
                         list(range(22, 27)))
        self.assertEqual(out["combined_multipart_cards_preserved_as_single_source_slot"], 0)
        self.assertEqual(out["unresolved_publisher_title_variants"], 1)
        self.assertEqual(out["unresolved_part_i_continuation_links"], 1)
        self.assertEqual(out["rows"][0]["identity_resolution"],
                         "PUBLISHER_TITLE_VOX_SOLIS_ALTERNATE_TITLE_UNRESOLVED_NO_GLOBAL_WORK_IDENTITY")
        self.assertEqual(out["rows"][4]["identity_resolution"],
                         "PUBLISHER_PART_I_CROSS_SEASON_CONTINUATION_UNRESOLVED_NO_GLOBAL_WORK_IDENTITY")
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
            ("accepted_b001_observations_sha256", "0" * 64),
            ("accepted_b001_records_sha256", "0" * 64),
        ):
            with self.subTest(field=key):
                self.rejects(lambda o, k=key, v=value: o.__setitem__(k, v))
        self.rejects(lambda o: o["rows"][0].update({"private_video_path": "D:/media/ent.mkv"}))
        self.rejects(lambda o: o.update({"full_text_episodes": 5}))

    def test_exact_title_slot_digest_and_synopsis_binding(self):
        self.rejects(lambda o: o["rows"][0].update(episode=21))
        self.rejects(lambda o: o["rows"][1].update(episode=22))
        self.rejects(lambda o: o["rows"][0].update(publisher_title="Vox Sola"))
        self.rejects(lambda o: o["rows"][2].update(publisher_description_sha256="0" * 64))
        self.rejects(lambda o: o["rows"][4].update(original_synopsis_draft=
                     "An authenticated scene read confirms the crew really witnessed the ship explode."))
        self.rejects(lambda o: o["rows"][0].update(identity_hold="TWO_IDENTICAL_WORKS"))
        self.rejects(lambda o: o["rows"][4].update(identity_hold="ACCEPTED_S2_SAME_WORK"))
        self.rejects(lambda o: o["rows"][3].update(mention_frame="DEPICTED_ACTIONS"))
        self.rejects(lambda o: o["rows"][4].update(entity_mentions_source_relative=
                     ["Jonathan Archer", "Suliban"]))

    def test_same_host_episode_artwork_swaps_rejected(self):
        self.rejects(lambda o: o["rows"][0].update(
            publisher_thumbnail_url=o["rows"][1]["publisher_thumbnail_url"]))
        self.rejects(lambda o: o["rows"][4].update(
            publisher_thumbnail_url=o["rows"][3]["publisher_thumbnail_url"]))
        self.rejects(lambda o: o["rows"][3].update(
            publisher_thumbnail_url="https://thumbnails.cbsig.net/_x/w400/other.jpg"))

    def test_duplicate_and_source_drift_rejected(self):
        self.rejects(lambda o: o["rows"].append(copy.deepcopy(o["rows"][0])))
        self.rejects(lambda o: o["rows"][4].update(row_id="legacy:s1:ent:023"))
        self.rejects(lambda o: o["rows"][3].update(row_id="legacy:s1:ent:019"))
        bad = copy.deepcopy(self.catalog)
        for row in bad["rows"]:
            if row["row_id"] == "legacy:s1:ent:023":
                row["context"] = "ENT S1E20"
                break
        with self.assertRaises(ValueError):
            self.compiled(catalog=bad)
        with self.assertRaises(ValueError):
            self.compiled(catalog_raw=b"{}")
        with self.assertRaises(ValueError):
            self.compiled(bundle_raw=b"{}")
        with self.assertRaises(ValueError):
            self.compiled(b001_obs_raw=b"{}")
        changed = copy.deepcopy(self.b001_obs)
        changed["rows"][0]["row_id"] = "legacy:s1:ent:020"
        with self.assertRaises(ValueError):
            self.compiled(b001_obs=changed)

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
