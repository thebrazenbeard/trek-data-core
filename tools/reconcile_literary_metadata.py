#!/usr/bin/env python3
"""Build private, noncanonical Work/edition/collection proposals from OPF inventory.

Only the selected bibliographic metadata of a prior private OPF intake and
optional manually supplied bibliography references are used. No ebook ZIPs,
prose, covers, network sources, accepted registry, or public inventories are
read. No identity or SOURCE_BOUND status can be promoted by this program.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import unicodedata
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_ITEMS = 10000
MAX_FIELD = 500
MAX_CITATION_URL = 2048
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
METADATA_LISTS = ("creators", "identifiers", "publishers", "dates", "languages")
METADATA_FIELDS = {"title", *METADATA_LISTS}
FORMS = {"SINGLE_WORK", "OMNIBUS_EDITION", "ANTHOLOGY_EDITION", "MULTIPART_SINGLE_WORK"}
WORK_TYPES = {"NOVEL", "NOVELLA", "SHORT_STORY", "COLLECTION", "OTHER", "UNKNOWN"}
SUPPORTS = {"PUBLICATION_FORM", "WORK_STRUCTURE", "PART_STRUCTURE", "EDITION_METADATA"}
PARSED = {"PARSED_UNVERIFIED", "PARSED_LEGACY_REVIEW_REQUIRED"}


class ReconciliationError(ValueError):
    """Untrusted input fails a proposal-only or privacy invariant."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReconciliationError(message)


def mapping(value: object, label: str) -> dict:
    require(type(value) is dict, f"{label} must be an object")
    return value


def exact_keys(value: dict, allowed: set[str], required: set[str], label: str) -> None:
    require(required <= value.keys() and value.keys() <= allowed,
            f"{label} has missing or unsupported fields")


def string(value: object, label: str, max_length: int = MAX_FIELD) -> str:
    require(type(value) is str and bool(value.strip()) and len(value) <= max_length
            and not any(ord(ch) < 32 or ord(ch) == 127 for ch in value),
            f"{label} must be bounded, nonempty text")
    return value.strip()


def string_list(value: object, label: str, *, nonempty: bool = False) -> list[str]:
    require(type(value) is list and len(value) <= 100 and (not nonempty or bool(value)),
            f"{label} must be a bounded list")
    return [string(item, label) for item in value]


def digest(value: object, label: str, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    require(type(value) is str and SHA256.fullmatch(value) is not None,
            f"{label} must be a lowercase SHA-256 digest")
    return value


def safe_member(value: object) -> str:
    member = string(value, "archive member", 2048)
    path = PurePosixPath(member)
    require(not member.startswith("/") and "\\" not in member and "\x00" not in member
            and ".." not in path.parts and "." not in path.parts
            and path.suffix.lower() == ".opf", "invalid OPF archive member path")
    return member


def normalized(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def private_id(prefix: str, *pieces: str) -> str:
    payload = json.dumps(pieces, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return prefix + hashlib.sha256(payload).hexdigest()[:24]


def validate_inventory(value: object) -> tuple[list[dict], dict]:
    data = mapping(value, "inventory")
    require(data.get("schema_version") == "0.1.0" and data.get("proposal_only") is True,
            "inventory must be a versioned proposal-only OPF intake")
    for effect in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect"):
        require(data.get(effect) == "NONE", "inventory contains an accepted-state effect")
    require(data.get("rights_status") == "USER_SUPPLIED_FILES_RIGHTS_NOT_VERIFIED",
            "inventory must not claim reproduction or publication rights")
    receipts = mapping(data.get("input_receipts"), "intake receipts")
    exact_keys(receipts, {"opf_archive_sha256", "original_archive_sha256"},
               {"opf_archive_sha256", "original_archive_sha256"}, "intake receipts")
    opf_receipt = digest(receipts["opf_archive_sha256"], "OPF ZIP receipt")
    original_receipt = digest(receipts["original_archive_sha256"], "source ZIP receipt",
                              optional=True)
    rows = data.get("candidates")
    require(type(rows) is list and len(rows) <= MAX_ITEMS,
            "inventory candidates must be a bounded list")
    seen: set[str] = set()
    prepared = []
    for row in rows:
        item = mapping(row, "OPF candidate")
        require(item.get("record_type") == "literary_work_metadata_candidate"
                and item.get("status") == "CANDIDATE"
                and item.get("canonical_work_id") is None
                and item.get("accepted_corpus_effect") == "NONE",
                "OPF candidate violates noncanonical intake status")
        member = safe_member(item.get("archive_member"))
        require(member not in seen, "duplicate OPF candidate member")
        seen.add(member)
        opf_hash = digest(item.get("opf_sha256"), "OPF description digest", optional=True)
        metadata_status = item.get("metadata_status")
        require(type(metadata_status) is str and metadata_status in PARSED | {"REVIEW_REQUIRED"},
                "unknown OPF metadata review status")
        raw_metadata = item.get("metadata")
        if raw_metadata is None:
            require(metadata_status == "REVIEW_REQUIRED", "parsed OPF metadata is missing")
            meta = None
        else:
            require(metadata_status in PARSED and opf_hash is not None,
                    "OPF descriptive fields lack parsed status or digest")
            raw_metadata = mapping(raw_metadata, "OPF metadata")
            exact_keys(raw_metadata, METADATA_FIELDS, METADATA_FIELDS, "OPF metadata")
            meta = {"title": string(raw_metadata["title"], "OPF title")}
            for key in METADATA_LISTS:
                meta[key] = string_list(raw_metadata[key], f"OPF {key}")
        hold = item.get("review_hold")
        if hold is not None:
            string(hold, "review hold")  # Validate, but never copy arbitrary text to output.
        require(metadata_status != "PARSED_LEGACY_REVIEW_REQUIRED" or hold is not None,
                "repaired OPF metadata must retain a review hold")
        hint = item.get("original_lit_match")
        require(hint in (None, "MATCHED_STEM", "AMBIGUOUS_STEM", "UNMATCHED_STEM"),
                "invalid source filename hint")
        prepared.append({"member": member, "opf_hash": opf_hash,
                         "metadata_status": metadata_status, "metadata": meta,
                         "has_hold": hold is not None, "lit_hint": hint})
    summary = mapping(data.get("summary"), "intake summary")
    counters = ("opf_packages", "parsed_metadata", "review_holds", "matched_lit_stems")
    require(all(type(summary.get(key)) is int for key in counters)
            and summary["opf_packages"] == len(prepared)
            and summary["parsed_metadata"] == sum(x["metadata"] is not None for x in prepared)
            and summary["review_holds"] == sum(x["has_hold"] for x in prepared)
            and summary["matched_lit_stems"] == sum(x["lit_hint"] == "MATCHED_STEM" for x in prepared),
            "intake summary contradicts candidate records")
    return prepared, {"opf_archive_sha256": opf_receipt,
                      "original_archive_sha256": original_receipt}


def bibliography(value: object) -> list[dict]:
    require(type(value) is list and 0 < len(value) <= 20,
            "a review needs bounded external bibliographic citations")
    result = []
    for entry in value:
        ref = mapping(entry, "bibliographic citation")
        exact_keys(ref, {"provider", "url", "retrieved_on", "supports"},
                   {"provider", "url", "retrieved_on", "supports"}, "bibliographic citation")
        provider = string(ref["provider"], "citation provider")
        url = string(ref["url"], "citation URL", MAX_CITATION_URL)
        try:
            parts = urlsplit(url)
            hostname = parts.hostname
        except ValueError as exc:
            raise ReconciliationError("malformed external citation URL") from exc
        # This is a syntax boundary, not a network reachability or authority
        # check. Citation locators are never fetched or trusted as evidence.
        require(parts.scheme == "https" and bool(hostname) and not parts.username
                and not parts.password and not parts.fragment and not any(
                    ch.isspace() for ch in url), "citations need HTTPS URL syntax")
        when = string(ref["retrieved_on"], "retrieval date", 10)
        try:
            require(date.fromisoformat(when).isoformat() == when, "invalid ISO retrieval date")
        except ValueError as exc:
            raise ReconciliationError("invalid ISO retrieval date") from exc
        supports = string_list(ref["supports"], "citation support", nonempty=True)
        require(set(supports) <= SUPPORTS and len(supports) == len(set(supports)),
                "unknown or duplicate bibliographic support types")
        result.append({"provider": provider, "url": url, "retrieved_on": when,
                       "supports": supports, "verification": "CITATION_SUPPLIED_NOT_CHECKED"})
    return result


def validate_reviews(value: object, candidates: set[str], eligible: set[str]) -> dict[str, dict]:
    if value is None:
        return {}
    data = mapping(value, "review file")
    exact_keys(data, {"schema_version", "reviews"}, {"schema_version", "reviews"}, "review file")
    require(data["schema_version"] == "0.1.0", "unsupported bibliographic review version")
    entries = data["reviews"]
    require(type(entries) is list and len(entries) <= MAX_ITEMS, "reviews must be bounded list")
    by_id = {}
    for entry in entries:
        review = mapping(entry, "structure review")
        exact_keys(review, {"candidate_id", "publication_form", "works", "parts", "bibliographic_references"},
                   {"candidate_id", "publication_form", "works", "parts", "bibliographic_references"},
                   "structure review")
        cid = string(review["candidate_id"], "review candidate ID")
        require(cid in candidates and cid in eligible and cid not in by_id,
                "review target is unknown, unparsed, or duplicated")
        form = review["publication_form"]
        require(type(form) is str and form in FORMS,
                "review needs an explicit supported publication form")
        works = review["works"]
        require(type(works) is list and 0 < len(works) <= 100,
                "review needs a bounded set of proposed component Works")
        validated_works = []
        seen_works = set()
        for raw_work in works:
            work = mapping(raw_work, "proposed Work")
            exact_keys(work, {"title", "creators", "work_type"},
                       {"title", "creators", "work_type"}, "proposed Work")
            title = string(work["title"], "proposed Work title")
            creators = string_list(work["creators"], "proposed Work creators", nonempty=True)
            kind = work["work_type"]
            require(type(kind) is str and kind in WORK_TYPES,
                    "unknown proposed literary Work type")
            key = (normalized(title), tuple(sorted(normalized(name) for name in creators)))
            require(key not in seen_works, "duplicate component Work requires resolution")
            seen_works.add(key)
            validated_works.append({"title": title, "creators": creators, "work_type": kind})
        parts = string_list(review["parts"], "multipart labels")
        require(len(parts) == len(set(normalized(part) for part in parts)),
                "multipart labels must be distinct")
        if form in {"SINGLE_WORK", "MULTIPART_SINGLE_WORK"}:
            require(len(works) == 1, "single-Work form cannot propose multiple Works")
        else:
            require(len(works) >= 2, "omnibus/anthology needs at least two distinct Works")
        if form == "MULTIPART_SINGLE_WORK":
            require(len(parts) >= 2, "multipart form needs at least two ordered part labels")
        else:
            require(not parts, "parts are only supported for multipart single-Work editions")
        refs = bibliography(review["bibliographic_references"])
        claims = set().union(*(set(ref["supports"]) for ref in refs))
        needed = {"PUBLICATION_FORM", "WORK_STRUCTURE"}
        if form == "MULTIPART_SINGLE_WORK":
            needed.add("PART_STRUCTURE")
        require(needed <= claims, "external citations must support the proposed form and structure")
        by_id[cid] = {"publication_form": form, "works": validated_works,
                     "parts": parts, "bibliographic_references": refs}
    return by_id


def build_proposals(inventory: object, reviews: object = None) -> dict:
    rows, receipts = validate_inventory(inventory)
    rows.sort(key=lambda row: (row["member"].casefold(), row["member"]))
    group_members: dict[tuple, list[str]] = defaultdict(list)
    for row in rows:
        row["candidate_id"] = private_id("PRIVATE-LIT-", receipts["opf_archive_sha256"],
                                          row["member"], row["opf_hash"] or "NO_OPF_HASH")
        meta = row["metadata"]
        if meta and meta["creators"]:
            key = (normalized(meta["title"]),
                   tuple(sorted(normalized(c) for c in meta["creators"])))
            group_members[key].append(row["candidate_id"])
            row["group_key"] = key
    by_id = validate_reviews(reviews, {r["candidate_id"] for r in rows},
                             {r["candidate_id"] for r in rows if r["metadata"] is not None})
    items = []
    groups = 0
    for members in group_members.values():
        groups += len(members) > 1
    for row in rows:
        cid = row["candidate_id"]
        meta = row["metadata"]
        review = by_id.get(cid)
        matching = group_members.get(row.get("group_key"), [])
        flags = []
        if row["has_hold"]:
            flags.append("INPUT_REVIEW_HOLD")
        if row["metadata_status"] == "PARSED_LEGACY_REVIEW_REQUIRED":
            flags.append("LEGACY_XML_REPAIR_UNVERIFIED")
        if meta is None:
            flags.append("OPF_METADATA_UNPARSED")
        if row["lit_hint"] != "MATCHED_STEM":
            flags.append("NO_UNIQUE_SOURCE_FILENAME_HINT")
        if len(matching) > 1:
            flags.append("MATCHING_TITLE_CREATOR_REVIEW_ONLY")
        work_candidates = []
        part_candidates = []
        if review:
            for index, work in enumerate(review["works"], 1):
                work_candidates.append({"candidate_id": f"{cid}-WORK-{index:03d}",
                                        "status": "CANDIDATE", "canonical_work_id": None,
                                        **work})
            if review["publication_form"] == "MULTIPART_SINGLE_WORK":
                part_candidates = [
                    {"sequence": index, "label": label,
                     "work_candidate_id": work_candidates[0]["candidate_id"],
                     "canonical_part_id": None, "status": "CANDIDATE"}
                    for index, label in enumerate(review["parts"], 1)
                ]
        group = (private_id("PRIVATE-RELATED-", row["group_key"][0],
                            *row["group_key"][1]) if len(matching) > 1 else None)
        items.append({
            "candidate_id": cid, "status": "CANDIDATE",
            "canonical_work_id": None, "canonical_edition_id": None, "canonical_source_id": None,
            "source_manifestation": {
                "kind": "CONVERTED_OPF_DESCRIPTION", "archive_member": row["member"],
                "opf_sha256": row["opf_hash"], "original_lit_stem_hint": row["lit_hint"],
                "lineage": "DERIVED_FROM_USER_SOURCE", "independent_witness_count": 0,
                "source_binding_status": "NOT_PROPOSED",
            },
            "edition_candidate": {"status": "CANDIDATE", "canonical_edition_id": None,
                                  "metadata": meta, "identity_status": "OPF_DESCRIPTION_UNVERIFIED"},
            "publication_form": review["publication_form"] if review else "UNRESOLVED",
            "structure_review": "REVIEWER_PROPOSED_UNVERIFIED" if review else "REQUIRES_BIBLIOGRAPHIC_REVIEW",
            "work_candidates": work_candidates, "part_candidates": part_candidates,
            "bibliographic_references": review["bibliographic_references"] if review else [],
            "possible_related_group": group,
            "review_flags": flags,
        })
    return {
        "schema_version": "0.1.0", "proposal_only": True, "private_output": True,
        "rights_status": "USER_POSSESSION_DOES_NOT_ESTABLISH_RIGHTS",
        "accepted_work_effect": "NONE", "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE", "input_receipts": receipts,
        "summary": {
            "items": len(items), "unresolved_structure": len(items) - len(by_id),
            "reviewed_structure_proposals": len(by_id),
            "input_review_holds": sum(row["has_hold"] for row in rows),
            "related_review_groups": groups,
        },
        "items": items,
    }


def reject_nonfinite(_: str) -> None:
    raise ReconciliationError("nonfinite JSON values are unsupported")


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate input JSON object key")
        result[key] = value
    return result


def read_private_json(path: Path) -> object:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_NONBLOCK"):
        raise ReconciliationError("secure private JSON input open is unavailable")
    try:
        # lstat/open/fstat pins one regular input object. Without O_NONBLOCK,
        # a local attacker could replace the checked file with a FIFO and
        # hang the process between the old stat and the subsequent open.
        initial = os.lstat(path)
        require(stat.S_ISREG(initial.st_mode) and initial.st_size <= MAX_INPUT_BYTES,
                "input must be a bounded regular private JSON file")
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as stream:
            opened = os.fstat(stream.fileno())
            require(stat.S_ISREG(opened.st_mode)
                    and (opened.st_dev, opened.st_ino) == (initial.st_dev, initial.st_ino)
                    and opened.st_size <= MAX_INPUT_BYTES,
                    "private JSON input changed before secure open")
            raw = stream.read(MAX_INPUT_BYTES + 1)
        require(len(raw) <= MAX_INPUT_BYTES, "input file exceeds private metadata limit")
        return json.loads(raw, parse_constant=reject_nonfinite,
                          object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ReconciliationError("input file is not valid secure bounded UTF-8 JSON") from exc


def private_destination(path: Path) -> Path:
    target = path.expanduser().resolve()
    # Empty `.git` placeholder directories are common in managed scratch and
    # /tmp; a real checkout has a gitdir pointer file or a HEAD control file.
    git_checkout = any((parent / ".git").is_file()
                       or (parent / ".git" / "HEAD").is_file()
                       for parent in target.parents)
    require(target != ROOT and ROOT not in target.parents
            and not git_checkout,
            "private literary proposals must be written outside any Git checkout")
    require(not target.exists(), "refusing to overwrite an existing private proposal")
    require(target.parent.is_dir(), "private output parent directory does not exist")
    return target


def secure_parent_fd(target: Path) -> int:
    if (os.open not in os.supports_dir_fd or not hasattr(os, "O_DIRECTORY")
            or not hasattr(os, "O_NOFOLLOW")):
        raise ReconciliationError("secure private output creation is unavailable")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(target.anchor, flags)
    try:
        for part in target.parent.parts[1:]:
            next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True,
                        help="private JSON from inventory_opf_metadata.py")
    parser.add_argument("--reviews", type=Path,
                        help="optional private, human-authored bibliographic review JSON")
    parser.add_argument("--out", type=Path, required=True, help="new private JSON path")
    args = parser.parse_args(argv)
    try:
        target = private_destination(args.out)
        parent_fd = secure_parent_fd(target)
        try:
            result = build_proposals(read_private_json(args.inventory),
                                     read_private_json(args.reviews) if args.reviews else None)
            payload = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
            pinned = os.fstat(parent_fd)
            current = os.stat(target.parent, follow_symlinks=False)
            require((pinned.st_dev, pinned.st_ino) == (current.st_dev, current.st_ino),
                    "private output parent changed during reconciliation")
            fd = os.open(target.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=parent_fd)
            with os.fdopen(fd, "w", encoding="utf-8", errors="strict") as stream:
                stream.write(payload)
        finally:
            os.close(parent_fd)
    except (ReconciliationError, OSError, ValueError) as exc:
        print(f"Private literary proposal refused: {exc}", file=sys.stderr)
        return 1
    summary = result["summary"]
    print(f"Private proposals: {summary['items']} descriptions, "
          f"{summary['unresolved_structure']} unresolved, "
          f"{summary['reviewed_structure_proposals']} reviewer proposals, "
          f"{summary['input_review_holds']} inherited holds; 0 accepted effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
