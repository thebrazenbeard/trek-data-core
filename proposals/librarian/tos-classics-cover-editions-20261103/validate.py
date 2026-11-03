"""Publisher edition and cover-source metadata inventory (proposal only)."""

import hashlib
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CATALOG = ROOT / "explorer/discovery-catalog.json"
EXPECTED = {
    "9780743412094": (
        "TOS-ENTROPY-EBOOK-9780743412094", "The Entropy Effect", "Vonda N. McIntyre",
        "eBook", "Pocket Books/Star Trek", "2002-10-08", 224,
        "https://www.simonandschuster.com/books/The-Entropy-Effect/Vonda-N-McIntyre/Star-Trek/9780743412094",
    ),
    "9781451607536": (
        "TOS-ENTROPY-TRADE-9781451607536", "The Entropy Effect", "Vonda N. McIntyre",
        "Trade Paperback", "Gallery Books", "2010-06-01", 224,
        "https://www.simonandschuster.com/books/The-Entropy-Effect/Vonda-N-McIntyre/Star-Trek-The-Original-Series/9781451607536",
    ),
    "9780743419642": (
        "TOS-WOUNDED-SKY-EBOOK-9780743419642", "The Wounded Sky", "Diane Duane",
        "eBook", "Pocket Books/Star Trek", "2000-09-22", 224,
        "https://www.simonandschuster.com/books/The-Wounded-Sky/Diane-Duane/Star-Trek-The-Original-Series/9780743419642",
    ),
    "9780743419673": (
        "TOS-FINAL-REFLECTION-EBOOK-9780743419673", "The Final Reflection", "John M. Ford",
        "eBook", "Pocket Books/Star Trek", "2000-09-22", 256,
        "https://www.simonandschuster.com/books/The-Final-Reflection/John-M-Ford/Star-Trek-The-Original-Series/9780743419673",
    ),
}
ROW_FIELDS = {
    "edition_candidate_id", "work_label", "creator", "format", "publisher_imprint",
    "publisher_listed_date", "publisher_listed_pages", "isbn13", "publisher_product_url",
    "cover_link_on_product_page", "cover_source_section", "cover_file_uri", "cover_rights_state", "status",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def valid_isbn13(code):
    return isinstance(code, str) and bool(re.fullmatch(r"97[89][0-9]{10}", code)) and (
        sum((1 if i % 2 == 0 else 3) * int(digit) for i, digit in enumerate(code)) % 10 == 0
    )


def validate(data, raw_catalog):
    require(set(data) == {
        "proposal_id", "role", "baseline_accepted_main", "observed_date_utc", "proposal_only",
        "accepted_corpus_effect", "source_family", "source_representation", "source_version",
        "raw_page_sha256", "source_body_read", "rights_to_publish_covered_images",
        "artwork_bytes_downloaded_or_committed", "catalog_gap_snapshot", "edition_candidates",
        "legacy_crosswalk_hold", "accepted_sources_added", "accepted_works_added",
        "accepted_edition_bindings_added", "coverage_events_added", "image_publication_effect",
    }, "unreviewed envelope fields")
    require(data["proposal_id"] == "LIBRARIAN-TOS-CLASSICS-EDITION-COVER-LOCATORS-20261103", "wrong proposal")
    require(data["role"] == "LIBRARIAN" and data["proposal_only"] is True, "unreviewed role/status")
    require(data["baseline_accepted_main"] == "8a89b16e96220188d200b6ff9300fb90fa137627", "wrong baseline")
    require(data["observed_date_utc"] == "2026-11-03", "unreviewed observation date")
    require(data["accepted_corpus_effect"] == "NONE" and data["image_publication_effect"] == "NONE", "unapproved effects")
    require(data["source_family"] == "publisher:simonandschuster.com", "wrong source lineage")
    require(data["source_representation"] == "RENDERED_OFFICIAL_PRODUCT_PAGE_METADATA_NOT_RAW_HTTP_CUSTODY", "misrepresented source")
    require(data["source_version"] is None and data["raw_page_sha256"] is None and data["source_body_read"] is False, "false source custody")
    require(data["rights_to_publish_covered_images"] == "UNVERIFIED", "cover rights overstated")
    require(data["artwork_bytes_downloaded_or_committed"] is False, "unverified image bytes")
    for field in ("accepted_sources_added", "accepted_works_added", "accepted_edition_bindings_added", "coverage_events_added"):
        require(data[field] == 0, field)
    gap = data["catalog_gap_snapshot"]
    require(set(gap) == {"path", "sha256", "rows", "matched_literature_rows"}, "gap envelope")
    require(gap["path"] == "explorer/discovery-catalog.json", "wrong catalog")
    require(gap["sha256"] == "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc", "unpinned directory hash")
    require(hashlib.sha256(raw_catalog).hexdigest() == gap["sha256"], "directory bytes changed")
    catalog = json.loads(raw_catalog)
    require(catalog["row_count"] == len(catalog["rows"]) == gap["rows"] == 1214, "directory row-count drift")
    book_titles = {row[1] for row in EXPECTED.values()}
    matches = sum(row.get("title") in book_titles and row.get("medium") == "LITERATURE" for row in catalog["rows"])
    require(matches == gap["matched_literature_rows"] == 0, "not actually an absent literary-title tranche")
    rows = data["edition_candidates"]
    require(isinstance(rows, list) and len(rows) == 4, "unexpected number of edition observations")
    observed = set()
    for item in rows:
        require(isinstance(item, dict) and set(item) == ROW_FIELDS, "unreviewed narrative/artwork payload")
        code = item["isbn13"]
        require(valid_isbn13(code) and code in EXPECTED and code not in observed, "bad/duplicate edition ISBN")
        observed.add(code)
        required = EXPECTED[code]
        actual = (item["edition_candidate_id"], item["work_label"], item["creator"],
                  item["format"], item["publisher_imprint"], item["publisher_listed_date"],
                  item["publisher_listed_pages"], item["publisher_product_url"])
        require(actual == required, "edition title/author/product URL mismatch")
        require(item["cover_link_on_product_page"] is True, "publisher cover-link observation omitted")
        require(item["cover_source_section"] == "Resources and Downloads > High Resolution Images > Book Cover Image (jpg)", "wrong cover evidence section")
        require(item["cover_file_uri"] is None and item["cover_rights_state"] == "UNVERIFIED_NOT_FOR_DISPLAY", "image rights/URI not reviewed")
        require(item["status"] == "EDITION_AND_COVER_SOURCE_METADATA_CANDIDATE_ONLY", "false source admission")
    require(observed == set(EXPECTED), "missing edition observation")
    require(data["legacy_crosswalk_hold"] == {
        "work_label": "The Wounded Sky", "prior_legacy_candidate_id": "STW-733c607491a5",
        "legacy_candidate_isbn10": "0671473891", "upstream_family": "community:memory-alpha.fandom.com",
        "relation": "TITLE_CREATOR_DISCOVERY_MATCH_ONLY_NOT_EDITION_IDENTITY",
        "accepted_binding_effect": "NONE",
    }, "legacy print/source-relative crosswalk silently reconciled")
    return {"edition_observations": len(rows), "distinct_work_labels": len(book_titles), "cover_links_indexed_not_cleared": len(rows)}


if __name__ == "__main__":
    print("TOS_CLASSIC_EDITION_COVER_METADATA_OK:", validate(
        json.loads((HERE / "records.json").read_text(encoding="utf-8")), CATALOG.read_bytes()))
