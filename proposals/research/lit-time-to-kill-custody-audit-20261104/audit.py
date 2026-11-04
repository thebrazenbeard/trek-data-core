#!/usr/bin/env python3
"""Cross-packet audit of public, held literary receipts; never reads book text.

This checks that two *proposed* observations have consistent fingerprints. It
does not independently authenticate the privately held source files.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
ORIGINAL = REPO_ROOT / "proposals/research/lit-time-to-kill-original-lit-20261103"
CONVERTED = REPO_ROOT / "proposals/research/lit-time-to-kill-structure-20261103"

# Pinned hashes refer to *accepted-main public proposal receipts*, not source
# binaries. Without the private blobs, neither SHA independently proves origin.
PUBLIC_RECEIPT_SHA256 = "0207a7288851890dee074f9c44f60331ce7981c5f7ddeed9e891df4a4251e444"
PUBLIC_INDEX_SHA256 = "a568ac8e3b7bd439b0939d3177b683f6b182a7189ceebd913646d2fbee6917c7"

HASH_CORRESPONDENCE = {
    "converted_archive_sha256": "source_container_sha256",
    "converted_opf_member_sha256": "opf_member_sha256",
    "converted_html_spine_sha256": "html_spine_sha256",
}


def _validator(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load prerequisite validator: {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate


def load_pinned(path: Path, expected_sha256: str) -> dict:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError(f"public proposal changed since audit baseline: {path.name}")
    return json.loads(raw)


def validate(receipt: dict, index: dict) -> dict:
    """Check public packet consistency without inferring private text identity."""
    if not isinstance(receipt, dict) or not isinstance(index, dict):
        raise ValueError("both proposal records must be objects")

    # Reuse each packet's own field whitelist, row digest, span and receipt
    # checks before asserting cross-packet consistency.
    _validator(ORIGINAL / "validate.py", "lit_original_receipt_validator")(receipt)
    _validator(CONVERTED / "validate.py", "lit_converted_index_validator")(index)

    for original_key, converted_key in HASH_CORRESPONDENCE.items():
        if receipt[original_key] != index[converted_key]:
            raise ValueError(f"cross-packet fingerprint mismatch: {original_key}")
    if receipt["candidate_work_title"] != index["work_candidate_title"]:
        raise ValueError("cross-packet candidate title mismatch")
    if receipt["candidate_work_creator"] != index["work_candidate_creator"]:
        raise ValueError("cross-packet candidate creator mismatch")
    if receipt["proposal_only"] is not True or index["proposal_only"] is not True:
        raise ValueError("cross-packet non-admission drift")
    for packet in (receipt, index):
        for field in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect"):
            if packet[field] != "NONE":
                raise ValueError(f"unexpected accepted effect: {field}")
    for field in ("original_lit_content_parsed", "conversion_equivalence_verified",
                  "complete_edition_verified", "close_read_performed"):
        if receipt[field] is not False:
            raise ValueError(f"unsupported source or coverage qualification: {field}")

    return {
        "audit_schema": "trek-lit-public-custody-crosspacket-v1",
        "source": "accepted-main-public-proposal-receipts-only",
        "candidate_work": "A Time to Kill — David Mack",
        "cross_packet_hash_pairs_consistent": sorted(HASH_CORRESPONDENCE),
        "converted_chapter_segments_observed": index["chapter_count"],
        "private_original_lit_payload_read_this_audit": False,
        "private_conversion_text_equivalence_verified": False,
        "edition_completeness_verified": False,
        "accepted_source_binding_effect": "NONE",
        "accepted_work_effect": "NONE",
        "coverage_effect": "NONE",
        "status": "PROPOSAL_CUSTODY_CONSISTENT_SOURCE_AUTHENTICITY_UNVERIFIED",
    }


def run() -> dict:
    original = load_pinned(ORIGINAL / "RECEIPT.json", PUBLIC_RECEIPT_SHA256)
    converted = load_pinned(CONVERTED / "CHAPTER_INDEX.json", PUBLIC_INDEX_SHA256)
    return validate(original, converted)


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
