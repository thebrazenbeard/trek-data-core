#!/usr/bin/env python3
"""Gate 14 original SHORT_FORM publisher overviews on a separate model review receipt.

This optional sidecar augments, but does not rewrite, 23 already approved
film/literature descriptions. No video close-read, admitted Work, or raw page.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_short_publisher_overview_request import ROOT, OUTPUT as REQUEST, build as request_build, read

REVIEW = Path("proposals/reviews/model-editorial-short-overviews-20261103/receipt.json")
OUTPUT = Path("explorer/short-synopsis-catalog.json")
PINNED_REVIEW_SHA256 = "2d36e659830814d81b534df208bab2975766ca11310c67da558996a399708768"
PINNED_REQUEST_SHA256 = "29a79c1fe518077f290e049c304c3117a50e8400d714e7e12e160ad1cf419aa7"
PINNED_REVIEWER_COMMIT = "3ccdbccada41544df7682605e6be856bcab80a0b"
PINNED_SOURCE_COMMIT = "2b39607c7f7bc5fb473d47f7f81a7939b5817b9c"
PINNED_REQUEST_COMMIT = "9064848ab408dc4f53d8cf7868a30e4cd0102368"


def build() -> dict:
    request, raw_request = read(REQUEST)
    review, raw_review = read(REVIEW)
    actual_request = request_build()
    if request != actual_request or hashlib.sha256(raw_request).hexdigest() != PINNED_REQUEST_SHA256:
        raise ValueError("review request is not exact accepted observation-based work")
    if hashlib.sha256(raw_review).hexdigest() != PINNED_REVIEW_SHA256:
        raise ValueError("editorial review receipt bytes changed after independent model review")
    if (review.get("schema_version") != "1.0.0" or review.get("review_kind") != "MODEL_EDITORIAL_REVIEW" or
        review.get("review_result") != "PASS_14_ORIGINAL_PUBLISHER_PREMISE_PARAPHRASES_ONLY_WITH_ONE_NULL_HELD" or
        review.get("reviewed_candidate_head") != PINNED_REQUEST_COMMIT or
        review.get("accepted_source_state_commit") != PINNED_SOURCE_COMMIT or
        review.get("review_request_path") != REQUEST.as_posix() or
        review.get("review_request_sha256") != PINNED_REQUEST_SHA256 or
        review.get("reviewer_agent") != "/root/repo_workflow_merger_audit" or
        review.get("provider") != "OpenAI" or
        review.get("review_independence") != "SEPARATE_MODEL_AGENT_FROM_RESEARCH_AND_RELEASE_AUTHOR_NOT_EXTERNAL_OR_HUMAN" or
        review.get("reviewed_paraphrase_count") != 14 or review.get("passed_paraphrase_count") != 14 or
        review.get("failed_paraphrase_count") != 0 or review.get("held_null_plot_summary_count") != 1 or
        review.get("held_null_row_id") != "directory:short:very-short-treks-04" or
        any(review.get(k) != "NONE" for k in ("source_admission_effect", "work_admission_effect",
                                                  "evidence_admission_effect", "coverage_effect",
                                                  "artwork_release_effect", "site_release_effect"))):
        raise ValueError("model review receipt claims unauthorized independent/admitted scope")
    source_receipts = request["source_observations"]
    audited_artifacts = review.get("source_artifacts")
    if (not isinstance(audited_artifacts, list) or len(audited_artifacts) != 2 or
        [(row["path"], row["sha256"], row["reviewed_paraphrases"]) for row in audited_artifacts] !=
        [(source_receipts[0]["path"], source_receipts[0]["sha256"], 10),
         (source_receipts[1]["path"], source_receipts[1]["sha256"], 4)]):
        raise ValueError("independent reviewer source observation SHA tuple mismatch")
    target_hashes = [[r["row_id"], r["original_paraphrase_sha256"]] for r in request["entries"]]
    if review.get("reviewed_paraphrases") != target_hashes:
        raise ValueError("independent model reviewer did not approve exact 14 row/text SHA pairs")
    entries = []
    for row in request["entries"]:
        if row["full_video_viewed"] is not False or row["raw_webpage_sha256"] is not None:
            raise ValueError("source review cannot claim viewed footage or raw HTML custody")
        entries.append({
            "row_id": row["row_id"], "title": row["title"], "medium": "SHORT_FORM",
            "source_group": row["source_group"], "source_input": row["source_input"],
            "source_context": row["source_context"], "source_locator": row["source_locator"],
            "overview_evidence_locator": row["overview_evidence_locator"],
            "overview_text": row["overview_text"],
            "overview_basis": "PUBLISHER_DESCRIPTION_PARAPHRASE",
            "source_snapshot_date": row["source_snapshot_date"],
            "research_observation_path": row["research_observation_path"],
            "research_observation_sha256": row["research_observation_sha256"],
            "raw_webpage_sha256": None,
            "editorial_receipt_sha256": PINNED_REVIEW_SHA256,
            "directory_alias_row_id": None, "directory_alias_context": None,
            "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    if len(entries) != 14 or any(row["row_id"] == "directory:short:very-short-treks-04" for row in entries):
        raise ValueError("null-premise hold bypassed")
    return {
        "schema_version": "1.0.0", "data_status": "EDITORIALLY_REVIEWED_DISPLAY_ONLY",
        "coverage_effect": "NONE", "admission_effect": "NONE",
        "synopsis_count": len(entries), "synopses": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    out = build()
    encoded = (json.dumps(out, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()
    dest = ROOT / OUTPUT
    if args.check:
        if dest.is_symlink() or not dest.is_file() or dest.read_bytes() != encoded:
            raise SystemExit("SHORT_SYNOPSIS_RELEASE_MISSING_OR_TAMPERED")
    else:
        if dest.is_symlink():
            raise SystemExit("SHORT_SYNOPSIS_RELEASE_SYMLINK_REFUSED")
        dest.write_bytes(encoded)
    print("SHORT_PUBLISHER_OVERVIEW_RELEASE_OK: 14 internal-model-reviewed original short premises; "
          "one plot null held; 23 existing overviews untouched; 0 research admission")


if __name__ == "__main__":
    main()
