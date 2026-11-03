"""Check Scouts #6–#10 metadata paraphrases without audiovisual promotion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OBSERVATIONS = HERE / "observations.json"
CATALOG = ROOT / "explorer/discovery-catalog.json"
PINNED_OBSERVATIONS_SHA256 = "a6d6aee00fb4e2735265960427f3e700e5d104a075c3a516879d5a810aa03092"
VIDEO_IDS = ("Ps3cQdL1By0", "GtJpqUH3gTA", "6lnl4qzwHt8", "ODb0D3ZTgug", "fSRr1CGFYiY")
DISPLAY_DATES = ("2025-10-18", "2025-11-01", "2025-11-08", "2025-11-15", "2025-12-06")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def read_pinned() -> dict:
    raw = OBSERVATIONS.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINNED_OBSERVATIONS_SHA256,
            "unreviewed proposal observations bytes")
    return json.loads(raw)


EXPECTED = read_pinned()


def valid_url(raw: str, host: str, path: str, query: str = "") -> bool:
    url = urlsplit(raw)
    return (url.scheme == "https" and url.netloc == host and url.username is None
            and url.password is None and url.port is None and url.path == path
            and url.query == query and not url.fragment)


def validate(data: dict, catalog: dict | None = None) -> int:
    require(isinstance(data, dict) and set(data) == set(EXPECTED), "unexpected packet keys")
    for key, value in EXPECTED.items():
        require(type(data[key]) is type(value) and data[key] == value,
                f"unreviewed observation change: {key}")
    require(data["schema_version"] == "trek-scouts-asteroid-06to10-publisher-description-v1"
            and data["proposal_only"] is True, "proposal only")
    require(data["source_access"] == "SEARCH_RETRIEVED_PUBLIC_YOUTUBE_VIDEO_DESCRIPTION_NOT_VIDEO_PAGE_OPENED"
            and data["verification_class"] == "PUBLISHER_DESCRIPTION_METADATA_READ_NOT_ANIMATION_VIEWED",
            "publisher description search result cannot become video evidence")
    require(data["source_family"] == "publisher:paramount-nickelodeon-youtube"
            and data["publisher_channel_display_name"] == "Blaze and the Monster Machines"
            and data["independent_upstream_families"] == 1,
            "first-party channel is one corporate source family")
    for key in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                "accepted_coverage_effect", "public_synopsis_release_effect", "artwork_release_effect"):
        require(data[key] == "NONE", f"protected effect {key}")
    for key in ("animations_viewed", "video_pages_opened", "source_bound", "close_read"):
        require(data[key] is False, f"unsupported source access {key}")
    require(data["raw_source_page_sha256"] is None, "no captured raw video page bytes")

    catalog = catalog if catalog is not None else json.loads(CATALOG.read_text(encoding="utf-8"))
    require(catalog.get("data_status") == "DISCOVERY_ONLY"
            and catalog.get("admission_effect") == "NONE"
            and catalog.get("coverage_effect") == "NONE", "discovery catalog promoted")
    source_rows = catalog.get("rows")
    require(isinstance(source_rows, list), "missing discovery rows")
    by_id = {r.get("row_id"): r for r in source_rows}
    require(len(by_id) == len(source_rows), "duplicate discovery ID")
    rows = data["description_paraphrases"]
    require(isinstance(rows, list) and len(rows) == data["short_count"] == 5
            and len({r["directory_row_id"] for r in rows}) == 5, "five unique Scout source observations")
    for ix, row in enumerate(rows):
        number = ix + 6
        video_id = VIDEO_IDS[ix]
        key = f"short:scouts:asteroid_blasters:{number:02d}"
        require(set(row) == {"directory_row_id", "publisher_video_id", "youtube_video_locator",
                "publisher_video_display_date", "description_locator", "description_class", "synopsis"},
                "unexpected row keys")
        source = by_id.get(key)
        require(row["directory_row_id"] == key and source is not None, "wrong Scouts candidate")
        require(source["medium"] == "SHORT_FORM"
                and source["candidate_kind"] == "SCRIPTED_SHORT"
                and source["identity_scope"] == "SOURCE_LOCAL"
                and source["source_group"] == "publisher:paramount"
                and source["verification_status"] == "UNVERIFIED_METADATA"
                and source["admission_effect"] == "NONE"
                and source["coverage_effect"] == "NONE"
                and source["context"] == f"SCOUTS · ASTEROID BLASTERS #{number}",
                "candidate scope changed")
        require(valid_url(source["source_locator"], "youtu.be", "/" + video_id),
                "wrong accepted short URL")
        require(row["publisher_video_id"] == video_id and valid_url(
                row["youtube_video_locator"], "www.youtube.com", "/watch", "v=" + video_id),
                "source ID or publisher URL mismatch")
        require(row["publisher_video_display_date"] == DISPLAY_DATES[ix],
                "publisher display date changed")
        require(row["description_locator"] ==
                "Official YouTube video search result > Description > first episode-specific paragraph",
                "misleading source locator")
        require(row["description_class"] == "PUBLISHER_DESCRIPTION_PARAPHRASE", "unqualified video story")
        synopsis = row["synopsis"]
        require(isinstance(synopsis, str) and 17 <= len(synopsis.split()) <= 50
                and "<" not in synopsis and "\n" not in synopsis,
                "source-local publisher paraphrase missing or malformed")
    return len(rows)


if __name__ == "__main__":
    print("SCOUTS_ASTEROID_06TO10_DESCRIPTION_OK:", validate(read_pinned()))
