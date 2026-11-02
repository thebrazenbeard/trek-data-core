"""Synthetic, strictly offline tests for the candidate-only review packet CLI."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "prepare_episode_review_packet.py"
FIXTURE = ROOT / "tests" / "fixtures" / "episode_review_synthetic.json"
spec = importlib.util.spec_from_file_location("episode_review_packet", CLI)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EpisodeReviewPacketTests(unittest.TestCase):
    def setUp(self):
        self.input = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def reject(self, fragment: str, mutate):
        draft = copy.deepcopy(self.input)
        mutate(draft)
        with self.assertRaises(module.Rejected) as ctx:
            module.build_packet(draft)
        self.assertIn(fragment, str(ctx.exception))

    def test_fixture_candidate_is_not_admitted_and_sha_is_reproducible(self):
        packet = module.build_packet(self.input)
        self.assertEqual(packet, module.build_packet(copy.deepcopy(self.input)))
        recorded = packet.pop("packet_sha256")
        self.assertEqual(recorded, hashlib.sha256(module.canonical(packet)).hexdigest())
        self.assertEqual(packet["candidate_status"], "FIXTURE_ONLY_NOT_ADMISSIBLE")
        self.assertEqual(packet["authenticity"], "SYNTHETIC_FIXTURE_NO_CONTENT_INSPECTED")
        self.assertTrue(all(gate["status"] == "BLOCKED_FIXTURE_ONLY" for gate in packet["review_gates"]))
        self.assertEqual(packet["binding_candidate"]["lifecycle"], "PROPOSED")
        self.assertEqual(packet["binding_candidate"]["mapping_role_requested"], "EVIDENCE_BEARING")
        self.assertEqual(packet["source_candidate"]["digest_verified"], False)
        self.assertEqual(packet["source_candidate"]["rights_verified"], False)
        self.assertEqual(packet["evidence_candidates"][0]["candidate_ref"], "TEST-TRAINING-001:evidence:TEST-EV-001")
        self.assertEqual(packet["assertion_candidates"][0]["evidence_candidate_refs"], ["TEST-TRAINING-001:evidence:TEST-EV-001"])
        self.assertEqual(packet["coverage_handoff"]["coverage_effect"], "NONE")
        self.assertEqual(packet["coverage_handoff"]["denominator_effect"], "NONE")
        self.assertIsNone(packet["projection_handoff"]["approved_projection_hash"])
        self.assertFalse(packet["projection_handoff"]["projection_emitted"])

    def test_uninspected_metadata_only_handoff(self):
        draft = module.template("snw")
        packet = module.build_packet(draft)
        self.assertEqual(packet["binding_candidate"]["mapping_role_requested"], "METADATA_ONLY")
        self.assertEqual(packet["authenticity"], "NO_EPISODE_CONTENT_INSPECTED")
        self.assertEqual(packet["evidence_candidates"], [])
        self.assertEqual(packet["assertion_candidates"], [])
        self.assertEqual(packet["coverage_handoff"]["state_for_independent_review"], "NONE")

    def test_nonfixture_report_still_requires_independent_admission(self):
        self.input["fixture_only"] = False
        packet = module.build_packet(self.input)
        self.assertEqual(packet["candidate_status"], "PROPOSED_NOT_ADMITTED")
        self.assertEqual(packet["authenticity"], "RESEARCHER_REPORT_NOT_INDEPENDENTLY_VERIFIED")
        self.assertTrue(all(gate["status"] == "PENDING_INDEPENDENT_REVIEW" for gate in packet["review_gates"]))
        self.assertFalse(packet["source_candidate"]["digest_verified"])
        self.assertEqual(packet["coverage_handoff"]["state_for_independent_review"], "SOURCE_BOUND")
        self.assertFalse(packet["coverage_handoff"]["ledger_event_emitted"])

    def test_no_unsupported_input_fields_or_acceptance_switch(self):
        self.reject("unexpected fields", lambda d: d.update({"status": "ACCEPTED"}))
        self.reject("unexpected fields", lambda d: d["source"].update({"admission": "ACCEPTED"}))
        self.reject("missing fields", lambda d: d["source"].pop("content_sha256"))
        self.reject("fixture_only must", lambda d: d.update({"fixture_only": "false"}))
        self.reject("mission_id", lambda d: d.update({"mission_id": ["tng"]}))
        self.reject("mission_id", lambda d: d.update({"mission_id": "fictional"}))

    def test_content_evidence_requires_rights_date_hash_and_linked_claim(self):
        self.reject("lawful access basis", lambda d: d["source"].update({"access_basis": "PUBLISHER_PUBLIC_METADATA"}))
        self.reject("declared digest", lambda d: d["source"].update({"content_sha256": None}))
        self.reject("date", lambda d: d["source"].update({"inspected_on": None}))
        self.reject("observations", lambda d: d.update({"observations": []}))
        self.reject("linked assertions", lambda d: d.update({"assertions": []}))
        self.reject("rights_note", lambda d: d["source"].update({"rights_note": "  "}))
        self.reject("valid date", lambda d: d["source"].update({"inspected_on": "2026-02-30"}))
        self.reject("64-hex digest", lambda d: d["source"].update({"content_sha256": "not-a-digest"}))

    def test_cannot_pass_publisher_metadata_off_as_content(self):
        self.reject("episode-content source", lambda d: d["source"].update({"kind": "PUBLISHER_METADATA"}))
        self.reject("uninspected source", lambda d: d["source"].update({"inspection": "NOT_INSPECTED"}))

    def test_timecode_local_citations_and_original_note_bounds(self):
        self.reject("bounded timecode", lambda d: d["observations"][0].update({"cue_end_seconds": 10}))
        self.reject("bounded timecode", lambda d: d["observations"][0].update({"cue_end_seconds": 611}))
        self.reject("integer", lambda d: d["observations"][0].update({"cue_start_seconds": True}))
        self.reject("original_note", lambda d: d["observations"][0].update({"original_note": "A" * 321}))
        self.reject("control/format", lambda d: d["observations"][0].update({"original_note": "Original\u202euntrusted"}))
        self.reject("plain text", lambda d: d["observations"][0].update({"original_note": "<script>x</script>"}))

    def test_assertion_references_are_closed_and_unambiguous(self):
        self.reject("non-local", lambda d: d["assertions"][0].update({"evidence_ids": ["MISSING-EV"]}))
        self.reject("duplicate", lambda d: d["assertions"][0].update({"evidence_ids": ["TEST-EV-001", "TEST-EV-001"]}))
        self.reject("duplicate evidence_id", lambda d: d["observations"].append(copy.deepcopy(d["observations"][0])))
        self.reject("duplicate assertion_id", lambda d: d["assertions"].append(copy.deepcopy(d["assertions"][0])))

    def test_public_locator_has_no_query_userinfo_or_local_host(self):
        self.reject("public HTTPS", lambda d: d["source"].update({"locator": "http://example.org/video"}))
        self.reject("public HTTPS", lambda d: d["source"].update({"locator": "https://user:token@example.org/video"}))
        self.reject("public HTTPS", lambda d: d["source"].update({"locator": "https://example.org/video?token=abc"}))
        self.reject("public HTTPS", lambda d: d["source"].update({"locator": "https://localhost/test"}))

    def test_cli_emits_json_without_creating_repo_files(self):
        before = {path.name for path in ROOT.iterdir()}
        cmd = subprocess.run([sys.executable, str(CLI), "--input", str(FIXTURE)],
                             capture_output=True, text=True, cwd=ROOT, check=False)
        self.assertEqual(cmd.returncode, 0, cmd.stderr)
        self.assertEqual(json.loads(cmd.stdout)["fixture_only"], True)
        self.assertEqual(before, {path.name for path in ROOT.iterdir()})
        template = subprocess.run([sys.executable, str(CLI), "--template", "tng"],
                                  capture_output=True, text=True, cwd=ROOT, check=False)
        self.assertEqual(template.returncode, 0, template.stderr)
        self.assertEqual(json.loads(template.stdout)["source"]["inspection"], "NOT_INSPECTED")

    def test_safe_json_reader_rejects_duplicate_keys_symlinks_and_nonregular_input(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            target = parent / "input.json"
            target.write_text('{"packet_id":"ok","packet_id":"second"}', encoding="utf-8")
            with self.assertRaisesRegex(module.Rejected, "duplicate JSON key"):
                module.read_input(target)
            target.write_text("x" * (module.INPUT_LIMIT + 1), encoding="utf-8")
            with self.assertRaisesRegex(module.Rejected, "64 KiB"):
                module.read_input(target)
            link = parent / "link.json"
            link.symlink_to(target)
            with self.assertRaisesRegex(module.Rejected, "unable to read regular"):
                module.read_input(link)
            fifo = parent / "fifo.json"
            os.mkfifo(fifo)
            with self.assertRaisesRegex(module.Rejected, "regular file"):
                module.read_input(fifo)

    def test_safe_json_reader_fails_closed_without_protective_open_flags(self):
        for flag in ("O_NOFOLLOW", "O_NONBLOCK"):
            with self.subTest(flag=flag, state="zero"):
                with mock.patch.object(module.os, flag, 0), mock.patch.object(module.os, "open") as opened:
                    with self.assertRaisesRegex(module.Rejected, "requires O_NOFOLLOW and O_NONBLOCK"):
                        module.read_input(FIXTURE)
                    opened.assert_not_called()
            with self.subTest(flag=flag, state="missing"):
                with mock.patch.object(module.os, flag, 0), mock.patch.object(module.os, "open") as opened:
                    delattr(module.os, flag)
                    with self.assertRaisesRegex(module.Rejected, "requires O_NOFOLLOW and O_NONBLOCK"):
                        module.read_input(FIXTURE)
                    opened.assert_not_called()

    def test_deeply_nested_bounded_json_is_rejected_without_traceback(self):
        # 30 KiB, far below the byte cap, but beyond the JSON parser's depth limit.
        nested = "[" * 15000 + "]" * 15000
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "deep.json"
            source.write_text(nested, encoding="utf-8")
            with self.assertRaisesRegex(module.Rejected, "RecursionError"):
                module.read_input(source)
            cmd = subprocess.run([sys.executable, str(CLI), "--input", str(source)],
                                 capture_output=True, text=True, cwd=ROOT, check=False)
            self.assertEqual(cmd.returncode, 1)
            self.assertEqual(cmd.stdout, "")
            self.assertIn("REVIEW_PACKET_REJECTED:", cmd.stderr)
            self.assertIn("RecursionError", cmd.stderr)
            self.assertNotIn("Traceback", cmd.stderr)


if __name__ == "__main__":
    unittest.main()
