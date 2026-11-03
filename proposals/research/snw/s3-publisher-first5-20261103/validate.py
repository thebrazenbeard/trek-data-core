"""Validate the unadmitted SNW Season 3 Paramount+ metadata source packet.

This validator intentionally cannot certify that any episode was watched, any
work was admitted, or any candidate thumbnail may be distributed.
"""

from datetime import datetime
import json
from pathlib import Path
from urllib.parse import urlparse


HERE = Path(__file__).resolve().parent
EXPECTED = [
    (1, "Hegemony, Part II", "2025-07-17T03:00:00-07:00", (1490, 1512)),
    (2, "Wedding Bell Blues", "2025-07-17T03:00:00-07:00", (1518, 1540)),
    (3, "Shuttle to Kenfori", "2025-07-24T03:00:00-07:00", (1546, 1568)),
    (4, "A Space Adventure Hour", "2025-07-31T03:00:00-07:00", (1574, 1596)),
    (5, "Through the Lens of Time", "2025-08-07T03:00:00-07:00", (1602, 1624)),
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_ids(rows, field):
    vals = [x.get(field) for x in rows]
    require(all(isinstance(x, str) and x for x in vals), f"missing {field}")
    require(len(set(vals)) == len(vals), f"duplicate {field}")
    return set(vals)


def validate_records(data):
    require(data.get("schema_version") == "1.0.0", "wrong schema")
    require(data.get("batch_id") == "SNW.PPLUS.S3.FIRST5.20261103", "wrong batch")
    require(data.get("lane") == "SNW", "partition violation")
    require(data.get("proposal_only") is True, "must remain proposal-only")
    for key in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "explorer_effect"):
        require(data.get(key) == "NONE", f"unauthorized {key}")
    for key in ("audiovisual_content_inspected", "full_primary_source_available"):
        require(data.get(key) is False, f"unsubstantiated source claim {key}")

    src = data.get("source", {})
    require(src.get("source_local_id") == "snw-s3-paramount-guide-20261103", "source ID mismatch")
    require(src.get("publisher") == "Paramount+", "publisher mismatch")
    require(src.get("kind") == "PUBLISHER_EPISODE_GUIDE_HTML", "source type mismatch")
    require(src.get("independence_group") == "publisher:paramountplus.com", "lineage mismatch")
    require(src.get("url") == "https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/3/", "source URL mismatch")
    require(src.get("retrieved_utc_date") == "2026-11-03", "unverified retrieval date")
    require(src.get("response_status") == 200 and src.get("response_body_bytes") == 271774, "response receipt mismatch")
    require(src.get("response_sha256") == "a2b3363d658b003c83732945b75c23621f16bb4fc782fb395b2b0c2a79796863", "body digest mismatch")
    require(src.get("second_response_sha256") == "dffc10f7e996ab0de9f2acc671823468d720c93cabed2f687a3c742843994254", "second observation digest mismatch")
    require(src.get("response_digest_stability") == "VOLATILE_WITH_SAME_BYTE_COUNT", "unstable HTML digest disguised as immutable")
    require(src.get("snapshot_committed") is False and src.get("publisher_revision") is None, "fabricated snapshot/revision")

    works, evidence, assertions, entities, images = (
        data.get("works"), data.get("evidence"), data.get("assertions"),
        data.get("local_entities"), data.get("artwork_candidates"),
    )
    require(all(isinstance(x, list) for x in (works, evidence, assertions, entities, images)), "missing data arrays")
    require(len(works) == len(evidence) == len(assertions) == len(images) == 5, "five-card tranche expected")
    works_set = unique_ids(works, "local_work_id")
    evidence_set = unique_ids(evidence, "evidence_id")
    entity_set = unique_ids(entities, "local_entity_id")
    unique_ids(assertions, "assertion_id")
    entities_by_id = {x["local_entity_id"]: x for x in entities}
    evidence_by_id = {x["evidence_id"]: x for x in evidence}

    for row, (n, title, timestamp, span) in zip(works, EXPECTED):
        require(row.get("local_work_id") == f"snw-s3-e{n:02d}-pplus", "local Work ID mismatch")
        require(row.get("season") == 3 and row.get("episode_number") == n and row.get("title") == title, "publisher episode mismatch")
        require(row.get("source_datetime") == timestamp, "publisher datetime mismatch")
        require(tuple(row.get("card_html_lines", [])) == span, "source locator mismatch")
        require(datetime.fromisoformat(timestamp).utcoffset() is not None, "missing source timezone")
        require(row.get("source_binding_id") is None and row.get("canonical_work_id") is None, "premature global Work binding")
        require(urlparse(row.get("publisher_video_url", "")).netloc == "www.paramountplus.com", "nonpublisher episode URL")
        require(row["publisher_video_url"].startswith("https://www.paramountplus.com/shows/video/"), "bad video path")
    require(len({x["publisher_video_url"] for x in works}) == 5, "duplicate episode video URL")

    for row in entities:
        require(row.get("work_id") in works_set, "orphan entity")
        require(row.get("global_entity_id") is None, "unadmitted global entity link")
        require(row.get("kind") in ("PERSON_MENTION", "VESSEL_MENTION"), "unknown entity kind")
        require(isinstance(row.get("label"), str) and row["label"], "missing entity label")

    for row in evidence:
        require(row.get("work_id") in works_set, "orphan evidence")
        require(row.get("source_local_id") == src["source_local_id"], "cross-source evidence")
        require(row.get("kind") == "PUBLISHER_DESCRIPTION" and row.get("observation_scope") == "PUBLISHER_TEXT_ONLY", "publisher statement promoted to episode fact")
        require(isinstance(row.get("locator"), str) and "HTML lines" in row["locator"], "missing source-relative locator")
        require(isinstance(row.get("paraphrase"), str) and 40 <= len(row["paraphrase"]) <= 240, "missing or long paraphrase")
        require("<" not in row["paraphrase"] and ">" not in row["paraphrase"], "HTML leaked into paraphrase")

    for row in assertions:
        require(row.get("work_id") in works_set, "orphan assertion")
        ref = row.get("evidence_id")
        require(ref in evidence_set and evidence_by_id[ref]["work_id"] == row["work_id"], "cross-work assertion")
        require(row.get("predicate") == "PUBLISHER_SUMMARY_MENTIONS", "unsupported objective-fiction predicate")
        require(row.get("status") == "SOURCE_RELATIVE_UNVERIFIED_EPISODE_CONTENT", "unwarranted truth elevation")
        refs = row.get("local_entity_ids")
        require(isinstance(refs, list) and refs, "empty entity references")
        for entity_ref in refs:
            require(entity_ref in entity_set and entities_by_id[entity_ref]["work_id"] == row["work_id"], "cross-work mention")

    for art, work in zip(images, works):
        require(art.get("work_id") == work["local_work_id"], "artwork cross-work association")
        require(urlparse(art.get("source_url", "")).netloc == "thumbnails.cbsig.net", "unexpected thumbnail host")
        require(art.get("source_kind") == "PUBLISHER_CARD_THUMBNAIL", "artwork evidence kind mismatch")
        require(art.get("rights_status") == "UNASSESSED", "unverified artwork license")
        require(art.get("local_copy") is False and art.get("repo_distribution") == "NONE" and art.get("explorer_effect") == "NONE", "unreviewed publication")
        require(isinstance(art.get("html_line"), int) and work["card_html_lines"][0] <= art["html_line"] <= work["card_html_lines"][1], "artwork locator outside card")
    require({x["kind"] for x in data.get("counterevidence_and_limits", [])} == {
        "NOT_INDEPENDENT", "DYNAMIC_HTML_DIGEST", "UNINSPECTED_PRIMARY_AV", "CROSS_SEASON_TITLE_UNRESOLVED", "ARTWORK_RIGHTS_UNASSESSED"
    }, "required uncertainty classes missing")
    return len(works)


if __name__ == "__main__":
    count = validate_records(json.loads((HERE / "records.json").read_text(encoding="utf-8")))
    print(f"SNW_S3_PUBLISHER_SOURCE_VALIDATED: {count} publisher cards; 0 admitted Works, coverage or Explorer effects")
