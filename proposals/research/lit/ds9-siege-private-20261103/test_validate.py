"""Adversarial public invariants for the private-source literary candidate."""
import copy
import json
from pathlib import Path
import unittest

from validate import validate

HERE = Path(__file__).resolve().parent
INDEX = json.loads((HERE / "CHAPTER_INDEX.json").read_text("utf-8"))
RECORDS = json.loads((HERE / "records.json").read_text("utf-8"))


class SiegeProposalTests(unittest.TestCase):
    def test_valid(self):
        validate(INDEX, RECORDS)

    def rejects(self, change):
        i, r = copy.deepcopy(INDEX), copy.deepcopy(RECORDS)
        change(i, r)
        with self.assertRaises(ValueError):
            validate(i, r)

    def test_wrong_member(self):
        self.rejects(lambda i, r: i.update(source_member_sha256="0" * 64))

    def test_wrong_archive(self):
        self.rejects(lambda i, r: i.update(archive_sha256="0" * 64))

    def test_edition_promotion(self):
        self.rejects(lambda i, r: r["candidate_work"].update(edition_match="VERIFIED"))

    def test_work_binding_promotion(self):
        self.rejects(lambda i, r: r["candidate_work"].update(source_work_binding="ACCEPTED"))

    def test_full_edition_claim(self):
        self.rejects(lambda i, r: r["candidate_work"].update(full_publisher_edition_complete="YES"))

    def test_accepted_coverage(self):
        self.rejects(lambda i, r: r["reading"].update(accepted_coverage_effect="CLOSE_READ"))

    def test_coverage_field_alternative(self):
        self.rejects(lambda i, r: i.update(accepted_work_coverage_effect="CLOSE_READ"))

    def test_wrong_byte_length(self):
        self.rejects(lambda i, r: i.update(source_member_bytes=423374))

    def test_segment_continuity(self):
        self.rejects(lambda i, r: i["chapters"][9].update(char_start=0))

    def test_line_continuity(self):
        self.rejects(lambda i, r: i["chapters"][8].update(nonempty_line_start=0))

    def test_missing_preface_segment(self):
        self.rejects(lambda i, r: i["chapters"].pop(0))

    def test_truncated_source_tail(self):
        self.rejects(lambda i, r: i["chapters"][-1].update(char_end_exclusive=423374))

    def test_fabricated_locator(self):
        self.rejects(lambda i, r: r["evidence"][0]["locator"].update(nonempty_line_zero_based=999))

    def test_negative_chapter(self):
        self.rejects(lambda i, r: r["evidence"][0]["locator"].update(chapter=-1))

    def test_boolean_line_index(self):
        self.rejects(lambda i, r: r["evidence"][0]["locator"].update(nonempty_line_zero_based=False))

    def test_global_entity(self):
        self.rejects(lambda i, r: r["local_entities"][0].update(id="global:odo"))

    def test_unknown_support(self):
        self.rejects(lambda i, r: r["assertions"][0]["supported_by"].append("ev-99"))

    def test_irrelevant_but_valid_counterweight(self):
        # Any valid ev ID is still invalid absent specific disconfirmatory relation.
        self.rejects(lambda i, r: r["assertions"][3]["counterweight"].append("ev-22"))

    def test_fabricated_counterevidence_certainty(self):
        self.rejects(lambda i, r: r["assertions"][0].update(counterevidence_status="NONE_FOUND"))

    def test_missing_unknown_counterevidence(self):
        self.rejects(lambda i, r: r["assertions"][0].pop("counterevidence_status"))

    def test_source_excerpt_leak(self):
        self.rejects(lambda i, r: r["evidence"][0].update(source_excerpt="forbidden"))

    def test_private_path_leak(self):
        self.rejects(lambda i, r: r.update(private_member_path="ST ebooks txt/"))

    def test_missing_narrative_frame(self):
        self.rejects(lambda i, r: r["evidence"][0].update(frame=""))

    def test_false_reconciliation_effect(self):
        self.rejects(lambda i, r: r["reading"].update(global_reconciliation_effect="GLOBAL_ENTITY_LINKED"))

    def test_malformed_segment_digest(self):
        self.rejects(lambda i, r: i["chapters"][0].update(segment_sha256="none"))


if __name__ == "__main__":
    unittest.main()
