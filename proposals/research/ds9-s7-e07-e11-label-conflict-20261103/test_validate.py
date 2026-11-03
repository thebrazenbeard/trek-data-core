"""Hostile source-label and nonadmission tests for DS9 S7E7–E11."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ds9_s7_e07_e11_validator", HERE / "validate.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DS9S7LabelGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs = mod.read_json(HERE / "observations.json")
        cls.claims = mod.read_json(HERE / "assertions.json")
        cls.directory_raw = mod.read(mod.DIRECTORY_PATH)
        cls.directory = mod.read_json(mod.DIRECTORY_PATH)
        cls.csv_raw = mod.read(mod.CSV_PATH)
        cls.old_index = mod.read_json(mod.INDEX_PATH)

    def test_unmodified_disputed_candidate_only(self):
        mod.check(self.obs, self.claims, self.directory, self.directory_raw,
                  self.csv_raw, self.old_index)
        rows = self.obs["records"]
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[1]["historical_and_current_paramount_title"], "The Siege of AR-555")
        self.assertIsNone(rows[1]["original_card_description_paraphrase"])
        self.assertEqual([r["editorial_status"] for r in rows].count("PENDING_HUMAN_REVIEW"), 4)
        self.assertEqual(self.obs["coverage_effect"], "NONE")

    def reject(self, mutate):
        obs, claims, directory, old_index = copy.deepcopy(
            (self.obs, self.claims, self.directory, self.old_index))
        raw_csv = [self.csv_raw]
        mutate(obs, claims, directory, old_index, raw_csv)
        with self.assertRaises(ValueError):
            mod.check(obs, claims, directory, self.directory_raw, raw_csv[0], old_index)

    def test_reject_admission_source_read_and_raw_hash(self):
        mutations = (
            ("accepted_source_work_effect", "SOURCE_BOUND"),
            ("coverage_effect", "CLOSE_READ"),
            ("public_synopsis_effect", "APPROVED"),
            ("actual_episode_or_script_content_read", True),
            ("current_publisher_page_raw_sha256", "f" * 64),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                self.reject(lambda o, a, d, i, c: o.__setitem__(field, value))

    def test_reject_unexpected_private_path_and_source_text(self):
        self.reject(lambda o, a, d, i, c: o.__setitem__("admission_status", "ADMITTED"))
        self.reject(lambda o, a, d, i, c: o["records"][0].__setitem__(
            "private_host_path", "D:/VERA/secret.mkv"))
        self.reject(lambda o, a, d, i, c: o["records"][1].__setitem__(
            "complete_transcript", "not-an-actual-transcript"))

    def test_reject_numeric_title_resolution_and_false_synopsis(self):
        cases = (
            (1, "historical_and_current_paramount_title", "The Siege of AR-558"),
            (1, "title_resolution", "EXACT_WITH_HISTORICAL_PUBLISHER_CSV"),
            (1, "original_card_description_paraphrase", "Episode demonstrates a battle."),
            (1, "editorial_status", "APPROVED"),
            (1, "same_family_conflict_sources", []),
            (0, "source_local_row_id", "publisher:s7:ds9:005"),
            (4, "episode", 12),
            (3, "accepted_work_id", "global-ds9-work"),
        )
        for n, field, value in cases:
            with self.subTest(record=n, field=field):
                self.reject(lambda o, a, d, i, c: o["records"][n].__setitem__(field, value))
        self.reject(lambda o, a, d, i, c: o["records"][1]["same_family_conflict_sources"][0]
                    .__setitem__("uri", "https://example.org/false-title"))

    def test_reject_revised_catalog_receipts_and_source_identity(self):
        self.reject(lambda o, a, d, i, c: o.__setitem__(
            "historical_publisher_page_sha256", "f" * 64))
        self.reject(lambda o, a, d, i, c: i["source_pages"][1].__setitem__(
            "source_body_bytes", 14))
        self.reject(lambda o, a, d, i, c: c.__setitem__(
            0, c[0].replace(b"Once More Unto the Breach", b"Fake Episode Title")))
        self.reject(lambda o, a, d, i, c: next(row for row in d["rows"]
                    if row["row_id"] == "publisher:s7:ds9:007")
                    .__setitem__("verification_status", "SOURCE_BOUND"))

    def test_reject_assertion_promotion_or_provenance_collision(self):
        self.reject(lambda o, a, d, i, c: a.__setitem__("accepted_assertions", 1))
        self.reject(lambda o, a, d, i, c: a["assertions"][0].__setitem__("status", "STABLE"))
        self.reject(lambda o, a, d, i, c: a["assertions"][0].__setitem__(
            "claim", "AR-558 is indisputably the only title"))
        self.reject(lambda o, a, d, i, c: o.__setitem__(
            "primary_publisher_family", "independent:source-family"))

    def test_optimized_mode_rejects_source_and_admission_mutations(self):
        cases = (("coverage_effect", "CLOSE_READ"),
                 ("current_publisher_page_raw_sha256", "f" * 64),
                 ("private_host_path", "D:/VERA/private/book.epub"))
        for field, value in cases:
            with self.subTest(field=field):
                tampered = copy.deepcopy(self.obs)
                tampered[field] = value
                code = (
                    f"import sys,json;sys.path.insert(0,{str(HERE)!r});"
                    "from validate import check,read_json,read,CSV_PATH,INDEX_PATH,DIRECTORY_PATH,ROOT;"
                    "c=read(CSV_PATH);i=read_json(INDEX_PATH);d=read_json(DIRECTORY_PATH);b=read(DIRECTORY_PATH);"
                    "a=read_json(ROOT/'proposals/research/ds9-s7-e07-e11-label-conflict-20261103/assertions.json');"
                    "check(json.load(sys.stdin),a,d,b,c,i)"
                )
                p = subprocess.run([sys.executable, "-O", "-c", code], input=json.dumps(tampered),
                                   capture_output=True, text=True, check=False)
                self.assertNotEqual(p.returncode, 0)
                self.assertIn("ValueError", p.stderr)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate key"):
            json.loads('{"role":"DS9","role":"OTHER"}', object_pairs_hook=mod.unique_keys)


if __name__ == "__main__":
    unittest.main()
