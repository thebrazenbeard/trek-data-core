#!/usr/bin/env python3
"""Guard audiobook-versus-private-OPF identity for one held literary lead.

The script accesses accepted public publisher-candidate data only. It cannot
establish that any privately held ebook is the same edition as this audiobook.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
PUBLISHER_BATCH = REPO_ROOT / "proposals/research/lit-three-archive-discovered-publisher-editions-20261103"
PUBLIC_BATCH_SHA256 = "03173ed5ac94c7052a8c416bcca9cc762a8e7ca0ca3280eae0a4b3f902954dea"
TARGET_ISBN = "9780743546744"
TARGET_SOURCE_URL = "https://www.simonandschuster.com/books/Shadows-of-the-Sun/Michael-Jan-Friedman/Star-Trek-The-Original-Series/9780743546744"
EXPECTED_METADATA = {
    "title": "Shadows of the Sun", "creator": "Michael Jan Friedman",
    "reader": "James Doohan", "isbn13": TARGET_ISBN,
    "edition_format": "ABRIDGED_AUDIO_DOWNLOAD", "imprint": "Simon & Schuster Audio",
    "publication_date": "1993-08-01", "runtime_minutes": 180,
}
EXPECTED_KEYS = {
    "schema_version", "proposal_only", "publisher_source_url", "publisher_page_checked_utc",
    "publisher_page_metadata", "publisher_description_spelling_disagreement",
    "publisher_upstream_family_count", "private_opf_edition_identified",
    "private_opf_to_audio_isbn_identity_verified", "audio_full_content_read",
    "private_ebook_full_content_read", "accepted_source_work_binding_effect",
    "accepted_work_effect", "accepted_evidence_effect", "coverage_effect",
    "public_synopsis_effect", "artwork_release_effect",
}


def load_pinned_public_batch() -> dict:
    raw = (PUBLISHER_BATCH / "records.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != PUBLIC_BATCH_SHA256:
        raise ValueError("accepted public inventory changed since audit baseline")
    return json.loads(raw)


def _validate_batch(batch: dict) -> None:
    path = PUBLISHER_BATCH / "validate.py"
    spec = importlib.util.spec_from_file_location("lit_publisher_batch_validator", path)
    if spec is None or spec.loader is None:
        raise ValueError("cannot load accepted inventory validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.validate(batch)


def validate(batch: dict, audit: dict) -> dict:
    if not isinstance(audit, dict) or set(audit) != EXPECTED_KEYS:
        raise ValueError("audit field-set drift")
    _validate_batch(batch)
    if audit["schema_version"] != "trek-lit-shadows-audio-identity-audit-v1":
        raise ValueError("audit schema drift")
    if audit["proposal_only"] is not True:
        raise ValueError("proposal falsely admitted")
    if audit["publisher_source_url"] != TARGET_SOURCE_URL or audit["publisher_page_checked_utc"] != "2026-11-04":
        raise ValueError("publisher page provenance drift")
    metadata = audit["publisher_page_metadata"]
    if not isinstance(metadata, dict) or metadata != EXPECTED_METADATA or any(type(metadata[k]) is not type(v) for k, v in EXPECTED_METADATA.items()):
        raise ValueError("publisher edition metadata drift")
    if audit["publisher_upstream_family_count"] != 1:
        raise ValueError("publisher source-family count inflation")
    if audit["publisher_description_spelling_disagreement"] != "SSAN_VS_SUSAN_UNRESOLVED":
        raise ValueError("publisher copy ambiguity lost")
    for flag in ("private_opf_edition_identified", "private_opf_to_audio_isbn_identity_verified",
                 "audio_full_content_read", "private_ebook_full_content_read"):
        if audit[flag] is not False:
            raise ValueError(f"unearned private text/edition qualification: {flag}")
    for field in ("accepted_source_work_binding_effect", "accepted_work_effect",
                  "accepted_evidence_effect", "coverage_effect", "public_synopsis_effect", "artwork_release_effect"):
        if audit[field] != "NONE":
            raise ValueError(f"protected effect attempted: {field}")
    candidates = [r for r in batch["candidates"] if r["publisher_isbn13"] == TARGET_ISBN]
    if len(candidates) != 1:
        raise ValueError("ambiguous publisher ISBN binding")
    candidate = candidates[0]
    pairs = {
        "publisher_title": "title", "creator": "creator", "publisher_isbn13": "isbn13",
        "publisher_edition_format": "edition_format", "publisher_imprint": "imprint",
        "publisher_publication_date": "publication_date",
    }
    for batch_field, audit_field in pairs.items():
        if candidate[batch_field] != metadata[audit_field]:
            raise ValueError(f"publisher edition mismatch: {batch_field}")
    if candidate["publisher_url"] != audit["publisher_source_url"]:
        raise ValueError("publisher page locator mismatch")
    if candidate["publisher_extent"] != "3 hours" or metadata["runtime_minutes"] != 180:
        raise ValueError("audiobook runtime mismatch")
    if candidate["private_archive_edition_identity"] != "UNVERIFIED" or batch["private_to_publisher_edition_match"] != "UNVERIFIED":
        raise ValueError("private ebook/audio edition identity was not established")
    return {
        "status": "PUBLISHER_ABRIDGED_AUDIO_IDENTITY_CONFIRMED_PRIVATE_OPF_MATCH_UNVERIFIED",
        "publisher_isbn13": TARGET_ISBN,
        "private_opf_edition_identified": False,
        "source_binding_effect": "NONE",
        "close_read_effect": "NONE",
    }


if __name__ == "__main__":
    batch = load_pinned_public_batch()
    audit = json.loads((HERE / "AUDIT.json").read_text(encoding="utf-8"))
    print(json.dumps(validate(batch, audit), sort_keys=True, indent=2))
