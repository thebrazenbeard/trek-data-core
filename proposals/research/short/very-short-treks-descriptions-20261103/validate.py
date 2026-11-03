"""Fail closed on source-relative very Short Treks promo premise descriptions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OBSERVATIONS = HERE / "observations.json"
CATALOG = ROOT / "explorer/discovery-catalog.json"
PINNED_OBSERVATIONS_SHA256 = "612485b687116757a8f0dcc5f9d971e27f53522bc3e2e73365000e87811d7d5a"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def read_pinned() -> dict:
    raw = OBSERVATIONS.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINNED_OBSERVATIONS_SHA256,
            "independent review is tied to exact observation bytes")
    return json.loads(raw)


EXPECTED = read_pinned()
SCHEDULE_DATES = ("2023-09-08", "2023-09-13", "2023-09-20", "2023-09-27", "2023-10-04")
VIDEO_SLUGS = ("skin-a-cat", "holiday-party", "worst-contact",
               "holograms-all-the-way-down", "walk-dont-run")


def official_url(raw: str, required_path: str) -> bool:
    url = urlsplit(raw)
    return (url.scheme == "https" and url.netloc == "www.startrek.com"
            and url.username is None and url.password is None and url.port is None
            and not url.query and not url.fragment and url.path == required_path)


def validate(data: dict, catalog: dict | None = None) -> int:
    require(isinstance(data, dict) and set(data) == set(EXPECTED), "observation keys changed")
    for key, value in EXPECTED.items():
        require(type(data[key]) is type(value) and data[key] == value,
                f"unreviewed observation change: {key}")
    require(data["schema_version"] == "trek-very-short-promotional-publisher-description-v1"
            and data["proposal_only"] is True, "proposal schema/status")
    require(data["verification_class"] == "PUBLISHER_PREMISE_ONLY_FOUR_AND_TOPIC_ONLY_ONE"
            and data["source_access"] == "RENDERED_OFFICIAL_VIDEO_LANDING_PAGE_TEXT_READ_NO_ANIMATION_VIEWED",
            "landing page metadata is not a viewed animation")
    require(data["source_family"] == "publisher:startrek.com"
            and data["independent_upstream_families"] == 1,
            "same upstream publisher across five pages")
    require(official_url(data["publisher_launch_source"],
            "/en-un/news/star-trek-very-short-treks-announce"), "unsafe launch URL")
    for effect in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                   "accepted_coverage_effect", "public_synopsis_release_effect",
                   "artwork_release_effect"):
        require(data[effect] == "NONE", f"unapproved protected effect {effect}")
    for flag in ("animated_shorts_viewed", "source_bound", "close_read"):
        require(data[flag] is False, f"unsupported close-read claim {flag}")
    require(data["raw_source_page_sha256"] is None, "source bytes not archived")
    require(data["short_count"] == 5 and data["qualified_premises"] == 4
            and data["plot_synopsis_pending"] == 1, "do not fabricate fifth plot")

    catalog = catalog if catalog is not None else json.loads(CATALOG.read_text(encoding="utf-8"))
    require(catalog.get("data_status") == "DISCOVERY_ONLY"
            and catalog.get("coverage_effect") == "NONE"
            and catalog.get("admission_effect") == "NONE", "catalog admission drift")
    all_rows = catalog.get("rows")
    require(isinstance(all_rows, list), "missing catalog rows")
    by_id = {r.get("row_id"): r for r in all_rows}
    require(len(by_id) == len(all_rows), "duplicate candidate row IDs")

    rows = data["description_paraphrases"]
    require(isinstance(rows, list) and len(rows) == 5
            and len({r["directory_row_id"] for r in rows}) == 5, "five distinct entries")
    for i, row in enumerate(rows, start=1):
        require(set(row) == {"directory_row_id", "directory_title", "publisher_video_title",
                "publisher_title_variation", "publisher_video_locator",
                "publisher_video_page_published_on", "publisher_announced_schedule_date",
                "source_section", "description_class", "synopsis"},
                "unexpected row structure")
        key = f"short:very-short-treks-{i:02d}"
        candidate = by_id.get(key)
        require(row["directory_row_id"] == key and candidate is not None, "wrong local row")
        require(candidate["medium"] == "SHORT_FORM"
                and candidate["candidate_kind"] == "PROMOTIONAL_ANIMATION"
                and candidate["identity_scope"] == "SOURCE_LOCAL"
                and candidate["source_group"] == "publisher:paramount"
                and candidate["source_locator"] == data["publisher_launch_source"]
                and candidate["verification_status"] == "UNVERIFIED_METADATA"
                and candidate["coverage_effect"] == "NONE"
                and candidate["admission_effect"] == "NONE"
                and candidate["context"] == f"very-short-treks · ANNOUNCED_RELEASE_{i:02d}",
                "do not silently alter source-relative promotional identity")
        require(row["directory_title"] == candidate["title"], "discovery title mismatch")
        require(row["publisher_video_page_published_on"] == SCHEDULE_DATES[i - 1]
                and row["publisher_announced_schedule_date"] == SCHEDULE_DATES[i - 1],
                "publisher publication/schedule date mismatch")
        require(official_url(row["publisher_video_locator"],
                "/videos/very-short-treks-" + VIDEO_SLUGS[i - 1]),
                "spoofed or swapped official video landing page")
        expected_variation = "CAPITALIZATION_ONLY" if i == 1 else (
            "PUNCTUATION_DIFFERENCE" if i == 4 else "NONE")
        require(row["publisher_title_variation"] == expected_variation,
                "publisher-vs-discovery title alias distinction lost")
        if i == 1:
            require(row["publisher_video_title"] == "Skin A Cat", "capitalization observation")
        elif i == 4:
            require(row["publisher_video_title"] == "Holograms All the Way Down", "comma difference")
        else:
            require(row["publisher_video_title"] == candidate["title"], "publisher title differs")
        if i == 4:
            require(row["description_class"] == "PUBLISHER_TOPIC_ONLY_PENDING_PLOT_SYNOPSIS"
                    and row["synopsis"] is None
                    and "Holodecktastic!" in row["source_section"],
                    "no specific plot exists in the source; synopsis must remain null")
        else:
            require(row["description_class"] == "PUBLISHER_PREMISE_PARAPHRASE",
                    "publisher premise wrongly promoted to video close-read")
            summary = row["synopsis"]
            require(isinstance(summary, str) and 13 <= len(summary.split()) <= 48
                    and "<" not in summary and "\n" not in summary,
                    "invalid publisher premise description")
    return len(rows)


if __name__ == "__main__":
    print("VERY_SHORT_PUBLISHER_DESCRIPTION_OK:", validate(read_pinned()))
