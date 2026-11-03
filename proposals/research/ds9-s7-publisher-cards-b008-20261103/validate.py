"""Fail-closed DS9 Season 7 source-card recheck; never admit an episode Work.

These pins verify internal metadata and the accepted discovery directory, not
an authenticated HTML snapshot or an audiovisual source.
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
EXPECTED = (
    (7, "Once More Unto the Breach"),
    (8, "The Siege of AR-555"),
    (9, "Covenant"),
    (10, "It's Only A Paper Moon"),
    (11, "Prodigal Daughter"),
    (12, "The Emperor's New Cloak"),
    (13, "Field of Fire"),
    (14, "Chimera"),
    (15, "Badda-Bing, Badda-Bang"),
    (16, "Inter Arma Enim Silent Leges"),
)
TOP_FIELDS = {
    "schema_version", "batch_id", "role", "proposal_only", "base_accepted_main",
    "observed_utc_date", "source_scope", "publisher_guide_url",
    "publisher_independence_group", "source_directory_sha256",
    "historical_publisher_csv_sha256", "fresh_raw_html_sha256",
    "fresh_raw_html_captured", "full_episode_or_script_read",
    "accepted_source_work_binding_effect", "accepted_work_effect", "coverage_effect",
    "public_synopsis_effect", "publisher_description_policy", "records",
    "unresolved_same_publisher_title_conflict",
}
RECORD_FIELDS = {
    "observation_id", "source_local_row_id", "publisher_season", "publisher_episode",
    "publisher_card_title", "publisher_card_locator", "title_slot_status",
    "synopsis_status", "accepted_work_id",
}
CONFLICT_FIELDS = {
    "observation_id", "paramount_plus_guide_title", "star_trek_franchise_page_title",
    "star_trek_franchise_page_url", "source_independence", "global_work_title_decision",
}


def require(condition, message):
    if not condition:
        raise ValueError("DS9 B008 invalid: " + message)


def unique_pairs(pairs):
    output = {}
    for key, value in pairs:
        require(key not in output, "duplicate JSON key: " + key)
        output[key] = value
    return output


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data=None):
    if data is None:
        data = read_json(HERE / "observations.json")
    require(set(data) == TOP_FIELDS, "top-level closed schema")
    require(data["schema_version"] == "1.0.0", "schema version")
    require(data["batch_id"] == "ds9-s7-publisher-cards-b008-20261103", "batch identity")
    require(data["role"] == "DS9" and data["proposal_only"] is True, "proposal lane")
    require(data["base_accepted_main"] == "1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b",
            "accepted selection base")
    require(data["observed_utc_date"] == "2026-11-03", "observation date")
    require(data["source_scope"] == "PUBLIC_RENDERED_PARAMOUNT_EPISODE_GUIDE_TITLE_SLOT_ONLY",
            "source scope")
    require(data["publisher_guide_url"] == GUIDE, "publisher guide identity")
    require(data["publisher_independence_group"] == "paramount_corporate_publisher_family",
            "source independence")
    require(data["source_directory_sha256"] == DIRECTORY_SHA
            and sha(ROOT / "explorer/discovery-catalog.json") == DIRECTORY_SHA,
            "accepted source-directory custody")
    require(data["historical_publisher_csv_sha256"] == CSV_SHA
            and sha(ROOT / "proposals/discovery/publisher-season7-20261102/ds9.csv") == CSV_SHA,
            "prior publisher CSV custody")
    require(data["fresh_raw_html_sha256"] is None
            and data["fresh_raw_html_captured"] is False, "raw HTML not captured")
    require(data["full_episode_or_script_read"] is False, "no episode full-source read")
    for key in ("accepted_source_work_binding_effect", "accepted_work_effect", "coverage_effect",
                "public_synopsis_effect"):
        require(data[key] == "NONE", "protected effect: " + key)
    require(data["publisher_description_policy"] ==
            "BLOCKS_SEEN_BUT_NO_TEXT_OR_PARAPHRASES_RELEASED", "synopsis hold")

    with (ROOT / "proposals/discovery/publisher-season7-20261102/ds9.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        csv_rows = list(csv.DictReader(stream))
    discovery = read_json(ROOT / "explorer/discovery-catalog.json")
    require(discovery["data_status"] == "DISCOVERY_ONLY", "directory status")
    directory_by_id = {row["row_id"]: row for row in discovery["rows"]}
    require(len(directory_by_id) == len(discovery["rows"]), "duplicate directory row ID")

    records = data["records"]
    require(isinstance(records, list) and len(records) == len(EXPECTED), "ten source cards")
    for offset, (record, (episode, title)) in enumerate(zip(records, EXPECTED), start=1):
        row_id = f"publisher:s7:ds9:{episode-1:03d}"
        require(set(record) == RECORD_FIELDS, "closed card schema")
        require(record["observation_id"] == f"ds9-b008-p{offset:02d}", "observation ordering")
        require(record["source_local_row_id"] == row_id, "source-local row identity")
        require(record["publisher_season"] == 7
                and record["publisher_episode"] == episode, "publisher slot")
        require(record["publisher_card_title"] == title, "literal publisher title")
        require(record["publisher_card_locator"] ==
                f"Season 7 Episode Guide > S7 E{episode} > {title}", "rendered card locator")
        expected_status = ("SAME_PUBLISHER_FAMILY_TITLE_CONFLICT_UNRESOLVED" if episode == 8
                           else "MATCHES_PRIOR_SAME_PUBLISHER_DIRECTORY")
        require(record["title_slot_status"] == expected_status, "same-family variant must remain open")
        require(record["synopsis_status"] == "HELD_NO_PUBLIC_COPY_OR_PARAPHRASE",
                "unreviewed description release")
        require(record["accepted_work_id"] is None, "no accepted Work identity")
        require(csv_rows[episode - 1] == {
            "season": "7", "episode_number": str(episode), "title": title,
        }, "historical publisher row mismatch")
        row = directory_by_id[row_id]
        require(row["title"] == title and row["context"] == f"DS9 S7E{episode}"
                and row["source_locator"] == GUIDE
                and row["identity_scope"] == "SOURCE_LOCAL"
                and row["admission_effect"] == "NONE"
                and row["coverage_effect"] == "NONE",
                "independent discovery directory is metadata only")

    conflict = data["unresolved_same_publisher_title_conflict"]
    require(set(conflict) == CONFLICT_FIELDS, "conflict schema")
    require(conflict == {
        "observation_id": "ds9-b008-p02",
        "paramount_plus_guide_title": "The Siege of AR-555",
        "star_trek_franchise_page_title": "The Siege of AR-558",
        "star_trek_franchise_page_url":
            "https://www.startrek.com/videos/episode-preview-the-siege-of-ar-558",
        "source_independence": "SAME_CORPORATE_FAMILY_NOT_INDEPENDENT_CORROBORATION",
        "global_work_title_decision": "UNRESOLVED",
    }, "same-publisher title disagreement must not be reconciled by the validator")
    return len(records)


if __name__ == "__main__":
    print(f"DS9_B008_OK: {validate()} publisher S7E7-E16 title/slot cards, synopsis HELD, "
          "title discrepancy unresolved, no accepted Work or coverage")
