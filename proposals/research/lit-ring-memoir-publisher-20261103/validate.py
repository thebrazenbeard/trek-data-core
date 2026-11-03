"""Validate one six-Work publisher/distributor observation, not source-book research."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RING_SOURCE = ROOT / "proposals/librarian/ring-of-fire-editions-20261102/records.json"
PRH_SOURCE = ROOT / "proposals/librarian/prh-star-trek-autobiographies-20261103/records.json"
PINNED_OBSERVATIONS_SHA256 = "9fb292b443ddaa2f332568981e4a6629f43bfa7b31fc7d58687be90d432a9514"

raw = (HERE / "observations.json").read_bytes()
if hashlib.sha256(raw).hexdigest() != PINNED_OBSERVATIONS_SHA256:
    raise ValueError("publisher observation raw bytes drifted without review")
EXPECTED = json.loads(raw)


def isbn13_valid(value):
    if not isinstance(value, str) or len(value) != 13 or not value.isdigit():
        return False
    checksum = sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(value[:12]))
    return (10 - checksum % 10) % 10 == int(value[-1])


def validate(data, ring_source=None, prh_source=None):
    if not isinstance(data, dict) or set(data) != set(EXPECTED):
        raise ValueError("observation field set drift")
    for k, expected in EXPECTED.items():
        if type(data[k]) is not type(expected) or data[k] != expected:
            raise ValueError(f"unreviewed observation change: {k}")
    if data["schema_version"] != "trek-lit-publisher-observation-v2" or data["proposal_only"] is not True:
        raise ValueError("unreviewed schema or proposal status")
    if data["verification_class"] != "DIRECT_OFFICIAL_PUBLISHER_OR_DISTRIBUTOR_PAGE_FIELDS_ONLY":
        raise ValueError("observation tier promotion")
    if data["distinct_upstream_lineages"] != 2 or data["source_lineages"] != [
        "publisher:simonandschuster.com", "distributor:penguinrandomhouse.com:titan-books"
    ]:
        raise ValueError("source lineage miscount")
    for field in ("accepted_source_binding_effect", "accepted_work_effect", "accepted_evidence_effect", "accepted_coverage_effect"):
        if data[field] != "NONE":
            raise ValueError("unauthorized accepted state")
    for field in ("source_bound", "full_text_available", "full_text_read", "semantic_close_read", "edition_family_completeness_verified", "artwork_display_rights_verified"):
        if data[field] is not False:
            raise ValueError("unsupported coverage or rights claim")

    ring_source = ring_source if ring_source is not None else json.loads(RING_SOURCE.read_text(encoding="utf-8"))
    prh_source = prh_source if prh_source is not None else json.loads(PRH_SOURCE.read_text(encoding="utf-8"))
    if ring_source.get("proposal_only") is not True or prh_source.get("proposal_only") is not True:
        raise ValueError("Librarian source unexpectedly accepted")
    ring_work = ring_source["work"]
    ring_by_isbn = {e["isbn13"]: e for e in ring_source["edition_candidates"]}
    ring_urls = {s["source_id"]: s["locator"] for s in ring_source["sources"]}
    prh_works = {w["work_id"]: w for w in prh_source["works"]}
    prh_by_isbn = {e["isbn13"]: e for e in prh_source["edition_candidates"]}
    prh_urls = {s["source_id"]: s["locator"] for s in prh_source["sources"]}
    if len(ring_by_isbn) != 4 or len(prh_by_isbn) != 5 or len(prh_works) != 5:
        raise ValueError("Librarian discovery candidate count drift")

    records = data["records"]
    if data["verified_candidate_work_count"] != 6 or data["verified_edition_page_count"] != 9:
        raise ValueError("count field drift")
    if len(records) != 9 or len({row["isbn13"] for row in records}) != 9:
        raise ValueError("edition count mismatch or duplicate")
    by_work = {}
    for row in records:
        if set(row) != {"candidate_work_id", "title", "creator", "isbn13", "format", "publisher_imprint", "publication_date", "publisher_extent", "narrator", "publisher_url", "field_verdict"}:
            raise ValueError("edition field set drift")
        if not isbn13_valid(row["isbn13"]) or row["field_verdict"] != "DIRECT_PAGE_FIELDS_MATCH":
            raise ValueError("ISBN check failure or unverified fields")
        by_work.setdefault(row["candidate_work_id"], set()).add(row["isbn13"])
        if row["candidate_work_id"] == ring_work["work_id"]:
            edition = ring_by_isbn.get(row["isbn13"])
            url = ring_urls.get(edition["source_id"]) if edition else None
            if not edition or row["title"] != ring_work["title"] or row["creator"] != ring_work["creator"]:
                raise ValueError("Ring of Fire Work or ISBN identity mismatch")
            if row["format"] != edition["format"] or row["publisher_url"] != url:
                raise ValueError("Ring of Fire edition mapping mismatch")
            if not row["publisher_url"].startswith("https://www.simonandschuster.com/books/") or not row["publisher_url"].endswith("/" + row["isbn13"]):
                raise ValueError("Ring of Fire publisher ISBN locator mismatch")
        else:
            work = prh_works.get(row["candidate_work_id"])
            edition = prh_by_isbn.get(row["isbn13"])
            url = prh_urls.get(edition["source_id"]) if edition else None
            if not work or not edition or edition["work_id"] != row["candidate_work_id"]:
                raise ValueError("PRH Work or edition identity mismatch")
            if row["title"] != work["title"] or row["creator"] != work["creator"]:
                raise ValueError("PRH creator/title mismatch")
            if row["format"] != edition["format"] or row["publication_date"] != edition["publication_date"] or row["publisher_url"] != url:
                raise ValueError("PRH edition mismatch")
            if row["publisher_imprint"] != "Titan Books" or not row["publisher_url"].startswith("https://www.penguinrandomhouse.com/books/"):
                raise ValueError("PRH imprint or distributor locator mismatch")
    if len(by_work) != 6 or by_work[ring_work["work_id"]] != set(ring_by_isbn):
        raise ValueError("Ring of Fire formats or Works incomplete")
    if any(by_work.get(wid) != {prh_by_isbn[i]["isbn13"] for i in prh_by_isbn if prh_by_isbn[i]["work_id"] == wid} for wid in prh_works):
        raise ValueError("PRH Work editions incomplete")

    synopses = data["work_synopses"]
    if len(synopses) != 6 or {s["candidate_work_id"] for s in synopses} != set(by_work):
        raise ValueError("one synopsis per Work required")
    bound_urls = {(r["candidate_work_id"], r["publisher_url"]) for r in records}
    for s in synopses:
        if set(s) != {"candidate_work_id", "status", "source_kind", "source_locator", "synopsis"}:
            raise ValueError("synopsis field set drift")
        if s["status"] != "PUBLISHER_DESCRIPTION_PARAPHRASE":
            raise ValueError("publisher synopsis falsely promoted to book text")
        if (s["candidate_work_id"], s["source_locator"]) not in bound_urls:
            raise ValueError("synopsis source is not tied to Work's edition")
        expected_kind = "OFFICIAL_PUBLISHER_PROMOTIONAL_COPY_NOT_BOOK_TEXT" if s["candidate_work_id"] == ring_work["work_id"] else "OFFICIAL_DISTRIBUTOR_PROMOTIONAL_COPY_NOT_BOOK_TEXT"
        if s["source_kind"] != expected_kind or not 15 <= len(s["synopsis"].split()) <= 65:
            raise ValueError("synopsis provenance/length mismatch")
    return True


if __name__ == "__main__":
    validate(EXPECTED)
    print("Nine official edition pages and six source-labeled paraphrases; no accepted book research")
