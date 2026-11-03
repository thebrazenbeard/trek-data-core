"""Adversarial, deterministic checks for discovery-only verification triage."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_discovery_verification_ledger as ledger  # noqa: E402


class DiscoveryVerificationLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.catalog_raw = ledger._read_json(ledger.CATALOG)
        cls.observations, _ = ledger._read_json(ledger.RECHECKS)
        cls.episode_observations, _ = ledger._read_json(ledger.EPISODE_RECHECKS)
        cls.built = ledger.build(cls.catalog, cls.catalog_raw, cls.observations, cls.episode_observations)

    def test_complete_one_to_one_directory_coverage_without_work_admission(self):
        self.assertEqual(self.built["summary"]["source_local_rows"], 1214)
        self.assertEqual(self.built["summary"]["rendered_primary_metadata_rechecks"], 8)
        self.assertEqual(self.built["summary"]["rendered_publisher_metadata_rechecks"], 5)
        self.assertEqual(self.built["summary"]["rendered_episode_title_slot_rechecks"], 3)
        self.assertEqual(self.built["summary"]["not_rechecked"], 1206)
        self.assertEqual(self.built["summary"]["raw_source_bodies_newly_pinned"], 0)
        self.assertEqual(self.built["summary"]["governed_works_or_evidence_admitted"], 0)
        self.assertEqual(self.built["admission_effect"], "NONE")
        self.assertEqual(self.built["coverage_effect"], "NONE")
        self.assertEqual(self.built["denominator_status"], "NOT_ESTABLISHED")
        self.assertEqual([r["row_id"] for r in self.built["rows"]],
                         [r["row_id"] for r in self.catalog["rows"]])
        for source, check in zip(self.catalog["rows"], self.built["rows"]):
            self.assertEqual(check["source_locator"], source["source_locator"])
            self.assertEqual(check["row_payload_sha256"], ledger._row_hash(source))
            self.assertEqual(check["provenance_family"], ledger.FAMILIES[source["source_group"]])
            self.assertEqual(check["source_local_discovery_state"], "CATALOGUED_METADATA_ONLY")
            self.assertEqual(check["governed_research_coverage_state"], "NOT_ADMITTED")
            self.assertEqual(check["snapshot"]["raw_body_sha256"], None)
            self.assertEqual(check["admission_effect"], "NONE")
            self.assertEqual(check["coverage_effect"], "NONE")
            self.assertEqual(check["secondary_memory_alpha_crosswalk"], "NOT_ASSESSED")
            self.assertTrue(check["synopsis"]["does_not_assert_close_read"])

    def test_duplicate_signatures_are_flagged_without_merging_rows_or_source_families(self):
        self.assertEqual(self.built["summary"]["duplicate_signature_groups"], 25)
        self.assertEqual(self.built["summary"]["rows_in_duplicate_signature_groups"], 50)
        flagged = [r for r in self.built["rows"] if r["duplicate_source_local_row_ids"]]
        self.assertEqual(len(flagged), 50)
        for row in flagged:
            self.assertEqual(len(row["duplicate_source_local_row_ids"]), 2)
            self.assertIn(row["row_id"], row["duplicate_source_local_row_ids"])
            self.assertEqual(row["duplicate_source_local_row_ids"], sorted(row["duplicate_source_local_row_ids"]))
        paramount_sources = {"publisher:paramount", "publisher:startrek.com", "publisher:paramountplus.com"}
        self.assertEqual({ledger.FAMILIES[k] for k in paramount_sources},
                         {"paramount_corporate_publisher_family"})

    def test_observations_cannot_mutate_source_identity_or_pretend_to_pin_source(self):
        invalid_updates = (
            ("observed_title", "Invented publisher title"),
            ("observed_creator", "Invented byline"),
            ("observed_isbn", "9781111111111"),
            ("source_locator", "https://www.penguinrandomhouse.com/books/999999/example/"),
            ("observed_at_utc_date", "NOT_KNOWN"),
            ("representation", "FULL_TEXT_AVAILABLE"),
            ("raw_body_sha256", "a" * 64),
            ("evidence_locator", "HTTP 200; no product fields checked"),
            ("observed_publisher", "Paramount"),
        )
        for key, value in invalid_updates:
            with self.subTest(key=key):
                dirty = copy.deepcopy(self.observations)
                dirty["observations"][0][key] = value
                with self.assertRaises(ValueError):
                    ledger.build(self.catalog, self.catalog_raw, dirty, self.episode_observations)

    def test_nonliterary_or_duplicate_observation_rejected(self):
        dirty = copy.deepcopy(self.observations)
        dirty["observations"][0]["row_id"] = self.catalog["rows"][0]["row_id"]
        with self.assertRaises(ValueError):
            ledger.build(self.catalog, self.catalog_raw, dirty, self.episode_observations)
        dirty = copy.deepcopy(self.observations)
        dirty["observations"][1] = copy.deepcopy(dirty["observations"][0])
        with self.assertRaises(ValueError):
            ledger.build(self.catalog, self.catalog_raw, dirty, self.episode_observations)

    def test_episode_tranche_checks_primary_title_but_not_unsourced_slots(self):
        for row in self.built["rows"][:3]:
            self.assertEqual(row["metadata_check_state"], "RENDERED_OFFICIAL_EPISODE_TITLE_SLOT_RECHECKED_UNPINNED")
            self.assertEqual(row["source_group"], "wikidata:wdqs")
            self.assertEqual(row["provenance_family"], "wikidata_collaborative_derivative")
            self.assertEqual(row["verification_independence_family"], "paramount_corporate_publisher_family")
            self.assertTrue(row["verification_source_url"].startswith("https://www.paramountplus.com/shows/video/"))
            self.assertEqual(row["field_checks"]["title"], "MATCHED_RENDERED_OFFICIAL_PAGE")
            self.assertEqual(row["field_checks"]["season_episode"], "OBSERVED_OFFICIAL_PAGE_NO_SOURCE_ROW_COMPARISON")
            self.assertEqual(row["field_checks"]["source_locator"], "NOT_RECHECKED")
            self.assertEqual(row["synopsis"]["status"], "BLURB_GROUNDED_ORIGINAL_PARAPHRASE_DRAFT")
            self.assertEqual(row["synopsis"]["human_review"], "PENDING")
            self.assertEqual(row["synopsis"]["grounding_url"], row["verification_source_url"])
        self.assertEqual(sum(bool(r["synopsis"]["original_text"]) for r in self.built["rows"]), 3)

    def test_episode_observation_mutation_rejected(self):
        invalid_updates = (
            ("observed_title", "Invented title"),
            ("observed_series", "Wrong series"),
            ("observed_season", 0),
            ("observed_episode", "6"),
            ("observed_air_date", "NOT_OBSERVED"),
            ("official_episode_url", "https://www.paramountplus.com/shows/video/1226106142/?tracking=1"),
            ("official_episode_url", "https://example.com/shows/video/1226106142/"),
            ("raw_body_sha256", "0" * 64),
            ("original_synopsis", "Invented"),
            ("evidence_locator", "Any unstructured substring matched"),
        )
        for key, value in invalid_updates:
            with self.subTest(key=key, value=value):
                dirty = copy.deepcopy(self.episode_observations)
                dirty["observations"][0][key] = value
                with self.assertRaises(ValueError):
                    ledger.build(self.catalog, self.catalog_raw, self.observations, dirty)

    def test_source_catalog_promotions_and_duplicate_ids_rejected(self):
        for key, value in (("verification_status", "SOURCE_BOUND"),
                           ("admission_effect", "ONE_WORK"), ("coverage_effect", "CLOSE_READ")):
            with self.subTest(key=key):
                dirty = copy.deepcopy(self.catalog)
                dirty["rows"][0][key] = value
                with self.assertRaises(ValueError):
                    ledger.build(dirty, self.catalog_raw, self.observations, self.episode_observations)
        dirty = copy.deepcopy(self.catalog)
        dirty["rows"][1]["row_id"] = dirty["rows"][0]["row_id"]
        with self.assertRaises(ValueError):
            ledger.build(dirty, self.catalog_raw, self.observations, self.episode_observations)

    def test_committed_derivative_deterministic_in_normal_and_optimized_runtime(self):
        for options in (("--check",), ("-O", "--check")):
            with self.subTest(options=options):
                args = [sys.executable]
                if "-O" in options:
                    args.append("-O")
                args.extend([str(ROOT / "tools" / "build_discovery_verification_ledger.py"), "--check"])
                result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                self.assertIn("1214 source-local rows", result.stdout)
        encoded = (json.dumps(self.built, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        self.assertEqual(encoded, (ROOT / ledger.OUTPUT).read_bytes())

    def test_queued_first_primary_episode_batch_does_not_claim_completion(self):
        work = ledger.next_batch(self.built, self.catalog, 16)
        self.assertEqual(work["pending_total"], 1206)
        self.assertEqual(work["processed"], 0)
        self.assertEqual(work["admission_effect"], "NONE")
        self.assertEqual(len(work["rows"]), 16)
        self.assertEqual([r["row_id"] for r in work["rows"][:3]],
                         ["lead:0003", "lead:0004", "lead:0005"])
        self.assertTrue(all(r["result"] == "PENDING" for r in work["rows"]))
        self.assertTrue(all("ACTUALLY_READ_OFFICIAL_EPISODE" in r["verification_requirement"]
                            for r in work["rows"]))
        with self.assertRaises(ValueError):
            ledger.next_batch(self.built, self.catalog, 51)
        cli = subprocess.run([sys.executable, str(ROOT / "tools" / "build_discovery_verification_ledger.py"),
                              "--queue-next", "2"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(cli.returncode, 0, cli.stderr)
        self.assertEqual(len(json.loads(cli.stdout)["rows"]), 2)


if __name__ == "__main__":
    unittest.main()
