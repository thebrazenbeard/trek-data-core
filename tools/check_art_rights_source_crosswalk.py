"""Deterministic, fail-closed Librarian audit of accepted and HELD art origins.

This reports no new image release, Source/Work identity, or coverage.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "proposals/librarian/art-rights-source-crosswalk-20261104/records.json"
EXPECTED_LANES = {
    "ACCEPTED_ORIGINAL_CATEGORY_ASSET": 3,
    "ACCEPTED_LICENSED_DOCUMENTARY_HELD": 1,
    "ACCEPTED_EXTERNAL_JACKET_API_RIGHTS_UNRESOLVED": 2,
    "ACCEPTED_OPF_PUBLISHER_METADATA_NO_IMAGE": 3,
    "UNACCEPTED_LOCAL_MEDIA_SOURCE_PROPOSAL_HELD": 3,
}
ACCEPTED_BASE = "3028765359001b90bc3e6b5c1835ee283b326e91"
PACKET_FIELDS = frozenset({
    "packet_id", "accepted_main_baseline", "status", "accepted_input_digests",
    "state_count_lanes", "new_public_artwork", "new_image_downloads",
    "new_source_work_admissions", "new_coverage_increment", "site_effect", "entries",
})
ROW_FIELDS = {
    "ACCEPTED_ORIGINAL_CATEGORY_ASSET": frozenset({
        "id", "lane", "asset_origin", "medium", "asset_path", "asset_sha256",
        "source_local_row_id", "reference_scope", "rights_class", "byte_evidence",
        "display_state", "new_public_release_eligible",
    }),
    "ACCEPTED_LICENSED_DOCUMENTARY_HELD": frozenset({
        "id", "lane", "asset_origin", "medium", "source_local_row_id",
        "source_url", "creator", "license", "byte_evidence", "original_sha256",
        "display_state", "reference_scope", "new_public_release_eligible",
    }),
    "ACCEPTED_EXTERNAL_JACKET_API_RIGHTS_UNRESOLVED": frozenset({
        "id", "lane", "asset_origin", "medium", "source_local_row_id",
        "artwork_catalog_row_id", "source_url", "isbn13", "cover_id",
        "rights_class", "byte_evidence", "display_state", "new_public_release_eligible",
    }),
    "ACCEPTED_OPF_PUBLISHER_METADATA_NO_IMAGE": frozenset({
        "id", "lane", "asset_origin", "medium", "source_local_row_id",
        "private_source_local_ref", "publisher_title", "publisher_isbn13",
        "publisher_url", "source_crosscheck_state", "work_identity",
        "private_edition_equivalence", "byte_evidence", "display_state",
        "new_public_release_eligible",
    }),
    "UNACCEPTED_LOCAL_MEDIA_SOURCE_PROPOSAL_HELD": frozenset({
        "id", "lane", "asset_origin", "medium", "source_local_row_id",
        "work_association", "proposed_source_commit", "proposed_candidate_id",
        "source_url", "creator", "license", "original_sha256_local_proposal",
        "byte_evidence", "display_state", "new_public_release_eligible",
    }),
}
# TIFF HEAD-only case carries an extra, independently observed response-length field.
LOCAL_TIFF_ID = "picard-costume-local-unaccepted-tiff"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fail(message: str) -> None:
    raise ValueError(message)


def matches(row: dict, expected: dict, context: str) -> None:
    for key, value in expected.items():
        # Python considers False == 0 and True == 1. Neither equivalence is
        # permitted for custody, rights, release, or coverage declarations.
        if type(row.get(key)) is not type(value) or row.get(key) != value:
            fail(f"{context}: mismatched {key}: {row.get(key)!r} != {value!r}")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def audit(packet: dict | None = None, root: Path = ROOT) -> dict:
    packet = load(root / PACKET.relative_to(ROOT)) if packet is None else packet
    if not isinstance(packet, dict) or set(packet) != PACKET_FIELDS:
        fail("packet: unexpected fields or missing fields; rights declarations are closed")
    matches(packet, {"packet_id": "librarian-art-rights-source-crosswalk-20261104",
                     "accepted_main_baseline": ACCEPTED_BASE,
                     "status": "HELD_RIGHTS_PROVENANCE_CROSSWALK_NO_PUBLIC_EFFECT",
                     "state_count_lanes": EXPECTED_LANES,
                     "new_public_artwork": False, "new_image_downloads": False,
                     "new_source_work_admissions": 0, "new_coverage_increment": 0,
                     "site_effect": "NONE"}, "packet")
    if any(type(packet["state_count_lanes"].get(lane)) is not int
           for lane in EXPECTED_LANES):
        fail("state_count_lanes requires exact integer counts")
    inputs = packet.get("accepted_input_digests")
    if not isinstance(inputs, dict) or set(inputs) != {
            "explorer/artwork-catalog.json", "explorer/artwork-catalog-v1.3.json",
            "explorer/picard-jackets-v1.0.json", "explorer/publisher-isbn-crosschecks.json",
            "explorer/beyond-premiere-photo.json", "explorer/beyond-premiere-release-decision.json",
            "explorer/search-catalog.json"}:
        fail("input pin set changed; deliberate review required")
    for rel, sha in inputs.items():
        path = root / rel
        if path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != sha:
            fail(f"accepted input drift: {rel}")
    entries = packet.get("entries")
    if not isinstance(entries, list) or len(entries) != 12:
        fail("bounded twelve-row packet required")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"row:{index}: record must be an object")
        lane = entry.get("lane")
        fields = ROW_FIELDS.get(lane)
        if lane == "UNACCEPTED_LOCAL_MEDIA_SOURCE_PROPOSAL_HELD" and entry.get("id") == LOCAL_TIFF_ID:
            fields = fields | {"source_reported_bytes"}
        if fields is None or set(entry) != fields:
            fail(f"row:{index}: unexpected fields or missing fields in lane {lane}")
    if len({entry.get("id") for entry in entries}) != len(entries):
        fail("duplicate/missing entry id")
    if Counter(entry.get("lane") for entry in entries) != EXPECTED_LANES:
        fail("source/artwork rights lanes changed")
    if any(entry.get("new_public_release_eligible") is not False for entry in entries):
        fail("held crosswalk attempted artwork promotion")
    by_id = {entry["id"]: entry for entry in entries}

    spec = importlib.util.spec_from_file_location("accepted_original_art", root / "tools/build_explorer_abstract_art.py")
    if spec is None or spec.loader is None:
        fail("accepted renderer unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for medium in ("episode", "film", "literature"):
        row = by_id[f"original-category-{medium}"]
        rel = f"explorer/art-original-{medium}.svg"
        matches(row, {"lane": "ACCEPTED_ORIGINAL_CATEGORY_ASSET",
                      "asset_origin": "REPO_ORIGINAL_PROCEDURAL", "medium": medium.upper(),
                      "asset_path": rel, "source_local_row_id": None,
                      "rights_class": "REPO_SOURCE_AVAILABLE_ORIGINAL_ART",
                      "byte_evidence": "DETERMINISTIC_ACCEPTED_RENDERER_AND_MATCHING_COMMITTED_BYTES",
                      "display_state": "ALREADY_ACCEPTED_CATEGORY_PLACEHOLDER"}, f"original:{medium}")
        if row.get("reference_scope") != {
                "episode": "GENERIC_CATEGORY_ONLY_NOT_EPISODE_ART",
                "film": "GENERIC_CATEGORY_ONLY_NOT_OFFICIAL_POSTER",
                "literature": "GENERIC_CATEGORY_ONLY_NOT_BOOK_COVER"}[medium]:
            fail(f"original art incorrectly assigned official reference: {medium}")
        path = root / rel
        if path.is_symlink() or path.read_bytes() != module.expected_art()[path]:
            fail(f"renderer byte mismatch: {rel}")
        if digest(path.read_bytes()) != row.get("asset_sha256"):
            fail(f"original art digest mismatch: {rel}")

    search = load(root / "explorer/search-catalog.json")
    if search.get("row_count") != 1214 or search.get("identity_scope") != "SOURCE_LOCAL_NOT_DEDUPLICATED":
        fail("discovery source-local denominator changed")
    search_rows = {entry["row_id"]: entry for entry in search["rows"]}
    if len(search_rows) != len(search["rows"]):
        fail("duplicate accepted search row ID")
    if any(item.get("verification_status") != "UNVERIFIED_METADATA" for item in search["rows"]):
        fail("search candidate verification status unexpectedly promoted")

    photo = load(root / "explorer/beyond-premiere-photo.json")
    decision = load(root / "explorer/beyond-premiere-release-decision.json")
    beyond = by_id["beyond-premiere-accepted-held"]
    matches(beyond, {"lane": "ACCEPTED_LICENSED_DOCUMENTARY_HELD",
                     "asset_origin": "THIRD_PARTY_DOCUMENTARY_PHOTO", "medium": "FILM",
                     "source_local_row_id": "film:film-beyond",
                     "source_url": photo["source_url"], "creator": photo["photographer"],
                     "license": photo["license"], "original_sha256": photo["original_image_sha256_observed"],
                     "byte_evidence": "ACCEPTED_PHOTO_RECEIPT_ORIGINAL_AND_RENDITION_SHA256_REPORTED",
                     "reference_scope": "REAL_WORLD_PREMIERE_NOT_FILM_STILL",
                     "display_state": "ACCEPTED_HELD_PENDING_INDEPENDENT_RELEASE_REVIEW"}, "Beyond photo")
    if beyond["source_local_row_id"] not in search_rows:
        fail("Beyond film source-local row missing")
    if decision.get("public_image_display_authorized") is not False or decision.get("decision_status") != "HELD_PENDING_INDEPENDENT_RELEASE_REVIEW":
        fail("Beyond photo release hold drift")
    if decision.get("photo_manifest_sha256") != inputs["explorer/beyond-premiere-photo.json"]:
        fail("Beyond accepted release decision has stale photo receipt")

    base_covers = load(root / "explorer/artwork-catalog.json")["artwork"]
    picard_covers = load(root / "explorer/picard-jackets-v1.0.json")["artwork"]
    jacket_cases = (("kirk-autobiography-jacket-api", base_covers, "literature:prh-autobiography-kirk"),
                    ("picard-dark-veil-jacket-api", picard_covers, None))
    for id_, catalog, source_id in jacket_cases:
        row = by_id[id_]
        ref = next((art for art in catalog if art["row_id"] == row.get("artwork_catalog_row_id")), None)
        if ref is None:
            fail(f"jacket source record absent: {id_}")
        matches(row, {"lane": "ACCEPTED_EXTERNAL_JACKET_API_RIGHTS_UNRESOLVED",
                      "asset_origin": "OPEN_LIBRARY_COVERS_API_EXTERNAL", "medium": "LITERATURE",
                      "source_local_row_id": source_id, "source_url": ref["source_locator"],
                      "cover_id": ref["cover_id"], "isbn13": ref["isbn"],
                      "rights_class": "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED",
                      "byte_evidence": "EXTERNAL_COVER_NOT_REHOST_RIGHTS",
                      "display_state": "EXISTING_OPT_IN_EXTERNAL_API_PREVIEW"}, f"jacket:{id_}")
        if ref["rights_status"] != "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED":
            fail(f"accepted jacket rights status drift: {id_}")
        if "original_sha256" in row or "private_source_local_ref" in row:
            fail(f"jacket disguised as owned bytes/private OPF equivalence: {id_}")
        if source_id and source_id not in search_rows:
            fail(f"jacket source-local row absent: {source_id}")

    publisher = load(root / "explorer/publisher-isbn-crosschecks.json")
    if publisher.get("row_count") != 39 or publisher.get("held_discrepancy_count") != 9:
        fail("publisher crosscheck count changed")
    pub_rows = {row["row_id"]: row for row in publisher["rows"]}
    for id_ in ("opf-publisher-0010-isbn-agree-no-cover", "opf-publisher-0009-format-discrepancy-no-cover",
                "opf-publisher-0067-title-discrepancy-no-cover"):
        row = by_id[id_]
        ref = pub_rows.get(row.get("source_local_row_id"))
        if ref is None:
            fail(f"OPF crosscheck missing: {id_}")
        matches(row, {"lane": "ACCEPTED_OPF_PUBLISHER_METADATA_NO_IMAGE",
                      "asset_origin": "NO_IMAGE", "medium": "LITERATURE",
                      "private_source_local_ref": ref["source_local_ref"],
                      "publisher_title": ref["publisher_title"],
                      "publisher_isbn13": ref["publisher_isbn13"],
                      "publisher_url": ref["publisher_url"],
                      "source_crosscheck_state": ref["crosscheck_state"],
                      "work_identity": "NOT_RECONCILED", "private_edition_equivalence": "UNVERIFIED",
                      "byte_evidence": "NONE_METADATA_ONLY", "display_state": "NO_BOOK_COVER_BOUND"}, f"OPF:{id_}")
        if ref.get("work_identity") != "NOT_RECONCILED" or ref.get("private_edition_equivalence") != "UNVERIFIED":
            fail(f"OPF source metadata silently admitted: {id_}")
        if "artwork_catalog_row_id" in row or "cover_id" in row:
            fail(f"OPF crosscheck falsely bound to cover: {id_}")

    # Unaccepted observations have no accepted upstream receipt. Pin their
    # *entire* source-relative attribution tuple pending separate verification;
    # source-commit labels and private original hashes are not authenticity proof.
    local_cases = {
        "discovery-lucca-local-unaccepted-photo": {
            "medium": "EPISODE", "source_local_row_id": None,
            "work_association": "Star Trek: Discovery series 2017 event, no episode ID",
            "proposed_source_commit": "36b8661",
            "proposed_candidate_id": "media-discovery-2017-lucca-caranti-panel-held",
            "source_url": "https://commons.wikimedia.org/wiki/File:Teatro_del_Giglio_-_Lucca_2017.jpg",
            "creator": "Niccolò Caranti", "license": "CC BY-SA 4.0",
            "original_sha256_local_proposal": "2a414b122e7f6a1a9d5ffec93c79dba4b72209e8bf1a17839565b2c3c1b41347",
            "byte_evidence": "UNACCEPTED_LOCAL_PRIVATE_ORIGINAL_SHA256",
            "display_state": "HELD_THIRD_PARTY_PERSONALITY_RIGHTS",
        },
        "nemesis-local-unaccepted-photo": {
            "medium": "FILM", "source_local_row_id": "film:film-nemesis",
            "work_association": "Star Trek: Nemesis behind-the-scenes set, not frame",
            "proposed_source_commit": "736024a",
            "proposed_candidate_id": "media-nemesis-2001-grcote-set-photo-held",
            "source_url": "https://commons.wikimedia.org/wiki/File:Glenn_Cote_Brent_Spiner.jpg",
            "creator": "Grcote", "license": "GFDL 1.2 or later",
            "original_sha256_local_proposal": "47984c7682846bfba2b6515f6137877b6b3c194f2d7420909bbf4113b8cfc54f",
            "byte_evidence": "UNACCEPTED_LOCAL_PRIVATE_ORIGINAL_SHA256",
            "display_state": "HELD_GFDL_UNSUPPORTED_AND_PERSONALITY_RIGHTS",
        },
        LOCAL_TIFF_ID: {
            "medium": "EPISODE", "source_local_row_id": None,
            "work_association": "Star Trek: Picard season three displayed costume, no episode ID",
            "proposed_source_commit": "f5541e5",
            "proposed_candidate_id": "media-picard-2023-fourthords-costume-held",
            "source_url": "https://commons.wikimedia.org/wiki/File:Star_Trek-_Picard_season-three_Starfleet_flag_officer's_casual_uniform_(1_March_2023,_aboard_Star_Trek-_The_Cruise_VI,_1_of_3).tif",
            "creator": "Fourthords", "license": "CC BY-SA 4.0",
            "original_sha256_local_proposal": None,
            "byte_evidence": "UNACCEPTED_LOCAL_COMMONS_API_AND_HTTP_HEAD_ONLY",
            "display_state": "HELD_UNDERLYING_COSTUME_AND_MARK_RIGHTS",
            "source_reported_bytes": 122012134,
        },
    }
    for id_, source_fields in local_cases.items():
        row = by_id[id_]
        matches(row, {"lane": "UNACCEPTED_LOCAL_MEDIA_SOURCE_PROPOSAL_HELD",
                      "asset_origin": "THIRD_PARTY_DOCUMENTARY_PHOTO", **source_fields},
                f"local-unaccepted:{id_}")
        source_id = source_fields["source_local_row_id"]
        if source_id and source_id not in search_rows:
            fail(f"local media source-local row missing: {id_}")
    return {"rows_validated": len(entries), "accepted_source_files_pinned": len(inputs),
            "rights_promotion": "NONE", "public_bytes_added": False}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
