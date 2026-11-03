#!/usr/bin/env python3
"""Five direct-publisher bibliographic comparisons to HELD owner-local OPF metadata.

This validates deterministic evidence custody; it does not independently fetch
live publisher HTML, authenticate private ebook editions, or resolve Works.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
INPUT = "proposals/research/opf-five-official-editions-20261103/observations.json"
OUTPUT = "proposals/consolidator/opf-five-official-editions-20261103/crosschecks.json"
OPF = "proposals/librarian/private-opf-metadata-20261103/observations.json"
HELD = "proposals/consolidator/opf-source-local-review-sample-20261103/cards.json"
OLDER_PUB = "proposals/librarian/tos-classics-cover-editions-20261103/records.json"
BASE = "explorer/discovery-catalog.json"
INPUT_SHA = "6da05813bb4159db83ed4022c6560d1554f13a356eca825bd7c00dc6dd755105"
OPF_SHA = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
HELD_SHA = "ca251b3dfb98293526ad3c76c7169148e1344d106a2365304d0ddbfe36e5f06c"
OLDER_PUB_SHA = "6688f233a5bb6053c728f4619db297451f2c7929985e115e1ed888996423364d"
OPF_ZIP_SHA = "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f"
BASE_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
IDS = ("opf-local:0106", "opf-local:0155", "opf-local:0231", "opf-local:0236", "opf-local:0301")
ISBN = {"opf-local:0106": "9780743419505", "opf-local:0155": "9780743419673",
        "opf-local:0231": "9780743454186", "opf-local:0236": "9780671041137",
        "opf-local:0301": "9780743420549"}
TITLES = {"opf-local:0106": "Diplomatic Implausibility", "opf-local:0155": "The Final Reflection",
          "opf-local:0231": "Prime Directive", "opf-local:0236": "Spock's World",
          "opf-local:0301": "The 34th Rule"}
OPF_BYTES = {"opf-local:0106": 1096, "opf-local:0155": 2802,
             "opf-local:0231": 3178, "opf-local:0236": 951, "opf-local:0301": 1009}
PUBLISHER_FIELDS = {
    "opf-local:0106": ("Keith R. A. DeCandido", "Star Trek: The Next Generation", 61,
                       "2001-07-07", 272, "Diplomatic-Implausibility/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation"),
    "opf-local:0155": ("John M. Ford", "Star Trek: The Original Series", 16,
                       "2000-09-22", 256, "The-Final-Reflection/John-M-Ford/Star-Trek-The-Original-Series"),
    "opf-local:0231": ("Judith Reeves-Stevens", "Star Trek: The Original Series", None,
                       "2002-10-02", 406, "Prime-Directive/Judith-Reeves-Stevens/Star-Trek-The-Original-Series"),
    "opf-local:0236": ("Diane Duane", "Star Trek: The Original Series", None,
                       "2001-06-07", 400, "Spocks-World/Diane-Duane/Star-Trek-The-Original-Series"),
    "opf-local:0301": ("Armin Shimerman|David R. George III", "Star Trek: Deep Space Nine", 23,
                       "2000-09-22", 448, "The-34th-Rule/Armin-Shimerman/Star-Trek-Deep-Space-Nine"),
}
# Source page metadata is human observed at the exact URLs in the separately
# pinned observations packet. Distinct product pages share one publisher family.


def encode(data: dict) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def read_pinned(root: Path, name: str, sha: str | None = None) -> dict:
    path = root / name
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("missing or unsafe accepted source: " + name)
    raw = path.read_bytes()
    if len(raw) > 2_000_000 or (sha and hashlib.sha256(raw).hexdigest() != sha):
        raise ValueError("accepted input source receipt changed: " + name)
    return json.loads(raw)


def isbn13_valid(value: str) -> bool:
    return len(value) == 13 and value.isascii() and value.isdecimal() and \
        sum(int(x) * (1 if i % 2 == 0 else 3) for i, x in enumerate(value)) % 10 == 0


def verify_observations(source: dict, opf: dict, held: dict, older_publisher: dict) -> list[dict]:
    expected_flags = {
        "schema_version": "1.0.0", "proposal_id": "opf-five-official-edition-metadata-20261103",
        "baseline_accepted_main": "05d05de1c0238ed7ff39bd04427795e351f9b68b",
        "observed_on": "2026-11-03", "method": "DIRECT_OFFICIAL_PUBLISHER_PRODUCT_PAGE_METADATA_READ",
        "publisher_source_group": "publisher:simonandschuster.com",
        "publisher_source_independence": "ONE_CORPORATE_FAMILY_FOR_ALL_FIVE",
        "opf_metadata_source": OPF, "opf_metadata_source_sha256": OPF_SHA,
        "owner_private_opf_archive_members_independently_rehashed": True,
        "original_opf_zip_sha256": OPF_ZIP_SHA,
        "source_rehash_method": "INDEPENDENT_LIBRARIAN_READ_ONLY_STREAMED_ZIP_AND_FIVE_UNCOMPRESSED_OPF_XML",
        "existing_publisher_candidate_input": OLDER_PUB,
        "existing_publisher_candidate_input_sha256": OLDER_PUB_SHA,
        "publisher_raw_html_archived": False, "publisher_page_snapshot_sha256": None,
        "copyrighted_ebook_text_or_images_exported": False,
        "owner_private_edition_equivalence": "NOT_VERIFIED",
        "source_to_work_binding": "NOT_VERIFIED",
        "work_admission_effect": "NONE", "coverage_effect": "NONE",
        "artwork_release_effect": "NONE", "public_synopsis_effect": "NONE",
    }
    if not isinstance(source, dict) or any(source.get(k) != v for k, v in expected_flags.items()):
        raise ValueError("research observation scope or held effect changed")
    if set(source) != {*expected_flags, "rows"} or len(source["rows"]) != 5 or len(opf["rows"]) != 347 or \
            held.get("selected_rows") != 39:
        raise ValueError("expected five records drawn from accepted 347/39 OPF source-local inventory")
    held_by_id = {row["source_local_id"]: row for row in held["card_rows"]}
    cards = []
    for expected_id, record in zip(IDS, source["rows"]):
        if record.get("opf_source_local_id") != expected_id or set(record) != {
            "opf_source_local_id", "opf_title_literal", "opf_creator_literals", "opf_entry_sha256",
            "opf_entry_uncompressed_bytes", "existing_publisher_candidate_id",
            "opf_isbn_candidates", "publisher_url", "publisher_title", "publisher_byline",
            "publisher_series", "publisher_series_ordinal", "publisher_format", "publisher_imprint",
            "publisher_product_date", "publisher_pages", "publisher_isbn13",
            "publisher_visible_field_basis", "candidate_match_basis", "unresolved_note",
            "edition_equivalence", "work_identity",
        }:
            raise ValueError("unexpected OPF-publisher crosscheck row or source ID")
        ordinal = int(expected_id.split(":")[1]); observed = opf["rows"][ordinal - 1]
        local = held_by_id.get(expected_id)
        if not local or record["opf_entry_uncompressed_bytes"] != OPF_BYTES[expected_id] or \
                observed.get("source_local_id") != expected_id or observed.get("parse_status") != "PARSED" or \
                (record["opf_title_literal"], record["opf_creator_literals"], record["opf_entry_sha256"],
                 record["opf_isbn_candidates"]) != (observed["title"][0], observed["creator"],
                                                    observed["opf_entry_sha256"], observed["isbn_checksum_valid"]) or \
                record["opf_entry_sha256"] != local["original_opf_xml_sha256"]:
            raise ValueError("publisher crosswalk does not preserve original local OPF metadata evidence")
        byline, series, series_ordinal, listed_date, pages, slug = PUBLISHER_FIELDS[expected_id]
        if record["publisher_isbn13"] != ISBN[expected_id] or record["publisher_title"] != TITLES[expected_id] or \
                ("|".join(record["publisher_byline"]), record["publisher_series"],
                 record["publisher_series_ordinal"], record["publisher_product_date"],
                 record["publisher_pages"]) != (byline, series, series_ordinal, listed_date, pages) or \
                not isbn13_valid(record["publisher_isbn13"]):
            raise ValueError("unreviewed ISBN or publisher title")
        url = urlsplit(record["publisher_url"])
        if (url.scheme, url.netloc, url.query, url.fragment) != ("https", "www.simonandschuster.com", "", "") or \
                url.path != "/books/" + slug + "/" + record["publisher_isbn13"]:
            raise ValueError("unapproved publisher product locator")
        if record["publisher_format"] != "EBOOK" or record["publisher_imprint"] != "Pocket Books/Star Trek" or \
                record["publisher_visible_field_basis"] != "PRODUCT_DETAILS_AND_BYLINE" or \
                record["edition_equivalence"] != "NOT_VERIFIED" or record["work_identity"] != "NOT_RECONCILED" or \
                not isinstance(record["publisher_pages"], int) or not 100 <= record["publisher_pages"] <= 1000 or \
                not isinstance(record["publisher_byline"], list) or not record["publisher_byline"] or \
                not all(isinstance(x, str) and x for x in record["publisher_byline"]) or \
                not isinstance(record["unresolved_note"], str) or not 20 <= len(record["unresolved_note"]) <= 400 or \
                not record["candidate_match_basis"].startswith("TITLE"):
            raise ValueError("publisher evidence shape or hold changed")
        existing_id = record["existing_publisher_candidate_id"]
        if expected_id == "opf-local:0155":
            edition_candidates = older_publisher.get("edition_candidates", [])
            matching = [e for e in edition_candidates if e.get("edition_candidate_id") == existing_id]
            if existing_id != "TOS-FINAL-REFLECTION-EBOOK-9780743419673" or len(matching) != 1 or \
                    matching[0].get("isbn13") != record["publisher_isbn13"] or \
                    matching[0].get("publisher_product_url") != record["publisher_url"]:
                raise ValueError("prior accepted same-family publisher candidate lineage drift")
        elif existing_id is not None:
            raise ValueError("unsupported accepted duplicate publisher candidate")
        cards.append({
            "crosscheck_id": "publisher-opf-metadata:" + expected_id,
            "opf_source_local_id": expected_id,
            "opf_title_as_recorded": record["opf_title_literal"],
            "opf_creator_as_recorded": record["opf_creator_literals"],
            "opf_xml_sha256": record["opf_entry_sha256"],
            "opf_xml_uncompressed_bytes_read_only_rehashed": record["opf_entry_uncompressed_bytes"],
            "source_opf_zip_sha256": OPF_ZIP_SHA,
            "publisher_product_url": record["publisher_url"],
            "publisher_edition_candidate_title": record["publisher_title"],
            "publisher_byline": record["publisher_byline"],
            "publisher_ebook_isbn13": record["publisher_isbn13"],
            "publisher_ebook_date": record["publisher_product_date"],
            "publisher_ebook_extent_pages": record["publisher_pages"],
            "publisher_ebook_imprint": record["publisher_imprint"],
            "publisher_series": record["publisher_series"],
            "publisher_series_ordinal": record["publisher_series_ordinal"],
            "source_observation": INPUT,
            "source_observation_sha256": INPUT_SHA,
            "prior_same_family_publisher_candidate": existing_id,
            "metadata_source": OPF,
            "candidate_basis": record["candidate_match_basis"],
            "unresolved_difference": record["unresolved_note"],
            "publisher_page_archived": False,
            "private_edition_equivalence": "NOT_VERIFIED",
            "work_identity": "NOT_RECONCILED",
            "public_explorer_release": "HELD",
            "admission_effect": "NONE",
            "coverage_effect": "NONE",
            "artwork_release_effect": "NONE",
        })
    return cards


def build(root: Path = ROOT) -> dict:
    source = read_pinned(root, INPUT, INPUT_SHA)
    opf = read_pinned(root, OPF, OPF_SHA)
    held = read_pinned(root, HELD, HELD_SHA)
    older_publisher = read_pinned(root, OLDER_PUB, OLDER_PUB_SHA)
    read_pinned(root, BASE, BASE_SHA)
    cards = verify_observations(source, opf, held, older_publisher)
    return {
        "schema_version": "1.0.0", "data_status": "PUBLISHER_EDITION_CANDIDATES_HELD_SOURCE_LOCAL_ONLY",
        "row_count": len(cards), "rows": cards, "source_observation": INPUT,
        "source_observation_sha256": INPUT_SHA,
        "opf_metadata_source_sha256": OPF_SHA, "historic_directory_sha256": BASE_SHA,
        "source_opf_zip_sha256": OPF_ZIP_SHA,
        "prior_publisher_input_sha256": OLDER_PUB_SHA,
        "historic_directory_rows": 1214, "distinct_work_count": None,
        "verified_private_edition_bindings": 0,
        "source_family_count": 1, "source_family": "publisher:simonandschuster.com",
        "public_explorer_release": "HELD", "admission_effect": "NONE",
        "work_admission_effect": "NONE", "coverage_effect": "NONE",
        "artwork_release_effect": "NONE", "public_synopsis_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    raw = encode(build())
    dest = ROOT / OUTPUT
    if args.check:
        if not dest.is_file() or dest.is_symlink() or dest.read_bytes() != raw:
            parser.error("five publisher crosschecks differ from pinned observations")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    print("PASS: five direct-publisher edition candidates; zero private-edition or Work bindings")


if __name__ == "__main__":
    main()
