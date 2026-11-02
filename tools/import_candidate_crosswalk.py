#!/usr/bin/env python3
"""Offline, candidate-only Wikidata crosswalk proposal normalization.

This tool does not query Wikidata, establish canon, or accept registry records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


MAX_INPUT_BYTES = 8 * 1024 * 1024
MAX_CANDIDATES = 10000
LICENSE_URL = "https://www.wikidata.org/wiki/Wikidata:Licensing"
QID_PATTERN = re.compile(r"Q[1-9][0-9]{0,19}\Z")
HEAD_PATTERN = re.compile(r"[0-9a-f]{40}\Z")


class AdmissionError(ValueError):
    """An input cannot be safely represented as candidate-only crosswalks."""


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AdmissionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json(path: Path):
    data = path.read_bytes()
    if len(data) > MAX_INPUT_BYTES:
        raise AdmissionError(f"input too large: {path}")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs), hashlib.sha256(data).hexdigest()
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdmissionError(f"invalid UTF-8 JSON in {path}: {exc}") from exc


def _object(value, name, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise AdmissionError(f"{name} must contain exactly: {', '.join(sorted(keys))}")
    return value


def _nonempty(value, name):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise AdmissionError(f"{name} must be a nonempty, trimmed string")
    if any(ord(char) < 32 for char in value):
        raise AdmissionError(f"{name} contains control characters")
    return value


def _wikidata_url(value, name):
    url = urlsplit(_nonempty(value, name))
    try:
        invalid_port = bool(url.port)
    except ValueError as exc:
        raise AdmissionError(f"{name} has an invalid port") from exc
    if (url.scheme != "https" or url.hostname not in ("www.wikidata.org", "query.wikidata.org")
            or url.username or url.password or invalid_port or url.fragment):
        raise AdmissionError(f"{name} must be an HTTPS Wikidata source URL")
    return value


def _utc_timestamp(value):
    value = _nonempty(value, "source.retrieved_at")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
        raise AdmissionError("source.retrieved_at must use UTC YYYY-MM-DDTHH:MM:SSZ")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AdmissionError("source.retrieved_at is not a valid timestamp") from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise AdmissionError("source.retrieved_at must be UTC")
    return value


def _registry_targets(registry):
    if not isinstance(registry, dict) or not isinstance(registry.get("sources"), list) or not isinstance(registry.get("works"), list):
        raise AdmissionError("registry must contain sources and works arrays")
    result = {}
    for kind, key, rows in (("SOURCE", "source_id", registry["sources"]), ("WORK", "work_id", registry["works"])):
        for row in rows:
            if not isinstance(row, dict):
                raise AdmissionError("registry rows must be objects")
            identity = row.get(key)
            if not isinstance(identity, str) or not identity:
                raise AdmissionError(f"registry {kind} row missing {key}")
            if (kind, identity) in result:
                raise AdmissionError(f"duplicate registry {kind} ID: {identity}")
            # A fixture ACCEPTED state is not accepted corpus authority.
            if row.get("record_type") != kind.lower():
                raise AdmissionError(f"registry {kind} row has wrong record_type")
            result[(kind, identity)] = row.get("status") == "ACCEPTED" and row.get("fixture_only") is False
    return result


def build_proposal(export, registry, registry_ref, export_hash, registry_hash):
    """Return a deterministic proposal receipt; never alter source inputs."""
    if not isinstance(registry_ref, str) or not HEAD_PATTERN.fullmatch(registry_ref):
        raise AdmissionError("registry-ref must be a complete lowercase 40-character Git commit SHA")
    _object(export, "export", {"source", "candidates"})
    source = _object(export["source"], "source", {
        "system", "url", "license", "license_url", "retrieved_at", "snapshot"
    })
    if source["system"] != "Wikidata":
        raise AdmissionError("only Wikidata structured-data exports are supported")
    _wikidata_url(source["url"], "source.url")
    if source["license"] != "CC0-1.0" or source["license_url"] != LICENSE_URL:
        raise AdmissionError("source must explicitly identify Wikidata structured data under CC0-1.0")
    _utc_timestamp(source["retrieved_at"])
    _nonempty(source["snapshot"], "source.snapshot")
    candidates = export["candidates"]
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= MAX_CANDIDATES:
        raise AdmissionError(f"candidates must be an array of 1 to {MAX_CANDIDATES} records")
    allowed_targets = _registry_targets(registry)
    seen_qid = set()
    seen_target = set()
    normalized = []
    for i, item in enumerate(candidates):
        row = _object(item, f"candidates[{i}]", {"external_id", "target_kind", "target_id", "mapping_basis"})
        qid = _nonempty(row["external_id"], f"candidates[{i}].external_id")
        if not QID_PATTERN.fullmatch(qid):
            raise AdmissionError(f"candidates[{i}].external_id must be a Wikidata QID")
        kind = row["target_kind"]
        if kind not in ("SOURCE", "WORK"):
            raise AdmissionError(f"candidates[{i}].target_kind must be SOURCE or WORK")
        target_id = _nonempty(row["target_id"], f"candidates[{i}].target_id")
        basis = _nonempty(row["mapping_basis"], f"candidates[{i}].mapping_basis")
        if not allowed_targets.get((kind, target_id), False):
            raise AdmissionError(f"candidate target is not an accepted, non-fixture {kind}: {target_id}")
        if qid in seen_qid or (kind, target_id) in seen_target:
            raise AdmissionError("ambiguous or duplicate candidate mapping requires manual adjudication")
        seen_qid.add(qid)
        seen_target.add((kind, target_id))
        digest = hashlib.sha256(f"Wikidata\0{qid}\0{kind}\0{target_id}".encode("utf-8")).hexdigest()[:24]
        normalized.append({
            "record_type": "external_crosswalk",
            "crosswalk_id": f"XCAND-WIKIDATA-{digest}",
            "target_kind": kind,
            "target_id": target_id,
            "external_system": "Wikidata",
            "external_id": qid,
            "snapshot": source["snapshot"],
            "retrieved_at": source["retrieved_at"],
            "mapping_status": "CANDIDATE",
            "independence_group": "WIKIDATA_STRUCTURED_DATA",
            "lineage_note": f"Discovery metadata only; Wikidata CC0-1.0; no narrative corroboration. Candidate basis: {basis}",
            "fixture_only": False,
        })
    normalized.sort(key=lambda x: (x["target_kind"], x["target_id"], x["external_id"]))
    return {
        "proposal_type": "EXTERNAL_CROSSWALK_CANDIDATES_V1",
        "proposal_only": True,
        "accepted_corpus_effect": "NONE",
        "source_provenance": {
            "external_system": source["system"],
            "source_url": source["url"],
            "license": source["license"],
            "license_url": source["license_url"],
            "snapshot": source["snapshot"],
            "retrieved_at": source["retrieved_at"],
            "input_sha256": export_hash,
            "lineage_warning": "Wikidata is a discovery crosswalk, not an independent Star Trek narrative witness",
        },
        "target_catalog": {
            "claimed_git_head": registry_ref,
            "input_sha256": registry_hash,
            "verification": "LOCAL_INPUT_ONLY_NOT_GITHUB_VERIFIED",
        },
        "records": normalized,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="User-supplied offline JSON export")
    parser.add_argument("--registry", type=Path, required=True, help="Offline Source/Work catalog; must contain non-fixture accepted IDs")
    parser.add_argument("--registry-ref", required=True, help="Claimed complete Git HEAD of catalog (not verified over network)")
    parser.add_argument("--output", type=Path, required=True, help="New candidate-only proposal JSON; never overwrites")
    args = parser.parse_args(argv)
    try:
        export, export_hash = _read_json(args.input)
        registry, registry_hash = _read_json(args.registry)
        result = build_proposal(export, registry, args.registry_ref, export_hash, registry_hash)
        encoded = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
    except (AdmissionError, OSError) as exc:
        print(f"CANDIDATE_IMPORT_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(f"CANDIDATE_IMPORT_OK: {len(result['records'])} unaccepted crosswalk proposals -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
