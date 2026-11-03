"""Validate six source-local S&S observations; no accepted literary research."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PICARD_SOURCE = ROOT / "proposals/librarian/picard-companion-editions-20261103/records.json"
PINNED_SHA256 = "a2e3fb75419559fde85ec5341bcc30823172b65d1bad20d2a4fe863e5ac81f3f"

raw = (HERE / "observations.json").read_bytes()
if hashlib.sha256(raw).hexdigest() != PINNED_SHA256:
    raise ValueError("publisher Work observations changed without review")
EXPECTED = json.loads(raw)

# Known earlier nine Work-level synopsis candidates from #261 and #266;
# this is a de-duplication fence, not a claim of complete literary catalog coverage.
PRIOR_NINE = {
    ("Star Trek: Picard", "Star Trek: Picard: Second Self"),
    ("Star Trek: Strange New Worlds", "Star Trek: Strange New Worlds: The High Country"),
    ("Star Trek: Discovery", "Star Trek: Discovery: The Enterprise War"),
    ("Star Trek: Strange New Worlds", "Star Trek: Strange New Worlds: Ring of Fire"),
    ("Star Trek Autobiographies", "The Autobiography of James T. Kirk"),
    ("Star Trek Autobiographies", "The Autobiography of Jean-Luc Picard"),
    ("Star Trek Autobiographies", "The Autobiography of Kathryn Janeway"),
    ("Star Trek Autobiographies", "The Autobiography of Mr. Spock"),
    ("Star Trek Autobiographies", "The Autobiography of Benjamin Sisko"),
}


def isbn13_valid(value):
    if not isinstance(value, str) or len(value) != 13 or not value.isdigit():
        return False
    result = sum((1 if i % 2 == 0 else 3) * int(char) for i, char in enumerate(value[:12]))
    return (10 - result % 10) % 10 == int(value[-1])


def validate(data, picard_source=None):
    if not isinstance(data, dict) or set(data) != set(EXPECTED):
        raise ValueError("source-local schema field drift")
    for field, expected in EXPECTED.items():
        if type(data[field]) is not type(expected) or data[field] != expected:
            raise ValueError(f"source-local observation changed: {field}")
    if data["schema_version"] != "trek-lit-six-sns-work-discovery-v1" or data["proposal_only"] is not True:
        raise ValueError("schema or proposal status changed")
    if data["verification_class"] != "DIRECT_PUBLISHER_EDITION_METADATA_AND_PROMOTIONAL_DESCRIPTION":
        raise ValueError("verification class overclaim")
    if data["independence_group"] != "publisher:simonandschuster.com" or data["distinct_upstream_sources"] != 1:
        raise ValueError("source independence inflation")
    for field in ("accepted_source_work_effect", "accepted_coverage_effect", "accepted_evidence_effect"):
        if data[field] != "NONE":
            raise ValueError("unauthorized admission")
    for field in ("source_bound", "full_text_available", "structurally_indexed", "close_read", "semantically_analyzed", "artwork_display_rights_verified", "publisher_edition_family_complete"):
        if data[field] is not False:
            raise ValueError("unsupported coverage or rights qualification")
    if (data["candidate_work_count"], data["edition_page_count"], data["synopsis_count"]) != (6, 6, 6):
        raise ValueError("Work/edition/synopsis count mismatch")

    picard_source = picard_source if picard_source is not None else json.loads(PICARD_SOURCE.read_text(encoding="utf-8"))
    if picard_source.get("proposal_only") is not True:
        raise ValueError("Picard Librarian source unexpectedly accepted")
    known_sources = {s["provider_metadata"]["isbn13"]: s for s in picard_source["sources"]}
    known_works = {w["work_id"]: w for w in picard_source["works"]}
    if len(known_sources) != 3 or len(known_works) != 3:
        raise ValueError("Picard discovery source shape drift")

    rows = data["candidate_works"]
    fields = {"candidate_id", "title", "creator", "series", "format", "isbn13", "imprint", "publisher_publication_date", "publisher_extent", "publisher_url", "existing_librarian_candidate_id", "observation_verdict", "synopsis_status", "synopsis"}
    if len(rows) != 6 or len({x["candidate_id"] for x in rows}) != 6 or len({x["isbn13"] for x in rows}) != 6:
        raise ValueError("duplicate or missing candidate Work")
    pairs = {(x["series"], x["title"]) for x in rows}
    if len(pairs) != 6 or pairs.intersection(PRIOR_NINE):
        raise ValueError("duplicate prior nine Work titles")
    known_count = 0
    for row in rows:
        if set(row) != fields or not isbn13_valid(row["isbn13"]):
            raise ValueError("candidate fields/ISBN malformed")
        if row["format"] != "TRADE_PAPERBACK" or row["imprint"] != "Pocket Books/Star Trek":
            raise ValueError("wrong publisher edition")
        if row["observation_verdict"] != "DIRECT_PAGE_EDITION_FIELDS_VERIFIED" or row["synopsis_status"] != "PUBLISHER_DESCRIPTION_PARAPHRASE":
            raise ValueError("publisher metadata/synopsis promoted")
        if not isinstance(row["synopsis"], str) or not 18 <= len(row["synopsis"].split()) <= 60:
            raise ValueError("missing or overlong original synopsis")
        if not row["publisher_url"].startswith("https://www.simonandschuster.com/books/") or not row["publisher_url"].endswith("/" + row["isbn13"]):
            raise ValueError("publisher ISBN locator mismatch")
        existing_id = row["existing_librarian_candidate_id"]
        if existing_id is not None:
            known_count += 1
            source = known_sources.get(row["isbn13"])
            known = known_works.get(existing_id)
            if not source or not known or source["provider_metadata"]["title"] != row["title"] or known["title"] != row["title"]:
                raise ValueError("known Picard Work binding mismatch")
            metadata = source["provider_metadata"]
            if row["creator"] != metadata["creator"] or row["format"] != metadata["format"] or row["publisher_publication_date"] != metadata["publication_date"] or row["publisher_extent"] != f'{metadata["length_pages"]} pages' or row["publisher_url"] != source["locator"]:
                raise ValueError("known Picard edition fields mismatch")
        elif not row["candidate_id"].startswith("lit-source-local-sns-") or row["isbn13"] in known_sources:
            raise ValueError("unreconciled or duplicate source-local identity")
    if known_count != 2:
        raise ValueError("known Picard discovery candidate count changed")
    return True


if __name__ == "__main__":
    validate(EXPECTED)
    print("Six distinct official publisher candidate Works; no accepted book-text admission")
