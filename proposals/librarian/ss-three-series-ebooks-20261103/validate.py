"""Deterministic source-local edition metadata validation: no admissions."""

import hashlib
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]

EXPECTED = {
    "9780743420587": (
        "SSEBOOK-DS9-STITCH-TIME-9780743420587", "A Stitch in Time", "Andrew J. Robinson",
        "Star Trek: Deep Space Nine", "2000-05-01", 432,
        "https://www.simonandschuster.com/books/A-Stitch-in-Time/Andrew-J-Robinson/Star-Trek-Deep-Space-Nine/9780743420587",
    ),
    "9780671040994": (
        "SSEBOOK-TNG-Q-IN-LAW-9780671040994", "Q-in-Law", "Peter David",
        "Star Trek: The Next Generation", "1991-10-01", 252,
        "https://www.simonandschuster.com/books/Q-in-Law/Peter-David/Star-Trek-The-Next-Generation/9780671040994",
    ),
    "9780743475631": (
        "SSEBOOK-VOY-HOMECOMING-9780743475631", "Homecoming", "Christie Golden",
        "Star Trek: Voyager", "2003-05-12", 288,
        "https://www.simonandschuster.com/books/Homecoming/Christie-Golden/Star-Trek-Voyager/9780743475631",
    ),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def valid_isbn13(value):
    return isinstance(value, str) and bool(re.fullmatch(r"97[89][0-9]{10}", value)) and (
        sum(int(x) * (1 if i % 2 == 0 else 3) for i, x in enumerate(value)) % 10 == 0
    )


def validate(data, catalog_bytes):
    require(set(data) == {
        "proposal_id", "baseline_accepted_main", "role", "observed_date_utc", "proposal_only",
        "accepted_corpus_effect", "rights_to_republish_text_or_art", "publisher_evidence",
        "catalog_gap_snapshot", "edition_candidates", "accepted_sources_added",
        "accepted_works_added", "accepted_source_work_bindings_added", "coverage_events_added",
        "global_identity_reconciliations",
    }, "unexpected proposal schema or protected content")
    require(data["proposal_id"] == "LIBRARIAN-SIMON-SCHUSTER-THREE-SERIES-EBOOKS-20261103", "unexpected proposal identity")
    require(data["observed_date_utc"] == "2026-11-03", "unreviewed observation date")
    require(data["role"] == "LIBRARIAN" and data["proposal_only"] is True, "role/status mismatch")
    require(data["baseline_accepted_main"] == "5b0fb86b322811ccea58f88f20d69bd4e62e9b22", "unreviewed accepted baseline")
    require(data["accepted_corpus_effect"] == "NONE", "admission effect forbidden")
    require(data["rights_to_republish_text_or_art"] == "NOT_ESTABLISHED", "copyright rights overstated")
    for field in ("accepted_sources_added", "accepted_works_added", "accepted_source_work_bindings_added", "coverage_events_added", "global_identity_reconciliations"):
        require(data[field] == 0, field)
    publisher = data["publisher_evidence"]
    require(set(publisher) == {
        "independence_group", "method", "response_sha256", "source_version",
        "page_field_locus", "independently_verified_publisher_families", "narrative_evidence_weight",
    }, "unexpected publisher evidence")
    require(publisher == {
        "independence_group": "publisher:simonandschuster.com",
        "method": "PUBLIC_RENDERED_PUBLISHER_PRODUCT_PAGES; NOT_RAW_HTTP_BYTES",
        "response_sha256": None,
        "source_version": None,
        "page_field_locus": "Product Details",
        "independently_verified_publisher_families": 1,
        "narrative_evidence_weight": 0,
    }, "publisher lineage or custody overstated")
    gap = data["catalog_gap_snapshot"]
    require(set(gap) == {"path", "sha256", "row_count", "exact_title_rows_for_these_three_candidates"}, "catalog gap schema")
    require(gap["path"] == "explorer/discovery-catalog.json", "unexpected catalog path")
    require(hashlib.sha256(catalog_bytes).hexdigest() == gap["sha256"], "catalog snapshot not reproducible")
    catalog = json.loads(catalog_bytes)
    require(catalog["row_count"] == gap["row_count"] == len(catalog["rows"]) == 1214, "catalog row-count drift")
    titles = {row[1] for row in EXPECTED.values()}
    # The real discovery-catalog schema uses LITERATURE, not LITERARY.
    actual = sum(row.get("title") in titles and row.get("medium") == "LITERATURE" for row in catalog["rows"])
    require(actual == gap["exact_title_rows_for_these_three_candidates"] == 0, "literary gap no longer valid")
    records = data["edition_candidates"]
    require(isinstance(records, list) and len(records) == len(EXPECTED), "unexpected edition candidate count")
    observed = set()
    for row in records:
        require(set(row) == {
            "candidate_id", "work_label", "creator", "publisher_series", "publisher_imprint",
            "format", "publisher_listed_date", "publisher_listed_pages", "isbn13",
            "source_locator", "status",
        }, "record contains narrative text or unreviewed fields")
        isbn = row["isbn13"]
        require(valid_isbn13(isbn) and isbn in EXPECTED, "unsupported ISBN-13")
        require(isbn not in observed, "duplicate edition")
        observed.add(isbn)
        ident, title, author, series, date, pages, url = EXPECTED[isbn]
        require((row["candidate_id"], row["work_label"], row["creator"], row["publisher_series"],
                 row["publisher_listed_date"], row["publisher_listed_pages"], row["source_locator"]) ==
                (ident, title, author, series, date, pages, url), "source title/creator/edition locator mismatch")
        require(row["publisher_imprint"] == "Pocket Books/Star Trek" and row["format"] == "eBook", "wrong edition format/imprint")
        require(row["status"] == "PUBLISHER_EDITION_METADATA_CANDIDATE_ONLY", "record claims admission")
    require(observed == set(EXPECTED), "missing ISBN")
    return len(observed)


if __name__ == "__main__":
    data = json.loads((HERE / "records.json").read_text(encoding="utf-8"))
    print("SS_THREE_SERIES_EBOOKS_OK:", validate(data, (ROOT / "explorer/discovery-catalog.json").read_bytes()))
