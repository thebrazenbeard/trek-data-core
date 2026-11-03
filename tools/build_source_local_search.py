#!/usr/bin/env python3
"""Deterministic, non-admitting search projection over approved public Explorer sidecars.

This is a search index of source-local *observations*, not a work/canon database.
No title matching, global identity resolution, or subjective semantic tagging occurs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "explorer/search-catalog.json"
INPUTS = (
    "explorer/discovery-catalog.json",
    "explorer/metadata-rechecks.json",
    "explorer/synopsis-catalog.json",
    "explorer/short-synopsis-catalog.json",
)
SERIES = frozenset("TOS TAS TNG DS9 VOY ENT DIS PIC LD SNW PRO SFA".split())
VALID_MEDIA = frozenset("EPISODE FILM LITERATURE SHORT_FORM AUDIO".split())
ROW_ID = re.compile(r"^[a-z0-9:_.-]{3,210}$")


def normalized(value: object) -> str:
    """Normalize for retrieval only. Preserve original spelling in results."""
    return unicodedata.normalize("NFKD", str(value)).casefold()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_inputs(root: Path = ROOT) -> tuple[dict[str, dict], list[dict]]:
    data = {}
    digests = []
    for relative in INPUTS:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing or symlinked public sidecar: {relative}")
        content = path.read_bytes()
        data[relative] = json.loads(content)
        digests.append({"path": relative, "sha256": hashlib.sha256(content).hexdigest()})
    return data, digests


def build(root: Path = ROOT) -> dict:
    inputs, digests = load_inputs(root)
    directory = inputs[INPUTS[0]]
    metadata = inputs[INPUTS[1]]
    syn_sources = [inputs[relative] for relative in INPUTS[2:]]
    if directory.get("schema_version") != "1.0.0" or directory.get("data_status") != "DISCOVERY_ONLY" or \
       directory.get("identity_scope") != "SOURCE_LOCAL_NOT_DEDUPLICATED" or \
       directory.get("row_count") != len(directory.get("rows", [])) or \
       directory.get("coverage_effect") != "NONE" or directory.get("admission_effect") != "NONE":
        raise ValueError("Discovery denominator/scope invalid; cannot project")
    if metadata.get("data_status") != "SOURCE_LOCAL_RENDERED_METADATA_RECHECKS_DISPLAY_ONLY" or \
       metadata.get("coverage_effect") != "NONE" or metadata.get("admission_effect") != "NONE" or \
       metadata.get("rendered_metadata_rechecks") != len(metadata.get("rows", [])):
        raise ValueError("Metadata recheck sidecar does not meet public contract")
    if any(s.get("data_status") != "EDITORIALLY_REVIEWED_DISPLAY_ONLY" or
           s.get("coverage_effect") != "NONE" or s.get("admission_effect") != "NONE" or
           s.get("synopsis_count") != len(s.get("synopses", [])) for s in syn_sources):
        raise ValueError("Synopsis review sidecar does not meet public contract")

    by_id = {}
    for source in directory["rows"]:
        ident = source["row_id"]
        if not ROW_ID.fullmatch(ident) or ident in by_id or source["medium"] not in VALID_MEDIA or \
           source["identity_scope"] != "SOURCE_LOCAL" or source["verification_status"] != "UNVERIFIED_METADATA" or \
           source["coverage_effect"] != "NONE" or source["admission_effect"] != "NONE":
            raise ValueError(f"Bad or duplicate source-local row: {ident}")
        by_id[ident] = source
    checks = {}
    for check in metadata["rows"]:
        ident = check["row_id"]
        if ident in checks or ident not in by_id or check["coverage_effect"] != "NONE" or check["admission_effect"] != "NONE":
            raise ValueError(f"Foreign/duplicate/promoted metadata recheck: {ident}")
        if check["source_local_title"] != by_id[ident]["title"] or check["source_local_group"] != by_id[ident]["source_group"]:
            raise ValueError(f"Recheck source row drift: {ident}")
        checks[ident] = check
    synopsis = {}
    for sidecar in syn_sources:
        for entry in sidecar["synopses"]:
            # An explicit directory row key/alias is the only permitted join.
            directory_key = entry["directory_alias_row_id"] or entry["row_id"]
            if not directory_key.startswith("directory:"):
                raise ValueError("Synopsis lacks explicit directory key")
            ident = directory_key.removeprefix("directory:")
            if ident in synopsis or ident not in by_id or entry["medium"] != by_id[ident]["medium"] or \
               entry["source_group"] != by_id[ident]["source_group"] or \
               entry["source_input"] != by_id[ident]["source_input"] or \
               entry["source_locator"] != by_id[ident]["source_locator"]:
                raise ValueError(f"Unlinked or mismatched synopsis: {directory_key}")
            synopsis[ident] = entry
    rows = []
    for ident, item in sorted(by_id.items()):
        context_code = item["context"].split(maxsplit=1)[0]
        series = context_code if item["medium"] == "EPISODE" and context_code in SERIES else None
        check = checks.get(ident)
        overview = synopsis.get(ident)
        metadata_status = "rechecked_exact" if check and check["title_check"] == "EXACT" else \
            "rechecked_unresolved" if check else "not_rechecked"
        synopsis_status = "reviewed_publisher_paraphrase" if overview else "pending"
        # Only structural facets, never inferred story topics/themes, work identity, or canonicity.
        tags = ["medium:" + item["medium"].lower(),
                "kind:" + item["candidate_kind"].lower(),
                "source:" + item["source_group"].lower(),
                "metadata:" + metadata_status,
                "synopsis:" + synopsis_status]
        if series:
            tags.append("series:" + series.lower())
        searchable = normalized(" ".join([item["title"], item["context"], item["candidate_kind"],
                                          item["source_group"], item["source_input"],
                                          *item["details"], overview["overview_text"] if overview else ""]))
        rows.append({
            "row_id": ident, "title": item["title"], "medium": item["medium"],
            "candidate_kind": item["candidate_kind"], "context": item["context"],
            "series_code": series, "source_group": item["source_group"],
            "source_input": item["source_input"], "source_locator": item["source_locator"],
            "verification_status": item["verification_status"], "metadata_recheck_status": metadata_status,
            "metadata_recheck_batch": check["recheck_batch"] if check else None,
            "synopsis_status": synopsis_status, "synopsis_receipt_sha256": overview["editorial_receipt_sha256"] if overview else None,
            "tags": sorted(tags), "search_text": searchable,
            "identity_scope": "SOURCE_LOCAL", "coverage_effect": "NONE", "admission_effect": "NONE",
        })
    return {
        "schema_version": "1.0.0", "data_status": "SOURCE_LOCAL_SEARCH_PROJECTION_ONLY",
        "identity_scope": "SOURCE_LOCAL_NOT_DEDUPLICATED", "denominator_status": "NOT_ESTABLISHED",
        "coverage_effect": "NONE", "admission_effect": "NONE", "row_count": len(rows),
        "source_input_sha256": digests,
        "facet_counts": {
            name: dict(sorted(Counter(row[name] or "none" for row in rows).items()))
            for name in ("medium", "candidate_kind", "series_code", "source_group", "metadata_recheck_status", "synopsis_status")
        },
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare committed index with deterministic rebuild")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    output = encoded(build())
    if args.check:
        if not args.out.is_file() or args.out.read_bytes() != output:
            parser.error("Search index is missing or does not match source-pinned inputs")
        print(f"PASS deterministic search index: {len(build()['rows'])} source-local rows")
    else:
        args.out.write_bytes(output)
        print(f"Wrote {args.out} ({len(output)} bytes)")


if __name__ == "__main__":
    main()
