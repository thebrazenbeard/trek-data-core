"""Offline, metadata-only validation for one held Commons artwork source lead.

This does not verify photographic bytes, underlying rights, or Work identity.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ROOT_KEYS = {
    "schema_version", "proposal_id", "status", "base_accepted_main", "observed_on_utc",
    "admission_effect", "coverage_effect", "public_display_effect",
    "image_binary_in_repository", "candidates",
}
ROW_KEYS = {
    "candidate_id", "associated_series_label", "subject_context", "association_evidence",
    "work_or_episode_row_id", "character_identity_inferred", "commons_file_title",
    "commons_pinned_oldid", "commons_pinned_revision_url", "flickr_original_url",
    "photographer", "photographed_date", "photo_license", "photo_license_url",
    "commons_flickr_license_review", "original_dimensions_claim",
    "original_jpeg_size_claim_bytes", "original_jpeg_sha1_claim", "image_sha_claim_source",
    "raw_page_sha256", "raw_jpeg_sha256", "imageinfo_json_sha256",
    "release_status", "copyright_scope", "public_asset_path", "public_image_url",
    "attribution_requirement",
}

PIN = {
    "candidate_id": "commons-picard-sdcc-panel-gage-skidmore-2019",
    "associated_series_label": "Star Trek: Picard",
    "work_or_episode_row_id": None,
    "character_identity_inferred": False,
    "commons_file_title": "File:Dominic Patten, Kirsten Beyer, Heather Kadin, Akiva Goldsman, Michael Chabon, Alex Kurtzman, Patrick Stewart, Isa Briones, Santiago Cabrera, Michelle Hurd, Alison Pill, Harry Treadaway, Evan Evagora, Brent Spiner & Jeri Ryan.jpg",
    "commons_pinned_oldid": 1076836194,
    "commons_pinned_revision_url": "https://commons.wikimedia.org/w/index.php?oldid=1076836194&title=File:Dominic_Patten,_Kirsten_Beyer,_Heather_Kadin,_Akiva_Goldsman,_Michael_Chabon,_Alex_Kurtzman,_Patrick_Stewart,_Isa_Briones,_Santiago_Cabrera,_Michelle_Hurd,_Alison_Pill,_Harry_Treadaway,_Evan_Evagora,_Brent_Spiner_%26_Jeri_Ryan.jpg",
    "flickr_original_url": "https://www.flickr.com/photos/gageskidmore/48445060081/",
    "photographer": "Gage Skidmore",
    "photographed_date": "2019-07-20",
    "photo_license": "CC-BY-SA-2.0",
    "photo_license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
    "commons_flickr_license_review": "FlickreviewR 2 confirmed 2019-08-03",
    "original_dimensions_claim": [6720, 4480],
    "original_jpeg_size_claim_bytes": 11006630,
    "original_jpeg_sha1_claim": "968429e937428bd27f026db1ed99a7f3a2235c89",
    "image_sha_claim_source": "WIKIMEDIA_COMMONS_FILE_PAGE_STRUCTURED_DATA_NOT_INDEPENDENT_BYTE_REHASH",
    "raw_page_sha256": None,
    "raw_jpeg_sha256": None,
    "imageinfo_json_sha256": None,
    "release_status": "HOLD_EXACT_BYTE_RECEIPT_AND_INDEPENDENT_RIGHTS_VISUAL_REVIEW",
    "copyright_scope": "PHOTO_LICENSE_ONLY_NO_UNDERLYING_STAR_TREK_IP_OR_PUBLICITY_CLEARANCE",
    "public_asset_path": None,
    "public_image_url": None,
}
REVIEWED_ROW_SHA256 = "3061066d557ace8ac88b36105e2538f75483a438f6863f0b28be87fad52418c8"


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def load(path=ROOT / "records.json"):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 30_000:
        raise ValueError("missing, symlinked, or oversized source packet")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def validate(packet):
    if not isinstance(packet, dict) or set(packet) != ROOT_KEYS:
        raise ValueError("proposal root schema drift")
    expected_root = {
        "schema_version": "1.0.0", "proposal_id": "picard-sdcc-cast-panel-20261103",
        "status": "PROPOSAL_SOURCE_METADATA_ONLY",
        "base_accepted_main": "3e1a49e6d06af28fd8cab89fa02dae14d63ca5f8",
        "observed_on_utc": "2026-11-03", "admission_effect": "NONE",
        "coverage_effect": "NONE", "public_display_effect": "NONE",
        "image_binary_in_repository": False,
    }
    if any(type(packet[key]) is not type(value) or packet[key] != value
           for key, value in expected_root.items()):
        raise ValueError("proposal effect/source boundary drift")
    rows = packet["candidates"]
    if not isinstance(rows, list) or len(rows) != 1:
        raise ValueError("candidate inventory changed")
    row = rows[0]
    if not isinstance(row, dict) or set(row) != ROW_KEYS:
        raise ValueError("candidate schema drift")
    if any(type(row[key]) is not type(value) or row[key] != value
           for key, value in PIN.items()):
        raise ValueError("source identity or held rights pin changed")
    if not isinstance(row["subject_context"], str) or "not a still" not in row["subject_context"]:
        raise ValueError("non-still context missing")
    if not isinstance(row["association_evidence"], str) or "source-relative" not in row["association_evidence"]:
        raise ValueError("source-relative limit missing")
    if not isinstance(row["attribution_requirement"], str) or "Gage Skidmore" not in row["attribution_requirement"]:
        raise ValueError("photo attribution missing")
    canonical = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != REVIEWED_ROW_SHA256:
        raise ValueError("exact source-relative candidate content changed without re-review")
    return {"candidate_count": 1, "admitted": 0, "public_images": 0}


if __name__ == "__main__":
    print("PICARD_SDCC_HELD_SOURCE_OK", validate(load()))
