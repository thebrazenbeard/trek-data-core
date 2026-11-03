#!/usr/bin/env python3
"""Fail-closed validation of the non-publishing TOS artwork candidate packet.

This validator establishes only syntactic/source-local reproducibility. It is
not a copyright clearance process or an artwork-release compiler.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).resolve().with_name("records.json")
DIRECTORY = ROOT / "explorer" / "discovery-catalog.json"
PACKET_KEYS = {
    "proposal_id", "baseline_main_commit", "directory_sha256", "packet_status",
    "identity_scope", "admission_effect", "coverage_effect",
    "public_display_eligible", "image_files_included", "records",
}
RECORD_KEYS = {
    "candidate_id", "directory_row_id", "directory_title", "source_locator",
    "commons_file_page", "commons_pinned_revision", "rights_page_html_sha256",
    "rights_page_html_bytes", "commons_claimed_rights_tag", "commons_credited_creator",
    "episode_link_basis", "historic_photo_scans", "image_sha256", "image_bytes",
    "commons_metadata_image_sha1", "open_rights_falsifier", "rights_status",
    "public_display_eligible", "display_url",
}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
SAFE_SCAN_STATES = {
    "FRONT_AND_BACK_LINKED_BOTH_OPENED",
    "FRONT_LINK_FAILED_BACK_OPENED",
    "FRONT_AND_BACK_LINKED_BOTH_FAILED",
    "BACK_LINK_NOT_DOCUMENTED",
    "UPLOADER_ADMITS_NO_BACK_INSPECTION",
    "FRONT_AND_BACK_LINKED_UNTESTED",
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
        raise ValueError(f"missing or symlinked packet input: {path}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)


def validate(packet: dict, directory_bytes: bytes) -> None:
    if not isinstance(packet, dict) or set(packet) != PACKET_KEYS:
        raise ValueError("packet schema changed")
    if packet["proposal_id"] != "tos-publicity-artwork-receipts-20261103":
        raise ValueError("unexpected proposal identity")
    if packet["baseline_main_commit"] != "da44aecc4a44829c2cd8c969e80ade7d311c355d":
        raise ValueError("accepted baseline changed")
    if packet["directory_sha256"] != hashlib.sha256(directory_bytes).hexdigest():
        raise ValueError("directory bytes no longer match accepted baseline receipt")
    if (packet["packet_status"], packet["identity_scope"], packet["admission_effect"],
            packet["coverage_effect"], packet["public_display_eligible"],
            packet["image_files_included"]) != ("PROPOSAL_ONLY", "SOURCE_LOCAL", "NONE", "NONE", False, 0):
        raise ValueError("packet attempted an unauthorized effect")

    directory = json.loads(directory_bytes, object_pairs_hook=strict_pairs)
    entries = {row["row_id"]: row for row in directory["rows"]}
    records = packet["records"]
    if not isinstance(records, list) or len(records) != 6:
        raise ValueError("six bounded candidates required")
    ids = set()
    work_rows = set()
    for rec in records:
        if not isinstance(rec, dict) or set(rec) != RECORD_KEYS:
            raise ValueError("candidate schema changed")
        row_id = rec["directory_row_id"]
        if rec["candidate_id"] in ids or row_id in work_rows:
            raise ValueError("duplicate candidate/episode slot")
        ids.add(rec["candidate_id"])
        work_rows.add(row_id)
        if not isinstance(row_id, str) or not row_id.startswith("legacy:s"):
            raise ValueError("candidate lacks exact source-local directory row")
        target = entries.get(row_id)
        if not target or target["medium"] != "EPISODE" or target["source_group"] != "publisher:paramount":
            raise ValueError(f"not a publisher episode discovery slot: {row_id}")
        if (target["title"], target["source_locator"]) != (rec["directory_title"], rec["source_locator"]):
            raise ValueError(f"source-local title/locator mismatch: {row_id}")
        if target["admission_effect"] != "NONE" or target["coverage_effect"] != "NONE":
            raise ValueError("source directory unexpectedly governed")
        page = rec["commons_file_page"]
        revision = rec["commons_pinned_revision"]
        if not isinstance(page, str) or not page.startswith("https://commons.wikimedia.org/wiki/File:"):
            raise ValueError("non-Commons file URL")
        if not isinstance(revision, str) or not revision.startswith("https://commons.wikimedia.org/w/index.php?title=File:") or "&oldid=" not in revision:
            raise ValueError("missing pinned Commons rights-page revision")
        if not SHA256.fullmatch(str(rec["rights_page_html_sha256"])) or type(rec["rights_page_html_bytes"]) is not int or rec["rights_page_html_bytes"] <= 0:
            raise ValueError("invalid Commons page receipt")
        if rec["commons_claimed_rights_tag"] != "PD-US-no-notice":
            raise ValueError("rights claim unexpectedly changed")
        if not rec["commons_credited_creator"] or rec["episode_link_basis"] not in {"EXPLICIT_COMMONS_DESCRIPTION", "INFERRED_FROM_COMMONS_USAGE_NOT_DESCRIPTION"}:
            raise ValueError("missing attribution or linkage limitations")
        if rec["historic_photo_scans"] not in SAFE_SCAN_STATES or len(rec["open_rights_falsifier"]) < 40:
            raise ValueError("rights falsifier/scan status removed")
        if rec["rights_status"] != "HOLD_INDEPENDENT_REVIEW" or rec["public_display_eligible"] is not False or rec["display_url"] is not None:
            raise ValueError("public display promoted without separate admission")
        image_sha, size = rec["image_sha256"], rec["image_bytes"]
        if (image_sha is None) != (size is None):
            raise ValueError("partial image byte receipt")
        if image_sha is not None and (not SHA256.fullmatch(str(image_sha)) or type(size) is not int or size <= 0):
            raise ValueError("invalid image byte receipt")
        metadata_sha1 = rec["commons_metadata_image_sha1"]
        if metadata_sha1 is not None and not SHA1.fullmatch(str(metadata_sha1)):
            raise ValueError("invalid Commons metadata SHA1")

    if len([r for r in records if r["image_sha256"] is not None]) != 1:
        raise ValueError("unverified extra image digests added")
    if len([r for r in records if r["episode_link_basis"] != "EXPLICIT_COMMONS_DESCRIPTION"]) != 1:
        raise ValueError("inference distinction unexpectedly changed")


def main() -> int:
    try:
        validate(read_json(PACKET), DIRECTORY.read_bytes())
    except Exception as exc:
        print(f"TOS publicity artwork candidate HOLD: {exc}", file=sys.stderr)
        return 1
    print("PASS: six source-local candidates; zero admission, coverage, binaries, or public display")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
