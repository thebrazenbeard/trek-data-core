"""Adversarial, no-image-display readiness packet regressions."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate as packet  # noqa: E402


class ReleaseReadinessTests(unittest.TestCase):
    def setUp(self):
        self.data = packet.read_json(packet.PACKET)

    def test_source_bound_held_packet_passes(self):
        packet.validate(self.data)
        self.assertEqual(self.data["public_release_effect"], "NONE")

    def test_public_release_or_coverage_upgrade_cannot_be_self_certified(self):
        for key, fake in (
            ("public_release_effect", "RELEASED"),
            ("explorer_effect", "PUBLISHED"),
            ("image_bytes_committed", True),
            ("accepted_source_coverage_effect", "SOURCE_BOUND"),
            ("release_decision", "LEGAL_RIGHTS_CLEARED"),
        ):
            with self.subTest(key=key):
                d = copy.deepcopy(self.data)
                d[key] = fake
                with self.assertRaises(ValueError):
                    packet.validate(d)

    def test_film_still_canonical_confusion_rejected(self):
        for key, fake in (
            ("identity_relation", "FILM_EVENT_IN_STORY"),
            ("recommended_ui_surface", "DEFAULT_MOVIE_POSTER_SLOT"),
            ("source_local_film_row_id", "film:film-beyond"),
            ("related_work_title", "Star Trek Beyond"),
        ):
            with self.subTest(key=key):
                d = copy.deepcopy(self.data)
                d[key] = fake
                with self.assertRaises(ValueError):
                    packet.validate(d)

    def test_attribution_laundering_and_promotional_caption_rejected(self):
        for key, fake in (
            ("attribution_text", "Paramount official poster, all rights cleared"),
            ("image_caption", "Official film still from Star Trek Into Darkness"),
            ("no_endorsement_notice", "Approved by Paramount and cast"),
            ("image_alt", "Official film poster"),
            ("change_notice", "Cropped by us, no adaptation license necessary"),
        ):
            with self.subTest(key=key):
                d = copy.deepcopy(self.data)
                d["proposed_visible_ui"][key] = fake
                with self.assertRaises(ValueError):
                    packet.validate(d)

    def test_source_image_and_legal_risk_mutation_rejected(self):
        for section, key, fake in (
            ("proposed_asset", "byte_sha256", "f" * 64),
            ("proposed_asset", "derivative_bytes_produced", True),
            ("proposed_asset", "optimization_decision", "CROP_PROMO_BACKDROP"),
            ("rights_evidence", "license", "PUBLIC_DOMAIN"),
            ("rights_evidence", "rights_page_sha256", "f" * 64),
            ("rights_evidence", "underlying_promotional_backdrop_status", "FULLY_CLEARED"),
            ("independent_review", "status", "PUBLIC_RELEASE_GO"),
        ):
            with self.subTest(section=section, key=key):
                d = copy.deepcopy(self.data)
                d[section][key] = fake
                with self.assertRaises(ValueError):
                    packet.validate(d)

    def test_network_user_ip_leak_rejected(self):
        for key, fake in (
            ("host", "REMOTE_COMMONS_CDN"),
            ("third_party_image_request", True),
            ("initial_image_dom", "PRELOADED_ON_PAGE_STARTUP"),
            ("referrer_policy", "unsafe-url"),
            ("external_links_only_after_click", False),
            ("loading", "eager"),
        ):
            with self.subTest(key=key):
                d = copy.deepcopy(self.data)
                d["network_plan"][key] = fake
                with self.assertRaises(ValueError):
                    packet.validate(d)

    def test_accepted_source_bytes_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / packet.EXPECTED_SOURCE_PATH
            source.parent.mkdir(parents=True)
            source.write_bytes((packet.ROOT / packet.EXPECTED_SOURCE_PATH).read_bytes() + b" ")
            with self.assertRaises(ValueError):
                packet.validate(self.data, root)

    def test_duplicate_json_keys_and_unknown_grant_fail(self):
        d = copy.deepcopy(self.data)
        d["rights_evidence"]["marketing_copyright_cleared"] = True
        with self.assertRaises(ValueError):
            packet.validate(d)
        with self.assertRaises(ValueError):
            json.loads('{"release":"HELD","release":"GO"}',
                       object_pairs_hook=packet.unique_object)


if __name__ == "__main__":
    unittest.main()
