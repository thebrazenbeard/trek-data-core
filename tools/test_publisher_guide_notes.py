"""Adversarial fixtures for held publisher-guide notes; never canonical admission."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_publisher_guide_notes.py")
SPEC = importlib.util.spec_from_file_location("trek_publisher_notes", SCRIPT)
notes = importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = notes
SPEC.loader.exec_module(notes)


class PublisherGuideNotesTests(unittest.TestCase):
    def test_current_accepted_main_compiles_57_drafts_and_one_identity_hold(self):
        result = notes.compile_notes()
        self.assertEqual(result["source_local_observation_count"], 58)
        self.assertEqual(result["held_paraphrase_count"], 57)
        self.assertEqual(result["withheld_identity_count"], 1)
        self.assertEqual({r["series"] for r in result["notes"]}, {"ENT", "VOY", "PIC", "DIS"})
        self.assertEqual((result["canonical_work_count_added"], result["canonical_briefing_count_added"]), (0, 0))
        self.assertEqual(result["episode_coverage_effect"], "NONE")
        held = [r for r in result["notes"] if r["paraphrase"] is None]
        self.assertEqual(len(held), 1)
        self.assertEqual(held[0]["source_local_title"], "Caretaker")
        self.assertEqual(held[0]["review_state"], "WITHHELD_MULTIPART_IDENTITY")
        self.assertTrue(all(r["canonical_work_id"] is None and r["canonical_briefing_id"] is None
                            for r in result["notes"]))
        self.assertTrue(all(r["paraphrase_kind"] == "MARKETING_DESCRIPTION_PARAPHRASE"
                            for r in result["notes"]))

    def test_checked_sidecar_matches_exact_deterministic_bytes(self):
        result = notes.run(check=True)
        output = notes.REPO / notes.OUTPUT
        self.assertEqual(output.read_bytes(), notes.serialized(result))
        self.assertEqual(notes.serialized(notes.compile_notes()), notes.serialized(result))

    def test_source_digest_change_fails_closed(self):
        original = notes.PACKETS[0]
        wrong = notes.Packet(original.path, "0" * 64, original.kind, original.count)
        with self.assertRaisesRegex(ValueError, "pinned proposal digest mismatch"):
            notes.compile_notes(packets=(wrong,))

    def test_missing_or_symlinked_input_fails_closed(self):
        packet = notes.PACKETS[0]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, "missing"):
                notes.read_packet(packet, root)
            target = notes.REPO / packet.path
            link = root / packet.path
            link.parent.mkdir(parents=True)
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symlinked"):
                notes.read_packet(packet, root)

    def test_duplicate_json_key_rejected_even_with_matching_digest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "proposals" / "poisoned.json"
            path.parent.mkdir()
            raw = b'{"rows":[],"rows":[]}'
            path.write_bytes(raw)
            packet = notes.Packet("proposals/poisoned.json", hashlib.sha256(raw).hexdigest(), "ENT", 0)
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                notes.read_packet(packet, root)

    def test_source_local_slot_collision_and_duplicate_row_rejected(self):
        packet = notes.PACKETS[0]
        row = {"row_id": "local-1", "title": "Example"}
        kwargs = dict(series="ENT", title="Example", season=1, episode=5, synopsis="A publisher text draft with enough length.",
                      status="HELD_EDITORIAL_DRAFT", guide_url="https://www.paramountplus.com/shows/enterprise/episodes/1/",
                      locator="S1 E5 > publisher card")
        collected = {}
        notes.add_note(collected, packet, row, row_id="local-1", **kwargs)
        with self.assertRaisesRegex(ValueError, "duplicate source-local note"):
            notes.add_note(collected, packet, row, row_id="local-1", **kwargs)
        with self.assertRaisesRegex(ValueError, "conflicting publisher-guide slot"):
            notes.add_note(collected, packet, row, row_id="local-2", **kwargs)

    def test_modified_packet_cannot_promote_admission_even_if_rehashed(self):
        source = notes.PACKETS[0]
        packet_data = notes.read_packet(source)
        packet_data["admission_effect"] = "ADMITTED"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / source.path
            path.parent.mkdir(parents=True)
            raw = (json.dumps(packet_data, sort_keys=True) + "\n").encode()
            path.write_bytes(raw)
            promoted = notes.Packet(source.path, hashlib.sha256(raw).hexdigest(), source.kind, source.count)
            with self.assertRaisesRegex(ValueError, "held provenance/effect"):
                notes.compile_notes(root, packets=(promoted,))

    def test_modified_packet_cannot_fabricate_a_synopsis_even_if_rehashed(self):
        source = notes.PACKETS[0]
        packet_data = notes.read_packet(source)
        packet_data["rows"][0]["original_synopsis_draft"] = ""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / source.path
            path.parent.mkdir(parents=True)
            raw = (json.dumps(packet_data, sort_keys=True) + "\n").encode()
            path.write_bytes(raw)
            mutated = notes.Packet(source.path, hashlib.sha256(raw).hexdigest(), source.kind, source.count)
            with self.assertRaisesRegex(ValueError, "paraphrase"):
                notes.compile_notes(root, packets=(mutated,))

    def test_browser_sidecar_remains_isolated(self):
        html = (notes.REPO / "explorer/publisher-guide-notes.html").read_text()
        script = (notes.REPO / "explorer/publisher-guide-notes.js").read_text()
        self.assertIn("HELD · NOT CANONICAL", html)
        self.assertIn("./publisher-guide-notes.json", html)
        self.assertIn('textContent', script)
        self.assertNotIn("innerHTML", script)
        self.assertNotIn("synopsis-catalog.json", script)
        self.assertNotIn("search-catalog.json", script)


if __name__ == "__main__":
    unittest.main()
