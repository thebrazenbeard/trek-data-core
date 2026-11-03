#!/usr/bin/env python3
"""Fail-closed local validation of a *nonpublishing* NASA archival-photo proposal.

No inference from this validator constitutes a license, Work identity, coverage
promotion, or authorization to display a photograph. It validates a fixed
research receipt and protects against accidental promotion or crosswalk drift.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

PACKET_DIR = Path(__file__).resolve().parent
PACKET = PACKET_DIR / "records.json"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")

PACKET_KEYS = {
    "proposal_id", "baseline_main_commit", "packet_status", "identity_scope",
    "admission_effect", "coverage_effect", "public_display_eligible",
    "image_files_included", "candidate",
}
CANDIDATE_KEYS = {
    "candidate_id", "subject_kind", "subject_label", "subject_date",
    "subject_place", "subject_basis", "fictional_episode_row_id",
    "fictional_film_row_id", "fictional_work_illustration", "source_lineage",
    "image_page_url", "image_page_html_sha256", "image_page_html_bytes",
    "image_page_credit", "source_image_url", "source_image_sha256",
    "source_image_bytes", "source_image_width_px", "source_image_height_px",
    "source_image_etag", "rights_page_url", "rights_page_html_sha256",
    "rights_page_html_bytes", "rights_basis", "reuse_scope_candidate",
    "individuals_publicity_caveat", "marks_endorsement_caveat",
    "chronology_page_url", "chronology_page_html_sha256",
    "chronology_page_html_bytes", "suggested_credit", "rights_status",
    "public_display_eligible", "display_url", "unresolved", "retrieved_on_utc_date",
}
FIXED_PINS = {
    "candidate_id": "nasa-space-shuttle-enterprise-rollout-cast-1976-photo",
    "subject_kind": "REAL_WORLD_EVENT",
    "subject_label": "Space Shuttle Enterprise public rollout attended by Star Trek cast and creator",
    "subject_date": "1976-09-17",
    "subject_place": "Rockwell International facility, Palmdale, California, USA",
    "subject_basis": "NASA_FIRST_PARTY_HISTORY",
    "source_lineage": "nasa.gov:NASA_OFFICIAL_ONE_INSTITUTION",
    "image_page_url": "https://www.nasa.gov/image-article/star-trek-nasa-54-years-counting/",
    "image_page_html_sha256": "d939f93283e51c80390a890459495138d7e37852dc9e278d683e923bdaa6e832",
    "image_page_html_bytes": 266590,
    "image_page_credit": "NASA",
    "source_image_url": "https://www.nasa.gov/wp-content/uploads/2023/03/ec76-5806-1.jpg",
    "source_image_sha256": "e36c3e1c94c53f57fe99ac921169c24a35c63851666885d20af6fdfe902ed6f8",
    "source_image_bytes": 165312,
    "source_image_width_px": 1041,
    "source_image_height_px": 833,
    "source_image_etag": '"8f1cc2c9faded2a4"',
    "rights_page_url": "https://www.nasa.gov/nasa-brand-center/images-and-media/",
    "rights_page_html_sha256": "2ec1c7a77eed18be8a61234704a178b3cea5711e3d5fc822ed9625e4a46f5746",
    "rights_page_html_bytes": 312840,
    "chronology_page_url": "https://www.nasa.gov/history/space-shuttle-enterprise-makes-its-public-debut/",
    "chronology_page_html_sha256": "3b5d3f74276c94f479c80e286dff691484c7094b297f1d2e4e8d8df481d5aa9f",
    "chronology_page_html_bytes": 297011,
    "reuse_scope_candidate": "NONPROMOTIONAL_FACTUAL_EDITORIAL_US",
    "rights_status": "PENDING_INDEPENDENT_REVIEW",
    "retrieved_on_utc_date": "2026-11-03",
}


def strict_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"missing or symlinked proposal packet: {path}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)


def validate(packet: dict) -> None:
    if not isinstance(packet, dict) or set(packet) != PACKET_KEYS:
        raise ValueError("packet schema changed")
    if packet["proposal_id"] != "nasa-enterprise-rollout-image-20261103":
        raise ValueError("unexpected proposal identity")
    if packet["baseline_main_commit"] != "54c683117640f2596e5ce2c9ef50913c1fad7eac":
        raise ValueError("accepted baseline changed")
    if (packet["packet_status"], packet["identity_scope"], packet["admission_effect"],
            packet["coverage_effect"], packet["public_display_eligible"],
            packet["image_files_included"]) != (
                "PROPOSAL_ONLY", "REAL_WORLD_EVENT_ONLY", "NONE", "NONE", False, 0):
        raise ValueError("packet attempted an unauthorized effect")
    if type(packet["public_display_eligible"]) is not bool or type(packet["image_files_included"]) is not int:
        raise ValueError("invalid packet effect field type")

    rec = packet["candidate"]
    if not isinstance(rec, dict) or set(rec) != CANDIDATE_KEYS:
        raise ValueError("candidate schema changed")
    for key, expected in FIXED_PINS.items():
        if type(rec[key]) is not type(expected) or rec[key] != expected:
            raise ValueError(f"source, rights, event, or image pin changed: {key}")
    for key in ("image_page_html_sha256", "source_image_sha256", "rights_page_html_sha256", "chronology_page_html_sha256"):
        if not SHA256.fullmatch(rec[key]):
            raise ValueError(f"malformed hash: {key}")
    if (rec["fictional_episode_row_id"], rec["fictional_film_row_id"],
            rec["fictional_work_illustration"], rec["public_display_eligible"],
            rec["display_url"]) != (None, None, False, False, None):
        raise ValueError("unauthorized fiction binding or public display")
    if type(rec["fictional_work_illustration"]) is not bool or type(rec["public_display_eligible"]) is not bool:
        raise ValueError("invalid candidate effect field type")
    required_text = {
        "rights_basis": ("NASA", "informational", "non-endorsement", "third-party"),
        "individuals_publicity_caveat": ("identifiable", "commercial", "right-of-publicity"),
        "marks_endorsement_caveat": ("insignia", "endorse"),
        "suggested_credit": ("NASA", "1976", "does not endorse", "Star Trek"),
        "unresolved": ("independent", "not an episode", "third-party"),
    }
    for key, needles in required_text.items():
        value = rec[key]
        if not isinstance(value, str) or len(value) < 50 or any(word.lower() not in value.lower() for word in needles):
            raise ValueError(f"critical rights/identity caveat removed: {key}")
    if any(child.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}
           for child in PACKET_DIR.iterdir()):
        raise ValueError("image binary unexpectedly included")


def main() -> int:
    try:
        validate(read_json(PACKET))
    except Exception as exc:
        print(f"NASA archival image research HOLD: {exc}", file=sys.stderr)
        return 1
    print("PASS: one pinned NASA real-world event photo, zero fiction binding, binaries, coverage, or public display")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
