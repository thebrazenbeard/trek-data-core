#!/usr/bin/env python3
"""Normalize an OFFLINE Wikidata SPARQL JSON response to episode discovery proposals.

No network access, canonical Work creation, registry mutation, or corpus admission.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


QID = re.compile(r"Q[1-9][0-9]{0,19}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
ENTITY = re.compile(r"https?://www\.wikidata\.org/entity/(Q[1-9][0-9]{0,19})\Z")
SOURCE_URL = "https://query.wikidata.org/sparql"
LICENSE_URL = "https://www.wikidata.org/wiki/Wikidata:Licensing"
MAX_BYTES = 8 * 1024 * 1024
MAX_ROWS = 10000
OPTIONAL = {"seriesLabel", "seasonNumber", "episodeNumber"}
REQUIRED = {"episode", "episodeLabel", "series"}


class Rejected(ValueError):
    """Input violates the fail-closed proposal admission contract."""


def unique_pairs(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise Rejected(f"duplicate JSON key: {key}")
        data[key] = value
    return data


def load_json(path):
    raw = Path(path).read_bytes()
    if len(raw) > MAX_BYTES:
        raise Rejected("input exceeds 8 MiB limit")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs), hashlib.sha256(raw).hexdigest()
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Rejected(f"not valid UTF-8 JSON: {exc}") from exc


def object_keys(value, keys, name, optional=frozenset()):
    if not isinstance(value, dict) or not set(keys) <= set(value) or set(value) - (set(keys) | set(optional)):
        raise Rejected(f"{name} has invalid or missing fields")
    return value


def clean_text(value, name, max_length=400, multiline=False):
    if (not isinstance(value, str) or not value or value != value.strip()
            or len(value) > max_length or any(
                ord(ch) < 32 and (not multiline or ch not in "\r\n\t") for ch in value)):
        raise Rejected(f"{name} must be a trimmed, nonempty printable string (max {max_length})")
    return value


def parse_entity(cell, name):
    object_keys(cell, {"type", "value"}, name)
    if cell["type"] != "uri" or not isinstance(cell["value"], str):
        raise Rejected(f"{name} must be a URI binding")
    match = ENTITY.fullmatch(cell["value"])
    if not match or not QID.fullmatch(match.group(1)):
        raise Rejected(f"{name} must be a Wikidata entity QID URI")
    return match.group(1)


def parse_label(cell, name):
    object_keys(cell, {"type", "value"}, name, {"xml:lang"})
    if cell["type"] != "literal" or cell.get("xml:lang") != "en":
        raise Rejected(f"{name} must be an English-language literal")
    return clean_text(cell["value"], name)


def parse_number(cell, name):
    object_keys(cell, {"type", "value"}, name, {"datatype"})
    if cell["type"] != "literal" or not isinstance(cell["value"], str) or not re.fullmatch(r"[1-9][0-9]{0,3}", cell["value"]):
        raise Rejected(f"{name} must be a positive integer literal from 1 to 9999")
    if "datatype" in cell and cell["datatype"] not in (
        "http://www.w3.org/2001/XMLSchema#integer",
        "http://www.w3.org/2001/XMLSchema#decimal",
    ):
        raise Rejected(f"{name} has an unsupported datatype")
    return int(cell["value"])


def parse_receipt(receipt):
    object_keys(receipt, {
        "source_url", "license", "license_url", "retrieved_at_epoch", "snapshot_id", "query_text"
    }, "provenance receipt")
    if receipt["source_url"] != SOURCE_URL or receipt["license"] != "CC0-1.0" or receipt["license_url"] != LICENSE_URL:
        raise Rejected("only explicit Wikidata Query Service CC0-1.0 provenance is accepted")
    epoch = receipt["retrieved_at_epoch"]
    if type(epoch) is not int or not 946684800 <= epoch <= 4102444800:
        raise Rejected("retrieved_at_epoch must be an integer Unix epoch between 2000 and 2100")
    clean_text(receipt["snapshot_id"], "snapshot_id", 200)
    query = clean_text(receipt["query_text"], "query_text", 20000, multiline=True)
    if not re.search(r"\bSELECT\b", query, flags=re.IGNORECASE):
        raise Rejected("query_text must identify a SELECT query")
    return {
        "source_url": SOURCE_URL,
        "license": "CC0-1.0",
        "license_url": LICENSE_URL,
        "retrieved_at_epoch": epoch,
        "snapshot_id": receipt["snapshot_id"],
        "query_sha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
        "provenance_verification": "USER_SUPPLIED_OFFLINE_EXPORT_NOT_REMOTE_VERIFIED",
    }


def build_proposal(sparql, receipt, input_sha256):
    source = parse_receipt(receipt)
    if not HEX64.fullmatch(input_sha256):
        raise Rejected("input SHA-256 must be lowercase 64-character hex")
    object_keys(sparql, {"head", "results"}, "SPARQL response")
    head = object_keys(sparql["head"], {"vars"}, "SPARQL head")
    if not isinstance(head["vars"], list) or not all(isinstance(v, str) for v in head["vars"]):
        raise Rejected("SPARQL head vars must be strings")
    if not REQUIRED <= set(head["vars"]) or set(head["vars"]) - (REQUIRED | OPTIONAL):
        raise Rejected("SPARQL head has missing or unrecognized variables")
    if len(head["vars"]) != len(set(head["vars"])):
        raise Rejected("SPARQL head has duplicate variables")
    object_keys(sparql["results"], {"bindings"}, "SPARQL results")
    rows = sparql["results"]["bindings"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_ROWS:
        raise Rejected(f"SPARQL results require 1 to {MAX_ROWS} rows")
    candidates = []
    seen_episodes = set()
    for index, binding in enumerate(rows):
        object_keys(binding, REQUIRED, f"binding[{index}]", OPTIONAL)
        if set(binding) - set(head["vars"]):
            raise Rejected(f"binding[{index}] contains variables absent from SPARQL head")
        episode_qid = parse_entity(binding["episode"], f"binding[{index}].episode")
        if episode_qid in seen_episodes:
            raise Rejected(f"duplicate episode QID: {episode_qid}")
        seen_episodes.add(episode_qid)
        item = {
            "record_type": "episode_discovery_candidate",
            "status": "CANDIDATE",
            "episode_qid": episode_qid,
            "episode_label": parse_label(binding["episodeLabel"], f"binding[{index}].episodeLabel"),
            "series_qid": parse_entity(binding["series"], f"binding[{index}].series"),
            "series_label": None,
            "season_number": None,
            "episode_number": None,
            "canonical_work_id": None,
            "evidence_status": "EXTERNAL_DISCOVERY_METADATA_ONLY",
        }
        if "seriesLabel" in binding:
            item["series_label"] = parse_label(binding["seriesLabel"], f"binding[{index}].seriesLabel")
        for variable, field in (("seasonNumber", "season_number"), ("episodeNumber", "episode_number")):
            if variable in binding:
                item[field] = parse_number(binding[variable], f"binding[{index}].{variable}")
        candidates.append(item)
    candidates.sort(key=lambda item: int(item["episode_qid"][1:]))
    source["response_sha256"] = input_sha256
    return {
        "proposal_type": "WIKIDATA_EPISODE_DISCOVERY_V1",
        "proposal_only": True,
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "provenance": source,
        "candidates": candidates,
    }


def validate_output_path(value, root):
    output = Path(value)
    if output.is_absolute() or ".." in output.parts or len(output.parts) < 2 or output.parts[0] != "proposals":
        raise Rejected("output must be a relative path under proposals/")
    allowed = (Path(root) / "proposals").resolve()
    resolved = (Path(root) / output).resolve()
    if not resolved.is_relative_to(allowed):
        raise Rejected("output resolves outside proposals/")
    return Path(root) / output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Existing offline WDQS SPARQL results JSON")
    parser.add_argument("--receipt", required=True, help="Offline user-supplied source/license/query receipt JSON")
    parser.add_argument("--output", required=True, help="New relative proposals/... JSON path")
    args = parser.parse_args(argv)
    try:
        response, digest = load_json(args.input)
        receipt, _ = load_json(args.receipt)
        proposal = build_proposal(response, receipt, digest)
        destination = validate_output_path(args.output, Path.cwd())
        encoded = json.dumps(proposal, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        with destination.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
    except (Rejected, OSError) as exc:
        print(f"EPISODE_DISCOVERY_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(f"EPISODE_DISCOVERY_CANDIDATES: {len(proposal['candidates'])} -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
