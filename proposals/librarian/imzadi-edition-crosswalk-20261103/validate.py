#!/usr/bin/env python3
"""Validate four page-read Simon & Schuster edition *leads*, not Source/Work admissions."""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKET = HERE / "records.json"
CATALOG = ROOT / "explorer/discovery-catalog.json"
OPF_OBSERVATIONS = ROOT / "proposals/librarian/private-opf-metadata-20261103/observations.json"
BASELINE = "51b7c99a15d8295ba9d87f2088d36866140c1a79"
CATALOG_SHA256 = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
OPF_SHA256 = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
CATALOG_PATH = "explorer/discovery-catalog.json"
OPF_PATH = "proposals/librarian/private-opf-metadata-20261103/observations.json"
RIGHTS_HOLD = "METADATA_ONLY_NO_SOURCE_OR_IMAGE_REUSE_RIGHTS_ESTABLISHED"
SOURCE_HOLD = "NO_FULL_SOURCE_OR_PRODUCT_SNAPSHOT"
PACKET_KEYS = {
    "schema_version", "batch_id", "role", "proposal_only", "observed_date_utc",
    "baseline_accepted_main", "source_family", "source_read_class",
    "source_page_snapshots_available", "publisher_product_page_read_count",
    "corpus_admission_effect", "literary_coverage_effect", "source_work_binding_effect",
    "image_download_or_display_effect", "prose_or_audio_custody_effect",
    "catalog_gap_snapshot", "private_opf_title_lead", "records", "crosswalk_decisions",
}
RECORD_KEYS = {
    "local_id", "publisher_title", "title_family_local_id", "publisher_product_url",
    "publisher_creator", "isbn13", "edition_format", "publisher_imprint",
    "publisher_product_date", "extent_value", "extent_unit", "reader",
    "product_details_line_anchor", "rights_status", "source_custody",
}
BASE_PATH = "https://www.simonandschuster.com/books/"
EDITION_ROWS = {
    # local ID -> (title, title family, product URL suffix, ISBN13, format,
    #              imprint, publisher date, extent, unit, reader, page line)
    "sns-imzadi-forever-trade-9780743485104": (
        "Imzadi Forever", "publisher-title-imzadi-forever",
        "Imzadi-Forever/Peter-David/Star-Trek-The-Next-Generation/9780743485104",
        "9780743485104", "TRADE_PAPERBACK", "Pocket Books/Star Trek", "2003-12-02", 432, "PAGES", None, 381),
    "sns-signature-imzadi-forever-ebook-9780743492645": (
        "Star Trek: Signature Edition: Imzadi Forever", "publisher-title-imzadi-forever",
        "Star-Trek-Signature-Edition-Imzadi-Forever/Peter-David/Star-Trek-The-Next-Generation/9780743492645",
        "9780743492645", "EBOOK", "Pocket Books/Star Trek", "2003-12-02", 432, "PAGES", None, 264),
    "sns-triangle-imzadi-ii-ebook-9780743420716": (
        "Star Trek: The Next Generation: Triangle: Imzadi II", "publisher-title-triangle-imzadi-ii",
        "Star-Trek-The-Next-Generation-Triangle-Imzadi-II/Peter-David/Star-Trek-The-Next-Generation/9780743420716",
        "9780743420716", "EBOOK", "Pocket Books/Star Trek", "2000-09-22", 384, "PAGES", None, 384),
    "sns-triangle-imzadi-ii-audio-9780743566827": (
        "Star Trek: The Next Generation: Triangle: Imzadi II", "publisher-title-triangle-imzadi-ii",
        "Star-Trek-The-Next-Generation-Triangle-Imzadi-II/Peter-David/Star-Trek-The-Next-Generation/9780743566827",
        "9780743566827", "ABRIDGED_AUDIO_DOWNLOAD", "Simon & Schuster Audio", "1998-10-01", 3, "HOURS", "Robert O'Reilly", 292),
}
EXPECTED_CROSSWALK = {
    "within_title_family": "PUBLISHER_PRODUCT_FORMAT_OPTIONS_OBSERVED_NOT_WORK_RECONCILIATION",
    "imzadi_forever_to_triangle_imzadi_ii": "TITLE_RELATEDNESS_DISCOVERY_ONLY_CONTAINMENT_UNVERIFIED",
    "private_opf_to_publisher_isbn": "UNRESOLVED_NO_ISBN_IN_PRIVATE_OPF_ENTRY",
    "two_title_families_are_one_canonical_work": "NOT_ASSERTED",
}


def _ensure(test: bool, failure: str) -> None:
    if not test:
        raise ValueError(failure)


def _keys(data: object, required: set[str], where: str) -> None:
    _ensure(isinstance(data, dict) and set(data) == required, f"{where}: closed schema drift")


def _isbn13_valid(code: str) -> bool:
    return (isinstance(code, str) and len(code) == 13 and code.isascii() and code.isdigit() and
            sum(int(ch) * (1 if i % 2 == 0 else 3) for i, ch in enumerate(code)) % 10 == 0)


def parse_json_no_duplicates(source: str | bytes) -> dict:
    """Never silently discard a contradictory field from raw proposal/source JSON."""
    def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
        out = {}
        for key, value in pairs:
            _ensure(key not in out, f"duplicate JSON key: {key}")
            out[key] = value
        return out

    result = json.loads(source, object_pairs_hook=unique_pairs)
    _ensure(isinstance(result, dict), "JSON root must be an object")
    return result


def validate(packet: dict, catalog_bytes: bytes, opf_bytes: bytes) -> int:
    _keys(packet, PACKET_KEYS, "packet")
    _ensure(packet["schema_version"] == "1.0.0", "schema version drift")
    _ensure(packet["batch_id"] == "LIBRARIAN.IMZADI.EDITION.CROSSWALK.20261103", "batch ID drift")
    _ensure(packet["role"] == "LIBRARIAN" and packet["proposal_only"] is True, "role/effect drift")
    _ensure(packet["baseline_accepted_main"] == BASELINE, "baseline drift")
    _ensure(packet["observed_date_utc"] == "2026-11-03", "unreviewed observation date")
    _ensure(packet["source_family"] == "publisher:simonandschuster.com", "source lineage drift")
    _ensure(packet["source_read_class"] == "FIRST_PARTY_RENDERED_PRODUCT_DETAILS", "source read class drift")
    _ensure(packet["source_page_snapshots_available"] is False, "unsupported source snapshot")
    _ensure(packet["publisher_product_page_read_count"] == 4, "unreviewed page count")
    for status in ("corpus_admission_effect", "literary_coverage_effect", "source_work_binding_effect",
                   "image_download_or_display_effect", "prose_or_audio_custody_effect"):
        _ensure(packet[status] == "NONE", f"{status} must remain NONE")

    catalog_gap = packet["catalog_gap_snapshot"]
    _keys(catalog_gap, {"path", "sha256", "source_local_rows", "literature_rows",
                        "publisher_product_title_rows_for_four_observations"}, "catalog snapshot")
    _ensure(catalog_gap["path"] == CATALOG_PATH and catalog_gap["sha256"] == CATALOG_SHA256,
            "reviewed catalog path/digest drift")
    _ensure(hashlib.sha256(catalog_bytes).hexdigest() == CATALOG_SHA256, "catalog bytes drift")
    catalog = parse_json_no_duplicates(catalog_bytes)
    rows = catalog["rows"]
    lit_rows = [r for r in rows if r.get("medium") == "LITERATURE"]
    _ensure(len(rows) == catalog_gap["source_local_rows"] == 1214 and
            len(lit_rows) == catalog_gap["literature_rows"] == 9, "directory denominator drift")
    _ensure(not any(r.get("title") in {data[0] for data in EDITION_ROWS.values()} for r in lit_rows) and
            catalog_gap["publisher_product_title_rows_for_four_observations"] == 0,
            "literary title overlap or gap count drift")

    private = packet["private_opf_title_lead"]
    _keys(private, {"source_path", "source_sha256", "source_local_id", "entry_fingerprint_sha256",
                    "title", "creator", "publisher", "date_year", "isbn_present", "crosswalk_class",
                    "exact_publisher_edition_binding"}, "private OPF crosswalk")
    _ensure(private == {
        "source_path": OPF_PATH, "source_sha256": OPF_SHA256, "source_local_id": "opf-local:0128",
        "entry_fingerprint_sha256": "f36bfb5d8c37a5045d24298385c629d08cb064d8e6228acd7bd96dc6eb074232",
        "title": "Imzadi Forever", "creator": "Peter David", "publisher": "Pocket Books",
        "date_year": "2003", "isbn_present": False,
        "crosswalk_class": "TITLE_CREATOR_PUBLISHER_YEAR_LEAD_ONLY",
        "exact_publisher_edition_binding": "NOT_VERIFIED",
    }, "private OPF cannot be assigned a specific ISBN")
    _ensure(hashlib.sha256(opf_bytes).hexdigest() == OPF_SHA256, "OPF bytes drift")
    opf_rows = parse_json_no_duplicates(opf_bytes)["rows"]
    matches = [r for r in opf_rows if r.get("source_local_id") == private["source_local_id"]]
    _ensure(len(matches) == 1 and matches[0].get("opf_entry_sha256") == private["entry_fingerprint_sha256"] and
            matches[0].get("title") == [private["title"]] and
            matches[0].get("creator") == [private["creator"]] and
            matches[0].get("publisher") == [private["publisher"]] and
            matches[0].get("date") == [private["date_year"]] and
            matches[0].get("isbn_checksum_valid") == [], "OPF metadata crosswalk not source-local")

    _ensure(packet["crosswalk_decisions"] == EXPECTED_CROSSWALK, "unreviewed crosswalk/containment claim")
    editions = packet["records"]
    _ensure(isinstance(editions, list) and len(editions) == 4, "four exact editions required")
    seen: set[str] = set()
    for row in editions:
        _keys(row, RECORD_KEYS, "edition row")
        local = row["local_id"]
        _ensure(local in EDITION_ROWS and local not in seen, "unreviewed or duplicate edition ID")
        seen.add(local)
        expected = EDITION_ROWS[local]
        observed = (row["publisher_title"], row["title_family_local_id"],
                    row["publisher_product_url"].removeprefix(BASE_PATH), row["isbn13"],
                    row["edition_format"], row["publisher_imprint"], row["publisher_product_date"],
                    row["extent_value"], row["extent_unit"], row["reader"], row["product_details_line_anchor"])
        _ensure(observed == expected, f"{local}: unreviewed publisher product edition data")
        _ensure(_isbn13_valid(row["isbn13"]), f"{local}: invalid ISBN13 checksum")
        parsed = urlsplit(row["publisher_product_url"])
        _ensure(parsed.scheme == "https" and parsed.netloc == "www.simonandschuster.com" and
                not parsed.query and not parsed.fragment and not parsed.username and not parsed.password,
                f"{local}: unsafe publisher locator")
        _ensure(row["publisher_creator"] == "Peter David", f"{local}: creator drift")
        _ensure(row["rights_status"] == RIGHTS_HOLD and row["source_custody"] == SOURCE_HOLD,
                f"{local}: rights or source custody promotion")
        _ensure(datetime.date.fromisoformat(row["publisher_product_date"]).isoformat() ==
                row["publisher_product_date"], f"{local}: invalid product date")
    _ensure(seen == set(EDITION_ROWS), "missing reviewed edition")
    return len(seen)


def main() -> None:
    proposal = parse_json_no_duplicates(PACKET.read_text(encoding="utf-8"))
    count = validate(proposal, CATALOG.read_bytes(), OPF_OBSERVATIONS.read_bytes())
    print(f"PASS: {count} publisher edition metadata candidates; 1 OPF title-only lead; 0 rights/Source/Work/coverage effects")


if __name__ == "__main__":
    main()
