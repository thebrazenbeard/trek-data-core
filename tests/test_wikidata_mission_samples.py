"""Guard the candidate-only and provenance boundaries of archived WDQS samples."""

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "proposals" / "discovery" / "wikidata-mission-samples-20261102"
MISSIONS = (
    ("classic", "tos", "tos-qids", "Q1077"),
    ("classic", "tas", "tas-qids", "Q20922"),
    ("classic", "ds9", "ds9-qids", "Q108774"),
    ("modern", "voy", "voy", "Q156329"),
    ("modern", "dis", "dis", "Q21296543"),
    ("modern", "pic", "pic", "Q62573305"),
    ("nextgen", "ld", "ld", "Q62573569"),
    ("nextgen", "pro", "pro", "Q65250765"),
    ("nextgen", "snw", "snw", "Q94527193"),
)


class ArchivedMissionSampleTests(unittest.TestCase):
    def test_all_samples_have_query_receipt_and_no_accepted_effects(self):
        seen_qids = set()
        for group, key, proposal_stem, series_qid in MISSIONS:
            with self.subTest(mission=series_qid):
                folder = SAMPLES / group
                query_bytes = (folder / "queries" / f"{key}.rq").read_bytes()
                receipt = json.loads((folder / "receipts" / f"{key}.json").read_text())
                proposal = json.loads((folder / "proposals" / f"{proposal_stem}.json").read_text())

                self.assertEqual(query_bytes, receipt["query_text"].encode("utf-8"))
                self.assertEqual(
                    hashlib.sha256(query_bytes).hexdigest(),
                    proposal["provenance"]["query_sha256"],
                )
                self.assertRegex(proposal["provenance"]["response_sha256"], r"^[0-9a-f]{64}$")
                self.assertEqual(receipt["snapshot_id"], proposal["provenance"]["snapshot_id"])
                self.assertEqual(receipt["retrieved_at_epoch"], proposal["provenance"]["retrieved_at_epoch"])
                self.assertEqual(receipt["source_url"], proposal["provenance"]["source_url"])
                self.assertEqual(receipt["license"], "CC0-1.0")
                self.assertTrue(proposal["proposal_only"])
                self.assertEqual(proposal["accepted_work_effect"], "NONE")
                self.assertEqual(proposal["accepted_source_binding_effect"], "NONE")
                self.assertEqual(proposal["coverage_effect"], "NONE")
                self.assertEqual(len(proposal["candidates"]), 20)

                for row in proposal["candidates"]:
                    self.assertEqual(row["series_qid"], series_qid)
                    self.assertEqual(row["status"], "CANDIDATE")
                    self.assertIsNone(row["canonical_work_id"])
                    self.assertEqual(row["evidence_status"], "EXTERNAL_DISCOVERY_METADATA_ONLY")
                    self.assertRegex(row["episode_qid"], r"^Q[1-9][0-9]*$")
                    self.assertNotIn(row["episode_qid"], seen_qids)
                    seen_qids.add(row["episode_qid"])
        self.assertEqual(len(seen_qids), 180)

    def test_failed_or_empty_queries_are_not_fabricated_into_candidates(self):
        self.assertTrue((SAMPLES / "modern" / "queries" / "ent.rq").is_file())
        self.assertFalse((SAMPLES / "modern" / "receipts" / "ent.json").exists())
        self.assertFalse((SAMPLES / "modern" / "proposals" / "ent.json").exists())
        sfa_query = (SAMPLES / "nextgen" / "queries" / "sfa.rq").read_bytes()
        sfa_receipt = json.loads((SAMPLES / "nextgen" / "receipts" / "sfa.json").read_text())
        self.assertEqual(sfa_query, sfa_receipt["query_text"].encode("utf-8"))
        self.assertFalse((SAMPLES / "nextgen" / "proposals" / "sfa.json").exists())

    def test_public_repository_contains_no_raw_source_responses(self):
        for group in ("classic", "modern", "nextgen"):
            self.assertFalse((SAMPLES / group / "responses").exists())


if __name__ == "__main__":
    unittest.main()
