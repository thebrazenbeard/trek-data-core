"""Negative fixtures for DS9 B006 source-local publisher-card nonadmission."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ds9_b006_validator", HERE / "validate.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class B006PublisherCardGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observations, _ = mod.read_json(HERE / "observations.json")
        cls.assertions, _ = mod.read_json(HERE / "assertions.json")
        cls.catalog, cls.raw = mod.read_json(mod.ROOT / "explorer/discovery-catalog.json")
        cls.b005, _ = mod.read_json(
            mod.ROOT / "proposals/verification/episode-guide-rechecks-b005-20261103/observations.json")

    def test_unchanged_receipt_is_candidate_only(self):
        mod.check(self.catalog, self.raw, self.observations, self.assertions, self.b005)
        self.assertEqual(len(self.observations["source_local_cards"]), 3)
        self.assertEqual([c["title_comparison"] for c in self.observations["source_local_cards"]],
                         ["EXACT_LITERAL", "EXACT_LITERAL", "CASE_VARIANT_UNRESOLVED"])
        self.assertEqual(self.observations["episode_research_coverage_effect"], "NONE")

    def reject(self, mutate):
        catalog, observations, assertions, b005 = copy.deepcopy(
            (self.catalog, self.observations, self.assertions, self.b005))
        mutate(catalog, observations, assertions, b005)
        with self.assertRaises(ValueError):
            mod.check(catalog, self.raw, observations, assertions, b005)

    def test_reject_false_publication_or_source_read(self):
        for field, value in (
            ("synopsis_publication_effect", "APPROVED"),
            ("episode_research_coverage_effect", "CLOSE_READ"),
            ("accepted_source_work_binding_effect", "SOURCE_BOUND"),
            ("raw_publisher_page_bytes_pinned", True),
            ("full_episode_or_script_source_read", True),
        ):
            with self.subTest(field=field):
                self.reject(lambda c, o, a, b: o.__setitem__(field, value))

    def test_reject_unknown_fields_or_private_media(self):
        self.reject(lambda c, o, a, b: o.__setitem__("admission_status", "ADMITTED"))
        self.reject(lambda c, o, a, b: o["source_local_cards"][0].__setitem__(
            "private_host_path", "D:/VERA/private/episode.mp4"))
        self.reject(lambda c, o, a, b: o["source_local_cards"][0].__setitem__(
            "script_text", "Forbidden hypothetical copyrighted source text"))

    def test_reject_title_slot_and_source_lineage_mutations(self):
        mutations = (
            (0, "official_title", "Unrelated Title"),
            (0, "season", 6),
            (1, "episode", 19),
            (2, "title_comparison", "EXACT_LITERAL"),
            (2, "official_title", "Favor the Bold"),
            (2, "publisher_guide_url", "https://example.org/episodes/6/"),
            (0, "seed_external_locator", "https://www.wikidata.org/wiki/Q999999"),
            (1, "publisher_card_locator", "Season 6 Episode Guide > His Way > S6 E19"),
            (1, "synopsis_status", "APPROVED_PUBLIC_SYNOPIS"),
            (1, "accepted_work_id", "global-work-123"),
            (1, "source_body_sha256", "f" * 64),
        )
        for index, key, value in mutations:
            with self.subTest(index=index, key=key):
                self.reject(lambda c, o, a, b: o["source_local_cards"][index].__setitem__(key, value))

    def test_reject_fabricated_story_evidence_and_assertion_promotion(self):
        self.reject(lambda c, o, a, b: o["source_local_cards"][0].__setitem__(
            "original_catalog_description_paraphrase", "The entire episode was personally watched."))
        self.reject(lambda c, o, a, b: a["assertions"][0].__setitem__("status", "STABLE"))
        self.reject(lambda c, o, a, b: a["assertions"][0].__setitem__("statement", "Identical Works confirmed"))

    def test_reject_directory_forgery_and_b005_overlap(self):
        self.reject(lambda c, o, a, b: next(x for x in c["rows"] if x["row_id"] == "lead:0067")
                    .__setitem__("verification_status", "SOURCE_BOUND"))
        self.reject(lambda c, o, a, b: b["rows"].append({"row_id": "lead:0067"}))
        with self.assertRaises(ValueError):
            mod.check(self.catalog, b"wrong input digest", self.observations, self.assertions, self.b005)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"role":"DS9","role":"ADMIN"}', object_pairs_hook=mod.unique_keys)

    def test_optimized_python_still_rejects_mutations(self):
        for field, value in (("synopsis_publication_effect", "APPROVED"),
                             ("full_episode_or_script_source_read", True),
                             ("admission_status", "ADMITTED")):
            with self.subTest(field=field):
                forged = copy.deepcopy(self.observations)
                forged[field] = value
                code = (
                    f"import json,sys;sys.path.insert(0,{str(HERE)!r});"
                    "from validate import read_json,check,ROOT;"
                    "d=json.load(sys.stdin);"
                    "c,raw=read_json(ROOT/'explorer/discovery-catalog.json');"
                    "b,_=read_json(ROOT/'proposals/verification/episode-guide-rechecks-b005-20261103/observations.json');"
                    "a,_=read_json(ROOT/'proposals/research/ds9-publisher-guide-tail-b006-20261103/assertions.json');"
                    "check(c,raw,d,a,b)"
                )
                proc = subprocess.run([sys.executable, "-O", "-c", code],
                                      input=json.dumps(forged), capture_output=True,
                                      text=True, check=False)
                self.assertNotEqual(proc.returncode, 0)
                self.assertIn("ValueError", proc.stderr)


if __name__ == "__main__":
    unittest.main()
