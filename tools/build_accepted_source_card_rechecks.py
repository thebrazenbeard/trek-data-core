#!/usr/bin/env python3
"""Deterministically project accepted, source-local publisher-card rechecks.

The B001-B004 56-row Explorer projection is intentionally separate. A publisher
episode card is NOT a watched episode, transcript, Work admission, original
synopsis approval, raw source-byte custody, or independent corroboration of
Wikidata. In particular, the SNW S3 cards lack explicit discovery row IDs and
must await an accepted reconciliation record before any directory join.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = Path("explorer/discovery-catalog.json")
OUTPUT = Path("explorer/accepted-source-card-rechecks.json")
SOURCES = (
    ("B005-DS9", Path("proposals/verification/episode-guide-rechecks-b005-20261103/observations.json"), 16),
    ("B006-VOY", Path("proposals/verification/episode-guide-rechecks-b006-voy-20261103/observations.json"), 13),
    ("B007-VOY", Path("proposals/librarian/voy-b007-source-card-20261103/records.json"), 7),
    ("B008-ENT", Path("proposals/verification/episode-guide-rechecks-b008-ent-20261103/observations.json"), 9),
    ("B009-ENT", Path("proposals/verification/episode-guide-rechecks-b009-ent-20261103/observations.json"), 9),
    ("DIS-S3-SEVEN", Path("proposals/research/dis/s3-publisher-seven-20261103/records.json"), 7),
)
UNMAPPED_SNW_INPUTS = (
    Path("proposals/research/snw/s3-publisher-first5-20261103/records.json"),
    Path("proposals/research/snw/s3-publisher-last5-20261103/records.json"),
)
EXPECTED_LEADS = [*(f"lead:{n:04d}" for n in range(51, 67)),
                  *(f"lead:{n:04d}" for n in range(70, 115))]
EXPECTED_DIRECTORY_SHA256 = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
APPROVED_TITLE_RESOLUTIONS = {
    "B005-DS9": frozenset({"EXACT", "CASE_VARIANT_UNRESOLVED"}),
    "B006-VOY": frozenset({"EXACT", "CASE_VARIANT_UNRESOLVED", "MULTIPART_TITLE_SCOPE_UNRESOLVED"}),
    "B007-VOY": frozenset({"EXACT", "NUMERAL_AND_CASE_VARIANT_UNRESOLVED", "ROMAN_NUMERAL_VARIANT_UNRESOLVED"}),
    "B008-ENT": frozenset({"EXACT_OFFICIAL_CARD_TITLE", "ROMAN_NUMERAL_VARIANT_UNRESOLVED"}),
    "B009-ENT": frozenset({"EXACT_OFFICIAL_CARD_TITLE", "PART_NUMERAL_STYLE_UNRESOLVED",
                            "PUNCTUATION_STYLE_UNRESOLVED", "COMBINED_CARD_SPLIT_UNRESOLVED"}),
    "DIS-S3-SEVEN": frozenset({"EXACT", "PART_NUMERAL_STYLE_UNRESOLVED"}),
}


def load(path: Path) -> tuple[dict, bytes]:
    target = ROOT / path
    if target.is_symlink() or not target.is_file():
        raise ValueError(f"missing or symlinked accepted input: {path}")
    raw = target.read_bytes()
    if len(raw) > 10_000_000:
        raise ValueError(f"unbounded accepted JSON input: {path}")

    def unique_pairs(pairs: list[tuple]) -> dict:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate accepted JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(raw, object_pairs_hook=unique_pairs)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value, raw


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _status(batch: str, value: str, directory_title: str, observed_title: str) -> str:
    # The closed vocabulary is a positive permission boundary. A suffix such
    # as *_UNRESOLVED cannot legitimize arbitrary research/admission claims.
    if value not in APPROVED_TITLE_RESOLUTIONS[batch]:
        raise ValueError(f"unapproved publisher title resolution for {batch}: {value!r}")
    exact = value in {"EXACT", "EXACT_OFFICIAL_CARD_TITLE"}
    if exact and observed_title != directory_title:
        raise ValueError("false EXACT publisher title claim")
    if not exact and observed_title == directory_title:
        raise ValueError("false unresolved publisher title claim")
    return "EXACT" if exact else value


def build() -> dict:
    directory, raw_directory = load(DIRECTORY)
    if (sha(raw_directory) != EXPECTED_DIRECTORY_SHA256
            or directory.get("row_count") != 1214
            or len(directory.get("rows", [])) != 1214):
        raise ValueError("accepted 1,214-row source-local directory digest changed")
    directory_by_id = {row["row_id"]: row for row in directory["rows"]}
    if len(directory_by_id) != 1214:
        raise ValueError("duplicate directory row IDs")

    checks: dict[str, dict] = {}
    receipts = [{"path": DIRECTORY.as_posix(), "sha256": sha(raw_directory)}]
    for batch, path, expected_count in SOURCES:
        doc, raw = load(path)
        receipts.append({"path": path.as_posix(), "sha256": sha(raw)})
        if batch == "B007-VOY":
            raw_rows = doc.get("candidate_rows", [])
            snapshot = doc.get("catalog_snapshot", {})
            if (snapshot.get("sha256") != sha(raw_directory)
                    or snapshot.get("row_count") != 1214):
                raise ValueError("B007 source-local catalog pin mismatch")
            if (doc.get("source_body_read") is not False
                    or doc.get("raw_http_response_sha256") is not None
                    or doc.get("source_family") != "paramount_corporate_publisher_family"
                    or doc.get("accepted_corpus_effect") != "NONE"):
                # The worker inspected rendered cards, not full source bodies.
                # Raw HTTP bytes were not pinned, so we require the null receipt.
                raise ValueError("B007 source representation changed")
            date = doc["observed_date_utc"]
        elif batch == "DIS-S3-SEVEN":
            raw_rows = doc.get("works", [])
            if (doc.get("accepted_work_effect") != "NONE"
                    or doc.get("coverage_effect") != "NONE"
                    or doc.get("full_primary_source_available") is not False
                    or doc.get("source", {}).get("independence_group") != "publisher:paramountplus.com"
                    or doc.get("source", {}).get("snapshot_committed") is not False):
                raise ValueError("DIS source-only custody was elevated")
            date = doc["source"]["retrieved_utc_date"]  # source read date, not episode release date
        else:
            raw_rows = doc.get("rows", [])
            if doc.get("coverage_effect") != "NONE" or doc.get("admission_effect") != "NONE":
                raise ValueError("publisher card source-only status was elevated")
            if doc.get("source_family") != "paramount_corporate_publisher_family":
                raise ValueError("publisher source family changed")
            if doc.get("catalog_sha256", sha(raw_directory)) != sha(raw_directory):
                raise ValueError("accepted source observation catalog pin mismatch")
            date = doc.get("observed_date_utc", doc.get("observed_utc_date"))

        if len(raw_rows) != expected_count or not isinstance(date, str) or not date:
            raise ValueError(f"unexpected accepted source batch count/date: {batch}")
        for original in raw_rows:
            row_id = original.get("lead_id") if batch == "DIS-S3-SEVEN" else original.get("row_id")
            row = directory_by_id.get(row_id)
            if (not isinstance(row_id, str) or row_id in checks or row is None
                    or row.get("medium") != "EPISODE" or row.get("source_group") != "wikidata:wdqs"
                    or row.get("coverage_effect") != "NONE"
                    or row.get("verification_status") != "UNVERIFIED_METADATA"):
                raise ValueError(f"missing/duplicate/non-source-local directory lead: {row_id!r}")

            if batch == "B005-DS9":
                cards = original["cards"]
                observed_title = " / ".join(card["official_title"] for card in cards)
                season_slots = [{"season": c["season"], "episode": c["episode"]} for c in cards]
                resolution = original["title_resolution"]
                guide = None  # no direct official card URL survives in accepted B005 record
            elif batch == "B007-VOY":
                observed_title = original["official_title"]
                season_slots = [{"season": original["season"], "episode": original["episode"]}]
                resolution = original["title_status"]
                guide = original["guide_url"]
            elif batch == "DIS-S3-SEVEN":
                observed_title = original["title"]
                season_slots = [{"season": original["season"], "episode": original["episode_number"]}]
                resolution = "EXACT" if observed_title == row["title"] else "PART_NUMERAL_STYLE_UNRESOLVED"
                guide = original["publisher_video_url"]
                if (original.get("source_binding_id") is not None
                        or original.get("canonical_work_id") is not None):
                    raise ValueError("DIS work admission must remain unset")
                if original.get("episode_qid") != row["source_locator"].rsplit("/", 1)[-1]:
                    raise ValueError("DIS lead_id -> QID exact source-local crosswalk failed")
            else:
                observed_title = original["official_card_title"] if batch in ("B008-ENT", "B009-ENT") else original["official_title"]
                season_slots = [{"season": original["season"], "episode": original["episode"]}]
                resolution = original["title_resolution"]
                guide = None  # accepted rendered observations have no per-row URL pin

            if not isinstance(observed_title, str) or not observed_title.strip():
                raise ValueError("missing publisher card title")
            status = _status(batch, resolution, row["title"], observed_title)
            if not isinstance(season_slots, list) or any(
                type(s["season"]) is not int or type(s["episode"]) is not int
                or s["season"] < 1 or s["episode"] < 1 for s in season_slots
            ):
                raise ValueError("invalid source-local publisher season/episode slots")
            if guide is not None and not guide.startswith("https://www.paramountplus.com/"):
                raise ValueError("non-Paramount publisher link in accepted publisher source batch")
            if row["context"] not in batch.split("-") and not (batch == "DIS-S3-SEVEN" and row["context"] == "DIS"):
                raise ValueError("source-local series and publisher batch mismatch")
            checks[row_id] = {
                "row_id": row_id,
                "medium": "EPISODE",
                "source_local_title": row["title"],
                "source_local_context": row["context"],
                "source_local_locator": row["source_locator"],
                "source_local_source_family": "wikidata:wdqs",
                "publisher_family": "paramount_corporate_publisher_family",
                "publisher_card_title": observed_title,
                "publisher_guide_url": guide,
                "publisher_season_episode_slots": season_slots,
                "publisher_title_check": status,
                "original_resolution": resolution,
                "observed_utc_date": date,
                "source_batch": batch,
                "accepted_observation_path": path.as_posix(),
                "accepted_observation_sha256": sha(raw),
                "publisher_surface": "RENDERED_PUBLISHER_CARD_SOURCE_ONLY",
                "raw_publisher_page_sha256": None,
                "full_episode_or_transcript_read": False,
                "source_local_discovery_state": "CATALOGUED_METADATA_ONLY",
                "admission_effect": "NONE",
                "coverage_effect": "NONE",
                "synopsis_publication_effect": "NONE",
            }
    if sorted(checks) != EXPECTED_LEADS:
        raise ValueError("unexpected lead scope / missing provenance")
    for path in UNMAPPED_SNW_INPUTS:
        source, raw = load(path)
        receipts.append({"path": path.as_posix(), "sha256": sha(raw)})
        works = source.get("works", [])
        if (len(works) != 5
                or source.get("accepted_work_effect") != "NONE"
                or source.get("coverage_effect") != "NONE"
                or source.get("source", {}).get("independence_group") != "publisher:paramountplus.com"
                or any("lead_id" in work or "directory_row_id" in work for work in works)):
            raise ValueError("SNW source-local rows acquired an unaccepted directory binding")
    result_rows = [checks[row_id] for row_id in sorted(checks)]
    exact_count = sum(r["publisher_title_check"] == "EXACT" for r in result_rows)
    return {
        "schema_version": "1.0.0",
        "data_status": "ACCEPTED_SOURCE_ONLY_RENDERED_PUBLISHER_CARDS_NOT_RESEARCH_COVERAGE",
        "directory_row_count": 1214,
        "prior_metadata_recheck_count_unchanged": 56,
        "new_publisher_card_source_local_lead_count": 61,
        "new_exact_title_matches": exact_count,
        "new_unresolved_title_or_split_cases": 61 - exact_count,
        "publisher_source_family_count": 1,
        "upstream_wikidata_is_not_independent_corroboration": True,
        "unmapped_snw_s3_cards_not_joined": 10,
        "source_directory_sha256": sha(raw_directory),
        "accepted_input_receipts": receipts,
        "admitted_works": 0,
        "approved_public_synopses": 0,
        "full_audiovisual_content_reads": 0,
        "raw_publisher_pages_custodied": 0,
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
        "rows": result_rows,
    }


def encode(result: dict) -> bytes:
    return (json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if committed sidecar differs from accepted inputs")
    args = parser.parse_args()
    encoded = encode(build())
    target = ROOT / OUTPUT
    if target.is_symlink():
        raise SystemExit("ACCEPTED_SOURCE_CARD_OUTPUT_SYMLINK_REFUSED")
    if args.check:
        if not target.is_file() or target.read_bytes() != encoded:
            raise SystemExit("ACCEPTED_SOURCE_CARD_PROJECTION_STALE_OR_TAMPERED")
    else:
        target.write_bytes(encoded)
    print("ACCEPTED_SOURCE_CARD_RECHECKS_OK: 61 additional source-only cards; "
          "prior 56 unchanged; no Work admissions, no audiovisual coverage")


if __name__ == "__main__":
    main()
