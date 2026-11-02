#!/usr/bin/env python3
"""Dry-run a pinned, untrusted legacy research batch; never admit its claims.

The supplied directory must already contain a manifest and the named blobs.
This command does not fetch, execute historical code, write records, or reason
about identity. Its output is a deterministic structural *proposal* only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path, PurePosixPath


HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
MAX_MANIFEST = 1024 * 1024
MAX_ARTIFACT = 2 * 1024 * 1024
MAX_TOTAL = 16 * 1024 * 1024
MAX_ARTIFACTS = 100


class MigrationRejected(ValueError):
    """Input is unsafe, incomplete, or internally contradictory."""


def _pairs_unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise MigrationRejected(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _json(data: bytes, name: str) -> dict:
    try:
        parsed = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs_unique)
    except (UnicodeError, ValueError) as exc:
        raise MigrationRejected(f"invalid or ambiguous JSON in {name}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise MigrationRejected(f"{name} must be a JSON object")
    return parsed


def _relative(path: str) -> PurePosixPath:
    if not isinstance(path, str) or not path or len(path) > 240:
        raise MigrationRejected("artifact path is invalid")
    posix = PurePosixPath(path)
    if (
        posix.is_absolute()
        or any(part in ("", ".", "..") for part in path.split("/"))
        or "\\" in path
        or ":" in path
        or len(posix.parts) > 8
    ):
        raise MigrationRejected(f"unsafe artifact path: {path}")
    return posix


def _read_regular(root: Path, rel: str, limit: int) -> bytes:
    parts = _relative(rel).parts
    cursor = root
    for part in parts[:-1]:
        cursor = cursor / part
        try:
            info = os.lstat(cursor)
        except OSError as exc:
            raise MigrationRejected(f"artifact directory unavailable: {rel}") from exc
        if not stat.S_ISDIR(info.st_mode):
            raise MigrationRejected(f"artifact parent is not a real directory: {rel}")
    path = root.joinpath(*parts)
    try:
        before = os.lstat(path)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise MigrationRejected(f"artifact is not a bounded regular file: {rel}")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        descriptor = os.open(path, flags)
        try:
            after = os.fstat(descriptor)
            if (
                not stat.S_ISREG(after.st_mode)
                or after.st_dev != before.st_dev
                or after.st_ino != before.st_ino
                or after.st_size > limit
            ):
                raise MigrationRejected(f"artifact changed during read: {rel}")
            with os.fdopen(descriptor, "rb", closefd=False) as handle:
                data = handle.read(limit + 1)
            if len(data) > limit or len(data) != after.st_size:
                raise MigrationRejected(f"artifact too large or changed during read: {rel}")
            return data
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise MigrationRejected(f"artifact unavailable or unsafe: {rel}") from exc


def _entries(value: object, label: str) -> list[dict]:
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise MigrationRejected(f"{label} must be a list of objects")
    return value


def _identity(row: dict, label: str) -> str:
    value = row.get("id")
    if not isinstance(value, str) or not value or len(value) > 256:
        raise MigrationRejected(f"invalid {label} ID")
    return value


def plan(root: Path, expected_manifest_sha256: str, *, source_pr: int | None = None,
         source_head_sha: str | None = None) -> dict:
    """Produce a deterministic, source-unverified migration eligibility report."""
    if not HEX64.fullmatch(expected_manifest_sha256):
        raise MigrationRejected("a full lowercase manifest SHA-256 is required")
    if source_pr is not None and (type(source_pr) is not int or source_pr < 1):
        raise MigrationRejected("source PR number must be a positive integer")
    if source_head_sha is not None and not HEX40.fullmatch(source_head_sha):
        raise MigrationRejected("source head SHA must be a full lowercase Git SHA-1")
    if root.is_symlink() or not root.is_dir():
        raise MigrationRejected("batch root must be a real directory")

    manifest_bytes = _read_regular(root, "manifest.json", MAX_MANIFEST)
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    if manifest_hash != expected_manifest_sha256:
        raise MigrationRejected("manifest hash does not match independently pinned input")
    manifest = _json(manifest_bytes, "manifest.json")
    if manifest.get("status") not in ("PROPOSAL_VALIDATED", "PROPOSAL_ONLY"):
        raise MigrationRejected("unsupported legacy status, no implicit admission")
    batch_id, lane, version = (manifest.get(k) for k in ("batch_id", "lane", "schema_version"))
    if any(not isinstance(x, str) or not x or len(x) > 100 for x in (batch_id, lane, version)):
        raise MigrationRejected("missing or invalid batch/lane/schema identity")
    expected_sha = manifest.get("artifact_sha256")
    expected_git = manifest.get("artifact_git_blob_sha1")
    if not isinstance(expected_sha, dict) or not expected_sha or len(expected_sha) > MAX_ARTIFACTS:
        raise MigrationRejected("missing or oversized artifact digest map")
    if not isinstance(expected_git, dict) or set(expected_sha) != set(expected_git):
        raise MigrationRejected("SHA-256/Git object manifest key disagreement")

    actual_artifacts = []
    observations = []
    assertions = []
    entities = []
    all_ids: set[str] = set()
    total_bytes = len(manifest_bytes)
    for name in sorted(expected_sha):
        if not name.startswith("records/") and name not in ("coverage_update.json", "validation.json"):
            raise MigrationRejected(f"unrecognized artifact category: {name}")
        declared_sha, declared_git = expected_sha[name], expected_git[name]
        if not isinstance(declared_sha, str) or not HEX64.fullmatch(declared_sha):
            raise MigrationRejected(f"bad declared SHA-256: {name}")
        if not isinstance(declared_git, str) or not HEX40.fullmatch(declared_git):
            raise MigrationRejected(f"bad declared Git blob ID: {name}")
        data = _read_regular(root, name, MAX_ARTIFACT)
        total_bytes += len(data)
        if total_bytes > MAX_TOTAL:
            raise MigrationRejected("aggregate input size exceeds limit")
        digest = hashlib.sha256(data).hexdigest()
        git_id = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        if digest != declared_sha or git_id != declared_git:
            raise MigrationRejected(f"artifact hashes disagree with manifest: {name}")
        actual_artifacts.append({"path": name, "sha256": digest, "git_blob_sha1": git_id})
        if not name.startswith("records/"):
            continue
        record = _json(data, name)
        if record.get("batch_id") != batch_id or record.get("lane") != lane:
            raise MigrationRejected(f"record batch/lane mismatch: {name}")
        if record.get("schema_version") != version:
            raise MigrationRejected(f"record schema mismatch: {name}")
        for category, dest in (("evidence", observations), ("assertions", assertions),
                               ("local_entities", entities)):
            for row in _entries(record.get(category, []), f"{name}.{category}"):
                identifier = _identity(row, category)
                if identifier in all_ids:
                    raise MigrationRejected(f"duplicate cross-file local record ID: {identifier}")
                all_ids.add(identifier)
                if category == "evidence":
                    if any(not isinstance(row.get(k), str) or not row[k] for k in ("src", "loc", "work")):
                        raise MigrationRejected(f"missing source-relative evidence locator: {identifier}")
                    dest.append({"id": identifier, "work_local_ref": row["work"],
                                 "source_alias": row["src"], "locator": row["loc"]})
                elif category == "assertions":
                    if not isinstance(row.get("support"), list) or not row["support"]:
                        raise MigrationRejected(f"unsupported assertion: {identifier}")
                    if any(not isinstance(v, str) for v in row["support"]):
                        raise MigrationRejected(f"invalid assertion support: {identifier}")
                    dest.append({"id": identifier, "support": row["support"]})
                else:
                    if row.get("global_identity") != "UNRESOLVED_LOCAL_ONLY":
                        raise MigrationRejected(f"global identity must stay unresolved: {identifier}")
                    dest.append({"id": identifier, "work_local_ref": row.get("work")})

    evidence_ids = {v["id"] for v in observations}
    for assertion in assertions:
        if any(key not in evidence_ids for key in assertion["support"]):
            raise MigrationRejected(f"missing evidence support: {assertion['id']}")
    source_rows = _entries(manifest.get("source_strategy", []), "source_strategy")
    source_alias_values = [row.get("alias") for row in source_rows]
    if any(not isinstance(alias, str) or not alias or len(alias) > 256
           for alias in source_alias_values):
        raise MigrationRejected("invalid source alias")
    aliases = set(source_alias_values)
    if not aliases or len(aliases) != len(source_rows):
        raise MigrationRejected("unknown/duplicate source aliases")
    if any(v["source_alias"] not in aliases for v in observations):
        raise MigrationRejected("evidence references undeclared source alias")
    counts = manifest.get("record_counts")
    if not isinstance(counts, dict) or any(type(counts.get(k)) is not int for k in ("evidence", "assertions", "local_entities")):
        raise MigrationRejected("missing historical record counts")
    observed_counts = {"evidence": len(observations), "assertions": len(assertions),
                       "local_entities": len(entities)}
    if any(counts[k] != observed_counts[k] for k in observed_counts):
        raise MigrationRejected("record counts do not match independently parsed files")
    scopes = _entries(manifest.get("scope", []), "scope")
    if type(counts.get("works")) is not int or counts["works"] != len(scopes):
        raise MigrationRejected("proposed Works count differs from scope declarations")

    result = {
        "schema_version": "trek-legacy-migration-dry-run-v1",
        "batch_id": batch_id,
        "lane": lane,
        "legacy_schema_version": version,
        "source_pr_declared": source_pr,
        "source_head_sha_declared": source_head_sha,
        "manifest_sha256": manifest_hash,
        "artifact_count": len(actual_artifacts),
        "artifacts": actual_artifacts,
        "observed_record_counts": observed_counts,
        "source_aliases": sorted(aliases),
        "evidence_locators": sorted(observations, key=lambda r: r["id"]),
        "assertion_support_links": sorted(assertions, key=lambda r: r["id"]),
        "local_entity_ids": sorted((r["id"] for r in entities)),
        "status": "STRUCTURAL_MIGRATION_CANDIDATE_NOT_ADMITTED",
        "external_source_bytes_inspected": False,
        "source_custody_review": "NOT_PERFORMED",
        "content_claims_verified": False,
        "human_review": "NOT_PERFORMED",
        "identity_reconciliation": "NOT_PERFORMED",
        "accepted_source_work_evidence_assertion_coverage_effect": "NONE",
    }
    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result["dry_run_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-dir", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--source-pr", type=int)
    parser.add_argument("--source-head-sha")
    args = parser.parse_args(argv)
    try:
        result = plan(args.batch_dir, args.expected_manifest_sha256,
                      source_pr=args.source_pr, source_head_sha=args.source_head_sha)
    except (MigrationRejected, OSError) as exc:
        print(f"LEGACY_MIGRATION_DRY_RUN_REJECTED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
