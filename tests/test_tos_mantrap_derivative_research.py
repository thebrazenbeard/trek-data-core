"""Integrity checks for a source-read, explicitly non-admitted TOS proposal.

These deliberately check provenance and referential consistency; a passing test
must not be advertised as a primary audiovisual, copyright, or semantic audit.
"""

from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "proposals/research/tos-man-trap-derivative-close-read-20261102"


def read_json(name: str) -> dict:
    return json.loads((BATCH / name).read_text(encoding="utf-8"))


class ManTrapDerivativeResearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = read_json("MANIFEST.json")
        cls.entities = read_json("local_entities.json")
        cls.evidence = read_json("evidence.json")
        cls.assertions = read_json("assertions.json")

    def test_file_integrity(self) -> None:
        self.assertEqual(self.manifest["admission"], "PROPOSAL_ONLY")
        digests = self.manifest["files_sha256"]
        self.assertEqual(set(digests), {"RESEARCH_RECORD.md", "assertions.json", "evidence.json", "local_entities.json"})
        stream = bytearray()
        for name in sorted(digests):
            path = BATCH / name
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, digests[name], name)
            stream.extend(f"{digest}  {path.relative_to(ROOT)}\n".encode())
        self.assertEqual(hashlib.sha256(stream).hexdigest(), self.manifest["files_sha256_stream_digest"])

    def test_source_receipt_and_read_windows(self) -> None:
        source = self.manifest["source"]
        self.assertEqual(source["retrieval"], "HTTP_200_AND_COMPLETE_AVAILABLE_ARTICLE_BODY_PROCESSED")
        self.assertFalse(source["authenticated_primary_av_or_studio_script"])
        self.assertFalse(source["public_transcript_text_included"])
        self.assertEqual(source["rights_to_republish_source_text"], "UNVERIFIED")
        self.assertEqual(source["source_lineage_class"], "SOURCE_SELF_REPORTED_UNVERIFIED_DERIVATION")
        upstream = source["upstream_self_report"]
        self.assertEqual(upstream["raw_html_physical_line"], 946)
        self.assertEqual(upstream["attributed_upstream_url"], "http://www.chakoteya.net/")
        self.assertIn("modified", upstream["publisher_statement"])
        self.assertFalse(upstream["attribution_is_independently_verified"])
        self.assertFalse(upstream["this_episode_upstream_match_verified"])
        self.assertEqual(upstream["upstream_candidate_direct_retrieval"], "HTTP_503_NO_TEXT_READ")
        self.assertEqual(upstream["independent_corroboration_count"], 0)
        self.assertEqual(source["raw_html_bytes"], 148006)
        self.assertEqual(source["rendered_text_bytes"], 32567)
        self.assertEqual(source["rendered_text_numbered_lines"], 982)
        self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", source["raw_html_sha256"]))
        self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", source["rendered_text_sha256"]))
        cursor = 1
        for start, end in source["complete_rendered_text_read_windows_inclusive"]:
            self.assertEqual(start, cursor)
            self.assertGreaterEqual(end, start)
            cursor = end + 1
        self.assertEqual(cursor, 983)

    def test_records_are_source_relative_and_consistent(self) -> None:
        local_ids = [item["id"] for item in self.entities["entities"]]
        evidence_ids = [item["id"] for item in self.evidence["evidence"]]
        assertion_ids = [item["id"] for item in self.assertions["assertions"]]
        self.assertEqual(len(local_ids), len(set(local_ids)))
        self.assertEqual(len(evidence_ids), len(set(evidence_ids)))
        self.assertEqual(len(assertion_ids), len(set(assertion_ids)))
        self.assertEqual(len(local_ids), 23)
        self.assertEqual(len(evidence_ids), 17)
        self.assertEqual(len(assertion_ids), 9)
        self.assertEqual(self.manifest["records"]["local_entities"], 23)
        self.assertEqual(self.manifest["records"]["source_relative_evidence"], 17)
        self.assertEqual(self.manifest["records"]["proposed_assertions"], 9)
        entity_set, evidence_set = set(local_ids), set(evidence_ids)
        for item in self.evidence["evidence"]:
            self.assertTrue(set(item["local_entity_ids"]).issubset(entity_set), item["id"])
            self.assertGreaterEqual(item["start_line"], 10)
            self.assertLessEqual(item["end_line"], 982)
            self.assertLessEqual(item["start_line"], item["end_line"])
            self.assertFalse('"' in item["observation"], "Avoid potentially copied dialogue in paraphrases")
        for item in self.assertions["assertions"]:
            self.assertEqual(item["status"], "PROPOSED")
            self.assertIn(item["predicate"], {"CLAIMS", "DEPICTS"})
            self.assertTrue(item["evidence"])
            self.assertTrue(set(item["evidence"]).issubset(evidence_set))
            for key in ("context_evidence_ids", "counter_evidence_ids"):
                self.assertTrue(set(item[key]).issubset(evidence_set), item["id"])
            if item["subject_type"] == "LOCAL_ENTITY":
                self.assertIn(item["subject"], entity_set)
            else:
                self.assertEqual(item["subject"], self.manifest["work"]["candidate_id"])

    def test_hostile_review_identity_mental_state_and_locators(self) -> None:
        entity_ids = {item["id"] for item in self.entities["entities"]}
        self.assertNotIn("green", entity_ids, "Old Green referent joined person and impersonation")
        self.assertTrue({"green_missing_person", "green_apparent", "green_identity_question"}.issubset(entity_ids))
        self.assertTrue({"nancy_apparent", "nancy_historical", "nancy_identity_question"}.issubset(entity_ids))

        evidence = {item["id"]: item for item in self.evidence["evidence"]}
        self.assertTrue({"green_missing_person", "green_apparent", "green_identity_question"}.issubset(evidence["e07"]["local_entity_ids"]))
        self.assertTrue({"nancy_apparent", "nancy_identity_question"}.issubset(evidence["e14"]["local_entity_ids"]))
        self.assertIn("he is guessing", evidence["e08"]["observation"])
        self.assertIn("not access to her private thoughts", evidence["e08"]["observation"])
        self.assertIn("uhura_interlocutor", evidence["e08"]["local_entity_ids"])
        self.assertEqual((evidence["e11a"]["start_line"], evidence["e11a"]["end_line"]), (742, 759))
        self.assertEqual((evidence["e11b"]["start_line"], evidence["e11b"]["end_line"]), (761, 769))
        self.assertEqual((evidence["e11c"]["start_line"], evidence["e11c"]["end_line"]), (784, 792))
        self.assertNotIn("e11", evidence, "Old combined death-and-ecology evidence must stay retired")
        self.assertEqual((evidence["e13"]["start_line"], evidence["e13"]["end_line"]), (890, 902))
        self.assertEqual((evidence["e14"]["start_line"], evidence["e14"]["end_line"]), (906, 971))
        self.assertEqual((evidence["e15"]["start_line"], evidence["e15"]["end_line"]), (974, 980))

        assertions = {item["id"]: item for item in self.assertions["assertions"]}
        self.assertEqual(assertions["a05"]["evidence"], ["e11b"])
        self.assertIn("killed", assertions["a05"]["object"])
        self.assertNotIn("last", assertions["a05"]["object"])
        self.assertEqual(assertions["a09"]["evidence"], ["e11a", "e11c"])
        self.assertIn("one survivor", assertions["a09"]["object"])
        self.assertNotIn("killed", assertions["a09"]["object"])
        for key in ("a03", "a06"):
            self.assertEqual(assertions[key]["predicate"], "DEPICTS")
            self.assertEqual(assertions[key]["proposed_projection_status"], "UNRESOLVED")
            self.assertTrue(assertions[key]["scope"]["truth_level"].startswith("SOURCE_RELATIVE_"))

    def test_no_projection_or_acceptance_claim(self) -> None:
        records = self.manifest["records"]
        self.assertEqual(records["accepted_briefings"], 0)
        self.assertEqual(records["global_identity_reconciliations"], 0)
        self.assertEqual(records["coverage_events"], 0)
        self.assertEqual(self.entities["global_identity_edges_created"], 0)
        self.assertEqual(self.assertions["accepted_assertions"], 0)
        self.assertEqual(self.assertions["projection_effect"], "NONE")
        self.assertFalse(self.evidence["audiovisual_verified"])
        self.assertFalse(self.evidence["copyright_text_republished"])
        source_ids = {self.entities["source_local_id"], self.evidence["source_local_id"], self.assertions["source_local_id"]}
        self.assertEqual(source_ids, {self.manifest["source"]["source_local_id"]})

    def test_librarian_rights_gate_links_are_real_local_files(self) -> None:
        gate = ROOT / "proposals/librarian/foreverdreaming-rights-gate-20261102/RESEARCH_RECORD.md"
        content = gate.read_text(encoding="utf-8")
        for relative in re.findall(r"\]\((\.\./[^)#]+)(?:#[^)]*)?\)", content):
            target = (gate.parent / relative).resolve()
            self.assertTrue(target.is_relative_to(ROOT), relative)
            self.assertTrue(target.is_file(), f"Broken repository-local reference: {relative}")
        self.assertIn("unverified historical reports", content)


if __name__ == "__main__":
    unittest.main()
