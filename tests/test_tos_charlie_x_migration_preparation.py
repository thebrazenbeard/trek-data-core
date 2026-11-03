"""Reject false promotion, broken references, or altered Charlie X legacy input."""

import copy
import runpy
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "proposals/migration/charlie-x-schema-prep-20261103/prepare.py"
ns = runpy.run_path(str(SCRIPT))
prepare = ns["prepare"]
load = prepare.__globals__["load"]


class CharlieXMigrationPreparation(unittest.TestCase):
    def test_all_records_remain_proposed_and_source_relative(self):
        result = prepare()
        self.assertEqual(result["admission_status"], "NOT_ADMITTED")
        self.assertEqual(result["accepted_coverage_events"], 0)
        self.assertIsNone(result["canonical_source_id"])
        self.assertIsNone(result["canonical_work_id"])
        self.assertEqual((len(result["local_entities"]), len(result["evidence"]), len(result["assertions"])), (20, 14, 7))
        self.assertTrue(all(e["frame"] == "DERIVATIVE_TRANSCRIPT_ONLY_NOT_AUTHENTICATED_AV" for e in result["evidence"]))
        self.assertTrue(all(e["evidence_kind"] == "other" and e["epistemic_status"] == "UNKNOWN" for e in result["evidence"]))
        self.assertTrue(all(a["status"] == "PROPOSED" for a in result["assertions"]))
        self.assertTrue(all(e["locator"]["rendered_text_sha256"] == "0e033f6883644602b7a941619f4f895e3780feffdc92e2a3a20f0e295721e849" for e in result["evidence"]))

    def test_schema_required_shape_without_implying_admission(self):
        result = prepare()
        for section, schema_name in (("local_entities", "local-entity"), ("evidence", "evidence"), ("assertions", "assertion")):
            import json
            schema = json.loads((ROOT / f"schema/{schema_name}.schema.json").read_text(encoding="utf-8"))
            for row in result[section]:
                self.assertTrue(set(schema["required"]) <= row.keys())
                self.assertEqual(row["record_type"], schema["properties"]["record_type"]["const"])
                for key, rule in schema["properties"].items():
                    if "enum" in rule and key in row:
                        self.assertIn(row[key], rule["enum"])

    def test_mutations_fail_closed(self):
        scenarios = (
            ("MANIFEST.json", ("source", "private_source_custody"), "DURABLE_AUTHENTICATED_SOURCE"),
            ("MANIFEST.json", ("records", "coverage_events"), 1),
            ("MANIFEST.json", ("source", "authenticated_primary_av_or_studio_script"), True),
            ("MANIFEST.json", ("source", "rendered_text_sha256"), "0" * 64),
            ("MANIFEST.json", ("source", "raw_html_sha256"), "0" * 64),
            ("MANIFEST.json", ("source", "url"), "https://example.invalid/fake"),
            ("MANIFEST.json", ("source", "rendered_text_numbered_lines"), 832),
            ("MANIFEST.json", ("work", "official_publisher_rendered_heading"), "S1 E2: Charlie X"),
            ("MANIFEST.json", ("source", "upstream_self_report", "independent_transcript_corroboration_count"), 1),
            ("MANIFEST.json", ("files_sha256", "evidence.json"), "0" * 64),
            ("local_entities.json", ("entities", 0, "id"), "charlie"),
            ("evidence.json", ("evidence", 0, "start_line"), 0),
            ("evidence.json", ("evidence", 0, "local_entity_ids", 0), "global-data-id"),
            ("assertions.json", ("assertions", 0, "status"), "ACCEPTED"),
            ("assertions.json", ("assertions", 0, "evidence", 0), "missing-evidence"),
            ("assertions.json", ("assertions", 0, "subject"), "global-charlie"),
        )
        for name, path, value in scenarios:
            originals = {n: copy.deepcopy(load(n)) for n in ("MANIFEST.json", "local_entities.json", "evidence.json", "assertions.json")}
            target = originals[name]
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = value
            prepare.__globals__["load"] = originals.__getitem__
            try:
                with self.subTest(name=name, path=path):
                    with self.assertRaises(ValueError):
                        prepare()
            finally:
                prepare.__globals__["load"] = load


if __name__ == "__main__":
    unittest.main()

