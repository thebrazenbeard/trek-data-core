"""Fail-closed DS9 S6E6-E15 publisher-card recheck; no Work/coverage effects.

Accepted input hashes attest repository artifact versions only, not a fresh raw
webpage snapshot or the audiovisual work. The publisher is its own source family.
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
EXPECTED = (
    (6, "Sacrifice Of Angels"),
    (7, "You Are Cordially Invited"),
    (8, "Resurrection"),
    (9, "Statistical Probabilities"),
    (10, "The Magnificent Ferengi"),
    (11, "Waltz"),
    (12, "Who Mourns For Morn?"),
    (13, "Far Beyond The Stars"),
    (14, "One Little Ship"),
    (15, "Honor Among Thieves"),
)
TOP_FIELDS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_main_at_selection",
    "observed_utc_date", "source_scope", "publisher_guide_url", "publisher_source_family",
    "source_independence_status", "source_directory_sha256",
    "historical_publisher_csv_sha256", "accepted_b006_source_record_sha256",
    "current_raw_html_sha256", "current_raw_html_captured", "actual_episode_or_script_read",
    "synopsis_policy", "accepted_source_work_effect", "accepted_work_effect",
    "coverage_effect", "public_synopsis_effect", "records",
}
RECORD_FIELDS = {
    "observation_id", "source_local_row_id", "season", "episode", "publisher_card_title",
    "card_locator", "title_slot_status", "synopsis_status", "accepted_work_id",
}


def require(ok, reason):
    if not ok:
        raise ValueError("DS9 B010 invalid: " + reason)


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
        "batch_id": "ds9-s6-middle-b010-20261103",
        "role": "DS9",
        "proposal_only": True,
        "accepted_main_at_selection": "07d0ab4294ede4ff202eb80f4055bc5c676413b2",
        "observed_utc_date": "2026-11-03",
        "source_scope": "PUBLIC_RENDERED_PARAMOUNT_S6_GUIDE_TITLE_SLOT_ONLY",
        "publisher_guide_url": GUIDE,
        "publisher_source_family": "paramount_corporate_publisher_family",
        "source_independence_status": "SAME_FAMILY_RECHECK_NOT_INDEPENDENT_CORROBORATION",
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
    }
    for field, (relative, expected_sha) in paths.items():
        require(data[field] == expected_sha and sha(ROOT / relative) == expected_sha,
                "accepted input drift: " + field)

    earlier = read_json(ROOT / paths["accepted_b006_source_record_sha256"][0])
    require(earlier["role"] == "DS9" and earlier["accepted_work_effect"] == "NONE",
            "prior source-only B006 classification")
    prior_s6 = {
        (r["episode"], r["official_title"])
        for r in earlier["source_local_cards"] if r["season"] == 6
    }
    require(prior_s6 == {(5, "Favor The Bold"), (20, "His Way")},
            "earlier S6 source-card recheck frontier")

    with (ROOT / paths["historical_publisher_csv_sha256"][0]).open(
        encoding="utf-8", newline=""
    ) as stream:
        csv_rows = list(csv.DictReader(stream))
    require(len(csv_rows) == 26, "historical S6 guide row count")
    directory = read_json(ROOT / paths["source_directory_sha256"][0])
    require(directory["data_status"] == "DISCOVERY_ONLY" and directory["row_count"] == 1214,
            "unadmitted directory state and denominator")
    by_id = {r["row_id"]: r for r in directory["rows"]}
    require(len(by_id) == len(directory["rows"]), "duplicate directory IDs")

    records = data["records"]
    require(isinstance(records, list) and len(records) == len(EXPECTED), "ten held S6 cards")
    for index, (record, (episode, title)) in enumerate(zip(records, EXPECTED), 1):
        row_id = f"publisher:s6:ds9:{episode - 1:03d}"
        require(isinstance(record, dict) and set(record) == RECORD_FIELDS,
                "closed source-card schema")
        require(record["observation_id"] == f"ds9-b010-p{index:02d}" and
                record["source_local_row_id"] == row_id, "source-local identity")
        require(record["season"] == 6 and record["episode"] == episode and
                record["publisher_card_title"] == title, "literal guide card title/slot")
        require(record["card_locator"] == f"Season 6 Episode Guide > S6 E{episode} > {title}",
                "current rendered card locator")
        require(record["title_slot_status"] == "SAME_PUBLISHER_RECHECK_MATCH" and
                record["synopsis_status"] == "HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE" and
                record["accepted_work_id"] is None, "no semantic/source promotion")
        require(episode not in {prior for prior, _ in prior_s6},
                "non-overlap with accepted B006 S6 cards")
        require(csv_rows[episode - 1] == {
            "season": "6", "episode_number": str(episode), "title": title,
        }, "historical guide directory consistency")
        prior_directory_row = by_id[row_id]
        require(prior_directory_row["title"] == title and
                prior_directory_row["context"] == f"DS9 S6E{episode}" and
                prior_directory_row["source_locator"] == GUIDE and
                prior_directory_row["identity_scope"] == "SOURCE_LOCAL" and
                prior_directory_row["admission_effect"] == "NONE" and
                prior_directory_row["coverage_effect"] == "NONE",
                "unadmitted source directory row")
    return len(records)


if __name__ == "__main__":
    print(f"DS9_B010_OK: {validate()} held S6E6-E15 source-card observations; "
          "no accepted Work/coverage/synopsis")
