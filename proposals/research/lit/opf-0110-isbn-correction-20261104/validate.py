"""Deterministic held correction check, without access to owner-private XML."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from candidate_parser import normalized_checksum_isbn


ROOT = Path(__file__).resolve().parents[4]
PRIVATE_DERIVATIVE = ROOT / "proposals/librarian/private-opf-metadata-20261103/observations.json"
PUBLISHER_PACKET = ROOT / "proposals/research/opf-seven-official-editions-20261103/observations.json"
PACKET = Path(__file__).with_name("held_correction.json")


def validate() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    for path, sha in ((PRIVATE_DERIVATIVE, packet["accepted_opf_observations_sha256"]),
                      (PUBLISHER_PACKET, packet["accepted_publisher_proposal_sha256"])):
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
            raise ValueError("accepted parent source receipt changed")
    derivative = json.loads(PRIVATE_DERIVATIVE.read_text(encoding="utf-8"))
    original = derivative["rows"][109]
    published = json.loads(PUBLISHER_PACKET.read_text(encoding="utf-8"))["rows"][0]
    if not (original["source_local_id"] == published["opf_source_local_id"] == packet["opf_source_local_id"]):
        raise ValueError("local identity chain changed")
    if original["opf_entry_sha256"] != packet["original_opf_xml_sha256_from_prior_independent_audit"]:
        raise ValueError("source-XML fingerprint changed")
    if original["isbn_checksum_valid"] != packet["accepted_derivative_isbn_checksum_valid"] != []:
        raise ValueError("prior recorded omission changed")
    if (original["publisher"], original["date"], original["title"], original["creator"]) != (
        ["Pocket Books"], ["2004"], ["A Time for War, A Time for Peace"], ["Keith R.A. DeCandido"]):
        raise ValueError("source-local metadata changed")
    if (packet["original_xml_identifier_tag_from_prior_independent_audit"],
        packet["original_xml_identifier_literal_from_prior_independent_audit"]) != (
        "dc:Identifier", "ISBN 0-7434-9997-2"):
        raise ValueError("independently reported source literal changed")
    if published["original_opf_xml_isbn10_literal"] != packet["original_xml_identifier_literal_from_prior_independent_audit"]:
        raise ValueError("independently reported literal differs from held publisher packet")
    candidate = normalized_checksum_isbn(packet["original_xml_identifier_literal_from_prior_independent_audit"])
    if candidate != packet["proposed_checksum_valid_isbn10"]:
        raise ValueError("identifier correction checksum mismatch")
    derived = "978" + candidate[:9]
    check = (10 - sum(int(digit) * (1 if i % 2 == 0 else 3) for i, digit in enumerate(derived)) % 10) % 10
    if derived + str(check) != packet["proposed_mathematically_derived_isbn13"]:
        raise ValueError("ISBN10 to ISBN13 transformation mismatch")
    for target, parent in (("publisher_2004_ebook", published["source_isbn10_corresponding_publisher_ebook"]),
                           ("publisher_2019_trade_paperback", published)):
        row = packet[target]
        for property_name, parent_name in (("isbn13", "isbn13" if target == "publisher_2004_ebook" else "publisher_isbn13"),
                                           ("format", "format" if target == "publisher_2004_ebook" else "publisher_format"),
                                           ("imprint", "imprint" if target == "publisher_2004_ebook" else "publisher_imprint"),
                                           ("date", "date" if target == "publisher_2004_ebook" else "publisher_date"),
                                           ("pages", "pages" if target == "publisher_2004_ebook" else "publisher_pages"),
                                           ("official_url", "url" if target == "publisher_2004_ebook" else "publisher_url")):
            if row[property_name] != parent[parent_name]:
                raise ValueError("official publisher product editions diverged")
    if packet["publisher_2004_ebook"]["isbn13"] == packet["publisher_2019_trade_paperback"]["isbn13"]:
        raise ValueError("distinct publisher product ISBNs collapsed")
    for field, expected in (("original_owner_xml_reread_this_wave", False),
                            ("legacy_owner_host_extractor_code_inspected", False),
                            ("upstream_extraction_root_cause", "UNKNOWN"),
                            ("source_text_equivalence", "NOT_VERIFIED"),
                            ("edition_admission", "NONE"),
                            ("global_work_identity", "NOT_RECONCILED"),
                            ("public_explorer_release", "HELD"),
                            ("coverage_effect", "NONE")):
        if packet.get(field) != expected:
            raise ValueError(f"held correction may not promote {field}")


if __name__ == "__main__":
    validate()
    print("PASS: OPF0110 ISBN10 metadata correction held; distinct publisher editions; zero admission")
