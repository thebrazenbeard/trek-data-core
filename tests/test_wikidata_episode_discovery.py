"""Offline WDQS episode candidate extraction and fail-closed provenance tests."""

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from import_wikidata_episodes import (  # noqa: E402
    Rejected, build_proposal, load_json, validate_output_path,
)


def entity(qid):
    return {"type": "uri", "value": f"http://www.wikidata.org/entity/{qid}"}


def label(text):
    return {"type": "literal", "xml:lang": "en", "value": text}


def integer(n):
    return {"type": "literal", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "value": str(n)}


def response():
    return {
        "head": {"vars": ["episode", "episodeLabel", "series", "seriesLabel", "seasonNumber", "episodeNumber"]},
        "results": {"bindings": [
            {"episode": entity("Q99"), "episodeLabel": label("Sample B"),
             "series": entity("Q1000"), "seriesLabel": label("Sample Series"),
             "seasonNumber": integer(2), "episodeNumber": integer(7)},
            {"episode": entity("Q42"), "episodeLabel": label("Sample A"),
             "series": entity("Q1000")},
        ]},
    }


def receipt():
    return {
        "source_url": "https://query.wikidata.org/sparql",
        "license": "CC0-1.0",
        "license_url": "https://www.wikidata.org/wiki/Wikidata:Licensing",
        "retrieved_at_epoch": 1793630000,
        "snapshot_id": "offline-test-20261102",
        "query_text": "SELECT ?episode ?episodeLabel ?series WHERE {\n  ?episode ?predicate ?series .\n}",
    }


def build(rows=None, provenance=None):
    return build_proposal(rows if rows is not None else response(),
                          provenance if provenance is not None else receipt(), "a" * 64)


class EpisodeDiscoveryTests(unittest.TestCase):
    def test_valid_rows_canonical_sorted_and_nonadmitted(self):
        result = build()
        self.assertTrue(result["proposal_only"])
        self.assertEqual(result["accepted_work_effect"], "NONE")
        self.assertEqual(result["accepted_source_binding_effect"], "NONE")
        self.assertEqual(result["coverage_effect"], "NONE")
        self.assertEqual([x["episode_qid"] for x in result["candidates"]], ["Q42", "Q99"])
        self.assertEqual([x["status"] for x in result["candidates"]], ["CANDIDATE", "CANDIDATE"])
        self.assertTrue(all(x["canonical_work_id"] is None for x in result["candidates"]))
        self.assertEqual(result["candidates"][1]["season_number"], 2)
        self.assertEqual(result["candidates"][0]["episode_number"], None)

    def test_input_row_order_does_not_change_normalization(self):
        reversed_rows = response()
        reversed_rows["results"]["bindings"].reverse()
        self.assertEqual(build(), build(rows=reversed_rows))

    def test_provenance_contains_retrieval_epoch_license_query_and_input_hash(self):
        out = build()
        self.assertEqual(out["provenance"]["retrieved_at_epoch"], 1793630000)
        self.assertEqual(out["provenance"]["license"], "CC0-1.0")
        self.assertEqual(out["provenance"]["response_sha256"], "a" * 64)
        self.assertEqual(out["provenance"]["query_sha256"], hashlib.sha256(receipt()["query_text"].encode()).hexdigest())
        self.assertEqual(out["provenance"]["provenance_verification"], "USER_SUPPLIED_OFFLINE_EXPORT_NOT_REMOTE_VERIFIED")

    def test_license_and_url_must_be_exact(self):
        for key, value in (("license", "CC-BY-SA-4.0"), ("license_url", "https://example.com"),
                           ("source_url", "http://query.wikidata.org/sparql"),
                           ("source_url", "https://query.wikidata.org/other")):
            changed = receipt()
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(Rejected):
                build(provenance=changed)

    def test_epoch_rejects_string_float_bool_negative_and_out_of_bounds(self):
        for epoch in ("1793630000", 1793630000.0, True, -1, 4102444801):
            changed = receipt()
            changed["retrieved_at_epoch"] = epoch
            with self.subTest(epoch=epoch), self.assertRaises(Rejected):
                build(provenance=changed)

    def test_duplicate_episode_qid_fails_closed(self):
        rows = response()
        rows["results"]["bindings"][1]["episode"] = entity("Q99")
        with self.assertRaises(Rejected):
            build(rows=rows)

    def test_wrong_entity_uri_and_non_english_label_rejected(self):
        changed = response()
        changed["results"]["bindings"][0]["episode"]["value"] = "https://evil.example/entity/Q99"
        with self.assertRaises(Rejected):
            build(rows=changed)
        changed = response()
        changed["results"]["bindings"][0]["episodeLabel"]["xml:lang"] = "fr"
        with self.assertRaises(Rejected):
            build(rows=changed)

    def test_reject_invalid_season_episode_fields(self):
        for value in ("0", "-1", "4.0", "not-a-number", "10000"):
            rows = response()
            rows["results"]["bindings"][0]["seasonNumber"]["value"] = value
            with self.subTest(value=value), self.assertRaises(Rejected):
                build(rows=rows)

    def test_reject_unknown_schema_variables_and_empty_results(self):
        rows = response()
        rows["head"]["vars"].append("canonicalWorkId")
        with self.assertRaises(Rejected):
            build(rows=rows)
        rows = response()
        rows["head"]["vars"].append("episode")
        with self.assertRaises(Rejected):
            build(rows=rows)
        rows = response()
        rows["head"]["vars"].remove("seriesLabel")
        with self.assertRaises(Rejected):
            build(rows=rows)
        rows = response()
        rows["results"]["bindings"] = []
        with self.assertRaises(Rejected):
            build(rows=rows)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(Rejected):
                load_json(path)

    def test_output_must_resolve_inside_proposals(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "proposals").mkdir()
            self.assertEqual(validate_output_path("proposals/batch.json", base), base / "proposals/batch.json")
            for invalid in ("registry/accepted.json", "/tmp/other.json", "proposals/../registry/other.json"):
                with self.subTest(invalid=invalid), self.assertRaises(Rejected):
                    validate_output_path(invalid, base)

    def test_cli_writes_proposal_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "proposals").mkdir()
            raw, rec = base / "data.json", base / "receipt.json"
            raw.write_text(json.dumps(response()), encoding="utf-8")
            rec.write_text(json.dumps(receipt()), encoding="utf-8")
            cmd = [sys.executable, str(ROOT / "tools" / "import_wikidata_episodes.py"),
                   "--input", str(raw), "--receipt", str(rec), "--output", "proposals/episodes.json"]
            first = subprocess.run(cmd, cwd=base, capture_output=True, text=True, check=False)
            self.assertEqual(first.returncode, 0, first.stderr)
            output = base / "proposals" / "episodes.json"
            data = output.read_bytes()
            self.assertEqual(json.loads(data)["candidates"][0]["status"], "CANDIDATE")
            second = subprocess.run(cmd, cwd=base, capture_output=True, text=True, check=False)
            self.assertEqual(second.returncode, 1)
            self.assertEqual(output.read_bytes(), data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
