"""Adversarial tests: discovery must never inflate canonical evidence."""

import copy
import json
import pathlib
import unittest

from validate import validate

DATA = json.loads((pathlib.Path(__file__).resolve().parent / "records.json").read_text(encoding="utf-8"))


class MemoryAlphaLocatorContract(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(copy.deepcopy(DATA)), 16)

    def test_claims_fail_closed(self):
        for patch in ({"coverage_events": 1}, {"sources_admitted": 1}, {"crosswalks_proposed": 1}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                altered = copy.deepcopy(DATA)
                altered.update(patch)
                validate(altered)

    def test_media_text_or_semantic_claim_forbidden(self):
        for field in ("transcript", "image_url", "factual_assertion", "canonical_work_id"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                altered = copy.deepcopy(DATA)
                altered["category_locators"][0][field] = "unverified"
                validate(altered)

    def test_robots_license_and_lineage_invariants(self):
        for field, value in (
            ("direct_page_access", "ACCESS_GRANTED"),
            ("license_observed", "CC0"),
            ("narrative_evidence_weight", 1),
            ("media_reuse_authorization", "YES"),
            ("independence_group", "stapi.co"),
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                altered = copy.deepcopy(DATA)
                altered["external_source"][field] = value
                validate(altered)

    def test_duplicate_and_unobserved_direct_page_rejected(self):
        altered = copy.deepcopy(DATA)
        altered["category_locators"][1]["category"] = altered["category_locators"][0]["category"]
        with self.assertRaises(ValueError):
            validate(altered)
        altered = copy.deepcopy(DATA)
        altered["category_locators"][0]["status"] = "DIRECT_API_VERIFIED"
        with self.assertRaises(ValueError):
            validate(altered)

    def test_wrong_host_and_locators_rejected(self):
        for url in ("https://example.org/wiki/Category:TOS_episodes", "https://memory-alpha.fandom.com/wiki/Category:TNG_episodes"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                altered = copy.deepcopy(DATA)
                altered["category_locators"][0]["url"] = url
                validate(altered)


if __name__ == "__main__":
    unittest.main()
