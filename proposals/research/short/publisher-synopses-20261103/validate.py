"""Validate a publisher-description packet; never promote short-video research."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OBSERVATIONS = HERE / "observations.json"
DISCOVERY = ROOT / "explorer/discovery-catalog.json"
PINNED_OBSERVATIONS_SHA256 = "91862225de0740c18b545de84efb4c9c84b0538d00888a55c4af1f78e3f2fd96"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_pinned() -> dict:
    raw = OBSERVATIONS.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINNED_OBSERVATIONS_SHA256,
            "source-reviewed short synopsis packet changed without new review")
    return json.loads(raw)


EXPECTED = read_pinned()
DATES = (
    "2018-10-04", "2018-11-08", "2018-12-06", "2019-01-03",
    "2019-10-05", "2019-10-10", "2019-11-14", "2019-12-12",
    "2019-12-12", "2020-01-09",
)


def verified_publisher_url(raw: str, host: str, path_prefix: str) -> bool:
    url = urlsplit(raw)
    return (url.scheme == "https" and url.netloc == host and url.username is None
            and url.password is None and url.port is None and not url.query
            and not url.fragment and url.path.startswith(path_prefix))


def validate(data: dict, discovery: dict | None = None) -> int:
    require(isinstance(data, dict) and set(data) == set(EXPECTED), "unexpected observation fields")
    for key, value in EXPECTED.items():
        require(type(data[key]) is type(value) and data[key] == value,
                f"unreviewed publisher-description mutation: {key}")
    require(data["schema_version"] == "trek-short-publisher-description-paraphrase-v1", "schema drift")
    require(data["proposal_only"] is True, "must be candidate-only")
    require(data["source_access"] == "RENDERED_FIRST_PARTY_WEB_DESCRIPTIONS_READ_NO_VIDEO_VIEWED",
            "website description reading is not a video close read")
    require(data["verification_class"] == "PUBLISHER_DESCRIPTION_FIELD_READ_NOT_SHORT_VIEWED",
            "not an admitted screenplay or video")
    require(data["source_family"] == "publisher:paramount-cbs-startrek"
            and data["independent_upstream_families"] == 1,
            "all publisher properties share a corporate independence family")
    for effect in ("accepted_source_work_binding_effect", "accepted_evidence_effect",
                   "accepted_coverage_effect", "public_synopsis_release_effect",
                   "artwork_release_effect"):
        require(data[effect] == "NONE", f"protected effect {effect}")
    for flag in ("full_short_viewed", "source_bound", "close_read"):
        require(data[flag] is False, f"unsupported coverage claim {flag}")
    require(data["raw_source_page_sha256"] is None,
            "web response bytes were not archived for a stable checksum")
    require(verified_publisher_url(data["source_guide"],
            "www.paramountplus.com", "/shows/star-trek-short-treks/episodes/"),
            "publisher guide host or path is not authentic")
    require(verified_publisher_url(data["source_2018_schedule"],
            "www.paramountplus.com", "/shows/star-trek-short-treks/news/"),
            "2018 schedule host or path is not authentic")
    require(verified_publisher_url(data["source_2019_schedule"],
            "www.startrek.com", "/news/"), "2019 schedule host or path is not authentic")
    require(verified_publisher_url(data["source_2020_schedule_crosscheck"],
            "www.paramountplus.com", "/shows/star-trek-short-treks/news/"),
            "2020 schedule host or path is not authentic")

    discovery = discovery if discovery is not None else json.loads(DISCOVERY.read_text(encoding="utf-8"))
    require(discovery.get("data_status") == "DISCOVERY_ONLY" and
            discovery.get("admission_effect") == "NONE" and
            discovery.get("coverage_effect") == "NONE", "candidate inventory has changed status")
    candidates = discovery.get("rows")
    require(isinstance(candidates, list), "missing discovery rows")
    by_id = {r.get("row_id"): r for r in candidates}
    require(len(by_id) == len(candidates), "duplicate discovery row IDs")
    observations = data["description_paraphrases"]
    require(isinstance(observations, list) and len(observations) == data["short_count"] == 10,
            "bounded ten Short Treks packet")
    require(len({r["directory_row_id"] for r in observations}) == 10,
            "duplicate short observation")
    for index, row in enumerate(observations, start=1):
        require(set(row) == {"directory_row_id", "title", "publisher_announcement_title",
                "publisher_guide_slot", "publisher_announced_date", "announcement_year_inferred",
                "guide_description_locator", "description_class", "synopsis"},
                "unexpected short description field")
        identifier = f"short:short-treks-{index:02d}"
        source = by_id.get(identifier)
        require(row["directory_row_id"] == identifier and source is not None,
                "discovery Short Treks row mismatch")
        require(source["medium"] == "SHORT_FORM" and source["candidate_kind"] == "SCRIPTED_SHORT"
                and source["identity_scope"] == "SOURCE_LOCAL"
                and source["source_group"] == "publisher:paramount"
                and source["source_locator"] == data["source_guide"]
                and source["verification_status"] == "UNVERIFIED_METADATA"
                and source["admission_effect"] == "NONE" and source["coverage_effect"] == "NONE",
                "must not treat a discovery lead as admitted short content")
        require(row["title"] == source["title"] and row["publisher_announcement_title"] == source["title"],
                "title identity or announcement alias requires source-local re-review")
        require(row["publisher_guide_slot"] == f"S1E{index}" and
                source["context"] == f"short-treks · S1E{index}",
                "publisher catalog slot mismatch")
        require(row["guide_description_locator"] ==
                f"Episode Guide > {source['title']} > S1E{index} > description paragraph",
                "source paragraph locator drift")
        require(row["publisher_announced_date"] == DATES[index - 1]
                and bool(re.fullmatch(r"20\d{2}-\d{2}-\d{2}", row["publisher_announced_date"])),
                "publisher announcement date changed")
        require(row["announcement_year_inferred"] is (index in (4, 10)),
                "publication-year inference must stay visible across New Year")
        require(row["description_class"] == "PUBLISHER_DESCRIPTION_PARAPHRASE",
                "cannot upgrade a source description to viewed audiovisual evidence")
        summary = row["synopsis"]
        require(isinstance(summary, str) and 15 <= len(summary.split()) <= 55 and
                "\n" not in summary and "<" not in summary and "http" not in summary.lower(),
                "short publisher-description paraphrase absent or malformed")
    return len(observations)


if __name__ == "__main__":
    print("SHORT_PUBLISHER_DESCRIPTION_PROPOSAL_OK:", validate(read_pinned()))
