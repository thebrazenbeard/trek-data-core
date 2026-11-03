"""Validate a source-local six-title publisher-description packet; no Source/Work admission."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PINNED_SHA256 = "a0d3aed8620c3202b44f0e29eae9b085e57887d3efa04b1b7b14a9433d33662e"
PRIOR_PATHS = (
    ROOT / "proposals/research/lit-three-publisher-editions-20261103/observations.json",
    ROOT / "proposals/research/lit-ring-memoir-publisher-20261103/observations.json",
    ROOT / "proposals/research/lit-six-next-publisher-works-20261103/observations.json",
    ROOT / "proposals/research/lit-six-era-publisher-20261103/observations.json",
)
PRIOR_SHA256 = (
    "908070be21a187c305b56f7aec880f30eb69cb2d12911f07663a4d2c3c616826",
    "9fb292b443ddaa2f332568981e4a6629f43bfa7b31fc7d58687be90d432a9514",
    "a2e3fb75419559fde85ec5341bcc30823172b65d1bad20d2a4fe863e5ac81f3f",
    "c25497a7b48482f6cceb21b55153dec55fbcf3ecf609a71ca116acf50ce8c533",
)
# #274 is now in accepted main (b0e5e6e); source-local observations remain
# proposals, not admitted Work/Coverage. Pin its exact file bytes like prior ones.
SOURCE_SCOPE_ANCHORS = {
    "9781668074572": ("klingon", "subspace echoes", "missing starfleet"),
    "9781668051375": ("una", "pike", "chionian"),
    "9781982123840": ("mycelial", "fuel", "discovery"),
    "9781982154042": ("betazed", "science station", "diplomatic"),
    "9781982133665": ("kirk", "medusans", "telepathic"),
    "9781665921176": ("protostar", "starfleet battery", "traders"),
}

raw = (HERE / "observations.json").read_bytes()
if hashlib.sha256(raw).hexdigest() != PINNED_SHA256:
    raise ValueError("unreviewed literary publisher observation bytes")
EXPECTED = json.loads(raw)


def isbn13_valid(value):
    if not isinstance(value, str) or len(value) != 13 or not value.isdigit():
        return False
    check = sum((1 if i % 2 == 0 else 3) * int(char) for i, char in enumerate(value[:12]))
    return (10 - check % 10) % 10 == int(value[-1])


def prior_inventory():
    observations = []
    for path, sha in zip(PRIOR_PATHS, PRIOR_SHA256):
        blob = path.read_bytes()
        if hashlib.sha256(blob).hexdigest() != sha:
            raise ValueError("previous accepted proposal observation changed")
        observations.append(json.loads(blob))
    a, b, c, d = observations
    if any(x.get("proposal_only") is not True for x in observations):
        raise ValueError("prior source-local proposal silently promoted")
    titles = [s["title"] for s in a["records"]] + [s["title"] for s in b["records"]] + [s["title"] for s in c["candidate_works"]] + [s["title"] for s in d["candidate_works"]]
    isbn = [s["isbn13"] for s in a["records"]] + [s["isbn13"] for s in b["records"]] + [s["isbn13"] for s in c["candidate_works"]] + [s["isbn13"] for s in d["candidate_works"]]
    if len(set(titles)) != 21 or len(set(isbn)) != 30:
        raise ValueError("previous 21-title/30-ISBN source-local inventory changed")
    return set(titles), set(isbn)


def validate_source_scope(rows):
    """Targeted paraphrase anchors; still requires independent publisher page review."""
    for row in rows:
        synopsis = row["synopsis"].casefold()
        anchors = SOURCE_SCOPE_ANCHORS.get(row["isbn13"])
        if not anchors or any(anchor not in synopsis for anchor in anchors):
            raise ValueError("publisher synopsis anchors missing or mixed between works")
        if row["isbn13"] == "9781668074572" and "strand" in synopsis:
            raise ValueError("Toward the Night publisher page does not establish a stranded party")
    return True


def validate(data):
    if not isinstance(data, dict) or set(data) != set(EXPECTED):
        raise ValueError("unreviewed schema")
    for key, expected in EXPECTED.items():
        if type(data[key]) is not type(expected) or data[key] != expected:
            raise ValueError(f"unreviewed publisher record: {key}")
    if data["schema_version"] != "trek-lit-six-series-sns-publisher-v1" or data["proposal_only"] is not True:
        raise ValueError("schema/admission drift")
    if data["verification_class"] != "DIRECT_OFFICIAL_PUBLISHER_PAGE_EDITION_METADATA_AND_DESCRIPTION":
        raise ValueError("claim exceeds inspected publisher description")
    if data["publisher_lineage"] != "publisher:simonandschuster.com" or data["distinct_upstream_sources"] != 1:
        raise ValueError("multiple imprints do not imply source independence")
    for key in ("accepted_source_work_effect", "accepted_coverage_effect", "accepted_evidence_effect"):
        if data[key] != "NONE":
            raise ValueError("accepted effect attempted")
    for key in ("source_bound", "full_text_available", "structurally_indexed", "close_read", "semantically_analyzed", "artwork_display_rights_verified", "cover_image_bytes_retrieved", "publisher_edition_family_complete"):
        if data[key] is not False:
            raise ValueError("source/book/artwork status overclaim")
    if tuple(data[k] for k in ("candidate_work_count", "verified_edition_page_count", "source_labeled_synopsis_count", "cover_url_locators_held_count")) != (6, 6, 6, 6):
        raise ValueError("source observation count drift")
    rows = data["candidate_works"]
    fields = {"candidate_id", "title", "creator", "series", "imprint", "format", "isbn13", "publisher_publication_date", "publisher_extent", "publisher_url", "synopsis_status", "synopsis", "cover_candidate_locator", "cover_locator_source", "cover_rights_status"}
    if len(rows) != 6 or len({r["title"] for r in rows}) != 6 or len({r["isbn13"] for r in rows}) != 6 or len({r["candidate_id"] for r in rows}) != 6:
        raise ValueError("duplicate local identity or edition")
    prior_titles, prior_isbn = prior_inventory()
    if {r["title"] for r in rows} & prior_titles or {r["isbn13"] for r in rows} & prior_isbn:
        raise ValueError("overlaps preceding four accepted-main literary discovery packets")
    for row in rows:
        if set(row) != fields or not isbn13_valid(row["isbn13"]):
            raise ValueError("invalid field or ISBN")
        if not row["candidate_id"].startswith("lit-source-local-sns-") or row["format"] != "TRADE_PAPERBACK":
            raise ValueError("unqualified global identity or format")
        if row["imprint"] not in {"Pocket Books/Star Trek", "Simon Spotlight"}:
            raise ValueError("unqualified publisher imprint")
        if row["synopsis_status"] != "PUBLISHER_DESCRIPTION_PARAPHRASE" or not isinstance(row["synopsis"], str) or not 18 <= len(row["synopsis"].split()) <= 60:
            raise ValueError("summary source or length drift")
        if not row["publisher_url"].startswith("https://www.simonandschuster.com/books/") or not row["publisher_url"].endswith("/" + row["isbn13"]):
            raise ValueError("edition page is not ISBN-bound official publisher")
        if row["cover_locator_source"] != "PUBLISHER_HIGH_RES_IMAGE_LINK" or row["cover_rights_status"] != "RIGHTS_UNVERIFIED_HOLD_NO_PUBLIC_DISPLAY":
            raise ValueError("cover display rights improperly promoted")
        image_url = row["cover_candidate_locator"]
        if not image_url.startswith("https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr" + row["isbn13"] + "/") or not image_url.endswith("-" + row["isbn13"] + "_hr.jpg"):
            raise ValueError("cover host/edition mismatch")
    validate_source_scope(rows)
    return True


if __name__ == "__main__":
    validate(EXPECTED)
    print("Six ISBN-specific publisher-ledger leads; zero accepted Works, coverage or display-rights effects")
