"""Synthetic negative and real-proposal contract checks for publisher roster intake."""

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "validate_publisher_episode_roster.py"
PROPOSAL = ROOT / "proposals" / "librarian" / "sfa-publisher-roster-20261102" / "bundle.json"
spec = importlib.util.spec_from_file_location("publisher_roster", TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PublisherRosterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = mod.read_json(ROOT / "registry" / "mission_catalog.json")
        cls.valid = mod.read_json(PROPOSAL)

    def check_rejected(self, change, reason):
        changed = copy.deepcopy(self.valid)
        change(changed)
        with self.assertRaisesRegex(mod.Rejected, reason):
            mod.validate(changed, self.catalog)

    def test_real_sfa_proposal_is_bounded_and_does_not_admit_episodes(self):
        report = mod.validate(copy.deepcopy(self.valid), self.catalog)
        self.assertEqual(report, {"mission_id": "sfa", "listed_slots": 10,
                                  "roster_completeness": "UNRESOLVED", "accepted_effect": "NONE"})
        self.assertEqual([row["episode_number"] for row in self.valid["episode_slots"]], list(range(1, 11)))
        self.assertEqual(self.valid["series_qid_redirect"]["displayed_qid"], "Q117350388")
        self.assertTrue(all(row["canonical_work_id"] is None and row["source_binding_id"] is None
                            for row in self.valid["episode_slots"]))

    def test_cli_readonly_and_deterministic(self):
        before = PROPOSAL.read_bytes()
        first = subprocess.run([sys.executable, str(TOOL), "--input", str(PROPOSAL)],
                               cwd=ROOT, capture_output=True, text=True)
        second = subprocess.run([sys.executable, str(TOOL), "--input", str(PROPOSAL)],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertIn('"accepted_effect": "NONE"', first.stdout)
        self.assertEqual(before, PROPOSAL.read_bytes())

    def test_no_work_status_or_denominator_promotion(self):
        for field in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
            self.check_rejected(lambda x: x.__setitem__(field, "ACCEPTED"), field)
        self.check_rejected(lambda x: x.__setitem__("proposal_status", "ACCEPTED"), "candidate-only")
        self.check_rejected(lambda x: x.__setitem__("roster_completeness", "COMPLETE"), "unresolved")

    def test_no_canonical_ids_or_source_bindings_even_if_row_status_claimed(self):
        self.check_rejected(lambda x: x["episode_slots"][0].__setitem__("canonical_work_id", "w1"), "cannot create Work")
        self.check_rejected(lambda x: x["episode_slots"][0].__setitem__("source_binding_id", "b1"), "cannot create Work")
        self.check_rejected(lambda x: x["episode_slots"][0].__setitem__("status", "ACCEPTED"), "cannot create Work")

    def test_no_fabricated_content_verification_or_page_hash(self):
        self.check_rejected(lambda x: x["observation"].__setitem__("audiovisual_content_inspected", True), "must not claim")
        self.check_rejected(lambda x: x["observation"].__setitem__("response_sha256", "a" * 64), "must not claim")
        self.check_rejected(lambda x: x["observation"].__setitem__("publisher_revision", "2026"), "must not claim")

    def test_observation_date_rejects_future_and_noncanonical_calendar_forms(self):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        self.check_rejected(lambda x: x["observation"].__setitem__("observed_on", tomorrow), "future")
        self.check_rejected(lambda x: x["observation"].__setitem__("observed_on", "9999-12-31"), "future")
        self.check_rejected(lambda x: x["observation"].__setitem__("observed_on", "2026-W44-1"), "canonical")
        self.check_rejected(lambda x: x["observation"].__setitem__("observed_on", "2026-02-30"), "ISO calendar")

    def test_extra_fields_are_rejected_in_every_layer(self):
        self.check_rejected(lambda x: x.__setitem__("episode_count", 10), "roster.*keys")
        self.check_rejected(lambda x: x["episode_slots"][0].__setitem__("narrative", "not safe"), "episode_slots")
        self.check_rejected(lambda x: x["observation"].__setitem__("received_body", "x"), "observation")
        self.check_rejected(lambda x: x["series_qid_redirect"].__setitem__("accepted", True), "redirect")

    def test_slots_do_not_accept_mixed_integer_bool_duplicate_or_reorder(self):
        self.check_rejected(lambda x: x["episode_slots"][0].__setitem__("season", True), "positive")
        self.check_rejected(lambda x: x["episode_slots"][0].__setitem__("episode_number", 0), "positive")
        self.check_rejected(lambda x: x["episode_slots"][1].__setitem__("episode_number", 1), "strictly sorted")
        self.check_rejected(lambda x: x["episode_slots"].reverse(), "strictly sorted")

    def test_ambiguous_duplicate_titles_and_script_markup_rejected(self):
        self.check_rejected(lambda x: x["episode_slots"][1].__setitem__("title", "Kids These Days"), "duplicate publisher")
        self.check_rejected(lambda x: x["episode_slots"][1].__setitem__("title", "<script>x</script>"), "printable")
        self.check_rejected(lambda x: x["episode_slots"][1].__setitem__("title", "injected\nline"), "printable")

    def test_missing_or_extra_slots_cannot_hide_listed_count(self):
        self.check_rejected(lambda x: x["episode_slots"].pop(), "listed slot count")
        self.check_rejected(lambda x: x.__setitem__("listed_slot_count", True), "listed slot count")
        self.check_rejected(lambda x: x.__setitem__("listed_slot_count", 11), "listed slot count")

    def test_mission_unknown_to_catalog_rejected(self):
        self.check_rejected(lambda x: x.__setitem__("mission_id", "fake"), "absent from current catalog")

    def test_unhashable_mission_id_is_controlled_rejection(self):
        self.check_rejected(lambda x: x.__setitem__("mission_id", ["sfa"]), "roster Mission")

    def test_unicode_line_separators_are_not_single_line_titles(self):
        for separator in ("\u2028", "\u2029"):
            self.check_rejected(
                lambda x, separator=separator: x["episode_slots"][0].__setitem__(
                    "title", "First" + separator + "Second"),
                "single-line",
            )

    def test_untrusted_redirect_claims_rejected(self):
        self.check_rejected(lambda x: x["series_qid_redirect"].__setitem__("displayed_qid", "not-qid"), "redirect")
        self.check_rejected(lambda x: x["series_qid_redirect"].__setitem__("verification_status", "AUTHORITATIVE"), "redirect")
        self.check_rejected(lambda x: x["series_qid_redirect"].__setitem__("locator", "https://www.wikidata.org/wiki/Q117350388"), "locator")

    def test_other_series_need_not_invent_a_wikidata_redirect(self):
        changed = copy.deepcopy(self.valid)
        changed["mission_id"] = "tos"
        changed["series_qid_redirect"] = None
        self.assertEqual(mod.validate(changed, self.catalog)["mission_id"], "tos")

    def test_web_locator_requires_https_and_no_tokens_or_loopback(self):
        for value in ("javascript:alert(1)", "http://www.paramountplus.com/episodes/1",
                      "https://user:pass@www.paramountplus.com/episodes/1",
                      "https://www.paramountplus.com/episodes/1?token=x",
                      "https://127.0.0.1/", "https://localhost/", "https://www.paramountplus.com:444/episodes/1",
                      "https://www.paramountplus.com:not-a-port/episodes/1"):
            self.check_rejected(lambda x, value=value: x["observation"].__setitem__("primary_locator", value),
                                "locator|nonpublic")

    def test_two_publisher_pages_count_as_one_independence_group(self):
        self.assertEqual(self.valid["observation"]["independence_group"], "publisher:paramount")
        self.check_rejected(lambda x: x["observation"].__setitem__("independent_sources", 2), "observation")

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "dup.json"
            path.write_text('{"coverage_effect":"NONE","coverage_effect":"ACCEPTED"}', encoding="utf-8")
            with self.assertRaisesRegex(mod.Rejected, "duplicate JSON key"):
                mod.read_json(path)

    def test_symlink_or_oversize_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "real.json"
            path.write_text("{}", encoding="utf-8")
            link = Path(temp) / "link.json"
            link.symlink_to(path)
            with self.assertRaisesRegex(mod.Rejected, "non-symlink"):
                mod.read_json(link)
            oversized = Path(temp) / "large.json"
            oversized.write_bytes(b" " * (mod.MAX_INPUT_BYTES + 1))
            with self.assertRaisesRegex(mod.Rejected, "256 KiB"):
                mod.read_json(oversized)

    def test_fifo_swap_after_stat_is_nonblocking_and_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "in.json"
            path.write_text("{}", encoding="utf-8")
            actual_open = os.open

            def swapped_open(open_path, flags, *args, **kwargs):
                self.assertEqual(Path(open_path), path)
                path.unlink()
                os.mkfifo(path)
                return actual_open(open_path, flags, *args, **kwargs)

            with mock.patch.object(mod.os, "open", side_effect=swapped_open):
                with self.assertRaisesRegex(mod.Rejected, "changed during safe open"):
                    mod.read_json(path)


if __name__ == "__main__":
    unittest.main()
