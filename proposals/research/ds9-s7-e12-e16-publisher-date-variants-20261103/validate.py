"""Fail-closed validation for five DS9 publisher-card observations, not Work admission."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CSV = ROOT / "proposals/discovery/publisher-season7-20261102/ds9.csv"
INDEX = ROOT / "proposals/discovery/publisher-season7-20261102/index.json"
DIRECTORY = ROOT / "explorer/discovery-catalog.json"
GUIDE = "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/"
LISTING = "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/"
BASE = "f7c111f351ab2f0eb629883a045ffc697c3d3209"
CSV_SHA = "1dbfe6a4b6af54a5eb2831108d358c8c3f984346b1b3a79de6301ccf2dc22aea"
DIRECTORY_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
HISTORICAL_HTML_SHA = "23dcb2cc9d7baec5e13ee27f80054ee3dcf9f95ae86985f6ecaaf1303f946cf1"
OBS_SHA = "542e90c19b30df8bbfc6f5124f569361a449e983f4b92a82ce6fbec018d7359e"
ASSERT_SHA = "18b669adfbbefed5801cccb0cf8ca9e7a51269267231dcdfe0805cfe38cac6b6"
FAMILY = "paramount_corporate_publisher_family"
BATCH = "ds9-s7-e12-e16-publisher-date-variants-20261103"
DATE_STATE = "UNRESOLVED_OFFICIAL_DISPLAY_SURFACE_DATE_VARIANT_NOT_AIRDATE"
SOURCE_CLASS = "SEARCH_INDEXED_FIRST_PARTY_LISTING_AND_EPISODE_DETAIL_HEADERS_NOT_RAW_CAPTURE"
EXPECTED = (
    (12, "The Emperor's New Cloak", "1999-01-04", "1999-01-03", "Bp20UMEBLgJ8PzFT5Gh31aQ8wc6D5aym"),
    (13, "Field of Fire", "1999-02-01", "1999-01-31", "YQIX1fnjpx7vB6UVXfh6CFR0BizblngJ"),
    (14, "Chimera", "1999-02-08", "1999-02-07", "dOv4Dn_D7_8nAjpPO3EiIPDkqyX2Qhfx"),
    (15, "Badda-Bing, Badda-Bang", "1999-02-22", "1999-02-21", "U7IHc59rpYYRrg6yqtTvwTE6WF7j__M_"),
    (16, "Inter Arma Enim Silent Leges", "1999-02-15", "1999-02-14", "WF5h4L2sYa_wqtWkZlILdO4D9BLaA8Lb"),
)
OBS_KEYS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_main_at_selection",
    "observed_utc_date", "source_family", "official_season_guide_url", "official_listing_url",
    "date_observation_channel", "historical_20261102_csv_sha256",
    "historical_20261102_html_capture_sha256", "current_raw_source_html_sha256",
    "complete_episode_or_script_read", "accepted_source_work_effect", "coverage_effect",
    "public_synopsis_effect", "records",
}
RECORD_KEYS = {
    "evidence_id", "source_local_row_id", "season", "episode", "observed_publisher_title",
    "guide_card_locator", "official_detail_url", "listing_display_date",
    "detail_header_display_date", "date_resolution", "title_slot_resolution",
    "original_description_draft", "editorial_status", "accepted_work_id",
}
ASSERT_KEYS = {"schema_version", "batch_id", "proposal_only", "accepted_assertions",
               "projection_effect", "assertions"}
CLAIM_KEYS = {"id", "predicate", "subject_source_family", "evidence_ids", "status",
              "claim", "falsifier"}


def require(condition, why):
    if not condition:
        raise ValueError(why)


def exact_keys(obj, keys, scope):
    require(type(obj) is dict and set(obj) == keys, f"{scope}: fields missing or added")


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read(path, limit=4_000_000):
    require(path.is_file() and not path.is_symlink() and 0 < path.stat().st_size < limit,
            f"unsafe or missing input: {path.name}")
    return path.read_bytes()


def read_json(path):
    return json.loads(read(path).decode("utf-8"), object_pairs_hook=no_duplicate_keys)


def canonical_hash(obj):
    data = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def qualify(obs, claims, directory, directory_bytes, csv_bytes, index):
    exact_keys(obs, OBS_KEYS, "observation envelope")
    require(obs["schema_version"] == "1.0.0" and obs["batch_id"] == BATCH
            and obs["role"] == "DS9" and obs["proposal_only"] is True
            and obs["accepted_main_at_selection"] == BASE
            and obs["observed_utc_date"] == "2026-11-03", "observation identity forged")
    require(obs["source_family"] == FAMILY and obs["official_season_guide_url"] == GUIDE
            and obs["official_listing_url"] == LISTING
            and obs["date_observation_channel"] == SOURCE_CLASS, "source identity upgraded")
    require(obs["historical_20261102_csv_sha256"] == CSV_SHA
            and hashlib.sha256(csv_bytes).hexdigest() == CSV_SHA
            and obs["historical_20261102_html_capture_sha256"] == HISTORICAL_HTML_SHA,
            "historical source provenance drift")
    require(obs["current_raw_source_html_sha256"] is None
            and obs["complete_episode_or_script_read"] is False,
            "source custody falsely claimed")
    for field in ("accepted_source_work_effect", "coverage_effect", "public_synopsis_effect"):
        require(obs[field] == "NONE", f"protected effect forged: {field}")

    require(type(index) is dict and index.get("proposal_status") == "DISCOVERY_ONLY"
            and index.get("admission_effect") == "NONE"
            and index.get("coverage_effect") == "NONE"
            and index.get("denominator_effect") == "NONE"
            and index.get("independence_group") == "publisher:paramount"
            and index.get("observed_on") == "2026-11-02", "historical index reclassified")
    pages = index.get("source_pages")
    require(type(pages) is list and len(pages) == 3, "source receipt pages drifted")
    ds9 = [p for p in pages if p.get("mission_id") == "ds9"]
    require(len(ds9) == 1 and ds9[0].get("official_page") == GUIDE
            and ds9[0].get("source_body_sha256") == HISTORICAL_HTML_SHA
            and ds9[0].get("observation_csv_sha256") == CSV_SHA
            and ds9[0].get("source_body_bytes") == 314706
            and ds9[0].get("listed_slot_count") == 25,
            "historical receipt not authenticated")

    require(hashlib.sha256(directory_bytes).hexdigest() == DIRECTORY_SHA, "directory drift")
    require(type(directory) is dict and directory.get("row_count") == 1214
            and type(directory.get("rows")) is list and len(directory["rows"]) == 1214
            and directory.get("data_status") == "DISCOVERY_ONLY"
            and directory.get("admission_effect") == "NONE"
            and directory.get("coverage_effect") == "NONE", "directory admitted or malformed")
    rows = {r["row_id"]: r for r in directory["rows"]}
    require(len(rows) == 1214, "duplicate directory row")
    historical = list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8"))))
    require(len(historical) == 25, "unexpected CSV source-card count")
    require(type(obs["records"]) is list and len(obs["records"]) == 5,
            "five-card scope drift")
    for offset, (record, (episode, title, listing_date, detail_date, video_id)) in enumerate(
            zip(obs["records"], EXPECTED), 1):
        exact_keys(record, RECORD_KEYS, "source-local card")
        row_id = f"publisher:s7:ds9:{episode-1:03d}"
        require(historical[episode - 1] == {"season": "7", "episode_number": str(episode),
                                           "title": title}, "historical title/slot mismatch")
        source = rows.get(row_id, {})
        require(source.get("title") == title and source.get("context") == f"DS9 S7E{episode}"
                and source.get("medium") == "EPISODE"
                and source.get("source_group") == "publisher:paramount"
                and source.get("source_locator") == GUIDE
                and source.get("verification_status") == "UNVERIFIED_METADATA"
                and source.get("admission_effect") == "NONE"
                and source.get("coverage_effect") == "NONE", "source local lineage upgraded")
        require(record["evidence_id"] == f"ds9-s7e12-16-p{offset:02d}"
                and record["source_local_row_id"] == row_id
                and type(record["season"]) is int and record["season"] == 7
                and type(record["episode"]) is int and record["episode"] == episode
                and record["observed_publisher_title"] == title
                and record["guide_card_locator"] == (
                    f"Season 7 Episode Guide > {title} > S7 E{episode} > short description")
                and record["official_detail_url"] == (
                    f"https://www.paramountplus.com/shows/video/{video_id}/"),
                "source card title, slot or locator swapped")
        require(record["listing_display_date"] == listing_date
                and record["detail_header_display_date"] == detail_date
                and record["date_resolution"] == DATE_STATE
                and record["title_slot_resolution"] == "EXACT_SOURCE_LOCAL_PUBLISHER_CARD_MATCH",
                "date promoted, swapped or misclassified")
        require(record["editorial_status"] == "PENDING_HUMAN_REVIEW"
                and record["accepted_work_id"] is None,
                "description or Work accepted without review")
        draft = record["original_description_draft"]
        require(type(draft) is str and 60 <= len(draft) <= 230
                and draft.endswith(".") and "\n" not in draft,
                "editorial draft structurally malformed")

    exact_keys(claims, ASSERT_KEYS, "source claim envelope")
    require(claims["schema_version"] == "1.0.0" and claims["batch_id"] == BATCH
            and claims["proposal_only"] is True and claims["accepted_assertions"] == 0
            and claims["projection_effect"] == "NONE"
            and type(claims["assertions"]) is list and len(claims["assertions"]) == 2,
            "source claims upgraded")
    predicates = (
        "PUBLISHER_DISPLAY_DATE_VARIANTS_REQUIRE_SEMANTICS",
        "PUBLISHER_DISPLAY_DATE_SEQUENCE_NONMONOTONIC_UNRESOLVED",
    )
    for i, claim in enumerate(claims["assertions"], 1):
        exact_keys(claim, CLAIM_KEYS, "unresolved source claim")
        require(claim["id"] == f"ds9-s7e12-16-a{i:02d}"
                and claim["predicate"] == predicates[i - 1]
                and claim["subject_source_family"] == FAMILY
                and claim["evidence_ids"] == ([f"ds9-s7e12-16-p{j:02d}" for j in range(1, 6)]
                                              if i == 1 else ["ds9-s7e12-16-p04", "ds9-s7e12-16-p05"])
                and claim["status"] == "PROPOSED_UNRESOLVED"
                and type(claim["claim"]) is str and len(claim["claim"]) > 70
                and type(claim["falsifier"]) is str and len(claim["falsifier"]) > 60,
                "claim status, lineage or references upgraded")
    require(canonical_hash(obs) == OBS_SHA, "frozen observation proposal modified")
    require(canonical_hash(claims) == ASSERT_SHA, "frozen source claims modified")


def validate():
    obs, claims = read_json(HERE / "observations.json"), read_json(HERE / "assertions.json")
    directory_bytes = read(DIRECTORY)
    qualify(obs, claims, read_json(DIRECTORY), directory_bytes, read(CSV), read_json(INDEX))
    print("DS9_S7_E12_16_SOURCE_ONLY_OK: 5 publisher cards; date displays unresolved; "
          "5 drafts pending; zero source/work/coverage/public effects")


if __name__ == "__main__":
    validate()
