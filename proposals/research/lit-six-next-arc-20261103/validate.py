"""Validate wave-six ISBN-specific literary candidates; no admitted book evidence."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PINNED_SHA256 = "15d90ff865ab08fd1df7ac12518247af85a502c1655a57bee095b45889a022a2"
PRIOR_PATHS = (
    ROOT / "proposals/research/lit-three-publisher-editions-20261103/observations.json",
    ROOT / "proposals/research/lit-ring-memoir-publisher-20261103/observations.json",
    ROOT / "proposals/research/lit-six-next-publisher-works-20261103/observations.json",
    ROOT / "proposals/research/lit-six-era-publisher-20261103/observations.json",
    ROOT / "proposals/research/lit-six-series-expansion-20261103/observations.json",
)
PRIOR_SHA256 = (
    "908070be21a187c305b56f7aec880f30eb69cb2d12911f07663a4d2c3c616826",
    "9fb292b443ddaa2f332568981e4a6629f43bfa7b31fc7d58687be90d432a9514",
    "a2e3fb75419559fde85ec5341bcc30823172b65d1bad20d2a4fe863e5ac81f3f",
    "c25497a7b48482f6cceb21b55153dec55fbcf3ecf609a71ca116acf50ce8c533",
    "590bcba5feb89923a8989f6a4b16f0cfd984c4b60cbb62293b6b4d5af269de62",
)
# #279 is now merged to main at e2bc820. Proposal source-local records remain
# nonadmitted, but their exact bytes are pinned like four older main packets.
SOURCE_SCOPE_ANCHORS = {
    "9781668096932": ("jake", "cardassia", "murders"),
    "9781501138836": ("full circle", "galen", "janeway"),
    "9781476779133": ("archer", "ware", "klingon"),
    "9781982157548": ("burnham", "burn", "discovery"),
    "9781982165895": ("kirk", "spock", "uhura"),
    "9781665925426": ("protostar", "supernova", "droids"),
}
raw = (HERE / "observations.json").read_bytes()
if hashlib.sha256(raw).hexdigest() != PINNED_SHA256:
    raise ValueError("wave-six publisher observations drifted")
EXPECTED = json.loads(raw)


def isbn13_valid(value):
    if not isinstance(value, str) or len(value) != 13 or not value.isdigit():
        return False
    check = sum((1 if i % 2 == 0 else 3) * int(char) for i, char in enumerate(value[:12]))
    return (10 - check % 10) % 10 == int(value[-1])


def prior_inventory():
    obs = []
    for path, sha in zip(PRIOR_PATHS, PRIOR_SHA256):
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError("accepted-main prior proposal observations drifted")
        obs.append(json.loads(raw))
    a, b, c, d, e = obs
    if any(x.get("proposal_only") is not True for x in obs):
        raise ValueError("prior proposal unexpectedly admitted")
    titles = [x["title"] for x in a["records"]] + [x["title"] for x in b["records"]] + [x["title"] for x in c["candidate_works"]] + [x["title"] for x in d["candidate_works"]] + [x["title"] for x in e["candidate_works"]]
    isbn = [x["isbn13"] for x in a["records"]] + [x["isbn13"] for x in b["records"]] + [x["isbn13"] for x in c["candidate_works"]] + [x["isbn13"] for x in d["candidate_works"]] + [x["isbn13"] for x in e["candidate_works"]]
    if len(set(titles)) != 27 or len(set(isbn)) != 36:
        raise ValueError("prior 27 Work candidates or 36 ISBN editions drifted")
    return set(titles), set(isbn)


def validate_source_scope(rows):
    for r in rows:
        synopsis = r["synopsis"].casefold()
        anchors = SOURCE_SCOPE_ANCHORS.get(r["isbn13"])
        if not anchors or any(x not in synopsis for x in anchors):
            raise ValueError("description paraphrase swapped or missing primary-page anchor")
        if r["isbn13"] == "9781665925426" and any(x in synopsis for x in ("captivity", "imprisoned", "incarcerat")):
            raise ValueError("Supernova publisher page does not establish earlier captivity")
    return True


def validate(data):
    if not isinstance(data, dict) or set(data) != set(EXPECTED):
        raise ValueError("unexpected schema")
    for key, expected in EXPECTED.items():
        if type(data[key]) is not type(expected) or data[key] != expected:
            raise ValueError(f"unreviewed publisher observation drift: {key}")
    if data["schema_version"] != "trek-lit-six-next-arc-publisher-v1" or data["proposal_only"] is not True:
        raise ValueError("unauthorized admission/schema drift")
    if data["verification_class"] != "DIRECT_OFFICIAL_PUBLISHER_PAGE_EDITION_METADATA_AND_DESCRIPTION":
        raise ValueError("claimed source tier too high")
    if data["publisher_lineage"] != "publisher:simonandschuster.com" or data["distinct_upstream_sources"] != 1:
        raise ValueError("upstream source family overcount")
    for key in ("accepted_source_work_effect", "accepted_coverage_effect", "accepted_evidence_effect"):
        if data[key] != "NONE":
            raise ValueError("unauthorized accepted effects")
    for key in ("source_bound", "full_text_available", "structurally_indexed", "close_read", "semantically_analyzed", "artwork_display_rights_verified", "cover_image_bytes_retrieved", "publisher_edition_family_complete"):
        if data[key] is not False:
            raise ValueError("unsubstantiated source/book/cover status")
    if tuple(data[x] for x in ("candidate_work_count", "verified_edition_page_count", "source_labeled_synopsis_count", "cover_url_locators_held_count")) != (6, 6, 6, 6):
        raise ValueError("invented batch count")
    rows = data["candidate_works"]
    fields = {"candidate_id", "title", "creator", "series", "imprint", "format", "isbn13", "publisher_publication_date", "publisher_release_state", "publisher_extent", "publisher_url", "synopsis_status", "synopsis", "cover_candidate_locator", "cover_locator_source", "cover_rights_status"}
    if len(rows) != 6 or any(len({r[k] for r in rows}) != 6 for k in ("candidate_id", "title", "isbn13")):
        raise ValueError("duplicate or missing work/edition")
    prior_titles, prior_isbns = prior_inventory()
    if {r["title"] for r in rows} & prior_titles or {r["isbn13"] for r in rows} & prior_isbns:
        raise ValueError("duplicate of a prior accepted-main source-local proposal edition/work")
    for r in rows:
        if set(r) != fields or not isbn13_valid(r["isbn13"]):
            raise ValueError("wrong record fields or ISBN check digit")
        if not r["candidate_id"].startswith("lit-source-local-sns-") or r["format"] not in {"TRADE_PAPERBACK", "MASS_MARKET_PAPERBACK"}:
            raise ValueError("global identity or edition format drift")
        if r["imprint"] not in {"Pocket Books/Star Trek", "Simon Spotlight"}:
            raise ValueError("wrong publisher imprint")
        if r["synopsis_status"] != "PUBLISHER_DESCRIPTION_PARAPHRASE" or not isinstance(r["synopsis"], str) or not 18 <= len(r["synopsis"].split()) <= 60:
            raise ValueError("unsupported summary source/length")
        if not r["publisher_url"].startswith("https://www.simonandschuster.com/books/") or not r["publisher_url"].endswith("/" + r["isbn13"]):
            raise ValueError("unqualified ISBN-specific official page")
        if r["cover_locator_source"] != "PUBLISHER_HIGH_RES_IMAGE_LINK" or r["cover_rights_status"] != "RIGHTS_UNVERIFIED_HOLD_NO_PUBLIC_DISPLAY":
            raise ValueError("unapproved cover display")
        url = r["cover_candidate_locator"]
        if not url.startswith("https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr" + r["isbn13"] + "/") or not url.endswith("-" + r["isbn13"] + "_hr.jpg"):
            raise ValueError("cover locator not ISBN-specific")
        future = r["isbn13"] == "9781668096932"
        if r["publisher_release_state"] != ("FUTURE_PUBLISHER_DATE_NO_TEXT_AVAILABILITY_CLAIM" if future else "PAST_PUBLISHER_DATE_NOT_FULL_TEXT_CUSTODY"):
            raise ValueError("publication date availability overclaim")
    validate_source_scope(rows)
    return True


if __name__ == "__main__":
    validate(EXPECTED)
    print("Six publisher catalog entries checked including one future release; zero admitted Work or image effects")
