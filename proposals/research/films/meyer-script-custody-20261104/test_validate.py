"""Adversarial guards for source/film boundary and mistaken archive item reconciliation."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("meyer_custody_validator", HERE / "validate.py")
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class TestMeyerScriptCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((HERE / "records.json").read_text(encoding="utf-8"))

    def mutate_and_reject(self, mutation):
        candidate = copy.deepcopy(self.original)
        mutation(candidate)
        with self.assertRaises(ValueError):
            validator.validate_records(candidate)

    def test_exact_packet_and_manifest(self):
        validator.validate_files()

    def test_rejects_false_film_close_read(self):
        self.mutate_and_reject(lambda d: d.__setitem__("full_film_viewed", True))

    def test_rejects_false_script_content_read(self):
        self.mutate_and_reject(lambda d: d.__setitem__("release_dialogue_content_read", True))

    def test_rejects_false_source_hash(self):
        self.mutate_and_reject(lambda d: d["sources"][0].__setitem__("content_hash", "f" * 64))

    def test_rejects_forged_source_url(self):
        self.mutate_and_reject(lambda d: d["sources"][0].__setitem__("locator", "https://example.com/fake"))

    def test_rejects_fake_independent_archive_corroboration(self):
        self.mutate_and_reject(lambda d: d["sources"][1].__setitem__("independence_group", "other-archive"))

    def test_rejects_silent_archive_item_merge(self):
        self.mutate_and_reject(lambda d: next(a for a in d["assertions"] if a["assertion_id"] == "meyer-a-current-mixed-title")["object"].__setitem__("identity_with_legacy_draft", "SAME_AS"))

    def test_rejects_silent_box_reconciliation(self):
        self.mutate_and_reject(lambda d: next(e for e in d["evidence"] if e["evidence_id"] == "meyer-e-current-mixed-title")["locator"].__setitem__("listed_box", "48"))

    def test_rejects_narrative_inference(self):
        self.mutate_and_reject(lambda d: d["assertions"][0].__setitem__("predicate", "KIRK_KILLS_KHAN"))

    def test_rejects_promoted_acceptance(self):
        self.mutate_and_reject(lambda d: d["assertions"][0].__setitem__("status", "ACCEPTED"))

    # Independent Auditor wave13, frozen 5486a48: source-specific semantic falsifiers.
    def test_reject_impossible_voyage_home_box(self):
        self.mutate_and_reject(lambda d: d["evidence"][2]["locator"].__setitem__("listed_box", "999"))

    def test_reject_invented_undiscovered_country_script_date(self):
        self.mutate_and_reject(lambda d: d["evidence"][3]["observed"].__setitem__("complete_script_date_as_listed", "2099-01-21"))

    def test_reject_ambiguous_item_work_reclassification_without_reconciliation(self):
        self.mutate_and_reject(lambda d: d["local_entities"][4].__setitem__("work_id", "candidate:film-undiscovered-country"))

    def test_reject_assertion_bound_to_wrong_source_evidence(self):
        self.mutate_and_reject(lambda d: d["assertions"][3].__setitem__("evidence", ["meyer-e-collection-access"]))

    def test_reject_evidence_work_inconsistent_with_local_claim(self):
        self.mutate_and_reject(lambda d: d["evidence"][3].__setitem__("work_id", "candidate:film-wrath-of-khan"))

    def test_rejects_assertion_forged_release_date(self):
        self.mutate_and_reject(lambda d: d["assertions"][1]["object"].__setitem__("date", "2099-05-24"))

    def test_rejects_assertion_forged_box(self):
        self.mutate_and_reject(lambda d: d["assertions"][2]["object"].__setitem__("listed_box", "999"))


if __name__ == "__main__":
    unittest.main()
