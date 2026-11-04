#!/usr/bin/env python3
"""Build/check a *held-only* source-relative artwork review queue.

The source ledger has publisher-observed URLs, not image copyright grants.
This builder cannot emit an Explorer/Pages artwork release. Even a plausible
rights/license assertion in candidate JSON cannot authorize publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("proposals/librarian/artwork-primary-asset-locators-20261103/records.json")
OUTPUT = Path("proposals/librarian/artwork-candidate-ingestion-20261104/records.json")
SOURCE_SHA256 = "9ffde76a5cd14d915dd17e672c8a5e3dc87d9f7fbc1d085e2638ab732f40f972"
RELEASE_STATUSES = frozenset({"PUBLIC_DISPLAY_PERMISSION_VERIFIED", "LICENSED", "PUBLIC_DOMAIN"})


class IntakeRejected(ValueError):
    pass


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _strict_json(raw: bytes) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise IntakeRejected(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    obj = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                     parse_constant=lambda _: (_ for _ in ()).throw(IntakeRejected("nonfinite JSON")))
    if not isinstance(obj, dict):
        raise IntakeRejected("packet root must be object")
    return obj


def _checked_file(root: Path, relative: Path) -> bytes:
    # All inputs are hard-coded repository-relative paths; no metadata-driven
    # paths are opened. Reject symlinks so a checkout cannot redirect reads.
    node = root
    for part in relative.parts:
        if part in ("", ".", ".."):
            raise IntakeRejected("unsafe repository path")
        node = node / part
        if node.is_symlink():
            raise IntakeRejected("symlink in repository input path")
    if not node.is_file() or node.stat().st_size > 2_000_000:
        raise IntakeRejected("missing, non-file, or oversized repository input")
    return node.read_bytes()


def build(root: Path = ROOT) -> dict:
    raw = _checked_file(root, SOURCE)
    if _digest(raw) != SOURCE_SHA256:
        raise IntakeRejected("pinned first-party locator packet changed")
    source = _strict_json(raw)
    source_validator = runpy.run_path(str(root / "proposals/librarian/artwork-primary-asset-locators-20261103/validate.py"))
    errors = source_validator["errors"](source, root)
    if errors:
        raise IntakeRejected("underlying source packet invalid: " + "; ".join(errors))
    source_hashes = {r["path"]: r["sha256"] for r in source["source_inputs"]}
    candidates = []
    for original in sorted(source["observations"], key=lambda item: item["local_id"]):
        candidates.append({
            "candidate_id": original["local_id"],
            "medium": original["medium"],
            "source_local_id": original["source_local_work_id"],
            "identity_scope": "SOURCE_RELATIVE_NOT_ACCEPTED_WORK",
            "publisher_page_url": original["publisher_source_url"],
            "image_url_observed": original["image_locator"],
            "image_kind_observed": original["image_kind"],
            "source_receipt": {
                "observed_date": source["observed_utc_date"],
                "observation_kind": original["source_inspection"],
                "packet_sha256": SOURCE_SHA256,
                "source_input_path": original["source_input"],
                "source_input_sha256": source_hashes[original["source_input"]],
                "locator_evidence_sha256": _digest(original["locator_evidence"].encode("utf-8")),
            },
            "rights": {
                "rights_class": "UNDERLYING_IMAGE_COPYRIGHT_UNRESOLVED",
                "license_identifier": None,
                "permission_receipt_sha256": None,
                "permission_receipt_url": None,
                "rights_reviewer": None,
                "allowed_public_operations": [],
            },
            "image_identity_reviewer": None,
            "independent_release_reviewer": None,
            "stage": "HELD_SOURCE_URL_ONLY",
            "public_display_eligible": False,
            "rehost_eligible": False,
            "public_image_path": None,
        })
    return {
        "schema_version": "1.0.0",
        "batch_id": "ARTWORK.CANDIDATE.INTAKE.20261104",
        "base_accepted_main": "3028765359001b90bc3e6b5c1835ee283b326e91",
        "data_status": "PROPOSED_HELD_METADATA_ONLY",
        "source_packet_path": SOURCE.as_posix(),
        "source_packet_sha256": SOURCE_SHA256,
        "candidate_count": len(candidates),
        "medium_counts": {medium: sum(row["medium"] == medium for row in candidates)
                          for medium in ("EPISODE", "FILM", "LITERATURE")},
        "reviewed_public_image_count": 0,
        "public_release_candidate_ids": [],
        "image_bytes_downloaded": False,
        "image_bytes_committed": False,
        "public_artwork_release_effect": "NONE",
        "accepted_source_work_effect": "NONE",
        "research_coverage_effect": "NONE",
        "candidates": candidates,
    }


def validate(candidate: dict, root: Path = ROOT) -> None:
    # Full structural equality is intentional: a proposed packet is not a
    # rights authority. An independently accepted rights review changes a
    # separate code-owned release gate, never this ingest queue in place.
    expected = build(root)
    if candidate != expected:
        raise IntakeRejected("candidate packet differs from pinned, held-only source-derived queue")
    if any(set(row["rights"]) != {
            "rights_class", "license_identifier", "permission_receipt_sha256",
            "permission_receipt_url", "rights_reviewer", "allowed_public_operations"
        } for row in candidate["candidates"]):
        raise IntakeRejected("rights schema drift")
    if any(row["rights"]["rights_class"] in RELEASE_STATUSES or
           row["public_display_eligible"] or row["rehost_eligible"] or
           row["public_image_path"] is not None for row in candidate["candidates"]):
        raise IntakeRejected("attempted self-certification of artwork rights")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--build", action="store_true", help="write only fixed local proposed held packet")
    args = parser.parse_args()
    expected = build()
    if args.build:
        target = ROOT / OUTPUT
        if target.exists() or target.is_symlink():
            raise IntakeRejected("refusing to overwrite preexisting candidate packet")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.parent.is_symlink():
            raise IntakeRejected("refusing output through symlink")
        target.write_text(json.dumps(expected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    actual = _strict_json(_checked_file(ROOT, OUTPUT))
    validate(actual)
    print("ARTWORK_CANDIDATE_INTAKE_HELD_OK:", expected["medium_counts"],
          "release candidates:", len(expected["public_release_candidate_ids"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
