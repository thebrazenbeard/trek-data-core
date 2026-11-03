#!/usr/bin/env python3
"""Deterministic nonpublishing NASA historical-image display-decision guard.

Checks exact evidence receipts, terms caveats, intended placement and no
fictional identity/canonical coverage effects. No license or rights clearance
can be issued by running this script.
"""
from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path

PACKET_DIR = Path(__file__).resolve().parent
PACKET = PACKET_DIR / "decision.json"
SHA = re.compile(r"[0-9a-f]{64}\Z")
KEYS = {
    "proposal_id", "baseline_main_commit", "status", "admission_effect",
    "coverage_effect", "site_effect", "image_binaries_included",
    "public_display_eligible", "photo_subject_type", "photo_subject",
    "event_date", "event_date_basis", "event_place", "fictional_episode_row_id",
    "fictional_film_row_id", "fictional_work_illustration",
    "historical_source_photo_url", "historical_source_page_sha256",
    "historical_source_page_bytes", "historical_source_image_credit",
    "historical_source_og_image_exact_url", "historical_source_image_sha256",
    "historical_source_image_bytes", "historical_source_image_dimensions",
    "historical_source_image_etag", "individual_photographer",
    "individual_third_party_copyright_notice_on_source_page",
    "nasa_image_credit_basis", "history_date_url", "history_date_page_sha256",
    "history_date_page_bytes", "nasa_media_policy_url",
    "nasa_media_policy_page_sha256_current_variant",
    "nasa_media_policy_page_sha256_prior_variant", "nasa_media_policy_html_bytes",
    "nasa_brand_center_url", "nasa_brand_center_page_sha256_observed_variant",
    "nasa_brand_center_html_bytes_observed_variant",
    "nasa_brand_center_copyright_clause_sha256",
    "nasa_brand_center_publicity_clause_sha256", "receipt_client",
    "receipt_accept_encoding", "html_receipt_interpretation", "policy_kind",
    "policy_support", "proposed_placement", "proposed_caption", "proposed_credit",
    "linked_official_page", "decision", "independent_rights_review",
    "independent_design_context_review", "release_authorization",
    "related_earlier_candidate_pr", "separate_held_photos_pr",
    "separate_held_photos_must_remain_held", "open_falsifiers",
}
FIXED = {
    "proposal_id": "nasa-enterprise-rollout-display-decision-20261103",
    "baseline_main_commit": "9653c01d6f620063de52bcb58da6e7be3cde6970",
    "status": "PROPOSAL_ONLY_NOT_A_PUBLICATION_GRANT",
    "admission_effect": "NONE", "coverage_effect": "NONE", "site_effect": "NONE",
    "image_binaries_included": 0, "public_display_eligible": False,
    "photo_subject_type": "REAL_WORLD_EVENT",
    "photo_subject": "Star Trek cast and Gene Roddenberry at Space Shuttle Enterprise rollout",
    "event_date": "1976-09-17", "event_date_basis": "NASA_HISTORY_PAGE_NOT_CAMERA_TIMESTAMP",
    "event_place": "Rockwell International plant, Palmdale, California, USA",
    "fictional_episode_row_id": None, "fictional_film_row_id": None,
    "fictional_work_illustration": False,
    "historical_source_photo_url": "https://www.nasa.gov/image-article/star-trek-nasa-54-years-counting/",
    "historical_source_page_sha256": "d939f93283e51c80390a890459495138d7e37852dc9e278d683e923bdaa6e832",
    "historical_source_page_bytes": 266590,
    "historical_source_image_credit": "NASA",
    "historical_source_og_image_exact_url": "https://www.nasa.gov/wp-content/uploads/2023/03/ec76-5806-1.jpg",
    "historical_source_image_sha256": "e36c3e1c94c53f57fe99ac921169c24a35c63851666885d20af6fdfe902ed6f8",
    "historical_source_image_bytes": 165312,
    "historical_source_image_dimensions": [1041, 833],
    "historical_source_image_etag": '"8f1cc2c9faded2a4"',
    "individual_photographer": None,
    "individual_third_party_copyright_notice_on_source_page": "NOT_OBSERVED",
    "nasa_image_credit_basis": "NASA_IMAGE_PAGE_VISIBLE_CREDIT_AND_OG_IMAGE",
    "history_date_url": "https://www.nasa.gov/history/space-shuttle-enterprise-makes-its-public-debut/",
    "history_date_page_sha256": "3b5d3f74276c94f479c80e286dff691484c7094b297f1d2e4e8d8df481d5aa9f",
    "history_date_page_bytes": 297011,
    "nasa_media_policy_url": "https://www.nasa.gov/nasa-brand-center/images-and-media/",
    "nasa_media_policy_page_sha256_current_variant": "0b37b9073042c38303de34b538db2a684647c28690a618fc433fc59473086db1",
    "nasa_media_policy_page_sha256_prior_variant": "2ec1c7a77eed18be8a61234704a178b3cea5711e3d5fc822ed9625e4a46f5746",
    "nasa_media_policy_html_bytes": 312840,
    "nasa_brand_center_url": "https://www.nasa.gov/nasa-brand-center/",
    "nasa_brand_center_page_sha256_observed_variant": "5472cec5c3ee32e83c56a757788e258fdced095f659205ac00621fa91dfa1226",
    "nasa_brand_center_html_bytes_observed_variant": 290037,
    "nasa_brand_center_copyright_clause_sha256": "361d9eb2c7f46fd68918da74ddf76ab5180b74c6f966da9634efc487354f325a",
    "nasa_brand_center_publicity_clause_sha256": "222816bae84192700f65bdd27b791e60ba6f9332340ec3798271346dfbbbaa88",
    "receipt_client": "Python requests 2.34.2 with default headers and r.content HTTP-decoded body, no text normalization",
    "receipt_accept_encoding": "gzip, deflate, zstd",
    "html_receipt_interpretation": "FETCH_VARIANT_ONLY_NOT_IMMUTABLE_ARCHIVE_OR_LEGAL_PERMIT",
    "policy_kind": "NASA_CONDITIONAL_FACTUAL_INFORMATIONAL_REPRODUCTION_POLICY_NOT_LICENSE",
    "proposed_placement": "SEPARATE_REAL_WORLD_NASA_TREK_HISTORY_CONTEXT_PANEL_ONLY",
    "linked_official_page": "https://www.nasa.gov/image-article/star-trek-nasa-54-years-counting/",
    "decision": "CONDITIONAL_EDITORIAL_REUSE_POLICY_SUPPORTED_PENDING_INDEPENDENT_REVIEW",
    "independent_rights_review": "PENDING", "independent_design_context_review": "PENDING",
    "release_authorization": "NOT_GRANTED",
    "related_earlier_candidate_pr": "https://github.com/thebrazenbeard/trek-data-core/pull/411",
    "separate_held_photos_pr": "https://github.com/thebrazenbeard/trek-data-core/pull/414",
    "separate_held_photos_must_remain_held": True,
    # Exact code-owned editorial copy prevents a valid source receipt from
    # laundering contradictory invented statements into the proposed panel.
    "proposed_caption": "At the public rollout of NASA's Space Shuttle Enterprise in Palmdale, California, on September 17, 1976, original Star Trek cast members and creator Gene Roddenberry joined NASA Administrator James C. Fletcher. This is a photograph of a real NASA event, not a Star Trek episode scene.",
    "proposed_credit": "Image: NASA. Historical event: Space Shuttle Enterprise rollout, September 17, 1976. Source: NASA. This independent Star Trek research archive is not affiliated with or endorsed by NASA.",
}
POLICY_KEYS = {
    "educational_informational_web_use", "independent_nasa_credit_required",
    "no_nasa_endorsement", "third_party_marked_photo_permission_needed",
    "recognizable_non_nasa_person_commercial_promotional_clearance_needed",
    "nasa_identifiers_incidental_factual_use_only",
    "nasa_logo_seal_as_interface_branding",
    "nasa_image_as_graphic_link_to_nasa_page", "remote_cdn_img_src_embed",
    "locally_mirrored_binary", "global_public_domain_or_cc0_claim",
}
FIXED_POLICY = {
    "educational_informational_web_use": "GENERAL_NASA_CREATED_CONTENT_PERMITTED_CONDITIONALLY",
    "independent_nasa_credit_required": True, "no_nasa_endorsement": True,
    "third_party_marked_photo_permission_needed": True,
    "recognizable_non_nasa_person_commercial_promotional_clearance_needed": True,
    "nasa_identifiers_incidental_factual_use_only": True,
    "nasa_logo_seal_as_interface_branding": False,
    "nasa_image_as_graphic_link_to_nasa_page": "CONDITIONALLY_PERMITTED",
    "remote_cdn_img_src_embed": "NOT_SEPARATELY_CONFIRMED_BY_GRAPHIC_LINK_POLICY",
    "locally_mirrored_binary": "REQUIRES_SEPARATE_IMAGE_RELEASE_AND_HASH_PIN",
    "global_public_domain_or_cc0_claim": False,
}
# Exact code-owned canonical digest of the five individually disclosed open
# falsifiers. Schema/keyword checks alone would permit contradictory appended
# rights or fictional-story claims to ride through the proposal preview.
EXPECTED_FALSIFIERS_SHA256 = "f9d5210c41c5325b13e4aae1eb2f971efdcb223ec8f9b4b2e70a462b99e341b2"


def strict_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing, nonregular, or symlinked decision packet")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)


def validate(packet: dict) -> None:
    if not isinstance(packet, dict) or set(packet) != KEYS:
        raise ValueError("decision schema changed")
    for key, expected in FIXED.items():
        value = packet[key]
        if type(value) is not type(expected) or value != expected:
            raise ValueError(f"source, rights, identity, or protected effect pin changed: {key}")
    ps = packet["policy_support"]
    if not isinstance(ps, dict) or set(ps) != POLICY_KEYS:
        raise ValueError("NASA policy interpretation schema changed")
    for key, expected in FIXED_POLICY.items():
        if type(ps[key]) is not type(expected) or ps[key] != expected:
            raise ValueError(f"NASA policy caveat/approval changed: {key}")
    hashes = (
        "historical_source_page_sha256", "historical_source_image_sha256",
        "history_date_page_sha256", "nasa_media_policy_page_sha256_current_variant",
        "nasa_media_policy_page_sha256_prior_variant",
        "nasa_brand_center_page_sha256_observed_variant",
        "nasa_brand_center_copyright_clause_sha256",
        "nasa_brand_center_publicity_clause_sha256",
    )
    if any(not SHA.fullmatch(packet[key]) for key in hashes):
        raise ValueError("malformed source or policy fingerprint")
    if (type(packet["historical_source_image_dimensions"][0]) is not int
            or type(packet["historical_source_image_dimensions"][1]) is not int):
        raise ValueError("image dimension type changed")
    caption = packet["proposed_caption"]
    credit = packet["proposed_credit"]
    if not isinstance(caption, str) or len(caption) < 160 or any(x not in caption for x in (
            "NASA", "Star Trek", "September 17, 1976", "real NASA event", "not a Star Trek episode scene")):
        raise ValueError("historical caption identity/context removed")
    if not isinstance(credit, str) or len(credit) < 100 or any(x not in credit for x in (
            "Image: NASA", "Source: NASA", "not affiliated with or endorsed by NASA")):
        raise ValueError("NASA attribution or nonendorsement removed")
    falsifiers = packet["open_falsifiers"]
    if not isinstance(falsifiers, list) or len(falsifiers) != 5 or not all(isinstance(x, str) and len(x) >= 130 for x in falsifiers):
        raise ValueError("material open falsifiers removed")
    observed_falsifiers_hash = hashlib.sha256(json.dumps(
        falsifiers, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")).hexdigest()
    if observed_falsifiers_hash != EXPECTED_FALSIFIERS_SHA256:
        raise ValueError("code-owned material falsifier text pin changed")
    if not all(any(needle in f.lower() for f in falsifiers) for needle in (
            "copyright", "non-nasa", "hotlink", "fictional", "html")):
        raise ValueError("material rights/identity uncertainty elided")
    if any(path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}
           for path in PACKET_DIR.iterdir()):
        raise ValueError("image binary unexpectedly included")


def main() -> int:
    try:
        validate(read_json(PACKET))
    except Exception as exc:
        print(f"NASA historical display decision HOLD: {exc}", file=sys.stderr)
        return 1
    print("PASS: NASA image policy decision proposal, no public display, fiction mapping, binary, or coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
