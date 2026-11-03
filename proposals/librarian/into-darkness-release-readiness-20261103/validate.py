#!/usr/bin/env python3
"""Fail-closed metadata validator for a local, NOT released, image readiness packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).with_name("decision.json")
EXPECTED_ACCEPTED_SOURCE_SHA = "b7a25bd69d641e183d1a19a38a970795ed9ea4fdbfc8e37c608dbe313267ded9"
EXPECTED_DECISION_CANONICAL_SHA = "2f4356cdf3afe29f4a365857859f47b2be554e6e7260de8b8137e5a5a4d6082b"
EXPECTED_IMAGE_SHA = "fadaaaedf16cc0b5c5924251f2ae1ddb3545a04796ec85fab951c160f9c3a9a6"
EXPECTED_RIGHTS_SHA = "6c715ffff293381a1cd2764a838e0463cb1119c6e208a7149944457a70e800f7"
EXPECTED_SOURCE_PATH = "proposals/librarian/into-darkness-commons-premiere-20261103/records.json"
EXPECTED_ROOT_FIELDS = {
    "schema_version", "batch_id", "accepted_main", "observed_on", "data_status",
    "source_packet_path", "source_packet_sha256", "source_local_film_row_id",
    "related_work_title", "related_work_locator", "real_world_event_local_id",
    "event_date", "event_place", "identity_relation", "recommended_ui_surface",
    "release_decision", "accepted_source_coverage_effect", "explorer_effect",
    "public_release_effect", "image_bytes_committed", "proposed_asset",
    "rights_evidence", "proposed_visible_ui", "network_plan",
    "independent_review", "public_release_gates",
}


def check(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        check(key not in result, f"duplicate key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    def reject_constant(value: str):
        raise ValueError(f"not finite JSON: {value}")

    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=unique_object, parse_constant=reject_constant)


def canonical_digest(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")).hexdigest()


def validate(packet: dict, root: Path = ROOT) -> None:
    check(type(packet) is dict and set(packet) == EXPECTED_ROOT_FIELDS,
          "unreviewed decision field or schema change")
    check(packet["schema_version"] == "1.0.0" and
          packet["batch_id"] == "LIBRARIAN.INTO_DARKNESS_PREMIERE.RELEASE_READINESS.20261103" and
          packet["accepted_main"] == "3e1a49e6d06af28fd8cab89fa02dae14d63ca5f8" and
          packet["data_status"] == "LOCAL_RELEASE_READINESS_PROPOSAL_ONLY" and
          packet["source_packet_path"] == EXPECTED_SOURCE_PATH and
          packet["source_packet_sha256"] == EXPECTED_ACCEPTED_SOURCE_SHA,
          "baseline or accepted source identification changed")
    check(packet["release_decision"] == "CONDITIONAL_GO_TO_BUILD_ONLY_PUBLIC_RELEASE_HELD" and
          packet["public_release_effect"] == "NONE" and
          packet["explorer_effect"] == "NONE" and
          packet["accepted_source_coverage_effect"] == "NONE" and
          packet["image_bytes_committed"] is False,
          "proposal cannot authorize display or coverage")
    source_path = root / EXPECTED_SOURCE_PATH
    check(hashlib.sha256(source_path.read_bytes()).hexdigest() == EXPECTED_ACCEPTED_SOURCE_SHA,
          "accepted source-proposal bytes differ")
    source = read_json(source_path)["candidate"]
    check(source["row_id"] == "film:film-into-darkness" and
          source["original_image_sha256"] == EXPECTED_IMAGE_SHA and
          source["commons_rights_page_sha256"] == EXPECTED_RIGHTS_SHA and
          source["reported_photographer_license"] == "CC_BY_SA_2_0" and
          source["editorial_display_admission"] == "HELD_UNTIL_INDEPENDENT_REVIEW",
          "source record no longer matches original held packet")
    image = packet["proposed_asset"]
    rights = packet["rights_evidence"]
    ui = packet["proposed_visible_ui"]
    network = packet["network_plan"]
    check(packet["identity_relation"] == "DOCUMENTARY_EVENT_ABOUT_FILM_NOT_FILM_CONTENT" and
          packet["recommended_ui_surface"] ==
          "SEPARATE_REAL_WORLD_PREMIERE_EVENT_PANEL_NOT_FILM_POSTER_STILL_OR_CANON_EVIDENCE" and
          packet["source_local_film_row_id"] == source["row_id"] and
          packet["related_work_locator"] == source["official_film_source"],
          "real event / fictional work boundary weakened")
    check(image["byte_sha256"] == EXPECTED_IMAGE_SHA and
          image["byte_size"] == source["original_image_bytes"] and
          image["original_url"] == source["original_commons_image_url"] and
          image["file_kind"] == "ORIGINAL_UNMODIFIED_JPEG" and
          image["derivative_bytes_produced"] is False,
          "image binary identity or non-derivative decision changed")
    check(rights["rights_page_sha256"] == EXPECTED_RIGHTS_SHA and
          rights["pinned_revision_url"] == source["commons_pinned_revision"] and
          rights["photographer"] == source["creator"] and
          rights["license"] == source["reported_photographer_license"] and
          rights["license_url"] == source["license_url"] and
          rights["no_endorsement"] is True,
          "license, subject or rights receipt mismatch")
    check("Star Trek Into Darkness Cast 2013" in ui["attribution_text"] and
          "Eva Rinaldi" in ui["attribution_text"] and
          "CC BY-SA 2.0" in ui["attribution_text"] and
          "unmodified" in ui["attribution_text"].lower() and
          "not a frame or poster" in ui["image_caption"] and
          "not affiliated with or endorsed" in ui["no_endorsement_notice"],
          "missing attribution, work title, factual caption or nonendorsement")
    check(network["host"] == "SAME_ORIGIN_GITHUB_PAGES_ONLY" and
          network["third_party_image_request"] is False and
          network["external_links_only_after_click"] is True and
          network["referrer_policy"] == "no-referrer" and
          network["initial_image_dom"] == "ABSENT_UNTIL_EXPLICIT_ARTWORK_OPT_IN" and
          network["loading"] == "lazy",
          "privacy or network boundary weakened")
    check(packet["independent_review"]["status"] ==
          "CONDITIONAL_BUILD_GO_PUBLIC_DISPLAY_HOLD" and
          len(packet["public_release_gates"]) == 6,
          "independent public release gate removed")
    # The immutable code-owned entire-decision pin catches malicious text
    # inside otherwise innocuous captions, threats and permission descriptions.
    check(canonical_digest(packet) == EXPECTED_DECISION_CANONICAL_SHA,
          "unreviewed release decision or caption changes")


if __name__ == "__main__":
    try:
        validate(read_json(PACKET))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"RELEASE_READINESS_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print("RELEASE_READINESS_OK: 1 conditional build recommendation; zero public release")
