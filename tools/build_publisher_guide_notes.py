#!/usr/bin/env python3
"""Compile *held source-local* publisher-note drafts into a separate Explorer sidecar.

No canonical Work, Briefing, episode close-read, coverage, or publisher approval
is inferred. Only exact bytes already committed on accepted main are inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
OUTPUT = Path("explorer/publisher-guide-notes.json")
SCHEMA = "trek-held-publisher-guide-notes-v1"


@dataclass(frozen=True)
class Packet:
    path: str
    sha256: str
    kind: str
    count: int


PACKETS = (
    Packet("proposals/verification/ent-season1-publisher-b001-20261103/observations.json", "761f45a956f8fc409f2c3a80273c9e0d6ba479310ac536729760cef10716de4b", "ENT", 10),
    Packet("proposals/verification/ent-season1-publisher-b002-20261103/observations.json", "ce21bf57f9863915e612f46d9e81cc15139433b909a48b6e659c03add5a324b4", "ENT", 10),
    Packet("proposals/verification/ent-season1-publisher-b003-20261103/observations.json", "a965e3b94cb3c59248b7cf5d3c3814a0db2a3140b7dc749a0a70d8666047090f", "ENT", 5),
    Packet("proposals/research/voy-s4-e10-e14-publisher-cards-20261103/records.json", "dde9b0b1fb24da95efe882e36042ed0d99045dd83583da5c29a18788852672b0", "VOY_S4", 5),
    Packet("proposals/research/pic/picard-s1-first5-guide-cards-20261103/records.json", "070dccdbda3b7a777e6f12201d725bd906610f4e1c5ee26e8c37c3a218c6829f", "PIC", 5),
    Packet("proposals/research/pic/picard-s1-last5-guide-cards-20261103/records.json", "fe962cc235ffc84f5cff7a970a940419cf9a21dce72cd5844cae76ce89f9a9cc", "PIC", 5),
    Packet("proposals/research/discovery/s1-publisher-first5-20261103/records.json", "9e4492351ebd2625968c8107f766a4317887e6726f674132b4b10a8af5e8c71b", "DIS", 5),
    Packet("proposals/research/voyager/b006-publisher-synopsis-drafts-20261103/records.json", "ffffcba59ecd1a1c9a6449fd1acc52e3909ce4b45eb19606de3d977d528a6638", "VOY_B006", 13),
)
VOY_B006_SOURCE = Packet("proposals/verification/episode-guide-rechecks-b006-voy-20261103/records.json", "c20af10beacfcf3a3d533352276e766dda98ddca983b8a87291dd2ac30e61df7", "VOY_METADATA", 13)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_packet(packet, root=REPO):
    relative = Path(packet.path)
    require(not relative.is_absolute() and ".." not in relative.parts and relative.parts,
            f"unsafe packet path: {packet.path}")
    current = root
    for component in relative.parts:
        current = current / component
        require(not current.is_symlink(), f"symlinked packet input: {packet.path}")
    require(current.is_file() and current.stat().st_size < 2_000_000,
            f"missing or oversized packet input: {packet.path}")
    raw = current.read_bytes()
    require(sha256(raw) == packet.sha256, f"pinned proposal digest mismatch: {packet.path}")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"malformed proposal JSON: {packet.path}") from exc
    require(isinstance(data, dict), f"proposal envelope is not object: {packet.path}")
    return data


def digest_check(value, label, *, optional=False):
    if optional and value is None:
        return None
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
            f"invalid {label}")
    return value


def synopsis_check(value, status):
    if status == "WITHHELD_MULTIPART_IDENTITY":
        require(value is None, "withheld synopsis text must remain absent")
    else:
        require(type(value) is str and 25 <= len(value) <= 350 and "\n" not in value,
                "invalid or missing held publisher paraphrase")


def add_note(records, packet, row, *, series, row_id, title, season, episode,
             synopsis, status, guide_url, locator, description_digest=None,
             source_receipts=(), identity_hold=None, discovery_lineage=None,
             discovery_locator=None, discovery_sha256=None):
    require(isinstance(row_id, str) and row_id and isinstance(title, str) and title.strip(), "missing local identity/title")
    require(isinstance(guide_url, str) and guide_url.startswith("https://www.paramountplus.com/shows/")
            and "?" not in guide_url and "#" not in guide_url, "invalid publisher source URL")
    require(isinstance(locator, str) and locator.strip(), "missing publisher-card locator")
    require(type(season) is int and season > 0 and type(episode) is int and episode > 0,
            "invalid source-local episode slot")
    synopsis_check(synopsis, status)
    digest_check(description_digest, "publisher description digest", optional=True)
    digest_check(discovery_sha256, "upstream discovery digest", optional=True)
    note_id = f"{packet.kind.lower()}:{row_id}"
    require(note_id not in records, f"duplicate source-local note: {note_id}")
    require(not any(other["series"] == series and other["season"] == season and other["episode"] == episode
                    for other in records.values()), f"conflicting publisher-guide slot: {series} S{season} E{episode}")
    records[note_id] = {
        "note_id": note_id,
        "series": series,
        "medium": "EPISODE",
        "source_local_row_id": row_id,
        "source_local_title": title,
        "season": season,
        "episode": episode,
        "paraphrase": synopsis,
        "paraphrase_kind": "MARKETING_DESCRIPTION_PARAPHRASE",
        "review_state": status,
        "research_state": "HELD_SOURCE_LOCAL_NOT_ADMITTED",
        "canonical_work_id": None,
        "canonical_briefing_id": None,
        "publisher_family": "PARAMOUNT_CBS_CORPORATE_SINGLE_LINEAGE",
        "source_kind": "OFFICIAL_PUBLISHER_EPISODE_GUIDE_METADATA_NOT_EPISODE_CONTENT",
        "publisher_guide_url": guide_url,
        "source_card_locator": locator,
        "publisher_description_sha256": description_digest,
        "reported_source_receipts": list(source_receipts),
        "upstream_discovery_lineage": discovery_lineage,
        "upstream_discovery_locator": discovery_locator,
        "upstream_discovery_sha256": discovery_sha256,
        "source_packet_path": packet.path,
        "source_packet_sha256": packet.sha256,
        "source_row_sha256": sha256(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")),
        "identity_hold": identity_hold or "NO_GLOBAL_WORK_IDENTITY_ASSERTED",
    }


def emit_packet(records, packet, data, *, voy_metadata=None):
    if packet.kind == "ENT":
        require(data.get("source_family") == "paramount_corporate_publisher_family"
                and data.get("admission_effect") == "NONE" and data.get("coverage_effect") == "NONE"
                and data.get("public_synopsis_authorized") is False
                and data.get("audiovisual_episodes_watched") is False, "ENT held provenance/effect changed")
        rows = data.get("rows")
        require(type(rows) is list and len(rows) == packet.count, "ENT packet cardinality")
        for row in rows:
            require(row.get("mention_frame") == "LITERAL_PUBLISHER_DESCRIPTION_TEXT_ONLY_NOT_UTTERANCE_OR_DEPICTION"
                    and row.get("identity_hold") and isinstance(row.get("original_synopsis_draft"), str),
                    "ENT source-local hold/summary changed")
            add_note(records, packet, row, series="ENT", row_id=row["row_id"],
                     title=row["publisher_title"], season=row["season"], episode=row["episode"],
                     synopsis=row["original_synopsis_draft"], status="HELD_EDITORIAL_DRAFT",
                     guide_url=data["guide_url"],
                     locator=f"S{row['season']} E{row['episode']} > {row['publisher_title']} > publisher description",
                     description_digest=row["publisher_description_sha256"], identity_hold=row["identity_hold"],
                     discovery_lineage="PARAMOUNT_EPISODE_DISCOVERY_BUNDLE_ONLY",
                     discovery_locator="proposals/discovery/legacy-paramount-season1-20261102/ent/bundle.json",
                     discovery_sha256=data["accepted_ent_bundle_sha256"])
    elif packet.kind == "VOY_S4":
        require(data.get("status") == "HELD_PROPOSAL_ONLY" and data.get("coverage_effect") == "NONE"
                and data.get("global_work_identity_effect") == "NONE"
                and data.get("episode_source_read") is False, "VOY S4 held provenance/effect changed")
        rows = data.get("source_local_cards")
        require(type(rows) is list and len(rows) == packet.count, "VOY S4 packet cardinality")
        for row in rows:
            require(row.get("evidence_state") == "PUBLISHER_DISPLAY_ONLY_HELD"
                    and row.get("work_id") is None and row.get("synopsis_status") == "HELD_ORIGINAL_PARAPHRASE_REQUIRES_EDITORIAL_REVIEW",
                    "VOY S4 evidence/identity hold changed")
            add_note(records, packet, row, series="VOY", row_id=row["id"],
                     title=row["source_title"], season=row["season"], episode=row["source_ordinal"],
                     synopsis=row["original_synopsis"], status="HELD_EDITORIAL_DRAFT",
                     guide_url=data["source"]["url"], locator=row["locator"],
                     description_digest=row["blurb_sha256"], identity_hold=row["title_reconciliation"],
                     discovery_lineage="PARAMOUNT_SEASON_SLOT_DISCOVERY_CSV_ONLY",
                     discovery_locator=data["source"]["upstream_discovery_csv"],
                     discovery_sha256=data["source"]["upstream_discovery_sha256"])
    elif packet.kind == "PIC":
        require(data.get("proposal_only") is True and data.get("accepted_work_effect") == "NONE"
                and data.get("accepted_source_binding_effect") == "NONE" and data.get("coverage_effect") == "NONE",
                "PIC held provenance/effect changed")
        src = data["source"]
        require(src.get("full_primary_audiovisual_content_read") is False
                and src.get("raw_html_retained_in_public_repo") is False, "PIC source custody promoted")
        rows = data.get("source_local_episode_cards")
        require(type(rows) is list and len(rows) == packet.count, "PIC packet cardinality")
        for row in rows:
            require(row.get("synopsis_state") == "HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_FULL_EPISODE"
                    and row.get("thumbnail_status") == "HELD_NO_PUBLIC_DISPLAY_LICENSE", "PIC release hold changed")
            add_note(records, packet, row, series="PIC", row_id=row["local_id"],
                     title=row["title"], season=row["season"], episode=row["episode_number"],
                     synopsis=row["synopsis_paraphrase_candidate"], status="HELD_EDITORIAL_DRAFT",
                     guide_url=src["url"],
                     locator=f"publisher guide lines {row['guide_line_window'][0]}–{row['guide_line_window'][1]}",
                     source_receipts=src["raw_sample_receipts"],
                     discovery_lineage="PARAMOUNT_SEASON_SLOT_CROSSCHECK_ONLY",
                     discovery_locator=data["upstream_discovery"]["path"],
                     discovery_sha256=data["upstream_discovery"]["sha256"])
    elif packet.kind == "DIS":
        require(data.get("status") == "PROPOSAL_ONLY"
                and data.get("accepted_work_effect") == "NONE" and data.get("coverage_effect") == "NONE"
                and data.get("explorer_synopsis_release_effect") == "NONE"
                and data.get("audiovisual_episodes_watched") is False
                and data.get("full_episode_text_read") is False, "DIS source-local hold changed")
        src = data["source"]
        require(src.get("original_html_committed") is False, "DIS source custody promoted")
        rows = data.get("works")
        require(type(rows) is list and len(rows) == packet.count, "DIS packet cardinality")
        for row in rows:
            require(row.get("canonical_work_id") is None, "DIS Work identity promoted")
            add_note(records, packet, row, series="DIS", row_id=row["id"],
                     title=row["title"], season=row["season"], episode=row["episode"],
                     synopsis=row["original_synopsis"], status="HELD_EDITORIAL_DRAFT",
                     guide_url=src["url"],
                     locator=f"publisher HTML lines {row['raw_html_card_lines'][0]}–{row['raw_html_card_lines'][1]}",
                     description_digest=row["publisher_description_sha256"],
                     source_receipts=[{"sha256": src["raw_html_sha256"], "bytes": src["raw_html_bytes"]}],
                     discovery_lineage="PARAMOUNT_SEASON_SLOT_CROSSCHECK_ONLY",
                     discovery_locator=data["candidate_inventory_crosswalk"]["path"],
                     discovery_sha256=data["candidate_inventory_crosswalk"]["sha256"])
    elif packet.kind == "VOY_B006":
        require(voy_metadata is not None and data.get("data_status") == "SOURCE_LOCAL_PROMOTIONAL_PARAPHRASE_DRAFT_ONLY"
                and data.get("accepted_metadata_sha256") == VOY_B006_SOURCE.sha256
                and data.get("publication_approval") == "NONE" and data.get("coverage_effect") == "NONE"
                and data.get("work_admission_effect") == "NONE" and data.get("episodes_viewed") == 0,
                "VOY b006 source/effect changed")
        rows = data.get("rows")
        observed = voy_metadata.get("rows")
        require(type(rows) is list and len(rows) == packet.count and type(observed) is list
                and len(observed) == packet.count, "VOY b006 source cardinality")
        for row, source_row in zip(rows, observed):
            require(row.get("row_id") == source_row.get("source_local_row_id")
                    and row.get("title") == source_row.get("source_local_title")
                    and row.get("title_resolution") == source_row.get("title_resolution")
                    and source_row.get("source_local_context") == "VOY"
                    and source_row.get("admission_effect") == "NONE", "VOY b006 metadata crosswalk drift")
            card = source_row["official_card"]
            require(card.get("brief_description_actually_read") is True and card.get("raw_webpage_sha256") is None,
                    "VOY b006 unsupported source content custody")
            withheld = row.get("synopsis_status") == "WITHHELD_COMBINED_MULTIPART_IDENTITY_UNRESOLVED"
            require(row.get("synopsis_status") == ("WITHHELD_COMBINED_MULTIPART_IDENTITY_UNRESOLVED" if withheld
                    else "PENDING_INDEPENDENT_EDITORIAL_REVIEW"), "VOY b006 synopsis approval drift")
            add_note(records, packet, row, series="VOY", row_id=row["row_id"],
                     title=row["title"], season=card["season"], episode=card["episode"],
                     synopsis=row["synopsis"],
                     status="WITHHELD_MULTIPART_IDENTITY" if withheld else "HELD_EDITORIAL_DRAFT",
                     guide_url=card["guide_url"], locator=card["section_locator"],
                     identity_hold=row["title_resolution"],
                     discovery_lineage=source_row["source_local_lineage"],
                     discovery_locator=source_row["source_local_locator"],
                     discovery_sha256=VOY_B006_SOURCE.sha256)
    else:
        raise ValueError(f"unknown compiler adapter: {packet.kind}")


def compile_notes(root=REPO, packets=PACKETS):
    records = {}
    voy_metadata = read_packet(VOY_B006_SOURCE, root) if any(packet.kind == "VOY_B006" for packet in packets) else None
    for packet in packets:
        data = read_packet(packet, root)
        before = len(records)
        emit_packet(records, packet, data, voy_metadata=voy_metadata)
        require(len(records) - before == packet.count, f"packet lost/duplicated source rows: {packet.path}")
    notes = sorted(records.values(), key=lambda row: (row["series"], row["season"], row["episode"], row["note_id"]))
    drafts = sum(row["paraphrase"] is not None for row in notes)
    holds = len(notes) - drafts
    if packets == PACKETS:
        require(drafts == 57 and holds == 1, "unexpected accepted-main held-note cardinality")
    return {
        "schema_version": SCHEMA,
        "data_status": "HELD_SOURCE_LOCAL_DERIVED_SIDECAR_NOT_CANONICAL",
        "source_family_independence": "ALL_PARAMOUNT_CBS_CORPORATE_SINGLE_LINEAGE_NOT_INDEPENDENT_EPISODE_CORROBORATION",
        "source_documents": [{"path": packet.path, "sha256": packet.sha256, "observations": packet.count} for packet in packets],
        "source_local_observation_count": len(notes),
        "held_paraphrase_count": drafts,
        "withheld_identity_count": holds,
        "canonical_work_count_added": 0,
        "canonical_briefing_count_added": 0,
        "episode_coverage_effect": "NONE",
        "synopsis_publication_approval": "NONE",
        "artwork_publication_approval": "NONE",
        "denominator_note": "Counts source-local publisher-guide observations; not distinct episodes, Works, primary-source reads, or accepted coverage.",
        "notes": notes,
    }


def serialized(data):
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def run(*, check=False, root=REPO):
    data = compile_notes(root)
    destination = root / OUTPUT
    payload = serialized(data)
    require(not destination.is_symlink() and not destination.parent.is_symlink(), "symlinked output refused")
    if check:
        require(destination.is_file() and destination.read_bytes() == payload, "stale publisher-guide notes sidecar")
    else:
        temp = destination.with_name(".publisher-guide-notes.json.tmp")
        require(not temp.exists() and not temp.is_symlink(), "temporary output already exists")
        try:
            temp.write_bytes(payload)
            os.replace(temp, destination)
        finally:
            temp.unlink(missing_ok=True)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = run(check=args.check)
    print(f"HELD_PUBLISHER_GUIDE_NOTES_OK: {data['held_paraphrase_count']} notes + {data['withheld_identity_count']} hold; zero Work/Briefing/coverage effects")


if __name__ == "__main__":
    main()
