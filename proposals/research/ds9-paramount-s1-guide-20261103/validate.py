"""Fail-closed local consistency check for DS9 source-relative publisher metadata.

This does not verify remote pages, copyright rights, or audiovisual content.
"""

import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
EXPECTED_EPISODE_NUMBERS = {1, 3, 4, 5, 6}


def check(value, message):
    if not value:
        raise ValueError(message)


def read_json(name, base=HERE):
    return json.loads((base / name).read_text(encoding="utf-8"))


def validate(base=HERE):
    records = read_json("records.json", base)
    entities = read_json("local_entities.json", base)
    evidence = read_json("evidence.json", base)
    assertions = read_json("assertions.json", base)

    check(records.get("proposal_only") is True, "must stay proposal-only")
    for key in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
        check(records.get(key) == "NONE", f"unexpected promotion: {key}")
    check(records.get("admitted_briefings") == 0, "unreviewed Briefings")
    source = records["source"]
    check(source.get("full_primary_audiovisual_content_read") is False, "false primary-source read")
    check(source.get("raw_html_retained_in_public_repo") is False, "raw source release")
    check(source.get("http_status") == 200, "missing guide retrieval")
    digest = source.get("raw_html_sha256", "")
    check(len(digest) == 64 and set(digest).issubset(set("0123456789abcdef")),
          "invalid guide receipt")

    slots = records["source_local_episode_slots"]
    check(len(slots) == 5, "expected five cards")
    check({x["episode_number"] for x in slots} == EXPECTED_EPISODE_NUMBERS, "episode slot drift")
    check(len({x["id"] for x in slots}) == 5, "duplicate slot IDs")
    check(len({x["video_url"] for x in slots}) == 5, "duplicate video links")
    for slot in slots:
        check(slot["season"] == 1, "out-of-partition season")
        parts = urlsplit(slot["video_url"])
        check(parts.scheme == "https" and parts.hostname == "www.paramountplus.com"
              and parts.path.startswith("/shows/video/") and not parts.username and not parts.query,
              "off-provider video locator")
        guide_date = dt.date.fromisoformat(slot["guide_date_indexed"])
        video_date = dt.date.fromisoformat(slot["video_page_date_indexed"])
        check(guide_date - video_date == dt.timedelta(days=1), "date observation changed")
        check(len(slot["guide_line_window"]) == 2 and slot["guide_line_window"][0] < slot["guide_line_window"][1],
              "invalid rendered guide locator")
    check(records["date_observation_caveat"]["broadcast_date_reconciliation"] == "UNRESOLVED",
          "date conflict silently resolved")

    entity_ids = [x["id"] for x in entities["entities"]]
    check(len(set(entity_ids)) == len(entity_ids), "duplicate entity ID")
    check(entities["accepted_entities"] == 0 and entities["global_identity_links_created"] == 0,
          "local entities were promoted")
    evidence_ids = [x["id"] for x in evidence["evidence"]]
    check(len(evidence_ids) == len(set(evidence_ids)) == 10, "evidence count/ID drift")
    slot_ids = {x["id"] for x in slots}
    for item in evidence["evidence"]:
        check(item["slot_id"] in slot_ids, "evidence points outside batch")
        check(set(item["entity_ids"]).issubset(entity_ids), "unknown local entity")
        check(item["kind"] in ("PUBLISHER_SYNOPSIS", "DATE_LABEL_SEARCH_INDEX_CONFLICT"),
              "unsupported evidence status")
    check(evidence["audiovisual_evidence_count"] == 0, "metadata is not audiovisual analysis")
    check(assertions["admitted_assertions"] == 0 and assertions["projection_effect"] == "NONE",
          "assertion promotion")
    for assertion in assertions["assertions"]:
        check(set(assertion["evidence_ids"]).issubset(evidence_ids), "assertion orphan evidence")
        check(assertion["status"].startswith("PROPOSED"), "unexpected accepted assertion")
    print("PASS: 5 DS9 publisher guide cards, 10 source-relative observations, "
          "6 unadmitted assertions; date discrepancy unresolved")


if __name__ == "__main__":
    validate()
