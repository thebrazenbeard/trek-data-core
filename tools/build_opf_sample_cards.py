#!/usr/bin/env python3
"""Deterministic, held source-local OPF card sample; never a public Work catalog.

The accepted 347-row metadata packet is already public, but its book sources
remain owner-private and the Explorer's OPF shelf is explicitly opt-in. This
proposal produces a bounded cross-era *review sample* without changing that
privacy/display boundary or the byte-pinned historical discovery directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "proposals/librarian/private-opf-metadata-20261103/observations.json"
OUTPUT = "proposals/consolidator/opf-source-local-review-sample-20261103/cards.json"
SOURCE_SHA256 = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
BASE_SHA256 = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"

# Selection is a sample, *not* semantic deduplication, an exhaustive census,
# or proof of distinct books. Each ordinal is an original owner-private OPF
# metadata observation, not an admitted global literary Work.
SAMPLE_ORDINALS = (
    10, 12, 16, 21, 25, 31, 36, 40,            # Starfleet Corps of Engineers
    55, 56, 61, 70, 71, 75, 106, 110,          # Next Generation title claims
    150, 155, 161, 166, 175, 181, 190, 201, 231, 236,  # Original Series claims
    260, 261, 275,                             # Voyager title claims
    290, 295, 296, 301, 320,                   # Deep Space Nine title claims
    325, 326,                                  # Enterprise title claims
    335, 336, 341,                             # New Frontier title claims
)
assert len(SAMPLE_ORDINALS) == 39 and len(set(SAMPLE_ORDINALS)) == 39


def encode(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def pinned_source(root: Path) -> dict:
    path = root / SOURCE
    base = root / "explorer/discovery-catalog.json"
    if not path.is_file() or path.is_symlink() or not base.is_file() or base.is_symlink():
        raise ValueError("missing or symlinked accepted source/base")
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("owner-private OPF metadata derivative changed")
    if hashlib.sha256(base.read_bytes()).hexdigest() != BASE_SHA256:
        raise ValueError("historic 1214-row discovery catalog changed")
    source = json.loads(path.read_bytes())
    expected = {
        "source_kind": "OWNER_PRIVATE_OPF_XML_METADATA",
        "private_member_paths_exported": False,
        "private_identifier_guids_exported": False,
        "copyrighted_text_or_images_exported": False,
        "ebook_full_text_read": False,
        "edition_binding_verified": False,
        "public_synopsis_approved": False,
        "work_admission_effect": "NONE",
        "coverage_effect": "NONE",
    }
    for key, value in expected.items():
        if source.get(key) != value:
            raise ValueError("OPF metadata custody flag changed: " + key)
    if not isinstance(source.get("rows"), list) or len(source["rows"]) != 347:
        raise ValueError("unexpected source-local OPF entry count")
    return source


def compile_sample(source: dict) -> dict:
    rows = source["rows"]
    cards = []
    for ordinal in SAMPLE_ORDINALS:
        item = rows[ordinal - 1]
        source_id = f"opf-local:{ordinal:04d}"
        if item.get("source_local_id") != source_id or item.get("parse_status") != "PARSED":
            raise ValueError("selected OPF identity or XML parse state changed")
        title = item.get("title")
        creators = item.get("creator")
        if not isinstance(title, list) or len(title) != 1 or not isinstance(title[0], str) or not title[0].strip():
            raise ValueError("selected OPF title is not a single literal")
        if not isinstance(creators, list) or not creators or any(not isinstance(c, str) or not c.strip() for c in creators):
            raise ValueError("selected OPF has no usable creator metadata literal")
        entry_sha = item.get("opf_entry_sha256")
        if not isinstance(entry_sha, str) or len(entry_sha) != 64 or any(c not in "0123456789abcdef" for c in entry_sha):
            raise ValueError("bad exact OPF XML entry digest")
        cards.append({
            "card_id": f"opf-metadata-sample:{source_id}",
            "source_local_id": source_id,
            "title_as_encoded_in_opf": title[0],
            "creator_strings_as_encoded_in_opf": creators,
            "original_opf_xml_sha256": entry_sha,
            "source_input": SOURCE,
            "source_observation_json_pointer": f"/rows/{ordinal - 1}",
            "record_class": "OWNER_PRIVATE_OPF_XML_METADATA",
            "metadata_parse_state": "PARSED",
            "edition_identity": "NOT_VERIFIED",
            "work_identity": "NOT_RECONCILED",
            "source_to_work_binding": "NOT_VERIFIED",
            "container_or_omnibus_contents": "NOT_RECONCILED",
            "data_rights": "UNKNOWN",
            "full_text_read": False,
            "synopsis_release": "NONE",
            "artwork_release": "NONE",
            "admission_effect": "NONE",
            "coverage_effect": "NONE",
        })
    return {
        "schema_version": "1.0.0",
        "data_status": "HELD_SOURCE_LOCAL_OPF_METADATA_REVIEW_SAMPLE_ONLY",
        "public_explorer_visibility": "NOT_AUTO_LOADED",
        "selected_rows": len(cards),
        "source_observation_count": len(rows),
        "distinct_work_count": None,
        "data_rights": "UNKNOWN",
        "source_input": SOURCE,
        "source_input_sha256": SOURCE_SHA256,
        "historical_directory_sha256": BASE_SHA256,
        "historical_directory_rows": 1214,
        "card_rows": cards,
        "edition_bindings_verified": 0,
        "full_text_sources_read": 0,
        "work_admission_effect": "NONE",
        "coverage_effect": "NONE",
        "artwork_release_effect": "NONE",
        "synopsis_release_effect": "NONE",
    }


def build(root: Path = ROOT) -> dict:
    return compile_sample(pinned_source(root))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="require committed byte-for-byte output")
    args = parser.parse_args()
    output = ROOT / OUTPUT
    value = encode(build())
    if args.check:
        if not output.is_file() or output.is_symlink() or output.read_bytes() != value:
            parser.error("source-local OPF sample differs from pinned projection")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(value)
    print("PASS: 39 exact-source OPF XML metadata cards; 0 admitted Works / text reads / released artwork")


if __name__ == "__main__":
    main()
