"""Fail-closed integrity audit of five HELD Voyager publisher-card observations.

Source-relative card fingerprints are not archived source-byte custody or
evidence of an audiovisual close read, Work identity, or canonical events.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RECORDS = HERE / "records.json"
BASE = "3028765359001b90bc3e6b5c1835ee283b326e91"
CSV = "proposals/discovery/publisher-season4-20261102/voy.csv"
CSV_SHA = "e9e8ac0cae8a30ac1c71b0c36b1d0f28b9ff9cf25d5f2a8d2875fad2e34e598e"
TITLES = {
    15: "Hunters",
    16: "Prey",
    17: "Retrospect",
    18: "Killing Game, The, Part 1",
    19: "Killing Game, The, Part 2",
}
BLURBS = {
    15: (88, "b06020b5cf4e334a26815c4b0910f580997c275726efecd7a580b1f2e5e72285"),
    16: (119, "2e0328d192e5aecfd886ca4d6a048d2a821db64479f8fe5ef6445ff6efc487e0"),
    17: (135, "ee0780db268ebd61a30b67886ba49196174497b7a2e54d9ff67a846c086d3284"),
    18: (101, "47b5da6d80508c75bd6d09e774e4689e95b4c587200ab977b2a5672479a1eeff"),
    19: (67, "c4469c50e649ade23dba04acbf897208bb15213b668bcb8ebca107851f4a8a77"),
}
ROW_SHA = {
    15: "c92e574cc439f1d3535631763f349d5fb3f44926838bed56ce219ff3bb757933",
    16: "2ce664235b87812c8f9e8b709e8cfabc55db653efd7a1c957b2aa0d90db5436d",
    17: "99d0eed99d2162ba7a8d7c1c081b7a7f42cc14e31cf7dec81c56b60c55cc7d94",
    18: "ce1a0a1ecad4fad71b07dc6c6ae9323ec670b4ce5d86bf6f10bec09362bc246a",
    19: "4f2bf84aaa70d116f61271b6adf3557927a0258d46b6026e15d70ba1c5fa8a3a",
}
ENVELOPE = {"schema_version", "packet_id", "role", "base_accepted_main", "observation_date_utc",
            "status", "rights_or_publication_effect", "source_binding_effect",
            "global_work_identity_effect", "coverage_effect", "episode_source_read",
            "transcript_or_full_text_read", "images_or_videos_retrieved", "source",
            "source_local_cards", "coverage_update"}
SOURCE = {"id", "url", "lineage_group", "type", "read_representation", "source_locator",
          "raw_page_sha256", "source_text_fingerprint_mode", "upstream_discovery_csv",
          "upstream_discovery_sha256", "independent_corroboration"}
CARD = {"id", "season", "source_ordinal", "source_title", "title_reconciliation", "blurb_sha256",
        "blurb_normalized_chars", "locator", "evidence_state", "work_id", "publisher_image_locator",
        "publisher_video_locator", "original_synopsis", "synopsis_status"}


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def row_sha(row: dict) -> str:
    raw = json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate(data: dict, repo: Path = REPO) -> None:
    require(type(data) is dict and set(data) == ENVELOPE, "packet shape")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "schema")
    require(data["packet_id"] == "voy-s4-e15-e19-publisher-cards-20261104", "packet ID")
    require(data["role"] == "VOY_SOURCE_LOCAL" and data["base_accepted_main"] == BASE, "role/base")
    require(data["observation_date_utc"] == "2026-11-04", "observation date")
    require(data["status"] == "HELD_PROPOSAL_ONLY", "promotion")
    for key in ("rights_or_publication_effect", "source_binding_effect", "global_work_identity_effect", "coverage_effect"):
        require(data[key] == "NONE", "effect: " + key)
    for key in ("episode_source_read", "transcript_or_full_text_read", "images_or_videos_retrieved"):
        require(data[key] is False, "unread source claim: " + key)

    src = data["source"]
    require(type(src) is dict and set(src) == SOURCE, "source shape")
    require(src["id"] == "paramount-voy-s4-guide-rendered", "source ID")
    require(src["url"] == "https://www.paramountplus.com/shows/star_trek_voyager/episodes/4/", "source URL bytes")
    url = urlsplit(src["url"])
    require((url.scheme, url.netloc, url.path, url.query, url.fragment, url.username, url.password) ==
            ("https", "www.paramountplus.com", "/shows/star_trek_voyager/episodes/4/", "", "", None, None), "source URL")
    require(src["lineage_group"] == "PARAMOUNT_CBS_SKYDANCE_CORPORATE", "lineage")
    require(src["type"] == "FIRST_PARTY_PUBLISHER_GUIDE" and src["read_representation"] == "WEB_RENDERED_HTML_TEXT", "source type")
    require(src["source_locator"] == "Season 4 > Episode Guide > S4 E15 through S4 E19", "source locator")
    require(src["raw_page_sha256"] is None, "unarchived raw-source claim")
    require(src["source_text_fingerprint_mode"] ==
            "SHA256_OF_NFKC_WHITESPACE_COLLAPSED_RENDERED_CARD_BLURB_UNARCHIVED", "source fingerprint mode")
    require(src["upstream_discovery_csv"] == CSV and src["upstream_discovery_sha256"] == CSV_SHA, "upstream provenance")
    require(src["independent_corroboration"] is False, "dependent source promoted")

    csv_path = (repo / CSV).resolve()
    require(csv_path.is_relative_to(repo.resolve()) and csv_path.is_file(), "unsafe upstream path")
    raw = csv_path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == CSV_SHA, "upstream changed")
    accepted_rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    require(len(accepted_rows) == 26, "accepted season denominator changed")

    cards = data["source_local_cards"]
    require(type(cards) is list and len(cards) == 5, "five source-local cards required")
    found = set()
    for card in cards:
        require(type(card) is dict and set(card) == CARD, "card shape")
        number = card["source_ordinal"]
        require(type(number) is int and number in TITLES and number not in found, "ordinal")
        found.add(number)
        title = TITLES[number]
        require(card["id"] == f"voy-s4-e{number:02d}-publisher-card", "local ID")
        require(type(card["season"]) is int and card["season"] == 4 and card["source_title"] == title, "title/season")
        require(card["title_reconciliation"] ==
                ("PUBLISHER_INVERTED_TITLE_HELD" if number in (18, 19) else "SOURCE_DISPLAY_ONLY"), "title reconciliation")
        require(card["locator"] == f"Season 4 > {title} > S4 E{number} > adjacent description", "locator")
        require(type(card["blurb_normalized_chars"]) is int and
                (card["blurb_normalized_chars"], card["blurb_sha256"]) == BLURBS[number], "blurb fingerprint")
        require(accepted_rows[number - 1] == {"season": "4", "episode_number": str(number), "title": title}, "discovery disagreement")
        require(card["evidence_state"] == "PUBLISHER_DISPLAY_ONLY_HELD" and card["work_id"] is None, "identity/evidence promotion")
        require(card["publisher_image_locator"] is None and card["publisher_video_locator"] is None, "unverified media")
        require(card["synopsis_status"] == "HELD_ORIGINAL_PARAPHRASE_REQUIRES_EDITORIAL_REVIEW", "synopsis released")
        require(type(card["original_synopsis"]) is str and 50 <= len(card["original_synopsis"]) <= 180, "synopsis shape")
        require(row_sha(card) == ROW_SHA[number], "source-local row changed")
    require(found == set(TITLES), "incomplete observed card set")
    coverage = data["coverage_update"]
    require(type(coverage) is dict and
            all(type(coverage.get(key)) is int for key in (
                "new_episode_discoveries", "accepted_work_bindings", "close_reads",
                "released_synopses", "released_artwork")), "coverage types")
    require(coverage == {
        "new_episode_discoveries": 0, "accepted_work_bindings": 0, "close_reads": 0,
        "released_synopses": 0, "released_artwork": 0, "status": "UNCHANGED",
    }, "coverage claim")


if __name__ == "__main__":
    payload = json.loads(RECORDS.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)
    validate(payload)
    print("PASS: VOY S4 E15-E19 held publisher cards; exact row pins; no admissions or coverage")
