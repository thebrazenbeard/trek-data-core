#!/usr/bin/env python3
"""Validate public-safe OPF structural anomaly receipts against accepted metadata.

This validates only a pinned public derivative, never owner-private ZIP bytes.
Synthetic URL/XML probes are regression fixtures, not private-source rereads.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = HERE / "observations.json"
SOURCE = ROOT / "proposals/librarian/private-opf-metadata-20261103/observations.json"
SOURCE_SHA256 = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
ARCHIVE_SHA256 = "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f"
ACCEPTED_MAIN = "69f0a5c46e78b9d034ff168d969374892fc997e0"
STRICT_FAILED_IDS = tuple(f"opf-local:{n:04d}" for n in (*range(50, 55), *range(140, 145), *range(282, 287)))
URI_ONLY_IDS = tuple(f"opf-local:{n:04d}" for n in (148, 203, 231, 317, 318))
ID_PATTERN = re.compile(r"^opf-local:\d{4}$")

TOP_KEYS = {
    "schema_version", "proposal_id", "accepted_main_baseline", "source_metadata_derivative",
    "source_metadata_sha256", "opaque_source_container_id", "source_container_sha256",
    "source_opf_members", "data_rights", "evidence_method", "external_xml_entities_resolved",
    "ebook_prose_or_images_read", "private_member_paths_exported", "full_ebook_text_exported",
    "artwork_exported", "source_work_binding", "edition_binding", "work_admission_effect",
    "coverage_effect", "strict_xml_parser", "manifest_link_audit",
    "original_lit_stem_encoding_candidate",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def source_rows(root: Path = ROOT) -> dict:
    path = root / SOURCE.relative_to(ROOT)
    require(path.is_file() and not path.is_symlink(), "accepted OPF metadata source missing/symlink")
    require(hashlib.sha256(path.read_bytes()).hexdigest() == SOURCE_SHA256, "accepted OPF source digest drift")
    return json.loads(path.read_text(encoding="utf-8"))


def uri_member_target(opf_member: str, href: str) -> str:
    """Return ZIP member targeted under URI semantics; never read/extract it.

    This deliberately cannot silently repair a raw '#' or '%' in a filename.
    """
    require(isinstance(opf_member, str) and opf_member.endswith(".opf"), "bad OPF relative locator")
    require(isinstance(href, str) and href != "", "missing href")
    parsed = urlsplit(href)
    require(not parsed.scheme and not parsed.netloc and not parsed.query, "external or query URL held")
    relative = unquote(parsed.path)
    require(not relative.startswith("/") and "\\" not in relative and "\x00" not in relative,
            "unsafe URL member target")
    target = posixpath.normpath(posixpath.join(posixpath.dirname(opf_member), relative))
    require(target not in ("", ".", "..") and not target.startswith("../"), "traversal URL member target")
    return target


def strict_opf_xml(xml: bytes) -> bool:
    """Synthetic-package strict parse; never resolve external document types."""
    require(isinstance(xml, bytes) and len(xml) <= 1024 * 1024, "invalid or oversized synthetic OPF")
    require(b"<!DOCTYPE" not in xml.upper() and b"<!ENTITY" not in xml.upper(), "DTD/entities held")
    ET.fromstring(xml)
    return True


def original_filename_pairing_state(stem: str) -> str:
    require(isinstance(stem, str) and stem != "", "bad original filename stem")
    return "UNRESOLVED_REPLACEMENT_CHARACTER" if "\ufffd" in stem else "CANDIDATE_ONLY"


def validate(record: dict, source: dict) -> None:
    require(isinstance(record, dict) and set(record) == TOP_KEYS, "unexpected anomaly receipt field")
    require(record["schema_version"] == "1.0.0" and
            record["proposal_id"] == "AUDITOR-PRIVATE-OPF-STRUCTURAL-20261103", "wrong anomaly receipt")
    require(record["accepted_main_baseline"] == ACCEPTED_MAIN, "accepted main mismatch")
    require(record["source_metadata_derivative"] == SOURCE.relative_to(ROOT).as_posix() and
            record["source_metadata_sha256"] == SOURCE_SHA256, "source derivative identity mismatch")
    require(record["opaque_source_container_id"] == "OWNER_PRIVATE_ST_OPF_ARCHIVE_A" and
            record["source_container_sha256"] == ARCHIVE_SHA256 and
            type(record["source_opf_members"]) is int and record["source_opf_members"] == 347,
            "private archive source identity mismatch")
    require(record["data_rights"] == "UNKNOWN" and
            record["source_work_binding"] == "UNRESOLVED" and
            record["edition_binding"] == "UNRESOLVED" and
            record["work_admission_effect"] == "NONE" and record["coverage_effect"] == "NONE",
            "false literary admissions/rights")
    require(record["evidence_method"] == "INDEPENDENT_READ_ONLY_OPF_XML_AND_ZIP_DIRECTORY_AUDIT",
            "unsupported evidence class")
    for key in ("external_xml_entities_resolved", "ebook_prose_or_images_read",
                "private_member_paths_exported", "full_ebook_text_exported", "artwork_exported"):
        require(record[key] is False, "protected private/source material was represented as released: " + key)

    require(isinstance(source, dict) and len(source.get("rows", [])) == 347, "unexpected accepted OPF rows")
    require(source["source_container"]["opaque_id"] == record["opaque_source_container_id"] and
            source["source_container"]["sha256"] == record["source_container_sha256"],
            "source archive not consistent with accepted derivative")
    indexed = {row["source_local_id"]: row for row in source["rows"]}
    require(len(indexed) == 347, "duplicate source-local IDs")
    for sid in indexed:
        require(ID_PATTERN.fullmatch(sid) is not None, "unexpected source-local identity")

    strict = record["strict_xml_parser"]
    require(set(strict) == {"parsed_packages", "undeclared_dc_namespace_entry_ids"}, "unexpected strict XML fields")
    require(type(strict["parsed_packages"]) is int and strict["parsed_packages"] == 332,
            "strict parse count drift")
    failed = strict["undeclared_dc_namespace_entry_ids"]
    require(isinstance(failed, list) and tuple(failed) == STRICT_FAILED_IDS, "strict XML anomaly IDs drifted")
    require(strict["parsed_packages"] + len(failed) == record["source_opf_members"], "OPF total mismatch")
    require({sid for sid, row in indexed.items() if row["parse_status"] == "OPF_XML_NAMESPACE_RECOVERED"} == set(failed),
            "strict namespace anomalies diverge from accepted metadata observations")

    manifest = record["manifest_link_audit"]
    require(set(manifest) == {
        "scope", "manifest_item_hrefs_examined", "literal_missing_member_targets",
        "additional_uri_decoding_mismatch_ids", "additional_uri_decoding_mismatch_class",
        "literal_missing_total", "uri_resolved_missing_total",
    }, "unexpected manifest anomaly fields")
    require(manifest["scope"] == "332_STRICTLY_PARSED_OPFS_ONLY", "overclaimed manifest coverage")
    require(type(manifest["manifest_item_hrefs_examined"]) is int and
            manifest["manifest_item_hrefs_examined"] == 2626, "manifest href count drift")
    require(manifest["literal_missing_member_targets"] == [{
        "source_local_id": "opf-local:0303", "count": 3,
        "anomaly_class": "UNESCAPED_FRAGMENT_MARKER_AND_INCORRECT_HTML_TARGET",
    }], "literal href anomaly drift")
    require(manifest["additional_uri_decoding_mismatch_ids"] == list(URI_ONLY_IDS) and
            manifest["additional_uri_decoding_mismatch_class"] ==
            "LITERAL_PERCENT26_MEMBER_NAME_REQUIRES_ESCAPED_PERCENT", "URI-only anomaly drift")
    require(type(manifest["literal_missing_total"]) is int and manifest["literal_missing_total"] == 3 and
            type(manifest["uri_resolved_missing_total"]) is int and manifest["uri_resolved_missing_total"] == 8,
            "unresolved manifest counts drift")
    require(all(indexed[sid]["parse_status"] == "PARSED" for sid in ("opf-local:0303", *URI_ONLY_IDS)),
            "manifest audit involved non-parseable OPF")
    encoding = record["original_lit_stem_encoding_candidate"]
    require(encoding == {
        "converted_opf_source_local_id": "opf-local:0156",
        "anomaly_class": "REPLACEMENT_CHARACTER_IN_ORIGINAL_LIT_FILENAME_STEM",
        "original_to_converted_filename_pairing": "UNRESOLVED",
    }, "unsafe automatic original-to-converted file identity")
    require(any("Search For Spock" in title for title in indexed["opf-local:0156"]["title"]),
            "unrelated OPF entry assigned original filename anomaly")


if __name__ == "__main__":
    validate(json.loads(DATA.read_text(encoding="utf-8")), source_rows())
    print("PASS: source-pinned private OPF structural anomaly fixture; zero Work/content release effects")
