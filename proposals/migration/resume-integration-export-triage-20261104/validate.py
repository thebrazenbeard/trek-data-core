#!/usr/bin/env python3
"""Offline migration intake gate: chat claims remain unadmitted.

Tests independently pin two *accepted-public-metadata* hazard classes at
main@3028765. They do not authenticate the historical chat or private books.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).resolve().parent
ACCEPTED_MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"
ARCHIVE_SHA = "06b99eb21e1970dbd4b24ffe682e73ee387c59cc1623812269fad4383f31cea1"
HTML_SHA = "4335ecc6a4c9d64c9d38c5b3e391e9d3c8e50e01160fdf26ebf540b76e888e21"
SHELF_BYTES_SHA = "1170e8cb56b4ff3c5beab8d412fa5613b6e3b9d0ab7b5a18f80fe403c5bde3e8"
SHELF_MEMBERSHIP_SHA = "62309367d5a4a68660e68c8a243ec2874c2c28c97395ba99ca1635985211fdef"
CLAIMS_SHA = "833b4355456d35fed09480f8604ba3d3190a872b1b1619254ad63ed49d0ecaad"
ISBN_FIELDS = ("source_local_ref", "publisher_isbn13", "crosscheck_state")
SECOND_SELF = "proposed-lit-picard-second-self"
PAPERBACK_ISBN = "9781982194833"
SOURCE_FAMILY = "publisher:simonandschuster.com"
PRODUCT_URL = ("https://www.simonandschuster.com/books/Star-Trek-Picard-Second-Self/"
               "Una-McCormack/Star-Trek-Picard/9781982194833")
LIT_MAIN = Path("proposals/librarian/simon-schuster-three-novels-20261103/records.json")
LIT_PICARD = Path("proposals/librarian/picard-companion-editions-20261103/records.json")
SHELF = Path("explorer/publisher-isbn-crosschecks.json")
DIRECTORY = Path("explorer/discovery-catalog.json")
EXPECTED_LEADS = {
    "RESUME-OPF-COUNTS": (61, 176),
    "RESUME-PUBLISHER-COUNTS": (426, 426),
    "RESUME-ISBN-MEMBERSHIP": (452, 456),
    "RESUME-SECOND-SELF-OVERLAP": (137, 192),
}


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise ValueError(explanation)


def unique_object(items: list[tuple]) -> dict:
    result = {}
    for key, value in items:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink() and path.stat().st_size < 8_000_000,
            f"missing/symlinked/oversized artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def verify_manifest(data: dict) -> dict:
    require(data.get("role") == "MIGRATION" and
            data.get("record_class") == "HISTORICAL_CHAT_CLAIM_TRIAGE" and
            data.get("admission") == "NOT_ADMITTED", "historical claim admission/class drift")
    require(data.get("accepted_main_at_intake") == ACCEPTED_MAIN, "accepted baseline drift")
    for effect in ("accepted_research_effect", "source_work_binding_effect", "coverage_effect",
                   "denominator_effect", "reconciliation_effect", "publication_effect"):
        require(data.get(effect) == "NONE", f"forbidden historical effect: {effect}")
    source = data.get("source", {})
    require(source.get("kind") == "USER_SUPPLIED_SAVED_CHATGPT_WEB_PAGE_ARCHIVE" and
            source.get("archive_sha256") == ARCHIVE_SHA and
            source.get("html_member_sha256") == HTML_SHA and
            source.get("filename") == "Resume Integration Updates.zip" and
            source.get("html_member_name") == "Resume Integration Updates.html",
            "chat export source attribution drift")
    leads = data.get("claims")
    require(isinstance(leads, list) and len(leads) == len(EXPECTED_LEADS),
            "historical lead set drift")
    seen = set()
    for lead in leads:
        require(isinstance(lead, dict), "non-object historical claim")
        ident = lead.get("id")
        require(ident in EXPECTED_LEADS and ident not in seen, "duplicate/unreviewed lead")
        seen.add(ident)
        require(lead.get("claimant") == "HISTORICAL_ASSISTANT_IN_CHAT" and
                lead.get("evidence_class") == "HISTORICAL_ASSISTANT_ASSERTION_NOT_REPLAYED" and
                lead.get("rendered_text_lines") == list(EXPECTED_LEADS[ident]) and
                isinstance(lead.get("historical_claim"), str) and
                isinstance(lead.get("next_gate"), str) and
                len(lead["historical_claim"]) > 30 and len(lead["next_gate"]) > 30,
                f"historical assertion improperly promoted/unlocated: {ident}")
    claims_bytes = json.dumps(leads, sort_keys=True, separators=(",", ":"),
                              ensure_ascii=False).encode("utf-8")
    require(digest(claims_bytes) == CLAIMS_SHA, "historical claim wording/pins changed")
    receipt = data.get("regression_receipts", {})
    require(receipt.get("publisher_isbn_projection_path") == SHELF.as_posix() and
            receipt.get("publisher_isbn_projection_sha256_at_intake") == SHELF_BYTES_SHA and
            receipt.get("publisher_isbn_exact_membership_sha256_at_intake") == SHELF_MEMBERSHIP_SHA and
            receipt.get("publisher_isbn_identity_fields") == list(ISBN_FIELDS) and
            receipt.get("literary_catalog_path") == DIRECTORY.as_posix() and
            receipt.get("literary_source_proposals") == [LIT_PICARD.as_posix(), LIT_MAIN.as_posix()] and
            receipt.get("literary_overlap_candidate_work_id") == SECOND_SELF and
            receipt.get("literary_overlap_paperback_isbn13") == PAPERBACK_ISBN and
            receipt.get("literary_overlap_expected_navigation_rows") == 1 and
            receipt.get("reconciliation_status") == "UNRESOLVED_GLOBAL_IDENTITY",
            "regression receipt/admission scope drift")
    return receipt


def verify_isbn_membership(root: Path) -> None:
    shelf_path = root / SHELF
    shelf = load_json(shelf_path)
    rows = shelf.get("rows")
    require(isinstance(rows, list) and len(rows) == shelf.get("row_count") == 39,
            "ISBN shelf row count drift")
    member_tuples = []
    for row in rows:
        require(isinstance(row, dict), "invalid ISBN row")
        triple = tuple(row.get(key) for key in ISBN_FIELDS)
        require(all(isinstance(x, str) for x in triple), "ISBN member lacks identity/state")
        require(re.fullmatch(r"opf-local:\d{4}", triple[0]) is not None and
                re.fullmatch(r"97[89]\d{10}", triple[1]) is not None,
                "invalid ISBN/member identifier")
        member_tuples.append(triple)
        require(row.get("private_edition_equivalence") == "UNVERIFIED" and
                row.get("work_identity") == "NOT_RECONCILED" and
                row.get("admission_effect") == "NONE" and
                row.get("coverage_effect") == "NONE", "ISBN row improperly admitted")
    require(len(set(member_tuples)) == 39 and
            len({t[0] for t in member_tuples}) == 39 and
            len({t[1] for t in member_tuples}) == 39,
            "duplicate ISBN shelf member")
    require(sum(t[2] == "ISBN_IDENTIFIER_AGREEMENT_SOURCE_LOCAL" for t in member_tuples) == 30 and
            shelf.get("publisher_isbn_identifier_agreements") == 30 and
            shelf.get("held_discrepancy_count") == 9,
            "ISBN aggregate drift")
    members_bytes = json.dumps(sorted(member_tuples), separators=(",", ":"),
                               ensure_ascii=False).encode("utf-8")
    require(digest(members_bytes) == SHELF_MEMBERSHIP_SHA,
            "ISBN membership drift despite possible unchanged 39/30/9 aggregates")
    require(digest(shelf_path.read_bytes()) == SHELF_BYTES_SHA,
            "accepted ISBN shelf bytes no longer match reviewed snapshot")


def verify_second_self(root: Path) -> None:
    picard = load_json(root / LIT_PICARD)
    novels = load_json(root / LIT_MAIN)
    require(picard.get("proposal_only") is True and novels.get("proposal_only") is True and
            picard.get("accepted_source_binding_effect") == "NONE" and
            picard.get("accepted_work_effect") == "NONE" and
            picard.get("coverage_effect") == "NONE" and
            set(novels.get("accepted_effects", {}).values()) == {"NONE"},
            "literary metadata proposal promoted")
    require(picard.get("source_group") == SOURCE_FAMILY and
            novels.get("independence_group") == SOURCE_FAMILY,
            "overlapping literary references falsely independent")
    picard_editions = [x for x in picard.get("edition_candidates", [])
                       if x.get("isbn13") == PAPERBACK_ISBN]
    novel_editions = [x for x in novels.get("editions", [])
                      if x.get("isbn13") == PAPERBACK_ISBN]
    require(len(picard_editions) == len(novel_editions) == 1,
            "missing/duplicated Second Self paperback edition proposal")
    a, b = picard_editions[0], novel_editions[0]
    require(a.get("work_id") == b.get("candidate_work_id") == SECOND_SELF and
            a.get("format") == b.get("format") == "TRADE_PAPERBACK" and
            a.get("status") == "PROPOSED" and b.get("status") == "PROPOSED_METADATA_ONLY" and
            b.get("publisher_product_url") == PRODUCT_URL,
            "conflicting proposal ISBN/Work/format/publisher URL; reconciliation required")
    bindings = [x for x in picard.get("bindings", []) if x.get("work_id") == SECOND_SELF]
    require(len(bindings) == 1 and bindings[0].get("lifecycle") == "PROPOSED" and
            bindings[0].get("source_scope", {}).get("scope_type") == "WHOLE" and
            bindings[0].get("basis") == [{"kind": "PUBLISHER_PRODUCT_URL", "value": PRODUCT_URL}],
            "historical proposal binding improperly settled")
    directory = load_json(root / DIRECTORY)
    rows = directory.get("rows")
    require(isinstance(rows, list) and directory.get("row_count") == len(rows) and
            directory.get("admission_effect") == "NONE" and
            directory.get("coverage_effect") == "NONE", "discovery projection scope drift")
    expected_row = f"literature:{SECOND_SELF}"
    refs = [x for x in rows if x.get("row_id") == expected_row or
            x.get("source_locator") == PRODUCT_URL or
            (x.get("medium") == "LITERATURE" and
             (x.get("title") == "Star Trek: Picard: Second Self" or
              (isinstance(x.get("details"), list) and
               any(PAPERBACK_ISBN in detail for detail in x["details"]
                   if isinstance(detail, str)))))]
    require(len(refs) == 1 and refs[0].get("row_id") == expected_row and
            refs[0].get("source_locator") == PRODUCT_URL and
            refs[0].get("source_group") == SOURCE_FAMILY and
            refs[0].get("identity_scope") == "SOURCE_LOCAL" and
            refs[0].get("verification_status") == "UNVERIFIED_METADATA" and
            refs[0].get("admission_effect") == "NONE" and
            refs[0].get("coverage_effect") == "NONE",
            "duplicated/inflated literary navigation reference or promoted Work")


def verify(root: Path = ROOT, manifest_path: Path | None = None) -> None:
    manifest = load_json(manifest_path or (root / "proposals/migration/resume-integration-export-triage-20261104/MANIFEST.json"))
    verify_manifest(manifest)
    verify_isbn_membership(root)
    verify_second_self(root)


if __name__ == "__main__":
    verify()
    print("RESUME_INTEGRATION_TRIAGE_VALID: 4 unadmitted historical leads; "
          "exact 39/30/9 ISBN membership pinned; one non-admitted Second Self source-local row")
