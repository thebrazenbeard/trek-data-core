"""Adversarial checks of source-only provenance and unresolved display dates."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ds9_s7_e12_e16_gate", HERE / "validate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class PublisherDisplayDateVariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observations = gate.read_json(HERE / "observations.json")
        cls.claims = gate.read_json(HERE / "assertions.json")
        cls.directory_bytes = gate.read(gate.DIRECTORY)
        cls.directory = gate.read_json(gate.DIRECTORY)
        cls.csv_bytes = gate.read(gate.CSV)
        cls.index = gate.read_json(gate.INDEX)

    def reject(self, transform):
        o, a, d, i = copy.deepcopy((self.observations, self.claims, self.directory, self.index))
        csv_bytes = [self.csv_bytes]
        directory_bytes = [self.directory_bytes]
        transform(o, a, d, i, csv_bytes, directory_bytes)
        with self.assertRaises(ValueError):
            gate.qualify(o, a, d, directory_bytes[0], csv_bytes[0], i)

    def test_candidate_only_control(self):
        gate.qualify(self.observations, self.claims, self.directory,
                     self.directory_bytes, self.csv_bytes, self.index)
        self.assertEqual(len(self.observations["records"]), 5)
        self.assertTrue(all(x["accepted_work_id"] is None for x in self.observations["records"]))

    def test_reject_any_protected_effect(self):
        for field, value in (("accepted_source_work_effect", "SOURCE_BOUND"),
                             ("coverage_effect", "CLOSE_READ"),
                             ("public_synopsis_effect", "APPROVED"),
                             ("complete_episode_or_script_read", True),
                             ("current_raw_source_html_sha256", "f" * 64),
                             ("proposal_only", False)):
            with self.subTest(field=field):
                self.reject(lambda o, a, d, i, c, z: o.__setitem__(field, value))

    def test_reject_extra_root_or_record_fields(self):
        self.reject(lambda o, a, d, i, c, z: o.__setitem__("admission_status", "ADMITTED"))
        self.reject(lambda o, a, d, i, c, z: o["records"][0].__setitem__(
            "private_host_path", "D:/VERA/private/script.txt"))
        self.reject(lambda o, a, d, i, c, z: o["records"][1].__setitem__(
            "full_script_text", "COPYRIGHTED_SOURCE_CONTENT"))

    def test_reject_schema_and_batch_relabeling(self):
        self.reject(lambda o, a, d, i, c, z: o.__setitem__("schema_version", "9.9.9"))
        self.reject(lambda o, a, d, i, c, z: a.__setitem__("batch_id", "accepted-work"))
        self.reject(lambda o, a, d, i, c, z: o.__setitem__("accepted_main_at_selection", "latest"))

    def test_reject_source_url_and_observation_channel_upgrades(self):
        for field, value in (("official_season_guide_url", "https://memory-alpha.fandom.com/wiki/DS9"),
                             ("official_listing_url", "https://example.com/listing"),
                             ("date_observation_channel", "AUTHENTICATED_RAW_HTML"),
                             ("source_family", "independent:five-sources")):
            with self.subTest(field=field):
                self.reject(lambda o, a, d, i, c, z: o.__setitem__(field, value))

    def test_reject_date_promotion_and_variant_drift(self):
        for index, field, value in ((0, "listing_display_date", "1999-01-03"),
                                    (1, "detail_header_display_date", "1999-02-01"),
                                    (2, "date_resolution", "VERIFIED_AIR_DATE"),
                                    (3, "listing_display_date", "1999-03-01"),
                                    (4, "detail_header_display_date", "1999-03-03")):
            with self.subTest(index=index, field=field):
                self.reject(lambda o, a, d, i, c, z: o["records"][index].__setitem__(field, value))

    def test_reject_title_slot_and_page_locator_forgery(self):
        for index, field, value in ((0, "episode", 6),
                                    (1, "source_local_row_id", "publisher:s7:ds9:999"),
                                    (2, "guide_card_locator", "Search result guessed"),
                                    (3, "observed_publisher_title", "Unknown title"),
                                    (4, "official_detail_url", "https://www.paramountplus.com/shows/video/not-the-page/")):
            with self.subTest(index=index, field=field):
                self.reject(lambda o, a, d, i, c, z: o["records"][index].__setitem__(field, value))

    def test_reject_editorial_and_work_promotion(self):
        self.reject(lambda o, a, d, i, c, z: o["records"][0].__setitem__(
            "editorial_status", "PUBLIC_APPROVED"))
        self.reject(lambda o, a, d, i, c, z: o["records"][2].__setitem__(
            "accepted_work_id", "ds9:7:14"))
        self.reject(lambda o, a, d, i, c, z: o["records"][3].__setitem__(
            "original_description_draft", "Watched the episode myself."))

    def test_reject_historical_receipt_and_catalog_tampering(self):
        self.reject(lambda o, a, d, i, c, z: i["source_pages"][1].__setitem__(
            "listed_slot_count", 99))
        self.reject(lambda o, a, d, i, c, z: o.__setitem__(
            "historical_20261102_html_capture_sha256", "f" * 64))
        self.reject(lambda o, a, d, i, c, z: c.__setitem__(
            0, c[0].replace(b"Field of Fire", b"False Episode")))
        self.reject(lambda o, a, d, i, c, z: next(r for r in d["rows"] if
                    r["row_id"] == "publisher:s7:ds9:011").__setitem__(
                        "verification_status", "SOURCE_BOUND"))

    def test_reject_assertion_reclassification(self):
        self.reject(lambda o, a, d, i, c, z: a.__setitem__("accepted_assertions", 2))
        self.reject(lambda o, a, d, i, c, z: a["assertions"][0].__setitem__(
            "status", "VERIFIED"))
        self.reject(lambda o, a, d, i, c, z: a["assertions"][1].__setitem__(
            "subject_source_family", "independent:multiple"))
        self.reject(lambda o, a, d, i, c, z: a["assertions"][0].__setitem__(
            "evidence_ids", ["unknown"] * 5))
        self.reject(lambda o, a, d, i, c, z: a["assertions"][0].__setitem__(
            "approval", "yes"))

    def test_reject_frozen_prose_rewrite(self):
        self.reject(lambda o, a, d, i, c, z: o["records"][0].__setitem__(
            "original_description_draft", "The publisher describes characters doing something else in this installment."))
        self.reject(lambda o, a, d, i, c, z: a["assertions"][0].__setitem__(
            "claim", "The release dates were confirmed as broadcast dates by an independent source."))

    def test_reject_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"schema_version":"1.0.0","schema_version":"9.9.9"}')
            with self.assertRaises(ValueError):
                gate.read_json(path)

    def test_reject_symlink_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.json"
            link = Path(directory) / "link.json"
            source.write_text(json.dumps({"a": 1}))
            link.symlink_to(source)
            with self.assertRaises(ValueError):
                gate.read_json(link)

    def test_optimized_mode_still_rejects_protected_mutation(self):
        code = """
import importlib.util
from pathlib import Path
p=Path(__import__('sys').argv[1]); s=importlib.util.spec_from_file_location('d',p/'validate.py')
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
o=m.read_json(p/'observations.json'); a=m.read_json(p/'assertions.json')
o['records'][0]['date_resolution']='VERIFIED_AIR_DATE'
try:
    m.qualify(o,a,m.read_json(m.DIRECTORY),m.read(m.DIRECTORY),m.read(m.CSV),m.read_json(m.INDEX))
except ValueError:
    raise SystemExit(0)
raise SystemExit(31)
"""
        result = subprocess.run([sys.executable, "-O", "-c", code, str(HERE)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
