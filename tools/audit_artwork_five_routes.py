#!/usr/bin/env python3
"""Read-only five-lane artwork custody/release decision audit.

Only code-owned, exact accepted metadata sources are inspected; no image
downloads or publisher resource requests occur. This does not grant rights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "proposals/librarian/artwork-five-route-audit-20261104/review.json"
INPUTS = {
    "primary": ("proposals/librarian/artwork-primary-asset-locators-20261103/records.json", "9ffde76a5cd14d915dd17e672c8a5e3dc87d9f7fbc1d085e2638ab732f40f972"),
    "commons": ("proposals/librarian/commons-asset-review-20261103/records.json", "604fd3373e637a994437b58818b308bd050ea6c76fc6c1bee37edc30854431f9"),
    "picard": ("explorer/picard-jackets-v1.0.json", "85bdc8ebbb348d713d604fb9486c2af091e36d40138587a761ddd93716cd9615"),
    "picard_receipt": ("registry/artwork-edition-receipts/picard-jackets-review.json", "21d9e9a897451a63b92b6600b2ea763bc3b87b29ffd781bd3c66427c1c4eb7e9"),
    "autobio_api": ("explorer/artwork-catalog-v1.3.json", "f4f51a71e9db95368d03d1db88d07137425c09f7918e4a491c98e0eb6e8cfa2f"),
}
EXPECTED = {
    "episode-snw-s3-e01": ("PRIMARY_ASSET_LOCATORS", "art-snw-s3-e01-20261103", "EPISODE", "PUBLISHER_EPISODE_CARD_THUMBNAIL", "HELD_NO_PUBLIC_DISPLAY_LICENSE"),
    "film-wrath-header": ("PRIMARY_ASSET_LOCATORS", "art-film-wrath-khan-og-20261103", "FILM", "PUBLISHER_PAGE_OG_HEADER_NOT_POSTER", "HELD_NO_PUBLIC_DISPLAY_LICENSE"),
    "literature-kobayashi-ebook-cover": ("PRIMARY_ASSET_LOCATORS", "art-lit-kobayashi-ebook-20261103", "LITERATURE", "PUBLISHER_LINKED_HIGH_RES_COVER_FOR_EBOOK_ISBN", "HELD_NO_PUBLIC_DISPLAY_LICENSE"),
    "commons-joe-ross-museum-photo": ("COMMONS_PHOTO_CANDIDATE", "commons-joe-ross-iconic-tos-props", "DOCUMENTARY_PHOTO", "COMMONS_CC_BY_SA_2_PHOTOGRAPH", "HELD_UNDERLYING_PROP_RIGHTS_AND_NO_BINARY_CUSTODY"),
    "picard-dark-veil-openlibrary-jacket": ("PICARD_OPEN_LIBRARY_SIDECAR", "directory:literature:proposed-lit-picard-the-dark-veil", "LITERATURE", "EDITION_PINNED_OPEN_LIBRARY_API_COVER", "OPT_IN_REMOTE_API_PREVIEW_NOT_LICENSED_COPY"),
}
RIGHTS_EVIDENCE = {
    "episode-snw-s3-e01": "PUBLISHER_HTML_LOCATOR_NOT_LICENSE",
    "film-wrath-header": "PUBLISHER_OG_META_NOT_LICENSE",
    "literature-kobayashi-ebook-cover": "DOWNLOAD_URL_NOT_PERMISSION_EXACT_EBOOK_ISBN_ONLY",
    "commons-joe-ross-museum-photo": "PHOTOGRAPH_CC_LICENSE_REPORTED_UNDERLYING_RIGHTS_UNRESOLVED",
    "picard-dark-veil-openlibrary-jacket": "API_DOCUMENTATION_AND_EDITION_RECEIPTS_COPYRIGHT_UNRESOLVED",
}
PR_HEAD = "8f71963f905eb4c2169ef46a1b488a257a99cc7e"
ACCEPTED_HEAD = "3028765359001b90bc3e6b5c1835ee283b326e91"
PR_PATHS = {
    "explorer/app.css", "explorer/app.js", "explorer/index.html",
    "tests/test_beyond_documentary_photo.py", "tests/test_explorer.mjs",
    "tests/test_explorer_accessibility.mjs", "tools/validate_beyond_documentary_photo.py",
}


class ArtworkAuditError(ValueError):
    pass


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ArtworkAuditError("duplicate JSON field")
        out[key] = value
    return out


def strict_json(data: bytes) -> dict:
    try:
        obj = json.loads(data, object_pairs_hook=unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ArtworkAuditError("malformed JSON") from exc
    if not isinstance(obj, dict):
        raise ArtworkAuditError("expected a JSON object")
    return obj


def read_accepted_sources() -> dict:
    records = {}
    for key, (name, expected_sha) in INPUTS.items():
        actual = (ROOT / name).read_bytes()
        if hashlib.sha256(actual).hexdigest() != expected_sha:
            raise ArtworkAuditError(f"accepted {key} input digest mismatch")
        records[key] = strict_json(actual)
    return records


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtworkAuditError(message)


def audit(review: dict, accepted: dict, *, licensed_artwork_dir: bool = False,
          rights_receipts_dir: bool = False) -> dict:
    require(review.get("record_type") == "librarian_artwork_rights_release_audit"
            and review.get("accepted_main") == ACCEPTED_HEAD
            and review.get("draft_explorer_pr") == 486
            and review.get("draft_explorer_head") == PR_HEAD,
            "unreviewed accepted main or draft PR scope")
    for effect in ("public_licensed_image_release", "canonical_source_work_effect", "coverage_effect"):
        require(review.get(effect) == "NONE", "false canonical or public image release claim")
    require(not licensed_artwork_dir and not rights_receipts_dir,
            "local licensed-artwork binary/rights receipt lane requires distinct review")
    candidates = review.get("representative_cases")
    require(isinstance(candidates, list) and len(candidates) == 5, "expected five representative decisions")
    require({r.get("case_id") for r in candidates if isinstance(r, dict)} == set(EXPECTED),
            "representative case IDs changed, omitted or duplicated")
    primary = accepted["primary"]
    require(primary.get("public_artwork_release_effect") == "NONE"
            and primary.get("image_bytes_retrieved") is False
            and primary.get("rights_assessment") == "NO_PUBLIC_DISPLAY_LICENSE_ESTABLISHED",
            "primary publisher locators cannot assert art rights or image bytes")
    observation_by_id = {row["local_id"]: row for row in primary.get("observations", [])}
    require(len(observation_by_id) == len(primary.get("observations", [])), "primary image duplicate IDs")
    commons = accepted["commons"].get("commons_photo_candidate", {})
    require(accepted["commons"].get("public_display_authorized") is False
            and accepted["commons"].get("artwork_binary_present") is False,
            "Commons candidate packet cannot assert a public image release")
    picard = accepted["picard"]
    receipt = accepted["picard_receipt"]
    autobio = accepted["autobio_api"]
    require(picard.get("copyright_status") == "UNDERLYING_JACKET_COPYRIGHT_UNRESOLVED"
            and picard.get("public_image_bytes_committed") is False
            and picard.get("artwork_count") == 2,
            "Picard sidecar copied or licensed more than recorded")
    require(receipt.get("copyright_status") == "UNRESOLVED"
            and receipt.get("api_display_scope") == "REMOTE_OPEN_LIBRARY_API_AFTER_EXPLICIT_CONSENT"
            and receipt.get("image_bytes_mirrored") is False
            and receipt.get("sidecar_sha256") == INPUTS["picard"][1],
            "Picard review receipt does not support limited API-preview route")
    require(autobio.get("artwork_count") == 4 and all(row.get("rights_status") == "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED"
        for row in autobio.get("artwork", [])), "autobiography API receipt/license boundary changed")
    rows = []
    for item in candidates:
        require(isinstance(item, dict) and set(item) == {"case_id", "source_packet", "source_local_asset_id", "expected_medium",
                "expected_image_kind", "public_delivery_route", "rights_evidence"}, "unreviewed case schema")
        case_id = item["case_id"]
        require(tuple(item[field] for field in ("source_packet", "source_local_asset_id", "expected_medium",
                "expected_image_kind", "public_delivery_route")) == EXPECTED[case_id],
                "representative asset identity/route switched")
        require(item["rights_evidence"] == RIGHTS_EVIDENCE[case_id],
                "rights evidence summary claims unreviewed permission")
        if item["source_packet"] == "PRIMARY_ASSET_LOCATORS":
            row = observation_by_id.get(item["source_local_asset_id"])
            require(row is not None and row.get("medium") == item["expected_medium"]
                    and row.get("image_kind") == item["expected_image_kind"]
                    and row.get("rights_status") == "HELD_NO_PUBLIC_DISPLAY_LICENSE"
                    and row.get("display_eligible") is False,
                    "publisher-linked image locator cannot grant display rights")
            require(row.get("source_inspection") in {"FIRST_PARTY_HTML_CARD", "FIRST_PARTY_HTML_META", "FIRST_PARTY_RENDERED_PAGE_AND_IMAGE_LINK"},
                    "unknown source inspection provenance")
        elif item["source_packet"] == "COMMONS_PHOTO_CANDIDATE":
            require(commons.get("id") == item["source_local_asset_id"]
                    and commons.get("file_page_license_claim") == "CC BY-SA 2.0"
                    and commons.get("underlying_fictional_prop_design_and_brand_rights") == "UNRESOLVED"
                    and commons.get("public_display_authorized", False) is False
                    and commons.get("asset_sha256") is None
                    and commons.get("public_display_decision") == "BLOCKED_PENDING_SEPARATE_HUMAN_RIGHTS_REVIEW",
                    "Commons photo CC label is not a full public image release")
        else:
            covers = [row for row in picard.get("artwork", []) if row.get("row_id") == item["source_local_asset_id"]]
            require(len(covers) == 1, "Picard edition/image crosswalk missing or ambiguous")
            cover = covers[0]
            require(cover.get("provider") == "OPEN_LIBRARY_COVERS_API"
                    and cover.get("cover_id") == 10691195 and cover.get("isbn") == "9781982154073"
                    and cover.get("image_size") == "M"
                    and cover.get("rights_status") == "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED"
                    and cover.get("attribution_url") == "https://openlibrary.org/isbn/9781982154073",
                    "Picard API preview does not provide licensed hosted binary")
        rows.append({"case_id": case_id, "public_delivery_route": item["public_delivery_route"],
                     "copyright_reuse_cleared": False})
    return {
        "status": "ZERO_LICENSED_IMAGE_BINARIES_AND_ONE_DOCUMENTED_OPT_IN_API_ROUTE",
        "audited_representative_count": len(rows),
        "licensed_local_image_count": 0,
        "underlying_copyright_cleared_count": 0,
        "held_provider_image_count": 3,
        "commons_cc_photo_held_underlying_rights_count": 1,
        "documented_opt_in_api_preview_count": 1,
        "accepted_api_cover_sidecar_candidates": 4 + picard["artwork_count"],
        "public_release_effect": "NONE",
        "cases": sorted(rows, key=lambda row: row["case_id"]),
    }


def verify_pr_486() -> dict:
    def git(*args):
        result = subprocess.run(["git", *args], cwd=ROOT, check=False, capture_output=True, text=True)
        if result.returncode:
            raise ArtworkAuditError("exact draft #486 Git object unavailable")
        return result.stdout
    paths = set(git("diff", "--name-only", f"{ACCEPTED_HEAD}...{PR_HEAD}").splitlines())
    require(paths == PR_PATHS, "draft #486 changed unreviewed asset or copyright-bearing files")
    html = git("show", f"{PR_HEAD}:explorer/index.html")
    js = git("show", f"{PR_HEAD}:explorer/app.js")
    require("img-src 'self' https://covers.openlibrary.org https://archive.org https://*.us.archive.org" in html
            and "https://thumbnails.cbsig.net" not in html
            and "https://d28hgpri8am2if.cloudfront.net" not in html,
            "Explorer CSP gained an unreviewed publisher image host")
    require("Pinned image previews" in html and "Image preview receipt (loaded)" in html
            and "receipt_pinned" in js and "Show sourced artwork" in html,
            "draft #486 UI wording/consent gate changed")
    return {"draft_pr_486_head_verified": PR_HEAD, "reviewed_changed_file_count": len(paths),
            "new_image_binary_or_sidecar_files": 0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-pr486", action="store_true")
    args = parser.parse_args()
    try:
        review = strict_json(REVIEW.read_bytes())
        accepted = read_accepted_sources()
        outcome = audit(review, accepted,
            licensed_artwork_dir=(ROOT / "explorer/licensed-artwork").exists(),
            rights_receipts_dir=(ROOT / "registry/artwork-rights-receipts").exists())
        if args.verify_pr486:
            outcome.update(verify_pr_486())
        else:
            outcome["draft_pr_486_head_verified"] = "NOT_CHECKED"
    except (OSError, ArtworkAuditError) as exc:
        print(json.dumps({"status": "ARTWORK_RELEASE_AUDIT_REJECTED", "reason": str(exc)}, sort_keys=True))
        return 3
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
