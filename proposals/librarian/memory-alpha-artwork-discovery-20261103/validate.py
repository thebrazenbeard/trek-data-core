"""Fail-closed validation for search-indexed Memory Alpha discovery, never art admission."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit


RECORD = Path(__file__).resolve().parent / "records.json"
ROOT = Path(__file__).resolve().parents[3]
LIT_CATEGORY = "https://memory-alpha.fandom.com/wiki/Category:Memory_Alpha_images_(literature_covers)"
TOS_CATEGORY = "https://memory-alpha.fandom.com/wiki/Category:Memory_Alpha_remastered_files_by_production_(TOS:_The_Doomsday_Machine)"
FILM_CATEGORY = "https://memory-alpha.fandom.com/wiki/Category:Memory_Alpha_files_by_production_(Star_Trek_II:_The_Wrath_of_Khan)"

# These are bounded observed search-index titles, NOT verified licensed image pages.
EXPECTED = {
    "ma-file-kirk-autobiography-cover": ("LITERATURE", "The Autobiography of James T. Kirk.jpg", LIT_CATEGORY, ("literature:prh-autobiography-kirk",), "TITLE_MATCH_ONLY_NOT_AN_EDITION_BINDING", "POSSIBLE_BOOK_COVER"),
    "ma-file-picard-autobiography-cover": ("LITERATURE", "The Autobiography of Jean-Luc Picard cover.jpg", LIT_CATEGORY, ("literature:prh-autobiography-picard",), "TITLE_MATCH_ONLY_NOT_AN_EDITION_BINDING", "POSSIBLE_BOOK_COVER"),
    "ma-file-janeway-autobiography-cover": ("LITERATURE", "Autobiography of Kathryn Janeway cover.jpg", LIT_CATEGORY, ("literature:prh-autobiography-janeway",), "TITLE_MATCH_ONLY_NOT_AN_EDITION_BINDING", "POSSIBLE_BOOK_COVER"),
    "ma-file-spock-autobiography-cover": ("LITERATURE", "The Autobiography of Spock cover.jpg", LIT_CATEGORY, ("literature:prh-autobiography-spock",), "TITLE_MATCH_ONLY_NOT_AN_EDITION_BINDING", "POSSIBLE_BOOK_COVER"),
    "ma-file-sisko-autobiography-cover": ("LITERATURE", "The Autobiography of Benjamin Sisko cover.jpg", LIT_CATEGORY, ("literature:prh-autobiography-sisko",), "TITLE_MATCH_ONLY_NOT_AN_EDITION_BINDING", "POSSIBLE_BOOK_COVER"),
    "ma-file-doomsday-remastered-title-card": ("EPISODE", "2x06 The Doomsday Machine title card.jpg", TOS_CATEGORY, ("lead:0000", "legacy:s2:tos:005"), "AMBIGUOUS_SOURCE_LOCAL_EPISODE_ROWS", "POSSIBLE_EPISODE_TITLE_CARD"),
    "ma-file-wrath-of-khan-artwork": ("FILM", "Star Trek The Wrath of Khan artwork.jpg", FILM_CATEGORY, ("film:film-wrath-of-khan",), "TITLE_MATCH_ONLY_NOT_AN_EDITION_BINDING", "POSSIBLE_FILM_PROMOTIONAL_ART"),
    "ma-file-uss-constellation-remastered": ("STARSHIP", "USS Constellation remastered.jpg", TOS_CATEGORY, (), "NO_ACCEPTED_STARSHIP_ROW", "POSSIBLE_SHIP_STILL"),
}

TOP_FIELDS = {"schema_version", "role", "proposal_only", "observed_on_utc", "source_provider",
              "source_independence_group", "retrieval_method", "file_description_pages_read",
              "file_bytes_retrieved", "image_urls_released", "hotlink_permission_verified",
              "accepted_source_effect", "accepted_work_effect", "accepted_evidence_effect",
              "coverage_effect", "public_artwork_release_effect", "rights_policy_sources",
              "commons_alternative_candidates", "file_candidates", "secondary_metadata_leads"}
FILE_FIELDS = {"candidate_id", "medium_hint", "file_title_from_index", "category_locator",
               "source_local_row_ids", "subject_mapping", "image_role_hint", "file_page_status",
               "uploader_and_license_status", "display_status", "image_url"}
METADATA_FIELDS = {"article_locator", "title_from_search_excerpt", "isbn10_from_search_excerpt",
                   "existing_source_local_row_id", "mapping_status", "evidence_status"}
RIGHTS_POLICY = {
    "https://memory-alpha.fandom.com/wiki/Memory_Alpha:File_use_policy",
    "https://memory-alpha.fandom.com/wiki/Memory_Alpha:Copyrights",
    "https://support.fandom.com/hc/en-us/articles/360035075654-I-want-to-reuse-text-or-images-from-a-Fandom-wiki",
    "https://commons.wikimedia.org/wiki/Commons:Fandom_files",
}
METADATA = {
    "https://memory-alpha.fandom.com/wiki/The_High_Country":
        ("The High Country", "1668002388", "literature:proposed-lit-snw-high-country",
         "POSSIBLE_DIFFERENT_FORMAT_HARDCOVER_NOT_RESOLVED"),
    "https://memory-alpha.fandom.com/wiki/The_Autobiography_of_Kathryn_Janeway":
        ("The Autobiography of Kathryn Janeway", "1789094798",
         "literature:prh-autobiography-janeway", "HARDCOVER_VS_LISTED_PAPERBACK_UNRESOLVED"),
}
COMMONS_FIELDS = {"candidate_id", "file_page", "original_source", "creator", "license",
                  "license_url", "flickr_license_reviewed_on", "candidate_use",
                  "photo_license_status", "underlying_prop_design_and_trademark_status",
                  "asset_publication", "image_url"}
COMMONS = {
    "commons-henry-ford-tng-props-photo": {
        "file_page": "https://commons.wikimedia.org/wiki/File:Star_Trek_-_The_Next_Generation_Props_-_Star_Trek-_Exploring_New_Worlds_Exhibit_at_the_Henry_Ford_Museum,_Dearborn,_Michigan.jpg",
        "original_source": "https://www.flickr.com/photos/joeross/49785566691/",
        "creator": "Joe Ross", "license": "CC BY-SA 2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "flickr_license_reviewed_on": "2023-06-15",
        "candidate_use": "POSSIBLE_DECORATIVE_MUSEUM_PHOTO_NOT_EPISODE_STILL"},
    "commons-starfleet-of1-insignia": {
        "file_page": "https://commons.wikimedia.org/wiki/File:Starfleet_OF1.png",
        "original_source": None, "creator": "Sano", "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "flickr_license_reviewed_on": None,
        "candidate_use": "POSSIBLE_STARFLEET_RANK_INSIGNIA_NOT_CANONICAL_BRAND_MARK"},
}


def check(condition: bool, explanation: str) -> None:
    if not condition:
        raise ValueError(explanation)


def validate(packet: dict, catalog: dict) -> None:
    """Reject mutation of a rights-/coverage-blocked discovery-only receipt."""
    check(type(packet) is dict and set(packet) == TOP_FIELDS, "packet field set")
    fixed = {
        "schema_version": "1.0.0", "role": "LIBRARIAN", "proposal_only": True,
        "observed_on_utc": "2026-11-03", "source_provider": "Memory Alpha (Fandom)",
        "source_independence_group": "secondary:memory-alpha.fandom.com",
        "retrieval_method": "SEARCH_INDEXED_CATEGORY_OR_ARTICLE_EXCERPT_ONLY",
        "file_description_pages_read": False, "file_bytes_retrieved": False,
        "image_urls_released": False, "hotlink_permission_verified": False,
        "accepted_source_effect": "NONE", "accepted_work_effect": "NONE",
        "accepted_evidence_effect": "NONE", "coverage_effect": "NONE",
        "public_artwork_release_effect": "NONE",
    }
    for field, value in fixed.items():
        check(type(packet[field]) is type(value) and packet[field] == value, f"fixed field: {field}")
    check(type(packet["rights_policy_sources"]) is list and
          len(packet["rights_policy_sources"]) == 4 and
          set(packet["rights_policy_sources"]) == RIGHTS_POLICY, "rights sources")
    check(type(packet["commons_alternative_candidates"]) is list and
          len(packet["commons_alternative_candidates"]) == len(COMMONS), "Commons count")
    commons_seen = set()
    for entry in packet["commons_alternative_candidates"]:
        check(type(entry) is dict and set(entry) == COMMONS_FIELDS, "Commons field set")
        candidate = entry["candidate_id"]
        check(type(candidate) is str and candidate in COMMONS and candidate not in commons_seen,
              "Commons candidate identity")
        commons_seen.add(candidate)
        expected = dict(COMMONS[candidate],
                        photo_license_status="DOCUMENTED_ON_COMMONS_FILE_PAGE",
                        underlying_prop_design_and_trademark_status="UNRESOLVED",
                        asset_publication="BLOCKED_PENDING_SEPARATE_REVIEW", image_url=None)
        for field, value in expected.items():
            check(type(entry[field]) is type(value) and entry[field] == value,
                  f"Commons {candidate}: {field}")
    rows = catalog["rows"]
    row_index = {row["row_id"]: row for row in rows}
    check(catalog["identity_scope"] == "SOURCE_LOCAL_NOT_DEDUPLICATED" and
          catalog["data_status"] == "DISCOVERY_ONLY", "accepted catalog model")
    check(type(packet["file_candidates"]) is list and
          len(packet["file_candidates"]) == len(EXPECTED), "image candidate count")
    seen = set()
    for entry in packet["file_candidates"]:
        check(type(entry) is dict and set(entry) == FILE_FIELDS, "image candidate field set")
        candidate = entry["candidate_id"]
        check(type(candidate) is str and candidate in EXPECTED and candidate not in seen,
              "image candidate identity")
        seen.add(candidate)
        medium, title, category, row_ids, mapping, role = EXPECTED[candidate]
        for field, expected in (("medium_hint", medium), ("file_title_from_index", title),
                                ("category_locator", category), ("subject_mapping", mapping),
                                ("image_role_hint", role),
                                ("file_page_status", "NOT_READ_ROBOTS_RESTRICTED"),
                                ("uploader_and_license_status", "UNVERIFIED"),
                                ("display_status", "BLOCKED_NO_FILE_LEVEL_PERMISSION"),
                                ("image_url", None)):
            check(type(entry[field]) is type(expected) and entry[field] == expected,
                  f"file {candidate}: {field}")
        check(type(entry["source_local_row_ids"]) is list and
              entry["source_local_row_ids"] == list(row_ids), f"file {candidate}: source-local rows")
        for row_id in row_ids:
            check(row_id in row_index and row_index[row_id]["medium"] == medium,
                  f"file {candidate}: missing or wrong-medium catalog row")
        if candidate == "ma-file-doomsday-remastered-title-card":
            check(all(row_index[row_id]["title"] == "The Doomsday Machine" for row_id in row_ids),
                  "ambiguous episode titles")
        if candidate == "ma-file-wrath-of-khan-artwork":
            check(row_index[row_ids[0]]["title"] == "Star Trek II: The Wrath of Khan", "film title")
    check(seen == set(EXPECTED), "missing image candidate")
    check(type(packet["secondary_metadata_leads"]) is list and
          len(packet["secondary_metadata_leads"]) == len(METADATA), "metadata lead count")
    seen_meta = set()
    for entry in packet["secondary_metadata_leads"]:
        check(type(entry) is dict and set(entry) == METADATA_FIELDS, "metadata field set")
        url = entry["article_locator"]
        check(type(url) is str and url in METADATA and url not in seen_meta, "metadata identity")
        seen_meta.add(url)
        title, isbn, row_id, status = METADATA[url]
        for field, expected in (("title_from_search_excerpt", title),
                                ("isbn10_from_search_excerpt", isbn),
                                ("existing_source_local_row_id", row_id),
                                ("mapping_status", status),
                                ("evidence_status", "SECONDARY_WIKI_DISCOVERY_ONLY")):
            check(type(entry[field]) is type(expected) and entry[field] == expected,
                  f"metadata {url}: {field}")
        check(row_id in row_index and row_index[row_id]["medium"] == "LITERATURE",
              "metadata source-local row")
    check(seen_meta == set(METADATA), "missing metadata lead")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, default=RECORD)
    parser.add_argument("--catalog", type=Path, default=ROOT / "explorer/discovery-catalog.json")
    args = parser.parse_args(argv)
    validate(json.loads(args.records.read_text(encoding="utf-8")),
             json.loads(args.catalog.read_text(encoding="utf-8")))
    print("Memory Alpha discovery-only packet: VALID (0 approved images, 0 admitted effects)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
