"""Fail-closed checks for a single bounded corrected-QID SFA WDQS receipt.

The raw SPARQL response was not retained. These tests validate normalized
observations and source-relative joining, not remote source authenticity.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
QUERY = HERE / "queries/sfa-current-qid.rq"
RECEIPT = HERE / "receipt.json"
CANDIDATES = HERE / "candidates.json"
PUBLISHER = ROOT / "proposals/research/sfa-publisher-video-routes-20261104/records.json"
EXPECTED_QIDS = [
    "Q137786752", "Q137793912", "Q137793913", "Q137793914", "Q137793915",
    "Q137793916", "Q137793917", "Q137793918", "Q137793920", "Q137793921", "Q137793922",
]
EXPECTED_LABELS = [
    "Star Trek: Starfleet Academy, season 1", "Kids These Days", "Beta Test", "Vitus Reflux",
    "Vox In Excelso", "Series Acclimation Mil", "Come, Let's Away", "Ko'Zeine",
    "The Life of the Stars", "300th Night", "Rubincon",
]
EXPECTED_HOLD_IDS = {
    "season-labeled-p179-member", "ordinal-absent", "title-case-variant",
    "qid-gap-not-evidence", "query-limited-untyped",
}


def check(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def validate(receipt: dict, candidates: dict, query: bytes, publisher: dict) -> None:
    check(type(receipt) is dict and set(receipt) == {
        "schema_version", "snapshot_id", "status", "endpoint", "method", "source_independence_group",
        "requested_series_qid", "previous_redirected_qid", "query_file", "query_sha256", "query_limit",
        "query_method", "client", "http_status", "content_type", "http_date_header", "retrieved_at_utc",
        "raw_response_bytes", "raw_response_sha256", "raw_response_committed", "binding_count",
        "variable_names", "nonempty_ordinal_bindings", "rights_basis", "accepted_work_effect",
        "accepted_source_binding_effect", "coverage_effect", "denominator_effect",
    }, "receipt schema")
    check(receipt["schema_version"] == "1.0.0" and receipt["snapshot_id"] == "SFA-WDQS-Q117350388-20261104-LIMIT40-001", "receipt id")
    check(receipt["status"] == "HELD_THIRD_PARTY_DISCOVERY", "held status")
    check(receipt["endpoint"] == "https://query.wikidata.org/sparql" and receipt["method"] == "GET", "official WDQS endpoint")
    check(receipt["source_independence_group"] == "thirdparty:wikidata", "Wikidata source lineage")
    check(receipt["requested_series_qid"] == "Q117350388" and receipt["previous_redirected_qid"] == "Q134592591", "corrected QID")
    check(receipt["query_file"] == "queries/sfa-current-qid.rq", "query file")
    check(receipt["query_sha256"] == hashlib.sha256(query).hexdigest() == "6611641ce34596d7f6f90b7050d5da4f4c9ea30cb7257d393899b5074034cce2", "exact query bytes")
    decoded = query.decode("utf-8")
    check("VALUES ?series { wd:Q117350388 }" in decoded and "wd:Q134592591" not in decoded, "corrected query binding")
    check("wdt:P179 ?series" in decoded and "wdt:P1545" in decoded and "wdt:P4908" in decoded, "query properties")
    check(receipt["query_limit"] == 40 and "LIMIT 40" in decoded, "bounded request")
    check(receipt["query_method"].startswith("P179 membership"), "documented method")
    check("30 s timeout" in receipt["client"] and "1,000,000-byte cap" in receipt["client"], "retrieval bounds")
    check(type(receipt["http_status"]) is int and receipt["http_status"] == 200, "HTTP result")
    check(receipt["content_type"] == "application/sparql-results+json;charset=utf-8", "JSON content type")
    check(receipt["http_date_header"] == "Wed, 04 Nov 2026 11:40:54 GMT", "response HTTP date")
    check(dt.datetime.fromisoformat(receipt["retrieved_at_utc"]) == dt.datetime.fromisoformat("2026-11-04T11:40:54.777494+00:00"), "retrieval time")
    check(type(receipt["raw_response_bytes"]) is int and receipt["raw_response_bytes"] == 4069, "response length")
    check(re.fullmatch(r"[0-9a-f]{64}", receipt["raw_response_sha256"]) is not None, "response hash syntax")
    check(receipt["raw_response_sha256"] == "3cd6579c8073e9e5f1547542b59a28384879917149615e5c36b00df11eb4d161", "raw response receipt digest")
    check(receipt["raw_response_committed"] is False, "raw response not archived")
    check(receipt["variable_names"] == ["episode", "episodeLabel", "seriesOrdinal", "seasonItem", "seasonOrdinal"], "query variable set")
    check(type(receipt["binding_count"]) is int and receipt["binding_count"] == 11, "observed rows")
    check(receipt["nonempty_ordinal_bindings"] == 0, "no supplied ordinal properties")
    check(receipt["rights_basis"] == "WIKIDATA_STRUCTURED_DATA_CC0_FOR_DISCOVERY_ONLY", "rights not episode-media license")
    for key in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
        check(receipt[key] == "NONE", f"forbidden receipt effect {key}")

    check(type(candidates) is dict and set(candidates) == {
        "schema_version", "batch_id", "status", "receipt", "query_parent_qid", "all_rows_untyped",
        "canonical_work_effect", "source_binding_effect", "coverage_effect", "denominator_effect",
        "ordinal_comparison", "publisher_route_basis", "rows", "holds",
    }, "candidate schema")
    check(candidates["schema_version"] == "1.0.0" and candidates["batch_id"] == "SFA-WDQS-CORRECTED-QID-20261104-001", "candidate ID")
    check(candidates["status"] == "HELD_WDQS_SOURCE_RELATIVE_CANDIDATES" and candidates["receipt"] == "receipt.json", "candidate status")
    check(candidates["query_parent_qid"] == "Q117350388" and candidates["all_rows_untyped"] is True, "no independent type validation")
    for key in ("canonical_work_effect", "source_binding_effect", "coverage_effect", "denominator_effect"):
        check(candidates[key] == "NONE", f"forbidden candidate effect {key}")
    check(candidates["ordinal_comparison"] == "UNAVAILABLE_FROM_WDQS_RESPONSE", "missing ordinals must remain null")
    check(candidates["publisher_route_basis"] == "proposals/research/sfa-publisher-video-routes-20261104/records.json", "publisher basis")
    check(publisher["disposition"] == "HELD_PUBLISHER_SOURCE_ROUTE_METADATA" and publisher["coverage_effect"] == "NONE", "publisher not source bound")
    routes = publisher["publisher_page_route_observations"]
    rows = candidates["rows"]
    check(type(rows) is list and len(rows) == receipt["binding_count"] == 11 and len(routes) == 10, "row count and publisher size")
    check(len({x["qid"] for x in rows}) == 11, "unique Wikidata local identity")
    for idx, row in enumerate(rows):
        check(type(row) is dict and set(row) == {
            "source_local_id", "qid", "label", "season_item_qid", "wikidata_episode_ordinal",
            "wikidata_season_ordinal", "publisher_episode_hint", "publisher_route_id",
            "title_comparison", "identity_hold",
        }, f"row schema {idx}")
        check(row["qid"] == EXPECTED_QIDS[idx] and row["label"] == EXPECTED_LABELS[idx], f"source-relative QID and exact label {idx}")
        check(row["source_local_id"] == "wdqs-sfa-20261104-" + row["qid"].lower(), f"local identity {idx}")
        check(row["wikidata_episode_ordinal"] is None and row["wikidata_season_ordinal"] is None, "no fabricated ordinal")
        if idx == 0:
            check(row["season_item_qid"] is None and row["publisher_episode_hint"] is None and row["publisher_route_id"] is None, "season-labeled member exclusion")
            check(row["title_comparison"] == "UNMATCHED_SEASON_LABELED_ITEM" and row["identity_hold"] == "P179_MEMBER_NOT_VERIFIED_AS_EPISODE", "season member hold")
        else:
            route = routes[idx - 1]
            check(row["season_item_qid"] == "Q137786752", "source-local P4908 season relationship")
            check(type(row["publisher_episode_hint"]) is int and row["publisher_episode_hint"] == idx == route["episode_number"], "publisher ordinal is only a hint")
            check(row["publisher_route_id"] == route["id"], "route crosswalk")
            title = route["displayed_title"]
            comparison = "CASE_SENSITIVE_EXACT" if row["label"] == title else "CASE_ONLY_VARIANT" if row["label"].casefold() == title.casefold() else "UNMATCHED"
            check(row["title_comparison"] == comparison and comparison != "UNMATCHED", "source-relative title only")
            check(row["identity_hold"] == "TITLE_LEAD_ONLY_NO_WORK_ADMISSION", "no identity promotion")
    check([x["title_comparison"] for x in rows].count("CASE_SENSITIVE_EXACT") == 9, "nine exact label matches")
    check([x["title_comparison"] for x in rows].count("CASE_ONLY_VARIANT") == 1, "one case-only title variant")

    holds = candidates["holds"]
    check(type(holds) is list and len(holds) == 5 and {x["id"] for x in holds} == EXPECTED_HOLD_IDS, "all five anomaly holds")
    by_id = {x["id"]: x for x in holds}
    check(by_id["season-labeled-p179-member"]["qid"] == "Q137786752" and by_id["season-labeled-p179-member"]["class"] == "POTENTIAL_NON_EPISODE_SERIES_MEMBER", "season item identity hold")
    check(by_id["ordinal-absent"]["class"] == "MISSING_DIRECT_ORDINAL_EVIDENCE", "ordinal hold")
    check(by_id["title-case-variant"]["qid"] == "Q137793915" and by_id["title-case-variant"]["publisher_route_id"] == "sfa-pplus-route-04", "case variant hold")
    check(by_id["qid-gap-not-evidence"]["qid"] == "Q137793919" and "not evidence" in by_id["qid-gap-not-evidence"]["finding"], "QID gap cannot imply episode")
    check(by_id["query-limited-untyped"]["class"] == "LIMITED_SOURCE_DISCOVERY", "query completeness hold")


def main() -> None:
    validate(
        json.loads(RECEIPT.read_text(encoding="utf-8")),
        json.loads(CANDIDATES.read_text(encoding="utf-8")),
        QUERY.read_bytes(),
        json.loads(PUBLISHER.read_text(encoding="utf-8")),
    )
    print("PASS: corrected-QID WDQS 11 source-local rows; 10 publisher-title leads, 1 season-labeled hold, 0 ordinals or admitted Works")


if __name__ == "__main__":
    main()
