#!/usr/bin/env python3
"""Deterministic HELD OPF↔publisher edition-candidate overlay (no Works)."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "proposals/research/opf-seven-official-editions-20261103/observations.json"
OUTPUT = "proposals/consolidator/opf-seven-official-editions-20261103/crosschecks.json"
OPF = "proposals/librarian/private-opf-metadata-20261103/observations.json"
HELD = "proposals/consolidator/opf-source-local-review-sample-20261103/cards.json"
OLDER = "proposals/librarian/ss-three-series-ebooks-20261103/records.json"
BASE = "explorer/discovery-catalog.json"
SOURCE_SHA = "3d3aa4703bb2ab47291aa7fadb487320ed4cbef68c7456fabe09c52a1e848d42"
OPF_SHA = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
HELD_SHA = "ca251b3dfb98293526ad3c76c7169148e1344d106a2365304d0ddbfe36e5f06c"
OLDER_SHA = "78dd5785c73ab91be932ff7865b36d45c4aca1c4c9ea3f93c28fc164975a8a20"
BASE_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
ZIP_SHA = "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f"
IDS = ("opf-local:0110", "opf-local:0150", "opf-local:0181", "opf-local:0275",
       "opf-local:0296", "opf-local:0326", "opf-local:0335")
# Explicit locks make observations auditable rather than trusting arbitrary publisher strings.
# Byline, title, format, publisher and dates refer to a *publisher product edition*,
# never the private conversion's actual edition. All URLs are same corporate family.
LOCKS = {
    "opf-local:0110": ("A Star Trek: The Next Generation: Time #9: A Time for War, A Time for Peace", "Keith R. A. DeCandido", "9781982134907", "TRADE_PAPERBACK", "Gallery Books", "2019-05-18", 384, "Star Trek: The Next Generation", 9,
                       "A-Star-Trek-The-Next-Generation-Time-9-A-Time-for-War-A-Time-for-Peace/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation"),
    "opf-local:0150": ("Yesterday's Son", "A.C. Crispin", "9780743419628", "EBOOK", "Pocket Books/Star Trek", "2000-09-22", 192, "Star Trek: The Original Series", 11,
                       "Yesterdays-Son/A-C-Crispin/Star-Trek-The-Original-Series"),
    "opf-local:0181": ("Doctor's Orders", "Diane Duane", "9780743420013", "EBOOK", "Pocket Books/Star Trek", "2000-09-22", 291, "Star Trek: The Original Series", 50,
                       "Doctors-Orders/Diane-Duane/Star-Trek-The-Original-Series"),
    "opf-local:0275": ("Homecoming", "Christie Golden", "9780743475631", "EBOOK", "Pocket Books/Star Trek", "2003-05-12", 288, "Star Trek: Voyager", None,
                       "Homecoming/Christie-Golden/Star-Trek-Voyager"),
    "opf-local:0296": ("The Heart of the Warrior", "John Gregory Betancourt", "9780743420488", "EBOOK", "Pocket Books/Star Trek", "2000-09-22", 288, "Star Trek: Deep Space Nine", 17,
                       "The-Heart-of-the-Warrior/John-Gregory-Betancourt/Star-Trek-Deep-Space-Nine"),
    "opf-local:0326": ("Star Trek: Enterprise: Shockwave", "Paul Ruditis", "9780743464574", "EBOOK", "Pocket Books/Star Trek", "2002-10-30", 256, "Star Trek: Enterprise", None,
                       "Star-Trek-Enterprise-Shockwave/Paul-Ruditis/Star-Trek-Enterprise"),
    "opf-local:0335": ("Fire On High", "Peter David", "9780743455725", "EBOOK", "Pocket Books/Star Trek", "2002-08-04", 288, "Star Trek: The Next Generation", 6,
                       "Fire-On-High/Peter-David/Star-Trek-The-Next-Generation"),
}


def encode(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_pinned(root: Path, name: str, digest: str) -> dict:
    target = root / name
    if not target.is_file() or target.is_symlink() or not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("unsafe or absent input: " + name)
    raw = target.read_bytes()
    if len(raw) > 3_000_000 or hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError("accepted source receipt SHA changed: " + name)
    return json.loads(raw)


def isbn13_valid(s: str) -> bool:
    return isinstance(s, str) and s.isascii() and len(s) == 13 and s.isdecimal() and \
        sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(s)) % 10 == 0


def isbn10_valid(s: str) -> bool:
    digits = s.replace("-", "")
    return len(digits) == 10 and digits[:9].isascii() and digits[:9].isdecimal() and \
        (digits[9].isascii() and digits[9].isdecimal() or digits[9] == "X") and \
        sum((10 - i) * (int(c) if c != "X" else 10) for i, c in enumerate(digits)) % 11 == 0


def isbn10_to_isbn13(s: str) -> str:
    if not isbn10_valid(s):
        raise ValueError("invalid original source ISBN10")
    stem = "978" + s.replace("-", "")[:9]
    check = (-sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(stem))) % 10
    return stem + str(check)


def build(root: Path = ROOT) -> dict:
    source = read_pinned(root, SOURCE, SOURCE_SHA)
    opf = read_pinned(root, OPF, OPF_SHA)
    held = read_pinned(root, HELD, HELD_SHA)
    older = read_pinned(root, OLDER, OLDER_SHA)
    read_pinned(root, BASE, BASE_SHA)
    flags = {
        "schema_version": "1.0.0", "proposal_id": "opf-seven-official-edition-candidates-20261103",
        "accepted_main_at_start": "969626a", "observation_date": "2026-11-03",
        "method": "DIRECT_FIRST_PARTY_PUBLISHER_PRODUCT_PAGE_READ",
        "publisher_family": "publisher:simonandschuster.com", "publisher_family_independent_witnesses": 1,
        "owner_opf_original_zip_sha256_from_prior_custody": ZIP_SHA,
        "original_opf_members_rehashed_by_this_consolidator": False,
        "publisher_pages_byte_snapshotted": False,
        "owner_private_edition_equivalence": "NOT_VERIFIED", "global_work_identity": "NOT_RECONCILED",
        "public_explorer_release": "HELD", "coverage_effect": "NONE", "artwork_effect": "NONE",
        "copyrighted_content_exported": False,
    }
    if any(source.get(k) != v for k, v in flags.items()) or set(source) != {*flags, "rows"} or \
            not isinstance(source["rows"], list) or len(source["rows"]) != len(IDS) or \
            len(opf["rows"]) != 347 or held.get("selected_rows") != 39:
        raise ValueError("proposal envelope/accepted input coverage changed")
    held_rows = {r["source_local_id"]: r for r in held["card_rows"]}
    seen_hashes = set()
    seen_isbns = set()
    result = []
    for local_id, record in zip(IDS, source["rows"]):
        expected_row_fields = {"opf_source_local_id", "opf_entry_sha256", "publisher_url", "publisher_title",
                           "publisher_byline", "publisher_format", "publisher_imprint", "publisher_date",
                           "publisher_pages", "publisher_isbn13", "publisher_series",
                           "publisher_series_ordinal", "prior_same_family_publisher_candidate", "unresolved_difference"}
        if local_id == "opf-local:0110":
            expected_row_fields |= {"original_opf_xml_isbn10_literal", "original_opf_xml_identifier_tag",
                                    "original_opf_xml_isbn10_review_provenance",
                                    "source_isbn10_corresponding_publisher_ebook"}
        if set(record) != expected_row_fields or \
                record["opf_source_local_id"] != local_id:
            raise ValueError("publisher observation shape or ordinal changed")
        src = opf["rows"][int(local_id[-4:]) - 1]
        sample = held_rows.get(local_id)
        if not sample or src.get("source_local_id") != local_id or src["parse_status"] != "PARSED" or \
                src["opf_entry_sha256"] != record["opf_entry_sha256"] or \
                sample["original_opf_xml_sha256"] != record["opf_entry_sha256"] or \
                src["opf_entry_sha256"] in seen_hashes:
            raise ValueError("local OPF source receipt or held sample not matched uniquely")
        seen_hashes.add(src["opf_entry_sha256"])
        title, byline, isbn, form, imprint, date, pages, series, ordinal, slug = LOCKS[local_id]
        uri = "https://www.simonandschuster.com/books/" + slug + "/" + isbn
        if (record["publisher_title"], record["publisher_byline"], record["publisher_isbn13"],
            record["publisher_format"], record["publisher_imprint"], record["publisher_date"],
            record["publisher_pages"], record["publisher_series"], record["publisher_series_ordinal"],
            record["publisher_url"]) != (title, byline, isbn, form, imprint, date, pages, series, ordinal, uri) or \
                not isbn13_valid(isbn) or isbn in seen_isbns:
            raise ValueError("publisher product field, ISBN, locator or uniqueness mismatch")
        seen_isbns.add(isbn)
        u = urlsplit(uri)
        if (u.scheme, u.netloc, u.query, u.fragment) != ("https", "www.simonandschuster.com", "", ""):
            raise ValueError("unapproved product URL")
        prior = record["prior_same_family_publisher_candidate"]
        if local_id == "opf-local:0275":
            matches = [r for r in older["edition_candidates"] if r.get("candidate_id") == prior]
            if prior != "SSEBOOK-VOY-HOMECOMING-9780743475631" or len(matches) != 1 or \
                    matches[0].get("isbn13") != isbn or matches[0].get("source_locator") != uri:
                raise ValueError("accepted same-family Homecoming duplicate lineage missing")
        elif prior is not None:
            raise ValueError("unreviewed prior publisher linkage")
        if not isinstance(record["unresolved_difference"], str) or \
                not 40 <= len(record["unresolved_difference"]) <= 500:
            raise ValueError("unresolved edition/containment note absent")
        source_xml_isbn10 = None
        publisher_ebook = None
        if local_id == "opf-local:0110":
            source_xml_isbn10 = "0-7434-9997-2"
            publisher_ebook = record["source_isbn10_corresponding_publisher_ebook"]
            approved_ebook = {
                "url": "https://www.simonandschuster.com/books/" + slug + "/9780743499972",
                "isbn13": "9780743499972", "title": title, "byline": byline,
                "format": "EBOOK", "imprint": "Pocket Books/Star Trek",
                "date": "2004-10-01", "pages": 384,
                "correspondence_basis": "VALID_SOURCE_XML_ISBN10_CONVERTS_EXACTLY_TO_PUBLISHER_EBOOK_ISBN13_PLUS_POCKET_BOOKS_2004_METADATA",
                "private_source_edition_equivalence": "NOT_VERIFIED",
            }
            if (record["original_opf_xml_isbn10_literal"], record["original_opf_xml_identifier_tag"],
                record["original_opf_xml_isbn10_review_provenance"]) != (
                    "ISBN 0-7434-9997-2", "dc:Identifier",
                    "INDEPENDENT_HOSTILE_AUDITOR_OWNER_ZIP_READ_ONLY_XML") or \
                    not isbn10_valid(source_xml_isbn10) or \
                    src.get("publisher") != ["Pocket Books"] or src.get("date") != ["2004"] or \
                    src.get("isbn_checksum_valid") != [] or \
                    not isinstance(publisher_ebook, dict) or publisher_ebook != approved_ebook or \
                    not isbn13_valid(publisher_ebook["isbn13"]) or \
                    isbn10_to_isbn13(source_xml_isbn10) != publisher_ebook["isbn13"] or \
                    publisher_ebook["isbn13"] == isbn:
                raise ValueError("independent original OPF ISBN10/metadata derivative discrepancy drift")
        result.append({
            "record_type": "HELD_SOURCE_LOCAL_OPF_PUBLISHER_EDITION_CANDIDATE",
            "opf_source_local_id": local_id,
            "opf_title_literal": src["title"],
            "opf_creator_literals": src["creator"],
            "original_opf_xml_sha256_from_accepted_metadata": src["opf_entry_sha256"],
            "source_xml_isbn10_independently_observed": source_xml_isbn10,
            "source_identifier_corresponding_publisher_ebook": publisher_ebook,
            "source_identifier_edition_correspondence_scope": "METADATA_MATCH_NOT_SOURCE_TEXT_AUTHENTICATION" if publisher_ebook else None,
            "source_xml_isbn10_checksum_valid": isbn10_valid(source_xml_isbn10) if source_xml_isbn10 else None,
            "source_xml_isbn10_read_only_auditor": "INDEPENDENT_HOSTILE_AUDITOR_OWNER_ZIP_READ_ONLY_XML" if source_xml_isbn10 else None,
            "source_xml_identifier_tag_exact_case": "dc:Identifier" if source_xml_isbn10 else None,
            "accepted_derivative_isbn_checksum_valid": src.get("isbn_checksum_valid"),
            "accepted_derivative_missed_source_xml_isbn10": True if source_xml_isbn10 else None,
            "source_opf_publisher_literal": src.get("publisher"),
            "source_opf_date_literal": src.get("date"),
            "original_opf_zip_sha256_from_prior_custody": ZIP_SHA,
            "private_opf_xml_rehashed_by_this_consolidator": False,
            "publisher_source_group": "publisher:simonandschuster.com",
            "publisher_product_url": uri,
            "publisher_candidate_title": title,
            "publisher_candidate_byline": byline,
            "publisher_candidate_format": form,
            "publisher_candidate_imprint": imprint,
            "publisher_candidate_listed_date": date,
            "publisher_candidate_extent_pages": pages,
            "publisher_candidate_isbn13": isbn,
            "publisher_candidate_series": series,
            "publisher_candidate_series_number": ordinal,
            "prior_same_family_publisher_candidate": prior,
            "unresolved_difference": record["unresolved_difference"],
            "edition_equivalence": "NOT_VERIFIED",
            "source_to_work_binding": "NOT_VERIFIED",
            "global_work_identity": "NOT_RECONCILED",
            "omnibus_or_containment": "UNRESOLVED_DO_NOT_ASSUME_ONE_TO_ONE",
            "data_rights": "UNKNOWN",
            "public_explorer_release": "HELD",
            "coverage_effect": "NONE", "artwork_effect": "NONE",
        })
    return {
        "schema_version": "1.0.0", "status": "SEVEN_SOURCE_LOCAL_CANDIDATES_HELD",
        "accepted_main_at_start": "969626a", "source": SOURCE, "source_sha256": SOURCE_SHA,
        "opf_accepted_metadata_sha256": OPF_SHA, "opf_held_sample_sha256": HELD_SHA,
        "accepted_prior_publisher_lineage_sha256": OLDER_SHA,
        "historic_directory_sha256": BASE_SHA, "historic_directory_rows": 1214,
        "owner_opf_member_records": 347, "candidate_rows": len(result), "distinct_work_count": None,
        "distinct_publisher_product_edition_candidates": 8,
        "source_identifier_corresponding_publisher_ebook_candidates": 1,
        "independently_flagged_original_xml_isbn10_omitted_by_derivative": 1,
        "publisher_corporate_families": 1,
        "prior_same_family_candidate_reused": sum(r["prior_same_family_publisher_candidate"] is not None for r in result),
        "private_edition_equivalence_verified": 0, "work_admissions": 0,
        "public_explorer_release": "HELD", "coverage_effect": "NONE", "artwork_effect": "NONE",
        "rows": result,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    raw = encode(build())
    dest = ROOT / OUTPUT
    if args.check:
        if not dest.is_file() or dest.is_symlink() or dest.read_bytes() != raw:
            parser.error("HELD seven-row projection drift")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    print("PASS: 7 OPF↔publisher candidates HELD; 1 existing same-family edition, 0 Works")


if __name__ == "__main__":
    main()
