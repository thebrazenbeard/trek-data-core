"""Archival TOS script leads must remain source-relative and unadmitted."""

from __future__ import annotations

import json
from pathlib import Path
import unittest
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "proposals/research/tos-script-archive-locators-20261103"
PRIOR = ROOT / "proposals/librarian/lead-qualification-tos-s1-20261103/selection.json"


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)


def validate_observations(observations: dict, selection: dict) -> None:
    if observations["role"] != "TOS" or observations["status"] != "PROPOSAL_ONLY_ARCHIVAL_CATALOG_METADATA":
        raise ValueError("wrong role or metadata-only status")
    if observations["observation_date_utc"] != "2026-11-03":
        raise ValueError("unexpected observation date")
    if observations["baseline_accepted_main"] != "5127598af7e7c9a1148b11bb15863643f2914dfc":
        raise ValueError("not anchored to exact accepted main")
    if observations["publisher_comparison"]["relative_input"] != str(PRIOR.relative_to(ROOT)):
        raise ValueError("publisher comparison not linked to prior accepted artifact")
    institutional = observations["institutional_source"]
    if institutional["locator"] != "https://iucat.iu.edu/lilly/19297540" or institutional["call_number"] != "PN6120.S48 S795":
        raise ValueError("unexpected physical archive locator")
    if institutional["raw_html_bytes_captured"] is not False or institutional["raw_html_sha256"] is not None or institutional["script_pages_read"] is not False:
        raise ValueError("script read/capture falsely asserted")

    # Expected archival catalog item ordinals and title-credited authors are
    # independently transcribed from Lilly's itemized online catalog. These
    # are library numbering, not Paramount+ episode ordinals.
    expected_scripts = {
        "The Man Trap": (1, "written by George Clayton Johnson"),
        "The Corbomite Maneuver": (10, "written by Jerry Sohl"),
        "The Devil in the Dark": (25, "written by Gene L. Coon"),
        "The Conscience of the King": (13, "written by Barry Trivers"),
        "The Naked Time": (4, "written by John D. F. Black"),
    }
    selected = {x["publisher_rendered_heading_locator"].split(" / ")[1]: x
                for x in selection["selected"]}
    if set(selected) != set(expected_scripts):
        raise ValueError("prior librarian selection changed")
    rows = observations["script_locator_candidates"]
    if type(rows) is not list or len(rows) != len(expected_scripts):
        raise ValueError("wrong source-relative catalog count")
    if {row["work_title_string"] for row in rows} != set(expected_scripts):
        raise ValueError("missing or duplicate work title")
    seen_script_numbers: set[int] = set()
    for row in rows:
        title = row["work_title_string"]
        selected_row = selected[title]
        num, credit = expected_scripts[title]
        if row["archive_script_list_number"] != num or row["archive_catalog_writer_credit"] != credit:
            raise ValueError("archive script ordinal or writer credit changed")
        if type(row["archive_script_list_number"]) is not int or num in seen_script_numbers:
            raise ValueError("duplicate/invalid archive script number")
        if (row["publisher_crosswalk_qid"] != selected_row["qid"]
                or row["publisher_episode_number"] != selected_row["publisher_episode_number"]
                or row["publisher_season"] != selected_row["season"]):
            raise ValueError("Paramount+ reference silently remapped")
        if row["script_revision_verification"] != "NOT_READ" or row["screen_version_match"] != "UNVERIFIED":
            raise ValueError("source script promoted without a read")
        seen_script_numbers.add(num)

    leads = observations["archive_collection_leads"]
    if type(leads) is not list or len(leads) != 3:
        raise ValueError("expected three separately held archive leads")
    expected_hosts = {"archives.lib.ku.edu", "libraryguides.fullerton.edu", "www.wgfoundation.org"}
    observed_hosts = {urlsplit(lead["locator"]).hostname for lead in leads}
    if observed_hosts != expected_hosts or len({lead["source_independence_group"] for lead in leads}) != 3:
        raise ValueError("unexpected archive lead or source independence grouping")
    for lead in leads:
        if lead["episode_level_holdings_verified"] is not False:
            raise ValueError("false exact-episode holdings claim")
    expected_effect = {"local_entities": 0, "episode_evidence": 0, "episode_assertions": 0,
                       "accepted_briefings": 0, "coverage_events": 0, "global_reconciliations": 0}
    if observations["research_records_generated"] != expected_effect:
        raise ValueError("archive metadata must not raise accepted coverage")


class TOSScriptArchiveLocatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.observations = read_json(BATCH / "observations.json")
        self.selection = read_json(PRIOR)

    def test_source_relative_archive_catalog(self) -> None:
        validate_observations(self.observations, self.selection)

    def test_rejects_publisher_archive_ordinal_swap(self) -> None:
        self.observations["script_locator_candidates"][0]["archive_script_list_number"] = 2
        with self.assertRaisesRegex(ValueError, "ordinal"):
            validate_observations(self.observations, self.selection)

    def test_rejects_promotion_without_source_read(self) -> None:
        self.observations["research_records_generated"]["episode_assertions"] = 1
        with self.assertRaisesRegex(ValueError, "coverage"):
            validate_observations(self.observations, self.selection)

    def test_rejects_unqualified_archival_full_read(self) -> None:
        self.observations["institutional_source"]["script_pages_read"] = True
        with self.assertRaisesRegex(ValueError, "falsely"):
            validate_observations(self.observations, self.selection)

    def test_rejects_unverified_collection_exact_holdings(self) -> None:
        self.observations["archive_collection_leads"][0]["episode_level_holdings_verified"] = True
        with self.assertRaisesRegex(ValueError, "false exact"):
            validate_observations(self.observations, self.selection)


if __name__ == "__main__":
    unittest.main()
