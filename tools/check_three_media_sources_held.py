"""Deterministic fail-closed checks for a metadata-only librarian artwork proposal.

This script never performs network requests or reads image pixels. It validates only
the proposed file-level provenance and the absence of public-release effects.
"""

import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "proposals/librarian/three-independent-media-sources-20261104/records.json"
BASELINE = "3028765359001b90bc3e6b5c1835ee283b326e91"
EXPECTED = {
    "media-nemesis-2001-grcote-set-photo-held": (931234115, "GFDL_1_2_OR_LATER_NO_INVARIANT_OR_COVER_TEXTS", "Grcote"),
    "media-discovery-2017-lucca-caranti-panel-held": (1155058425, "CC_BY_SA_4_0_INTERNATIONAL", "Niccolò Caranti"),
    "media-picard-2023-fourthords-costume-held": (1145272591, "CC_BY_SA_4_0_INTERNATIONAL", "Fourthords"),
}


def validate(packet):
    errors = []
    if packet.get("baseline_accepted_main") != BASELINE:
        errors.append("wrong accepted baseline")
    if packet.get("proposal_state") != "HELD_METADATA_ONLY":
        errors.append("packet must remain held")
    for key, expected in (("image_binary_committed", False), ("image_downloaded", False),
                          ("public_release_eligible", False), ("accepted_coverage_increment", 0),
                          ("accepted_source_work_admissions", 0), ("site_effect", "NONE")):
        if packet.get(key) != expected or type(packet.get(key)) is not type(expected):
            errors.append(f"unsafe packet effect: {key}")
    rows = packet.get("candidates", [])
    if len(rows) != len(EXPECTED):
        errors.append("expected three distinct files")
    if len({r.get("candidate_id") for r in rows}) != len(rows):
        errors.append("duplicate candidate id")
    if len({r.get("source_family_id") for r in rows}) != len(rows):
        errors.append("non-independent source families")
    if len({r.get("creator") for r in rows}) != len(rows):
        errors.append("non-independent photographers")
    if len({r.get("commons_file") for r in rows}) != len(rows):
        errors.append("duplicate file")
    for row in rows:
        ident = row.get("candidate_id")
        if ident not in EXPECTED:
            errors.append(f"unknown id {ident}")
            continue
        oldid, license_id, creator = EXPECTED[ident]
        if (row.get("fixed_description_revision_oldid"), row.get("license_id"), row.get("creator")) != (oldid, license_id, creator):
            errors.append(f"identity/license revision drift: {ident}")
        parsed = urlparse(row.get("fixed_description_url", ""))
        query = parse_qs(parsed.query)
        if parsed.hostname != "commons.wikimedia.org" or parsed.path != "/w/index.php" or query.get("oldid") != [str(oldid)] or query.get("title") != [row.get("commons_file")]:
            errors.append(f"unfixed or mismatched Commons page: {ident}")
        if not row.get("source_family_id") or not row.get("association_evidence") or not row.get("rights_holds"):
            errors.append(f"insufficient evidence/holds: {ident}")
        if not row.get("asset_kind", "").startswith("DOCUMENTARY_") or "NOT_EPISODE" not in row.get("asset_kind", "") and "NOT_FILM_FRAME" not in row.get("asset_kind", ""):
            errors.append(f"misrepresented studio still/frame: {ident}")
        if row.get("public_release_eligible") is not False or row.get("independent_binary_sha256") is not None:
            errors.append(f"unsafely published or fabricated SHA256: {ident}")
        if row.get("checksum_evidence") == "COMMONS_STRUCTURED_DATA_REPORTED_NOT_LOCALLY_RECOMPUTED":
            digest = row.get("reported_original_sha1")
            if not isinstance(digest, str) or len(digest) != 40 or any(c not in "0123456789abcdef" for c in digest):
                errors.append(f"invalid reported sha1: {ident}")
        elif row.get("checksum_evidence") == "NO_CHECKSUM_IN_INSPECTED_FIXED_FILE_PAGE":
            if row.get("reported_original_sha1") is not None or row.get("reported_original_bytes") is not None:
                errors.append(f"unsupported original digest/bytes: {ident}")
        else:
            errors.append(f"unqualified digest provenance: {ident}")
        if not row.get("license_url", "").startswith("https://"):
            errors.append(f"missing license URL: {ident}")
        if ident.startswith("media-nemesis"):
            if row.get("license_allowlist_state") != "OUTSIDE_ACCEPTED_ARTWORK_LICENSE_BASES" or "GFDL" not in row.get("license_id", ""):
                errors.append("GFDL must remain unsupported and held")
            if "private ticket NOT read" not in row.get("license_evidence", ""):
                errors.append("VRT ticket falsely elevated")
        else:
            if row.get("license_allowlist_state") != "NOMINALLY_RECOGNIZED_BUT_NOT_RELEASE_APPROVAL":
                errors.append(f"license allowed incorrectly as release: {ident}")
            if row.get("license_url") != "https://creativecommons.org/licenses/by-sa/4.0/":
                errors.append(f"license-version mismatch: {ident}")
        if ident.startswith("media-picard") and (row.get("reported_original_size_label") != "116.36 MB" or row.get("reported_original_sha1") is not None):
            errors.append("large TIFF checksum/size claim altered")
    return errors


if __name__ == "__main__":
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    failures = validate(packet)
    if failures:
        raise SystemExit("FAIL: " + "; ".join(failures))
    print("PASS: 3 independent photographer-source files, fixed source revisions, all HELD; no image bytes or publication")
