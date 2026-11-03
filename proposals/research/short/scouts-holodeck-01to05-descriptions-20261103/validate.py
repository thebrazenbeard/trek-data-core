"""Fail-closed validator for Scouts Holodeck 1–5 publisher-search summaries.

This checks proposal provenance, not animation content or source admissibility.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OBSERVATIONS = HERE / "observations.json"
CATALOG = ROOT / "explorer/discovery-catalog.json"
PINNED_OBSERVATIONS_SHA256 = "b2459678c03bd7b2cbadc297f662b178e81e4c266d451a8555bd1c3808b9cf9e"
VIDEO_IDS = ("69jkEMz87co", "6AAJlEn3DeY", "fybF9xOzXs4", "M02cKstXmjo", "dZznmiZYV-A")
DISPLAY_DATES = ("2026-01-23", "2026-01-24", "2026-01-25", "2026-01-26", "2026-02-06")
PUBLISHER_TITLES = (
    "Holodeck Rescues #1 | Star Trek Scouts Save a Baby Animal! 🌋 | Star Trek: Scouts",
    "Holodeck Rescues #2 | Star Trek Scouts Save a Baby Monkey in Outer Space! 🐵 | Star Trek: Scouts",
    "Holodeck Rescues #3 | Star Trek Scouts Stop a Mudslide & Save Dinosaurs! 🦖 | Star Trek: Scouts",
    "Roo Helps a Space Whale Stuck in a Black Hole! 🐋🌟 | Star Trek: Scouts | Holodeck Rescues Episode #4",
    "Holodeck Rescues #5 | Star Trek Scouts vs. Shadowtrix in Underwater Mission! 🌊🌟 | Star Trek: Scouts",
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def read_pinned() -> dict:
    raw = OBSERVATIONS.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINNED_OBSERVATIONS_SHA256,
            "Holodeck publisher-description packet changed since source review")
    return json.loads(raw)


EXPECTED = read_pinned()


def correct_url(url: str, host: str, path: str, query: str = "") -> bool:
    parsed = urlsplit(url)
    return (parsed.scheme == "https" and parsed.netloc == host and parsed.path == path
            and parsed.query == query and parsed.username is None and parsed.password is None
            and parsed.port is None and not parsed.fragment)


def validate(data: dict, catalog: dict | None = None) -> int:
    require(isinstance(data, dict) and set(data) == set(EXPECTED), "unexpected source packet fields")
    for key, value in EXPECTED.items():
        require(type(data[key]) is type(value) and data[key] == value,
                f"unreviewed observation changed: {key}")
    require(data["schema_version"] == "trek-scouts-holodeck-01to05-publisher-description-v1"
            and data["proposal_only"] is True, "must remain source-only proposal")
    require(data["source_access"] == "SEARCH_RETRIEVED_PUBLIC_YOUTUBE_VIDEO_DESCRIPTION_NOT_VIDEO_PAGE_OPENED",
            "search result cannot be called a directly opened publisher page")
    require(data["verification_class"] == "PUBLISHER_DESCRIPTION_METADATA_READ_NOT_ANIMATION_VIEWED"
            and data["source_family"] == "publisher:paramount-nickelodeon-youtube"
            and data["publisher_channel_display_name"] == "Blaze and the Monster Machines"
            and data["independent_upstream_families"] == 1,
            "publisher metadata source class or corporate family changed")
    for effect in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                   "accepted_coverage_effect", "public_synopsis_release_effect", "artwork_release_effect"):
        require(data[effect] == "NONE", f"protected effect changed: {effect}")
    for flag in ("animations_viewed", "video_pages_opened", "source_bound", "close_read"):
        require(data[flag] is False, f"unsupported direct-source claim: {flag}")
    require(data["raw_source_page_sha256"] is None, "no video-page response bytes held")

    catalog = catalog if catalog is not None else json.loads(CATALOG.read_text(encoding="utf-8"))
    require(catalog.get("data_status") == "DISCOVERY_ONLY"
            and catalog.get("admission_effect") == "NONE"
            and catalog.get("coverage_effect") == "NONE", "catalog silently promoted")
    sources = catalog.get("rows")
    require(isinstance(sources, list), "missing discovery rows")
    candidates = {r.get("row_id"): r for r in sources}
    require(len(candidates) == len(sources), "duplicate discovery row IDs")
    rows = data["description_paraphrases"]
    require(isinstance(rows, list) and len(rows) == data["short_count"] == 5
            and len({r["directory_row_id"] for r in rows}) == 5, "must be five unique sources")
    for index, row in enumerate(rows, start=1):
        require(set(row) == {"directory_row_id", "publisher_video_id", "youtube_video_locator",
                "publisher_video_display_date", "publisher_video_title", "description_locator",
                "description_class", "synopsis"}, "unreviewed row fields")
        key = f"short:scouts:holodeck_rescues:{index:02d}"
        source = candidates.get(key)
        video_id = VIDEO_IDS[index - 1]
        require(row["directory_row_id"] == key and source is not None, "wrong directory row")
        require(source["medium"] == "SHORT_FORM" and source["candidate_kind"] == "SCRIPTED_SHORT"
                and source["identity_scope"] == "SOURCE_LOCAL"
                and source["verification_status"] == "UNVERIFIED_METADATA"
                and source["source_group"] == "publisher:paramount"
                and source["admission_effect"] == "NONE" and source["coverage_effect"] == "NONE"
                and source["context"] == f"SCOUTS · HOLODECK RESCUES #{index}",
                "discovery row regrouped/admitted")
        require(correct_url(source["source_locator"], "youtu.be", "/" + video_id),
                "accepted discovery video ID changed")
        require(row["publisher_video_id"] == video_id and correct_url(
                row["youtube_video_locator"], "www.youtube.com", "/watch", "v=" + video_id),
                "publisher video locator spoof or ID mismatch")
        require(row["publisher_video_display_date"] == DISPLAY_DATES[index - 1],
                "publisher metadata date drift")
        require(row["publisher_video_title"] == PUBLISHER_TITLES[index - 1],
                "publisher video title variant changed")
        require(row["description_locator"] ==
                "Official YouTube video search result > Description > first episode-specific paragraph"
                and row["description_class"] == "PUBLISHER_DESCRIPTION_PARAPHRASE",
                "summary promoted to video plot evidence")
        synopsis = row["synopsis"]
        require(isinstance(synopsis, str) and 17 <= len(synopsis.split()) <= 50
                and "<" not in synopsis and "\n" not in synopsis,
                "missing, overly long, or unsafe original synopsis")
    return len(rows)


if __name__ == "__main__":
    print("SCOUTS_HOLODECK_01TO05_PUBLISHER_DESCRIPTION_OK:", validate(read_pinned()))
