"""Fail-closed checks for the TOS publisher-metadata-only source pilot.

This validates the proposal's stated limits, not actual episode inspection.
"""

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "proposals" / "research" / "tos-source-pilot-20261102"


class TosSourcePilotTests(unittest.TestCase):
    def test_review_packet_is_metadata_only_with_no_episode_claims(self):
        proposal = json.loads((PILOT / "episode-review-input.json").read_text(encoding="utf-8"))
        self.assertEqual(proposal["mission_id"], "tos")
        self.assertEqual(proposal["episode"]["title"], "The Cage")
        self.assertEqual(proposal["source"]["kind"], "PUBLISHER_METADATA")
        self.assertEqual(proposal["source"]["inspection"], "NOT_INSPECTED")
        self.assertEqual(proposal["source"]["access_basis"], "PUBLISHER_PUBLIC_METADATA")
        self.assertIsNone(proposal["source"]["inspected_on"])
        self.assertIsNone(proposal["source"]["content_sha256"])
        self.assertEqual(proposal["observations"], [])
        self.assertEqual(proposal["assertions"], [])

        check = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "prepare_episode_review_packet.py"),
                "--input",
                str(PILOT / "episode-review-input.json"),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(check.returncode, 0, check.stderr)
        packet = json.loads(check.stdout)
        self.assertEqual(packet["record_type"], "episode_review_packet")
        self.assertEqual(packet["authenticity"], "NO_EPISODE_CONTENT_INSPECTED")
        self.assertEqual(packet["source_candidate"]["admission"], "NONE")
        self.assertFalse(packet["source_candidate"]["digest_verified"])
        self.assertEqual(packet["binding_candidate"]["accepted_source_work_binding_effect"], "NONE")
        self.assertEqual(packet["coverage_handoff"]["coverage_effect"], "NONE")
        self.assertEqual(packet["projection_handoff"]["projection_effect"], "NONE")

    def test_historical_and_streaming_dimensions_remain_source_attributed(self):
        context = json.loads((PILOT / "source-relative-context.json").read_text(encoding="utf-8"))
        self.assertEqual(context["status"], "RESEARCH_LEADS_ONLY")
        self.assertFalse(context["full_audiovisual_episode_inspected"])
        self.assertEqual(context["partial_playback_visual_witness"]["title"], "The Man Trap")
        self.assertFalse(context["partial_playback_visual_witness"]["complete_audio_visual_processing"])
        self.assertIsNone(context["partial_playback_visual_witness"]["media_byte_sha256"])
        self.assertIsNone(context["source_response_sha256"])
        self.assertEqual(context["identity_reconciliation"], "NOT_ATTEMPTED")
        self.assertEqual(context["coverage_effect"], "NONE")
        statements = context["statements"]
        self.assertEqual(len(statements), len({s["id"] for s in statements}))
        dimensions = {s["dimension"] for s in statements}
        self.assertIn("PILOT_PRODUCTION_STATUS", dimensions)
        self.assertIn("PILOT_LEAD_CHARACTER_METADATA", dimensions)
        self.assertIn("ORIGINAL_TELEVISION_BROADCAST", dimensions)
        self.assertIn("CURRENT_STREAMING_CATALOG_POSITION", dimensions)
        for entry in statements:
            self.assertTrue(entry["source_url"].startswith("https://"))
            self.assertTrue(entry["source_attribution"])
            self.assertTrue(entry["scope_note"])
        self.assertEqual(
            [(s["source_attribution"], s["object"]) for s in statements
             if s["subject_title"] == "The Man Trap"
             and s["dimension"] == "CURRENT_STREAMING_CATALOG_POSITION"],
            [("PARAMOUNT_PLUS_ROSTER", "Season 1, Episode 2"),
             ("PLUTO_ROSTER", "Season 1, Episode 1")],
        )


if __name__ == "__main__":
    unittest.main()
