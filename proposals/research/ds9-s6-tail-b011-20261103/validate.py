"""Fail-closed DS9 S6E16–25 publisher-card recheck, excluding accepted S6E20.

This pins existing repository source candidate artifacts, not the current page's
raw HTML, a broadcast edition, a full script, or a governed Source↔Work match.
"""

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GUIDE = "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/6/"
DIRECTORY_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
CSV_SHA = "328e2df32a5492249a756a23a22eb641d135877cfca930ffc444b005c04b9ef8"
PRIOR_SHA = "12bacfb550e3b52ce8e14c591bcc7e258f59e1544bf28fa010ce249f60c96a08"
PREVIOUS_SHA = "98701739ef225d6b36d2c17ecc057dd1a94b8987e1c58f277bde5851a543d1d5"
EXPECTED = (
    (16, "Change Of Heart"),
    (17, "Wrongs Darker Than Death Or Night"),
    (18, "Inquisition"),
    (19, "In The Pale Moonlight"),
    (21, "The Reckoning"),
    (22, "Valiant"),
    (23, "Profit And Lace"),
    (24, "Time's Orphan"),
    (25, "The Sound of Her Voice"),
)
TOP_FIELDS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_main_at_selection",
    "observed_utc_date", "source_scope", "publisher_guide_url", "publisher_source_family",
    "source_independence_status", "guide_presentation_scope", "source_directory_sha256",
    "historical_publisher_csv_sha256", "accepted_b006_source_record_sha256",
    "accepted_b010_source_record_sha256",
    "current_raw_html_sha256", "current_raw_html_captured", "actual_episode_or_script_read",
    "synopsis_policy", "accepted_source_work_effect", "accepted_work_effect",
    "coverage_effect", "public_synopsis_effect", "excluded_prior_accepted_card", "records",
}
RECORD_FIELDS = {
    "observation_id", "source_local_row_id", "season", "episode", "publisher_card_title",
    "card_locator", "title_slot_status", "synopsis_status", "accepted_work_id",
}
EXCLUDED_FIELDS = {
    "omitted_episode", "publisher_row_id", "publisher_card_title", "prior_accepted_seed_row_id",
    "identity_relation", "exclusion_reason",
}


def require(ok, reason):
    if not ok:
        raise ValueError("DS9 B011 invalid: " + reason)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data=None):
    if data is None:
        data = read_json(HERE / "observations.json")
    require(isinstance(data, dict) and set(data) == TOP_FIELDS, "closed top-level schema")
    expected_fields = {
        "schema_version": "1.0.0",
        "batch_id": "ds9-s6-tail-b011-20261103",
        "role": "DS9",
        "proposal_only": True,
        "accepted_main_at_selection": "96fbfe270d249e6c3ba04e3aa49b40ed7b508caf",
        "observed_utc_date": "2026-11-03",
        "source_scope": "PUBLIC_RENDERED_PARAMOUNT_S6_GUIDE_TITLE_SLOT_ONLY",
        "publisher_guide_url": GUIDE,
        "publisher_source_family": "paramount_corporate_publisher_family",
        "source_independence_status": "SAME_FAMILY_RECHECK_NOT_INDEPENDENT_CORROBORATION",
        "guide_presentation_scope": "ONE_RENDERED_CARD_PER_LISTED_SLOT_NO_BROADCAST_CUT_INFERENCE",
        "current_raw_html_sha256": None,
        "current_raw_html_captured": False,
        "actual_episode_or_script_read": False,
        "synopsis_policy": "DESCRIPTION_BLOCKS_VISIBLE_NO_TEXT_OR_PARAPHRASE_STORED",
        "accepted_source_work_effect": "NONE",
        "accepted_work_effect": "NONE",
        "coverage_effect": "NONE",
        "public_synopsis_effect": "NONE",
    }
    for field, expected in expected_fields.items():
        require(type(data[field]) is type(expected) and data[field] == expected,
                "publisher/proposal/admission scope and type: " + field)

    paths = {
        "source_directory_sha256": ("explorer/discovery-catalog.json", DIRECTORY_SHA),
        "historical_publisher_csv_sha256": (
            "proposals/discovery/publisher-season6-20261102/ds9.csv", CSV_SHA),
        "accepted_b006_source_record_sha256": (
            "proposals/research/ds9-publisher-guide-tail-b006-20261103/observations.json",
            PRIOR_SHA),
        "accepted_b010_source_record_sha256": (
            "proposals/research/ds9-s6-middle-b010-20261103/observations.json",
            PREVIOUS_SHA),
    }
    for field, (relative, expected_sha) in paths.items():
        require(data[field] == expected_sha and sha(ROOT / relative) == expected_sha,
                "accepted input drift: " + field)

    earlier = read_json(ROOT / paths["accepted_b006_source_record_sha256"][0])
    require(earlier["role"] == "DS9" and earlier["accepted_work_effect"] == "NONE",
            "prior source-only B006 classification")
    prior_s6 = {
        (r["episode"], r["official_title"], r["source_local_row_id"])
        for r in earlier["source_local_cards"] if r["season"] == 6
    }
    require(prior_s6 == {(5, "Favor The Bold", "lead:0069"), (20, "His Way", "lead:0068")},
            "accepted B006 Season 6 source-card frontier")

    accepted_b010 = read_json(ROOT / paths["accepted_b010_source_record_sha256"][0])
    require(accepted_b010["role"] == "DS9" and accepted_b010["coverage_effect"] == "NONE"
            and accepted_b010["accepted_work_effect"] == "NONE",
            "accepted B010 source-only classification")
    prior_b010 = {r["source_local_row_id"] for r in accepted_b010["records"]}
    require(prior_b010 == {f"publisher:s6:ds9:{i:03d}" for i in range(5, 15)},
            "accepted S6E6-E15 source-card row frontier")

    excluded = data["excluded_prior_accepted_card"]
    require(isinstance(excluded, dict) and set(excluded) == EXCLUDED_FIELDS,
            "closed excluded-card schema")
    require(excluded == {
        "omitted_episode": 20,
        "publisher_row_id": "publisher:s6:ds9:019",
        "publisher_card_title": "His Way",
        "prior_accepted_seed_row_id": "lead:0068",
        "identity_relation": "TITLE_SLOT_SOURCE_COMPARISON_ONLY_NOT_GLOBAL_SAME_AS",
        "exclusion_reason": "PREVIOUSLY_SOURCE_RECHECKED_IN_ACCEPTED_B006",
    }, "E20 exclusion and non-reconciliation hold")

    with (ROOT / paths["historical_publisher_csv_sha256"][0]).open(
        encoding="utf-8", newline=""
    ) as stream:
        csv_rows = list(csv.DictReader(stream))
    require(len(csv_rows) == 26, "historical S6 publisher guide row count")
    directory = read_json(ROOT / paths["source_directory_sha256"][0])
    require(directory["data_status"] == "DISCOVERY_ONLY" and directory["row_count"] == 1214,
            "unadmitted directory state and denominator")
    by_id = {r["row_id"]: r for r in directory["rows"]}
    require(len(by_id) == len(directory["rows"]), "duplicate directory IDs")

    records = data["records"]
    require(isinstance(records, list) and len(records) == len(EXPECTED), "nine held S6 cards")
    for index, (record, (episode, title)) in enumerate(zip(records, EXPECTED), 1):
        row_id = f"publisher:s6:ds9:{episode - 1:03d}"
        require(isinstance(record, dict) and set(record) == RECORD_FIELDS,
                "closed source-card schema")
        require(record["observation_id"] == f"ds9-b011-p{index:02d}" and
                record["source_local_row_id"] == row_id, "source-local observation identity")
        require(record["season"] == 6 and record["episode"] == episode and
                record["publisher_card_title"] == title, "literal guide card title/slot")
        require(record["card_locator"] == f"Season 6 Episode Guide > S6 E{episode} > {title}",
                "rendered publisher card locator")
        require(record["title_slot_status"] == "SAME_PUBLISHER_RECHECK_MATCH" and
                record["synopsis_status"] == "HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE" and
                record["accepted_work_id"] is None, "no source/semantic promotion")
        require(episode not in {prior for prior, _, _ in prior_s6},
                "nonduplication with accepted B006 S6 cards")
        require(row_id not in prior_b010, "nonduplication with accepted B010 S6 cards")
        require(csv_rows[episode - 1] == {
            "season": "6", "episode_number": str(episode), "title": title,
        }, "historical publisher CSV consistency")
        existing = by_id[row_id]
        require(existing["title"] == title and existing["context"] == f"DS9 S6E{episode}" and
                existing["source_locator"] == GUIDE and
                existing["identity_scope"] == "SOURCE_LOCAL" and
                existing["admission_effect"] == "NONE" and
                existing["coverage_effect"] == "NONE", "unadmitted source directory row")
    return len(records)


if __name__ == "__main__":
    print(f"DS9_B011_OK: {validate()} held S6E16-E25 source-card observations, "
          "E20 excluded as prior accepted source recheck; no Work/coverage/synopsis")
