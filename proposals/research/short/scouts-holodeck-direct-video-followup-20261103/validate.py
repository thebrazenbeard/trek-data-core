"""Reproducible validation of five direct first-party video *description* observations.

This compiler never fetches a live YouTube page and never claims playback. The
raw-page hashes are time-specific retrieval receipts, not immutable publisher
versions. Source-relative title discrepancies remain separate observations.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OBSERVATIONS = HERE / "observations.json"
HISTORICAL = ROOT / "proposals/research/short/scouts-holodeck-06to09-descriptions-20261103/observations.json"
CATALOG = ROOT / "explorer/discovery-catalog.json"
PINNED_OBSERVATIONS_SHA256 = "bc40f22a7da0e8423e9c7bf0b1afc1b046637dbd174afa1aa1f1395587bfea04"
PINNED_HISTORICAL_SHA256 = "8610b331dc882c1aed933e0ae46a5469666cc7f61e45045222d94f754ec1b116"

VIDEO_IDS = ("-m7ISEuAhac", "cYRzkzu_zhg", "O5wUrGB_6qw", "TbZFOtuHpxk", "vlez2Dtu95E")
TITLE_HASHES = (
    "0f7f6892168fbedab00036ea64716467bde33b5df786d4350fd2473a54778f07",
    "5c605ea07992699e62cec8de2aa89e202f4dca76d76b0b39522991b3846f66ea",
    "114b0215dc18cf5cd8098d64275a6382252052b7d9e8b710de09bd1920d88bc2",
    "d6cd146bd1986938f2bb793beae872f928a0ae95707832747d2e1756c0120798",
    "2de4a4021425a1a9baaaa628158fe392d99087c862acf0130e19c89d09f19ec0",
)
DESCRIPTION_FINGERPRINTS = (
    "34a62eadf72c56379e65039f0755e166cb9d70e0b1eef4e37023d1595276cd54",
    "902fc9bcf986af7fbe158119c19467f87219901643290a5a3265ab3cc681d1f9",
    "56891e51d17223654b3e6729a931ef742ed465280df895e65c348733e906a5f8",
    "9eb34d098114d4cd59533bbd1b0f47925f214d609fd8b66b32f6f08acb728a97",
    "28fb5994edeecf38b66835ece60098d6b8a0b31dadab52c74cf5c5a0b05ee95a",
)
RAW_HTML_RETRIEVAL_SHA256 = (
    "0065eeae482404b7623e101b53d1b05f47e3b87696fd4d03291b64aa8a5ab357",
    "14333cfc4e0bdbcfd08dedea4a7d720056d4dc84fe73872724fe9247e893c199",
    "e4d5d4ac55f3a4f65ab404de95975b9caae2816f5c58647cad5c6df610dc0a30",
    "4c1bff5f5306d5819cdfb832c3554fbb3fba0fa552354afb8d26b2d639050dc1",
    "c0356bb62ae8a023ba0b674d092f3aeafec1492b346859bf2629b4cc7f0a07b1",
)
RAW_HTML_BYTES = (1389004, 1393499, 1494325, 1259036, 1410946)
PUBLISH_DATES = ("2026-02-14", "2026-02-28", "2026-03-07", "2026-03-16", "2026-03-21")
ROW_FIELDS = {
    "directory_row_id", "video_id", "video_page", "current_first_party_title",
    "first_party_publish_datetime", "title_sha256", "first_description_paragraph_sha256",
    "raw_html_retrieval_sha256", "raw_html_retrieval_bytes", "title_relation_to_historical_search",
    "new_synopsis_proposal",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_pinned() -> dict:
    raw = OBSERVATIONS.read_bytes()
    require(digest_bytes(raw) == PINNED_OBSERVATIONS_SHA256, "current followup snapshot changed")
    return json.loads(raw)


def read_historical() -> dict:
    raw = HISTORICAL.read_bytes()
    require(digest_bytes(raw) == PINNED_HISTORICAL_SHA256, "historical search receipt changed")
    return json.loads(raw)


EXPECTED = read_pinned()


def exact_url(value: object, video_id: str, host: str) -> bool:
    if not isinstance(value, str):
        return False
    parts = urlsplit(value)
    return (parts.scheme == "https" and parts.hostname == host and parts.netloc == host
            and parts.path == ("/watch" if host == "www.youtube.com" else "/" + video_id)
            and parts.query == ("v=" + video_id if host == "www.youtube.com" else "")
            and not parts.fragment and not parts.username and not parts.password)


def validate(data: dict, *, historical: dict | None = None, catalog: dict | None = None) -> int:
    require(isinstance(data, dict) and set(data) == set(EXPECTED), "unexpected followup document fields")
    require(data["schema_version"] == "trek-scouts-holodeck-direct-video-followup-v1"
            and data["proposal_only"] is True and data["observed_on_utc"] == "2026-11-03",
            "source-only observation identity changed")
    require(data["source_access"] == "DIRECT_YOUTUBE_VIDEO_PAGE_HTML_DESCRIPTION_READ_NOT_PLAYBACK"
            and data["source_family"] == "publisher:paramount-nickelodeon-youtube"
            and data["publisher_channel"] == "Blaze and the Monster Machines"
            and data["independent_upstream_families"] == 1,
            "first-party publisher lineage or evidence class changed")
    require(data["video_playback_performed"] is False and data["full_episodes_read"] is False
            and data["raw_html_bytes_committed"] is False, "false playback/full-source/binary claim")
    for field in ("accepted_work_effect", "accepted_evidence_effect", "accepted_coverage_effect",
                  "public_synopsis_release_effect", "artwork_release_effect"):
        require(data[field] == "NONE", f"protected effect promoted: {field}")
    require(data["historical_search_observation_path"] == str(HISTORICAL.relative_to(ROOT))
            and data["historical_search_observation_sha256"] == PINNED_HISTORICAL_SHA256,
            "historical source locator or fingerprint changed")

    historical = historical if historical is not None else read_historical()
    require(historical.get("source_access") == "SEARCH_RETRIEVED_PUBLIC_YOUTUBE_VIDEO_DESCRIPTION_NOT_VIDEO_PAGE_OPENED"
            and len(historical.get("description_paraphrases", [])) == 4,
            "older search-result source class changed")
    prior = historical["description_paraphrases"]
    held = historical["held_following_row"]
    require(held["directory_row_id"] == "short:scouts:holodeck_rescues:10"
            and held["synopsis"] is None
            and held["status"] == "HOLD_FIRST_PARTY_DESCRIPTION_NOT_RETRIEVED",
            "historical #10 hold must remain historical evidence")

    catalog = catalog if catalog is not None else json.loads(CATALOG.read_text(encoding="utf-8"))
    require(catalog.get("data_status") == "DISCOVERY_ONLY" and catalog.get("admission_effect") == "NONE"
            and catalog.get("coverage_effect") == "NONE", "discovery ledger promoted")
    rows_by_id = {r["row_id"]: r for r in catalog["rows"]}
    require(len(rows_by_id) == len(catalog["rows"]), "duplicate discovery row IDs")
    rows = data["observations"]
    require(isinstance(rows, list) and len(rows) == 5, "direct first-party batch must have five rows")
    require(len({r.get("directory_row_id") for r in rows if isinstance(r, dict)}) == 5,
            "duplicate source-local row IDs")

    for offset, row in enumerate(rows):
        require(isinstance(row, dict) and set(row) == ROW_FIELDS, "unreviewed direct-page row fields")
        video_id = VIDEO_IDS[offset]
        directory_id = f"short:scouts:holodeck_rescues:{offset + 6:02d}"
        require(row["directory_row_id"] == directory_id and row["video_id"] == video_id,
                "source-local video assignment changed")
        require(exact_url(row["video_page"], video_id, "www.youtube.com"),
                "source video URL or host changed")
        source = rows_by_id.get(directory_id)
        require(source is not None and source["identity_scope"] == "SOURCE_LOCAL"
                and source["medium"] == "SHORT_FORM" and source["candidate_kind"] == "SCRIPTED_SHORT"
                and source["verification_status"] == "UNVERIFIED_METADATA"
                and source["source_group"] == "publisher:paramount"
                and source["admission_effect"] == "NONE" and source["coverage_effect"] == "NONE"
                and source["context"] == f"SCOUTS · HOLODECK RESCUES #{offset + 6}"
                and exact_url(source["source_locator"], video_id, "youtu.be"),
                "unadmitted discovery crosswalk changed")
        require(isinstance(row["current_first_party_title"], str)
                and digest_bytes(row["current_first_party_title"].encode("utf-8")) == TITLE_HASHES[offset]
                and row["title_sha256"] == TITLE_HASHES[offset],
                "direct first-party title/fingerprint changed")
        try:
            pub_date = datetime.fromisoformat(row["first_party_publish_datetime"])
            require(pub_date.tzinfo is not None and pub_date.date().isoformat() == PUBLISH_DATES[offset],
                    "published timestamp/date changed")
        except (ValueError, TypeError) as exc:
            raise ValueError("published timestamp/date changed") from exc
        require(row["first_description_paragraph_sha256"] == DESCRIPTION_FINGERPRINTS[offset]
                and row["raw_html_retrieval_sha256"] == RAW_HTML_RETRIEVAL_SHA256[offset]
                and type(row["raw_html_retrieval_bytes"]) is int
                and row["raw_html_retrieval_bytes"] == RAW_HTML_BYTES[offset],
                "first-party description fingerprint or retrieval receipt changed")
        if offset < 4:
            require(prior[offset]["publisher_video_id"] == video_id and
                    prior[offset]["directory_row_id"] == directory_id,
                    "historical publisher search ID assignment changed")
            relation = ("MATCHES_SOURCE_RELATIVE" if
                        row["current_first_party_title"] == prior[offset]["publisher_video_title"]
                        else "DIFFERS_SOURCE_RELATIVE")
            require(row["title_relation_to_historical_search"] == relation,
                    "separate historical/current publisher title state collapsed")
            require(row["new_synopsis_proposal"] is None,
                    "earlier four synopses must not be rewritten in this followup")
        else:
            require(row["title_relation_to_historical_search"] ==
                    "PREVIOUSLY_HELD_NOW_DIRECT_PAGE_OBSERVED", "old #10 hold silently overwritten")
            synopsis = row["new_synopsis_proposal"]
            require(isinstance(synopsis, str) and 15 <= len(synopsis.split()) <= 44
                    and "<" not in synopsis and "\n" not in synopsis,
                    "unsafe or unsupported fifth original publisher synopsis")

    # The digest pins every source-relative observation after the guards above
    # have been exercised; it prevents undetected free-form paraphrase edits.
    for key, value in EXPECTED.items():
        require(type(data[key]) is type(value) and data[key] == value,
                f"unreviewed current-page followup content: {key}")
    return len(rows)


if __name__ == "__main__":
    print("SCOUTS_HOLODECK_DIRECT_VIDEO_FOLLOWUP_OK:", validate(read_pinned()))
