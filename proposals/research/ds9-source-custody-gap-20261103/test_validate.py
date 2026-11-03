"""Negative checks that the DS9 custody proposal cannot self-promote."""

import copy
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from validate import REPO, check_contract  # noqa: E402


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


class TestCustodyGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = load("source_routes.json")
        cls.evidence = load("evidence.json")
        cls.assertions = load("assertions.json")
        prior = json.loads((REPO / "proposals/research/ds9-paramount-s1-guide-20261103/records.json").read_text())
        cls.cards = {x["id"] for x in prior["source_local_episode_slots"]}

    def test_untouched(self):
        check_contract(self.routes, self.evidence, self.assertions, self.cards)

    def reject(self, mutate):
        routes, evidence, assertions = copy.deepcopy((self.routes, self.evidence, self.assertions))
        mutate(routes, evidence, assertions)
        with self.assertRaises(ValueError):
            check_contract(routes, evidence, assertions, self.cards)

    def test_reject_coverage(self):
        self.reject(lambda r, e, a: r.__setitem__("coverage_effect", "SOURCE_BOUND"))

    def test_reject_primary_read(self):
        self.reject(lambda r, e, a: r.__setitem__("primary_script_or_av_reads_completed", 1))

    def test_reject_work_identity(self):
        self.reject(lambda r, e, a: r.__setitem__("target_work_identity_status", "ACCEPTED"))

    def test_reject_untrusted_url(self):
        self.reject(lambda r, e, a: r["routes"][0]["public_observation_urls"].append("https://example.org/script"))

    def test_reject_claimed_rights(self):
        self.reject(lambda r, e, a: r["routes"][0].__setitem__("rights_to_republish_script_text", "GRANTED"))

    def test_reject_fiction_evidence(self):
        self.reject(lambda r, e, a: e.__setitem__("episode_scene_or_dialogue_evidence_count", 5))

    def test_reject_unresolved_promotion(self):
        self.reject(lambda r, e, a: a["assertions"][0].__setitem__("status", "STABLE"))


if __name__ == "__main__":
    unittest.main()
