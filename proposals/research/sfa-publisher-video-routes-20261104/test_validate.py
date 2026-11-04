"""Adversarial controls for held publisher-source route observations."""

from __future__ import annotations

import copy
import json
import unittest

from validate import RECORDS, ROSTER, validate


class HeldPublisherRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(RECORDS.read_text(encoding="utf-8"))
        cls.roster = json.loads(ROSTER.read_text(encoding="utf-8"))

    def test_valid(self) -> None:
        validate(copy.deepcopy(self.data), self.roster)

    def test_all_attempted_promotions_rejected(self) -> None:
        changes = [
            ("accepted_work_effect", "UPSERT"),
            ("accepted_source_binding_effect", "BIND"),
            ("coverage_effect", "SOURCE_BOUND"),
            ("denominator_effect", "TEN_EPISODES"),
            ("reconciliation_effect", "SET_CANONICAL_ID"),
            ("audiovisual_content_inspected", True),
            ("episode_page_playback_attempted", True),
            ("rights_to_reproduce_media", "PUBLIC_DISPLAY_PERMISSION_VERIFIED"),
        ]
        for field, value in changes:
            with self.subTest(field=field):
                altered = copy.deepcopy(self.data)
                altered[field] = value
                with self.assertRaises(ValueError):
                    validate(altered, self.roster)

    def test_malformed_or_cross_domain_routes_rejected(self) -> None:
        for value in ("https://external.example/video/abc", "/shows/video/../../private/", "/shows/video/", "/shows/video/abc?token=secret", self.data["publisher_page_route_observations"][1]["route_path"]):
            with self.subTest(route=value):
                altered = copy.deepcopy(self.data)
                altered["publisher_page_route_observations"][0]["route_path"] = value
                with self.assertRaises(ValueError):
                    validate(altered, self.roster)

    def test_source_lineage_and_snapshot_limits(self) -> None:
        for field, value in (("independence_group", "independent:audiovisual"), ("raw_snapshot_committed", True), ("html_mutable", False), ("source_locator", "https://example.com/")):
            with self.subTest(field=field):
                altered = copy.deepcopy(self.data)
                altered["source_observation"][field] = value
                with self.assertRaises(ValueError):
                    validate(altered, self.roster)

    def test_extra_schema_field_rejected(self) -> None:
        altered = copy.deepcopy(self.data)
        altered["publisher_page_route_observations"][0]["canonical_work_id"] = "work:sfa:s1e1"
        with self.assertRaises(ValueError):
            validate(altered, self.roster)


if __name__ == "__main__":
    unittest.main()
