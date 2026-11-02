"""Fail-closed invariants for the separate ENT/SFA metadata discovery.

These do not verify external source truth; they verify proposal limitations.
"""

from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "proposals/discovery/wikidata-ent-sfa-second-pass-20261102"
ENT_QIDS = {
    "Q861673", "Q861686", "Q866375", "Q1027348", "Q1185745",
    "Q2122661", "Q2133397", "Q2134825", "Q2139300", "Q2153354",
    "Q2213032", "Q2309926", "Q2313211", "Q42594945", "Q42595960",
    "Q42596046", "Q42596397", "Q44166126", "Q44166211", "Q56247746",
}


class SecondPassTests(unittest.TestCase):
    def test_ent_receipt_and_proposal_query_match_exact_bytes(self):
        receipt = json.loads((BATCH / "receipts/ent.json").read_text(encoding="utf-8"))
        proposal = json.loads((BATCH / "proposals/ent.json").read_text(encoding="utf-8"))
        query = (BATCH / "queries/ent.rq").read_bytes()
        self.assertEqual(receipt["query_text"].encode("utf-8"), query)
        self.assertEqual(proposal["provenance"]["query_sha256"], hashlib.sha256(query).hexdigest())
        self.assertEqual(proposal["provenance"]["response_sha256"],
                         "5925ba3576baf65f0406e99cd8f78ce085192fbacb53b1a6b46d277bb9580c71")
        self.assertEqual(proposal["provenance"]["snapshot_id"], receipt["snapshot_id"])

    def test_sfa_negative_result_has_no_invented_proposal(self):
        receipt = json.loads((BATCH / "receipts/sfa.json").read_text(encoding="utf-8"))
        query = (BATCH / "queries/sfa.rq").read_bytes()
        self.assertEqual(receipt["query_text"].encode("utf-8"), query)
        self.assertEqual(hashlib.sha256(query).hexdigest(),
                         "315a0153d1841f82ac9f445b6ce76c6e375e27f75d6be882fb1da94a059ab4cb")
        self.assertFalse((BATCH / "proposals/sfa.json").exists())
        self.assertIn("Q134592591", receipt["query_text"])

    def test_ent_candidates_are_only_research_leads(self):
        proposal = json.loads((BATCH / "proposals/ent.json").read_text(encoding="utf-8"))
        self.assertEqual(len(proposal["candidates"]), 20)
        self.assertTrue(proposal["proposal_only"])
        for effect in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect"):
            self.assertEqual(proposal[effect], "NONE")
        qids = set()
        for record in proposal["candidates"]:
            self.assertEqual(record["series_qid"], "Q380519")
            self.assertEqual(record["status"], "CANDIDATE")
            self.assertIsNone(record["canonical_work_id"])
            self.assertEqual(record["evidence_status"], "EXTERNAL_DISCOVERY_METADATA_ONLY")
            self.assertRegex(record["episode_qid"], r"^Q[1-9][0-9]*$")
            self.assertTrue(record["episode_label"].strip())
            qids.add(record["episode_qid"])
        self.assertEqual(qids, ENT_QIDS)

    def test_review_holds_reference_known_candidates(self):
        proposal = json.loads((BATCH / "proposals/ent.json").read_text(encoding="utf-8"))
        holds = json.loads((BATCH / "REVIEW_HOLDS.json").read_text(encoding="utf-8"))
        qids = {row["episode_qid"] for row in proposal["candidates"]}
        held = {row["episode_qid"] for row in holds["exclude_from_public_episode_search_until_review"]}
        self.assertEqual(held, {"Q56247746", "Q866375"})
        self.assertTrue(held <= qids)
        self.assertEqual(holds["canonical_admission_effect"], "NONE")
        self.assertEqual(len(holds["series_identity_holds"]), 1)
        self.assertEqual(holds["series_identity_holds"][0]["queried_series_qid"], "Q134592591")
        self.assertEqual(holds["series_identity_holds"][0]["current_target_qid"], "Q117350388")


if __name__ == "__main__":
    unittest.main()
