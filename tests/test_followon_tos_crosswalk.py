"""Falsification checks for frozen-receipt follow-on Librarian crosswalks."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_followon_tos_crosswalk as followon


class FollowonTOSCrosswalkTest(unittest.TestCase):
    def setUp(self) -> None:
        self.selection = json.loads((followon.BATCH / "selection.json").read_text(encoding="utf-8"))

    def test_committed_replay_is_deterministic_and_nonadmitting(self) -> None:
        self.assertEqual((followon.BATCH / "crosswalk.json").read_bytes(), followon.canonical_bytes(followon.build()))
        result = followon.build()
        self.assertEqual(result["source_retrieved_in_this_batch"], "NONE_REPLAY_OF_PRIOR_HASH_PINNED_OBSERVATION")
        self.assertEqual(result["source_local_crosswalk_count"], 5)
        self.assertEqual(result["total_research_leads_unchanged"], 218)
        self.assertEqual(result["prior_tranche_crosswalk_count"], 5)
        for effect in ("source_work_binding_admission", "briefing_admission_effect", "denominator_effect", "coverage_effect"):
            self.assertEqual(result[effect], "NONE")
        for item in result["matches"]:
            self.assertEqual(item["candidate_title"], item["publisher_title"])
            self.assertEqual(item["status"], "PROPOSED_TITLE_AND_SERIES_CROSSWALK")
            self.assertEqual(item["candidate_independence_group"], "wikidata:wdqs")
            self.assertEqual(item["publisher_independence_group"], "publisher:paramount")
            self.assertIsNone(item["canonical_work_id"])
            self.assertIsNone(item["accepted_source_work_binding"])
            self.assertEqual(item["coverage_effect"], "NONE")

    def assert_mutation_fails(self, mutate) -> None:
        poisoned = copy.deepcopy(self.selection)
        mutate(poisoned)
        with self.assertRaises(followon.CrosswalkValidationError):
            followon.build(selection_override=poisoned)

    def test_wrong_title_ordinal_or_unknown_qid_fails_closed(self) -> None:
        self.assert_mutation_fails(lambda s: s["selected"][0].update(publisher_title="Wrong title"))
        self.assert_mutation_fails(lambda s: s["selected"][0].update(publisher_episode_number=4))
        self.assert_mutation_fails(lambda s: s["selected"][0].update(qid="Q0"))

    def test_overlapping_prior_tranche_and_duplicate_fail(self) -> None:
        self.assert_mutation_fails(lambda s: s["selected"][0].update(qid="Q1287667", publisher_title="The Man Trap", publisher_episode_number=2))
        self.assert_mutation_fails(lambda s: s["selected"][1].update(qid=s["selected"][0]["qid"]))

    def test_retrieval_claim_cannot_be_silently_elevated(self) -> None:
        self.assert_mutation_fails(lambda s: s["source_custody"].update(live_page_rechecked=True))
        self.assert_mutation_fails(lambda s: s["source_custody"].update(new_primary_source_retrieval="COMPLETE_PAGE"))
        self.assert_mutation_fails(lambda s: s["source_custody"].update(new_html_response_sha256="invented"))

    def test_mutually_rehashed_publisher_index_and_csv_cannot_self_attest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="trek-source-anchor-", dir=followon.ROOT) as folder:
            temp = Path(folder)
            (temp / "tos").mkdir()
            index = json.loads((followon.PUBLISHER_DIR / "index.json").read_text(encoding="utf-8"))
            csv_bytes = (followon.PUBLISHER_DIR / "tos.csv").read_bytes()
            changed_csv = csv_bytes.replace(b"The Cage", b"An altered pilot", 1)
            index["source_pages"][0]["observation_csv_sha256"] = hashlib.sha256(changed_csv).hexdigest()
            (temp / "index.json").write_text(json.dumps(index), encoding="utf-8")
            (temp / "tos.csv").write_bytes(changed_csv)
            (temp / "tos/bundle.json").write_bytes((followon.PUBLISHER_DIR / "tos/bundle.json").read_bytes())
            selection = copy.deepcopy(self.selection)
            selection["source_custody"]["prior_observation_directory"] = str(temp.relative_to(followon.ROOT))
            with patch.object(followon, "PUBLISHER_DIR", temp):
                with self.assertRaisesRegex(followon.CrosswalkValidationError, "source-lineage anchor drift"):
                    followon.build(selection_override=selection)

    def test_replaced_candidate_snapshot_with_duplicate_qid_cannot_pass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="trek-lead-anchor-") as folder:
            replacement = Path(folder) / "research-leads.json"
            data = json.loads(followon.LEADS.read_text(encoding="utf-8"))
            reference = next(x for x in data["leads"] if x.get("episode_qid") == "Q2664096")
            data["leads"][-1] = copy.deepcopy(reference)
            replacement.write_text(json.dumps(data), encoding="utf-8")
            with patch.object(followon, "LEADS", replacement):
                with self.assertRaisesRegex(followon.CrosswalkValidationError, "source-lineage anchor drift"):
                    followon.build()
                # Even after an explicitly updated baseline anchor, the
                # duplicate QID must be rejected semantically.
                adjusted = dict(followon.ACCEPTED_SOURCE_SHA256)
                adjusted["archived_wdqs_leads"] = hashlib.sha256(replacement.read_bytes()).hexdigest()
                with patch.object(followon, "ACCEPTED_SOURCE_SHA256", adjusted):
                    with self.assertRaisesRegex(followon.CrosswalkValidationError, "candidate QID collision"):
                        followon.build()


if __name__ == "__main__":
    unittest.main()
