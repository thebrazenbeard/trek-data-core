"""Validate Scouts publisher-search descriptions without claiming video content."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OBSERVATIONS = HERE / "observations.json"
CATALOG = ROOT / "explorer/discovery-catalog.json"
PINNED_OBSERVATIONS_SHA256 = "6faa60b57c7435e40d4bbfe8f534665804ff61db039990940bff9a25dddd0ae2"
VIDEO_IDS = ("j-KvjtSgfJs", "x1mIN62O00s", "PfaNbFeRCm4", "j3asH2YbKz8", "60SkYJy-_2U")
DISPLAY_DATES = ("2025-09-08", "2025-09-08", "2025-09-19", "2025-10-04", "2025-10-11")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def read_pinned() -> dict:
    raw = OBSERVATIONS.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINNED_OBSERVATIONS_SHA256,
            "publisher-description packet changed since source review")
    return json.loads(raw)


EXPECTED = read_pinned()


def correct_url(url: str, host: str, path: str, query: str = "") -> bool:
    parsed = urlsplit(url)
    return (parsed.scheme == "https" and parsed.netloc == host and parsed.path == path
            and parsed.query == query and parsed.username is None and parsed.password is None
            and parsed.port is None and not parsed.fragment)


def validate(data: dict, catalog: dict | None = None) -> int:
    require(isinstance(data, dict) and set(data) == set(EXPECTED), "unknown source packet fields")
    for key, value in EXPECTED.items():
        require(type(data[key]) is type(value) and data[key] == value,
                f"unreviewed observation text changed: {key}")
    require(data["schema_version"] == "trek-scouts-asteroid-publisher-description-v1"
            and data["proposal_only"] is True, "must remain proposal-only")
    require(data["source_access"] == "SEARCH_RETRIEVED_PUBLIC_YOUTUBE_VIDEO_DESCRIPTION_NOT_VIDEO_PAGE_OPENED",
            "search-result description must not be described as a directly opened page")
    require(data["verification_class"] == "PUBLISHER_DESCRIPTION_METADATA_READ_NOT_ANIMATION_VIEWED",
            "video metadata is not a watched episode")
    require(data["source_family"] == "publisher:paramount-nickelodeon-youtube"
            and data["publisher_channel_display_name"] == "Blaze and the Monster Machines"
            and data["independent_upstream_families"] == 1,
            "five channel descriptions are not independent sources")
    for effect in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                   "accepted_coverage_effect", "public_synopsis_release_effect",
                   "artwork_release_effect"):
        require(data[effect] == "NONE", f"protected effect {effect}")
    for flag in ("animations_viewed", "video_pages_opened", "source_bound", "close_read"):
        require(data[flag] is False, f"unsupported full-video/page claim {flag}")
    require(data["raw_source_page_sha256"] is None, "no YouTube response bytes held")

    catalog = catalog if catalog is not None else json.loads(CATALOG.read_text(encoding="utf-8"))
    require(catalog.get("data_status") == "DISCOVERY_ONLY"
            and catalog.get("admission_effect") == "NONE"
            and catalog.get("coverage_effect") == "NONE", "candidate catalog promoted")
    sources = catalog.get("rows")
    require(isinstance(sources, list), "missing candidates")
    candidates = {r.get("row_id"): r for r in sources}
    require(len(candidates) == len(sources), "duplicate discovery IDs")
    rows = data["description_paraphrases"]
    require(isinstance(rows, list) and len(rows) == data["short_count"] == 5
            and len({x["directory_row_id"] for x in rows}) == 5, "bounded five unique observations")
    for i, row in enumerate(rows, start=1):
        require(set(row) == {"directory_row_id", "publisher_video_id", "youtube_video_locator",
                "publisher_video_display_date", "description_locator", "description_class", "synopsis"},
                "unreviewed row schema")
        key = f"short:scouts:asteroid_blasters:{i:02d}"
        video_id = VIDEO_IDS[i - 1]
        source = candidates.get(key)
        require(row["directory_row_id"] == key and source is not None,
                "source-local Scouts candidate mismatch")
        require(source["medium"] == "SHORT_FORM" and source["candidate_kind"] == "SCRIPTED_SHORT"
                and source["identity_scope"] == "SOURCE_LOCAL"
                and source["verification_status"] == "UNVERIFIED_METADATA"
                and source["source_group"] == "publisher:paramount"
                and source["admission_effect"] == "NONE"
                and source["coverage_effect"] == "NONE"
                and source["context"] == f"SCOUTS · ASTEROID BLASTERS #{i}",
                "Scouts discovery identity cannot be admitted or regrouped")
        require(correct_url(source["source_locator"], "youtu.be", "/" + video_id),
                "accepted discovery publisher video ID changed")
        require(row["publisher_video_id"] == video_id and correct_url(
                row["youtube_video_locator"], "www.youtube.com", "/watch", "v=" + video_id),
                "YouTube search-result video source ID mismatch or spoof")
        require(row["publisher_video_display_date"] == DISPLAY_DATES[i - 1],
                "publisher video metadata date drift")
        require(row["description_locator"] ==
                "Official YouTube video search result > Description > first episode-specific paragraph",
                "source access field incorrectly promoted")
        require(row["description_class"] == "PUBLISHER_DESCRIPTION_PARAPHRASE",
                "publisher source utterance must not become audiovisual evidence")
        description = row["synopsis"]
        require(isinstance(description, str) and 17 <= len(description.split()) <= 50
                and "<" not in description and "\n" not in description,
                "publisher paraphrase missing or unsafe")
    return len(rows)


if __name__ == "__main__":
    print("SCOUTS_ASTEROID_PUBLISHER_DESCRIPTION_OK:", validate(read_pinned()))
