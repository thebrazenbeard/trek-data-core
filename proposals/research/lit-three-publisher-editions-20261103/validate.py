"""Validate a nine-page primary publisher bibliographic crosswalk, not book text."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "proposals/librarian/simon-schuster-three-novels-20261103/records.json"
PINNED_OBSERVATIONS_SHA256 = "908070be21a187c305b56f7aec880f30eb69cb2d12911f07663a4d2c3c616826"
raw = (HERE / "observations.json").read_bytes()
if hashlib.sha256(raw).hexdigest() != PINNED_OBSERVATIONS_SHA256:
    raise ValueError("publisher verification sidecar changed without review")
EXPECTED = json.loads(raw)


def isbn13_valid(value):
    if not isinstance(value, str) or len(value) != 13 or not value.isdigit():
        return False
    total = sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(value[:12]))
    return (10 - total % 10) % 10 == int(value[-1])


def validate(data, source_bundle=None):
    if not isinstance(data, dict) or set(data) != set(EXPECTED):
        raise ValueError("verification field set drift")
    for key, value in EXPECTED.items():
        if type(data[key]) is not type(value) or data[key] != value:
            raise ValueError(f"unreviewed verification change: {key}")
    if data["schema_version"] != "trek-lit-publisher-bibliography-verification-v1":
        raise ValueError("schema mismatch")
    if data["verification_class"] != "DIRECT_OFFICIAL_PUBLISHER_PAGE_BIBLIOGRAPHIC_FIELDS_ONLY":
        raise ValueError("publisher observation overclaim")
    if data["independence_group"] != "publisher:simonandschuster.com" or data["distinct_upstream_sources"] != 1:
        raise ValueError("independent source overcount")
    for field in ("accepted_source_binding_effect", "accepted_work_effect", "accepted_evidence_effect", "accepted_coverage_effect"):
        if data[field] != "NONE":
            raise ValueError("unauthorized research admission")
    for field in ("source_bound", "full_text_available", "full_text_read", "semantic_close_read", "publisher_edition_completeness_verified", "private_original_file_match", "artwork_display_rights_verified"):
        if data[field] is not False:
            raise ValueError("unsupported source/rights qualification")

    records = data["records"]
    if len(records) != 9 or len({row["isbn13"] for row in records}) != 9:
        raise ValueError("edition count or duplicate ISBN")
    by_work = {}
    for row in records:
        if not isbn13_valid(row["isbn13"]):
            raise ValueError("invalid publisher ISBN13")
        by_work.setdefault(row["candidate_work_id"], set()).add(row["format"])
        if row["field_verdict"] != "ALL_CHECKED_PUBLISHER_PAGE_FIELDS_MATCH":
            raise ValueError("unverified edition fields")
    if len(by_work) != 3 or any(kinds != {"TRADE_PAPERBACK", "EBOOK", "UNABRIDGED_AUDIO_DOWNLOAD"} for kinds in by_work.values()):
        raise ValueError("edition format distribution mismatch")

    synopses = data["work_synopses"]
    if len(synopses) != 3 or {s["candidate_work_id"] for s in synopses} != set(by_work):
        raise ValueError("one publisher synopsis per candidate Work required")
    publisher_rows = {(r["candidate_work_id"], r["publisher_url"]) for r in records}
    for synopsis in synopses:
        if set(synopsis) != {"candidate_work_id", "status", "source_kind", "source_locator", "synopsis"}:
            raise ValueError("publisher synopsis field set drift")
        if synopsis["status"] != "PUBLISHER_DESCRIPTION_PARAPHRASE" or synopsis["source_kind"] != "OFFICIAL_PUBLISHER_PROMOTIONAL_COPY_NOT_BOOK_TEXT":
            raise ValueError("publisher synopsis falsely promoted as full-text evidence")
        if (synopsis["candidate_work_id"], synopsis["source_locator"]) not in publisher_rows:
            raise ValueError("publisher synopsis is not bound to the same Work's source")
        if not isinstance(synopsis["synopsis"], str) or not 15 <= len(synopsis["synopsis"].split()) <= 55:
            raise ValueError("publisher synopsis missing or overlong")

    source_bundle = source_bundle if source_bundle is not None else json.loads(SOURCE.read_text(encoding="utf-8"))
    if source_bundle.get("proposal_only") is not True:
        raise ValueError("Librarian source unexpectedly promoted")
    source_works = {w["candidate_work_id"]: w for w in source_bundle["works"]}
    source_editions = {e["isbn13"]: e for e in source_bundle["editions"]}
    if len(source_editions) != 9:
        raise ValueError("Librarian source edition set changed")
    for row in records:
        work = source_works.get(row["candidate_work_id"])
        edition = source_editions.get(row["isbn13"])
        if work is None or edition is None:
            raise ValueError("unknown publisher work or ISBN")
        for verified, source_field in (("title", "title"), ("creator", "creator")):
            if row[verified] != work[source_field]:
                raise ValueError("candidate Work identity mismatch")
        for verified, source_field in (
            ("candidate_work_id", "candidate_work_id"),
            ("format", "format"),
            ("publisher_imprint", "publisher_imprint"),
            ("publication_date", "publisher_publication_date"),
            ("publisher_extent", "publisher_extent"),
            ("narrator", "narrator"),
            ("publisher_url", "publisher_product_url"),
        ):
            if row[verified] != edition[source_field]:
                raise ValueError(f"publisher source mismatch: {verified}")
        if not row["publisher_url"].startswith("https://www.simonandschuster.com/books/") or not row["publisher_url"].endswith("/" + row["isbn13"]):
            raise ValueError("publisher edition locator mismatch")
    return True


if __name__ == "__main__":
    validate(EXPECTED)
    print("Nine publisher edition pages verified; no book-text or coverage admission")
