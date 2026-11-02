#!/usr/bin/env python3
"""Build an isolated, unverified episode discovery index from reviewed proposals.

This is *not* the canonical Explorer index. It cannot admit Works, Evidence,
Mission Briefings, continuity assertions, or coverage. The ten reviewed input
snapshots are explicitly enumerated and the output is deliberately separate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path


MISSION_ORDER = (
    "tos", "tas", "tng", "ds9", "voy", "ent",
    "dis", "pic", "ld", "pro", "snw", "sfa",
)
EXPECTED_SOURCE_URL = "https://query.wikidata.org/sparql"
EXPECTED_LICENSE_URL = "https://www.wikidata.org/wiki/Wikidata:Licensing"
PROVENANCE_STATUS = "USER_SUPPLIED_OFFLINE_EXPORT_NOT_REMOTE_VERIFIED"
QID_PATTERN = re.compile(r"Q[1-9][0-9]{0,15}\Z")
DIGEST_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
SNAPSHOT_PATTERN = re.compile(r"[A-Za-z0-9_-]{3,100}\Z")

# Explicit allowlist: group, query stem, proposal stem, series QID, Mission ID,
# and maximum archived rows (NOT full-series episode denominators).
SOURCE_BATCHES = (
    ("classic", "tos", "tos-qids", "Q1077", "tos", 20),
    ("classic", "tas", "tas-qids", "Q20922", "tas", 20),
    ("tng", "tng", "candidates", "Q16290", "tng", 10),
    ("classic", "ds9", "ds9-qids", "Q108774", "ds9", 20),
    ("modern", "voy", "voy", "Q156329", "voy", 20),
    ("modern", "dis", "dis", "Q21296543", "dis", 20),
    ("modern", "pic", "pic", "Q62573305", "pic", 20),
    ("nextgen", "ld", "ld", "Q62573569", "ld", 20),
    ("nextgen", "pro", "pro", "Q65250765", "pro", 20),
    ("nextgen", "snw", "snw", "Q94527193", "snw", 20),
)
PROPOSAL_FIELDS = {
    "accepted_source_binding_effect", "accepted_work_effect", "candidates",
    "coverage_effect", "proposal_only", "proposal_type", "provenance",
}
CANDIDATE_FIELDS = {
    "canonical_work_id", "episode_label", "episode_number", "episode_qid",
    "evidence_status", "record_type", "season_number", "series_label",
    "series_qid", "status",
}
PROVENANCE_FIELDS = {
    "license", "license_url", "provenance_verification", "query_sha256",
    "response_sha256", "retrieved_at_epoch", "snapshot_id", "source_url",
}
RECEIPT_FIELDS = {
    "source_url", "license", "license_url", "retrieved_at_epoch",
    "snapshot_id", "query_text",
}
OUTPUT_PATH = Path("explorer/research-leads.json")


def _no_duplicates(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _bad_constant(value: str) -> None:
    raise ValueError(f"non-JSON numeric constant: {value}")


def _strict_json(data: bytes, label: str) -> object:
    try:
        return json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_no_duplicates,
            parse_constant=_bad_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label}: malformed UTF-8 JSON") from exc


def _validate_root(repo_root: Path) -> Path:
    if repo_root.is_symlink():
        raise ValueError("repo root is a symlink")
    root = repo_root.resolve()
    if not root.is_dir():
        raise ValueError(f"missing repository directory: {repo_root}")
    return root


def safe_read(repo_root: Path, relative_path: Path, *, max_bytes: int = 512_000) -> bytes:
    """Read only regular in-repository files; reject path traversal/symlinks."""
    root = _validate_root(repo_root)
    rel = Path(relative_path)
    if rel.is_absolute() or not rel.parts or any(part in ("..", ".") for part in rel.parts):
        raise ValueError(f"unsafe path: {rel}")
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlinked governed input: {rel}")
    if not current.is_file():
        raise ValueError(f"missing governed input: {rel}")
    if current.stat().st_size > max_bytes:
        raise ValueError(f"oversized governed input: {rel}")
    return current.read_bytes()


def _required_object(value: object, fields: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label}: unexpected or missing fields")
    return value


def _check_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not DIGEST_PATTERN.fullmatch(value):
        raise ValueError(f"{label}: expected lowercase 64-digit SHA-256")
    return value


def _checked_title(value: object) -> str:
    if (
        not isinstance(value, str)
        or not 1 <= len(value) <= 160
        or value != value.strip()
        or any(unicodedata.category(char)[0] == "C" or char in "<>" for char in value)
    ):
        raise ValueError("unsafe episode_label")
    return value


def _source_paths(group: str, key: str, proposal_stem: str) -> tuple[Path, Path, Path]:
    if group == "tng":
        folder = Path("proposals/discovery/wikidata-tng-q16290-20261102")
        return folder / "query.rq", folder / "receipt.json", folder / "candidates.json"
    folder = Path("proposals/discovery/wikidata-mission-samples-20261102") / group
    return (
        folder / "queries" / f"{key}.rq",
        folder / "receipts" / f"{key}.json",
        folder / "proposals" / f"{proposal_stem}.json",
    )


def _validate_catalog(root: Path) -> None:
    catalog = _strict_json(safe_read(root, Path("registry/mission_catalog.json")), "mission catalog")
    if not isinstance(catalog, dict) or catalog.get("admission_status") != "DISPLAY_CATALOG_ONLY":
        raise ValueError("mission catalog must be display-only")
    missions = catalog.get("missions")
    if not isinstance(missions, list):
        raise ValueError("mission catalog lacks Missions")
    ids = []
    for mission in missions:
        if not isinstance(mission, dict) or not isinstance(mission.get("id"), str):
            raise ValueError("invalid Mission catalog entry")
        ids.append(mission["id"])
    if tuple(ids) != MISSION_ORDER:
        raise ValueError("Mission catalog identity/order mismatch")


def _load_batch(
    root: Path,
    group: str,
    key: str,
    proposal_stem: str,
    series_qid: str,
    mission_id: str,
    count: int,
    seen_qids: set[str],
    seen_snapshots: set[str],
) -> list[dict]:
    query_path, receipt_path, proposal_path = _source_paths(group, key, proposal_stem)
    query = safe_read(root, query_path, max_bytes=20_000)
    receipt = _required_object(
        _strict_json(safe_read(root, receipt_path), str(receipt_path)),
        RECEIPT_FIELDS, f"{receipt_path}: receipt fields",
    )
    proposal = _required_object(
        _strict_json(safe_read(root, proposal_path), str(proposal_path)),
        PROPOSAL_FIELDS, f"{proposal_path}: proposal fields",
    )
    provenance = _required_object(
        proposal["provenance"], PROVENANCE_FIELDS, f"{proposal_path}: provenance fields"
    )
    if not isinstance(receipt["query_text"], str) or receipt["query_text"].encode("utf-8") != query:
        raise ValueError(f"{receipt_path}: query text mismatch")
    actual_sha = hashlib.sha256(query).hexdigest()
    if _check_digest(provenance["query_sha256"], "query_sha256") != actual_sha:
        raise ValueError(f"{proposal_path}: query SHA-256 mismatch")
    _check_digest(provenance["response_sha256"], "response_sha256")
    if (
        receipt["source_url"] != EXPECTED_SOURCE_URL
        or provenance["source_url"] != EXPECTED_SOURCE_URL
        or receipt["license"] != "CC0-1.0"
        or provenance["license"] != "CC0-1.0"
        or receipt["license_url"] != EXPECTED_LICENSE_URL
        or provenance["license_url"] != EXPECTED_LICENSE_URL
        or provenance["provenance_verification"] != PROVENANCE_STATUS
    ):
        raise ValueError(f"{proposal_path}: unsupported source/provenance")
    snapshot = provenance["snapshot_id"]
    stamp = provenance["retrieved_at_epoch"]
    if (
        not isinstance(snapshot, str)
        or not SNAPSHOT_PATTERN.fullmatch(snapshot)
        or receipt["snapshot_id"] != snapshot
        or snapshot in seen_snapshots
        or type(stamp) is not int
        or stamp <= 0
        or receipt["retrieved_at_epoch"] != stamp
    ):
        raise ValueError(f"{proposal_path}: invalid or duplicate retrieval snapshot")
    seen_snapshots.add(snapshot)
    if (
        proposal["proposal_only"] is not True
        or proposal["proposal_type"] != "WIKIDATA_EPISODE_DISCOVERY_V1"
        or proposal["accepted_work_effect"] != "NONE"
        or proposal["accepted_source_binding_effect"] != "NONE"
    ):
        raise ValueError(f"{proposal_path}: forbidden accepted Work/Source effects")
    if proposal["coverage_effect"] != "NONE":
        raise ValueError(f"{proposal_path}: forbidden coverage_effect")
    candidates = proposal["candidates"]
    if not isinstance(candidates, list) or len(candidates) != count:
        raise ValueError(f"{proposal_path}: expected {count} bounded candidates")
    leads = []
    for row in candidates:
        _required_object(row, CANDIDATE_FIELDS, f"{proposal_path}: candidate fields")
        episode_qid = row["episode_qid"]
        if not isinstance(episode_qid, str) or not QID_PATTERN.fullmatch(episode_qid):
            raise ValueError(f"{proposal_path}: malformed episode QID")
        if episode_qid in seen_qids:
            raise ValueError(f"{proposal_path}: duplicate episode QID: {episode_qid}")
        seen_qids.add(episode_qid)
        if row["series_qid"] != series_qid:
            raise ValueError(f"{proposal_path}: wrong series QID for {mission_id}")
        if row["status"] != "CANDIDATE" or row["evidence_status"] != "EXTERNAL_DISCOVERY_METADATA_ONLY":
            raise ValueError(f"{proposal_path}: episode row is not candidate-only")
        if row["canonical_work_id"] is not None:
            raise ValueError(f"{proposal_path}: forbidden canonical_work_id")
        if (
            row["record_type"] != "episode_discovery_candidate"
            or row["episode_number"] is not None
            or row["season_number"] is not None
            or row["series_label"] is not None
        ):
            raise ValueError(f"{proposal_path}: unsupported candidate detail")
        leads.append({
            "mission_id": mission_id,
            "episode_qid": episode_qid,
            "episode_label": _checked_title(row["episode_label"]),
            "snapshot_id": snapshot,
            "query_sha256": actual_sha,
            "response_sha256": provenance["response_sha256"],
            "verification_status": "UNVERIFIED_METADATA",
        })
    return leads


def build_bytes(repo_root: Path) -> bytes:
    """Return canonical, byte-deterministic output without modifying files."""
    root = _validate_root(Path(repo_root))
    _validate_catalog(root)
    seen_qids, seen_snapshots = set(), set()
    all_leads = []
    for batch in SOURCE_BATCHES:
        all_leads.extend(_load_batch(root, *batch, seen_qids, seen_snapshots))
    mission_index = {mission: i for i, mission in enumerate(MISSION_ORDER)}
    all_leads.sort(key=lambda row: (mission_index[row["mission_id"]], int(row["episode_qid"][1:])))
    document = {
        "schema_version": "1.0.0",
        "data_status": "CANDIDATE_DISCOVERY_ONLY",
        "source_policy": "EXTERNAL_METADATA_ONLY",
        "coverage_effect": "NONE",
        "lead_count": len(all_leads),
        "sampled_missions_count": len({row["mission_id"] for row in all_leads}),
        "leads": all_leads,
    }
    return (json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_or_check(repo_root: Path, *, check: bool) -> Path:
    root = _validate_root(Path(repo_root))
    encoded = build_bytes(root)
    out_dir = root / OUTPUT_PATH.parent
    target = root / OUTPUT_PATH
    if out_dir.is_symlink() or target.is_symlink():
        raise ValueError("symlinked public output path")
    if check:
        if (
            not target.is_file()
            or target.stat().st_size != len(encoded)
            or target.read_bytes() != encoded
        ):
            raise ValueError(f"out of date: {OUTPUT_PATH}")
        return target
    out_dir.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".research-leads-", suffix=".tmp", dir=out_dir)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, target)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="compare committed index, do not write")
    options = parser.parse_args(argv)
    try:
        target = write_or_check(options.repo_root, check=options.check)
        print(f"RESEARCH_LEADS_CANDIDATES: {len(json.loads(target.read_bytes())['leads'])} -> {target}")
        return 0
    except (ValueError, OSError) as exc:
        parser.exit(1, f"RESEARCH_LEADS_ERROR: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
