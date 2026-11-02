#!/usr/bin/env python3
"""Recover the 2026 TNG pilot's *metadata* as an unadmitted, auditable proposal.

Reads historical Git blob bytes as data only; never checks out or executes a
historical revision and never copies narrative/transcript passages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

PR_NUMBER = 3
COMMIT = "0695fb2d36870e9c156ce7acd16f00f70103b19e"
PREFIX = "research/tng/batches/tng-s01-b001/"
MANIFEST = PREFIX + "manifest.json"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
EXPECTED_COUNTS = {"works": 5, "evidence": 58, "local_entities": 69, "assertions": 31}
MAX_BLOB_BYTES = 1024 * 1024


class RecoveryError(ValueError):
    pass


def read_git_blob(repo: Path, commit: str, path: str) -> tuple[str, bytes]:
    """Return an immutable Git blob identity and its raw bytes; no Git hooks."""
    if not HEX40.fullmatch(commit) or not safe_artifact_path(path):
        raise RecoveryError("invalid historical Git object reference")
    def run(*args: str) -> bytes:
        try:
            result = subprocess.run(
                ["git", "-C", str(repo), *args], capture_output=True,
                check=False, timeout=10,
                env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"},
            )
        except subprocess.TimeoutExpired as exc:
            raise RecoveryError("offline historical Git object read timed out") from exc
        if result.returncode:
            raise RecoveryError(f"historical Git object unavailable: {path}")
        return result.stdout
    blob_sha = run("rev-parse", f"{commit}:{path}").decode("ascii").strip()
    if not HEX40.fullmatch(blob_sha):
        raise RecoveryError("invalid Git blob SHA returned")
    size = run("cat-file", "-s", blob_sha).decode("ascii").strip()
    if not size.isdecimal() or int(size) > MAX_BLOB_BYTES:
        raise RecoveryError(f"unexpectedly large historical blob: {path}")
    raw = run("cat-file", "blob", blob_sha)
    if len(raw) != int(size):
        raise RecoveryError(f"historical blob size mismatch: {path}")
    return blob_sha, raw


def safe_artifact_path(path: object) -> bool:
    if not isinstance(path, str) or not path or "\\" in path or path.startswith("/"):
        return False
    parts = PurePosixPath(path).parts
    return all(piece not in (".", "..") for piece in parts) and path.startswith(PREFIX)


def checksum(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip() or len(value) > 800:
        raise RecoveryError(f"invalid {label}")
    if any(ord(ch) < 32 for ch in value):
        raise RecoveryError(f"control character in {label}")
    return value


def build_proposal(manifest: dict, commit: str, manifest_sha: str, manifest_bytes: bytes,
                   verified_artifacts: dict[str, tuple[str, str]]) -> dict:
    if not isinstance(manifest, dict) or not HEX40.fullmatch(commit) or not HEX40.fullmatch(manifest_sha):
        raise RecoveryError("invalid pilot manifest or Git commit")
    if manifest.get("batch_id") != "tng-s01-b001" or manifest.get("lane") != "TNG" or manifest.get("status") != "PROPOSAL_VALIDATED":
        raise RecoveryError("not the pinned TNG pilot proposal")
    if manifest.get("record_counts") != EXPECTED_COUNTS:
        raise RecoveryError("historical pilot aggregate counts changed")
    claims = manifest.get("artifact_git_blob_sha1")
    hashes = manifest.get("artifact_sha256")
    if not isinstance(claims, dict) or not isinstance(hashes, dict) or set(claims) != set(hashes) or len(claims) != 11:
        raise RecoveryError("invalid pilot artifact receipt inventory")
    if len(verified_artifacts) != len(claims):
        raise RecoveryError("missing pilot artifact verification")
    inventory = []
    for relative in sorted(claims):
        path = PREFIX + relative
        if not safe_artifact_path(path) or not (relative.startswith("records/") and relative.endswith(".json") or relative in ("coverage_update.json", "validation.json")):
            raise RecoveryError("unsafe or unexpected historical artifact path")
        blob_sha = claims[relative]
        blob_sha256 = hashes[relative]
        if not isinstance(blob_sha, str) or not HEX40.fullmatch(blob_sha) or not isinstance(blob_sha256, str) or not HEX64.fullmatch(blob_sha256):
            raise RecoveryError("malformed artifact receipt")
        if verified_artifacts.get(relative) != (blob_sha, blob_sha256):
            raise RecoveryError(f"historical artifact digest mismatch: {relative}")
        inventory.append({"historical_path": path, "git_blob_sha1": blob_sha, "content_sha256": blob_sha256})
    scope = manifest.get("scope")
    strategy = manifest.get("source_strategy")
    if not isinstance(scope, list) or len(scope) != 5 or not isinstance(strategy, list) or len(strategy) != 5:
        raise RecoveryError("pilot must have exactly five candidate Work/source rows")
    sources = {}
    for item in strategy:
        if not isinstance(item, dict):
            raise RecoveryError("invalid historical source row")
        local_ref = require_text(item.get("work_local_ref"), "source Work local reference")
        if local_ref in sources:
            raise RecoveryError("duplicate source Work reference")
        for field in ("url", "crosscheck_url"):
            url = require_text(item.get(field), field)
            if not url.startswith("https://"):
                raise RecoveryError("historical source URL is not HTTPS")
        sources[local_ref] = {
            "historical_provider": require_text(item.get("provider"), "source provider"),
            "historical_url": item["url"],
            "historical_crosscheck_provider": require_text(item.get("crosscheck_provider"), "crosscheck provider"),
            "historical_crosscheck_url": item["crosscheck_url"],
            "historical_retrieval_date": require_text(item.get("retrieved_utc_date"), "retrieval date"),
            "historical_line_extent_note": require_text(item.get("line_extent_processed"), "line extent"),
            "historical_representation_type": require_text(item.get("source_type"), "representation type"),
            "primary_audiovisual_verified": item.get("primary_audiovisual_verified") is True,
            "independence_status": require_text(item.get("lineage_independence"), "independence"),
        }
    works = []
    work_refs = set()
    episode_titles = set()
    transcript_indices = set()
    for row in scope:
        if not isinstance(row, dict):
            raise RecoveryError("invalid Work candidate")
        local_ref = require_text(row.get("work_local_ref"), "Work local reference")
        if local_ref in work_refs or local_ref not in sources:
            raise RecoveryError("duplicate/unbound local Work candidate")
        work_refs.add(local_ref)
        title = require_text(row.get("display_title"), "episode title")
        transcript_index = require_text(row.get("transcript_index"), "transcript index")
        if title.casefold() in episode_titles:
            raise RecoveryError("duplicate title in pilot scope")
        if transcript_index in transcript_indices:
            raise RecoveryError("duplicate transcript index in pilot scope")
        episode_titles.add(title.casefold())
        transcript_indices.add(transcript_index)
        works.append({
            "candidate_type": "EPISODE_WORK_METADATA",
            "status": "CANDIDATE",
            "historical_local_work_ref": local_ref,
            "title": title,
            "historical_airdate_crosscheck": require_text(row.get("airdate_crosscheck"), "airdate"),
            "historical_production_code": require_text(row.get("production_code_crosscheck"), "production code"),
            "historical_transcript_index": transcript_index,
            "source_candidate": sources[local_ref],
            "canonical_work_id": None,
            "canonical_source_id": None,
            "accepted_evidence_ids": [],
            "source_work_binding_status": "NOT_ADMITTED",
        })
    if set(sources) != work_refs:
        raise RecoveryError("orphan historical source strategy")
    blockers = manifest.get("known_blockers")
    if not isinstance(blockers, list) or len(blockers) < 4:
        raise RecoveryError("missing historical admission blockers")
    blockers = [require_text(v, "blocker") for v in blockers]
    works.sort(key=lambda w: w["historical_local_work_ref"])
    return {
        "proposal_type": "HISTORICAL_TNG_PILOT_CANDIDATES_V1",
        "proposal_only": True,
        "accepted_corpus_effect": "NONE",
        "accepted_coverage_effect": "NONE",
        "historical_source": {
            "repository": "thebrazenbeard/trek-data-core",
            "pull_request": PR_NUMBER,
            "immutable_commit": commit,
            "manifest_path": MANIFEST,
            "manifest_git_blob_sha1": manifest_sha,
            "manifest_sha256": checksum(manifest_bytes),
            "original_status": "PROPOSAL_VALIDATED_NOT_CANONICALLY_ADMITTED",
            "original_base_main_sha": manifest.get("base_main_sha"),
        },
        "original_candidate_counts": dict(EXPECTED_COUNTS),
        "known_admission_blockers": blockers,
        "numbering_note": require_text(manifest.get("numbering_note"), "numbering note"),
        "artifacts_verified": inventory,
        "episode_work_candidates": works,
    }


def extract(repo: Path) -> dict:
    manifest_sha, raw = read_git_blob(repo, COMMIT, MANIFEST)
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RecoveryError("historical pilot manifest is not valid JSON") from exc
    claims = manifest.get("artifact_git_blob_sha1")
    if not isinstance(claims, dict):
        raise RecoveryError("missing historical artifact claims")
    verified = {}
    for relative in claims:
        path = PREFIX + relative
        if not safe_artifact_path(path):
            raise RecoveryError("unsafe relative artifact path")
        sha, content = read_git_blob(repo, COMMIT, path)
        verified[relative] = (sha, checksum(content))
    return build_proposal(manifest, COMMIT, manifest_sha, raw, verified)


def output_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or len(path.parts) < 2 or path.parts[0] != "proposals":
        raise RecoveryError("output must be relative to proposals/")
    # The authoritative proposals boundary is root-relative, *not* a symlink
    # target chosen by the destination directory.
    allowed = root.resolve() / "proposals"
    target = (root / path).resolve()
    if not target.is_relative_to(allowed):
        raise RecoveryError("output resolves outside proposals/ via symlink")
    return root / path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical-repo", type=Path, required=True, help="Read-only Git object store containing historical PR #3")
    parser.add_argument("--output", default="proposals/tng/tng-s01-b001-historical-candidates.json")
    args = parser.parse_args(argv)
    try:
        payload = extract(args.historical_repo)
        dest = output_path(Path.cwd(), args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    except (RecoveryError, OSError) as exc:
        print(f"RECOVERY_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(f"RECOVERY_CANDIDATES: {len(payload['episode_work_candidates'])} unadmitted TNG episode Works -> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
