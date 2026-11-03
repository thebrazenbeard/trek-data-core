"""Fail-closed DS9 S6 E1–E4/E26 source-card recheck; not episode research."""

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GUIDE = "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/6/"
DIRECTORY_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
CSV_SHA = "328e2df32a5492249a756a23a22eb641d135877cfca930ffc444b005c04b9ef8"
B006_SHA = "12bacfb550e3b52ce8e14c591bcc7e258f59e1544bf28fa010ce249f60c96a08"
B010_SHA = "98701739ef225d6b36d2c17ecc057dd1a94b8987e1c58f277bde5851a543d1d5"
B011_SHA = "2641a978cad2dced4f742af1ecda6508ef3ff643d681a220b8fe1c3beb9054c2"
EXPECTED = (
    (1, "A Time To Stand", "The publisher describes Sisko's crew undertaking a covert mission aboard a captured Jem'Hadar vessel."),
    (2, "Rocks And Shoals", "The publisher places Sisko's team on an isolated world alongside a dying Vorta and a small Jem'Hadar contingent."),
    (3, "Sons And Daughters", "The publisher frames Worf's estrangement from his son as a problem when the younger Klingon joins a ship's crew."),
    (4, "Behind The Lines", "The publisher contrasts Sisko's reassignment away from the Defiant with a loyalty challenge involving Odo and another shapeshifter."),
    (26, "Tears Of The Prophets", "The publisher describes Sisko leading an incursion into Dominion territory in spite of warnings from the Prophets."),
)
TOP_FIELDS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_main_at_selection",
    "observed_utc_date", "source_scope", "publisher_guide_url", "publisher_source_family",
    "source_independence_status", "source_directory_sha256", "historical_publisher_csv_sha256",
    "accepted_b006_source_record_sha256", "accepted_b010_source_record_sha256",
    "accepted_b011_source_record_sha256", "current_raw_html_sha256", "current_raw_html_captured",
    "actual_episode_or_script_read", "synopsis_policy", "accepted_source_work_effect",
    "accepted_work_effect", "coverage_effect", "public_synopsis_effect", "records",
}
RECORD_FIELDS = {
    "observation_id", "source_local_row_id", "season", "episode", "publisher_card_title",
    "card_locator", "description_block_read", "publisher_claim_paraphrase_draft",
    "title_slot_status", "synopsis_status", "accepted_work_id",
}


def require(condition, detail):
    if not condition:
        raise ValueError("DS9 B012 invalid: " + detail)


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
    fixed = {
        "schema_version": "1.0.0",
        "batch_id": "ds9-s6-gaps-b012-20261103",
        "role": "DS9",
        "proposal_only": True,
        "accepted_main_at_selection": "f4ea65391cf1543a55bf19dfcf3ed776dd80ab04",
        "observed_utc_date": "2026-11-03",
        "source_scope": "PUBLIC_RENDERED_PARAMOUNT_S6_GUIDE_CARDS",
        "publisher_guide_url": GUIDE,
        "publisher_source_family": "paramount_corporate_publisher_family",
        "source_independence_status": "SAME_FAMILY_RECHECK_NOT_INDEPENDENT_CORROBORATION",
        "current_raw_html_sha256": None,
        "current_raw_html_captured": False,
        "actual_episode_or_script_read": False,
        "synopsis_policy": "SOURCE_RELATIVE_ORIGINAL_DRAFTS_HELD_PENDING_EDITORIAL_REVIEW",
        "accepted_source_work_effect": "NONE",
        "accepted_work_effect": "NONE",
        "coverage_effect": "NONE",
        "public_synopsis_effect": "NONE",
    }
    for field, expected in fixed.items():
        require(type(data[field]) is type(expected) and data[field] == expected,
                "metadata/admission scope: " + field)

    inputs = {
        "source_directory_sha256": ("explorer/discovery-catalog.json", DIRECTORY_SHA),
        "historical_publisher_csv_sha256": (
            "proposals/discovery/publisher-season6-20261102/ds9.csv", CSV_SHA),
        "accepted_b006_source_record_sha256": (
            "proposals/research/ds9-publisher-guide-tail-b006-20261103/observations.json", B006_SHA),
        "accepted_b010_source_record_sha256": (
            "proposals/research/ds9-s6-middle-b010-20261103/observations.json", B010_SHA),
        "accepted_b011_source_record_sha256": (
            "proposals/research/ds9-s6-tail-b011-20261103/observations.json", B011_SHA),
    }
    for field, (path, expected) in inputs.items():
        require(data[field] == expected and sha(ROOT / path) == expected,
                "accepted input drift: " + field)

    b006 = read_json(ROOT / inputs["accepted_b006_source_record_sha256"][0])
    b010 = read_json(ROOT / inputs["accepted_b010_source_record_sha256"][0])
    b011 = read_json(ROOT / inputs["accepted_b011_source_record_sha256"][0])
    require(b006["accepted_work_effect"] == "NONE" and b010["coverage_effect"] == "NONE"
            and b011["coverage_effect"] == "NONE", "accepted prior status boundary")
    earlier_episodes = {
        r["episode"] for r in b006["source_local_cards"] if r["season"] == 6
    } | {r["episode"] for r in b010["records"]} | {
        r["episode"] for r in b011["records"]
    }
    require(earlier_episodes == set(range(5, 26)), "accepted Season 6 prior frontier")

    with (ROOT / inputs["historical_publisher_csv_sha256"][0]).open(
        encoding="utf-8", newline=""
    ) as stream:
        csv_rows = list(csv.DictReader(stream))
    require(len(csv_rows) == 26, "historical publisher Season 6 rows")
    directory = read_json(ROOT / inputs["source_directory_sha256"][0])
    require(directory["data_status"] == "DISCOVERY_ONLY" and directory["row_count"] == 1214,
            "unadmitted directory state")
    by_id = {r["row_id"]: r for r in directory["rows"]}
    require(len(by_id) == len(directory["rows"]), "duplicate directory row")

    records = data["records"]
    require(isinstance(records, list) and len(records) == 5, "five held gap cards")
    for index, (record, (episode, title, paraphrase)) in enumerate(zip(records, EXPECTED), 1):
        require(isinstance(record, dict) and set(record) == RECORD_FIELDS,
                "closed source card schema")
        row_id = f"publisher:s6:ds9:{episode - 1:03d}"
        require(type(record["season"]) is int and type(record["episode"]) is int
                and record["season"] == 6 and record["episode"] == episode,
                "literal episode slot and types")
        require(episode not in earlier_episodes, "duplicate previously rechecked episode")
        require(record["observation_id"] == f"ds9-b012-p{index:02d}" and
                record["source_local_row_id"] == row_id, "source-local observation identity")
        require(record["publisher_card_title"] == title and
                record["card_locator"] == f"Season 6 Episode Guide > S6 E{episode} > {title}",
                "exact publisher title and locator")
        require(record["description_block_read"] is True and
                record["publisher_claim_paraphrase_draft"] == paraphrase and
                record["title_slot_status"] == "SAME_PUBLISHER_RECHECK_MATCH" and
                record["synopsis_status"] == "HELD_PENDING_INDEPENDENT_EDITORIAL_REVIEW" and
                record["accepted_work_id"] is None, "held source-relative editorial scope")
        require(csv_rows[episode - 1] == {
            "season": "6", "episode_number": str(episode), "title": title,
        }, "historical publisher CSV title and slot")
        original = by_id[row_id]
        require(original["title"] == title and original["context"] == f"DS9 S6E{episode}"
                and original["source_locator"] == GUIDE and
                original["identity_scope"] == "SOURCE_LOCAL" and
                original["admission_effect"] == "NONE" and
                original["coverage_effect"] == "NONE", "unadmitted directory row")
    return len(records)


if __name__ == "__main__":
    print(f"DS9_B012_OK: {validate()} source-local Season 6 gap cards; "
          "held editorial drafts; no Work, primary read or coverage effect")
