"""Hostile mutations of the public, source-relative LIT proposal."""
import copy
import json
from pathlib import Path
import unittest

from validate import validate


HERE = Path(__file__).resolve().parent
INDEX = json.loads((HERE / "CHAPTER_INDEX.json").read_text("utf-8"))
RECORDS = json.loads((HERE / "records.json").read_text("utf-8"))


class EmissaryProposalTests(unittest.TestCase):
    def test_valid_proposal(self):
        validate(INDEX, RECORDS)

    def bad(self, edit):
        i, r = copy.deepcopy(INDEX), copy.deepcopy(RECORDS)
        edit(i, r)
        with self.assertRaises(ValueError):
            validate(i, r)

    def test_false_accepted_coverage(self):
        self.bad(lambda i, r: r["reading"].update(accepted_coverage_effect="CLOSE_READ"))

    def test_edition_spoof(self):
        self.bad(lambda i, r: r["candidate_work"].update(edition_match="VERIFIED"))

    def test_wrong_archive(self):
        self.bad(lambda i, r: i.update(archive_sha256="0" * 64))

    def test_changed_chapter_digest(self):
        self.bad(lambda i, r: i["chapters"][5].update(segment_sha256="0" * 64))

    def test_wrong_length(self):
        self.bad(lambda i, r: i["chapters"][11].update(char_end_exclusive=363542))

    def test_false_contiguous_index(self):
        self.bad(lambda i, r: i["chapters"][4].update(char_start=0))

    def test_fabricated_locator(self):
        self.bad(lambda i, r: r["evidence"][0]["locator"].update(nonempty_line_zero_based=300))

    def test_cross_reconciled_character(self):
        self.bad(lambda i, r: r["local_entities"][0].update(id="global:ben-sisko"))

    def test_unknown_evidence(self):
        self.bad(lambda i, r: r["assertions"][0]["supported_by"].append("ev-made-up"))

    def test_added_book_text_field(self):
        self.bad(lambda i, r: r["evidence"][0].update(source_excerpt="not permitted"))

    def test_false_private_path(self):
        self.bad(lambda i, r: r.update(private_member_path="ST ebooks txt/example"))

    def test_no_source_interpretation_without_frame(self):
        self.bad(lambda i, r: r["evidence"][0].update(frame=""))

    def test_unknown_counterweight(self):
        self.bad(lambda i, r: r["assertions"][0]["counterweight"].append("made-up"))

    def test_false_relevant_counterweight_with_real_evidence_id(self):
        # A syntactically valid evidence ID is not proof of logical disconfirmation.
        self.bad(lambda i, r: r["assertions"][1]["counterweight"].append("ev-14"))

    def test_false_counterevidence_status(self):
        self.bad(lambda i, r: r["assertions"][2].update(counterevidence_status="NONE_FOUND"))

    def test_silent_counterevidence_status_removal(self):
        self.bad(lambda i, r: r["assertions"][3].pop("counterevidence_status"))

    def test_boolean_position(self):
        self.bad(lambda i, r: i["chapters"][0].update(char_start=False))


if __name__ == "__main__":
    unittest.main()
