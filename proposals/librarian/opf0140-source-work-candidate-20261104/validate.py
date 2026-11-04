#!/usr/bin/env python3
"""Check the HELD first nonfixture literary candidacy, never the private ebook.

This is a public consistency check against accepted OPF metadata, a first-party
publisher locator and reported owner-side byte receipts. It deliberately cannot
replay the private source or determine the novel's content/rights/edition.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))

from validate_librarian_registry import validate_registry  # noqa: E402


ORIGINAL_ZIP = "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac"
CONVERTED_ZIP = "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f"
PRIVATE_ANCHOR = "f755a66592372056bb180798e3fd507dfdb39d58d7e07f01d9cb2cbdcf0f5e60"
PRIVATE_CROSSWALK = "357bb3a5a1db47e9849600112dd8de01e7c9928f66c5365b964ae2b50a0b479e"
ORIGINAL_MEMBER = "910b2da59954827c2bd6311088e2de3d3934437cc20331e684ee7952ca870462"
OPF_MEMBER = "b815b98f15098b44c4e75aef3bc006feabd9f3e671bb4586566c48140ee8b248"
PUBLISHER_URL = "https://www.simonandschuster.com/books/Star-Trek/Gene-Roddenberry/Star-Trek/9780743412087"
SHA = re.compile(r"[0-9a-f]{64}\Z")


def _no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value):
    raise ValueError("nonstandard JSON numeric constant")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=_no_duplicate_keys,
                      parse_constant=_reject_constant)


def isbn10_to_13(isbn10: str) -> str:
    if not re.fullmatch(r"[0-9]{10}", isbn10):
        raise ValueError("ISBN10 must be 10 digits")
    if sum((10 - i) * int(ch) for i, ch in enumerate(isbn10)) % 11:
        raise ValueError("ISBN10 check digit incorrect")
    body = "978" + isbn10[:9]
    check = (-sum((1 if i % 2 == 0 else 3) * int(ch)
                  for i, ch in enumerate(body))) % 10
    return body + str(check)


def check(packet, upstream_observations):
    if type(packet) is not dict or type(upstream_observations) is not dict:
        raise ValueError("packet and observations must be objects")
    if packet.get("record_type") != "librarian_nonfixture_source_work_candidate":
        raise ValueError("wrong record type")
    if packet.get("schema_version") != "1.0.0":
        raise ValueError("unsupported version")
    if packet.get("source_local_reference") != "opf-local:0140":
        raise ValueError("wrong source-local candidate")
    if packet.get("accepted_main_at_start") != "3028765359001b90bc3e6b5c1835ee283b326e91":
        raise ValueError("wrong accepted-main context")
    rows = [r for r in upstream_observations.get("rows", [])
            if r.get("source_local_id") == "opf-local:0140"]
    if len(rows) != 1 or rows[0].get("opf_entry_sha256") != OPF_MEMBER:
        raise ValueError("upstream OPF proposal source row changed")
    opf = rows[0]
    if (opf.get("title") != ["THE MOTION PICTURE™"] or
            opf.get("creator") != ["Gene Roddenberry"] or
            opf.get("isbn_checksum_valid") != ["0743412087"]):
        raise ValueError("upstream OPF proposal identity fields changed")
    if packet.get("evidence_classes", {}).get("opf_metadata") != "MAIN_TRACKED_SOURCE_LOCAL_PROPOSAL_METADATA":
        raise ValueError("OPF proposal mistakenly promoted to accepted metadata")
    if packet.get("opf_source_isbn10") != "0743412087":
        raise ValueError("unverified OPF ISBN drift")

    c = packet["custody_observation"]
    expected = {
        "original_archive_sha256": ORIGINAL_ZIP,
        "original_extracted_member_sha256": ORIGINAL_MEMBER,
        "original_extracted_member_bytes": 314662,
        "original_extracted_member_rehashed_and_matched_archive": True,
        "converted_archive_sha256": CONVERTED_ZIP,
        "converted_opf_member_sha256": OPF_MEMBER,
        "private_archive_member_rehash_anchor_sha256": PRIVATE_ANCHOR,
        "private_converter_crosswalk_receipt_sha256": PRIVATE_CROSSWALK,
        "converted_link_disposition": "CANDIDATE_EXPLICIT_CONVERTER_LINK",
        "converted_link_count_for_this_opf": 1,
        "content_completeness": "UNVERIFIED",
        "narrative_content_read": False,
        "source_edition_identity_verified": False,
        "rights_verification": "NOT_PERFORMED",
        "independent_private_source_witness": False,
    }
    if set(c) != set(expected) or any(type(c[k]) is not type(v) or c[k] != v
                                         for k, v in expected.items()):
        raise ValueError("unverified owner custody observation drift")

    p = packet["publisher_observation"]
    pub_expected = {
        "url": PUBLISHER_URL, "source_family": "publisher:simonandschuster.com",
        "title": "Star Trek", "subtitle": "The Motion Picture", "author": "Gene Roddenberry",
        "format": "eBook", "isbn13": "9780743412087",
        "imprint": "Pocket Books/Star Trek", "publication_date": "2000-05-23",
        "page_count": 252, "publisher_html_bytes_custodied": False,
        "work_content_verified_from_publisher_blurb": False,
    }
    if set(p) != set(pub_expected) or any(type(p[k]) is not type(v) or p[k] != v
                                           for k, v in pub_expected.items()):
        raise ValueError("official publisher page observation drift")
    if isbn10_to_13(packet["opf_source_isbn10"]) != p["isbn13"]:
        raise ValueError("publisher and OPF ISBN check digits differ")
    if packet.get("isbn_relation") != "ISBN10_CHECKDIGIT_CONVERTS_TO_PUBLISHER_ISBN13_NOT_EDITION_IDENTITY":
        raise ValueError("ISBN relationship over-promoted")

    pr = packet["proposal"]
    if set(pr) != {"source", "work", "source_work_binding"}:
        raise ValueError("unexpected proposed registry record")
    s, w, b = pr["source"], pr["work"], pr["source_work_binding"]
    errors = validate_registry([s], [w], [b], [])
    if errors:
        raise ValueError("Librarian contract: " + "; ".join(errors))
    if (s["status"] != "PROPOSED" or w["status"] != "PROPOSED" or
            b["lifecycle"] != "PROPOSED" or b["mapping_role"] != "METADATA_ONLY" or
            s["fixture_only"] is not False or w["fixture_only"] is not False or
            b["fixture_only"] is not False):
        raise ValueError("nonfixture metadata candidate was promoted")
    if (s["content_hash"] != "sha256:" + ORIGINAL_MEMBER or
            s["provenance_family"] != s["independence_group"] or
            s["provider_metadata"].get("standalone_source_custody_receipt") != "NOT_CAPTURED" or
            s["provider_metadata"].get("publisher_edition_equality") != "NOT_VERIFIED" or
            s["provider_metadata"].get("rights_basis") != "UNKNOWN" or
            b["basis"] != [
                {"kind": "BYTE_HASH", "value": "sha256:" + ORIGINAL_MEMBER},
                {"kind": "CONTAINER_MANIFEST", "value": "sha256:" + PRIVATE_CROSSWALK},
            ]):
        raise ValueError("source/binding hash, rights or lineage contract drift")
    if (packet.get("source_work_identity_state") != "UNVERIFIED" or
            any(packet.get(k) != "NONE" for k in (
                "accepted_registry_effect", "coverage_effect", "public_release_effect")) or
            packet.get("private_member_names_or_paths_exported") is not False or
            packet.get("copyrighted_prose_or_cover_bytes_exported") is not False):
        raise ValueError("forbidden admission, privacy or publication promotion")
    if not isinstance(packet.get("admission_blockers"), list) or len(packet["admission_blockers"]) < 4:
        raise ValueError("missing candidacy admission blockers")
    # No private filename, path, member ID or prose should enter this packet.
    body = json.dumps(packet, ensure_ascii=False)
    if any(x in body for x in ("member_name_private", "member_id", "C:\\\\", "/home/", "/Users/", ".lit\"")):
        raise ValueError("private identifier or path disclosure")
    return True


def main():
    try:
        packet = load(HERE / "candidate.json")
        accepted = load(ROOT / "proposals" / "librarian" / "private-opf-metadata-20261103" / "observations.json")
        check(packet, accepted)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print("LIBRARIAN_NONFIXTURE_CANDIDATE_REJECTED:", exc, file=sys.stderr)
        return 1
    print("LIBRARIAN_NONFIXTURE_CANDIDATE_VALIDATED: PROPOSED_METADATA_ONLY; admission NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
