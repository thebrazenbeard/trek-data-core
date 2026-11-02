#!/usr/bin/env python3
"""Prepare a human-review episode research packet; never admit registry records.

This intentionally does not verify a media file, fetch URLs, watch an episode,
change coverage, or write a projection. Content inspections are researcher claims
that must be independently verified before any governed record is accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MISSION_CATALOG = ROOT / "registry" / "mission_catalog.json"
INPUT_LIMIT = 64 * 1024
IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9._-]{2,63}\Z")
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
ACCESS_BASES = {"LICENSED_STREAMING", "OWNED_COPY", "RIGHTS_HOLDER_PERMISSION", "PUBLISHER_PUBLIC_METADATA"}
EVIDENCE_KINDS = {"depiction", "testimony", "sensor_report", "memory", "document", "narration", "other"}
EPISTEMIC = {"DIRECT", "CONTESTED", "UNRESOLVED", "UNKNOWN"}


class Rejected(ValueError):
    """An input cannot safely become a proposal-only research packet."""


def strict_json_pairs(pairs: list[tuple[str, object]]) -> dict:
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise Rejected(f"duplicate JSON key {key!r}")
        obj[key] = value
    return obj


def read_input(path: Path) -> dict:
    """Read one bounded regular JSON file without following a final symlink."""
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    nonblock = getattr(os, "O_NONBLOCK", 0)
    if not nofollow or not nonblock:
        raise Rejected("safe regular-file input requires O_NOFOLLOW and O_NONBLOCK")
    flags = os.O_RDONLY | nofollow | nonblock
    try:
        with os.fdopen(os.open(path, flags), "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise Rejected("input must be a regular file")
            if info.st_size > INPUT_LIMIT:
                raise Rejected("input exceeds 64 KiB limit")
            raw = stream.read(INPUT_LIMIT + 1)
    except OSError as exc:
        raise Rejected(f"unable to read regular input file ({exc.strerror or exc.__class__.__name__})") from None
    if len(raw) > INPUT_LIMIT:
        raise Rejected("input exceeds 64 KiB limit")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=strict_json_pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(Rejected(f"invalid JSON constant {value}")))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Rejected(f"input is not valid UTF-8 JSON ({exc.__class__.__name__})") from None
    if not isinstance(data, dict):
        raise Rejected("input must be a JSON object")
    return data


def shape(value: object, fields: set[str], required: set[str], field: str) -> dict:
    if not isinstance(value, dict):
        raise Rejected(f"{field} must be an object")
    if set(value) - fields:
        raise Rejected(f"{field}: unexpected fields: {', '.join(sorted(set(value) - fields))}")
    if required - set(value):
        raise Rejected(f"{field}: missing fields: {', '.join(sorted(required - set(value)))}")
    return value


def clean_text(value: object, field: str, *, max_length: int = 180) -> str:
    if not isinstance(value, str) or not value or len(value) > max_length or value != value.strip():
        raise Rejected(f"{field} must be nonblank trimmed text of at most {max_length} characters")
    if any(unicodedata.category(char) in {"Cc", "Cf", "Cs", "Zl", "Zp"} for char in value):
        raise Rejected(f"{field} contains a control/format character")
    if "<" in value or ">" in value:
        raise Rejected(f"{field} must be plain text")
    return value


def identifier(value: object, field: str) -> str:
    value = clean_text(value, field, max_length=64)
    if not IDENTIFIER.fullmatch(value):
        raise Rejected(f"{field} must be a portable proposal identifier")
    return value


def number(value: object, field: str, *, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise Rejected(f"{field} must be an integer from {minimum} to {maximum}")
    return value


def choice(value: object, options: set[str], field: str) -> str:
    if not isinstance(value, str) or value not in options:
        raise Rejected(f"{field} must be one of {', '.join(sorted(options))}")
    return value


def public_url(value: object, field: str) -> str:
    value = clean_text(value, field, max_length=500)
    try:
        parts = urlsplit(value)
        host = parts.hostname
        port = parts.port
    except ValueError:
        raise Rejected(f"{field} is not a valid public URL") from None
    if (parts.scheme != "https" or not host or "." not in host or parts.username or
            parts.password or parts.query or parts.fragment or port is not None or
            host.endswith(".local") or host.endswith(".internal") or
            host.endswith(".localhost") or host.startswith("localhost") or
            not re.fullmatch(r"[A-Za-z0-9.-]+", host) or
            re.fullmatch(r"[0-9.]+", host) or "\\" in value):
        raise Rejected(f"{field} must be a clean public HTTPS URL without credentials, query or fragment")
    return value


def missions() -> set[str]:
    catalog = json.loads(MISSION_CATALOG.read_text(encoding="utf-8"))
    return {mission["id"] for mission in catalog["missions"]}


def validate_input(data: dict) -> dict:
    shape(data, {"record_type", "schema_version", "packet_id", "fixture_only", "mission_id", "episode", "source", "observations", "assertions"},
          {"record_type", "schema_version", "packet_id", "fixture_only", "mission_id", "episode", "source", "observations", "assertions"}, "input")
    if data["record_type"] != "episode_review_input" or data["schema_version"] != "1.0.0":
        raise Rejected("record_type/schema_version must be episode_review_input/1.0.0")
    identifier(data["packet_id"], "packet_id")
    if type(data["fixture_only"]) is not bool:
        raise Rejected("fixture_only must be a boolean")
    if not isinstance(data["mission_id"], str) or data["mission_id"] not in missions():
        raise Rejected("mission_id is not in the display Mission catalog")
    ep = shape(data["episode"], {"title", "season", "episode_number", "publisher_roster_url"},
               {"title", "season", "episode_number", "publisher_roster_url"}, "episode")
    clean_text(ep["title"], "episode.title")
    number(ep["season"], "episode.season", minimum=1, maximum=100)
    number(ep["episode_number"], "episode.episode_number", minimum=1, maximum=1000)
    public_url(ep["publisher_roster_url"], "episode.publisher_roster_url")
    source = shape(data["source"],
                   {"kind", "locator", "version", "access_basis", "rights_note", "inspection", "inspected_on", "content_sha256"},
                   {"kind", "locator", "version", "access_basis", "rights_note", "inspection", "inspected_on", "content_sha256"}, "source")
    choice(source["kind"], {"EPISODE_CONTENT", "PUBLISHER_METADATA"}, "source.kind")
    public_url(source["locator"], "source.locator")
    clean_text(source["version"], "source.version")
    choice(source["access_basis"], ACCESS_BASES, "source.access_basis")
    clean_text(source["rights_note"], "source.rights_note", max_length=300)
    choice(source["inspection"], {"NOT_INSPECTED", "RESEARCHER_REPORTED"}, "source.inspection")
    if source["inspected_on"] is not None:
        if not isinstance(source["inspected_on"], str) or not ISO_DATE.fullmatch(source["inspected_on"]):
            raise Rejected("source.inspected_on must be YYYY-MM-DD or null")
        try:
            from datetime import date
            date.fromisoformat(source["inspected_on"])
        except ValueError:
            raise Rejected("source.inspected_on is not a valid date") from None
    if source["content_sha256"] is not None and (not isinstance(source["content_sha256"], str) or not SHA256.fullmatch(source["content_sha256"])):
        raise Rejected("source.content_sha256 must be a lowercase 64-hex digest or null")
    observations = data["observations"]
    assertions = data["assertions"]
    if not isinstance(observations, list) or len(observations) > 12:
        raise Rejected("observations must be an array of at most 12 entries")
    if not isinstance(assertions, list) or len(assertions) > 12:
        raise Rejected("assertions must be an array of at most 12 entries")
    inspected = source["inspection"] == "RESEARCHER_REPORTED"
    if inspected:
        if (source["kind"] != "EPISODE_CONTENT" or source["access_basis"] == "PUBLISHER_PUBLIC_METADATA" or
                source["inspected_on"] is None or source["content_sha256"] is None or
                not observations or not assertions):
            raise Rejected("content inspection requires an episode-content source, lawful access basis, date, declared digest, observations and linked assertions")
        if len(source["rights_note"]) < 24:
            raise Rejected("content inspection requires a specific rights_note of at least 24 characters")
    elif (source["kind"] != "PUBLISHER_METADATA" or source["access_basis"] != "PUBLISHER_PUBLIC_METADATA" or
          source["inspected_on"] is not None or source["content_sha256"] is not None or observations or assertions):
        raise Rejected("uninspected source may contain publisher metadata only, with no media digest or narrative evidence")
    seen_evidence = set()
    for i, item in enumerate(observations):
        label = f"observations[{i}]"
        item = shape(item, {"evidence_id", "cue_start_seconds", "cue_end_seconds", "kind", "epistemic_status", "original_note"},
                     {"evidence_id", "cue_start_seconds", "cue_end_seconds", "kind", "epistemic_status", "original_note"}, label)
        eid = identifier(item["evidence_id"], f"{label}.evidence_id")
        if eid in seen_evidence:
            raise Rejected(f"duplicate evidence_id {eid}")
        seen_evidence.add(eid)
        start = number(item["cue_start_seconds"], f"{label}.cue_start_seconds", minimum=0, maximum=86400)
        end = number(item["cue_end_seconds"], f"{label}.cue_end_seconds", minimum=1, maximum=86400)
        if end <= start or end - start > 600:
            raise Rejected(f"{label}: bounded timecode must be positive and at most 600 seconds")
        choice(item["kind"], EVIDENCE_KINDS, f"{label}.kind")
        choice(item["epistemic_status"], EPISTEMIC, f"{label}.epistemic_status")
        clean_text(item["original_note"], f"{label}.original_note", max_length=320)
    seen_assertions = set()
    for i, item in enumerate(assertions):
        label = f"assertions[{i}]"
        item = shape(item, {"assertion_id", "subject", "predicate", "object", "evidence_ids"},
                     {"assertion_id", "subject", "predicate", "object", "evidence_ids"}, label)
        aid = identifier(item["assertion_id"], f"{label}.assertion_id")
        if aid in seen_assertions:
            raise Rejected(f"duplicate assertion_id {aid}")
        seen_assertions.add(aid)
        for field in ("subject", "predicate", "object"):
            clean_text(item[field], f"{label}.{field}", max_length=180)
        refs = item["evidence_ids"]
        if not isinstance(refs, list) or not refs or len(refs) > 12:
            raise Rejected(f"{label}.evidence_ids requires one or more bounded references")
        if any(not isinstance(ref, str) or ref not in seen_evidence for ref in refs) or len(refs) != len(set(refs)):
            raise Rejected(f"{label}.evidence_ids contains duplicate or non-local evidence references")
    return data


def canonical(data: dict) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_packet(data: dict) -> dict:
    validate_input(data)
    pid = data["packet_id"]
    inspected = data["source"]["inspection"] == "RESEARCHER_REPORTED"
    packet = {
        "record_type": "episode_review_packet",
        "schema_version": "1.0.0",
        "packet_id": pid,
        "fixture_only": data["fixture_only"],
        "candidate_status": "FIXTURE_ONLY_NOT_ADMISSIBLE" if data["fixture_only"] else "PROPOSED_NOT_ADMITTED",
        "authenticity": ("SYNTHETIC_FIXTURE_NO_CONTENT_INSPECTED" if data["fixture_only"] else
                         "RESEARCHER_REPORT_NOT_INDEPENDENTLY_VERIFIED" if inspected else "NO_EPISODE_CONTENT_INSPECTED"),
        "mission_id": data["mission_id"],
        "work_candidate": {"candidate_ref": f"{pid}:work", **data["episode"], "admission": "NONE"},
        "source_candidate": {"candidate_ref": f"{pid}:source", **data["source"], "digest_verified": False, "rights_verified": False, "admission": "NONE"},
        "binding_candidate": {
            "candidate_ref": f"{pid}:binding", "source_ref": f"{pid}:source", "work_ref": f"{pid}:work",
            "mapping_role_requested": "EVIDENCE_BEARING" if inspected else "METADATA_ONLY",
            "lifecycle": "PROPOSED", "independent_binding_review": "PENDING",
            "accepted_source_work_binding_effect": "NONE",
        },
        "evidence_candidates": [
            {"candidate_ref": f"{pid}:evidence:{obs['evidence_id']}", "source_ref": f"{pid}:source",
             "work_ref": f"{pid}:work", **obs, "admission": "NONE"}
            for obs in data["observations"]
        ],
        "assertion_candidates": [
            {"candidate_ref": f"{pid}:assertion:{a['assertion_id']}", **a,
             "evidence_candidate_refs": [f"{pid}:evidence:{eid}" for eid in a["evidence_ids"]],
             "admission": "NONE"}
            for a in data["assertions"]
        ],
        "coverage_handoff": {"state_for_independent_review": "SOURCE_BOUND" if inspected else "NONE",
                             "ledger_event_emitted": False, "coverage_effect": "NONE", "denominator_effect": "NONE"},
        "projection_handoff": {"approved_projection_hash": None, "projection_emitted": False,
                               "explorer_rebuilt": False, "projection_effect": "NONE"},
        "review_gates": [
            {"role": role, "status": "BLOCKED_FIXTURE_ONLY" if data["fixture_only"] else "PENDING_INDEPENDENT_REVIEW"}
            for role in ("LIBRARIAN", "RIGHTS_AND_SOURCE", "RESEARCH", "AUDITOR", "PROJECTION_MAINTAINER")
        ],
        "review_warning": "No source bytes have been inspected by this tool. A declared digest and lawful-access basis are unverified researcher statements, not accepted evidence or an episode-viewing claim by the repository.",
    }
    packet["packet_sha256"] = hashlib.sha256(canonical(packet)).hexdigest()
    return packet


def template(mission_id: str) -> dict:
    if mission_id not in missions():
        raise Rejected("template Mission ID is not in the Mission catalog")
    return {
        "record_type": "episode_review_input", "schema_version": "1.0.0", "packet_id": "PILOT-REPLACE-ME",
        "fixture_only": False, "mission_id": mission_id,
        "episode": {"title": "Replace with verified publisher episode title", "season": 1,
                    "episode_number": 1, "publisher_roster_url": "https://www.startrek.com/"},
        "source": {"kind": "PUBLISHER_METADATA", "locator": "https://www.startrek.com/",
                   "version": "Replace with publisher page edition / retrieval context",
                   "access_basis": "PUBLISHER_PUBLIC_METADATA", "rights_note": "Public episode listing only; no audiovisual content inspected",
                   "inspection": "NOT_INSPECTED", "inspected_on": None, "content_sha256": None},
        "observations": [], "assertions": [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Private local JSON input; emits proposal-only packet to stdout")
    source.add_argument("--template", metavar="MISSION_ID", help="Print non-inspected researcher input template")
    args = parser.parse_args(argv)
    try:
        result = template(args.template) if args.template else build_packet(read_input(args.input))
    except Rejected as exc:
        print(f"REVIEW_PACKET_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
