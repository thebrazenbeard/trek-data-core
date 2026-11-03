"""Fail-closed LD Season 1 publisher title/slot/literal mention observations."""

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GUIDE = "https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/1/"
DIRECTORY_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
CSV_SHA = "435dde1dc5e62b8298e1f38bca1e57413f25e9dc1e9acc323603b185220a6132"
RECEIPT_SHA = "9ea6d99bc63104bfcce9cfa145cc5c8a0e340b9e1b5a8d06639e135ef48a54a4"
EXPECTED = (
    (1, "Second Contact", ("Ensign Tendi", "U.S.S. Cerritos", "Mariner", "Boimler", "Rutherford")),
    (2, "Envoys", ("Boimler", "Mariner")),
    (3, "Temporal Edict", ("buffer time", "Lower Decks")),
    (4, "Moist Vessel", ("Captain Freeman", "Mariner")),
    (5, "Cupid's Errant Arrow", ("Mariner", "Boimler", "Tendi", "Rutherford")),
    (6, "Terminal Provocations", ("Ensign Fletcher", "Mariner", "Boimler", "Rutherford", "Tendi")),
    (7, "Much Ado About Boimler", ("Mariner", "Starfleet Academy")),
    (8, "Veritas", ("Mariner", "Boimler", "Tendi", "Rutherford")),
    (9, "Crisis Point", ("Mariner", "Boimler", "holodeck")),
    (10, "No Small Parts", ("U.S.S. Cerritos", "Tendi")),
)
TOP_FIELDS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_main_at_selection",
    "observed_utc_date", "publisher_guide_url", "source_scope", "publisher_source_family",
    "source_independence_status", "source_directory_sha256",
    "historical_publisher_csv_sha256", "historical_observation_receipt_sha256",
    "current_raw_html_sha256", "current_raw_html_captured", "actual_episode_or_script_read",
    "description_source_policy", "synopsis_policy", "artwork_policy",
    "accepted_source_work_effect", "accepted_work_effect", "coverage_effect",
    "public_synopsis_effect", "public_artwork_effect", "records",
}
RECORD_FIELDS = {
    "observation_id", "local_card_entity_id", "source_local_row_id", "season", "episode",
    "publisher_card_title", "card_locator", "evidence_kind", "evidence_scope",
    "literal_mentions", "literal_mention_scope", "synopsis_status",
    "artwork_candidate_page_url", "artwork_asset_url", "artwork_rights_status", "accepted_work_id",
}


def require(ok, why):
    if not ok:
        raise ValueError("LD L001 invalid: " + why)


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
        "batch_id": "ld-s1-guide-l001-20261103",
        "role": "LD",
        "proposal_only": True,
        "accepted_main_at_selection": "d07eced8571275fe7f1bb6387935db98f95e0bca",
        "observed_utc_date": "2026-11-03",
        "publisher_guide_url": GUIDE,
        "source_scope": "PUBLIC_RENDERED_PARAMOUNT_LD_S1_GUIDE_TITLE_SLOT_AND_LITERAL_DESCRIPTION_MENTIONS",
        "publisher_source_family": "paramount_corporate_publisher_family",
        "source_independence_status": "SAME_FAMILY_RECHECK_NOT_INDEPENDENT_CORROBORATION",
        "current_raw_html_sha256": None,
        "current_raw_html_captured": False,
        "actual_episode_or_script_read": False,
        "description_source_policy": "LITERAL_MENTION_TOKENS_ONLY_NO_BLURBS_OR_PARAPHRASES_STORED",
        "synopsis_policy": "ALL_HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE",
        "artwork_policy": "FIRST_PARTY_GUIDE_PAGE_LEAD_ONLY_NO_ASSET_OR_RIGHTS",
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
            "proposals/discovery/modern-paramount-season1-20261102/ld-observed-slots.csv", CSV_SHA),
        "historical_observation_receipt_sha256": (
            "proposals/discovery/modern-paramount-season1-20261102/ld-observation.json", RECEIPT_SHA),
    }
    for field, (relative, expected_sha) in paths.items():
        require(data[field] == expected_sha and sha(ROOT / relative) == expected_sha,
                "accepted source-directory input drift: " + field)
    receipt = read_json(ROOT / paths["historical_observation_receipt_sha256"][0])
    require(receipt["batch_id"] == "LD.PPLUS.S1.DISPLAYED10.20261102" and
            receipt["primary_locator"] == GUIDE and receipt["mission_id"] == "ld",
            "historical same-family discovery provenance")

    with (ROOT / paths["historical_publisher_csv_sha256"][0]).open(
        encoding="utf-8", newline=""
    ) as stream:
        csv_rows = list(csv.DictReader(stream))
    require(len(csv_rows) == 10, "historical publisher guide row count")
    directory = read_json(ROOT / paths["source_directory_sha256"][0])
    require(directory["data_status"] == "DISCOVERY_ONLY" and directory["row_count"] == 1214,
            "unadmitted discovery directory state")
    by_id = {row["row_id"]: row for row in directory["rows"]}
    require(len(by_id) == len(directory["rows"]), "duplicate discovery row")

    records = data["records"]
    require(isinstance(records, list) and len(records) == 10, "ten LD S1 cards")
    for i, (record, (episode, title, mentions)) in enumerate(zip(records, EXPECTED), 1):
        row_id = f"roster:modern-s1:ld:{episode - 1:03d}"
        require(isinstance(record, dict) and set(record) == RECORD_FIELDS,
                "closed source-local evidence schema")
        require(record["observation_id"] == f"ld-l001-o{i:02d}" and
                record["local_card_entity_id"] == f"ld-l001-card-{i:02d}" and
                record["source_local_row_id"] == row_id, "local entity and evidence identities")
        require(type(record["episode"]) is int and record["season"] == 1 and
                record["episode"] == episode and record["publisher_card_title"] == title,
                "literal publisher title/slot")
        require(record["card_locator"] ==
                f"Season 1 Episode Guide > S1 E{episode} > {title} > description",
                "current public source locator")
        require(record["evidence_kind"] == "PUBLISHER_CARD_DISPLAY_AND_LITERAL_DESCRIPTION_MENTION" and
                record["evidence_scope"] == "TITLE_SLOT_AND_MENTION_TOKENS_NOT_PLOT_FACTS" and
                record["literal_mention_scope"] == "PUBLISHER_DESCRIPTION_TEXT_ONLY",
                "publisher utterance is not depicted episode truth")
        require(type(record["literal_mentions"]) is list and
                record["literal_mentions"] == list(mentions), "literal description tokens")
        require(record["synopsis_status"] == "HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE" and
                record["artwork_candidate_page_url"] == GUIDE and
                record["artwork_asset_url"] is None and
                record["artwork_rights_status"] == "UNKNOWN_HELD" and
                record["accepted_work_id"] is None,
                "no public blurb/artwork or admitted Work")
        require(csv_rows[episode - 1] == {"season": "1", "episode_number": str(episode),
                                          "title": title}, "same-family historic discovery consistency")
        prior = by_id[row_id]
        require(prior["title"] == title and prior["context"] == f"LD S1E{episode}" and
                prior["source_locator"] == GUIDE and
                prior["verification_status"] == "UNVERIFIED_METADATA" and
                prior["identity_scope"] == "SOURCE_LOCAL" and
                prior["admission_effect"] == "NONE" and prior["coverage_effect"] == "NONE",
                "legacy discovery metadata has no admitted Work/coverage")
    return len(records)


if __name__ == "__main__":
    print(f"LD_L001_OK: {validate()} Lower Decks S1 publisher title/slot/mention observations, "
          "synopsis & artwork HELD; no Work/coverage")
