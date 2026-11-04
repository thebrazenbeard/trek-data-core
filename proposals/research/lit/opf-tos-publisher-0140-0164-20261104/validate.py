"""Fail-closed HELD literary publisher packet checks; no live network or ebook reads.

Source page fields were independently observed from the publisher's rendered
product pages. This deterministic validator pins the *report*, not the
current mutable web page, the private OPF body or any canonical Work identity.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "proposals/librarian/private-opf-metadata-20261103/observations.json"
PACKET = Path(__file__).with_name("records.json")
SOURCE_SHA = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
PACKET_SHA = "5e20783761b1651713d69e08eaa8395115bc0ec4561f44b3203ce1654a622410"
IDS = tuple(f"opf-local:{n:04d}" for n in range(140, 165) if n not in {150, 155})
EXPECTED_FIELDS = {
    "schema_version": "1.0.0",
    "proposal_id": "LIT-TOS-OPF-0140-0164-PUBLISHER-20261104",
    "accepted_main_at_start": "3028765359001b90bc3e6b5c1835ee283b326e91",
    "owner_opf_observations_sha256": SOURCE_SHA,
    "observation_date": "2026-11-04",
    "method": "DIRECT_OFFICIAL_RENDERED_PUBLISHER_PAGE_OPEN_AND_SECTION_READ",
    "publisher_family": "publisher:simonandschuster.com",
    "independent_source_families": 1,
    "source_retrieved": 23,
    "publisher_pages_actually_read": 23,
    "source_local_records_generated": 23,
    "batch_manifest_generated": True,
    "publisher_page_sections_read": ["visible product title/format/byline", "About the Book", "Product Details"],
    "publisher_page_raw_bytes_snapshotted": False,
    "owner_private_opf_xml_or_ebook_prose_read_this_batch": False,
    "publisher_blurb_claim_scope": "PUBLISHER_PROMOTIONAL_DESCRIPTION_NOT_NARRATIVE_FACT_OR_CANON",
    "source_rights": "UNKNOWN",
    "edition_equivalence": "NOT_VERIFIED",
    "source_work_bindings": 0,
    "global_work_identity": "NOT_RECONCILED",
    "work_admissions": 0,
    "close_reads": 0,
    "public_explorer_release": "HELD",
    "coverage_effect": "NONE",
    "artwork_effect": "NONE",
}
ROW_FIELDS = {"opf_source_local_id", "opf_entry_sha256", "publisher_url", "publisher_title",
              "publisher_subtitle", "publisher_byline", "publisher_format", "publisher_imprint",
              "publisher_date", "publisher_pages", "publisher_isbn13",
              "source_isbn10_to_publisher_isbn13", "hold", "publisher_blurb_paraphrase"}


def isbn13_valid(text: str) -> bool:
    return bool(re.fullmatch(r"[0-9]{13}", text)) and sum(
        int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(text)) % 10 == 0


def isbn10_to13(text: str) -> str:
    if not re.fullmatch(r"[0-9]{9}[0-9X]", text):
        raise ValueError("unrecognized ISBN10")
    check10 = sum((10 - i) * int(c) for i, c in enumerate(text[:9]))
    check10 += 10 if text[-1] == "X" else int(text[-1])
    if check10 % 11:
        raise ValueError("source ISBN10 checksum invalid")
    prefix = "978" + text[:9]
    check = (10 - sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(prefix)) % 10) % 10
    return prefix + str(check)


def validate_packet(report: dict, accepted: dict) -> tuple[int, int]:
    if not isinstance(report, dict) or set(report) != set(EXPECTED_FIELDS) | {"rows"}:
        raise ValueError("unexpected publisher-packet envelope")
    for field, expected in EXPECTED_FIELDS.items():
        if type(report[field]) is not type(expected):
            raise ValueError(f"publisher packet type drift: {field}")
        if report[field] != expected:
            raise ValueError(f"publisher packet attempted drift: {field}")
    if len(accepted.get("rows", [])) != 347:
        raise ValueError("unexpected OPF owner-source ledger")
    rows = report["rows"]
    if not isinstance(rows, list) or len(rows) != 23:
        raise ValueError("source-retrieved/read/record cardinality mismatch")
    if tuple(row.get("opf_source_local_id") for row in rows if isinstance(row, dict)) != IDS:
        raise ValueError("OPF local IDs changed/duplicated/overlap accepted audited IDs")
    publisher_isbns = set()
    isbn10_matches = 0
    for row in rows:
        if set(row) != ROW_FIELDS:
            raise ValueError("unreviewed publisher field shape")
        sid = row["opf_source_local_id"]
        source = accepted["rows"][int(sid.rsplit(":", 1)[1]) - 1]
        if source["source_local_id"] != sid or source["opf_entry_sha256"] != row["opf_entry_sha256"]:
            raise ValueError("source-local OPF fingerprint mismatch")
        if row["publisher_format"] != "EBOOK" or row["publisher_imprint"] != "Pocket Books/Star Trek":
            raise ValueError("unreviewed publisher format or imprint")
        if not isinstance(row["publisher_title"], str) or not row["publisher_title"].strip():
            raise ValueError("missing publisher title")
        if row["publisher_subtitle"] is not None and (not isinstance(row["publisher_subtitle"], str)
                                                         or not row["publisher_subtitle"].strip()):
            raise ValueError("invalid publisher subtitle")
        byline = row["publisher_byline"]
        if not isinstance(byline, list) or not byline or len(byline) > 3 or any(
            not isinstance(c, str) or not c.strip() or len(c) > 100 for c in byline):
            raise ValueError("missing or malformed publisher byline")
        try:
            date.fromisoformat(row["publisher_date"])
        except (ValueError, TypeError) as exc:
            raise ValueError("invalid publisher date") from exc
        if type(row["publisher_pages"]) is not int or not 1 <= row["publisher_pages"] <= 1500:
            raise ValueError("unbounded publisher extent")
        isbn = row["publisher_isbn13"]
        if not isinstance(isbn, str) or not isbn13_valid(isbn) or isbn in publisher_isbns:
            raise ValueError("duplicate or checksum-invalid publisher ISBN13")
        publisher_isbns.add(isbn)
        url = urlsplit(row["publisher_url"])
        if (url.scheme != "https" or url.hostname != "www.simonandschuster.com"
                or not url.path.startswith("/books/") or not url.path.endswith("/" + isbn)
                or url.query or url.fragment or url.username or url.password):
            raise ValueError("publisher URL/ISBN association not exact first-party page")
        if not isinstance(row["hold"], str) or len(row["hold"]) > 130 or not row["hold"]:
            raise ValueError("missing publisher/source uncertainty")
        paraphrase = row["publisher_blurb_paraphrase"]
        if not isinstance(paraphrase, str) or not 40 <= len(paraphrase) <= 260 or "\n" in paraphrase:
            raise ValueError("missing or unbounded original short publisher blurb paraphrase")
        origin_isbns = source["isbn_checksum_valid"]
        observed_status = row["source_isbn10_to_publisher_isbn13"]
        if origin_isbns:
            if len(origin_isbns) != 1 or isbn10_to13(origin_isbns[0]) != isbn or observed_status != "MATCH":
                raise ValueError("source ISBN10/publisher ISBN13 match not proven")
            isbn10_matches += 1
        elif observed_status != "NO_SOURCE_ISBN":
            raise ValueError("source missing ISBN is not edition agreement")
    if isbn10_matches != 5:
        raise ValueError("unexpected source-local ISBN10 alignment count")
    row_map = {r["opf_source_local_id"]: r for r in rows}
    if (accepted["rows"][162]["creator"] != ["Kevin Underwood"]
        or row_map["opf-local:0163"]["publisher_byline"] != ["J.M. Dillard"]
        or row_map["opf-local:0163"]["hold"] != "CRITICAL_CREATOR_CONFLICT_OPF_KEVIN_UNDERWOOD_VS_PUBLISHER_JM_DILLARD"):
        raise ValueError("Mindshadow source-versus-publisher creator contradiction obscured")
    if (not accepted["rows"][156]["title"][0].startswith("Rihannsu #1")
        or row_map["opf-local:0157"]["publisher_isbn13"] != "9780743419697"
        or row_map["opf-local:0157"]["hold"] != "COMPATIBLE_PUBLISHER_RIHANNSU_1_AND_TOS_18_LABELS_PRIVATE_EDITION_UNVERIFIED"):
        raise ValueError("compatible Rihannsu #1 and TOS #18 labels incorrectly reported as conflicting")
    if (row_map["opf-local:0140"]["publisher_title"], row_map["opf-local:0140"]["publisher_subtitle"]) != (
        "Star Trek", "The Motion Picture"):
        raise ValueError("Motion Picture official title and subtitle flattened")
    if (accepted["rows"][143]["creator"] != ["Sondra Marshak", "Myrna Culbreath"]
        or row_map["opf-local:0144"]["publisher_byline"] != ["Myrna Culbreath", "Sondra Marshak"]):
        raise ValueError("Prometheus Design byline order must retain provenance")
    for n in (145, 152, 159, 160):
        if accepted["rows"][n - 1]["creator"] != [] or "OPF_CREATOR_ABSENT" not in row_map[f"opf-local:{n:04d}"]["hold"]:
            raise ValueError("publisher author silently projected into absent source OPF creator")
    return len(rows), isbn10_matches


def validate() -> tuple[int, int]:
    raw_source, raw_report = SOURCE.read_bytes(), PACKET.read_bytes()
    if hashlib.sha256(raw_source).hexdigest() != SOURCE_SHA:
        raise ValueError("accepted private-derived OPF source packet changed")
    if hashlib.sha256(raw_report).hexdigest() != PACKET_SHA:
        raise ValueError("held publisher receipt changed without review")
    accepted = json.loads(raw_source)
    report = json.loads(raw_report)
    return validate_packet(report, accepted)


if __name__ == "__main__":
    count, aligned = validate()
    print(f"LIT_OPF_TOS_HELD_OK: {count} publisher pages read/records, {aligned} ISBN10 alignments, zero Work admissions")
