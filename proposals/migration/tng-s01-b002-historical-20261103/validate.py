#!/usr/bin/env python3
"""Check an unadmitted historical TNG staging migration and its crosswalk."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COMMIT = "e4c891b26622ae08eac346a55059a58f687d064c"
HISTORICAL_PREFIX = "research/tng/staging/tng-s01-b002/"
SHA1 = re.compile(r"[a-f0-9]{40}\Z")
SHA256 = re.compile(r"[a-f0-9]{64}\Z")


def check(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def read_historical(repo: Path, path: str, blob_sha: str) -> bytes:
    check(path.startswith(HISTORICAL_PREFIX) and ".." not in Path(path).parts,
          "unsafe historical path")
    env = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"}
    def git(*args: str) -> bytes:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True,
            check=False, env=env, timeout=15,
        )
        check(result.returncode == 0, f"historical Git object unavailable: {path}")
        return result.stdout
    actual_sha = git("rev-parse", f"{COMMIT}:{path}").decode("ascii").strip()
    check(actual_sha == blob_sha, f"historical tree/blob mismatch: {path}")
    size = int(git("cat-file", "-s", blob_sha).decode("ascii").strip())
    check(size < 1024 * 1024, f"historical blob too large: {path}")
    content = git("cat-file", "blob", blob_sha)
    check(len(content) == size, f"historical blob length mismatch: {path}")
    return content


def validate(historical_repo: Path | None) -> None:
    data = json.loads((HERE / "records.json").read_text(encoding="utf-8"))
    check(data["proposal_type"] == "HISTORICAL_TNG_STAGING_METADATA_V1", "proposal type")
    check(data["proposal_only"] is True and data["admission_status"] == "NOT_ADMITTED", "not proposal-only")
    check(data["accepted_corpus_effect"] == data["accepted_coverage_effect"] == "NONE", "accepted effect")
    check(data["source_content_retrieved_by_this_migration"] is False, "source read claim")
    check(data["primary_audiovisual_verified"] is False, "AV verification claim")
    historical = data["historical_source"]
    check(historical["immutable_commit"] == COMMIT and historical["pr_number"] == 12, "historical ref")
    check(historical["reported_counts"] == {"works": 5, "evidence": 50, "staging_assertions": 25}, "reported counts")
    check(historical["transcript_lineage_independence"] == "UNKNOWN", "lineage falsely resolved")

    artifacts = data["historical_artifacts"]
    check(len(artifacts) == 8, "not eight historical artifacts")
    check(len({item["path"] for item in artifacts}) == 8, "duplicate historical paths")
    check(any(item["path"].endswith("validation.json") for item in artifacts), "historical validation absent")
    for item in artifacts:
        path, blob_sha, digest = item["path"], item["git_blob_sha1"], item["sha256"]
        check(path.startswith(HISTORICAL_PREFIX) and ".." not in Path(path).parts, "unsafe path")
        check(bool(SHA1.fullmatch(blob_sha)) and bool(SHA256.fullmatch(digest)), "invalid digest")
        if historical_repo is not None:
            content = read_historical(historical_repo, path, blob_sha)
            check(hashlib.sha256(content).hexdigest() == digest, f"historical SHA-256 mismatch: {path}")

    crosswalk = data["publisher_crosswalk_candidate"]
    check(crosswalk["source_role"] == "DISCOVERY_METADATA_ONLY" and crosswalk["identity_effect"] == "NONE", "crosswalk promoted")
    relative = Path(crosswalk["path"])
    check(relative.as_posix() == "proposals/discovery/legacy-paramount-season1-20261102/tng.csv", "unexpected publisher catalog")
    publisher_bytes = (ROOT / relative).read_bytes()
    check(hashlib.sha256(publisher_bytes).hexdigest() == crosswalk["sha256"], "publisher snapshot changed")
    with (ROOT / relative).open(encoding="utf-8", newline="") as f:
        publisher_rows = {(int(row["season"]), int(row["episode_number"])): row["title"] for row in csv.DictReader(f)}

    rows = data["episode_candidates"]
    check(len(rows) == 5 and [r["historical_local_sequence"] for r in rows] == list(range(6, 11)), "historical order")
    check([r["publisher_episode_number"] for r in rows] == list(range(7, 12)), "publisher order")
    check(len({r["title"].casefold() for r in rows}) == 5, "duplicate title")
    for row in rows:
        check(row["canonical_work_id"] is None and row["canonical_source_id"] is None,
              "canonical identity invented")
        check(row["accepted_evidence_ids"] == [] and row["binding_status"] == "NOT_ADMITTED",
              "governed evidence or binding invented")
        check(row["publisher_season"] == 1 and row["publisher_title"] == publisher_rows.get((1, row["publisher_episode_number"])),
              "publisher row mismatch")
        check(row["historical_transcript_locator"].startswith("https://www.springfieldspringfield.co.uk/"), "source locator")
        check(row["historical_crosscheck_locator"].startswith("https://www.chakoteya.net/"), "crosscheck locator")
        check(row["transcript_lines_reported"][0] == 13 and row["transcript_lines_reported"][1] > 13,
              "invalid historical line extent")
        expected_status = "PUNCTUATION_VARIANT_REVIEW" if row["title"] == "Hide and Q" else "EXACT_CASE_INSENSITIVE"
        check(row["title_match_status"] == expected_status, "title match status")
        if expected_status == "EXACT_CASE_INSENSITIVE":
            check(row["title"].casefold() == row["publisher_title"].casefold(), "exact title mismatch")
    check(len(data["unresolved"]) >= 5, "missing unresolved gates")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical-repo", type=Path,
                        help="Optional offline Git repository holding exact historical PR #12 blobs")
    args = parser.parse_args()
    try:
        validate(args.historical_repo)
    except (ValueError, OSError, KeyError, IndexError, TypeError, subprocess.TimeoutExpired) as exc:
        print(f"MIGRATION_VALIDATION_FAILED: {exc}")
        return 1
    print("MIGRATION_VALIDATION_OK: five unadmitted TNG metadata candidates; eight historical receipts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
