"""Adversarial candidate-only DS9 publisher-card recheck tests."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ds9_s7_recheck_validator", HERE / "validate.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class S7CardRecheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs = mod.read_json(HERE / "observations.json")
        cls.claims = mod.read_json(HERE / "assertions.json")
        cls.directory_raw = mod.read(mod.DIRECTORY_PATH)
        cls.directory = mod.read_json(mod.DIRECTORY_PATH)
        cls.csv_bytes = mod.read(mod.CSV_PATH)
        cls.index = mod.read_json(mod.INDEX_PATH)

    def test_unchanged_source_local_receipt_is_unadmitted(self):
        mod.qualify(self.obs, self.claims, self.directory, self.directory_raw,
                    self.csv_bytes, self.index)
        self.assertEqual(len(self.obs["records"]), 5)
        self.assertEqual(self.obs["coverage_effect"], "NONE")
        self.assertEqual(self.obs["public_synopsis_approval_effect"], "NONE")
        self.assertTrue(all(r["accepted_work_id"] is None for r in self.obs["records"]))

    def reject(self, mutate):
        o, a, d, i = copy.deepcopy((self.obs, self.claims, self.directory, self.index))
        mutation_csv = [self.csv_bytes]
        mutate(o, a, d, i, mutation_csv)
        with self.assertRaises(ValueError):
            mod.qualify(o, a, d, self.directory_raw, mutation_csv[0], i)

    def test_reject_admission_and_false_source_read(self):
        cases = (
            ("accepted_source_work_binding_effect", "SOURCE_BOUND"),
            ("accepted_work_effect", "WORK_ACCEPTED"),
            ("coverage_effect", "CLOSE_READ"),
            ("public_synopsis_approval_effect", "APPROVED"),
            ("fresh_raw_html_bytes_captured", True),
            ("fresh_rendered_page_body_sha256", "f" * 64),
            ("full_episode_or_script_read", True),
        )
        for field, value in cases:
            with self.subTest(field=field):
                self.reject(lambda o, a, d, i, c: o.__setitem__(field, value))

    def test_reject_extra_private_or_copyrighted_payload(self):
        self.reject(lambda o, a, d, i, c: o.__setitem__("admission_status", "ADMITTED"))
        self.reject(lambda o, a, d, i, c: o["records"][0].__setitem__(
            "private_host_path", "D:/VERA/private/video.mkv"))
        self.reject(lambda o, a, d, i, c: o["records"][2].__setitem__(
            "full_script_text", "Fabricated forbidden full source-content slot"))

    def test_reject_source_identity_card_and_editorial_forgery(self):
        cases = (
            (0, "source_local_row_id", "publisher:s7:ds9:000"),
            (0, "historical_csv_episode", 1),
            (1, "fresh_publisher_card_title", "No Such Episode"),
            (2, "fresh_publisher_card_locator", "Episode Guide > wrong edition"),
            (3, "title_slot_observation", "SOURCE_BOUND"),
            (4, "editorial_status", "APPROVED_PUBLIC"),
            (4, "accepted_work_id", "global-ds9-episode-6"),
            (1, "original_description_draft", "Scene directly witnessed in episode."),
        )
        for n, field, value in cases:
            with self.subTest(record=n, field=field):
                self.reject(lambda o, a, d, i, c: o["records"][n].__setitem__(field, value))

    def test_reject_historical_capture_relabeling(self):
        self.reject(lambda o, a, d, i, c: o.__setitem__(
            "historical_20261102_page_capture_sha256", "f" * 64))
        self.reject(lambda o, a, d, i, c: i["source_pages"][1].__setitem__(
            "source_body_bytes", 20))
        self.reject(lambda o, a, d, i, c: c.__setitem__(
            0, c[0].replace(b"Shadows and Symbols", b"Fabricated Publisher Episode")))

    def test_reject_directory_metadata_and_lineage_promotion(self):
        self.reject(lambda o, a, d, i, c: next(x for x in d["rows"] if
                    x["row_id"] == "publisher:s7:ds9:003")
                    .__setitem__("verification_status", "SOURCE_BOUND"))
        self.reject(lambda o, a, d, i, c: o.__setitem__(
            "publisher_independence_group", "independent:second-source"))

    def test_reject_fabricated_accepted_source_assertion(self):
        self.reject(lambda o, a, d, i, c: a.__setitem__("accepted_assertions", 1))
        self.reject(lambda o, a, d, i, c: a["assertions"][0].__setitem__("status", "STABLE"))
        self.reject(lambda o, a, d, i, c: a["assertions"][0].__setitem__(
            "statement", "Page text independently proves all episode story content"))

    def test_reject_duplicate_json_and_symlink_input(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"role":"DS9","role":"ADMIN"}', object_pairs_hook=mod.unique_keys)
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "source.json"
            link = Path(temp) / "link.json"
            target.write_text('{"ok":true}', encoding="utf-8")
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "unsafe or absent input"):
                mod.read(link)

    def test_optimized_mode_rejects_fake_effects(self):
        for field, value in (("coverage_effect", "CLOSE_READ"),
                             ("fresh_raw_html_bytes_captured", True),
                             ("source_content", "copyrighted-full-episode")):
            with self.subTest(field=field):
                tampered = copy.deepcopy(self.obs)
                tampered[field] = value
                code = (
                    f"import json,sys;sys.path.insert(0,{str(HERE)!r});"
                    "from validate import qualify,read_json,read,DIRECTORY_PATH,CSV_PATH,INDEX_PATH,ROOT;"
                    "d=read_json(DIRECTORY_PATH);b=read(DIRECTORY_PATH);c=read(CSV_PATH);"
                    "i=read_json(INDEX_PATH);"
                    "a=read_json(ROOT/'proposals/research/ds9-s7-publisher-card-recheck-20261103/assertions.json');"
                    "qualify(json.load(sys.stdin),a,d,b,c,i)"
                )
                result = subprocess.run([sys.executable, "-O", "-c", code],
                                        input=json.dumps(tampered), text=True,
                                        capture_output=True, check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ValueError", result.stderr)


if __name__ == "__main__":
    unittest.main()
