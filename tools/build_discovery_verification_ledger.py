#!/usr/bin/env python3
"""Deterministic source-local verification triage; never a research admission.

The five bounded rendered-page checks below are *declared observations* from
official publisher surfaces. They are not an authenticated raw-page snapshot,
full literary source binding, or independent confirmation of fictional facts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
RECHECKS = Path("proposals/verification/discovery-source-rechecks-b001-20261103/source_rechecks.json")
EPISODE_RECHECKS = Path("proposals/verification/discovery-source-rechecks-b001-20261103/episode_rechecks.json")
OUTPUT = Path("proposals/verification/discovery-source-rechecks-b001-20261103/ledger.json")

FAMILIES = {
    "wikidata:wdqs": "wikidata_collaborative_derivative",
    "publisher:paramount": "paramount_corporate_publisher_family",
    "publisher:startrek.com": "paramount_corporate_publisher_family",
    "publisher:paramountplus.com": "paramount_corporate_publisher_family",
    "publisher:simonandschuster.com": "simon_and_schuster_publisher_family",
    "distributor:penguinrandomhouse.com:titan-books": "titan_books_via_prh_distributor_family",
}
RECHECK_KEYS = {
    "row_id", "source_locator", "observed_title", "observed_creator", "observed_isbn",
    "observed_publisher", "observed_at_utc_date", "representation", "raw_body_sha256",
    "evidence_locator",
}
EPISODE_KEYS = {
    "row_id", "official_episode_url", "observed_title", "observed_series",
    "observed_season", "observed_episode", "observed_air_date", "observed_at_utc_date",
    "representation", "raw_body_sha256", "evidence_locator", "original_synopsis",
}
ISBN = re.compile(r"^97[89][0-9]{10}$")
DATE = re.compile(r"^20[0-9]{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$")
AIR_DATE = re.compile(r"^(?:19|20)[0-9]{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$")


def _read_json(path: Path) -> tuple[dict, bytes]:
    target = ROOT / path
    if target.is_symlink() or not target.is_file() or target.stat().st_size > 4_000_000:
        raise ValueError(f"missing, symlinked or oversized input: {path}")
    raw = target.read_bytes()
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    if not isinstance(data, dict):
        raise ValueError("expected top-level JSON object")
    return data, raw


def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _normalized(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _sig(row: dict) -> str:
    fields = (row["medium"], row["context"], row["title"], row["source_locator"])
    canonical = json.dumps([_normalized(field or "") for field in fields], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _row_hash(row: dict) -> str:
    canonical = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _check_rechecks(catalog: dict, declared: dict) -> dict[str, dict]:
    if (set(declared) != {"schema_version", "data_status", "admission_effect", "coverage_effect", "observations"}
            or declared["schema_version"] != "1.0.0"
            or declared["data_status"] != "BOUNDED_RENDERED_PRIMARY_METADATA_OBSERVATIONS"
            or declared["admission_effect"] != "NONE" or declared["coverage_effect"] != "NONE"
            or not isinstance(declared["observations"], list) or len(declared["observations"]) != 5):
        raise ValueError("unreviewed source recheck envelope")
    source_rows = {row["row_id"]: row for row in catalog["rows"]}
    checked = {}
    for obs in declared["observations"]:
        if not isinstance(obs, dict) or set(obs) != RECHECK_KEYS:
            raise ValueError("malformed rendered publisher observation")
        ident = obs["row_id"]
        row = source_rows.get(ident)
        if not row or ident in checked or row["medium"] != "LITERATURE":
            raise ValueError("duplicate or nonliterary source recheck")
        parsed = urlsplit(obs["source_locator"])
        if (obs["source_locator"] != row["source_locator"] or parsed.scheme != "https"
                or parsed.username or parsed.password or parsed.query or parsed.fragment
                or parsed.hostname not in {"www.penguinrandomhouse.com", "www.simonandschuster.com"}):
            raise ValueError("source URL not exact official publisher locator")
        if obs["observed_title"] != row["title"] or obs["observed_creator"] != row["context"].split(" · ", 1)[0]:
            raise ValueError("observed title or creator conflicts with source-local row")
        if (not isinstance(obs["observed_isbn"], str) or not ISBN.fullmatch(obs["observed_isbn"])
                or not any(isinstance(detail, str) and re.search(r"\bISBN " + obs["observed_isbn"] + r"$", detail)
                           for detail in row["details"])):
            raise ValueError("observed edition ISBN absent from source-local details")
        if not isinstance(obs["observed_at_utc_date"], str) or not DATE.fullmatch(obs["observed_at_utc_date"]):
            raise ValueError("invalid or unknown observation date")
        if (obs["representation"] != "OFFICIAL_RENDERED_WEB_PRODUCT_DETAILS" or obs["raw_body_sha256"] is not None
                or not isinstance(obs["evidence_locator"], str)
                or not obs["evidence_locator"].startswith(("Product Details:", "Trade Paperback Product Details:"))):
            raise ValueError("rendered-page check falsely claims pinned raw-body custody")
        if parsed.hostname == "www.penguinrandomhouse.com":
            if (row["source_group"] != "distributor:penguinrandomhouse.com:titan-books"
                    or row["candidate_kind"] != "FICTIONAL_MEMOIR" or obs["observed_publisher"] != "Titan Books"):
                raise ValueError("PRH/Titan check escaped its source and medium scope")
        elif (row["source_group"] != "publisher:simonandschuster.com" or row["candidate_kind"] != "NOVEL"
              or obs["observed_publisher"] is not None or not parsed.path.endswith("/" + obs["observed_isbn"])):
            raise ValueError("Simon & Schuster check escaped exact product edition")
        checked[ident] = obs
    if len({FAMILIES[source_rows[key]["source_group"]] for key in checked}) != 2:
        raise ValueError("bounded tranche must preserve both original source families")
    return checked


def _check_episode_rechecks(catalog: dict, declared: dict) -> dict[str, dict]:
    if (set(declared) != {"schema_version", "data_status", "admission_effect", "coverage_effect", "observations"}
            or declared["schema_version"] != "1.0.0"
            or declared["data_status"] != "BOUNDED_RENDERED_PRIMARY_EPISODE_METADATA_OBSERVATIONS"
            or declared["admission_effect"] != "NONE" or declared["coverage_effect"] != "NONE"
            or not isinstance(declared["observations"], list) or len(declared["observations"]) != 3):
        raise ValueError("unreviewed episode recheck envelope")
    source_rows = {row["row_id"]: row for row in catalog["rows"]}
    checked = {}
    for obs in declared["observations"]:
        if not isinstance(obs, dict) or set(obs) != EPISODE_KEYS:
            raise ValueError("malformed rendered official episode observation")
        ident = obs["row_id"]
        row = source_rows.get(ident)
        if (not row or ident in checked or row["medium"] != "EPISODE"
                or row["candidate_kind"] != "WIKIDATA_EPISODE" or row["context"] != "TOS"
                or row["source_group"] != "wikidata:wdqs"):
            raise ValueError("duplicate, non-TOS or non-episode recheck")
        parsed = urlsplit(obs["official_episode_url"])
        if (parsed.scheme != "https" or parsed.hostname != "www.paramountplus.com"
                or not re.fullmatch(r"/shows/video/[A-Za-z0-9]+/", parsed.path)
                or parsed.username or parsed.password or parsed.query or parsed.fragment):
            raise ValueError("official episode page must be an exact Paramount+ video locator")
        if (obs["observed_title"] != row["title"] or obs["observed_series"] != "Star Trek: The Original Series (Remastered)"
                or type(obs["observed_season"]) is not int or not 1 <= obs["observed_season"] <= 3
                or type(obs["observed_episode"]) is not int or not 1 <= obs["observed_episode"] <= 31
                or not isinstance(obs["observed_air_date"], str) or not AIR_DATE.fullmatch(obs["observed_air_date"])):
            raise ValueError("rendered official episode metadata invalid or title mismatch")
        expected_section = f'Paramount+ page heading: S{obs["observed_season"]} E{obs["observed_episode"]}: {obs["observed_title"]}'
        if (obs["evidence_locator"] != expected_section
                or obs["representation"] != "OFFICIAL_RENDERED_EPISODE_DETAILS"
                or obs["raw_body_sha256"] is not None
                or not isinstance(obs["observed_at_utc_date"], str)
                or not DATE.fullmatch(obs["observed_at_utc_date"])):
            raise ValueError("inconsistent/unpinned rendered official episode observation")
        synopsis = obs["original_synopsis"]
        if (not isinstance(synopsis, str) or not 35 <= len(synopsis) <= 360
                or "\n" in synopsis or not synopsis.endswith(".")
                or _normalized(synopsis) == _normalized(row["title"])):
            raise ValueError("invalid original short synopsis proposal")
        checked[ident] = obs
    return checked


def build(catalog: dict, catalog_bytes: bytes, declared: dict, episode_declared: dict) -> dict:
    if (catalog.get("data_status") != "DISCOVERY_ONLY" or catalog.get("coverage_effect") != "NONE"
            or catalog.get("admission_effect") != "NONE" or catalog.get("identity_scope") != "SOURCE_LOCAL_NOT_DEDUPLICATED"
            or catalog.get("denominator_status") != "NOT_ESTABLISHED"
            or not isinstance(catalog.get("rows"), list) or catalog.get("row_count") != len(catalog["rows"])
            or len(catalog["rows"]) != 1214):
        raise ValueError("source directory is not exact unadmitted 1,214-row accepted input")
    if any(row.get("source_group") not in FAMILIES or row.get("admission_effect") != "NONE"
           or row.get("coverage_effect") != "NONE" or row.get("verification_status") != "UNVERIFIED_METADATA"
           for row in catalog["rows"]):
        raise ValueError("unrecognized source lineage or promoted discovery row")
    ids = [row["row_id"] for row in catalog["rows"]]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate source-local row IDs")
    checked = _check_rechecks(catalog, declared)
    checked_episodes = _check_episode_rechecks(catalog, episode_declared)
    if set(checked).intersection(checked_episodes):
        raise ValueError("source row checked in mutually exclusive media tranches")
    groups: dict[str, list[str]] = defaultdict(list)
    for row in catalog["rows"]:
        groups[_sig(row)].append(row["row_id"])
    result = []
    for row in catalog["rows"]:
        ident = row["row_id"]
        obs = checked.get(ident)
        episode = checked_episodes.get(ident)
        group = sorted(groups[_sig(row)])
        has_check = obs is not None
        has_episode_check = episode is not None
        source_metadata_state = ("RENDERED_PUBLISHER_FIELDS_RECHECKED_UNPINNED" if has_check else
                                 "RENDERED_OFFICIAL_EPISODE_TITLE_SLOT_RECHECKED_UNPINNED" if has_episode_check else
                                 "NOT_RECHECKED")
        result.append({
            "row_id": ident,
            "source_local_title": row["title"],
            "medium": row["medium"],
            "candidate_kind": row["candidate_kind"],
            "source_locator": row["source_locator"],
            "source_input": row["source_input"],
            "source_group": row["source_group"],
            "provenance_family": FAMILIES[row["source_group"]],
            "row_payload_sha256": _row_hash(row),
            "duplicate_signature_sha256": _sig(row),
            "duplicate_source_local_row_ids": group if len(group) > 1 else [],
            "source_local_discovery_state": "CATALOGUED_METADATA_ONLY",
            "governed_research_coverage_state": "NOT_ADMITTED",
            "metadata_check_state": source_metadata_state,
            "verification_source_url": (obs["source_locator"] if has_check else
                                        episode["official_episode_url"] if has_episode_check else None),
            "verification_independence_family": (FAMILIES[row["source_group"]] if has_check else
                                                 "paramount_corporate_publisher_family" if has_episode_check else None),
            "field_checks": {
                "source_locator": "MATCHED_RENDERED_OFFICIAL_PAGE" if has_check else "NOT_RECHECKED",
                "title": "MATCHED_RENDERED_OFFICIAL_PAGE" if has_check or has_episode_check else "NOT_RECHECKED",
                "creator": "MATCHED_RENDERED_OFFICIAL_PAGE" if has_check else "NOT_RECHECKED",
                "edition_isbn": "MATCHED_RENDERED_OFFICIAL_PAGE" if has_check else "NOT_RECHECKED",
                "publisher": "MATCHED_RENDERED_OFFICIAL_PAGE" if has_check and obs["observed_publisher"] else "NOT_RECHECKED",
                "series": "OBSERVED_OFFICIAL_PAGE_NO_SOURCE_ROW_COMPARISON" if has_episode_check else "NOT_RECHECKED",
                "season_episode": "OBSERVED_OFFICIAL_PAGE_NO_SOURCE_ROW_COMPARISON" if has_episode_check else "NOT_RECHECKED",
                "air_date": "OBSERVED_OFFICIAL_PAGE_NO_SOURCE_ROW_COMPARISON" if has_episode_check else "NOT_RECHECKED",
            },
            "snapshot": {
                "observed_utc_date": (obs or episode)["observed_at_utc_date"] if has_check or has_episode_check else None,
                "representation": ("RENDERED_OFFICIAL_PRODUCT_PAGE_NOT_BYTE_CUSTODIED" if has_check else
                                   "RENDERED_OFFICIAL_EPISODE_PAGE_NOT_BYTE_CUSTODIED" if has_episode_check else
                                   "NO_FRESH_SOURCE_READ"),
                "raw_body_sha256": None,
                "section_locator": (obs or episode)["evidence_locator"] if has_check or has_episode_check else None,
            },
            "secondary_memory_alpha_crosswalk": "NOT_ASSESSED",
            "synopsis": {
                "status": "BLURB_GROUNDED_ORIGINAL_PARAPHRASE_DRAFT" if has_episode_check else "NOT_AUTHORED_SOURCE_NOT_READ",
                "original_text": episode["original_synopsis"] if has_episode_check else None,
                "basis": "OFFICIAL_EPISODE_PAGE_BRIEF_DESCRIPTION_ONLY" if has_episode_check else None,
                "grounding_url": episode["official_episode_url"] if has_episode_check else None,
                "human_review": "PENDING" if has_episode_check else "NOT_APPLICABLE",
                "does_not_assert_close_read": True,
            },
            "unresolved_reason": ("RAW_SOURCE_BYTES_NOT_CUSTODIED_AND_WORK_IDENTITY_UNRESOLVED" if has_check or has_episode_check
                                  else "PRIMARY_SOURCE_NOT_RECHECKED_AND_WORK_IDENTITY_UNRESOLVED"),
            "admission_effect": "NONE",
            "coverage_effect": "NONE",
        })
    duplicate_groups = [rows for rows in groups.values() if len(rows) > 1]
    counts = Counter(row["medium"] for row in catalog["rows"])
    lineage_counts = Counter(FAMILIES[row["source_group"]] for row in catalog["rows"])
    return {
        "schema_version": "1.0.0",
        "data_status": "PROPOSAL_ONLY_SOURCE_LOCAL_VERIFICATION_LEDGER",
        "source_directory_sha256": hashlib.sha256(catalog_bytes).hexdigest(),
        "source_recheck_observations_sha256": hashlib.sha256(
            json.dumps(declared, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "episode_recheck_observations_sha256": hashlib.sha256(
            json.dumps(episode_declared, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
        "denominator_status": "NOT_ESTABLISHED",
        "summary": {
            "source_local_rows": len(result),
            "rendered_primary_metadata_rechecks": len(checked) + len(checked_episodes),
            "rendered_publisher_metadata_rechecks": len(checked),
            "rendered_episode_title_slot_rechecks": len(checked_episodes),
            "not_rechecked": len(result) - len(checked) - len(checked_episodes),
            "raw_source_bodies_newly_pinned": 0,
            "governed_works_or_evidence_admitted": 0,
            "duplicate_signature_groups": len(duplicate_groups),
            "rows_in_duplicate_signature_groups": sum(len(rows) for rows in duplicate_groups),
            "counts_by_medium": dict(sorted(counts.items())),
            "counts_by_provenance_family": dict(sorted(lineage_counts.items())),
        },
        "rows": result,
    }


def next_batch(ledger: dict, catalog: dict, requested: int) -> dict:
    """Deterministic explicit work queue, not an assertion that a page was fetched."""
    if not 1 <= requested <= 50:
        raise ValueError("bounded metadata verification queue requires 1..50 rows")
    pending = [row for row in ledger["rows"]
               if row["metadata_check_state"] == "NOT_RECHECKED"]
    # Prioritize initial Wikidata episode leads before other metadata. The
    # accepted discovery row order is stable and is never silently deduped.
    ranked = sorted(pending, key=lambda row: (
        0 if row["medium"] == "EPISODE" and row["source_group"] == "wikidata:wdqs" else 1,
        0 if row["medium"] == "EPISODE" else 1,
        row["row_id"],
    ))
    contexts = {row["row_id"]: row["context"] for row in catalog["rows"]}
    return {
        "schema_version": "1.0.0",
        "data_status": "PENDING_PRIMARY_SOURCE_RECHECK_QUEUE_ONLY",
        "source_directory_sha256": ledger["source_directory_sha256"],
        "processed": 0,
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
        "pending_total": len(pending),
        "requested_limit": requested,
        "rows": [{
            "row_id": row["row_id"],
            "title": row["source_local_title"],
            "context": contexts[row["row_id"]],
            "source_locator": row["source_locator"],
            "source_group": row["source_group"],
            "provenance_family": row["provenance_family"],
            "verification_requirement": (
                "ACTUALLY_READ_OFFICIAL_EPISODE_TITLE_AND_SEASON_EPISODE_SAME_CARD_OR_DETAIL_PAGE"
                if row["medium"] == "EPISODE" else
                "ACTUALLY_READ_OFFICIAL_EXACT_TITLE_EDITION_CREATOR_METADATA"
            ),
            "result": "PENDING",
        } for row in ranked[:requested]],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="verify committed derivative is exactly reproducible")
    group.add_argument("--queue-next", type=int, metavar="N", help="print next 1..50 unverified rows (JSON); no fetch")
    args = parser.parse_args()
    catalog, raw = _read_json(CATALOG)
    declared, _ = _read_json(RECHECKS)
    episode_declared, _ = _read_json(EPISODE_RECHECKS)
    ledger = build(catalog, raw, declared, episode_declared)
    if args.queue_next is not None:
        print(json.dumps(next_batch(ledger, catalog, args.queue_next), ensure_ascii=False, sort_keys=True, indent=2))
        return
    encoded = (json.dumps(ledger, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    target = ROOT / OUTPUT
    if args.check:
        if not target.is_file() or target.is_symlink() or target.read_bytes() != encoded:
            raise SystemExit("VERIFICATION_LEDGER_STALE_OR_MUTATED")
    else:
        if target.is_symlink():
            raise SystemExit("VERIFICATION_LEDGER_OUTPUT_SYMLINK_REFUSED")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
    s = ledger["summary"]
    print(f"VERIFICATION_LEDGER_OK: {s['source_local_rows']} source-local rows, "
          f"{s['rendered_primary_metadata_rechecks']} rendered-source metadata rechecks, "
          f"{s['not_rechecked']} pending, {s['duplicate_signature_groups']} duplicate-signature groups; "
          "zero admission")


if __name__ == "__main__":
    main()
