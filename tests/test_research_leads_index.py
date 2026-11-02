"""Candidate-only research index contract and hostile input tests."""

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import build_research_leads as leads


class ResearchLeadsIndexTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        (self.root / "registry").mkdir()
        (self.root / "explorer").mkdir()
        catalog = {"catalog_version": "1.0.0", "authority": "https://www.startrek.com/series-and-movies", "admission_status": "DISPLAY_CATALOG_ONLY", "missions": [
            {"id": m, "title": m.upper(), "focus": "Sample"}
            for m in leads.MISSION_ORDER
        ]}
        (self.root / "registry" / "mission_catalog.json").write_text(
            json.dumps(catalog), encoding="utf-8"
        )
        self.files = []
        for group, query_name, proposal_name, series_qid, mission_id, n in (
            *leads.SOURCE_BATCHES,
            ("enterprise-second-pass", "ent", "ent", "Q380519", "ent", 20),
        ):
            if group == "tng":
                folder = self.root / "proposals/discovery/wikidata-tng-q16290-20261102"
            elif group == "enterprise-second-pass":
                folder = self.root / leads.ENT_FOLDER
            else:
                folder = self.root / f"proposals/discovery/wikidata-mission-samples-20261102/{group}"
            (folder / "queries").mkdir(parents=True, exist_ok=True)
            (folder / "receipts").mkdir(parents=True, exist_ok=True)
            (folder / "proposals").mkdir(parents=True, exist_ok=True)
            qpath = folder / "queries" / f"{query_name}.rq"
            if group == "tng":
                qpath = folder / "query.rq"
                rpath = folder / "receipt.json"
                ppath = folder / "candidates.json"
            else:
                rpath = folder / "receipts" / f"{query_name}.json"
                ppath = folder / "proposals" / f"{proposal_name}.json"
            query = f"SELECT ?episode WHERE {{ wd:{series_qid} ?p ?episode }} LIMIT {n}\n"
            qpath.write_text(query, encoding="utf-8")
            stamp = ("WDQS-ENT-Q380519-SIMPLE-P179-20261102-LIMIT20-001"
                     if group == "enterprise-second-pass" else f"WDQS-{mission_id.upper()}-20261102")
            receipt = {
                "source_url": leads.EXPECTED_SOURCE_URL,
                "license": "CC0-1.0",
                "license_url": leads.EXPECTED_LICENSE_URL,
                "retrieved_at_epoch": 1793600000,
                "snapshot_id": stamp,
                "query_text": query,
            }
            rpath.write_text(json.dumps(receipt), encoding="utf-8")
            i = leads.MISSION_ORDER.index(mission_id)
            candidates = [
                {
                    "canonical_work_id": None,
                    "episode_label": f"Sample {mission_id.upper()} {j}",
                    "episode_number": None,
                    "episode_qid": f"Q{100000 + i * 100 + j}",
                    "evidence_status": "EXTERNAL_DISCOVERY_METADATA_ONLY",
                    "record_type": "episode_discovery_candidate",
                    "season_number": None,
                    "series_label": None,
                    "series_qid": series_qid,
                    "status": "CANDIDATE",
                }
                for j in range(1, n + 1)
            ]
            if group == "enterprise-second-pass":
                candidates[0].update(episode_qid="Q56247746", episode_label="Temporal Cold War arc")
                candidates[1].update(episode_qid="Q866375", episode_label="In a Mirror, Darkly")
            proposal = {
                "accepted_source_binding_effect": "NONE",
                "accepted_work_effect": "NONE",
                "candidates": candidates,
                "coverage_effect": "NONE",
                "proposal_only": True,
                "proposal_type": "WIKIDATA_EPISODE_DISCOVERY_V1",
                "provenance": {
                    "license": "CC0-1.0",
                    "license_url": leads.EXPECTED_LICENSE_URL,
                    "provenance_verification": "USER_SUPPLIED_OFFLINE_EXPORT_NOT_REMOTE_VERIFIED",
                    "query_sha256": hashlib.sha256(query.encode()).hexdigest(),
                    "response_sha256": "a" * 64,
                    "retrieved_at_epoch": 1793600000,
                    "snapshot_id": stamp,
                    "source_url": leads.EXPECTED_SOURCE_URL,
                },
            }
            ppath.write_text(json.dumps(proposal), encoding="utf-8")
            self.files.append((qpath, rpath, ppath))
        repo = Path(__file__).resolve().parents[1]
        holds = self.root / leads.ENT_HOLDS_PATH
        shutil.copyfile(repo / leads.ENT_HOLDS_PATH, holds)
        roster = self.root / leads.SFA_ROSTER_PATH
        roster.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(repo / leads.SFA_ROSTER_PATH, roster)
        self.holds = holds
        self.roster = roster

    def mutate(self, index, fn):
        ppath = self.files[index][2]
        proposal = json.loads(ppath.read_text(encoding="utf-8"))
        fn(proposal)
        ppath.write_text(json.dumps(proposal), encoding="utf-8")

    def test_218_leads_two_holds_twelve_missions_without_touching_canon(self):
        canon = self.root / "explorer/index.json"
        canon.write_bytes(b'{"do_not_change":true}\n')
        first = leads.build_bytes(self.root)
        self.assertEqual(first, leads.build_bytes(self.root))
        doc = json.loads(first)
        self.assertEqual(doc["data_status"], "CANDIDATE_DISCOVERY_ONLY")
        self.assertEqual(doc["coverage_effect"], "NONE")
        self.assertEqual(doc["schema_version"], "2.0.0")
        self.assertEqual(doc["lead_count"], 218)
        self.assertEqual(doc["sampled_missions_count"], 12)
        self.assertEqual(doc["held_candidate_count"], 2)
        self.assertEqual(len(doc["leads"]), 218)
        self.assertEqual(set(doc), {
            "schema_version", "data_status", "source_policy", "coverage_effect",
            "lead_count", "sampled_missions_count", "held_candidate_count", "leads",
        })
        self.assertEqual(set(doc["leads"][0]), {
            "mission_id", "episode_qid", "episode_label", "snapshot_id",
            "query_sha256", "response_sha256", "verification_status",
            "source_type", "independence_group",
        })
        self.assertFalse(any("canonical_work_id" in r for r in doc["leads"]))
        self.assertEqual({r["verification_status"] for r in doc["leads"]}, {"UNVERIFIED_METADATA"})
        self.assertEqual(sum(r["mission_id"] == "ent" for r in doc["leads"]), 18)
        self.assertEqual(sum(r["mission_id"] == "sfa" for r in doc["leads"]), 10)
        self.assertFalse(any(r.get("episode_qid") in leads.ENT_REVIEW_HOLDS for r in doc["leads"]))
        self.assertEqual({r["source_type"] for r in doc["leads"]},
                         {"WIKIDATA_METADATA", "PUBLISHER_EPISODE_SLOT_METADATA"})
        self.assertTrue(all(r["independence_group"] == "publisher:paramount" and
                            "episode_qid" not in r and "response_sha256" not in r
                            for r in doc["leads"] if r["mission_id"] == "sfa"))
        out = leads.write_or_check(self.root, check=False)
        self.assertEqual(out.read_bytes(), first)
        leads.write_or_check(self.root, check=True)
        self.assertEqual(canon.read_bytes(), b'{"do_not_change":true}\n')
        out.write_bytes(b"tampered\n")
        with self.assertRaisesRegex(ValueError, "out of date"):
            leads.write_or_check(self.root, check=True)

    def test_rejects_mismatched_query_digest(self):
        self.mutate(0, lambda p: p["provenance"].update(query_sha256="b" * 64))
        with self.assertRaisesRegex(ValueError, "query SHA-256"):
            leads.build_bytes(self.root)

    def test_qids_sort_numerically_within_mission(self):
        def reverse_lexical_order(proposal):
            proposal["candidates"][0]["episode_qid"] = "Q10"
            proposal["candidates"][1]["episode_qid"] = "Q9"

        self.mutate(0, reverse_lexical_order)
        document = json.loads(leads.build_bytes(self.root))
        tos_qids = [row["episode_qid"] for row in document["leads"] if row["mission_id"] == "tos"]
        self.assertEqual(tos_qids[:2], ["Q9", "Q10"])

    def test_rejects_admission_effect(self):
        self.mutate(0, lambda p: p.update(coverage_effect="INCREMENT"))
        with self.assertRaisesRegex(ValueError, "coverage_effect"):
            leads.build_bytes(self.root)

    def test_rejects_accepted_status(self):
        self.mutate(0, lambda p: p["candidates"][0].update(status="ACCEPTED"))
        with self.assertRaisesRegex(ValueError, "not candidate-only"):
            leads.build_bytes(self.root)

    def test_rejects_unverified_response_digest_format(self):
        self.mutate(0, lambda p: p["provenance"].update(response_sha256="not-a-digest"))
        with self.assertRaisesRegex(ValueError, "response_sha256"):
            leads.build_bytes(self.root)

    def test_rejects_false_remotely_verified_claim(self):
        self.mutate(0, lambda p: p["provenance"].update(
            provenance_verification="REMOTE_SIGNED_AND_VERIFIED"
        ))
        with self.assertRaisesRegex(ValueError, "unsupported source/provenance"):
            leads.build_bytes(self.root)

    def test_rejects_canonical_work_id(self):
        self.mutate(0, lambda p: p["candidates"][0].update(canonical_work_id="TNG-001"))
        with self.assertRaisesRegex(ValueError, "canonical_work_id"):
            leads.build_bytes(self.root)

    def test_rejects_duplicate_episode_qid_across_series(self):
        duplicate_qid = json.loads(self.files[0][2].read_text())["candidates"][0]["episode_qid"]
        self.mutate(1, lambda p: p["candidates"][0].update(episode_qid=duplicate_qid))
        with self.assertRaisesRegex(ValueError, "duplicate episode QID"):
            leads.build_bytes(self.root)

    def test_rejects_wrong_series_item(self):
        self.mutate(0, lambda p: p["candidates"][0].update(series_qid="Q999"))
        with self.assertRaisesRegex(ValueError, "series QID"):
            leads.build_bytes(self.root)

    def test_rejects_markup_in_title(self):
        self.mutate(0, lambda p: p["candidates"][0].update(episode_label="<script>alert(1)</script>"))
        with self.assertRaisesRegex(ValueError, "episode_label"):
            leads.build_bytes(self.root)

    def test_rejects_unexpected_candidate_properties(self):
        self.mutate(0, lambda p: p["candidates"][0].update(accepted=True))
        with self.assertRaisesRegex(ValueError, "candidate fields"):
            leads.build_bytes(self.root)

    def test_rejects_duplicate_json_keys(self):
        p = self.files[0][2]
        p.write_text('{"proposal_only":true,"proposal_only":false}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            leads.build_bytes(self.root)

    def test_rejects_missing_proposal(self):
        self.files[0][2].unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            leads.build_bytes(self.root)

    def test_rejects_symlinked_governed_file(self):
        orig = self.files[0][2]
        dest = orig.with_name("hidden.json")
        orig.rename(dest)
        orig.symlink_to(dest)
        with self.assertRaisesRegex(ValueError, "symlink"):
            leads.build_bytes(self.root)

    def test_rejects_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "unsafe path"):
            leads.safe_read(self.root, Path("../elsewhere.json"))

    def test_ignores_unreviewed_historical_proposal_file(self):
        unreviewed = self.root / "proposals/discovery/unreviewed.json"
        unreviewed.write_text('{"accepted_work_effect":"ACCEPTED"}', encoding="utf-8")
        self.assertEqual(len(json.loads(leads.build_bytes(self.root))["leads"]), 218)

    def test_rejects_removed_arc_hold(self):
        holds = json.loads(self.holds.read_text(encoding="utf-8"))
        holds["exclude_from_public_episode_search_until_review"].pop()
        self.holds.write_text(json.dumps(holds), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "two explicit episode holds"):
            leads.build_bytes(self.root)

    def test_rejects_mismatched_held_label(self):
        self.mutate(-1, lambda p: p["candidates"][0].update(episode_label="Episode 1"))
        with self.assertRaisesRegex(ValueError, "source batch no longer matches"):
            leads.build_bytes(self.root)

    def test_rejects_held_arc_as_ordinary_episode(self):
        self.mutate(-1, lambda p: p["candidates"][0].update(episode_qid="Q999999"))
        with self.assertRaisesRegex(ValueError, "source batch no longer matches"):
            leads.build_bytes(self.root)

    def test_rejects_publisher_claim_of_verified_coverage(self):
        roster = json.loads(self.roster.read_text(encoding="utf-8"))
        roster["denominator_effect"] = "ACCEPTED"
        self.roster.write_text(json.dumps(roster), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "accepted state"):
            leads.build_bytes(self.root)

    def test_rejects_publisher_claim_of_independent_second_source(self):
        roster = json.loads(self.roster.read_text(encoding="utf-8"))
        roster["observation"]["independence_group"] = "publisher:independently-verified"
        self.roster.write_text(json.dumps(roster), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unexpected publisher source"):
            leads.build_bytes(self.root)

    def test_rejects_duplicate_publisher_slot(self):
        roster = json.loads(self.roster.read_text(encoding="utf-8"))
        roster["episode_slots"][1]["episode_number"] = 1
        self.roster.write_text(json.dumps(roster), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "strictly sorted"):
            leads.build_bytes(self.root)

    def test_rejects_unreviewed_publisher_season_expansion(self):
        roster = json.loads(self.roster.read_text(encoding="utf-8"))
        for row in roster["episode_slots"]:
            row["season"] = 2
        self.roster.write_text(json.dumps(roster), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Season 1 candidate slot sequence"):
            leads.build_bytes(self.root)

    def test_rejects_undocumented_publisher_observation_revision(self):
        roster = json.loads(self.roster.read_text(encoding="utf-8"))
        roster["observation"]["observed_on"] = "2026-11-01"
        self.roster.write_text(json.dumps(roster), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unexpected publisher source"):
            leads.build_bytes(self.root)

    def test_rejects_publisher_fabricated_response_digest(self):
        roster = json.loads(self.roster.read_text(encoding="utf-8"))
        roster["observation"]["response_sha256"] = "a" * 64
        self.roster.write_text(json.dumps(roster), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "response or audiovisual verification"):
            leads.build_bytes(self.root)

    def test_rejects_publisher_unicode_format_control(self):
        roster = json.loads(self.roster.read_text(encoding="utf-8"))
        roster["episode_slots"][0]["title"] = "Kids\u202eThese Days"
        self.roster.write_text(json.dumps(roster), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unsafe episode_label"):
            leads.build_bytes(self.root)

    def test_rejects_publisher_lone_surrogate(self):
        roster = json.loads(self.roster.read_text(encoding="utf-8"))
        roster["episode_slots"][0]["title"] = "Kids\ud800These Days"
        self.roster.write_text(json.dumps(roster), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unsafe episode_label"):
            leads.build_bytes(self.root)

    def test_rejects_symlinked_public_output_directory(self):
        leads_dir = self.root / "other"
        leads_dir.mkdir()
        (self.root / "explorer").rmdir()
        (self.root / "explorer").symlink_to(leads_dir, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            leads.write_or_check(self.root, check=False)


if __name__ == "__main__":
    unittest.main()
