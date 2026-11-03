"""Fail-closed source-local validation for unpublished Voyager B006 synopsis drafts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE_PATH = ROOT / "proposals/verification/episode-guide-rechecks-b006-voy-20261103/records.json"
PACKET_PATH = Path(__file__).with_name("records.json")

# These two publisher-card paraphrases were narrowed after independent source
# review.  Pin the corrected wording until another reviewed, source-bound
# supersession is proposed, preventing a reverted overclaim from passing CI.
SOURCE_NARROWING_LOCKS = {
    "lead:0072": "Voyager is forced out of warp when it detects a dangerous particle called Omega, whose properties are linked to subspace.",
    "lead:0078": "The Doctor finds that his passion for music starts influencing matters in his personal life.",
}


def validate(packet: dict | None = None, source: dict | None = None) -> int:
    source_bytes = SOURCE_PATH.read_bytes()
    pinned_hash = hashlib.sha256(source_bytes).hexdigest()
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8")) if packet is None else packet
    source = json.loads(source_bytes) if source is None else source

    expected = {
        "data_status": "SOURCE_LOCAL_PROMOTIONAL_PARAPHRASE_DRAFT_ONLY",
        "source_representation": "OFFICIAL_RENDERED_CARD_TEXT_UNPINNED",
        "publisher_family": "paramount_corporate_publisher_family",
        "publication_approval": "NONE",
        "work_admission_effect": "NONE",
        "evidence_admission_effect": "NONE",
        "coverage_effect": "NONE",
        "verification_counter_effect": "NONE",
        "episodes_viewed": 0,
        "transcripts_read": 0,
        "raw_webpage_bytes_custodied": False,
    }
    for key, value in expected.items():
        if packet.get(key) != value:
            raise ValueError(f"protected status changed: {key}")
    if packet.get("accepted_metadata_sha256") != pinned_hash:
        raise ValueError("accepted source metadata sha256 mismatch")
    if packet.get("accepted_metadata_source") != SOURCE_PATH.relative_to(ROOT).as_posix():
        raise ValueError("accepted source path changed")
    if packet.get("draft_lineage_sha256") != "cd3d6297e202fd6eefd813b9339fe4e2af11b9643dec0527d61d49b695d8584d":
        raise ValueError("superseded candidate lineage hash changed")
    if packet.get("draft_lineage_pr") != 290:
        raise ValueError("superseded candidate lineage changed")

    rows = packet.get("rows")
    source_rows = source.get("rows")
    if not isinstance(rows, list) or len(rows) != 13 or not isinstance(source_rows, list) or len(source_rows) != 13:
        raise ValueError("expected exactly thirteen existing Voyager observations")
    expected_ids = [f"lead:{i:04d}" for i in range(70, 83)]
    if [item.get("row_id") for item in rows] != expected_ids:
        raise ValueError("draft row IDs changed or repeated")
    if [item.get("source_local_row_id") for item in source_rows] != expected_ids:
        raise ValueError("accepted metadata source row IDs changed")
    if any(item.get("source_local_context") != "VOY" for item in source_rows):
        raise ValueError("non-Voyager metadata source row")

    published = 0
    for item, observed in zip(rows, source_rows):
        if set(item) != {"row_id", "title", "title_resolution", "synopsis", "synopsis_status"}:
            raise ValueError("unknown field in synopsis proposal")
        if item["title"] != observed.get("source_local_title"):
            raise ValueError(f"source-local title mismatch: {item['row_id']}")
        if item["title_resolution"] != observed.get("title_resolution"):
            raise ValueError(f"unresolved title relation overwritten: {item['row_id']}")
        description = item["synopsis"]
        if item["row_id"] in SOURCE_NARROWING_LOCKS and description != SOURCE_NARROWING_LOCKS[item["row_id"]]:
            raise ValueError(f"reviewed source-bound paraphrase changed: {item['row_id']}")
        if item["row_id"] == "lead:0074":
            if description is not None or item["synopsis_status"] != "WITHHELD_COMBINED_MULTIPART_IDENTITY_UNRESOLVED":
                raise ValueError("Caretaker combined multipart must stay withheld")
            if item["title_resolution"] != "MULTIPART_TITLE_SCOPE_UNRESOLVED":
                raise ValueError("Caretaker multipart ambiguity lost")
        else:
            if (not isinstance(description, str) or len(description.strip()) < 25
                    or len(description) > 350 or "\n" in description):
                raise ValueError(f"invalid original short paraphrase: {item['row_id']}")
            if item["synopsis_status"] != "PENDING_INDEPENDENT_EDITORIAL_REVIEW":
                raise ValueError(f"unapproved public synopsis: {item['row_id']}")
            published += 1
    if published != 12:
        raise ValueError("expected twelve unapproved drafts and one null hold")
    return published


if __name__ == "__main__":
    print(f"VOY_B006_UNPUBLISHED_SYNOPSES_OK: {validate()} drafts, one multipart hold")
