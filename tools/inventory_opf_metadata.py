#!/usr/bin/env python3
"""Inventory user-supplied ebook OPF metadata offline, never ebook content.

This is a *private intake* utility. It reads only OPF package descriptions and
ZIP directory entries, never text chapters, HTML bodies, or cover images.
Output is deliberately refused inside the public repository checkout.
Neither possession of a file nor an OPF label establishes rights, canon, or an
accepted Trek Source/Work identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import unicodedata
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
MAX_MEMBERS = 10000
MAX_OPF = 1024 * 1024
MAX_TOTAL_OPF = 32 * 1024 * 1024
MAX_FIELD = 500
DC_NS = {
    "http://purl.org/dc/elements/1.0/",
    "http://purl.org/dc/elements/1.1/",
    "http://purl.org/metadata/dublin_core",  # Legacy Open eBook/ReaderWorks packages.
}
FIELDS = ("title", "creator", "identifier", "publisher", "date", "language")
DOCTYPE = re.compile(
    rb'<!DOCTYPE\s+[a-zA-Z][\w.-]*\s+(?:PUBLIC\s+"[^"<>]*"\s+"[^"<>]*"|SYSTEM\s+"[^"<>]*")\s*>',
    flags=re.IGNORECASE | re.DOTALL,
)


class IntakeError(ValueError):
    """An archive or output request violates the private intake boundary."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_members(archive: ZipFile) -> list[ZipInfo]:
    entries = archive.infolist()
    if len(entries) > MAX_MEMBERS:
        raise IntakeError("archive has too many ZIP entries")
    names = set()
    for info in entries:
        name = info.filename
        path = PurePosixPath(name)
        if (not name or "\\" in name or "\x00" in name or path.is_absolute()
                or ".." in path.parts or "." in path.parts):
            raise IntakeError("archive contains an unsafe member path")
        if name in names:
            raise IntakeError("archive contains duplicate member paths")
        names.add(name)
        if stat.S_ISLNK(info.external_attr >> 16):
            raise IntakeError("archive contains a symbolic-link member")
    return entries


def normalized_stem(name: str) -> str:
    return unicodedata.normalize("NFKC", PurePosixPath(name).stem).casefold().strip()


def clean_field(text: str | None) -> str | None:
    if text is None:
        return None
    value = " ".join(text.split()).strip()
    if not value or len(value) > MAX_FIELD or any(ord(ch) < 32 for ch in value):
        return None
    return value


def opf_metadata(raw: bytes) -> dict:
    """Parse only whitelisted Dublin Core metadata, with no DTD resolution.

    Legacy ReaderWorks OPF commonly has a simple external PUBLIC DOCTYPE. We
    remove only that exact declaration. Internal DTD subsets, entity
    declarations, and any remaining DOCTYPE are rejected before XML parsing.
    ElementTree never receives a remote DTD reference or external entity.
    """
    upper = raw.upper()
    if b"<!ENTITY" in upper or b"<![" in upper:
        raise IntakeError("OPF contains entity declarations or DTD subsets")
    scrubbed = DOCTYPE.sub(b"", raw, count=1)
    if b"<!DOCTYPE" in scrubbed.upper():
        raise IntakeError("OPF contains an unsupported document type")
    try:
        root = ET.fromstring(scrubbed)
    except ET.ParseError as exc:
        raise IntakeError("OPF XML cannot be parsed safely") from exc
    if root.tag.rsplit("}", 1)[-1].lower() != "package":
        raise IntakeError("OPF root is not a package")
    values: dict[str, list[str]] = {key: [] for key in FIELDS}
    for item in root.iter():
        if not item.tag.startswith("{"):
            continue
        namespace, local = item.tag[1:].split("}", 1)
        key = local.lower()
        if namespace in DC_NS and key in values:
            value = clean_field(item.text)
            if value and value not in values[key]:
                values[key].append(value)
    if not values["title"]:
        raise IntakeError("OPF has no usable Dublin Core title")
    return {
        "title": values["title"][0],
        "creators": values["creator"],
        "identifiers": values["identifier"],
        "publishers": values["publisher"],
        "dates": values["date"],
        "languages": values["language"],
    }


def opf_metadata_with_legacy_review(raw: bytes) -> tuple[dict, bool]:
    """Recover a known broken ReaderWorks prefix while retaining a review hold.

    Some old converted packages contain literal ``dc:Title`` and
    ``dc:Creator`` but omit their ``xmlns:dc`` declaration entirely. The
    deterministic correction is *never* treated as verified source metadata.
    Other XML failures remain quarantined rather than guessed from filenames.
    """
    try:
        return opf_metadata(raw), False
    except IntakeError:
        if (b"<dc-metadata>" not in raw or b"xmlns:dc" in raw
                or b"<dc:Title>" not in raw):
            raise
        repaired = raw.replace(
            b"<dc-metadata>",
            b'<dc-metadata xmlns:dc="http://purl.org/metadata/dublin_core">',
            1,
        )
        return opf_metadata(repaired), True


def build_inventory(converted_zip: Path, original_zip: Path | None = None) -> dict:
    """Read only OPF members and ZIP directories; return candidate metadata."""
    if not converted_zip.is_file():
        raise IntakeError("converted OPF ZIP does not exist")
    original_index: dict[str, int] = {}
    source_types: dict[str, int] = {}
    original_digest = None
    if original_zip is not None:
        if not original_zip.is_file():
            raise IntakeError("original ebook ZIP does not exist")
        with ZipFile(original_zip) as original:
            for member in safe_members(original):
                if member.is_dir():
                    continue
                suffix = PurePosixPath(member.filename).suffix.lower()
                source_types[suffix] = source_types.get(suffix, 0) + 1
                if suffix == ".lit":
                    stem = normalized_stem(member.filename)
                    original_index[stem] = original_index.get(stem, 0) + 1
        original_digest = sha256_file(original_zip)

    records: list[dict] = []
    with ZipFile(converted_zip) as archive:
        members = safe_members(archive)
        opfs = sorted((entry for entry in members if not entry.is_dir()
                       and PurePosixPath(entry.filename).suffix.lower() == ".opf"),
                      key=lambda item: item.filename.casefold())
        total = sum(info.file_size for info in opfs)
        if total > MAX_TOTAL_OPF:
            raise IntakeError("OPF metadata total exceeds bounded limit")
        for info in opfs:
            record = {
                "record_type": "literary_work_metadata_candidate",
                "status": "CANDIDATE",
                "canonical_work_id": None,
                "accepted_corpus_effect": "NONE",
                "archive_member": info.filename,
                "opf_sha256": None,
                "metadata_status": "REVIEW_REQUIRED",
                "metadata": None,
                "original_lit_match": None,
            }
            if original_zip is not None:
                stem = normalized_stem(PurePosixPath(info.filename).parent.name)
                matches = original_index.get(stem, 0)
                record["original_lit_match"] = (
                    "MATCHED_STEM" if matches == 1 else
                    "AMBIGUOUS_STEM" if matches > 1 else "UNMATCHED_STEM"
                )
            if info.file_size > MAX_OPF:
                record["review_hold"] = "OPF exceeds per-file metadata limit"
            else:
                with archive.open(info) as stream:
                    raw = stream.read(MAX_OPF + 1)
                if len(raw) > MAX_OPF:
                    raise IntakeError("OPF decompressed beyond metadata limit")
                record["opf_sha256"] = hashlib.sha256(raw).hexdigest()
                try:
                    record["metadata"], repaired = opf_metadata_with_legacy_review(raw)
                    record["metadata_status"] = (
                        "PARSED_LEGACY_REVIEW_REQUIRED" if repaired else "PARSED_UNVERIFIED"
                    )
                    if repaired:
                        record["review_hold"] = "undeclared Dublin Core XML prefix repaired for candidate review"
                except IntakeError as exc:
                    record["review_hold"] = str(exc)
            records.append(record)
    return {
        "schema_version": "0.1.0",
        "proposal_only": True,
        "rights_status": "USER_SUPPLIED_FILES_RIGHTS_NOT_VERIFIED",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "input_receipts": {
            "opf_archive_sha256": sha256_file(converted_zip),
            "original_archive_sha256": original_digest,
        },
        "summary": {
            "opf_packages": len(records),
            "parsed_metadata": sum(row["metadata"] is not None for row in records),
            "review_holds": sum("review_hold" in row for row in records),
            "matched_lit_stems": sum(row["original_lit_match"] == "MATCHED_STEM" for row in records),
            "source_asset_extensions": dict(sorted(source_types.items())),
        },
        "candidates": records,
    }


def private_output_path(path: Path) -> Path:
    target = path.expanduser().resolve()
    if target == ROOT or ROOT in target.parents:
        raise IntakeError("private ebook inventories must be written outside the public repo")
    if target.exists():
        raise IntakeError("refusing to overwrite an existing inventory")
    if not target.parent.is_dir():
        raise IntakeError("output parent directory must already exist")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--opf-zip", type=Path, required=True)
    parser.add_argument("--original-zip", type=Path)
    parser.add_argument("--out", type=Path, required=True,
                        help="new private output JSON outside the public checkout")
    args = parser.parse_args()
    try:
        out = private_output_path(args.out)
        inventory = build_inventory(args.opf_zip, args.original_zip)
        payload = json.dumps(inventory, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
        # Exclusive creation closes the check/write race: even if a second
        # process creates the target after private_output_path(), never clobber
        # that file or follow an existing final-component symlink.
        with out.open("x", encoding="utf-8", errors="strict") as stream:
            stream.write(payload)
    except (IntakeError, BadZipFile, OSError, ValueError) as exc:
        print(f"OPF intake refused: {exc}", file=sys.stderr)
        return 1
    summary = inventory["summary"]
    print(f"Private OPF inventory: {summary['opf_packages']} packages, "
          f"{summary['parsed_metadata']} parsed, {summary['review_holds']} holds; "
          f"{summary['matched_lit_stems']} matching LIT stems; "
          "0 accepted Work/Source effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
