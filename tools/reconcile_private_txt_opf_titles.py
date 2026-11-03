#!/usr/bin/env python3
"""Private, conservative TXT filename ↔ converted-OPF title candidate crosswalk.

All filenames and bibliographic titles are held transiently in memory. Output
contains only opaque prior member IDs, OPF ordinals, digests, and classifications.
No source prose is read, no edition identity is asserted, and nothing is
admitted to a governed Source, Work, binding, or coverage ledger.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import unicodedata
from zipfile import BadZipFile, ZipFile

from inventory_opf_metadata import (
    IntakeError, build_inventory as build_opf_inventory,
    open_private_output_parent, private_output_path,
)
from source_custody_receipt import no_duplicate_keys, reject_constant


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "proposals/librarian/private-opf-metadata-20261103/MANIFEST.md"
MAX_LEDGER_BYTES = 8 * 1024**2
MAX_ARCHIVE_BYTES = 4 * 1024**3
MAX_MEMBERS = 10000
CHUNK = 1024 * 1024
STABLE = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
SHA = re.compile(r"[0-9a-f]{64}\Z")


def _stable(a, b) -> bool:
    return all(getattr(a, key) == getattr(b, key) for key in STABLE)


def _pinned_input(path: Path) -> int:
    path = Path(os.path.abspath(path))
    parent_fd = open_private_output_parent(path)
    try:
        return os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                       dir_fd=parent_fd)
    finally:
        os.close(parent_fd)


def _hash(stream) -> str:
    digest = hashlib.sha256()
    while block := stream.read(CHUNK):
        digest.update(block)
    return digest.hexdigest()


def _private_ledger(path: Path, expected: str) -> tuple[dict, str]:
    if not SHA.fullmatch(expected):
        raise IntakeError("expected ledger digest is not lowercase SHA-256")
    fd = _pinned_input(path)
    with os.fdopen(fd, "rb") as source:
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or
                not 0 < before.st_size <= MAX_LEDGER_BYTES):
            raise IntakeError("private ledger must be a bounded regular file")
        raw = source.read(MAX_LEDGER_BYTES + 1)
        after = os.fstat(fd)
    if len(raw) != before.st_size or not _stable(before, after):
        raise IntakeError("private ledger changed while reading")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected:
        raise IntakeError("prior private custody ledger digest mismatch")
    try:
        ledger = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicate_keys,
                            parse_constant=reject_constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise IntakeError("private ledger is not safe JSON") from exc
    if (type(ledger) is not dict or
            ledger.get("record_type") != "private_ebook_member_custody_inventory" or
            ledger.get("proposal_only") is not True or
            ledger.get("source_admission_effect") != "NONE" or
            ledger.get("work_identity_effect") != "NONE" or
            ledger.get("source_work_binding_effect") != "NONE" or
            ledger.get("coverage_effect") != "NONE"):
        raise IntakeError("private ledger lacks exact proposal-only contract")
    return ledger, digest


def _member_key(name: str) -> str:
    # This is the ordering used by the private original-member receipt tool.
    if (not name or len(name) > 512 or name.startswith("/") or "\\" in name or
            "\x00" in name or "//" in name or name.startswith("./")):
        raise IntakeError("unsafe original ZIP member path")
    pieces = name.rstrip("/").split("/")
    if (not pieces or len(pieces) > 16 or
            any(item in ("", ".", "..") or ":" in item for item in pieces) or
            any(unicodedata.category(ch) in ("Cc", "Cf", "Cs") for ch in name)):
        raise IntakeError("unsafe original ZIP member path")
    return unicodedata.normalize("NFKC", name.rstrip("/")).casefold()


def normalize_title(raw: str) -> str:
    """Strict Unicode/punctuation/space normalization, no prefix/word deletion."""
    if not isinstance(raw, str) or len(raw) > 512 or any(
            unicodedata.category(ch) in ("Cc", "Cf", "Cs") for ch in raw):
        return ""
    folded = unicodedata.normalize("NFKC", raw).casefold()
    key = " ".join(re.findall(r"[^\W_]+", folded, flags=re.UNICODE))
    # Single-character/generic labels must never acquire a confident match.
    return key if len(key) >= 4 else ""


def _validated_original_names(original_zip: Path, ledger: dict, expected: str) -> list:
    if not SHA.fullmatch(expected) or ledger.get("container_sha256") != expected:
        raise IntakeError("source ZIP not pinned to prior custody receipt")
    rows = ledger.get("member_receipts")
    if type(rows) is not list or not 0 < len(rows) <= MAX_MEMBERS:
        raise IntakeError("invalid private custody member cardinality")
    fd = _pinned_input(original_zip)
    with os.fdopen(fd, "rb") as source:
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or
                not 0 < before.st_size <= MAX_ARCHIVE_BYTES):
            raise IntakeError("original ZIP is not a bounded regular file")
        if _hash(source) != expected:
            raise IntakeError("original ZIP bytes disagree with accepted receipt")
        source.seek(0)
        with ZipFile(source) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_MEMBERS:
                raise IntakeError("too many original ZIP members")
            keys = [_member_key(entry.filename) for entry in entries]
            if len(keys) != len(set(keys)):
                raise IntakeError("duplicate or normalized-colliding ZIP members")
            files = sorted((entry for entry in entries if not entry.is_dir()),
                           key=lambda entry: _member_key(entry.filename))
            if len(files) != len(rows):
                raise IntakeError("private ledger member count differs from original ZIP")
            bound_names = []
            for ordinal, (info, receipt) in enumerate(zip(files, rows), 1):
                if not isinstance(receipt, dict):
                    raise IntakeError("invalid private custody member row")
                suffix = PurePosixPath(info.filename).suffix.casefold()
                if suffix not in (".txt", ".lit"):
                    raise IntakeError("unexpected original member type")
                if (receipt.get("member_id") != f"member:{ordinal:05d}" or
                        receipt.get("media_hint") != suffix.lstrip(".").upper() or
                        not isinstance(receipt.get("byte_sha256"), str) or
                        not SHA.fullmatch(receipt["byte_sha256"]) or
                        receipt.get("canonical_source_id") is not None or
                        receipt.get("canonical_work_id") is not None or
                        receipt.get("member_name_sha256") != hashlib.sha256(
                            info.filename.encode("utf-8")).hexdigest() or
                        receipt.get("uncompressed_bytes") != info.file_size or
                        receipt.get("compressed_bytes") != info.compress_size or
                        receipt.get("crc32") != f"{info.CRC:08x}"):
                    raise IntakeError("private member receipt could not bind to ZIP directory")
                bound_names.append((receipt["member_id"], suffix, info.filename))
        middle = os.fstat(fd)
        if not _stable(before, middle):
            raise IntakeError("original ZIP changed while reading directory")
        source.seek(0)
        replay = _hash(source)
        after = os.fstat(fd)
        if replay != expected or not _stable(before, after):
            raise IntakeError("original ZIP changed during replay")
    return bound_names


def _verify_manifest(original: str, opf: str) -> None:
    if not SHA.fullmatch(opf):
        raise IntakeError("converted OPF digest is not lowercase SHA-256")
    text = MANIFEST.read_text(encoding="utf-8")
    if original not in text or opf not in text:
        raise IntakeError("private archives disagree with accepted custody manifest")


def _pinned_opf_inventory(opf_zip: Path, expected_sha256: str) -> dict:
    """Pin the converted archive while the accepted OPF helper reopens it.

    `/proc/self/fd/N` resolves to the already-open inode: a swapped original
    path cannot change which bytes the helper parses or subsequently hashes.
    We require POSIX procfs rather than allowing an unsafe path fallback.
    """
    if not Path("/proc/self/fd").is_dir():
        raise IntakeError("stable converted OPF descriptor bridge unavailable")
    fd = _pinned_input(opf_zip)
    with os.fdopen(fd, "rb") as source:
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or
                not 0 < before.st_size <= MAX_ARCHIVE_BYTES):
            raise IntakeError("converted OPF ZIP is not a bounded regular file")
        if _hash(source) != expected_sha256:
            raise IntakeError("converted OPF ZIP bytes disagree with accepted manifest")
        pinned = Path(f"/proc/self/fd/{fd}")
        metadata = build_opf_inventory(pinned)
        if metadata["input_receipts"]["opf_archive_sha256"] != expected_sha256:
            raise IntakeError("converted OPF helper digest mismatch")
        middle = os.fstat(fd)
        if not _stable(before, middle):
            raise IntakeError("converted OPF ZIP changed during parsing")
        source.seek(0)
        replay = _hash(source)
        after = os.fstat(fd)
        if replay != expected_sha256 or not _stable(before, after):
            raise IntakeError("converted OPF ZIP changed during custody replay")
    return metadata


def reconcile(original_zip: Path, opf_zip: Path, private_ledger: Path, *,
              expected_original: str, expected_opf: str,
              expected_ledger: str) -> dict:
    """Strict title hypotheses only; all private labels remain in volatile RAM."""
    _verify_manifest(expected_original, expected_opf)
    ledger, ledger_digest = _private_ledger(private_ledger, expected_ledger)
    names = _validated_original_names(original_zip, ledger, expected_original)
    metadata = _pinned_opf_inventory(opf_zip, expected_opf)
    candidates = metadata["candidates"]
    if len(candidates) != metadata["summary"]["opf_packages"]:
        raise IntakeError("converted OPF metadata candidate count disagreement")

    opf_keys: dict[str, list[int]] = {}
    for ordinal, opf in enumerate(candidates, 1):
        item = opf.get("metadata")
        title = item.get("title") if isinstance(item, dict) else None
        key = normalize_title(title) if title else ""
        if key:
            opf_keys.setdefault(key, []).append(ordinal)

    txt_keys: dict[str, list[str]] = {}
    txt_names = []
    for member_id, suffix, name in names:
        if suffix == ".txt":
            key = normalize_title(PurePosixPath(name).stem)
            txt_names.append((member_id, key))
            if key:
                txt_keys.setdefault(key, []).append(member_id)

    records = []
    for member_id, key in txt_names:
        match_ordinals = opf_keys.get(key, []) if key else []
        competing_txt = txt_keys.get(key, []) if key else []
        if not match_ordinals:
            classification = "NO_EXACT_TITLE_CANDIDATE"
        elif len(match_ordinals) != 1 or len(competing_txt) != 1:
            classification = "AMBIGUOUS_EXACT_TITLE_CANDIDATES"
        else:
            classification = "UNIQUE_EXACT_TITLE_CANDIDATE_UNVERIFIED"
        records.append({
            "txt_member_id": member_id,
            "normalized_filename_title_sha256": hashlib.sha256(
                key.encode("utf-8")).hexdigest() if key else None,
            "opf_ordinals": match_ordinals,
            "opf_metadata_review_required": any(
                "review_hold" in candidates[i - 1] for i in match_ordinals),
            "classification": classification,
            "evidence": "TXT_FILENAME_VS_CONVERTED_OPF_DC_TITLE_ONLY",
            "identity_effect": "NONE",
            "edition_equivalence_effect": "NONE",
        })

    classifications = {kind: sum(row["classification"] == kind for row in records)
                       for kind in ("UNIQUE_EXACT_TITLE_CANDIDATE_UNVERIFIED",
                                    "AMBIGUOUS_EXACT_TITLE_CANDIDATES",
                                    "NO_EXACT_TITLE_CANDIDATE")}
    return {
        "record_type": "private_txt_opf_title_candidate_crosswalk",
        "schema_version": "0.1.0",
        "proposal_only": True,
        "accepted_source_effect": "NONE",
        "accepted_work_effect": "NONE",
        "source_work_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "rights_verification": "NOT_PERFORMED",
        "prior_member_ledger_sha256": ledger_digest,
        "original_container_sha256": expected_original,
        "converted_opf_container_sha256": expected_opf,
        "normalization": "NFKC_CASEFOLD_UNICODE_WORD_TOKENS_NO_WORD_REMOVAL",
        "matching_scope": "EXACT_NORMALIZED_TITLE_STRING_CANDIDATES_ONLY",
        "summary": {
            "original_file_observations": len(names),
            "txt_file_observations": len(records),
            "lit_file_observations": len(names) - len(records),
            "opf_metadata_observations": len(candidates),
            "opf_metadata_review_holds": metadata["summary"]["review_holds"],
            "txt_candidates_touching_opf_metadata_review_hold": sum(
                row["opf_metadata_review_required"] for row in records),
            "unique_exact_title_candidates_unverified":
                classifications["UNIQUE_EXACT_TITLE_CANDIDATE_UNVERIFIED"],
            "ambiguous_exact_title_txt_observations":
                classifications["AMBIGUOUS_EXACT_TITLE_CANDIDATES"],
            "no_exact_title_txt_observations":
                classifications["NO_EXACT_TITLE_CANDIDATE"],
        },
        "txt_candidate_rows": records,
    }


def _write_private(path: Path, value: dict) -> None:
    target = private_output_path(path)
    fd_parent = open_private_output_parent(target)
    try:
        pinned = os.fstat(fd_parent)
        now = os.stat(target.parent, follow_symlinks=False)
        if (pinned.st_dev, pinned.st_ino) != (now.st_dev, now.st_ino):
            raise IntakeError("private output parent changed")
        fd = os.open(target.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=fd_parent)
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(value, output, sort_keys=True, indent=2, ensure_ascii=False)
            output.write("\n")
    finally:
        os.close(fd_parent)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-zip", required=True, type=Path)
    parser.add_argument("--opf-zip", required=True, type=Path)
    parser.add_argument("--member-ledger", required=True, type=Path)
    parser.add_argument("--expected-original-sha256", required=True)
    parser.add_argument("--expected-opf-sha256", required=True)
    parser.add_argument("--expected-ledger-sha256", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        private_output_path(args.out)
        value = reconcile(args.original_zip, args.opf_zip, args.member_ledger,
                          expected_original=args.expected_original_sha256,
                          expected_opf=args.expected_opf_sha256,
                          expected_ledger=args.expected_ledger_sha256)
        _write_private(args.out, value)
    except (IntakeError, BadZipFile, OSError, ValueError, RuntimeError) as exc:
        print(f"TXT_OPF_CROSSWALK_REFUSED: {type(exc).__name__}", file=sys.stderr)
        return 1
    s = value["summary"]
    print("PRIVATE_TXT_OPF_CROSSWALK_OK "
          f"txt={s['txt_file_observations']} opf={s['opf_metadata_observations']} "
          f"exact_unique={s['unique_exact_title_candidates_unverified']} "
          f"ambiguous={s['ambiguous_exact_title_txt_observations']} "
          f"no_exact={s['no_exact_title_txt_observations']} admission=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
