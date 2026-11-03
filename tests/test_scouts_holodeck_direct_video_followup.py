"""Hostile semantic and provenance checks for first-party Holodeck 6–10 pages."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "proposals/research/short/scouts-holodeck-direct-video-followup-20261103"
spec = importlib.util.spec_from_file_location("scouts_holodeck_direct", PACKET / "validate.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
OBS = module.read_pinned()
HISTORICAL = module.read_historical()
CATALOG = json.loads((ROOT / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))


class ScoutsHolodeckDirectSourceTests(unittest.TestCase):
    def reject_semantic(self, change, message):
        candidate = copy.deepcopy(OBS)
        change(candidate)
        with self.assertRaisesRegex(ValueError, message):
            module.validate(candidate)

    def test_direct_page_metadata_only_and_one_new_fifth_summary(self):
        self.assertEqual(module.validate(OBS), 5)
        self.assertEqual([r["video_id"] for r in OBS["observations"]], list(module.VIDEO_IDS))
        self.assertEqual([r["title_relation_to_historical_search"] for r in OBS["observations"]], [
            "DIFFERS_SOURCE_RELATIVE", "DIFFERS_SOURCE_RELATIVE", "DIFFERS_SOURCE_RELATIVE",
            "MATCHES_SOURCE_RELATIVE", "PREVIOUSLY_HELD_NOW_DIRECT_PAGE_OBSERVED",
        ])
        self.assertEqual(sum(r["new_synopsis_proposal"] is not None for r in OBS["observations"]), 1)
        self.assertIsNone(HISTORICAL["held_following_row"]["synopsis"])

    def test_watched_video_claim_is_rejected_before_snapshot_pin(self):
        self.reject_semantic(lambda d: d.update(video_playback_performed=True), "false playback")
        self.reject_semantic(lambda d: d.update(full_episodes_read=True), "false playback")
        self.reject_semantic(lambda d: d.update(raw_html_bytes_committed=True), "false playback")

    def test_private_or_unapproved_release_effects_cannot_be_set(self):
        for field in ("accepted_work_effect", "accepted_evidence_effect", "accepted_coverage_effect",
                      "public_synopsis_release_effect", "artwork_release_effect"):
            with self.subTest(field=field):
                self.reject_semantic(lambda d, f=field: d.update({f: "ACCEPTED"}),
                                     "protected effect promoted")

    def test_host_spoof_and_cross_video_source_rewrite(self):
        self.reject_semantic(lambda d: d["observations"][0].update(
            video_page="https://www.youtube.com@evil.invalid/watch?v=-m7ISEuAhac"),
            "source video URL")
        self.reject_semantic(lambda d: d["observations"][0].update(video_id="vlez2Dtu95E"),
                             "source-local video assignment")

    def test_title_variant_is_derived_from_historical_vs_current(self):
        self.reject_semantic(lambda d: d["observations"][0].update(
            title_relation_to_historical_search="MATCHES_SOURCE_RELATIVE"),
            "historical/current publisher title state")
        self.reject_semantic(lambda d: d["observations"][3].update(
            title_relation_to_historical_search="DIFFERS_SOURCE_RELATIVE"),
            "historical/current publisher title state")

    def test_current_title_and_fingerprint_are_not_unpinned_claims(self):
        self.reject_semantic(lambda d: d["observations"][2].update(
            current_first_party_title="A fabricated current YouTube title"),
            "direct first-party title/fingerprint")
        self.reject_semantic(lambda d: d["observations"][4].update(title_sha256="f" * 64),
                             "direct first-party title/fingerprint")

    def test_page_receipts_and_description_fingerprints_cannot_be_swapped(self):
        self.reject_semantic(lambda d: d["observations"][0].update(
            first_description_paragraph_sha256=d["observations"][1]["first_description_paragraph_sha256"]),
            "first-party description fingerprint")
        self.reject_semantic(lambda d: d["observations"][4].update(raw_html_retrieval_bytes=0),
                             "first-party description fingerprint")

    def test_date_claim_cannot_shift(self):
        self.reject_semantic(lambda d: d["observations"][4].update(
            first_party_publish_datetime="1900-01-01T00:00:00Z"), "published timestamp/date")

    def test_fifth_source_addition_must_not_retroactively_erase_the_hold(self):
        self.reject_semantic(lambda d: d["observations"][4].update(
            title_relation_to_historical_search="MATCHES_SOURCE_RELATIVE"),
            "old #10 hold silently overwritten")
        historical = copy.deepcopy(HISTORICAL)
        historical["held_following_row"]["synopsis"] = "Misrepresented as earlier verified."
        with self.assertRaisesRegex(ValueError, "historical #10 hold"):
            module.validate(OBS, historical=historical)

    def test_four_original_synopses_are_not_rewritten_through_this_followup(self):
        self.reject_semantic(lambda d: d["observations"][1].update(
            new_synopsis_proposal="A silent retcon of the #7 synopsis."),
            "earlier four synopses")

    def test_fifth_original_synopsis_is_pinned_after_semantic_checks(self):
        self.reject_semantic(lambda d: d["observations"][4].update(
            new_synopsis_proposal="The farmer and Scouts record something entirely invented by the auditor without any actual publisher-source support or evidence whatsoever."),
            "unreviewed current-page followup content")
        self.reject_semantic(lambda d: d["observations"][4].update(
            new_synopsis_proposal="<script>alert(1)</script>"), "unsafe or unsupported fifth")

    def test_discovery_crosswalk_does_not_admit_work_or_fake_source(self):
        changed = copy.deepcopy(CATALOG)
        row = next(r for r in changed["rows"] if r["row_id"] == "short:scouts:holodeck_rescues:10")
        row["source_locator"] = "https://youtu.be/AAAA"
        with self.assertRaisesRegex(ValueError, "unadmitted discovery crosswalk"):
            module.validate(OBS, catalog=changed)
        changed = copy.deepcopy(CATALOG)
        changed["coverage_effect"] = "ACCEPTED"
        with self.assertRaisesRegex(ValueError, "discovery ledger promoted"):
            module.validate(OBS, catalog=changed)


if __name__ == "__main__":
    unittest.main()
