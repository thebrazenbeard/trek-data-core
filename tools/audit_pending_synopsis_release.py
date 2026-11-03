#!/usr/bin/env python3
"""Read-only status adapter for held literary and Scouts publisher descriptions.

This adapter emits *no* public sidecar or synopsis text. A separate, reviewed
code-pinned receipt and Director release remain prerequisites to any future
display compiler change. A self-declared review JSON cannot release itself.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


class FrontierError(ValueError):
    pass


def _module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lit_request = _module("lit_expansion_request", "tools/build_lit_overview_expansion_request.py")
publisher = _module("publisher_overview_release", "tools/build_publisher_synopsis_release.py")
short_publisher = _module("short_publisher_overview_release", "tools/build_short_publisher_overview_release.py")
scouts_first = _module("scouts_asteroid_01to05", "proposals/research/short/scouts-asteroid-descriptions-20261103/validate.py")
scouts_second = _module("scouts_asteroid_06to10", "proposals/research/short/scouts-asteroid-06to10-descriptions-20261103/validate.py")

# No reviewer-owned, independently qualified receipt is pinned for either
# pending tranche. Adding a file alone MUST NOT affect release eligibility.
REVIEW_RECEIPTS = {
    "literature": "proposals/reviews/lit-overview-expansion-20261103/receipt.json",
    "scouts": "proposals/reviews/scouts-asteroid-descriptions-20261103/receipt.json",
}
ACCEPTED_REVIEW_DIGESTS = {"literature": None, "scouts": None}


def _expected_review_rows(lane: str, request: dict, first: dict, second: dict) -> list[dict]:
    if lane == "literature":
        return sorted(({
            "source_row_id": candidate["candidate_work_id"],
            "source_locator": candidate["overview_evidence_url"],
            "observation_sha256": candidate["observation_sha256"],
            "paraphrase_sha256": candidate["original_paraphrase_sha256"],
        } for candidate in request["candidates"]), key=lambda row: row["source_row_id"])
    if lane != "scouts":
        raise FrontierError("Unknown review lane")
    return sorted(({
        "source_row_id": row["directory_row_id"],
        "source_locator": row["youtube_video_locator"],
        "observation_sha256": hashlib.sha256(raw).hexdigest(),
        "paraphrase_sha256": hashlib.sha256(row["synopsis"].encode("utf-8")).hexdigest(),
    } for packet, raw in ((first, scouts_first.OBSERVATIONS.read_bytes()),
                          (second, scouts_second.OBSERVATIONS.read_bytes()))
    for row in packet["description_paraphrases"]), key=lambda row: row["source_row_id"])


def validate_review_receipt(lane: str, receipt: object, expected: list[dict], request_sha256: str) -> None:
    keys = {"schema_version", "review_kind", "review_result", "reviewed_on_utc", "reviewer_agent",
            "provider", "runtime", "separate_author_review", "review_request_sha256",
            "reviewed_entry_count", "reviewed_entries", "source_review_method",
            "material_qualifications", "source_work_effect", "coverage_effect",
            "artwork_effect", "site_effect"}
    if not isinstance(receipt, dict) or set(receipt) != keys or \
       receipt["schema_version"] != "1.0.0" or \
       receipt["review_kind"] != "SEPARATE_MODEL_EDITORIAL_REVIEW" or \
       receipt["review_result"] != "PASS_SOURCE_LABELED_PARAPHRASES_DISPLAY_ONLY" or \
       receipt["separate_author_review"] is not True or \
       not isinstance(receipt["reviewer_agent"], str) or not receipt["reviewer_agent"].strip() or \
       not isinstance(receipt["provider"], str) or not receipt["provider"].strip() or \
       not isinstance(receipt["runtime"], str) or not receipt["runtime"].strip() or \
       re.fullmatch(r"20\d\d-\d\d-\d\d", str(receipt["reviewed_on_utc"])) is None or \
       receipt["review_request_sha256"] != request_sha256 or \
       receipt["reviewed_entry_count"] != len(expected) or \
       receipt["reviewed_entries"] != expected or \
       receipt["source_review_method"] != "RENDERED_FIRST_PARTY_DESCRIPTION_CHECK_NOT_FULL_WORK_READ" or \
       not isinstance(receipt["material_qualifications"], list) or \
       len(receipt["material_qualifications"]) < 2 or \
       any(not isinstance(x, str) or not x.strip() for x in receipt["material_qualifications"]) or \
       any(receipt[k] != "NONE" for k in ("source_work_effect", "coverage_effect", "artwork_effect", "site_effect")):
        raise FrontierError(f"Unqualified {lane} independent editorial receipt claim")


def _unique_object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise FrontierError("Duplicate review receipt JSON key")
        result[key] = value
    return result


def receipt_state(lane: str, expected_rows: list[dict], request_sha256: str) -> str:
    path = ROOT / REVIEW_RECEIPTS[lane]
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
        raise FrontierError(f"Symlink reviewer receipt refused for {lane}")
    if not path.is_file():
        return "ABSENT"
    pinned_digest = ACCEPTED_REVIEW_DIGESTS[lane]
    if pinned_digest is None:
        return "UNPINNED_REVIEW_CLAIM"
    if not isinstance(pinned_digest, str) or len(pinned_digest) != 64 or any(c not in "0123456789abcdef" for c in pinned_digest):
        raise FrontierError("Invalid trusted reviewer digest pin")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != pinned_digest:
        raise FrontierError(f"Reviewer receipt bytes drifted for {lane}")
    try:
        receipt = json.loads(raw, object_pairs_hook=_unique_object_pairs)
    except (ValueError, TypeError, UnicodeDecodeError) as error:
        raise FrontierError(f"Unparseable reviewer receipt for {lane}") from error
    validate_review_receipt(lane, receipt, expected_rows, request_sha256)
    # A matching hash proves only that a reviewed artifact was pinned by code;
    # it does not independently authenticate a human or model identity.
    return "CODE_PINNED_REVIEW_RECEIPT_NOT_RELEASE_AUTHORIZATION"


def report() -> dict:
    try:
        request = lit_request.build()
        if lit_request._read(lit_request.OUTPUT) != lit_request._render(request):
            raise FrontierError("Literary review request no longer matches accepted observations")
        directory = lit_request._json("explorer/discovery-catalog.json")
        if directory.get("row_count") != 1214 or len(directory.get("rows", [])) != 1214:
            raise FrontierError("Unqualified accepted directory snapshot")
        directory_by_id = {row["row_id"]: row for row in directory["rows"]}
        if len(directory_by_id) != len(directory["rows"]):
            raise FrontierError("Duplicate accepted source-local directory identity")

        candidates = request["candidates"]
        literary_matches = 0
        for candidate in candidates:
            row = directory_by_id.get(candidate["proposed_directory_row_id"])
            if row is None:
                continue
            if (row["medium"] != "LITERATURE" or row["candidate_kind"] != "NOVEL" or
                    row["source_group"] != "publisher:simonandschuster.com" or
                    row["source_locator"] != candidate["publisher_edition_url"] or
                    row["title"] != candidate["title"] or
                    row["admission_effect"] != "NONE" or row["coverage_effect"] != "NONE"):
                raise FrontierError("Literary candidate directory crosswalk conflicts with publisher observation")
            literary_matches += 1

        first = scouts_first.read_pinned()
        second = scouts_second.read_pinned()
        count_first = scouts_first.validate(first, directory)
        count_second = scouts_second.validate(second, directory)
        if count_first != 5 or count_second != 5:
            raise FrontierError("Scouts description observation count drift")

        reviewed_candidates = publisher.candidate_entries()
        existing_request = publisher.review_request(reviewed_candidates)
        existing_release = publisher.public_release(
            reviewed_candidates, publisher._load(publisher.REVIEW_PATH), existing_request
        )
        if publisher._raw(publisher.PUBLIC_PATH) != publisher._pretty(existing_release) or existing_release["synopsis_count"] != 23:
            raise FrontierError("Accepted 23-entry review display projection is stale")
        short_release = short_publisher.build()
        short_encoded = (json.dumps(short_release, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        short_path = ROOT / short_publisher.OUTPUT
        if (short_path.is_symlink() or not short_path.is_file() or short_path.read_bytes() != short_encoded or
                short_release["synopsis_count"] != 14 or
                any(row["row_id"].startswith("directory:short:scouts:") for row in short_release["synopses"])):
            raise FrontierError("Accepted 14-entry Short Treks/Very Short Treks release is stale or reclassified as Scouts")
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        raise FrontierError(str(error)) from error

    lit_expected = _expected_review_rows("literature", request, first, second)
    scouts_expected = _expected_review_rows("scouts", request, first, second)
    lit_receipt = receipt_state("literature", lit_expected, hashlib.sha256(lit_request._read(lit_request.OUTPUT)).hexdigest())
    scouts_request_hash = hashlib.sha256(json.dumps(scouts_expected, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    scouts_receipt = receipt_state("scouts", scouts_expected, scouts_request_hash)
    literature_blockers = []
    scouts_blockers = []
    if literary_matches != 18:
        literature_blockers.append("DIRECTORY_ROW_ACCEPTANCE_REQUIRED")
    if lit_receipt != "CODE_PINNED_REVIEW_RECEIPT_NOT_RELEASE_AUTHORIZATION":
        literature_blockers.append("INDEPENDENT_EDITORIAL_RECEIPT_REQUIRED")
    # These source observations were obtained through YouTube search-result
    # description snippets; neither video page nor animation was opened.
    scouts_blockers.append("FULL_SOURCE_PAGE_OBSERVATION_REQUIRED")
    if scouts_receipt != "CODE_PINNED_REVIEW_RECEIPT_NOT_RELEASE_AUTHORIZATION":
        scouts_blockers.append("INDEPENDENT_EDITORIAL_RECEIPT_REQUIRED")

    status = "PROPOSAL_RELEASE_HELD" if literature_blockers or scouts_blockers else "READY_FOR_SEPARATE_DIRECTOR_REVIEW"
    return {
        "schema_version": "1.0.0", "data_status": status,
        "accepted_directory_rows": directory["row_count"],
        "accepted_display_overviews": existing_release["synopsis_count"] + short_release["synopsis_count"],
        "accepted_display_overviews_by_medium": {"FILM": 14, "LITERATURE": 9, "SHORT_FORM": 14},
        "literature": {
            "source_local_candidates": len(candidates), "source_upstream_families": request["independent_source_count"],
            "accepted_directory_matches": literary_matches, "editorial_receipt_state": lit_receipt,
            "blockers": literature_blockers,
        },
        "scouts": {
            "source_description_observations": count_first + count_second,
            "accepted_directory_matches": count_first + count_second,
            "opened_source_pages": 0, "editorial_receipt_state": scouts_receipt,
            "blockers": scouts_blockers,
        },
        "coverage_effect": "NONE", "admission_effect": "NONE",
        "public_release_effect": "NONE", "artwork_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ready", action="store_true", help="Exit 2 unless all documentary prerequisites exist")
    args = parser.parse_args()
    result = report()
    print(json.dumps(result, sort_keys=True, indent=2))
    if args.require_ready and result["data_status"] != "READY_FOR_SEPARATE_DIRECTOR_REVIEW":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
