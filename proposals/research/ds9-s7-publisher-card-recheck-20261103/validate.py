"""DS9 official Season 7 five-card provenance recheck: candidate-only gate."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CSV_PATH = ROOT / "proposals/discovery/publisher-season7-20261102/ds9.csv"
INDEX_PATH = ROOT / "proposals/discovery/publisher-season7-20261102/index.json"
DIRECTORY_PATH = ROOT / "explorer/discovery-catalog.json"
URL = "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/"
BASE = "8a89b16e96220188d200b6ff9300fb90fa137627"
CSV_SHA = "1dbfe6a4b6af54a5eb2831108d358c8c3f984346b1b3a79de6301ccf2dc22aea"
DIRECTORY_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
HISTORICAL_HTML_SHA = "23dcb2cc9d7baec5e13ee27f80054ee3dcf9f95ae86985f6ecaaf1303f946cf1"
OBSERVATIONS_SHA = "0d1e54aa959f57d9be2962716165500b4f3cca77bdfe84a146a5443c1cba014a"
ASSERTIONS_SHA = "c3a4efc14668824774720657167bdbc03b7e02adc05e160df5891d0e3fa1acee"
EXPECTED = (
    (2, "Shadows and Symbols"),
    (3, "Afterimage"),
    (4, "Take Me Out to the Holosuite"),
    (5, "Chrysalis"),
    (6, "Treachery, Faith, and the Great River"),
)
OBS_FIELDS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_main_at_selection",
    "source_recheck_utc_date", "source_scope", "publisher_guide_url",
    "publisher_independence_group", "source_directory_sha256",
    "historical_20261102_publisher_csv_sha256", "historical_20261102_page_capture_sha256",
    "fresh_rendered_page_body_sha256", "fresh_raw_html_bytes_captured",
    "full_episode_or_script_read", "accepted_source_work_binding_effect", "accepted_work_effect",
    "coverage_effect", "public_synopsis_approval_effect", "records",
}
RECORD_FIELDS = {
    "observation_id", "source_local_row_id", "historical_csv_season", "historical_csv_episode",
    "historical_csv_title", "fresh_publisher_card_title", "fresh_publisher_card_locator",
    "title_slot_observation", "source_description_observation", "original_description_draft",
    "editorial_status", "accepted_work_id",
}
ASSERTION_FIELDS = {"schema_version", "batch_id", "proposal_only", "accepted_assertions",
                    "projection_effect", "assertions"}
CLAIM_FIELDS = {"id", "predicate", "subject", "evidence_ids", "counter_evidence_ids",
                "status", "statement", "falsifier"}


def require(value, message):
    if not value:
        raise ValueError(message)


def exact_keys(value, keys, scope):
    require(type(value) is dict and set(value) == keys, f"{scope}: unexpected or missing fields")


def canonical_digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read(path, max_bytes=4_000_000):
    require(path.is_file() and not path.is_symlink() and 0 < path.stat().st_size < max_bytes,
            f"unsafe or absent input: {path.name}")
    return path.read_bytes()


def read_json(path):
    return json.loads(read(path).decode("utf-8"), object_pairs_hook=unique_keys)


def qualify(observations, assertions, directory, directory_raw, csv_bytes, old_index):
    exact_keys(observations, OBS_FIELDS, "DS9 S7 publisher recheck envelope")
    require(observations["schema_version"] == "1.0.0"
            and observations["batch_id"] == "ds9-s7-publisher-card-recheck-20261103"
            and observations["role"] == "DS9" and observations["proposal_only"] is True
            and observations["accepted_main_at_selection"] == BASE
            and observations["source_recheck_utc_date"] == "2026-11-03",
            "wrong batch scope or provenance date")
    require(observations["source_scope"] == "PUBLIC_RENDERED_PUBLISHER_GUIDE_TITLE_SLOT_BRIEF_DESCRIPTION_ONLY"
            and observations["publisher_guide_url"] == URL
            and observations["publisher_independence_group"] == "paramount_corporate_publisher_family",
            "source URL or family reclassified")
    require(observations["source_directory_sha256"] == DIRECTORY_SHA
            and hashlib.sha256(directory_raw).hexdigest() == DIRECTORY_SHA,
            "source directory content drift")
    require(observations["historical_20261102_publisher_csv_sha256"] == CSV_SHA
            and hashlib.sha256(csv_bytes).hexdigest() == CSV_SHA,
            "historical publisher CSV provenance drift")
    require(observations["historical_20261102_page_capture_sha256"] == HISTORICAL_HTML_SHA,
            "historical HTML receipt relabeled")
    require(observations["fresh_rendered_page_body_sha256"] is None
            and observations["fresh_raw_html_bytes_captured"] is False
            and observations["full_episode_or_script_read"] is False,
            "current page or full episode custody falsely claimed")
    for effect in ("accepted_source_work_binding_effect", "accepted_work_effect",
                   "coverage_effect", "public_synopsis_approval_effect"):
        require(observations[effect] == "NONE", f"unexpected {effect}")

    require(type(old_index) is dict and old_index.get("proposal_status") == "DISCOVERY_ONLY"
            and old_index.get("admission_effect") == "NONE"
            and old_index.get("coverage_effect") == "NONE"
            and old_index.get("denominator_effect") == "NONE"
            and old_index.get("independence_group") == "publisher:paramount"
            and old_index.get("observed_on") == "2026-11-02", "historical receipt envelope changed")
    pages = old_index.get("source_pages", [])
    require(type(pages) is list and len(pages) == 3, "historical receipt page count changed")
    old_ds9 = [r for r in pages if r.get("mission_id") == "ds9"]
    require(len(old_ds9) == 1, "historical DS9 capture collision")
    receipt = old_ds9[0]
    require(receipt.get("official_page") == URL and receipt.get("source_body_sha256") == HISTORICAL_HTML_SHA
            and receipt.get("source_body_bytes") == 314706
            and receipt.get("observation_csv_sha256") == CSV_SHA
            and receipt.get("listed_slot_count") == 25,
            "historical DS9 receipt was rewritten")

    require(type(directory) is dict and directory.get("row_count") == 1214
            and len(directory.get("rows", [])) == 1214
            and directory.get("data_status") == "DISCOVERY_ONLY"
            and directory.get("admission_effect") == "NONE"
            and directory.get("coverage_effect") == "NONE", "directory not source-only")
    directory_rows = {r["row_id"]: r for r in directory["rows"]}
    require(len(directory_rows) == 1214, "duplicated directory row ids")
    parsed = list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8"))))
    require(len(parsed) == 25, "historical publisher S7 CSV row count changed")
    require(type(observations["records"]) is list and len(observations["records"]) == 5,
            "five card scope drift")
    for i, (record, (number, expected_title)) in enumerate(zip(observations["records"], EXPECTED), 1):
        exact_keys(record, RECORD_FIELDS, "individual publisher guide card")
        row_id = f"publisher:s7:ds9:{i:03d}"
        source = directory_rows[row_id]
        historical_csv = parsed[number - 1]
        require(historical_csv == {"season": "7", "episode_number": str(number), "title": expected_title},
                "historical publisher CSV slot/title changed")
        require(source.get("title") == expected_title and source.get("context") == f"DS9 S7E{number}"
                and source.get("medium") == "EPISODE"
                and source.get("source_group") == "publisher:paramount"
                and source.get("source_locator") == URL
                and source.get("verification_status") == "UNVERIFIED_METADATA"
                and source.get("admission_effect") == "NONE" and source.get("coverage_effect") == "NONE",
                "source-local directory lineage or status changed")
        require(record["observation_id"] == f"ds9-s7r-p{i:02d}"
                and record["source_local_row_id"] == row_id
                and type(record["historical_csv_season"]) is int
                and record["historical_csv_season"] == 7
                and type(record["historical_csv_episode"]) is int
                and record["historical_csv_episode"] == number
                and record["historical_csv_title"] == expected_title
                and record["fresh_publisher_card_title"] == expected_title,
                "observation title/slot identity drift")
        require(record["fresh_publisher_card_locator"] == (
            f"Season 7 Episode Guide > {expected_title} > S7 E{number} > short description"
        ), "source card locator changed")
        require(record["title_slot_observation"] == "MATCHES_HISTORICAL_PUBLISHER_CSV_AND_SOURCE_LOCAL_DIRECTORY"
                and record["source_description_observation"] == (
                    "PUBLISHER_CARD_DESCRIPTION_READ_NOT_FULL_EPISODE_EVIDENCE"
                ) and record["editorial_status"] == "PENDING_HUMAN_REVIEW"
                and record["accepted_work_id"] is None, "candidate promoted to coverage or Work")
        draft = record["original_description_draft"]
        require(type(draft) is str and 60 <= len(draft) <= 230
                and draft.endswith(".") and "\n" not in draft,
                "unreviewed draft structurally unsafe")

    exact_keys(assertions, ASSERTION_FIELDS, "DS9 source assertion envelope")
    require(assertions["schema_version"] == "1.0.0"
            and assertions["batch_id"] == observations["batch_id"]
            and assertions["proposal_only"] is True
            and assertions["accepted_assertions"] == 0
            and assertions["projection_effect"] == "NONE"
            and type(assertions["assertions"]) is list and len(assertions["assertions"]) == 1,
            "assertion state upgraded")
    claim = assertions["assertions"][0]
    exact_keys(claim, CLAIM_FIELDS, "DS9 source assertion")
    require(claim["id"] == "ds9-s7r-a01"
            and claim["predicate"] == "SAME_UPSTREAM_PUBLISHER_LINEAGE_NOT_INDEPENDENT_CORROBORATION"
            and claim["subject"] == "paramount-corporate-publisher-family:ds9-s7-guide"
            and claim["evidence_ids"] == [f"ds9-s7r-p{i:02d}" for i in range(1, 6)]
            and claim["counter_evidence_ids"] == []
            and claim["status"] == "PROPOSED_UNRESOLVED"
            and type(claim["falsifier"]) is str and len(claim["falsifier"]) > 50,
            "source assertion upgraded or orphaned")
    # These freeze the observation *proposal*, not inaccessible source HTML.
    require(canonical_digest(observations) == OBSERVATIONS_SHA, "observation proposal silently rewritten")
    require(canonical_digest(assertions) == ASSERTIONS_SHA, "source assertion silently rewritten")


def validate():
    observations = read_json(HERE / "observations.json")
    assertions = read_json(HERE / "assertions.json")
    csv_bytes = read(CSV_PATH)
    index = read_json(INDEX_PATH)
    directory_raw = read(DIRECTORY_PATH)
    directory = json.loads(directory_raw.decode("utf-8"), object_pairs_hook=unique_keys)
    qualify(observations, assertions, directory, directory_raw, csv_bytes, index)
    print("DS9_S7_RECHECK_OK: 5 current publisher guide cards match historical titles/slots; "
          "same-family source metadata only, 5 editorial drafts pending, zero admission")


if __name__ == "__main__":
    validate()
