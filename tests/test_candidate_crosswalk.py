"""Adversarial tests for offline, candidate-only external crosswalk intake."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from import_candidate_crosswalk import (  # noqa: E402
    AdmissionError, _read_json, build_proposal,
)


HEAD = "a" * 40


def export_rows():
    return {
        "source": {
            "system": "Wikidata",
            "url": "https://query.wikidata.org/sparql",
            "license": "CC0-1.0",
            "license_url": "https://www.wikidata.org/wiki/Wikidata:Licensing",
            "retrieved_at": "2026-11-02T14:00:00Z",
            "snapshot": "WDQS-OFFLINE-EXPORT-20261102",
        },
        "candidates": [
            {"external_id": "Q42", "target_kind": "WORK", "target_id": "TESTWORK-1", "mapping_basis": "manual title and edition review"},
            {"external_id": "Q99", "target_kind": "SOURCE", "target_id": "TESTSRC-1", "mapping_basis": "manual provider identity review"},
        ],
    }


def catalog():
    return {
        "sources": [{"record_type": "source", "source_id": "TESTSRC-1", "status": "ACCEPTED", "fixture_only": False}],
        "works": [{"record_type": "work", "work_id": "TESTWORK-1", "status": "ACCEPTED", "fixture_only": False}],
    }


def build(export=None, registry=None):
    return build_proposal(export if export is not None else export_rows(),
                          registry if registry is not None else catalog(), HEAD,
                          "e" * 64, "f" * 64)


class CandidateCrosswalkTests(unittest.TestCase):
    def test_good_export_is_candidate_only_and_schema_compatible(self):
        proposal = build()
        self.assertIs(proposal["proposal_only"], True)
        self.assertEqual(proposal["accepted_corpus_effect"], "NONE")
        self.assertEqual(proposal["source_provenance"]["license"], "CC0-1.0")
        self.assertEqual(proposal["target_catalog"]["verification"], "LOCAL_INPUT_ONLY_NOT_GITHUB_VERIFIED")
        for row in proposal["records"]:
            self.assertEqual(row["mapping_status"], "CANDIDATE")
            self.assertEqual(row["record_type"], "external_crosswalk")
            self.assertEqual(set(row), {
                "record_type", "crosswalk_id", "target_kind", "target_id", "external_system",
                "external_id", "snapshot", "retrieved_at", "mapping_status",
                "independence_group", "lineage_note", "fixture_only",
            })

    def test_record_order_is_canonical(self):
        initial = build()
        reversed_input = export_rows()
        reversed_input["candidates"].reverse()
        self.assertEqual(initial, build(export=reversed_input))

    def test_license_must_be_explicitly_cc0(self):
        for license_name in ("", "CC-BY-4.0", "UNKNOWN", "Public domain"):
            doc = export_rows()
            doc["source"]["license"] = license_name
            with self.subTest(license_name=license_name), self.assertRaises(AdmissionError):
                build(export=doc)

    def test_license_url_cannot_be_redirected(self):
        doc = export_rows()
        doc["source"]["license_url"] = "https://elsewhere.example/licensing"
        with self.assertRaises(AdmissionError):
            build(export=doc)

    def test_source_url_rejects_insecure_or_foreign_host(self):
        for url in ("http://www.wikidata.org/wiki/Q42", "https://www.wikidata.org.evil.example/wiki/Q42", "https://bad.example/Q42", "https://www.wikidata.org:abc/wiki/Q42"):
            doc = export_rows()
            doc["source"]["url"] = url
            with self.subTest(url=url), self.assertRaises(AdmissionError):
                build(export=doc)

    def test_reject_unknown_or_nonaccepted_target(self):
        for target in ("MISSING", "TESTWORK-FIXTURE"):
            doc = export_rows()
            doc["candidates"][0]["target_id"] = target
            with self.subTest(target=target), self.assertRaises(AdmissionError):
                build(export=doc)
        reg = catalog()
        reg["works"][0]["status"] = "PROPOSED"
        with self.assertRaises(AdmissionError):
            build(registry=reg)

    def test_fixture_accepted_is_not_accepted_state(self):
        reg = catalog()
        reg["works"][0]["fixture_only"] = True
        with self.assertRaises(AdmissionError):
            build(registry=reg)

    def test_duplicate_external_id_fails_closed(self):
        doc = export_rows()
        doc["candidates"][1]["external_id"] = "Q42"
        with self.assertRaises(AdmissionError):
            build(export=doc)

    def test_empty_proposal_is_rejected(self):
        doc = export_rows()
        doc["candidates"] = []
        with self.assertRaises(AdmissionError):
            build(export=doc)

    def test_duplicate_target_fails_closed(self):
        doc = export_rows()
        doc["candidates"].append({
            "external_id": "Q123", "target_kind": "WORK", "target_id": "TESTWORK-1", "mapping_basis": "second proposal",
        })
        with self.assertRaises(AdmissionError):
            build(export=doc)

    def test_bad_qid_and_type_fail_closed(self):
        for qid in ("Q0", "123", "Q1; DROP TABLE", "P42", "Q-12"):
            doc = export_rows()
            doc["candidates"][0]["external_id"] = qid
            with self.subTest(qid=qid), self.assertRaises(AdmissionError):
                build(export=doc)
        doc = export_rows()
        doc["candidates"][0]["target_kind"] = "ENTITY"
        with self.assertRaises(AdmissionError):
            build(export=doc)

    def test_metadata_only_cannot_admit_extra_fields(self):
        doc = export_rows()
        doc["candidates"][0]["mapping_status"] = "ACCEPTED"
        with self.assertRaises(AdmissionError):
            build(export=doc)

    def test_registry_ref_must_be_exact_hex(self):
        with self.assertRaises(AdmissionError):
            build_proposal(export_rows(), catalog(), "main", "e" * 64, "f" * 64)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(AdmissionError):
                _read_json(path)

    def test_cli_writes_once_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            input_path, reg_path, output = base / "input.json", base / "registry.json", base / "out.json"
            input_path.write_text(json.dumps(export_rows()), encoding="utf-8")
            reg_path.write_text(json.dumps(catalog()), encoding="utf-8")
            cmd = [sys.executable, str(ROOT / "tools" / "import_candidate_crosswalk.py"),
                   "--input", str(input_path), "--registry", str(reg_path),
                   "--registry-ref", HEAD, "--output", str(output)]
            first = subprocess.run(cmd, check=False, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            output_bytes = output.read_bytes()
            second = subprocess.run(cmd, check=False, capture_output=True, text=True)
            self.assertEqual(second.returncode, 1)
            self.assertEqual(output.read_bytes(), output_bytes)
            self.assertEqual(json.loads(output_bytes)["records"][0]["mapping_status"], "CANDIDATE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
