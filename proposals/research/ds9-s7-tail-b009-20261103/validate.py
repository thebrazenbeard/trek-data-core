"""Fail-closed DS9 Season 7 tail metadata recheck; no episode Work admission.

Hashes pin accepted repository inputs, not fresh raw publisher HTML or an AV cut.
The source family can report one streaming slot and a historical two-hour finale
without this worker inventing an additional episode or reconciliation decision.
"""

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GUIDE = "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/"
DIRECTORY_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
CSV_SHA = "1dbfe6a4b6af54a5eb2831108d358c8c3f984346b1b3a79de6301ccf2dc22aea"
EARLIER_SHA = "294f90c60e5a94c6b21998a9b728f1738b42efedcb81c7a962fba456eb7d84b9"
PREVIOUS_SHA = "1d39066d421acff9851778d54ba6ed5f0acbac0e20489a19896c1166a234e1c7"
EXPECTED = (
    (17, "Penumbra"),
    (18, "'Til Death Do Us Part"),
    (19, "Strange Bedfellows"),
    (20, "The Changing Face of Evil"),
    (21, "When It Rains..."),
    (22, "Tacking Into The Wind"),
    (23, "Extreme Measures"),
    (24, "The Dogs of War"),
    (25, "What You Leave Behind"),
)
TOP_FIELDS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_main_at_selection",
    "observed_utc_date", "source_scope", "publisher_guide_url",
    "publisher_source_family", "source_directory_sha256", "historical_publisher_csv_sha256",
    "accepted_s7e7_e11_source_record_sha256", "accepted_s7e12_e16_source_record_sha256",
    "current_raw_html_sha256", "current_raw_html_captured", "actual_episode_or_script_read",
    "synopsis_policy", "accepted_source_work_effect", "accepted_work_effect",
    "coverage_effect", "public_synopsis_effect", "records", "finale_presentation_hold",
}
RECORD_FIELDS = {
    "observation_id", "source_local_row_id", "season", "episode", "publisher_card_title",
    "card_locator", "title_slot_status", "synopsis_status", "accepted_work_id",
}
FINALE_FIELDS = {
    "source_local_row_id", "paramount_guide_single_card_slot", "franchise_history_description",
    "franchise_history_url", "source_relation", "split_episode_or_work_decision",
    "additional_s7e26_inferred",
}


def require(ok, why):
    if not ok:
        raise ValueError("DS9 B009 invalid: " + why)


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
    require(type(data) is dict and set(data) == TOP_FIELDS,
            "top-level closed schema")
    for key, value in {
        "schema_version": "1.0.0",
        "batch_id": "ds9-s7-tail-b009-20261103",
        "role": "DS9",
        "proposal_only": True,
        "accepted_main_at_selection": "5b59deec9cf832ed030f25bd09c6fd7c318efb90",
        "observed_utc_date": "2026-11-03",
        "source_scope": "PUBLIC_RENDERED_PARAMOUNT_S7_GUIDE_TITLE_SLOT_ONLY",
        "publisher_guide_url": GUIDE,
        "publisher_source_family": "paramount_corporate_publisher_family",
        "current_raw_html_sha256": None,
        "current_raw_html_captured": False,
        "actual_episode_or_script_read": False,
        "synopsis_policy": "DESCRIPTION_BLOCKS_VISIBLE_NO_TEXT_OR_PARAPHRASE_STORED",
        "accepted_source_work_effect": "NONE",
        "accepted_work_effect": "NONE",
        "coverage_effect": "NONE",
        "public_synopsis_effect": "NONE",
    }.items():
        require(type(data[key]) is type(value) and data[key] == value,
                "source/admission scope: " + key)

    paths = {
        "source_directory_sha256": ("explorer/discovery-catalog.json", DIRECTORY_SHA),
        "historical_publisher_csv_sha256": (
            "proposals/discovery/publisher-season7-20261102/ds9.csv", CSV_SHA),
        "accepted_s7e7_e11_source_record_sha256": (
            "proposals/research/ds9-s7-e07-e11-label-conflict-20261103/observations.json", EARLIER_SHA),
        "accepted_s7e12_e16_source_record_sha256": (
            "proposals/research/ds9-s7-publisher-cards-b008-20261103/observations.json", PREVIOUS_SHA),
    }
    for field, (relative, expected_sha) in paths.items():
        require(data[field] == expected_sha and sha(ROOT / relative) == expected_sha,
                "accepted input drift: " + field)

    prior_rows = set()
    for relative in (paths["accepted_s7e7_e11_source_record_sha256"][0],
                     paths["accepted_s7e12_e16_source_record_sha256"][0]):
        prior_rows.update(r["source_local_row_id"] for r in read_json(ROOT / relative)["records"])
    require(prior_rows == {f"publisher:s7:ds9:{i:03d}" for i in range(6, 16)},
            "previous accepted source-only S7 frontier")

    with (ROOT / paths["historical_publisher_csv_sha256"][0]).open(
        encoding="utf-8", newline=""
    ) as stream:
        csv_rows = list(csv.DictReader(stream))
    directory = read_json(ROOT / paths["source_directory_sha256"][0])
    require(directory["data_status"] == "DISCOVERY_ONLY" and directory["row_count"] == 1214,
            "unadmitted directory status/denominator")
    by_id = {r["row_id"]: r for r in directory["rows"]}
    require(len(by_id) == len(directory["rows"]), "duplicate accepted directory row")

    records = data["records"]
    require(isinstance(records, list) and len(records) == len(EXPECTED), "nine tail cards")
    for index, (record, (episode, title)) in enumerate(zip(records, EXPECTED), 1):
        row_id = f"publisher:s7:ds9:{episode - 1:03d}"
        require(set(record) == RECORD_FIELDS, "source-card closed schema")
        require(record["observation_id"] == f"ds9-b009-p{index:02d}" and
                record["source_local_row_id"] == row_id, "local observation identity")
        require(type(record["season"]) is int and type(record["episode"]) is int and
                record["season"] == 7 and record["episode"] == episode and
                record["publisher_card_title"] == title, "literal guide card title/slot")
        require(record["card_locator"] == f"Season 7 Episode Guide > S7 E{episode} > {title}",
                "rendered text locator")
        require(record["title_slot_status"] == "SAME_PUBLISHER_RECHECK_MATCH"
                and record["synopsis_status"] == "HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE"
                and record["accepted_work_id"] is None, "title match is not admission")
        require(row_id not in prior_rows, "overlap with accepted source recheck")
        require(csv_rows[episode - 1] == {
            "season": "7", "episode_number": str(episode), "title": title,
        }, "historical publisher CSV source identity")
        accepted_row = by_id[row_id]
        require(accepted_row["title"] == title
                and accepted_row["context"] == f"DS9 S7E{episode}"
                and accepted_row["source_locator"] == GUIDE
                and accepted_row["identity_scope"] == "SOURCE_LOCAL"
                and accepted_row["admission_effect"] == "NONE"
                and accepted_row["coverage_effect"] == "NONE", "directory metadata-only identity")

    finale = data["finale_presentation_hold"]
    require(set(finale) == FINALE_FIELDS, "finale scope schema")
    require(type(finale["additional_s7e26_inferred"]) is bool and finale == {
        "source_local_row_id": "publisher:s7:ds9:024",
        "paramount_guide_single_card_slot": "S7E25",
        "franchise_history_description": "TWO_HOUR_SERIES_FINALE_BROADCAST_CLAIM",
        "franchise_history_url":
            "https://www.startrek.com/news/what-you-leave-behind-aired-18-years-ago-today",
        "source_relation": "SAME_CORPORATE_FAMILY_DIFFERENT_PRESENTATION_CONTEXTS",
        "split_episode_or_work_decision": "UNRESOLVED",
        "additional_s7e26_inferred": False,
    }, "do not infer another finale installment from presentation")
    return len(records)


if __name__ == "__main__":
    print(f"DS9_B009_OK: {validate()} held Paramount S7E17-E25 card observations, "
          "finale edition/part unresolved, no accepted Work/coverage/synopsis")
