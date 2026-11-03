"""Validate six publisher-ledger observations; never qualify book text or cover art."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR_A = ROOT / "proposals/research/lit-three-publisher-editions-20261103/observations.json"
PRIOR_B = ROOT / "proposals/research/lit-ring-memoir-publisher-20261103/observations.json"
PRIOR_C = ROOT / "proposals/research/lit-six-next-publisher-works-20261103/observations.json"
PRIOR_SHA256 = (
    "908070be21a187c305b56f7aec880f30eb69cb2d12911f07663a4d2c3c616826",
    "9fb292b443ddaa2f332568981e4a6629f43bfa7b31fc7d58687be90d432a9514",
    "a2e3fb75419559fde85ec5341bcc30823172b65d1bad20d2a4fe863e5ac81f3f",
)
PINNED_SHA256 = "c25497a7b48482f6cceb21b55153dec55fbcf3ecf609a71ca116acf50ce8c533"

raw = (HERE / "observations.json").read_bytes()
if hashlib.sha256(raw).hexdigest() != PINNED_SHA256:
    raise ValueError("publisher and cover-locator observation bytes drifted")
EXPECTED = json.loads(raw)


def isbn13_valid(value):
    if not isinstance(value, str) or len(value) != 13 or not value.isdigit():
        return False
    check = sum((1 if i % 2 == 0 else 3) * int(char) for i, char in enumerate(value[:12]))
    return (10 - check % 10) % 10 == int(value[-1])


def prior_inventory(prior_a=None, prior_b=None, prior_c=None):
    expected = []
    for path, sha in zip((PRIOR_A, PRIOR_B, PRIOR_C), PRIOR_SHA256):
        prior_raw = path.read_bytes()
        if hashlib.sha256(prior_raw).hexdigest() != sha:
            raise ValueError("prior accepted publisher observation changed; redo deduplication")
        expected.append(json.loads(prior_raw))
    for supplied, original in zip((prior_a, prior_b, prior_c), expected):
        if supplied is not None and supplied != original:
            raise ValueError("prior Work candidate snapshot was tampered with")
    a, b, c = expected
    if any(p.get("proposal_only") is not True for p in (a, b, c)):
        raise ValueError("prior publisher proposal unexpectedly accepted")
    titles = [s["title"] for s in a["records"]] + [s["title"] for s in b["records"]] + [s["title"] for s in c["candidate_works"]]
    isbn = [s["isbn13"] for s in a["records"]] + [s["isbn13"] for s in b["records"]] + [s["isbn13"] for s in c["candidate_works"]]
    if len(set(titles)) != 15 or len(set(isbn)) != 24:
        raise ValueError("prior Work identity/edition snapshot changed; inspect reconciliation")
    return set(titles), set(isbn)


def validate_page_description_scope(rows):
    """Reject independently falsified synopsis claims absent from the cited publisher page.

    This is a scoped regression, not a substitute for publisher-page rereads.
    """
    picard = next((r for r in rows if r.get("isbn13") == "9781982142186"), None)
    if picard is None:
        raise ValueError("Last Best Hope source page missing")
    synopsis = picard["synopsis"].casefold()
    if any(unsupported in synopsis for unsupported in ("romulan", "supernova")):
        raise ValueError("Last Best Hope synopsis imports specifics absent from cited page")
    return True


def validate(data, prior_a=None, prior_b=None, prior_c=None):
    if not isinstance(data, dict) or set(data) != set(EXPECTED):
        raise ValueError("schema field set changed")
    for key, expected in EXPECTED.items():
        if type(data[key]) is not type(expected) or data[key] != expected:
            raise ValueError(f"publisher observation not reviewed: {key}")
    if data["schema_version"] != "trek-lit-six-era-sns-publisher-v1" or data["proposal_only"] is not True:
        raise ValueError("schema or proposed status drift")
    if data["verification_class"] != "DIRECT_OFFICIAL_PUBLISHER_PAGE_EDITION_METADATA_AND_DESCRIPTION":
        raise ValueError("source verification tier overclaim")
    if data["independence_group"] != "publisher:simonandschuster.com" or data["distinct_upstream_sources"] != 1:
        raise ValueError("publisher independence overcount")
    for key in ("accepted_source_work_effect", "accepted_coverage_effect", "accepted_evidence_effect"):
        if data[key] != "NONE":
            raise ValueError("unauthorized admission")
    for key in ("full_text_available", "source_bound", "structurally_indexed", "close_read", "semantically_analyzed", "artwork_display_rights_verified", "cover_image_bytes_retrieved", "publisher_edition_family_complete"):
        if data[key] is not False:
            raise ValueError("false content, art, or coverage qualification")
    if (data["candidate_work_count"], data["verified_edition_page_count"], data["source_labeled_synopsis_count"]) != (6, 6, 6):
        raise ValueError("Work/edition/synopsis count misreported")
    titles_before, isbn_before = prior_inventory(prior_a, prior_b, prior_c)

    rows = data["candidate_works"]
    required = {"candidate_id", "title", "creator", "series", "format", "isbn13", "imprint", "publisher_publication_date", "publisher_extent", "publisher_url", "synopsis_status", "synopsis", "cover_candidate_locator", "cover_locator_source", "cover_rights_status"}
    if len(rows) != 6 or len({r["candidate_id"] for r in rows}) != 6 or len({r["title"] for r in rows}) != 6 or len({r["isbn13"] for r in rows}) != 6:
        raise ValueError("duplicate candidate/Work/edition")
    if {r["title"] for r in rows} & titles_before or {r["isbn13"] for r in rows} & isbn_before:
        raise ValueError("duplicate previously proposed title or edition")
    validate_page_description_scope(rows)
    for row in rows:
        if set(row) != required or not isbn13_valid(row["isbn13"]):
            raise ValueError("invalid record fields/ISBN")
        if not row["candidate_id"].startswith("lit-source-local-sns-") or row["imprint"] != "Pocket Books/Star Trek":
            raise ValueError("unauthorized global identity or imprint")
        if row["format"] not in {"TRADE_PAPERBACK", "MASS_MARKET_PAPERBACK"}:
            raise ValueError("unverified edition format")
        if row["synopsis_status"] != "PUBLISHER_DESCRIPTION_PARAPHRASE" or not isinstance(row["synopsis"], str) or not 18 <= len(row["synopsis"].split()) <= 60:
            raise ValueError("unsupported synopsis or close-read promotion")
        if not row["publisher_url"].startswith("https://www.simonandschuster.com/books/") or not row["publisher_url"].endswith("/" + row["isbn13"]):
            raise ValueError("publisher edition locator not ISBN-specific")
        if row["cover_locator_source"] != "PUBLISHER_HIGH_RES_IMAGE_LINK" or row["cover_rights_status"] != "RIGHTS_UNVERIFIED_HOLD_NO_PUBLIC_DISPLAY":
            raise ValueError("unqualified cover image display")
        if not row["cover_candidate_locator"].startswith("https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr" + row["isbn13"] + "/") or not row["cover_candidate_locator"].endswith("-" + row["isbn13"] + "_hr.jpg"):
            raise ValueError("cover locator mismatch/unsafe host")
    return True


if __name__ == "__main__":
    validate(EXPECTED)
    print("Six new publisher descriptions and rights-held cover locators; zero accepted literary effects")
