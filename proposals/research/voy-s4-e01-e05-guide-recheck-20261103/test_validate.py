"""Hostile mutations must fail with or without Python asserts enabled."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("voy_s4_guide_validator", HERE / "validate.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class GuideRecheckValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads((HERE / "records.json").read_text(encoding="utf-8"), object_pairs_hook=MOD.unique_pairs)

    def test_exact_clean_payload(self):
        MOD.validate(self.base)

    def reject(self, mutate):
        altered = copy.deepcopy(self.base)
        mutate(altered)
        with self.assertRaises(ValueError):
            MOD.validate(altered)

    def test_reject_episode_title_substitution(self):
        self.reject(lambda x: x["local_entities"][0].__setitem__("display_title", "Scorpion, Part 1"))

    def test_reject_wrong_ordinal_and_bool_as_int(self):
        self.reject(lambda x: x["local_entities"][2].__setitem__("display_ordinal", 4))
        self.reject(lambda x: x["local_entities"][2].__setitem__("display_ordinal", True))

    def test_reject_foreign_work_binding(self):
        self.reject(lambda x: x["local_entities"][0].__setitem__("work_id", "voy:s4e01"))

    def test_reject_coverage_or_admission_advance(self):
        self.reject(lambda x: x.__setitem__("admission_effect", "ADMITTED"))
        self.reject(lambda x: x["coverage_update"].__setitem__("close_reads", 1))
        self.reject(lambda x: x["coverage_update"].__setitem__("episodes_discovered_new", 5))

    def test_reject_false_full_source_read_and_custody(self):
        self.reject(lambda x: x.__setitem__("full_episode_or_transcript_read", True))
        self.reject(lambda x: x.__setitem__("raw_source_bytes_newly_custodied", True))
        self.reject(lambda x: x["source"].__setitem__("new_raw_source_sha256", "a" * 64))

    def test_reject_synopsis_release_or_close_read(self):
        self.reject(lambda x: x["local_entities"][1]["synopsis_candidate"].__setitem__("public_release", True))
        self.reject(lambda x: x["local_entities"][1]["synopsis_candidate"].__setitem__("state", "APPROVED"))
        self.reject(lambda x: x["local_entities"][1]["synopsis_candidate"].__setitem__("full_episode_read", True))

    def test_reject_source_lineage_or_other_season(self):
        self.reject(lambda x: x["source"].__setitem__("url", "https://www.paramountplus.com/shows/star_trek_voyager/episodes/5/"))
        self.reject(lambda x: x["source"].__setitem__("lineage_group", "INDEPENDENT_CORROBORATION"))
        self.reject(lambda x: x["source"].__setitem__("existing_repo_csv", "../../etc/passwd"))

    def test_reject_evidence_or_assertion_foreign_key(self):
        self.reject(lambda x: x["evidence"][0].__setitem__("entity_id", "voy-s4e03-paramount-guide-card"))
        self.reject(lambda x: x["assertions"][0].__setitem__("evidence_ids", ["voy-s4e02-guide-heading"]))

    def test_reject_unrecognized_fields(self):
        self.reject(lambda x: x.__setitem__("licensed_cover_url", "https://example.com/cover"))
        self.reject(lambda x: x["local_entities"][0].__setitem__("air_date", "1997-09-03"))

    def test_reject_duplicate_json_keys(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"state":"HELD","state":"ACCEPTED"}', object_pairs_hook=MOD.unique_pairs)

    def test_reject_missing_or_modified_existing_discovery_csv(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / self.base["source"]["existing_repo_csv"]
            target.parent.mkdir(parents=True)
            target.write_text("season,episode_number,title\n4,1,Forged Title\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                MOD.validate(self.base, root=root)


if __name__ == "__main__":
    unittest.main()
