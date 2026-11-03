#!/usr/bin/env python3
"""Fail-closed, source-local validation of the DIS S3 Paramount guide proposal."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records.json"
# Raw-repository record custody, updated only with a reviewed editorial correction.
RECORDS_SHA256 = "a80c8df4a9885d210db3e6bf69440eb05f11292a676329c2e860d55fcb4a22f1"
SOURCE_URL = "https://www.paramountplus.com/shows/star-trek-discovery/episodes/3/"
EXPECTED = (
    ("Forget Me Not", "Q100327253", "9QFl6ub5zIcHljkBWPZMcSBfDz9eFGNl", "304_NO_LOGO"),
    ("Die Trying", "Q100327254", "H_y5oaUVjtq8NmOnkVhQVUuTBRbSit8y", "305_NO_LOGO"),
    ("Scavengers", "Q100327258", "f3PngaryfJwyvS81U_qB9kqhnhJoHMPj", "306_NO_LOGO"),
    ("Unification III", "Q100327260", "BJtfcsojwp4z7C_zddvNqhjU36_vwoA2", "307_NO_LOGO"),
    ("The Sanctuary", "Q100327261", "mUJjsKkUd01TLh_jsfDB5O3yRMZlDRSP", "308_NO_LOGO"),
    ("Terra Firma, Part 1", "Q100327263", "73BJ1N0qerkG0WPoUKNuDPcvBdvD6fEX", "309_NO_LOGO"),
    ("Terra Firma, Part 2", "Q100327265", "vAMnijrEC3s_g9cuwb7ZFnfKupYLQL3j", "310_NO_LOGO"),
)


def _require(condition: bool, issue: str) -> None:
    if not condition:
        raise ValueError(issue)


def validate_records(data: dict) -> None:
    _require(isinstance(data, dict), "record root must be object")
    _require(set(data) == {
        "schema_version", "batch_id", "lane", "proposal_only",
        "accepted_source_binding_effect", "accepted_work_effect",
        "coverage_effect", "denominator_effect", "explorer_effect",
        "audiovisual_content_inspected", "full_primary_source_available",
        "source", "works", "local_entities", "evidence", "assertions",
        "artwork_candidates", "counterevidence_and_limits",
    }, "unknown or missing root fields")
    _require(data.get("schema_version") == "1.0.0", "schema version mismatch")
    _require(data.get("lane") == "DIS" and data.get("proposal_only") is True, "not DIS proposal")
    for name in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "explorer_effect"):
        _require(data.get(name) == "NONE", f"promoted {name}")
    _require(data.get("audiovisual_content_inspected") is False, "false AV close-read")
    _require(data.get("full_primary_source_available") is False, "false primary-source claim")
    source = data.get("source") or {}
    _require(source.get("url") == SOURCE_URL, "publisher guide URL changed")
    _require(source.get("independence_group") == "publisher:paramountplus.com", "source lineage changed")
    _require(source.get("response_status") == 200, "source HTTP receipt changed")
    _require(source.get("response_digest_stability") == "VOLATILE_WITH_SAME_BYTE_COUNT", "digest falsely stabilized")
    _require(source.get("snapshot_committed") is False and source.get("publisher_revision") is None, "fabricated raw custody")
    for key in ("response_sha256", "second_response_sha256"):
        _require(bool(re.fullmatch(r"[0-9a-f]{64}", str(source.get(key, "")))), f"bad {key}")
    _require(source.get("response_sha256") != source.get("second_response_sha256"), "lost dynamic receipt")
    works, evidence = data.get("works"), data.get("evidence")
    entities, assertions, artwork = data.get("local_entities"), data.get("assertions"), data.get("artwork_candidates")
    _require(all(isinstance(rows, list) for rows in (works, evidence, entities, assertions, artwork)), "missing list")
    _require((len(works), len(evidence), len(entities), len(assertions), len(artwork)) == (7, 7, 13, 7, 7), "cardinality")
    ids = set()
    for i, (work, expected) in enumerate(zip(works, EXPECTED), start=4):
        title, qid, video_id, art_marker = expected
        work_id = f"dis-s3-e{i:02d}-pplus"
        _require(set(work) == {
            "local_work_id", "lead_id", "episode_qid", "season", "episode_number",
            "title", "source_datetime", "card_html_lines", "publisher_video_url",
            "source_binding_id", "canonical_work_id",
        }, "unknown work fields")
        _require(work.get("local_work_id") == work_id and work_id not in ids, "work ID changed/duplicated")
        ids.add(work_id)
        _require(work.get("lead_id") == f"lead:{i+104:04d}", "discovery crosswalk changed")
        _require(work.get("episode_qid") == qid, "external QID changed")
        _require(work.get("season") == 3 and work.get("episode_number") == i and work.get("title") == title, "publisher slot mismatch")
        _require(work.get("source_binding_id") is None and work.get("canonical_work_id") is None, "premature identity admission")
        _require(work.get("publisher_video_url") == f"https://www.paramountplus.com/shows/video/{video_id}/", "wrong episode video")
        _require(bool(re.fullmatch(r"2020-\d\d-\d\dT23:00:00-08:00", work.get("source_datetime", ""))), "date mismatch")
        _require(work.get("card_html_lines") == [1500 + (i-4)*28 + 112, 1523 + (i-4)*28 + 112], "line locator mismatch")
        ev = evidence[i-4]
        _require(set(ev) == {
            "evidence_id", "work_id", "source_local_id", "kind",
            "locator", "paraphrase", "observation_scope",
        }, "unknown evidence fields")
        _require(ev.get("work_id") == work_id and ev.get("evidence_id") == f"dis-e{i:02d}-publisher-copy", "evidence binding changed")
        _require(ev.get("kind") == "PUBLISHER_DESCRIPTION" and ev.get("observation_scope") == "PUBLISHER_TEXT_ONLY", "publisher copy promoted")
        _require(ev.get("source_local_id") == source.get("source_local_id"), "evidence source mismatch")
        _require(bool(ev.get("paraphrase")) and len(ev["paraphrase"]) < 300, "missing or excessive original paraphrase")
        art = artwork[i-4]
        _require(set(art) == {"work_id", "source_url", "html_line", "rights_status", "local_copy"}, "unknown artwork fields")
        _require(art.get("work_id") == work_id and art.get("rights_status") == "UNASSESSED" and art.get("local_copy") is False, "artwork rights mutated")
        art_url = art.get("source_url", "")
        parsed = urlsplit(art_url)
        _require(parsed.scheme == "https" and parsed.netloc == "thumbnails.cbsig.net" and parsed.path.endswith(".jpg"), "artwork source host")
        _require(art_marker in parsed.path and art.get("html_line") == 1614 + (i-4)*28, "image/card cross-binding")
        a = assertions[i-4]
        _require(set(a) == {"assertion_id", "work_id", "evidence_id", "predicate", "local_entity_ids", "status"}, "unknown assertion fields")
        _require(a.get("work_id") == work_id and a.get("evidence_id") == ev["evidence_id"], "assertion/evidence mismatch")
        _require(a.get("predicate") == "PUBLISHER_SUMMARY_MENTIONS" and a.get("status") == "SOURCE_RELATIVE_UNVERIFIED_EPISODE_CONTENT", "assertion promoted")
    entity_ids = {x.get("local_entity_id") for x in entities}
    _require(len(entity_ids) == len(entities), "duplicate local entity IDs")
    for entity in entities:
        _require(set(entity) == {"local_entity_id", "work_id", "label", "kind", "global_entity_id"}, "unknown entity fields")
        _require(entity.get("work_id") in ids and entity.get("global_entity_id") is None, "entity global identity promotion")
    for assertion in assertions:
        _require(set(assertion.get("local_entity_ids", ())) <= entity_ids, "assertion references absent local entity")
    kinds = {x.get("kind") for x in data.get("counterevidence_and_limits", ())}
    _require({"SAME_SOURCE_LINEAGE", "EXISTING_DISCOVERY_CANDIDATES", "TITLE_MULTIPART_AMBIGUITY", "UNINSPECTED_AV", "ARTWORK_HELD"} <= kinds, "limits omitted")
    _require(all("private" not in json.dumps(x).lower() for x in works), "private source path")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=RECORDS)
    options = parser.parse_args()
    raw = options.path.read_bytes()
    data = json.loads(raw)
    validate_records(data)
    _require(hashlib.sha256(raw).hexdigest() == RECORDS_SHA256, "unpinned record bytes; independent review required")
    print(f"DIS S3 publisher proposal PASS: {len(data['works'])} source-relative observations; raw SHA-256 pinned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
