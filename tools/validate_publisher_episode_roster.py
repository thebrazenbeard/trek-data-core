#!/usr/bin/env python3
"""Validate an offline, *unadmitted* publisher episode-slot observation.

This verifies only proposal shape and internal consistency, not the truth,
completeness, currency or legal availability of a publisher's page. No network,
canonical registry, coverage ledger or projection mutations are performed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "registry" / "mission_catalog.json"
MAX_INPUT_BYTES = 256 * 1024
QID = re.compile(r"Q[1-9][0-9]{0,15}\Z")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,120}\Z")


class Rejected(ValueError):
    """A proposal violates the bounded candidate-only roster contract."""


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Rejected(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path):
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_NONBLOCK"):
        raise Rejected("safe no-follow/nonblocking input flags are unavailable")
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise Rejected("input must be a regular non-symlink file")
    if before.st_size > MAX_INPUT_BYTES:
        raise Rejected("input exceeds 256 KiB")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if (not stat.S_ISREG(opened.st_mode) or opened.st_dev != before.st_dev
                or opened.st_ino != before.st_ino):
            raise Rejected("input file changed during safe open")
        if opened.st_size > MAX_INPUT_BYTES:
            raise Rejected("input exceeds 256 KiB")
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise Rejected("input exceeds 256 KiB")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Rejected(f"invalid UTF-8 JSON: {exc}") from exc


def keys(obj, expected, name):
    if not isinstance(obj, dict) or set(obj) != set(expected):
        raise Rejected(f"{name} has unexpected/missing keys")
    return obj


def text(value, name, limit=160):
    if (not isinstance(value, str) or not value or value != value.strip()
            or len(value) > limit or any(ord(c) < 32 or ord(c) in (127, 0x2028, 0x2029) for c in value)
            or "<" in value or ">" in value):
        raise Rejected(f"{name} must be bounded, single-line and printable")
    return value


def safe_locator(value, name):
    value = text(value, name, 500)
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise Rejected(f"{name} has malformed HTTPS URL syntax") from exc
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or not parsed.path.startswith("/")
            or port not in (None, 443)):
        raise Rejected(f"{name} must be an HTTPS page locator without tokens")
    host = parsed.hostname.lower()
    if (host == "localhost" or host.endswith(".localhost") or host.endswith(".local")
            or host.replace(".", "").isdigit() or "." not in host):
        raise Rejected(f"{name} has a nonpublic host")
    return value


def validate(data, mission_catalog):
    keys(data, {"record_type", "schema_version", "batch_id", "mission_id", "proposal_status",
                "accepted_work_effect", "accepted_source_binding_effect", "coverage_effect",
                "denominator_effect", "roster_completeness", "listed_slot_count", "observation",
                "series_qid_redirect", "episode_slots"}, "roster")
    if data["record_type"] != "publisher_episode_roster_proposal" or data["schema_version"] != "1.0.0":
        raise Rejected("unsupported roster record/schema")
    if not IDENTIFIER.fullmatch(text(data["batch_id"], "batch_id", 120)):
        raise Rejected("invalid batch ID")
    keys(mission_catalog, {"catalog_version", "authority", "admission_status", "missions"}, "Mission catalog")
    missions = {row["id"] for row in mission_catalog["missions"] if isinstance(row, dict) and isinstance(row.get("id"), str)}
    if not isinstance(data["mission_id"], str) or data["mission_id"] not in missions:
        raise Rejected("roster Mission is absent from current catalog")
    if data["proposal_status"] != "CANDIDATE_METADATA_ONLY" or data["roster_completeness"] != "UNRESOLVED":
        raise Rejected("roster must remain candidate-only and completeness unresolved")
    for key in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
        if data[key] != "NONE":
            raise Rejected(f"roster cannot change accepted state: {key}")

    observation = keys(data["observation"], {"publisher", "independence_group", "observed_on",
                  "primary_locator", "crosscheck_locator", "scope", "response_sha256",
                  "publisher_revision", "audiovisual_content_inspected"}, "observation")
    text(observation["publisher"], "publisher", 100)
    text(observation["independence_group"], "independence group", 100)
    observed_on = text(observation["observed_on"], "observed date", 10)
    try:
        observed_date = date.fromisoformat(observed_on)
    except ValueError as exc:
        raise Rejected("observed_on must be ISO calendar date") from exc
    if observed_date.isoformat() != observed_on:
        raise Rejected("observed_on must be canonical YYYY-MM-DD date")
    if observed_date > date.today():
        raise Rejected("observed_on cannot be in the future")
    safe_locator(observation["primary_locator"], "primary locator")
    safe_locator(observation["crosscheck_locator"], "crosscheck locator")
    if observation["scope"] != "PUBLISHER_PAGE_TITLE_AND_SEASON_EPISODE_SLOT_ONLY":
        raise Rejected("publisher roster has unsupported observation scope")
    if (observation["response_sha256"] is not None or observation["publisher_revision"] is not None
            or observation["audiovisual_content_inspected"] is not False):
        raise Rejected("metadata observation must not claim response or audiovisual verification")

    if data["series_qid_redirect"] is not None:
        redirect = keys(data["series_qid_redirect"], {"system", "requested_qid", "displayed_qid",
                        "locator", "verification_status"}, "series QID redirect")
        if (redirect["system"] != "Wikidata" or redirect["verification_status"] != "PAGE_REDIRECT_OBSERVATION_ONLY"
                or not isinstance(redirect["requested_qid"], str) or not QID.fullmatch(redirect["requested_qid"])
                or not isinstance(redirect["displayed_qid"], str) or not QID.fullmatch(redirect["displayed_qid"])
                or redirect["requested_qid"] == redirect["displayed_qid"]):
            raise Rejected("invalid candidate-only Wikidata redirect observation")
        safe_locator(redirect["locator"], "Wikidata redirect locator")
        if redirect["locator"] != "https://www.wikidata.org/wiki/" + redirect["requested_qid"]:
            raise Rejected("Wikidata redirect locator must identify the requested QID")

    rows = data["episode_slots"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 500 or type(data["listed_slot_count"]) is not int or data["listed_slot_count"] != len(rows):
        raise Rejected("listed slot count must equal a bounded nonempty episode list")
    previous = (0, 0)
    seen_titles = set()
    for index, row in enumerate(rows):
        keys(row, {"season", "episode_number", "title", "status", "canonical_work_id", "source_binding_id"},
             f"episode_slots[{index}]")
        season, episode = row["season"], row["episode_number"]
        if (type(season) is not int or not 1 <= season <= 999 or type(episode) is not int
                or not 1 <= episode <= 9999 or (season, episode) <= previous):
            raise Rejected("episode slots must be unique, positive and strictly sorted")
        title = text(row["title"], f"episode_slots[{index}].title").casefold()
        if title in seen_titles:
            raise Rejected("duplicate publisher title requires explicit identity review")
        seen_titles.add(title)
        if row["status"] != "CANDIDATE" or row["canonical_work_id"] is not None or row["source_binding_id"] is not None:
            raise Rejected("publisher metadata cannot create Work IDs or source bindings")
        previous = (season, episode)
    return {"mission_id": data["mission_id"], "listed_slots": len(rows),
            "roster_completeness": "UNRESOLVED", "accepted_effect": "NONE"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = validate(read_json(args.input), read_json(CATALOG))
    except (Rejected, OSError) as exc:
        print(f"PUBLISHER_ROSTER_REJECTED: {exc}", file=sys.stderr)
        return 1
    print("PUBLISHER_ROSTER_CANDIDATE: " + json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
