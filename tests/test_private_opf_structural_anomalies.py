"""Synthetic and accepted-derivative adversarial OPF anomaly fixtures."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "proposals/auditor/opf-structural-anomalies-20261103"
SPEC = importlib.util.spec_from_file_location("opf_anomalies", SCOPE / "validate.py")
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class OPFStructuralAnomalyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(mod.DATA.read_text(encoding="utf-8"))
        cls.source = mod.source_rows()

    def test_exact_source_local_receipt_has_no_admission(self):
        mod.validate(self.data, self.source)
        self.assertEqual(self.data["manifest_link_audit"]["uri_resolved_missing_total"], 8)
        self.assertEqual(len(self.data["strict_xml_parser"]["undeclared_dc_namespace_entry_ids"]), 15)

    def test_source_derivative_sha_is_pinned(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = Path(temp)
            path = fake / mod.SOURCE.relative_to(mod.ROOT)
            path.parent.mkdir(parents=True)
            path.write_bytes(mod.SOURCE.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "source digest drift"):
                mod.source_rows(fake)

    def test_unbound_dublin_core_prefix_is_not_silent_truth(self):
        bad = b'<package><metadata><dc:Title>synthetic</dc:Title></metadata></package>'
        with self.assertRaises(ET.ParseError):
            mod.strict_opf_xml(bad)
        self.assertTrue(mod.strict_opf_xml(
            b'<package xmlns:dc="http://purl.org/dc/elements/1.1/"><metadata><dc:Title>synthetic</dc:Title></metadata></package>'
        ))
        with self.assertRaisesRegex(ValueError, "DTD/entities held"):
            mod.strict_opf_xml(b'<!DOCTYPE package [<!ENTITY a "unsafe">]><package/>')

    def test_unescaped_hash_filename_breaks_url_resolution(self):
        opf = "synthetic/volume.opf"
        actual = "synthetic/ds9_(#24)_part1.htm"
        target = mod.uri_member_target(opf, "ds9_(#24)_part1.htm#24)_part1.htm")
        self.assertEqual(target, "synthetic/ds9_(")
        self.assertNotEqual(target, actual)

    def test_literal_percent26_requires_percent_escape_for_url(self):
        opf = "synthetic/book.opf"
        actual = "synthetic/author_%26_friend.htm"
        self.assertEqual(mod.uri_member_target(opf, "author_%26_friend.htm"),
                         "synthetic/author_&_friend.htm")
        self.assertNotEqual(mod.uri_member_target(opf, "author_%26_friend.htm"), actual)
        self.assertEqual(mod.uri_member_target(opf, "author_%2526_friend.htm"), actual)

    def test_unicode_replacement_filename_must_remain_unresolved(self):
        self.assertEqual(mod.original_filename_pairing_state("Search For Spock \ufffd"),
                         "UNRESOLVED_REPLACEMENT_CHARACTER")
        self.assertEqual(mod.original_filename_pairing_state("Search For Spock A"), "CANDIDATE_ONLY")

    def test_admission_and_private_path_injection_fail(self):
        for field, value in (("data_rights", "OWNER"), ("source_work_binding", "VERIFIED"),
                             ("edition_binding", "VERIFIED"), ("work_admission_effect", "ADMITTED"),
                             ("private_member_paths_exported", True), ("external_xml_entities_resolved", True)):
            bad = copy.deepcopy(self.data)
            bad[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.validate(bad, self.source)
        bad = copy.deepcopy(self.data)
        bad["owner_local_path"] = "C:/private/source.zip"
        with self.assertRaisesRegex(ValueError, "unexpected anomaly receipt field"):
            mod.validate(bad, self.source)

    def test_false_coverage_or_wrong_anomaly_ids_fail(self):
        bad = copy.deepcopy(self.data)
        bad["strict_xml_parser"]["undeclared_dc_namespace_entry_ids"][0] = "opf-local:0001"
        with self.assertRaises(ValueError):
            mod.validate(bad, self.source)
        bad = copy.deepcopy(self.data)
        bad["manifest_link_audit"]["uri_resolved_missing_total"] = 3
        with self.assertRaises(ValueError):
            mod.validate(bad, self.source)
        bad = copy.deepcopy(self.data)
        bad["original_lit_stem_encoding_candidate"]["original_to_converted_filename_pairing"] = "VERIFIED"
        with self.assertRaises(ValueError):
            mod.validate(bad, self.source)

    def test_uri_resolution_blocks_unsafe_paths(self):
        for href in ("../../other.xml", "/absolute.xml", "https://example.org/file.xml", "file.xml?token=1", "\\evil"):
            with self.subTest(href=href), self.assertRaises(ValueError):
                mod.uri_member_target("synthetic/book.opf", href)


if __name__ == "__main__":
    unittest.main()
