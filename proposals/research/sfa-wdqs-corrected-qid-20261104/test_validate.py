"""Adversarial checks of a bounded WDQS response interpretation."""

from __future__ import annotations

import copy
import json
import unittest

from validate import CANDIDATES, PUBLISHER, QUERY, RECEIPT, validate


class CorrectedQidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        cls.candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
        cls.publisher = json.loads(PUBLISHER.read_text(encoding="utf-8"))
        cls.query = QUERY.read_bytes()

    def alter_reject(self, target, key, value) -> None:
        receipt = copy.deepcopy(self.receipt)
        candidates = copy.deepcopy(self.candidates)
        if target == "receipt":
            receipt[key] = value
        elif target == "candidates":
            candidates[key] = value
        elif target == "row":
            candidates["rows"][4][key] = value
        elif target == "season":
            candidates["rows"][0][key] = value
        with self.assertRaises(ValueError):
            validate(receipt, candidates, self.query, self.publisher)

    def test_valid(self):
        validate(self.receipt, self.candidates, self.query, self.publisher)

    def test_no_obsolete_query_replay(self):
        changed = self.query.replace(b"Q117350388", b"Q134592591")
        with self.assertRaises(ValueError):
            validate(self.receipt, self.candidates, changed, self.publisher)

    def test_no_episode_count_denominator(self):
        self.alter_reject("receipt", "denominator_effect", "ELEVEN_WORKS")

    def test_no_source_admission(self):
        self.alter_reject("candidates", "source_binding_effect", "ACCEPTED")

    def test_no_playback_coverage(self):
        self.alter_reject("candidates", "coverage_effect", "CLOSE_READ")

    def test_season_labeled_member_not_episode(self):
        self.alter_reject("season", "publisher_episode_hint", 1)

    def test_no_synthetic_ordinal(self):
        self.alter_reject("row", "wikidata_episode_ordinal", 4)

    def test_no_title_case_flattening(self):
        self.alter_reject("row", "label", "Vox in Excelso")

    def test_no_title_match_promoted_to_work(self):
        self.alter_reject("row", "identity_hold", "CANONICAL_WORK")

    def test_no_altered_source_row_count(self):
        self.alter_reject("receipt", "binding_count", 10)

    def test_no_response_hash_laundering(self):
        self.alter_reject("receipt", "raw_response_sha256", "a" * 64)


if __name__ == "__main__":
    unittest.main()
