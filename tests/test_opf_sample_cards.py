"""Fail-closed held OPF card sample, with no inferred book/Work coverage."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location("opf_sample", ROOT / "tools/build_opf_sample_cards.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)
import query_opf_sample_cards as query  # noqa: E402


class OPFReviewSampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = builder.pinned_source(ROOT)
        cls.sample = builder.build(ROOT)

    def test_exact_deterministic_projection_of_39_literal_source_records(self):
        raw = (ROOT / builder.OUTPUT).read_bytes()
        self.assertEqual(raw, builder.encode(self.sample))
        self.assertEqual(self.sample["selected_rows"], 39)
        self.assertEqual(self.sample["source_observation_count"], 347)
        self.assertIsNone(self.sample["distinct_work_count"])
        self.assertEqual(self.sample["data_rights"], "UNKNOWN")
        self.assertEqual(self.sample["public_explorer_visibility"], "NOT_AUTO_LOADED")
        self.assertEqual(len(self.sample["card_rows"]), 39)
        ids = set()
        for ordinal, card in zip(builder.SAMPLE_ORDINALS, self.sample["card_rows"]):
            record = self.source["rows"][ordinal - 1]
            self.assertNotIn(card["source_local_id"], ids)
            ids.add(card["source_local_id"])
            self.assertEqual(card["source_local_id"], record["source_local_id"])
            self.assertEqual(card["title_as_encoded_in_opf"], record["title"][0])
            self.assertEqual(card["creator_strings_as_encoded_in_opf"], record["creator"])
            self.assertEqual(card["original_opf_xml_sha256"], record["opf_entry_sha256"])
            self.assertEqual(card["source_observation_json_pointer"], f"/rows/{ordinal - 1}")
            self.assertEqual(card["metadata_parse_state"], "PARSED")

    def test_no_admission_cover_release_or_private_paths(self):
        self.assertEqual(self.sample["historical_directory_rows"], 1214)
        self.assertEqual(self.sample["historical_directory_sha256"], builder.BASE_SHA256)
        self.assertEqual(self.sample["work_admission_effect"], "NONE")
        self.assertEqual(self.sample["coverage_effect"], "NONE")
        self.assertEqual(self.sample["artwork_release_effect"], "NONE")
        self.assertEqual(self.sample["full_text_sources_read"], 0)
        public = (ROOT / builder.OUTPUT).read_text(encoding="utf-8")
        for forbidden in ("OneDrive", "C:\\Users", "file://", "OverDriveGUID", "/mnt/c/", "cover.jpg", "ebook_full_text"):
            self.assertNotIn(forbidden, public)
        for card in self.sample["card_rows"]:
            self.assertFalse(card["full_text_read"])
            for key in ("artwork_release", "synopsis_release", "admission_effect", "coverage_effect"):
                self.assertEqual(card[key], "NONE")
            self.assertEqual(card["edition_identity"], "NOT_VERIFIED")
            self.assertEqual(card["source_to_work_binding"], "NOT_VERIFIED")
            self.assertEqual(card["work_identity"], "NOT_RECONCILED")
            self.assertEqual(card["container_or_omnibus_contents"], "NOT_RECONCILED")
            self.assertEqual(card["data_rights"], "UNKNOWN")

    def test_mutated_selected_member_is_rejected_and_unselected_stays_uncounted(self):
        for field, value in (
            ("source_local_id", "opf-local:9999"),
            ("parse_status", "OPF_XML_NAMESPACE_RECOVERED"),
            ("title", []),
            ("title", ["A", "B"]),
            ("creator", []),
            ("opf_entry_sha256", "bad"),
        ):
            changed = copy.deepcopy(self.source)
            changed["rows"][builder.SAMPLE_ORDINALS[0] - 1][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                builder.compile_sample(changed)
        changed = copy.deepcopy(self.source)
        changed["rows"][0]["title"] = ["This is unselected, not a new public Work"]
        self.assertEqual(builder.compile_sample(changed), self.sample)

    def test_byte_tampering_fails_even_if_json_still_well_formed(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = Path(temp)
            (fake / builder.SOURCE).parent.mkdir(parents=True)
            (fake / "explorer").mkdir()
            (fake / builder.SOURCE).write_bytes((ROOT / builder.SOURCE).read_bytes() + b" ")
            (fake / "explorer/discovery-catalog.json").write_bytes((ROOT / "explorer/discovery-catalog.json").read_bytes())
            with self.assertRaisesRegex(ValueError, "derivative changed"):
                builder.pinned_source(fake)
            (fake / builder.SOURCE).write_bytes((ROOT / builder.SOURCE).read_bytes())
            (fake / "explorer/discovery-catalog.json").write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError, "historic 1214-row"):
                builder.pinned_source(fake)

    def test_safeguard_original_byte_pins(self):
        for path, expected in ((ROOT / builder.SOURCE, builder.SOURCE_SHA256),
                               (ROOT / "explorer/discovery-catalog.json", builder.BASE_SHA256)):
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_bounded_source_local_query_and_pagination(self):
        rows = query.validated_cards(ROOT)
        self.assertEqual(len(rows), 39)
        result = query.search(rows, query="Spock")
        self.assertEqual(result["total_matches"], 1)
        self.assertEqual(result["rows"][0]["source_local_id"], "opf-local:0236")
        direct = query.search(rows, source_id="opf-local:0295")
        self.assertEqual(direct["total_matches"], 1)
        self.assertEqual(direct["rows"][0]["title_as_encoded_in_opf"],
                         "Star Trek - DS9 - Invasion! 3 - Time's Enemy")
        page = query.search(rows, offset=38, limit=1)
        self.assertEqual(len(page["rows"]), 1)
        self.assertIsNone(page["next_offset"])
        self.assertIsNone(result["distinct_works"])
        for params in ({"query": "X" * 161}, {"source_id": "Z" * 31},
                       {"offset": -1}, {"limit": 0}, {"limit": 51}):
            with self.subTest(params=params), self.assertRaises(ValueError):
                query.search(rows, **params)

    def test_query_rejects_tampered_held_file(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = Path(temp)
            (fake / builder.SOURCE).parent.mkdir(parents=True)
            (fake / "explorer").mkdir()
            (fake / builder.OUTPUT).parent.mkdir(parents=True)
            (fake / builder.SOURCE).write_bytes((ROOT / builder.SOURCE).read_bytes())
            (fake / "explorer/discovery-catalog.json").write_bytes((ROOT / "explorer/discovery-catalog.json").read_bytes())
            forged = copy.deepcopy(self.sample)
            forged["card_rows"][0]["title_as_encoded_in_opf"] = "Invented Work"
            (fake / builder.OUTPUT).write_bytes(builder.encode(forged))
            with self.assertRaisesRegex(ValueError, "exact pinned"):
                query.validated_cards(fake)


if __name__ == "__main__":
    unittest.main()
