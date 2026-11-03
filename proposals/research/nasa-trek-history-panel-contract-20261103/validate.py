#!/usr/bin/env python3
"""Fail-closed design-contract verifier; cannot approve NASA image publication.

This packet deliberately models only a held future interface. It neither
compiles the Explorer nor grants rights, media delivery, or user consent.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "contract.json"
MANIFEST = HERE / "MANIFEST.md"
EXPECTED_CANONICAL_SHA256 = "a7eaf9603f0310ac57b88178bbf997e313360ed792fe99fc50f435bdd02238ab"
EXPECTED_MANIFEST_SHA256 = "8411b5d629146378f2ae6600a6f9d36581640a0340f8dcc718707d93cbcccb30"
HELD_RENDER_STATE = "SOURCE_LINK_ONLY_IMAGE_WITHHELD"
MEDIA_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".mp4"}
EXPECTED_FILES = {"contract.json", "MANIFEST.md", "validate.py", "test_validate.py"}


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate contract key")
        result[key] = value
    return result


def read_contract(path: Path = CONTRACT) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 128_000:
        raise ValueError("contract must be a bounded regular nonsymlink file")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def validate(packet: dict) -> None:
    if not isinstance(packet, dict):
        raise ValueError("panel contract must be an object")
    canonical = json.dumps(packet, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"), allow_nan=False).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != EXPECTED_CANONICAL_SHA256:
        raise ValueError("code-owned panel contract source/editorial/rights pin changed")
    if (type(packet["proposal_only"]) is not bool or packet["proposal_only"] is not True
            or packet["public_site_change"] != "NONE"
            or type(packet["image_binaries_included"]) is not int
            or packet["image_binaries_included"] != 0
            or packet["coverage_effect"] != "NONE"
            or packet["admission_effect"] != "NONE"):
        raise ValueError("panel proposal exceeded protected effects")
    event = packet["event_record"]
    if (event["record_kind"] != "REAL_WORLD_EVENT"
            or event["fictional_work_id"] is not None
            or event["fictional_episode_row_id"] is not None
            or event["fictional_film_row_id"] is not None
            or event["fictional_scene_evidence"] is not False):
        raise ValueError("real-world source was misbound to fictional identity")
    placement = packet["placement"]
    if (placement["search_catalog_membership"] is not False
            or placement["fictional_media_gallery_membership"] is not False
            or placement["fictional_work_count_increment"] != 0):
        raise ValueError("historical panel contaminated fictional catalog")
    gate = packet["release_gate"]
    if (gate["public_image_display_authorized"] is not False
            or gate["separate_release_manifest"] is not None
            or gate["approved_release_manifest_sha256"] is not None
            or gate["approved_local_asset_path"] is not None
            or gate["display_image_by_default"] is not False
            or gate["prepublication_state"] != HELD_RENDER_STATE):
        raise ValueError("NASA image release not independently approved")
    browser = packet["browser_contract"]
    if (browser["visitor_opt_in_initially"] is not False
            or browser["remote_image_request"] != "FORBIDDEN"
            or browser["visitor_opt_in_storage"] != "IN_MEMORY_ONLY_NO_LOCAL_STORAGE_COOKIE_OR_SERVER_SYNC"
            or browser["csp_change_in_this_proposal"] != "NONE"):
        raise ValueError("browser privacy or visitor consent weakened")
    if packet["public_release_decision"] != "HOLD":
        raise ValueError("public release decision exceeded approved effect")
    if (MANIFEST.is_symlink() or not MANIFEST.is_file()
            or hashlib.sha256(MANIFEST.read_bytes()).hexdigest() != EXPECTED_MANIFEST_SHA256):
        raise ValueError("code-owned explanation and release-boundary text pin changed")
    for path in HERE.rglob("*"):
        rel = path.relative_to(HERE)
        if path.is_symlink() or path.suffix.lower() in MEDIA_SUFFIXES:
            raise ValueError("proposal includes unexpected media or symlink")
        if path.is_dir():
            if rel.parts != ("__pycache__",):
                raise ValueError("unexpected proposal directory")
        elif path.is_file():
            if len(rel.parts) == 1 and rel.name in EXPECTED_FILES:
                continue
            if len(rel.parts) == 2 and rel.parts[0] == "__pycache__" and rel.suffix == ".pyc":
                continue
            raise ValueError("unexpected proposal file")
        else:
            raise ValueError("unexpected proposal filesystem object")


def prospective_render_state(packet: dict, *, visitor_opted_in: bool = False,
                             claimed_release: object = None) -> str:
    """Today's contract never renders media, regardless of simulated claims.

    Future positive release behavior requires a distinct code-owned reviewed
    manifest and browser implementation; it is not inferable from a JSON GO.
    """
    validate(packet)
    if type(visitor_opted_in) is not bool:
        raise ValueError("visitor consent must be an explicit boolean")
    if claimed_release is not None:
        raise ValueError("untrusted release assertion cannot unlock preview")
    return HELD_RENDER_STATE


def main() -> int:
    try:
        data = read_contract()
        validate(data)
        if prospective_render_state(data, visitor_opted_in=False) != HELD_RENDER_STATE:
            raise ValueError("held render state did not survive initial load")
    except Exception as exc:
        print(f"NASA–Trek history panel proposal HOLD: {exc}", file=sys.stderr)
        return 1
    print("PASS: NASA real-world panel contract is proposal-only, image withheld, no site or fictional Work effect")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
