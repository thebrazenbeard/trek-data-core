#!/usr/bin/env python3
"""Fail-closed *proposal-only* checks for three NASA-hosted history photographs.

Static receipts do not prove photo ownership, clear cast publicity rights, or
authorize an Explorer publication. No filesystem or network mutations occur.
"""
from __future__ import annotations

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
    "image_files_included", "source_page_url", "source_page_html_sha256",
    "source_page_html_bytes", "supplementary_page_url",
    "supplementary_page_html_sha256", "supplementary_page_html_bytes",
    "rights_page_url", "rights_page_html_sha256", "rights_page_html_bytes",
    "receipt_semantics", "receipt_client", "receipt_accept_encoding",
    "source_page_user_agent", "supplementary_page_user_agent",
    "rights_page_user_agent", "source_images_user_agent", "rights_basis",
    "source_lineage", "review_status", "retrieved_on_utc_date", "records",
}
RECORD_KEYS = {
    "candidate_id", "subject_kind", "subject_label", "subject_date",
    "subject_date_precision", "subject_place", "source_image_url",
    "source_image_sha256", "source_image_bytes", "source_image_width_px",
    "source_image_height_px", "source_image_etag",
    "filename_archival_identifier_unverified", "source_caption_basis",
    "individual_photo_credit", "photo_credit_status", "open_rights_falsifier",
    "fictional_episode_row_id", "fictional_film_row_id",
    "fictional_work_illustration", "rights_status", "public_display_eligible",
    "display_url",
}
FIXED_PACKET = {
    "proposal_id": "nasa-nichols-doohan-photo-receipts-20261103",
    "baseline_main_commit": "50e20f8776abb5c78d04a89df7ed7c56c31af8ac",
    "packet_status": "PROPOSAL_ONLY",
    "identity_scope": "REAL_WORLD_EVENT_ONLY",
    "admission_effect": "NONE",
    "coverage_effect": "NONE",
    "public_display_eligible": False,
    "image_files_included": 0,
    "source_page_url": "https://www.nasa.gov/history/55-years-ago-star-trek-debuts-begins-an-enduring-relationship-with-nasa/",
    "source_page_html_sha256": "a84f084048d73bf2cde45a099fb19d83757f41d275b112f17691e77ad8820de0",
    "source_page_html_bytes": 286437,
    "supplementary_page_url": "https://www.nasa.gov/history/55-years-ago-star-trek-final-episode-airs-relationship-with-nasa-endures/",
    "supplementary_page_html_sha256": "dadc9dae9bec360dbe4823954b3e514e0ded60269479235dda1431aabc4c877e",
    "supplementary_page_html_bytes": 337278,
    "rights_page_url": "https://www.nasa.gov/nasa-brand-center/images-and-media/",
    "rights_page_html_sha256": "2ec1c7a77eed18be8a61234704a178b3cea5711e3d5fc822ed9625e4a46f5746",
    "rights_page_html_bytes": 312840,
    "receipt_semantics": "DECODED_HTTP_RESPONSE_BODY_SINGLE_CLIENT_VARIANT_NOT_IMMUTABLE_ARCHIVE",
    "receipt_client": "Python requests 2.34.2; r.content; no text normalization",
    "receipt_accept_encoding": "gzip, deflate, zstd",
    "source_page_user_agent": "python-requests/2.34.2",
    "supplementary_page_user_agent": "python-requests/2.34.2",
    "rights_page_user_agent": "TrekDataCoreResearch/1.0",
    "source_images_user_agent": "python-requests/2.34.2",
    "source_lineage": "nasa.gov:ONE_INSTITUTION_NOT_INDEPENDENT_CORROBORATION",
    "review_status": "HOLD_IMAGE_SPECIFIC_RIGHTS_REVIEW",
    "retrieved_on_utc_date": "2026-11-03",
}
IMAGE_BASE = "https://www.nasa.gov/wp-content/uploads/2021/09/"
EXPECTED = {
    "nasa-nichols-bean-shuttle-simulator-march-1977": {
        "subject_label": "Nichelle Nichols and NASA astronaut Alan Bean in the shuttle simulator",
        "subject_date": "1977-03", "subject_place": "NASA Johnson Space Center, Houston, Texas, USA",
        "source_image_url": IMAGE_BASE + "star_trek_first_episode_5_nichols_and_bean_nin_shuttle_simulator_mar_4_1977_s77-22306.jpg",
        "source_image_sha256": "921f03fb404949c77642f0dd3ce0b194abf59b17c5da0316eb29c055098e021b",
        "source_image_bytes": 110305, "source_image_width_px": 985, "source_image_height_px": 730,
        "source_image_etag": '"34d4b1b9f37efbe6"',
        "filename_archival_identifier_unverified": "S77-22306",
        "photo_credit_status": "NOT_EXPLICIT_IN_ARTICLE",
    },
    "nasa-nichols-mission-control-recruiting-march-1977": {
        "subject_label": "Nichelle Nichols filming NASA astronaut recruitment material in Mission Control",
        "subject_date": "1977-03", "subject_place": "NASA Johnson Space Center, Houston, Texas, USA",
        "source_image_url": IMAGE_BASE + "star_trek_first_episode_6_nichols_in_mcc_filming_promotional_video_s77-22305.jpg",
        "source_image_sha256": "dfd5d4c861867477f666c96103d41f8bf472e7fdb29b977b337eb35ad1cd8dd1",
        "source_image_bytes": 92904, "source_image_width_px": 985, "source_image_height_px": 659,
        "source_image_etag": '"f49f186df598e976"',
        "filename_archival_identifier_unverified": "S77-22305",
        "photo_credit_status": "NOT_EXPLICIT_IN_ARTICLE",
    },
    "nasa-doohan-bruce-peterson-dryden-april-1967": {
        "subject_label": "James Doohan visiting NASA test pilot Bruce Peterson beside the M2-F2 lifting body",
        "subject_date": "1967-04", "subject_place": "NASA Dryden Flight Research Center, California, USA",
        "source_image_url": IMAGE_BASE + "star_trek_first_episode_9_doohan_and_bruce_peterson_at_dryden_apr_13_1967.jpg",
        "source_image_sha256": "edca35e4ab946bbb202334ac14cb7aa1a8973487095ffe82f1fc6b1489b5fd20",
        "source_image_bytes": 55896, "source_image_width_px": 512, "source_image_height_px": 640,
        "source_image_etag": '"9e7831513f1556dc"',
        "filename_archival_identifier_unverified": None,
        "photo_credit_status": "AMBIGUOUS_GROUPED_CAPTION_THIRD_PARTY_RIGHTMOST",
    },
}


def strict_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise ValueError("packet missing, nonregular, or symlinked")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)


def validate(packet: dict) -> None:
    if not isinstance(packet, dict) or set(packet) != PACKET_KEYS:
        raise ValueError("packet schema changed")
    for key, value in FIXED_PACKET.items():
        if type(packet[key]) is not type(value) or packet[key] != value:
            raise ValueError(f"packet identity, baseline, source, or rights pin changed: {key}")
    basis = packet["rights_basis"]
    if not isinstance(basis, str) or len(basis) < 100 or any(k not in basis.lower() for k in ("nasa", "third-party", "informational", "endorsement", "no image-specific")):
        raise ValueError("unsupported blanket rights assertion")
    if len(packet["records"]) != 3 or not isinstance(packet["records"], list):
        raise ValueError("three bounded candidates required")
    seen = set()
    for rec in packet["records"]:
        if not isinstance(rec, dict) or set(rec) != RECORD_KEYS:
            raise ValueError("candidate schema changed")
        candidate = rec["candidate_id"]
        if candidate not in EXPECTED or candidate in seen:
            raise ValueError("unknown or repeated candidate")
        seen.add(candidate)
        for key, value in EXPECTED[candidate].items():
            if type(rec[key]) is not type(value) or rec[key] != value:
                raise ValueError(f"candidate source or subject pin changed: {candidate}/{key}")
        if (rec["subject_kind"], rec["subject_date_precision"],
                rec["source_caption_basis"], rec["individual_photo_credit"],
                rec["fictional_episode_row_id"], rec["fictional_film_row_id"],
                rec["fictional_work_illustration"], rec["rights_status"],
                rec["public_display_eligible"], rec["display_url"]) != (
                    "REAL_WORLD_EVENT", "MONTH", "NASA_FIRST_PARTY_HISTORY_IMAGE_CAPTION", None,
                    None, None, False, "HOLD_INDEPENDENT_REVIEW", False, None):
            raise ValueError("unsafe fictional identity, rights, or public display promotion")
        if type(rec["fictional_work_illustration"]) is not bool or type(rec["public_display_eligible"]) is not bool:
            raise ValueError("invalid candidate promotion types")
        note = rec["open_rights_falsifier"]
        if not isinstance(note, str) or len(note) < 150 or ("rights" not in note.lower() and "authorship" not in note.lower()):
            raise ValueError("rights/identity uncertainty removed")
        if not SHA256.fullmatch(rec["source_image_sha256"]):
            raise ValueError("malformed source image digest")
    if seen != set(EXPECTED):
        raise ValueError("missing expected candidates")
    for key in ("source_page_html_sha256", "supplementary_page_html_sha256", "rights_page_html_sha256"):
        if not SHA256.fullmatch(packet[key]):
            raise ValueError("malformed source page digest")
    if any(path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}
           for path in PACKET_DIR.iterdir()):
        raise ValueError("image binary unexpectedly included")


def main() -> int:
    try:
        validate(read_json(PACKET))
    except Exception as exc:
        print(f"NASA historical photo receipt HOLD: {exc}", file=sys.stderr)
        return 1
    print("PASS: 3 exact NASA-hosted real-world photos; no fiction binding, rights approval, binaries, or public display")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
