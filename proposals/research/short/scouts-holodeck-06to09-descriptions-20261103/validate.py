"""Fail-closed source-local Scouts Holodeck 6–9 summaries; #10 remains held."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OBSERVATIONS = HERE / "observations.json"
CATALOG = ROOT / "explorer/discovery-catalog.json"
PINNED_OBSERVATIONS_SHA256 = "8610b331dc882c1aed933e0ae46a5469666cc7f61e45045222d94f754ec1b116"
VIDEO_IDS = ("-m7ISEuAhac", "cYRzkzu_zhg", "O5wUrGB_6qw", "TbZFOtuHpxk")
DISPLAY_DATES = ("2026-02-14", "2026-02-28", "2026-03-07", "2026-03-16")
PUBLISHER_TITLES = (
    "Holodeck Rescues #6 | Star Trek Scouts Defeat ROBOTS on the Moon! 🌕 | Star Trek: Scouts",
    "Holodeck Rescues #7 | Star Trek Scouts Save a Chameleon's Invisible Power! 💥 | Star Trek: Scouts",
    "Holodeck Rescues #8 | Star Trek Scouts Rescue a Moon Alien! 👽 | Star Trek: Scouts",
    "Sprocket Gets Stuck in an Underwater Whirlpool! 🌊 | Star Trek: Scouts | Holodeck Rescues Episode #9",
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def read_pinned() -> dict:
    raw = OBSERVATIONS.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINNED_OBSERVATIONS_SHA256,
            "publisher-search observations changed after source review")
    return json.loads(raw)


EXPECTED = read_pinned()


def exact_url(url: str, host: str, path: str, query: str = "") -> bool:
    parsed = urlsplit(url)
    return (parsed.scheme == "https" and parsed.netloc == host and parsed.path == path
            and parsed.query == query and parsed.username is None and parsed.password is None
            and parsed.port is None and not parsed.fragment)


def validate(data: dict, catalog: dict | None = None) -> int:
    require(isinstance(data, dict) and set(data) == set(EXPECTED), "unreviewed top-level fields")
    for key, value in EXPECTED.items():
        require(type(data[key]) is type(value) and data[key] == value,
                f"unreviewed observation content: {key}")
    require(data["schema_version"] == "trek-scouts-holodeck-06to09-publisher-description-v1"
            and data["proposal_only"] is True and data["short_count"] == 4,
            "source-only four-entry boundary changed")
    require(data["source_access"] == "SEARCH_RETRIEVED_PUBLIC_YOUTUBE_VIDEO_DESCRIPTION_NOT_VIDEO_PAGE_OPENED"
            and data["verification_class"] == "PUBLISHER_DESCRIPTION_METADATA_READ_NOT_ANIMATION_VIEWED"
            and data["source_family"] == "publisher:paramount-nickelodeon-youtube"
            and data["publisher_channel_display_name"] == "Blaze and the Monster Machines"
            and data["independent_upstream_families"] == 1,
            "publisher search source class or corporate lineage changed")
    for key in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                "accepted_coverage_effect", "public_synopsis_release_effect", "artwork_release_effect"):
        require(data[key] == "NONE", f"protected effect changed: {key}")
    for key in ("animations_viewed", "video_pages_opened", "source_bound", "close_read"):
        require(data[key] is False, f"unsupported video/page claim: {key}")
    require(data["raw_source_page_sha256"] is None, "no raw publisher page bytes retrieved")

    catalog = catalog if catalog is not None else json.loads(CATALOG.read_text(encoding="utf-8"))
    require(catalog.get("data_status") == "DISCOVERY_ONLY"
            and catalog.get("admission_effect") == "NONE"
            and catalog.get("coverage_effect") == "NONE", "discovery projection promoted")
    source_rows = catalog.get("rows")
    require(isinstance(source_rows, list), "discovery rows missing")
    candidates = {row.get("row_id"): row for row in source_rows}
    require(len(candidates) == len(source_rows), "duplicate discovery rows")

    rows = data["description_paraphrases"]
    require(isinstance(rows, list) and len(rows) == 4
            and len({r["directory_row_id"] for r in rows}) == 4, "only four read sources")
    for offset, row in enumerate(rows):
        i = offset + 6
        key = f"short:scouts:holodeck_rescues:{i:02d}"
        video_id = VIDEO_IDS[offset]
        source = candidates.get(key)
        require(set(row) == {"directory_row_id", "publisher_video_id", "youtube_video_locator",
                "publisher_video_display_date", "publisher_video_title", "description_locator",
                "description_class", "synopsis"}, "unreviewed description row field")
        require(row["directory_row_id"] == key and source is not None, "wrong discovery row")
        require(source["identity_scope"] == "SOURCE_LOCAL" and source["medium"] == "SHORT_FORM"
                and source["candidate_kind"] == "SCRIPTED_SHORT"
                and source["verification_status"] == "UNVERIFIED_METADATA"
                and source["source_group"] == "publisher:paramount"
                and source["admission_effect"] == "NONE" and source["coverage_effect"] == "NONE"
                and source["context"] == f"SCOUTS · HOLODECK RESCUES #{i}",
                "discovery row identity/coverage promoted")
        require(exact_url(source["source_locator"], "youtu.be", "/" + video_id)
                and row["publisher_video_id"] == video_id
                and exact_url(row["youtube_video_locator"], "www.youtube.com", "/watch", "v=" + video_id),
                "source video ID, exact locator, or host changed")
        require(row["publisher_video_display_date"] == DISPLAY_DATES[offset]
                and row["publisher_video_title"] == PUBLISHER_TITLES[offset],
                "first-party display metadata/alias changed")
        require(row["description_locator"] ==
                "Official YouTube video search result > Description > first episode-specific paragraph"
                and row["description_class"] == "PUBLISHER_DESCRIPTION_PARAPHRASE",
                "search description promoted to video plot evidence")
        synopsis = row["synopsis"]
        require(isinstance(synopsis, str) and 16 <= len(synopsis.split()) <= 55
                and "<" not in synopsis and "\n" not in synopsis,
                "missing/unsafe or overly long paraphrase")

    held = data["held_following_row"]
    require(set(held) == {"directory_row_id", "discovery_video_id", "source_locator",
                             "status", "reason", "synopsis"}, "unreviewed hold fields")
    require(held["directory_row_id"] == "short:scouts:holodeck_rescues:10"
            and held["discovery_video_id"] == "vlez2Dtu95E"
            and exact_url(held["source_locator"], "youtu.be", "/vlez2Dtu95E")
            and held["status"] == "HOLD_FIRST_PARTY_DESCRIPTION_NOT_RETRIEVED"
            and held["synopsis"] is None
            and isinstance(held["reason"], str) and "Derivative" in held["reason"],
            "unretrieved #10 first-party synopsis must remain held")
    source = candidates.get(held["directory_row_id"])
    require(source is not None and source["verification_status"] == "UNVERIFIED_METADATA"
            and source["identity_scope"] == "SOURCE_LOCAL"
            and source["admission_effect"] == "NONE" and source["coverage_effect"] == "NONE"
            and source["source_locator"] == held["source_locator"],
            "held #10 discovery crosswalk changed")
    return len(rows)


if __name__ == "__main__":
    print("SCOUTS_HOLODECK_06TO09_SOURCE_DESCRIPTION_OK:", validate(read_pinned()))
