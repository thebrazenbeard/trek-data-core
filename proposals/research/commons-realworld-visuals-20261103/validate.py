"""Fail-closed schema review for three SOURCE-CLAIM-ONLY Commons photo candidates.

This does not validate underlying Star Trek/performer rights or admit images.
Rechecking the pinned Commons revisions and JPEG bytes is a separate live probe.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "records.json"
HEX40 = re.compile(r"[a-f0-9]{40}\Z")
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
ROOT_KEYS = {
    "schema_version", "proposal_id", "data_status", "baseline_main_commit",
    "observed_on_utc", "actor", "admission_effect", "coverage_effect", "work_effect",
    "entity_reconciliation_effect", "public_artwork_release_effect", "image_files_committed",
    "image_urls_in_public_sidecar", "source_policy", "evidence_limit", "candidate_count", "candidates",
}
RECORD_KEYS = {
    "candidate_id", "subject_kind", "subject_label", "source_described_context",
    "source_claim_scope", "work_or_episode_row_id", "character_identity_inferred",
    "commons_file_title", "commons_file_page", "commons_pinned_revision", "commons_page_html_bytes",
    "commons_page_html_sha256", "imageinfo_api_response_sha256", "imageinfo_api_query",
    "original_jpeg_bytes", "original_jpeg_width", "original_jpeg_height", "original_jpeg_mime",
    "original_jpeg_sha1", "original_jpeg_sha256", "image_hash_observation", "photographer",
    "photographer_source", "photo_license", "photo_license_url", "commons_flickr_license_review",
    "attribution_text", "subject_rights_status", "copyright_scope", "proposed_display_role",
    "release_status", "public_asset_path", "public_image_url",
}


class Refused(ValueError):
    pass


def require(condition, reason: str) -> None:
    if not condition:
        raise Refused(reason)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load_packet(path: Path = PACKET):
    require(path.is_file() and not path.is_symlink(), "missing or symlinked proposal")
    raw = path.read_bytes()
    require(0 < len(raw) < 100_000, "oversized or empty proposal")
    return json.loads(raw, object_pairs_hook=unique)


def same_commons_title(page_url: str, revision_url: str, title: str) -> bool:
    try:
        page = urlsplit(page_url)
        rev = urlsplit(revision_url)
        query = parse_qs(rev.query)
        return (
            page.scheme == rev.scheme == "https" and
            page.netloc == rev.netloc == "commons.wikimedia.org" and
            not page.query and not page.fragment and not rev.fragment and
            unquote(page.path.removeprefix("/wiki/")).replace("_", " ") == title and
            rev.path == "/w/index.php" and
            query.get("title") == [title.replace(" ", "_")] and
            len(query) == 2 and re.fullmatch(r"[1-9][0-9]{7,12}", query.get("oldid", [""])[0]) is not None
        )
    except (ValueError, IndexError):
        return False


def validate(data) -> dict:
    require(isinstance(data, dict) and set(data) == ROOT_KEYS, "proposal envelope shape drift")
    require(data["schema_version"] == "1.0.0" and
            data["proposal_id"] == "commons-realworld-visuals-20261103" and
            data["data_status"] == "PROPOSAL_ONLY_INDEPENDENT_RIGHTS_AND_SUBJECT_REVIEW_REQUIRED" and
            data["observed_on_utc"] == "2026-11-03" and
            data["baseline_main_commit"] == "a0494934782963b9a7f344cf50ed83191e08bf95" and
            data["actor"] == "chatgpt.trek.consolidator.source_discovery" and
            data["source_policy"] == "COMMONS_PRIMARY_FILE_PAGE_AND_DIRECT_IMAGEINFO_PLUS_FLICKR_REVIEW" and
            data["evidence_limit"] == "COMMONS_DESCRIPTION_ESTABLISHES_SOURCE_CLAIM_NOT_PRODUCTION_OBJECT_PROVENANCE_OR_LICENSE_TO_UNDERLYING_IP",
            "proposal source/methodology envelope drift")
    require(all(data[key] == "NONE" for key in ("admission_effect", "coverage_effect", "work_effect",
            "entity_reconciliation_effect", "public_artwork_release_effect")) and
            type(data["image_files_committed"]) is int and data["image_files_committed"] == 0 and
            type(data["image_urls_in_public_sidecar"]) is int and data["image_urls_in_public_sidecar"] == 0,
            "public release or coverage promotion forbidden")
    rows = data["candidates"]
    require(isinstance(rows, list) and type(data["candidate_count"]) is int and
            data["candidate_count"] == len(rows) == 3, "proposal row count mismatch")
    seen_ids, seen_digests, kinds = set(), set(), set()
    for row in rows:
        require(isinstance(row, dict) and set(row) == RECORD_KEYS, "candidate shape drift")
        candidate_id = row["candidate_id"]
        kind = row["subject_kind"]
        require(isinstance(candidate_id, str) and re.fullmatch(r"commons-[a-z0-9-]{8,100}", candidate_id)
                is not None and candidate_id not in seen_ids, "duplicate or unsafe candidate ID")
        require(kind in ("REAL_WORLD_PERFORMER_AT_EVENT", "EXHIBITED_PRODUCTION_OBJECT") and
                isinstance(row["subject_label"], str) and 5 <= len(row["subject_label"]) <= 100 and
                isinstance(row["source_described_context"], str) and
                20 <= len(row["source_described_context"]) <= 250, "unsupported subject scope")
        require(row["source_claim_scope"] in ("COMMONS_FILE_DESCRIPTION_ONLY",
                "COMMONS_FILE_DESCRIPTION_ONLY_PRODUCTION_USE_UNVERIFIED") and
                row["work_or_episode_row_id"] is None and row["character_identity_inferred"] is False,
                "real-world photo cannot silently bind episode/character identity")
        require(isinstance(row["commons_file_title"], str) and
                row["commons_file_title"].startswith("File:") and
                same_commons_title(row["commons_file_page"], row["commons_pinned_revision"],
                                   row["commons_file_title"]), "Commons page/revision identity mismatch")
        require(type(row["commons_page_html_bytes"]) is int and
                5_000 < row["commons_page_html_bytes"] < 1_000_000 and
                all(isinstance(row[key], str) and HEX64.fullmatch(row[key]) is not None for key in
                    ("commons_page_html_sha256", "imageinfo_api_response_sha256", "original_jpeg_sha256")) and
                isinstance(row["original_jpeg_sha1"], str) and
                HEX40.fullmatch(row["original_jpeg_sha1"]) is not None and
                row["original_jpeg_sha256"] not in seen_digests and
                row["imageinfo_api_query"] == "action=query;prop=imageinfo;iiprop=size|sha1|mime|extmetadata|url;format=json",
                "untraceable or duplicate source/image hash receipt")
        require(type(row["original_jpeg_bytes"]) is int and
                100_000 < row["original_jpeg_bytes"] < 12_000_000 and
                type(row["original_jpeg_width"]) is int and 200 <= row["original_jpeg_width"] < 10_000 and
                type(row["original_jpeg_height"]) is int and 200 <= row["original_jpeg_height"] < 10_000 and
                row["original_jpeg_mime"] == "image/jpeg" and
                row["image_hash_observation"] == "DIRECT_BYTES_IN_MEMORY_SHA1_MATCHES_COMMONS_IMAGEINFO_NO_FILE_SAVED",
                "unreviewed JPEG identity")
        photographer = row["photographer"]
        flickr = urlsplit(row["photographer_source"])
        require(photographer in ("Gage Skidmore", "Joe Ross") and
                flickr.scheme == "https" and flickr.netloc == "www.flickr.com" and
                flickr.path.startswith("/photos/") and not flickr.query and not flickr.fragment and
                row["photo_license"] == "CC-BY-SA-2.0" and
                row["photo_license_url"] == "https://creativecommons.org/licenses/by-sa/2.0" and
                row["commons_flickr_license_review"] in (
                    "FLICKREVIEWR_CONFIRMED_CC_BY_SA_2_0_ON_2017_02_13",
                    "FLICKREVIEWR_2_CONFIRMED_CC_BY_SA_2_0_ON_2023_06_15") and
                isinstance(row["attribution_text"], str) and photographer in row["attribution_text"] and
                "CC BY-SA 2.0" in row["attribution_text"] and
                len(row["attribution_text"]) <= 180,
                "photographer credit/license provenance invalid")
        require(row["copyright_scope"] == "PHOTOGRAPH_LICENSE_ONLY_NOT_ALL_DEPICTED_SUBJECT_RIGHTS" and
                isinstance(row["subject_rights_status"], str) and
                row["subject_rights_status"].endswith("NOT_ASSESSED") and
                row["release_status"] == "HOLD_INDEPENDENT_RIGHTS_AND_SUBJECT_REVIEW" and
                row["proposed_display_role"] in (
                    "PERFORMER_EVENT_PHOTO_NOT_EPISODE_STILL",
                    "MUSEUM_OBJECT_PHOTO_NOT_EPISODE_STILL_OR_CANON_ASSERTION") and
                row["public_asset_path"] is None and row["public_image_url"] is None,
                "candidate cannot self-authorize public display or source assertion")
        seen_ids.add(candidate_id)
        seen_digests.add(row["original_jpeg_sha256"])
        kinds.add(kind)
    require(kinds == {"REAL_WORLD_PERFORMER_AT_EVENT", "EXHIBITED_PRODUCTION_OBJECT"},
            "real-world subject-class diversity lost")
    return {"status": "PROPOSAL_ONLY", "candidates": len(rows), "release": 0, "coverage": 0}


if __name__ == "__main__":
    report = validate(load_packet())
    print(f"COMMONS_REALWORLD_SOURCE_HOLD_OK: {report['candidates']} candidates; no release or coverage")
