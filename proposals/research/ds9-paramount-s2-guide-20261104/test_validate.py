"""Adversarial regressions against false admission and unsupported source claims."""

import copy
import json
from pathlib import Path
import unittest

from validate import validate, locator_receipt


ORIGINAL = json.loads((Path(__file__).resolve().parent / "observations.json").read_text(encoding="utf-8"))


class TestHeldGuideCards(unittest.TestCase):
    def test_clean_batch(self):
        self.assertEqual(validate(ORIGINAL), [])
        self.assertEqual(len(locator_receipt(ORIGINAL)), 64)

    def test_no_admission_or_coverage_mutations(self):
        for key, value in (
            ("proposal_only", False),
            ("accepted_work_effect", "ADDED"),
            ("accepted_source_binding_effect", "ADDED"),
            ("episode_research_coverage_effect", "CLOSE_READ"),
            ("synopsis_publication_effect", "PUBLISHED"),
            ("admitted_briefings", 25),
        ):
            with self.subTest(field=key):
                copy_data = copy.deepcopy(ORIGINAL)
                copy_data[key] = value
                self.assertTrue(validate(copy_data))

    def test_no_fake_source_proof(self):
        for key, value in (
            ("http_status_verified", True),
            ("raw_html_bytes_pinned", True),
            ("full_primary_episode_audiovisual_or_script_read", True),
            ("source_body_sha256", "e" * 64),
            ("independence_group", "independent:another-source"),
        ):
            with self.subTest(field=key):
                copy_data = copy.deepcopy(ORIGINAL)
                copy_data["source"][key] = value
                self.assertTrue(validate(copy_data))

    def test_no_invented_or_missing_ordinals(self):
        for transform in (
            lambda x: x["source_local_cards"].pop(),
            lambda x: x["source_local_cards"].append(copy.deepcopy(x["source_local_cards"][-1])),
            lambda x: x["source_local_cards"][7].update({"episode": 7}),
            lambda x: x["source_local_cards"][2].update({"official_title": "The Visitor"}),
            lambda x: x["source_local_cards"][4].update({"publisher_card_locator": "Season 2 > Episode Guide"}),
            lambda x: x["source_local_cards"][8].update({"accepted_work_id": "work:ds9-2-9"}),
        ):
            with self.subTest(transform=repr(transform)):
                copy_data = copy.deepcopy(ORIGINAL)
                transform(copy_data)
                self.assertTrue(validate(copy_data))


if __name__ == "__main__":
    unittest.main()
