"""Hostile, source-bound publication tests for HELD episode guide shelf."""

import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_episode_source_cards as builder
from tools.query_episode_source_cards import query


class EpisodeSourceCardTests(unittest.TestCase):
    def test_compiler_uses_all_four_original_source_validators(self):
        rows, receipts = builder.compile_rows()
        self.assertEqual(len(rows), 20)
        self.assertEqual(len(receipts), 4)
        self.assertEqual(len({r["source_row_sha256"] for r in rows}), 20)
        self.assertEqual({r["series_code"] for r in rows}, {"SNW", "PIC"})
        self.assertEqual({r["publisher_family"] for r in rows}, {"publisher:paramountplus.com"})
        self.assertEqual({r["source_status"] for r in rows}, {"HELD_PUBLISHER_GUIDE_ONLY"})
        self.assertEqual({r["coverage_effect"] for r in rows}, {"NONE"})
        self.assertEqual({r["work_admission_effect"] for r in rows}, {"NONE"})
        for row in rows:
            self.assertIs(row["full_episode_read"], False)
            self.assertNotIn("synopsis", row)
            self.assertNotIn("thumbnail", row)
            self.assertNotIn("video_url", row)
            self.assertEqual(row["artwork_release_effect"], "NONE")
            self.assertEqual(row["synopsis_release_effect"], "NONE")

    def test_exact_public_artifact_and_query_facets(self):
        data = builder.build()
        self.assertEqual((builder.ROOT / builder.OUTPUT).read_bytes(), builder.encode(data))
        self.assertEqual(query(data, "S1E06", "PIC")["matching_count"], 1)
        self.assertEqual(query(data, "Pike", "SNW")["matching_count"], 4)
        self.assertEqual(query(data, "", "PIC")["matching_count"], 10)
        self.assertEqual(query(data, "", "SNW")["matching_count"], 10)
        self.assertEqual(query(data, tag="publisher-utterance:enterprise")["matching_count"], 2)
        self.assertEqual(query(data, status="HELD_PUBLISHER_GUIDE_ONLY")["matching_count"], 20)
        with self.assertRaisesRegex(ValueError, "query too long"):
            query(data, "x" * 161)
        with self.assertRaises(ValueError):
            query(data, series="INCORRECT")
        with self.assertRaises(ValueError):
            query(data, limit=21)

    def test_same_count_public_status_url_and_tags_forgery_rejected(self):
        valid = builder.encode(builder.build())
        reviewed = builder.build()
        for mutator in (
            lambda d: d["rows"][0].__setitem__("source_status", "AUDITED"),
            lambda d: d["rows"][0].__setitem__("coverage_effect", "CLOSE_READ"),
            lambda d: d["rows"][0].__setitem__("publisher_guide_url", "https://www.paramountplus.com/other"),
            lambda d: d["rows"][0]["tags"].append("audited:global-work"),
            lambda d: d["rows"][0].__setitem__("source_row_sha256", "0" * 64),
            lambda d: d["rows"][0].__setitem__("title", "<img src=x onerror=alert(1)>"),
            lambda d: d["rows"].__setitem__(0, copy.deepcopy(d["rows"][1])),
        ):
            data = json.loads(valid)
            mutator(data)
            self.assertNotEqual(builder.encode(data), valid)
            with tempfile.TemporaryDirectory() as temp:
                target = Path(temp) / "explorer" / builder.OUTPUT.name
                target.parent.mkdir()
                target.write_bytes(builder.encode(data))
                with patch.object(builder, "ROOT", Path(temp)), \
                        patch.object(builder, "build", return_value=reviewed), \
                        patch.object(sys, "argv", ["builder", "--check"]):
                    with self.assertRaisesRegex(ValueError, "stale or poisoned"):
                        builder.main()

    def test_same_host_url_swap_even_with_forged_whole_input_sha_fails_code_owned_row_pins(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for _, _, rel, _ in builder.INPUTS:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(builder.ROOT / rel, root / rel)
                shutil.copy2(builder.ROOT / rel.with_name("validate.py"), root / rel.with_name("validate.py"))
            # The PIC original validators need their independently pinned prior discovery inventory.
            prior = Path("proposals/discovery/modern-paramount-season1-20261102/pic-observed-slots.csv")
            (root / prior).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(builder.ROOT / prior, root / prior)
            batch, lane, rel, _ = builder.INPUTS[2]
            source = root / rel
            data = json.loads(source.read_text(encoding="utf-8"))
            self.assertEqual(len(data["works"]), 5)
            # Same publisher host, existing good URLs, same five rows/titles/counts.
            a, b = data["works"][0], data["works"][1]
            a["publisher_video_url"], b["publisher_video_url"] = b["publisher_video_url"], a["publisher_video_url"]
            source.write_bytes(builder.encode(data))
            new_pin = hashlib.sha256(source.read_bytes()).hexdigest()
            inputs = list(builder.INPUTS)
            inputs[2] = (batch, lane, rel, new_pin)
            with patch.object(builder, "ROOT", root), patch.object(builder, "INPUTS", tuple(inputs)):
                # Even after an adversary alters the whole-file SHA expectation,
                # the source-local card digest must detect changed video binding.
                with self.assertRaisesRegex(ValueError, "row digest changed"):
                    builder.compile_rows()

    def test_duplicate_json_keys_rejected_before_original_validator(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, lane, rel, _ = builder.INPUTS[2]
            target = root / rel
            target.parent.mkdir(parents=True)
            source = (builder.ROOT / rel).read_text(encoding="utf-8")
            target.write_text(source.replace('{\n', '{\n  "coverage_effect": "CLOSE_READ",\n', 1), encoding="utf-8")
            shutil.copy2(builder.ROOT / rel.with_name("validate.py"), target.with_name("validate.py"))
            malicious_pin = hashlib.sha256(target.read_bytes()).hexdigest()
            with patch.object(builder, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "duplicate accepted source JSON key"):
                    builder.accepted_source(rel, malicious_pin, lane)


if __name__ == "__main__":
    unittest.main()
