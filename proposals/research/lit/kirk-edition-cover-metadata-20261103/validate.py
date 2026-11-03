#!/usr/bin/env python3
"""Fail-closed check for a metadata-only, non-admitted literary format/cover gap."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RECORDS = HERE / "records.json"
DIRECTORY = ROOT / "explorer" / "discovery-catalog.json"
PAGE = "https://www.penguinrandomhouse.com/books/250795/the-autobiography-of-james-t-kirk-by-david-a-goodman/"

EXPECTED = {
    "PAPERBACK": ("9781783297481", "2016-07-05", "https://images1.penguinrandomhouse.com/cover/9781783297481"),
    "HARDCOVER": ("9781783297467", "2015-09-08", "https://images4.penguinrandomhouse.com/cover/9781783297467"),
    "EBOOK": ("9781783297474", "2015-09-08", "https://images1.penguinrandomhouse.com/cover/9781783297474"),
}
PROVIDERS = {
    "PAPERBACK": "Penguin Random House (Titan Books distributor)",
    "HARDCOVER": "Titan Books publisher",
    "EBOOK": "OverDrive licensed-library distributor",
}
ROOT_KEYS = frozenset({
    "schema_version", "lane", "batch_kind", "observed_on_utc", "proposal_only", "book_content_read",
    "accepted_source_work_binding_effect", "accepted_work_effect", "global_identity_effect",
    "coverage_effect", "public_artwork_release_effect", "candidate_directory_row", "edition_observations",
    "catalog_crosscheck", "promotional_description_discrepancy", "unresolved_gates",
})
ANCHOR_KEYS = frozenset({"row_id", "title", "source_locator", "edition_match_scope", "isbn13"})
OBSERVATION_KEYS = frozenset({
    "local_observation_id", "format", "isbn13", "us_publication_date", "edition_metadata_locator",
    "edition_metadata_provider", "cover_link_observation_page", "cover_link_locator",
    "cover_evidence_scope", "cover_display_rights", "edition_identity_status", "source_html_sha256",
})
CROSSCHECK_KEYS = frozenset({
    "source_locator", "source_record_kind", "edition_key", "isbn13", "match_scope", "cover_id",
    "exact_json_sha256", "cover_rights", "note",
})
DISCREPANCY_KEYS = frozenset({
    "source_locator", "source_relative_claim", "start_year", "end_year", "narrative_truth_effect",
})
UNRESOLVED_GATES = frozenset({
    "PAPERBACK_VS_HARDCOVER_VS_EBOOK_TEXT_EQUIVALENCE",
    "EDITION_TO_PRIVATE_OPF_OR_ORIGINAL_LIT_BYTE_IDENTITY",
    "OPEN_LIBRARY_EDITION_JSON_AND_COVER_ID",
    "PUBLISHER_IMAGE_DISPLAY_OR_REUSE_PERMISSION",
    "COPYRIGHT_AND_SOURCE_ACCESS_PERMISSION",
    "SOURCE_WORK_BINDING_AND_COVERAGE_ADMISSION",
})
OPEN_LIBRARY_NOTE = (
    "The live Open Library edition JSON endpoint could not be fetched; do not infer a cover ID "
    "from a page image or adjacent edition."
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def require_keys(value: object, expected: frozenset[str], level: str) -> None:
    require(type(value) is dict and set(value) == expected, f"unexpected or missing {level} fields")


def isbn13_valid(value: object) -> bool:
    return (type(value) is str and len(value) == 13 and value.isascii() and value.isdigit()
            and sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(value)) % 10 == 0)


def safe_public_url(value: object) -> bool:
    if type(value) is not str:
        return False
    parts = urlsplit(value)
    return (parts.scheme == "https" and parts.hostname in {
        "www.penguinrandomhouse.com", "titanbooks.com", "library2go.overdrive.com",
        "images1.penguinrandomhouse.com", "images4.penguinrandomhouse.com", "openlibrary.org"
    } and parts.username is None and parts.password is None and parts.port is None
        and not parts.query and not parts.fragment and parts.path.startswith("/")
        and ".." not in parts.path.split("/"))


def validate_records(data: object) -> None:
    require_keys(data, ROOT_KEYS, "root")
    require(data.get("schema_version") == "1.0.0" and data.get("lane") == "LIT", "wrong batch contract")
    require(data.get("batch_kind") == "SOURCE_LOCAL_EDITION_COVER_METADATA_GAP", "wrong batch kind")
    require(data.get("observed_on_utc") == "2026-11-03", "missing bounded observation date")
    require(data.get("proposal_only") is True and data.get("book_content_read") is False,
            "must remain unadmitted metadata-only proposal")
    for gate in ("accepted_source_work_binding_effect", "accepted_work_effect", "global_identity_effect",
                 "coverage_effect", "public_artwork_release_effect"):
        require(data.get(gate) == "NONE", f"forbidden effect {gate}")

    anchor = data.get("candidate_directory_row")
    require_keys(anchor, ANCHOR_KEYS, "directory row")
    require(anchor.get("row_id") == "literature:prh-autobiography-kirk",
            "not the accepted publisher-directory row")
    require(anchor.get("title") == "The Autobiography of James T. Kirk" and
            anchor.get("source_locator") == PAGE and anchor.get("isbn13") == "9781783297481" and
            anchor.get("edition_match_scope") == "PAPERBACK_ISBN_ONLY", "unverified row or edition expansion")

    observations = data.get("edition_observations")
    require(type(observations) is list and len(observations) == 3, "require exactly three observed formats")
    seen_formats, seen_isbns, seen_ids = set(), set(), set()
    for item in observations:
        require_keys(item, OBSERVATION_KEYS, "edition observation")
        fmt, isbn = item.get("format"), item.get("isbn13")
        require(fmt in EXPECTED and isbn13_valid(isbn), "invalid format or ISBN")
        require(fmt not in seen_formats and isbn not in seen_isbns, "duplicate edition")
        seen_formats.add(fmt)
        seen_isbns.add(isbn)
        require((isbn, item.get("us_publication_date"), item.get("cover_link_locator")) == EXPECTED[fmt],
                "wrong edition/date/cover correspondence")
        require(item.get("local_observation_id") == {
            "PAPERBACK": "kirk-prh-paperback", "HARDCOVER": "kirk-titan-hardcover",
            "EBOOK": "kirk-overdrive-ebook"
        }[fmt], "wrong source-local observation identity")
        require(item["local_observation_id"] not in seen_ids, "duplicate observation identity")
        seen_ids.add(item["local_observation_id"])
        require(item.get("edition_metadata_locator") == {
            "PAPERBACK": PAGE,
            "HARDCOVER": "https://titanbooks.com/8302-the-autobiography-of-james-t-kirk/",
            "EBOOK": "https://library2go.overdrive.com/library2go-111-134/content/media/2148177"
        }[fmt], "unverified edition metadata locator")
        require(item.get("cover_link_observation_page") == PAGE, "cover link not observed on the publisher page")
        require(item.get("cover_evidence_scope") == "PUBLISHER_IMAGE_LINK_ONLY_NO_BINARY_RECEIPT" and
                item.get("cover_display_rights") == "NOT_ESTABLISHED" and
                item.get("edition_identity_status") == "PUBLIC_METADATA_OBSERVATION_NOT_AUTHENTICATED_TEXT" and
                item.get("source_html_sha256") is None, "forbidden rights, text or source-byte promotion")
        for key in ("edition_metadata_locator", "cover_link_observation_page", "cover_link_locator"):
            require(safe_public_url(item.get(key)), "unsafe metadata URL")
        require(item.get("edition_metadata_provider") == PROVIDERS[fmt],
                "unverified provider label")
    require(seen_formats == set(EXPECTED), "missing edition format")

    cross = data.get("catalog_crosscheck")
    require_keys(cross, CROSSCHECK_KEYS, "catalog crosscheck")
    require(cross.get("source_locator") ==
            "https://openlibrary.org/books/OL28813033M/Autobiography_of_James_T._Kirk" and
            cross.get("source_record_kind") == "OPEN_LIBRARY_EDITION_PAGE" and
            cross.get("edition_key") == "OL28813033M" and cross.get("isbn13") == EXPECTED["PAPERBACK"][0] and
            cross.get("match_scope") == "PAPERBACK_ISBN_METADATA_ONLY" and
            cross.get("cover_id") is None and cross.get("exact_json_sha256") is None and
            cross.get("cover_rights") == "NOT_ESTABLISHED" and
            cross.get("note") == OPEN_LIBRARY_NOTE, "unearned Open Library cover receipt")

    discrepancy = data.get("promotional_description_discrepancy")
    require(type(discrepancy) is list and len(discrepancy) == 2, "preserve both promotional descriptions")
    for item in discrepancy:
        require_keys(item, DISCREPANCY_KEYS, "promotional discrepancy")
    require({(x.get("source_locator"), x.get("start_year"), x.get("end_year")) for x in discrepancy
             if type(x) is dict} == {
        ("https://titanbooks.com/8302-the-autobiography-of-james-t-kirk/", 2233, 2293),
        (PAGE, 2233, 2371)
    }, "publisher/distributor marketing chronology discrepancy must remain unresolved")
    require(all(x.get("source_relative_claim") == "MARKETING_DESCRIPTION_YEAR_RANGE" and
                x.get("narrative_truth_effect") == "NONE" for x in discrepancy),
            "marketing copy cannot become narrative evidence")
    holds = data.get("unresolved_gates")
    require(type(holds) is list and len(holds) == len(UNRESOLVED_GATES) and
            all(type(value) is str for value in holds) and set(holds) == UNRESOLVED_GATES,
            "required unresolved gates substituted or absent")


def validate_directory(data: dict) -> None:
    registry = json.loads(DIRECTORY.read_text(encoding="utf-8"))
    matched = [row for row in registry["rows"] if row["row_id"] == data["candidate_directory_row"]["row_id"]]
    require(len(matched) == 1, "anchor directory row missing or duplicated")
    row = matched[0]
    require(row["medium"] == "LITERATURE" and row["source_locator"] == PAGE and
            row["verification_status"] == "UNVERIFIED_METADATA" and
            row["admission_effect"] == "NONE" and row["coverage_effect"] == "NONE",
            "current directory drift or premature research promotion")


def main() -> int:
    try:
        data = json.loads(RECORDS.read_text(encoding="utf-8"))
        validate_records(data)
        validate_directory(data)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"LIT_EDITION_COVER_GAP_REJECTED: {exc}", file=sys.stderr)
        return 1
    print("LIT_EDITION_COVER_GAP_OK: 3 separate formats, no rights or coverage promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
