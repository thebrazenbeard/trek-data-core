"""Fail-closed Voyager S2E6-E15 publisher-card metadata; synopsis/artwork held."""

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GUIDE = "https://www.paramountplus.com/shows/star_trek_voyager/episodes/2/"
DIRECTORY_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
CSV_SHA = "192a970935739a618b68609598532443da8fb9de2529d1d53399b323245c0a97"
PRIOR_VOY_SHA = "3b55fcf2b9a9aab7a02293400e4ccac1f62d0ad097ffb2ff057f02fa305b8080"
EXPECTED = (
    (6, "Twisted"),
    (7, "Parturition"),
    (8, "Persistence of Vision"),
    (9, "Tattoo"),
    (10, "Cold Fire"),
    (11, "Maneuvers"),
    (12, "Resistance"),
    (13, "Prototype"),
    (14, "Alliances"),
    (15, "Threshold"),
)
TOP_FIELDS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_main_at_selection",
    "observed_utc_date", "source_scope", "publisher_guide_url", "publisher_source_family",
    "source_independence_status", "source_directory_sha256",
    "historical_publisher_csv_sha256", "accepted_voy_b006_source_record_sha256",
    "current_raw_html_sha256", "current_raw_html_captured", "actual_episode_or_script_read",
    "synopsis_artwork_policy", "accepted_source_work_effect", "accepted_work_effect",
    "coverage_effect", "public_synopsis_effect", "public_artwork_effect", "records",
}
RECORD_FIELDS = {
    "observation_id", "local_entity_id", "source_local_row_id", "season", "episode",
    "publisher_card_title", "card_locator", "evidence_kind", "evidence_scope",
    "title_slot_status", "synopsis_status", "artwork_candidate_page_url",
    "artwork_asset_url", "artwork_rights_status", "accepted_work_id",
}


def require(ok, reason):
    if not ok:
        raise ValueError("VOY V001 invalid: " + reason)


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
        "batch_id": "voy-s2-middle-v001-20261103",
        "role": "VOY",
        "proposal_only": True,
        "accepted_main_at_selection": "2070b0153228272b5dd667b0a23465ff49a95a5f",
        "observed_utc_date": "2026-11-03",
        "source_scope": "PUBLIC_RENDERED_PARAMOUNT_VOY_S2_GUIDE_TITLE_SLOT_ONLY",
        "publisher_guide_url": GUIDE,
        "publisher_source_family": "paramount_corporate_publisher_family",
        "source_independence_status": "SAME_FAMILY_RECHECK_NOT_INDEPENDENT_CORROBORATION",
        "current_raw_html_sha256": None,
        "current_raw_html_captured": False,
        "actual_episode_or_script_read": False,
        "synopsis_artwork_policy": "DESCRIPTION_VISIBLE_NOT_REPUBLISHED_ARTWORK_PAGE_LEAD_ONLY_RIGHTS_HELD",
        "accepted_source_work_effect": "NONE",
        "accepted_work_effect": "NONE",
        "coverage_effect": "NONE",
        "public_synopsis_effect": "NONE",
        "public_artwork_effect": "NONE",
    }
    for field, expected in expected_fields.items():
        require(type(data[field]) is type(expected) and data[field] == expected,
                "source/admission scope and type: " + field)

    paths = {
        "source_directory_sha256": ("explorer/discovery-catalog.json", DIRECTORY_SHA),
        "historical_publisher_csv_sha256": (
            "proposals/discovery/legacy-paramount-season2-20261102/voy.csv", CSV_SHA),
        "accepted_voy_b006_source_record_sha256": (
            "proposals/verification/episode-guide-rechecks-b006-voy-20261103/observations.json",
            PRIOR_VOY_SHA),
    }
    for field, (relative, expected_sha) in paths.items():
        require(data[field] == expected_sha and sha(ROOT / relative) == expected_sha,
                "accepted input drift: " + field)

    earlier = read_json(ROOT / paths["accepted_voy_b006_source_record_sha256"][0])
    require(earlier["admission_effect"] == "NONE" and earlier["coverage_effect"] == "NONE"
            and earlier["source_family"] == "paramount_corporate_publisher_family",
            "earlier VOY source-only B006 scope")
    prior_s2 = {(r["episode"], r["official_title"], r["row_id"])
                for r in earlier["rows"] if r["season"] == 2}
    require(prior_s2 == {(2, "Initiations", "lead:0076"),
                         (20, "Investigations", "lead:0077")},
            "prior accepted Voyager S2 recheck slots")

    directory = read_json(ROOT / paths["source_directory_sha256"][0])
    require(directory["data_status"] == "DISCOVERY_ONLY" and directory["row_count"] == 1214,
            "unadmitted directory status")
    by_id = {row["row_id"]: row for row in directory["rows"]}
    require(len(by_id) == len(directory["rows"]), "duplicate discovery directory row")
    with (ROOT / paths["historical_publisher_csv_sha256"][0]).open(
        encoding="utf-8", newline=""
    ) as stream:
        csv_rows = list(csv.DictReader(stream))
    require(len(csv_rows) == 26, "historical publisher season-two row count")

    records = data["records"]
    require(isinstance(records, list) and len(records) == len(EXPECTED), "ten VOY S2 records")
    for index, (record, (episode, title)) in enumerate(zip(records, EXPECTED), 1):
        row_id = f"legacy:s2:voy:{episode - 1:03d}"
        require(isinstance(record, dict) and set(record) == RECORD_FIELDS,
                "closed source-relative evidence schema")
        require(record["observation_id"] == f"voy-v001-o{index:02d}" and
                record["local_entity_id"] == f"voy-v001-card-{index:02d}" and
                record["source_local_row_id"] == row_id, "local entity/evidence identity")
        require(type(record["episode"]) is int and record["season"] == 2 and
                record["episode"] == episode and record["publisher_card_title"] == title,
                "rendered publisher title/slot")
        require(record["card_locator"] == f"Season 2 Episode Guide > S2 E{episode} > {title}",
                "publisher source card locator")
        require(record["evidence_kind"] == "PUBLISHER_GUIDE_CARD_DISPLAY" and
                record["evidence_scope"] == "TITLE_AND_SLOT_ONLY" and
                record["title_slot_status"] == "SAME_PUBLISHER_RECHECK_MATCH",
                "publisher metadata evidence, not episode depiction")
        require(record["synopsis_status"] == "HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE" and
                record["artwork_candidate_page_url"] == GUIDE and
                record["artwork_asset_url"] is None and
                record["artwork_rights_status"] == "UNKNOWN_HELD" and
                record["accepted_work_id"] is None,
                "no publication or unlicensed artwork/Work admission")
        require(episode not in {e for e, _, _ in prior_s2},
                "no overlap with accepted source-rechecked Voyager seed")
        require(csv_rows[episode - 1] == {"season": "2", "episode_number": str(episode),
                                          "title": title}, "historical same-family source row")
        row = by_id[row_id]
        require(row["title"] == title and row["context"] == f"VOY S2E{episode}" and
                row["source_locator"] == GUIDE and row["source_group"] == "publisher:paramount"
                and row["verification_status"] == "UNVERIFIED_METADATA" and
                row["identity_scope"] == "SOURCE_LOCAL" and
                row["admission_effect"] == "NONE" and row["coverage_effect"] == "NONE",
                "legacy discovery candidate remains unadmitted")
    return len(records)


if __name__ == "__main__":
    print(f"VOY_V001_OK: {validate()} S2E6-E15 current publisher title/slot cards; "
          "synopsis and artwork HELD; no Work/coverage")
