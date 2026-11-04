"""Deterministic librarian-only metadata handoff for original reference cards.

No artwork is generated, downloaded or published. Returns bounded accepted
source-local row tuples as reference/display inputs for a separate UI owner.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "proposals/librarian/reference-card-provenance-contract-20261104/records.json"
CATALOG_PATH = ROOT / "explorer/search-catalog.json"
EXPECTED_MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"
EXPECTED_CATALOG_SHA256 = "a197138a9069fb67ac5307055588659dd74a9fb4e1caa9d5295d24bc0687d4e5"
MEDIA = {"EPISODE", "FILM", "LITERATURE", "SHORT_FORM", "AUDIO"}


def _canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def _safe_https_locator(value):
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password and "\\" not in value


def build_inputs(packet=None, catalog=None):
    if packet is None:
        packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    if catalog is None:
        catalog_bytes = CATALOG_PATH.read_bytes()
        if hashlib.sha256(catalog_bytes).hexdigest() != EXPECTED_CATALOG_SHA256:
            raise ValueError("accepted catalog byte digest drift")
        catalog = json.loads(catalog_bytes)
    if packet.get("accepted_main_baseline") != EXPECTED_MAIN or packet.get("accepted_source_catalog_sha256") != EXPECTED_CATALOG_SHA256:
        raise ValueError("unaccepted baseline/source digest")
    if packet.get("status") != "HELD_METADATA_CONTRACT_NO_ARTWORK_PUBLICATION":
        raise ValueError("unapproved publication status")
    if packet.get("source_identity_class") != "SOURCE_LOCAL_NOT_DEDUPLICATED" or packet.get("source_data_status") != "SOURCE_LOCAL_SEARCH_PROJECTION_ONLY":
        raise ValueError("source identity/data status elevated")
    if packet.get("generated_svgs_committed") is not False or packet.get("image_or_media_bytes_downloaded") is not False or packet.get("replaced_existing_artwork") is not False or packet.get("public_release_eligible") is not False or packet.get("site_effect") != "NONE":
        raise ValueError("unsupported image/public effect")
    if packet.get("accepted_source_work_admissions") != 0 or packet.get("accepted_coverage_increment") != 0:
        raise ValueError("coverage or work admission inflated")
    if catalog.get("schema_version") != "1.0.0" or catalog.get("row_count") != 1214 or len(catalog.get("rows", [])) != 1214:
        raise ValueError("accepted directory shape drift")
    if catalog.get("data_status") != packet["source_data_status"] or catalog.get("identity_scope") != packet["source_identity_class"]:
        raise ValueError("accepted directory status drift")
    if catalog.get("admission_effect") != "NONE" or catalog.get("coverage_effect") != "NONE":
        raise ValueError("catalog claims admission/coverage")
    indices = [r.get("row_id") for r in catalog["rows"]]
    if len(set(indices)) != len(indices):
        raise ValueError("accepted directory contains duplicate source-local IDs")
    by_id = {row["row_id"]: row for row in catalog["rows"]}
    selected = packet.get("sample_source_local_row_ids", [])
    if not isinstance(selected, list) or len(selected) != 6 or len(set(selected)) != len(selected):
        raise ValueError("sample IDs must be six unique source-local rows")
    outputs = []
    for row_id in selected:
        row = by_id.get(row_id)
        if row is None:
            raise ValueError(f"source-local row absent: {row_id}")
        for key in ("title", "source_locator", "source_input", "source_group", "medium", "verification_status", "metadata_recheck_status"):
            if not isinstance(row.get(key), str) or not row[key]:
                raise ValueError(f"missing accepted source-local field: {row_id} {key}")
        if row["medium"] not in MEDIA or not _safe_https_locator(row["source_locator"]):
            raise ValueError(f"unsupported media or unsafe source locator: {row_id}")
        if row.get("identity_scope") != "SOURCE_LOCAL" or row.get("verification_status") != "UNVERIFIED_METADATA":
            raise ValueError(f"candidate incorrectly promoted: {row_id}")
        if row.get("admission_effect") != "NONE" or row.get("coverage_effect") != "NONE":
            raise ValueError(f"source row claims admission: {row_id}")
        outputs.append({
            "source_local_row_id": row_id,
            "medium": row["medium"],
            "title": row["title"],
            "context_label": row.get("series_code") or row.get("context") or "SOURCE-LOCAL",
            "source_reference_url": row["source_locator"],
            "source_group": row["source_group"],
            "source_input": row["source_input"],
            "identity_scope": row["identity_scope"],
            "verification_status": row["verification_status"],
            "metadata_recheck_status": row["metadata_recheck_status"],
            "admission_effect": "NONE",
            "coverage_effect": "NONE",
            "edition_identifier": None,
            "visual_seed_sha256": hashlib.sha256((row["medium"] + "\x00" + row_id).encode("utf-8")).hexdigest(),
            "source_row_sha256": _canonical_hash(row),
        })
    by_medium = {medium: sum(row["medium"] == medium for row in outputs) for medium in ("EPISODE", "FILM", "LITERATURE")}
    if by_medium != packet.get("medium_coverage"):
        raise ValueError("sample medium coverage drift")
    return outputs


def main():
    print(json.dumps({"status": "HELD_REFERENCE_CARD_INPUTS_ONLY", "rows": build_inputs()}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
