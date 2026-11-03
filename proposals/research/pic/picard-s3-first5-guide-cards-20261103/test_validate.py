#!/usr/bin/env python3
"""Falsifying cases for Picard S3 guide-only HELD proposal."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import validate as gate


class PicardS3GuideGateTests(unittest.TestCase):
    def setUp(self):
        self.original = gate.load(gate.HERE / "records.json")

    def test_clean(self):
        self.assertEqual(gate.validate(self.original), 5)

    def test_hostile_tampering_fails_closed(self):
        edits = [
            ("coverage false positive", lambda p: p.__setitem__("coverage_effect", "SOURCE_BOUND")),
            ("work admission", lambda p: p.__setitem__("accepted_work_effect", "ADMITTED")),
            ("rights escalation", lambda p: p["source_local_episode_cards"][0].__setitem__("thumbnail_status", "LICENSED_PUBLIC_IMAGE_SET")),
            ("explorer effect", lambda p: p.__setitem__("explorer_effect", "PUBLISH")),
            ("future claimed retrieval", lambda p: p["source"].__setitem__("retrieval_date_utc", "2099-01-01")),
            ("forged source", lambda p: p["source"].__setitem__("url", "https://evil.example/path")),
            ("wrong publisher independence", lambda p: p["source"].__setitem__("independence_group", "third-party:memory-alpha")),
            ("unread AV promoted", lambda p: p["source"].__setitem__("full_primary_audiovisual_content_read", True)),
            ("unretained HTML contradicted", lambda p: p["source"].__setitem__("raw_html_retained_in_public_repo", True)),
            ("fake source receipt", lambda p: p["source"]["raw_sample_receipts"][0].__setitem__("sha256", "0"*64)),
            ("extra row", lambda p: p["source_local_episode_cards"].append(copy.deepcopy(p["source_local_episode_cards"][0]))),
            ("missing row", lambda p: p["source_local_episode_cards"].pop()),
            ("row reorder", lambda p: p["source_local_episode_cards"].reverse()),
            ("false title", lambda p: p["source_local_episode_cards"][0].__setitem__("title", "A Forged Episode")),
            ("false episode number", lambda p: p["source_local_episode_cards"][0].__setitem__("episode_number", 6)),
            ("false description fingerprint", lambda p: p["source_local_episode_cards"][0].__setitem__("description_sha256", "a"*64)),
            ("false description size", lambda p: p["source_local_episode_cards"][0].__setitem__("description_length_utf8_codepoints", 1)),
            ("same-host video cross-row switch", lambda p: p["source_local_episode_cards"][0].__setitem__("video_url", p["source_local_episode_cards"][1]["video_url"])),
            ("same-host image cross-row switch", lambda p: p["source_local_episode_cards"][0].__setitem__("thumbnail_url", p["source_local_episode_cards"][1]["thumbnail_url"])),
            ("paired asset URL rebinding", lambda p: [p["source_local_episode_cards"][0].__setitem__(k, p["source_local_episode_cards"][1][k]) for k in ("video_url", "thumbnail_url")]),
            ("publisher utterance forgery", lambda p: p["source_local_episode_cards"][0]["literal_name_mentions"].__setitem__(0, "False Entity Added")),
            ("synopsis promotion", lambda p: p["source_local_episode_cards"][0].__setitem__("synopsis_state", "VERIFIED_FULL_EPISODE")),
            ("synopsis rewording", lambda p: p["source_local_episode_cards"][0].__setitem__("synopsis_paraphrase_candidate", "This is unsupported.")),
            ("guide claim as AV fact", lambda p: p["source_local_episode_cards"][0].__setitem__("evidence_scope", "FULL_EPISODE_SCENE")),
            ("wrong discovery lineage", lambda p: p["upstream_discovery"].__setitem__("sha256", "e"*64)),
            ("false status bool", lambda p: p["source_local_episode_cards"][0].__setitem__("thumbnail_status", True)),
            ("extra magical field", lambda p: p["source_local_episode_cards"][0].__setitem__("globally_verified", True)),
            ("true-as-one source HTTP", lambda p: p["source"].__setitem__("http_status", True)),
            ("true-as-one season", lambda p: p["source_local_episode_cards"][0].__setitem__("season", True)),
        ]
        for name, change in edits:
            with self.subTest(name=name):
                packet = copy.deepcopy(self.original)
                change(packet)
                with self.assertRaises((ValueError, TypeError)):
                    gate.validate(packet)

    def test_duplicate_json_keys_and_optimized_interpreter(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "forged.json"
            raw = (gate.HERE / "records.json").read_text(encoding="utf-8")
            raw = raw.replace('"coverage_effect": "NONE",', '"coverage_effect": "NONE", "coverage_effect": "ADMITTED",', 1)
            path.write_text(raw, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                gate.load(path)
            path.write_text(json.dumps({**self.original, "coverage_effect": "AUDITED"}), encoding="utf-8")
            for options in ([], ["-O"]):
                p = subprocess.run([sys.executable, *options, str(gate.HERE / "validate.py")], capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stderr)
                # Explicitly validate the hostile packet in both normal and -O mode.
                script = ("import sys; sys.path.insert(0, sys.argv[1]); import validate as v; "
                          "v.validate(v.load(sys.argv[2]))")
                bad = subprocess.run([sys.executable, *options, "-c", script, str(gate.HERE), str(path)], capture_output=True, text=True)
                self.assertNotEqual(bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()
