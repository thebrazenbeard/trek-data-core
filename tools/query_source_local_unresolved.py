#!/usr/bin/env python3
"""Read-only, fail-closed query of accepted-file *unadmitted* local assertion proposals.

This intentionally has no global entity joining, acceptance, projection promotion,
or coverage accounting. An accepted Git file is not an accepted assertion.
Only the six explicitly reviewed input SHAPES below are eligible; adding a new
research partition requires a separate methodology/code review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "proposals/research/"
INPUTS = (
    (PREFIX + "ds9-paramount-s1-guide-20261103/assertions.json",
     PREFIX + "ds9-paramount-s1-guide-20261103/evidence.json", "ds9_s1"),
    (PREFIX + "ds9-publisher-guide-tail-b006-20261103/assertions.json",
     PREFIX + "ds9-publisher-guide-tail-b006-20261103/observations.json", "ds9_b006"),
    (PREFIX + "ds9-s7-publisher-card-recheck-20261103/assertions.json",
     PREFIX + "ds9-s7-publisher-card-recheck-20261103/observations.json", "ds9_s7"),
    (PREFIX + "ds9-source-custody-gap-20261103/assertions.json",
     PREFIX + "ds9-source-custody-gap-20261103/evidence.json", "ds9_custody"),
    (PREFIX + "tos-charlie-x-derivative-close-read-20261103/assertions.json",
     PREFIX + "tos-charlie-x-derivative-close-read-20261103/evidence.json", "tos_derivative"),
    (PREFIX + "tos-man-trap-derivative-close-read-20261102/assertions.json",
     PREFIX + "tos-man-trap-derivative-close-read-20261102/evidence.json", "tos_derivative"),
)
# Explicit accepted-main byte identity at the first integration gate. These
# proposal files are never authoritative assertions merely because committed.
# Any append/correction requires reviewed updates to this input manifest.
TRUSTED_SHA256 = {
    PREFIX + "ds9-paramount-s1-guide-20261103/assertions.json": "58f5e3b9267b8c75ef1904ba5bce1f93b3a238ae5c698011aa8db215c5ef31b9",
    PREFIX + "ds9-paramount-s1-guide-20261103/evidence.json": "cc521abebd3a814a34d9b3ea8dbfb841059e39099518976305dc42a3865fa91b",
    PREFIX + "ds9-publisher-guide-tail-b006-20261103/assertions.json": "ee32c1a0e7f4e90c245a9740f322615f443e884107b371cc1f975e399cfb030e",
    PREFIX + "ds9-publisher-guide-tail-b006-20261103/observations.json": "12bacfb550e3b52ce8e14c591bcc7e258f59e1544bf28fa010ce249f60c96a08",
    PREFIX + "ds9-s7-publisher-card-recheck-20261103/assertions.json": "7c1adafd3d708965d1d3696436b1c01abc86eda51641db3f60921094a9a1e2ad",
    PREFIX + "ds9-s7-publisher-card-recheck-20261103/observations.json": "0d80e5d76f873de72f3ac3d2b906bad7852eff2e7eb74a65ce196a32acbd152d",
    PREFIX + "ds9-source-custody-gap-20261103/assertions.json": "5cc30cfee25f6c43758f6da6dd782ba362d062f749bf44ae63782b49dbe26174",
    PREFIX + "ds9-source-custody-gap-20261103/evidence.json": "6db08fab4c51adb30fc9a1304d8773aaae8614163a9c96f7563988a43530f4bf",
    PREFIX + "tos-charlie-x-derivative-close-read-20261103/assertions.json": "12676349b2edff2c6e5c7ef2e03f45bbf5e1b337824d1abbce565daa32a4d4ad",
    PREFIX + "tos-charlie-x-derivative-close-read-20261103/evidence.json": "bfe28fe51b32bb83bba5a9d47c596d99e04a69b788495faeb8e4f898b3c08b57",
    PREFIX + "tos-man-trap-derivative-close-read-20261102/assertions.json": "fb823f811d5f8e764594d8f88ca26f64d1071799049d82bab1eab2e2d2b31826",
    PREFIX + "tos-man-trap-derivative-close-read-20261102/evidence.json": "2119e1be463146326c28f854db8867ca7d54bbc8fb750b5cd1933b83b467985a",
}
_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,79}\Z")
_EVIDENCE_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,79}\Z")
_PREDICATE = re.compile(r"[A-Z][A-Z_]{1,119}\Z")
_COMMON_ROW = {"id", "predicate", "status", "counter_evidence_ids", "falsifier"}
_FIELDS = {
    "ds9_s1": (_COMMON_ROW | {"subject", "object", "evidence_ids", "truth_scope"}, {"falsifier"}),
    "ds9_b006": (_COMMON_ROW | {"subject_source_local_row_id", "statement", "evidence_ids"}, set()),
    "ds9_s7": (_COMMON_ROW | {"subject", "statement", "evidence_ids"}, set()),
    "ds9_custody": (_COMMON_ROW | {"subject", "object", "evidence_ids"}, set()),
    "tos_derivative": (_COMMON_ROW | {"subject_type", "subject", "object", "evidence", "context_evidence_ids",
                                   "counter_evidence_search", "proposed_projection_status", "scope"}, set()),
}
_ENVELOPES = {
    "ds9_s1": {"record_type", "source_local_id", "assertions", "admitted_assertions", "projection_effect"},
    "ds9_b006": {"schema_version", "batch_id", "proposal_only", "accepted_assertions", "projection_effect", "assertions"},
    "ds9_s7": {"schema_version", "batch_id", "proposal_only", "accepted_assertions", "projection_effect", "assertions"},
    "ds9_custody": {"record_type", "batch_id", "assertions", "accepted_assertions", "projection_effect"},
    "tos_derivative": {"record_type", "source_local_id", "work_local_id", "assertions", "accepted_assertions", "projection_effect"},
}
_RECORD_TYPES = {
    "ds9_s1": "PROPOSED_SOURCE_RELATIVE_ASSERTIONS",
    "ds9_custody": "PROPOSED_SOURCE_ROUTE_ASSERTIONS_NOT_FICTIONAL_FACTS",
    "tos_derivative": "PROPOSED_SOURCE_RELATIVE_ASSERTIONS",
}


def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_json_constant(value: str) -> None:
    raise ValueError(f"Nonstandard JSON constant rejected: {value}")


def _read(root: Path, relative: str) -> tuple[dict, str]:
    # Reject static symlink aliases for every ancestor, not just the leaf.
    path = root
    for component in Path(relative).parts:
        path = path / component
        if path.is_symlink():
            raise ValueError(f"Symlinked proposal input: {relative}")
    if not path.is_file() or path.stat().st_size > 250_000:
        raise ValueError(f"Missing, special, or oversized proposal input: {relative}")
    content = path.read_bytes()
    try:
        parsed = json.loads(content.decode("utf-8"), object_pairs_hook=_no_duplicate_keys,
                            parse_constant=_invalid_json_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid proposal JSON: {relative}") from exc
    if type(parsed) is not dict:
        raise ValueError(f"Proposal input is not an object: {relative}")
    return parsed, hashlib.sha256(content).hexdigest()


def _text(value: object, name: str, maximum: int = 2000) -> str:
    if type(value) is not str or not value.strip() or len(value) > maximum or \
       any(ord(ch) < 32 and ch not in "\n\t" for ch in value):
        raise ValueError(f"Invalid bounded {name}")
    return value


def _refs(value: object, field: str, evidence_ids: set[str], required: bool = False) -> list[str]:
    if type(value) is not list or (required and not value) or len(value) > 40 or \
       any(type(item) is not str or not _EVIDENCE_ID.fullmatch(item) for item in value) or \
       len(value) != len(set(value)) or not set(value).issubset(evidence_ids):
        raise ValueError(f"Invalid or unbound {field} references")
    return value


def _evidence_ids(data: dict, shape: str) -> set[str]:
    field = "source_local_cards" if shape == "ds9_b006" else "records" if shape == "ds9_s7" else "evidence"
    id_field = "evidence_id" if shape == "ds9_b006" else "observation_id" if shape == "ds9_s7" else "id"
    records = data.get(field)
    if type(records) is not list or not records or len(records) > 100:
        raise ValueError("Missing bounded source-local evidence records")
    ids = []
    for record in records:
        if type(record) is not dict or type(record.get(id_field)) is not str or \
           not _EVIDENCE_ID.fullmatch(record[id_field]):
            raise ValueError("Evidence record lacks an explicit source-local ID")
        ids.append(record[id_field])
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate source-local evidence IDs")
    return set(ids)


def _assertions(data: dict, evidence: dict, shape: str, path: str) -> tuple[list[dict], int]:
    if set(data) != _ENVELOPES[shape] or data["projection_effect"] != "NONE" or \
       type(data["assertions"]) is not list or not data["assertions"] or len(data["assertions"]) > 100:
        raise ValueError(f"Unclosed or promoting assertion envelope: {path}")
    if shape in _RECORD_TYPES and data["record_type"] != _RECORD_TYPES[shape]:
        raise ValueError(f"Unexpected assertion record type: {path}")
    if shape in {"ds9_b006", "ds9_s7"} and (data["schema_version"] != "1.0.0" or data["proposal_only"] is not True):
        raise ValueError(f"Not a versioned proposal-only envelope: {path}")
    if shape != "ds9_s1" and (type(data["accepted_assertions"]) is not int or data["accepted_assertions"] != 0):
        raise ValueError(f"Accepted assertions falsely claimed: {path}")
    if shape == "ds9_s1" and (type(data["admitted_assertions"]) is not int or data["admitted_assertions"] != 0):
        raise ValueError(f"Admitted assertions falsely claimed: {path}")
    batch = Path(path).parent.name
    if "batch_id" in data and data["batch_id"] != batch:
        raise ValueError(f"Cross-batch assertion envelope: {path}")
    if "source_local_id" in data and data["source_local_id"] != evidence.get("source_local_id"):
        raise ValueError(f"Cross-source evidence envelope: {path}")
    if "work_local_id" in data and data["work_local_id"] != evidence.get("work_local_id"):
        raise ValueError(f"Cross-work local evidence envelope: {path}")
    if "batch_id" in evidence and evidence["batch_id"] != batch:
        raise ValueError(f"Cross-batch evidence records: {path}")
    known_evidence = _evidence_ids(evidence, shape)
    seen = set()
    unresolved = []
    expected, optional = _FIELDS[shape]
    for item in data["assertions"]:
        if type(item) is not dict or set(item) - expected or not (expected - optional).issubset(item):
            raise ValueError(f"Unclosed assertion row: {path}")
        assertion_id = item["id"]
        if type(assertion_id) is not str or not _ID.fullmatch(assertion_id) or assertion_id in seen or \
           type(item["predicate"]) is not str or not _PREDICATE.fullmatch(item["predicate"]):
            raise ValueError(f"Invalid or repeated source-local assertion ID/predicate: {path}")
        seen.add(assertion_id)
        if item["status"] not in {"PROPOSED", "PROPOSED_UNRESOLVED"}:
            raise ValueError(f"An unadmitted source asserted an unsupported status: {path}")
        if shape == "tos_derivative" and (item["status"] != "PROPOSED" or
             item["proposed_projection_status"] not in {"UNRESOLVED", "CONTESTED"}):
            raise ValueError(f"Non-proposed derivative classification: {path}")
        ids_key = "evidence" if shape == "tos_derivative" else "evidence_ids"
        evidence_ids = _refs(item[ids_key], ids_key, known_evidence, required=True)
        counter = _refs(item["counter_evidence_ids"], "counter_evidence_ids", known_evidence)
        if shape == "tos_derivative":
            _refs(item["context_evidence_ids"], "context_evidence_ids", known_evidence)
            if item["subject_type"] not in {"LOCAL_ENTITY", "WORK"} or type(item["scope"]) is not dict or \
               set(item["scope"]) != {"truth_level", "edition"} or item["scope"]["edition"] != "TVMEG_DERIVATIVE_TEXT":
                raise ValueError(f"Invalid derivative source-relative scope: {path}")
            scope = _text(item["scope"]["truth_level"], "truth level", 150)
            _text(item["counter_evidence_search"], "counterevidence search")
            kind = "PROPOSED_PROJECTED_" + item["proposed_projection_status"]
        else:
            scope = _text(item.get("truth_scope", evidence.get("source_scope", evidence.get("read_scope", "SOURCE_LOCAL_PROPOSAL"))), "source scope", 150)
            kind = "PROPOSED_UNRESOLVED" if item["status"] == "PROPOSED_UNRESOLVED" else None
        subject = _text(item.get("subject", item.get("subject_source_local_row_id")), "source-local subject", 200)
        if not re.fullmatch(r"[a-z0-9][a-z0-9:_.-]{0,199}", subject) or subject.startswith(("global:", "canonical:")):
            raise ValueError("Assertion subject must be an unambiguous local reference")
        if shape == "ds9_b006" and not re.fullmatch(r"lead:[0-9]{4}", subject):
            raise ValueError("The DS9 B006 row must remain an explicit source-local lead ID")
        if shape == "tos_derivative" and item["subject_type"] == "WORK" and subject != data["work_local_id"]:
            raise ValueError("Derivative Work assertion must use its own local candidate reference")
        statement = _text(item.get("statement", item.get("object")), "source-relative statement")
        falsifier = _text(item["falsifier"], "explicit falsifier") if "falsifier" in item else None
        if kind and not falsifier:
            raise ValueError(f"Unresolved claim lacks a falsifier: {path}")
        if kind:
            unresolved.append({
                "source_key": f"{path}:{assertion_id}", "batch": batch,
                "source_path": path, "assertion_id": assertion_id,
                "predicate": item["predicate"], "subject_local_reference": subject,
                "source_scope": scope, "kind": kind, "truth_status": "PROPOSED_NOT_ADMITTED",
                "statement": statement, "evidence_ids": evidence_ids,
                "counter_evidence_ids": counter, "falsifier": falsifier,
            })
    return unresolved, len(seen)


def _compile(root: Path, enforce_pins: bool) -> dict:
    rows, digests = [], []
    total_proposals = 0
    if set(TRUSTED_SHA256) != {path for source, evidence, _ in INPUTS for path in (source, evidence)}:
        raise ValueError("Trusted proposal-source manifest and explicit source paths disagree")
    for source_path, evidence_path, shape in INPUTS:
        data, source_sha = _read(root, source_path)
        evidence, evidence_sha = _read(root, evidence_path)
        if enforce_pins and (TRUSTED_SHA256[source_path] != source_sha or
                             TRUSTED_SHA256[evidence_path] != evidence_sha):
            raise ValueError(f"Source/evidence bytes drifted from accepted review pins: {source_path}")
        projected, total = _assertions(data, evidence, shape, source_path)
        rows.extend(projected)
        total_proposals += total
        digests.extend([{"path": source_path, "sha256": source_sha},
                        {"path": evidence_path, "sha256": evidence_sha}])
    rows.sort(key=lambda row: row["source_key"])
    return {
        "schema_version": "1.0.0", "data_status": "ACCEPTED_FILES_WITH_UNADMITTED_PROPOSALS_ONLY",
        "admission_effect": "NONE", "coverage_effect": "NONE", "identity_resolution_effect": "NONE",
        "denominator_status": "NO_SOURCE_WORK_COVERAGE_DENOMINATOR",
        "source_file_count": len(INPUTS), "total_proposal_assertions_observed": total_proposals,
        "unresolved_proposal_count": len(rows),
        "plain_proposals_not_in_unresolved_report": total_proposals - len(rows),
        "kind_counts": dict(sorted(Counter(row["kind"] for row in rows).items())),
        "source_sha256": sorted(digests, key=lambda receipt: receipt["path"]),
        "rows": rows,
    }


def build(root: Path = ROOT) -> dict:
    """Only pinned accepted-main source bytes can enter the public CLI report."""
    return _compile(root, enforce_pins=True)


def query(report: dict, *, kind: str | None = None, batch: str | None = None,
          predicate: str | None = None, text: str | None = None, limit: int = 25, offset: int = 0) -> dict:
    if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or offset < 0:
        raise ValueError("Query limit must be 1..100 and offset nonnegative")
    terms = (text or "").casefold().split()
    matched = [row for row in report["rows"] if
               (not kind or row["kind"] == kind) and (not batch or row["batch"] == batch) and
               (not predicate or row["predicate"] == predicate) and
               all(term in " ".join((row["statement"], row["falsifier"], row["predicate"],
                                     row["subject_local_reference"])).casefold() for term in terms)]
    visible = matched[offset:offset + limit]
    return {"schema_version": report["schema_version"], "data_status": report["data_status"],
            "admission_effect": "NONE", "coverage_effect": "NONE", "identity_resolution_effect": "NONE",
            "total_matches": len(matched), "offset": offset, "limit": limit,
            "next_offset": offset + len(visible) if offset + len(visible) < len(matched) else None,
            "rows": visible}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", help="Exact proposed unresolved class")
    parser.add_argument("--batch", help="Exact source-local research batch")
    parser.add_argument("--predicate", help="Exact asserted predicate; not canon")
    parser.add_argument("--q", help="Case-insensitive text retrieval from proposed statements")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()
    try:
        output = query(build(), kind=args.kind, batch=args.batch, predicate=args.predicate,
                       text=args.q, limit=args.limit, offset=args.offset)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
