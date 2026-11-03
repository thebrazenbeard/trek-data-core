#!/usr/bin/env python3
"""Fail-closed validation for an append-only publisher-modality correction."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORRECTION = HERE / "records.json"
SOURCE = HERE.parent / "lit-three-publisher-overviews-20261103" / "observations.json"
SOURCE_SHA = "3989c480061492453b2b905c14e2b1b61014f9d379d9b0e8ea0d7afe3019f85f"
EXPECTED_FIELDS = {
    "schema_version", "proposal_only", "observed_on_utc", "correction_id",
    "superseded_source_path", "superseded_source_sha256", "superseded_candidate_id",
    "superseded_field", "publisher_title", "publisher_creator", "publisher_edition_isbn13",
    "official_publisher_url", "source_reader", "source_independence_group", "source_issue",
    "source_assertion_scope", "replacement_original_overview", "source_relative_tags",
    "global_work_identity_effect", "accepted_evidence_effect", "coverage_effect",
    "public_synopsis_effect", "image_or_ebook_bytes_retrieved", "publisher_html_sha256",
    "close_read",
}
EXPECTED_OLD = (
    "The publisher follows a Voyager fleet survey of former Borg-controlled regions in the Delta Quadrant. "
    "As the vessels investigate, Fleet Commander Afsarah Eden experiences further clues to her obscured origins, "
    "while an unnamed but significant Starfleet figure's anticipated return raises the stakes."
)


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def validate(value: object, old: object) -> None:
    require(type(value) is dict and set(value) == EXPECTED_FIELDS, "correction schema drift")
    require(value["schema_version"] == "trek-lit-source-local-correction-v1", "schema version")
    require(value["proposal_only"] is True, "must remain a proposal")
    require(value["observed_on_utc"] == "2026-11-03", "observation date")
    require(value["superseded_source_sha256"] == SOURCE_SHA, "wrong source artifact hash")
    require(value["superseded_source_path"] == "proposals/research/lit-three-publisher-overviews-20261103/observations.json", "wrong source artifact")
    require(value["superseded_candidate_id"] == "lit-source-local-sns-voy-eternal-tide-20261103", "wrong source candidate")
    require(value["superseded_field"] == "original_overview", "wrong corrected field")
    require(value["publisher_title"] == "The Eternal Tide" and value["publisher_creator"] == "Kirsten Beyer", "publisher title/creator mismatch")
    require(value["publisher_edition_isbn13"] == "9781668288559", "edition binding mismatch")
    require(value["official_publisher_url"] == "https://www.simonandschuster.com/books/The-Eternal-Tide/Kirsten-Beyer/Star-Trek-Voyager/9781668288559", "source URL mismatch")
    require(value["source_reader"] == "DIRECT_RENDERED_FIRST_PARTY_ABOUT_THE_BOOK_NO_RAW_HTML_CUSTODY", "source tier drift")
    require(value["source_independence_group"] == "publisher:simonandschuster.com", "lineage drift")
    require(value["source_assertion_scope"] == "PUBLISHER_DESCRIPTION_NOT_VERIFIED_BOOK_EVENTS", "fiction truth promotion")
    original = next((x for x in old["candidates"] if x.get("candidate_id") == value["superseded_candidate_id"]), None)
    require(original is not None and original.get("original_overview") == EXPECTED_OLD, "superseded source candidate has changed")
    text = value["replacement_original_overview"]
    require(type(text) is str and 100 <= len(text) <= 600, "invalid corrected paraphrase")
    lowered = text.casefold()
    require("unexpected return" in lowered and "unforeseen by the fleet" in lowered, "publisher uncertainty missing")
    require(not re.search(r"\b(anticipated|expected|foreseen|predicted)\s+return\b", lowered), "modal inversion")
    require("afsarah eden" in lowered and "delta quadrant" in lowered, "source context lost")
    require("who returns" not in lowered, "invented returning identity")
    require(value["source_relative_tags"] == [
        "series:star-trek-voyager", "setting:delta-quadrant", "context:former-borg-sectors",
        "character:afsarah-eden", "plot:unexpected-starfleet-leader-return",
    ], "unsupported or changed source-relative tags")
    for key in ("global_work_identity_effect", "accepted_evidence_effect", "coverage_effect", "public_synopsis_effect"):
        require(value[key] == "NONE", f"protected effect: {key}")
    require(value["publisher_html_sha256"] is None and value["image_or_ebook_bytes_retrieved"] is False and value["close_read"] is False, "unsupported custody/read claim")


def main() -> None:
    raw = SOURCE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA, "accepted source artifact bytes changed")
    validate(json.loads(CORRECTION.read_text(encoding="utf-8")), json.loads(raw))
    print("PASS: one append-only correction, modal inversion barred, zero protected effects")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
