"""Fail-closed structural checks for held SFA publisher video-route metadata.

This is not source authentication, an accepted Source-to-Work binding, or
verification of audiovisual content. Run from any working directory.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROSTER = ROOT / "proposals/librarian/sfa-publisher-roster-20261102/bundle.json"
RECORDS = HERE / "records.json"

TOP_KEYS = {
    "schema_version", "batch_id", "role", "disposition", "accepted_work_effect",
    "accepted_source_binding_effect", "coverage_effect", "denominator_effect",
    "reconciliation_effect", "audiovisual_content_inspected",
    "episode_page_playback_attempted", "rights_to_reproduce_media",
    "source_observation", "prior_accepted_proposal", "publisher_page_route_observations",
}
SOURCE_KEYS = {
    "source_id", "source_locator", "source_type", "publisher", "independence_group",
    "retrieved_utc_day", "method", "http_status", "raw_response_bytes",
    "raw_response_sha256", "raw_snapshot_committed", "html_mutable", "observed_scope",
}
ROUTE_KEYS = {
    "id", "season", "episode_number", "displayed_title", "route_path",
    "publisher_datetime", "html_link_line",
}
ROUTE_PATTERN = re.compile(r"/shows/video/[A-Za-z0-9_]+/")
HASH_PATTERN = re.compile(r"[a-f0-9]{64}")


def check(ok: bool, detail: str) -> None:
    if not ok:
        raise ValueError(detail)


def validate(data: dict, roster: dict) -> None:
    check(type(data) is dict and set(data) == TOP_KEYS, "exact packet fields")
    check(data["schema_version"] == "1.0.0", "schema")
    check(data["batch_id"] == "SFA-PUBLISHER-VIDEO-ROUTES-20261104-001", "batch")
    check(data["role"] == "SFA", "role")
    check(data["disposition"] == "HELD_PUBLISHER_SOURCE_ROUTE_METADATA", "disposition")
    for key in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect", "reconciliation_effect"):
        check(data[key] == "NONE", f"forbidden effect: {key}")
    check(data["audiovisual_content_inspected"] is False, "av not inspected")
    check(data["episode_page_playback_attempted"] is False, "playback not attempted")
    check(data["rights_to_reproduce_media"] == "NOT_ESTABLISHED", "rights must remain held")
    check(data["prior_accepted_proposal"] == "proposals/librarian/sfa-publisher-roster-20261102/bundle.json", "prior proposal path")
    check(roster["batch_id"] == "SFA-PUBLISHER-ROSTER-20261102-001", "accepted roster source")
    check(roster["accepted_work_effect"] == "NONE" and roster["coverage_effect"] == "NONE", "roster admission ceiling")

    source = data["source_observation"]
    check(type(source) is dict and set(source) == SOURCE_KEYS, "source receipt fields")
    check(source["source_id"] == "sfa-paramountplus-episodes-html-20261104", "source identity")
    check(source["source_locator"] == "https://www.paramountplus.com/shows/star-trek-starfleet-academy/episodes/", "source URL")
    check(source["source_type"] == "OFFICIAL_PUBLISHER_EPISODE_GUIDE_HTML", "source class")
    check(source["publisher"] == "Paramount+" and source["independence_group"] == "publisher:paramount", "source lineage")
    check(source["retrieved_utc_day"] == "2026-11-04", "observation day")
    check("read-only" in source["method"].lower() and "urllib" in source["method"], "retrieval method")
    check(type(source["http_status"]) is int and source["http_status"] == 200, "HTTP receipt")
    check(type(source["raw_response_bytes"]) is int and source["raw_response_bytes"] > 0, "response length")
    check(type(source["raw_response_sha256"]) is str and HASH_PATTERN.fullmatch(source["raw_response_sha256"]) is not None, "response SHA-256")
    check(source["raw_snapshot_committed"] is False and source["html_mutable"] is True, "no durable source bytes")
    check("no linked media fetched" in source["observed_scope"], "scope")

    routes = data["publisher_page_route_observations"]
    check(type(routes) is list and len(routes) == 10, "ten publisher route observations only")
    check(type(roster["episode_slots"]) is list and len(roster["episode_slots"]) == 10, "accepted proposal slot count")
    seen_ids: set[str] = set()
    seen_routes: set[str] = set()
    for i, (route, slot) in enumerate(zip(routes, roster["episode_slots"], strict=True), start=1):
        check(type(route) is dict and set(route) == ROUTE_KEYS, f"route fields {i}")
        check(route["id"] == f"sfa-pplus-route-{i:02d}", f"local route id {i}")
        check(route["id"] not in seen_ids, "duplicate local identity")
        seen_ids.add(route["id"])
        check(type(route["season"]) is int and route["season"] == slot["season"] == 1, f"season {i}")
        check(type(route["episode_number"]) is int and route["episode_number"] == slot["episode_number"] == i, f"ordinal {i}")
        check(route["displayed_title"] == slot["title"], f"accepted publisher title {i}")
        path = route["route_path"]
        check(type(path) is str and ROUTE_PATTERN.fullmatch(path) is not None, f"publisher-only href {i}")
        check(path not in seen_routes, "duplicate publisher href")
        seen_routes.add(path)
        check(type(route["publisher_datetime"]) is str, "publisher datetime type")
        try:
            stamped = dt.datetime.fromisoformat(route["publisher_datetime"])
        except ValueError as exc:
            raise ValueError(f"invalid publisher date {i}") from exc
        check(stamped.tzinfo is not None and stamped.year == 2026, f"date offset {i}")
        check(type(route["html_link_line"]) is int and route["html_link_line"] == 1405 + 28 * (i - 1), f"source-relative link locator {i}")


def main() -> None:
    validate(json.loads(RECORDS.read_text(encoding="utf-8")), json.loads(ROSTER.read_text(encoding="utf-8")))
    print("PASS: SFA held publisher route metadata matches accepted roster, zero admission/rights/coverage effects")


if __name__ == "__main__":
    main()
