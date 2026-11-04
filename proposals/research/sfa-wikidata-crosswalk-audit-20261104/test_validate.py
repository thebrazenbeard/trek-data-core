"""Falsification controls for the held SFA publisher-versus-WDQS comparison."""

from __future__ import annotations

import copy
import json
import unittest

from validate import HERE, read_sources, validate


class SfaCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.original = json.loads((HERE / "crosswalk.json").read_text(encoding="utf-8"))
        cls.sources = read_sources()

    def mutate_reject(self, callback) -> None:
        data = copy.deepcopy(self.original)
        callback(data)
        with self.assertRaises(ValueError):
            validate(data, self.sources)

    def test_source_aligned(self) -> None:
        validate(copy.deepcopy(self.original), self.sources)

    def test_publisher_title_mismatch_rejected(self) -> None:
        self.mutate_reject(lambda d: d["comparison_rows"][9].update(publisher_title="Rubicon"))

    def test_wrong_ordinal_rejected(self) -> None:
        self.mutate_reject(lambda d: d["comparison_rows"][4].update(episode=6))

    def test_invented_wikidata_candidate_rejected(self) -> None:
        self.mutate_reject(lambda d: d["comparison_rows"][0].update(wikidata_episode_qid="Q123456"))

    def test_false_zero_means_no_episodes_rejected(self) -> None:
        self.mutate_reject(lambda d: d["negative_or_ambiguous_evidence"][0].update(interpretation="NO_EPISODES_EXIST"))

    def test_false_omnipotent_crosswalk_rejected(self) -> None:
        self.mutate_reject(lambda d: d["comparison_rows"][3].update(wikidata_alignment="EXACT"))

    def test_media_bucket_promotion_rejected(self) -> None:
        self.mutate_reject(lambda d: d["negative_or_ambiguous_evidence"][3].update(interpretation="S2_EPISODE_200"))

    def test_lineage_independence_laundering_rejected(self) -> None:
        self.mutate_reject(lambda d: d["lineage"][1].update(independence_group="independent:press"))

    def test_governance_bypass_rejected(self) -> None:
        self.mutate_reject(lambda d: d["effects"].update(source_work_binding="ACCEPTED"))

    def test_source_drift_rejected(self) -> None:
        sources = copy.deepcopy(self.sources)
        sources[next(iter(sources))]["disposition"] = "SOURCE_BOUND"
        with self.assertRaises(ValueError):
            validate(copy.deepcopy(self.original), sources)


if __name__ == "__main__":
    unittest.main()
