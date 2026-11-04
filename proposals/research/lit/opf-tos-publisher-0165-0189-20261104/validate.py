"""Deterministic fail-closed checks for a held 24-page official publisher report.

This validator pins the *worker's report*, not current publisher HTML or a
private literary edition. It cannot admit Source, Work, prose or coverage.
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
PACKET_SHA = "2b9f17bf26dc0a32c307c0181c36766d4b1a7d8e9ea2e049d5d4125a0fa625a7"
IDS = tuple(f"opf-local:{n:04d}" for n in range(165, 190) if n != 178)
EXPECTED_FIELDS = {
    "schema_version": "1.0.0",
    "proposal_id": "LIT-TOS-OPF-0165-0189-PUBLISHER-20261104",
    "accepted_main_at_start": "3028765359001b90bc3e6b5c1835ee283b326e91",
    "owner_opf_observations_sha256": SOURCE_SHA,
    "observation_date": "2026-11-04",
    "method": "DIRECT_OFFICIAL_RENDERED_PUBLISHER_PAGE_OPEN_AND_SECTION_READ",
    "publisher_family": "publisher:simonandschuster.com",
    "independent_source_families": 1,
    "source_retrieved": 24,
    "publisher_pages_actually_read": 24,
    "source_local_records_generated": 24,
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
              "publisher_date", "publisher_pages", "publisher_isbn13", "hold", "publisher_blurb_paraphrase"}


def isbn13_valid(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9]{13}", value)) and sum(
        int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(value)) % 10 == 0


def validate_packet(report: dict, source: dict) -> tuple[int, int]:
    if not isinstance(report, dict) or set(report) != set(EXPECTED_FIELDS) | {"rows"}:
        raise ValueError("unreviewed publisher envelope")
    for key, expected in EXPECTED_FIELDS.items():
        if type(report[key]) is not type(expected):
            raise ValueError(f"publisher packet type drift: {key}")
        if report[key] != expected:
            raise ValueError(f"publisher packet attempted drift: {key}")
    if len(source.get("rows", [])) != 347:
        raise ValueError("unexpected source-local OPF ledger")
    rows = report["rows"]
    if not isinstance(rows, list) or len(rows) != 24:
        raise ValueError("source-retrieved/read/record cardinality discrepancy")
    if tuple(r.get("opf_source_local_id") for r in rows if isinstance(r, dict)) != IDS:
        raise ValueError("OPF local IDs changed, duplicated or overlap a prior tranche")
    seen = set()
    for row in rows:
        if set(row) != ROW_FIELDS:
            raise ValueError("unreviewed publisher row fields")
        sid = row["opf_source_local_id"]
        origin = source["rows"][int(sid.rsplit(":", 1)[1]) - 1]
        if origin["source_local_id"] != sid or origin["opf_entry_sha256"] != row["opf_entry_sha256"]:
            raise ValueError("source-local OPF fingerprint mismatch")
        if origin["isbn_checksum_valid"]:
            raise ValueError("source ISBN10 unexpectedly available: requires independent comparison")
        if row["publisher_format"] != "EBOOK" or row["publisher_imprint"] != "Pocket Books/Star Trek":
            raise ValueError("unsupported format or publisher imprint")
        if not isinstance(row["publisher_title"], str) or not row["publisher_title"].strip():
            raise ValueError("missing publisher product title")
        if row["publisher_subtitle"] is not None and (not isinstance(row["publisher_subtitle"], str)
                                                       or not row["publisher_subtitle"].strip()):
            raise ValueError("invalid publisher subtitle")
        creators = row["publisher_byline"]
        if (not isinstance(creators, list) or not 1 <= len(creators) <= 3 or
                any(not isinstance(c, str) or not c.strip() or len(c) > 100 for c in creators)):
            raise ValueError("malformed publisher byline")
        try:
            date.fromisoformat(row["publisher_date"])
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid official product date") from exc
        if type(row["publisher_pages"]) is not int or not 1 <= row["publisher_pages"] <= 1500:
            raise ValueError("invalid official product page count")
        isbn = row["publisher_isbn13"]
        if not isinstance(isbn, str) or not isbn13_valid(isbn) or isbn in seen:
            raise ValueError("duplicate or invalid ISBN13")
        seen.add(isbn)
        url = urlsplit(row["publisher_url"])
        if (url.scheme != "https" or url.hostname != "www.simonandschuster.com"
                or not url.path.startswith("/books/") or not url.path.endswith("/" + isbn)
                or url.query or url.fragment or url.username or url.password):
            raise ValueError("unreviewed first-party publisher URL/ISBN association")
        if not isinstance(row["hold"], str) or not 1 <= len(row["hold"]) <= 150:
            raise ValueError("missing source-relative uncertainty hold")
        summary = row["publisher_blurb_paraphrase"]
        if not isinstance(summary, str) or not 40 <= len(summary) <= 260 or "\n" in summary:
            raise ValueError("missing or overlong short original publisher blurb paraphrase")

    byid = {r["opf_source_local_id"]: r for r in rows}
    if (source["rows"][168]["creator"] != ["Carmen Carter"] or
            byid["opf-local:0169"]["publisher_byline"] != ["Carter Carmen"] or
            "BYLINE_CARTER_CARMEN_VS_PUBLISHER_BIO_AND_OPF_CARMEN_CARTER" not in byid["opf-local:0169"]["hold"]):
        raise ValueError("Carter Carmen publisher name-order discrepancy erased")
    if (byid["opf-local:0170"]["publisher_subtitle"] is not None or
            "COMPATIBLE_PUBLISHER_RIHANNSU_2_TOS_35_LABELS" not in byid["opf-local:0170"]["hold"]):
        raise ValueError("compatible nested Rihannsu #2 and TOS #35 series labels misclassified as subtitle or conflict")
    if (source["rows"][172]["title"] != ["Star Trek - TOS 038 - Idic Plan"] or
            byid["opf-local:0173"]["publisher_title"] != "The IDIC Epidemic" or
            "TITLE_IDIC_PLAN_VS_PUBLISHER_THE_IDIC_EPIDEMIC" not in byid["opf-local:0173"]["hold"]):
        raise ValueError("IDIC Plan vs Epidemic source title discrepancy erased")
    if (source["rows"][188]["creator"] != ["Peter David, Michael Jan Friedman, Robert Greenberger"] or
            byid["opf-local:0189"]["publisher_byline"] != ["Peter David"] or
            "OPF_THREE_CREATORS_VS_PUBLISHER_SINGLE_PETER_DAVID" not in byid["opf-local:0189"]["hold"]):
        raise ValueError("three creators vs one publisher byline discrepancy erased")
    if (byid["opf-local:0185"]["publisher_title"] !=
            "A Star Trek: The Original Series: A Flag Full of Sta" or
            "OFFICIAL_PRODUCT_HEADING_TRUNCATED" not in byid["opf-local:0185"]["hold"]):
        raise ValueError("truncated original publisher title silently normalized")
    if (not all("53" in source["rows"][n-1]["title"][0] for n in (183, 184)) or
            "OPF_ITEM_NUMBER_53_DUPLICATES" not in byid["opf-local:0184"]["hold"]):
        raise ValueError("duplicate OPF #53 product ordering discrepancy erased")
    if (byid["opf-local:0177"]["publisher_date"] != "2006-08-01" or
            byid["opf-local:0177"]["publisher_isbn13"] != "9780743419956" or
            "2006_EBOOK_NOT_2010_TRADE_PAPERBACK" not in byid["opf-local:0177"]["hold"]):
        raise ValueError("2006 eBook edition substituted with 2010 trade paperback")
    return (24, 0)


def validate() -> tuple[int, int]:
    src, packet = SOURCE.read_bytes(), PACKET.read_bytes()
    if hashlib.sha256(src).hexdigest() != SOURCE_SHA:
        raise ValueError("owner-private-derived accepted OPF observation packet changed")
    if hashlib.sha256(packet).hexdigest() != PACKET_SHA:
        raise ValueError("held publisher edition receipt changed without review")
    return validate_packet(json.loads(packet), json.loads(src))


if __name__ == "__main__":
    count, matches = validate()
    print(f"LIT_OPF_TOS_2_HELD_OK: {count} first-party pages read/cards; {matches} owner ISBN alignment claims; 0 Source/Work admissions")
