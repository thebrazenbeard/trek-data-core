"""Fail-closed structural validation for the SNW S3/E06–10 publisher-card proposal.

This does not validate depicted episode events, admit canonical identities, or
authorize publication of source images; those are separate research gates.
"""

from datetime import datetime
import json
from pathlib import Path
from urllib.parse import urlparse


HERE = Path(__file__).resolve().parent
EXPECTED = [
    (6, "The Sehlat Who Ate Its Tail", "2025-08-14T03:00:00-07:00", (1630, 1654), "8xFW5cr_Md8aQJnq_LL8GSkmQiOfOo4q", 1633),
    (7, "What is Starfleet?", "2025-08-21T03:00:00-07:00", (1658, 1682), "TnvjBKqK_a9q5I2OvQa9gncUYwOUdCVt", 1661),
    (8, "Four-and-a-Half Vulcans", "2025-08-28T03:00:00-07:00", (1686, 1710), "lTwwMmmIgsNPBTR8Y9bkNjfCuuq1MPpf", 1689),
    (9, "Terrarium", "2025-09-04T03:00:00-07:00", (1714, 1738), "AfpvVBONdI5AA_gpRdjRsLGe0ozAPTm4", 1717),
    (10, "New Life and New Civilizations", "2025-09-11T03:00:00-07:00", (1742, 1766), "_m6Ipk4F0HyBL8Rqe0eeBkhDehCm9fQX", 1745),
]


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


def ids(records, key):
    values = [x.get(key) for x in records]
    require(all(isinstance(x, str) and x for x in values), f"missing {key}")
    require(len(values) == len(set(values)), f"duplicate {key}")
    return set(values)


def validate_records(data):
    require(data.get("schema_version") == "1.0.0", "schema version")
    require(data.get("batch_id") == "SNW.PPLUS.S3.LAST5.20261103", "batch ID")
    require(data.get("lane") == "SNW" and data.get("proposal_only") is True, "lane proposal gate")
    for key in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "explorer_effect"):
        require(data.get(key) == "NONE", f"unapproved {key}")
    require(data.get("audiovisual_content_inspected") is False, "uninspected AV content elevated")
    require(data.get("full_primary_source_available") is False, "full AV source claim unsupported")

    source = data.get("source")
    require(isinstance(source, dict), "missing source")
    require(source.get("source_local_id") == "snw-s3-paramount-guide-last5-20261103", "source identity")
    require(source.get("publisher") == "Paramount+" and source.get("kind") == "PUBLISHER_EPISODE_GUIDE_HTML", "source type")
    require(source.get("url") == "https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/3/", "source URL")
    require(source.get("independence_group") == "publisher:paramountplus.com", "source independence claim")
    require(source.get("retrieved_utc_date") == "2026-11-03", "source retrieval date")
    require(source.get("response_status") == 200 and source.get("response_body_bytes") == 271803, "response receipt")
    require(source.get("response_sha256") == "a970f41f9257adc002d86d7036dd0e495d0c3e92a9c51b2ef234638e859317bb", "response digest")
    require(source.get("response_digest_stability") == "DYNAMIC_SITE_UNDETERMINED", "incorrect source snapshot stability")
    require(source.get("snapshot_committed") is False and source.get("publisher_revision") is None, "fabricated source archival claim")

    keys = ("works", "evidence", "assertions", "local_entities", "artwork_candidates")
    require(all(isinstance(data.get(key), list) for key in keys), "missing records")
    works, evidence, assertions, entities, images = (data[key] for key in keys)
    require(len(works) == len(evidence) == len(assertions) == len(images) == 5, "unexpected publisher-card count")
    require(len(entities) == 7, "unexpected source-local mention count")
    work_ids = ids(works, "local_work_id")
    evidence_ids = ids(evidence, "evidence_id")
    entity_ids = ids(entities, "local_entity_id")
    ids(assertions, "assertion_id")
    entity_by_id = {x["local_entity_id"]: x for x in entities}
    evidence_by_id = {x["evidence_id"]: x for x in evidence}

    for work, (episode, title, stamp, span, video_token, _) in zip(works, EXPECTED):
        require(work.get("local_work_id") == f"snw-s3-e{episode:02d}-pplus", "publisher work ID")
        require(work.get("season") == 3 and work.get("episode_number") == episode and work.get("title") == title, "publisher episode mismatch")
        require(work.get("source_datetime") == stamp and datetime.fromisoformat(stamp).utcoffset() is not None, "publisher date mismatch")
        require(tuple(work.get("card_html_lines", [])) == span, "publisher source locator")
        require(work.get("publisher_video_url") == f"https://www.paramountplus.com/shows/video/{video_token}/", "publisher video URL mismatch")
        require(work.get("source_binding_id") is None and work.get("canonical_work_id") is None, "premature Work reconciliation")

    for entity in entities:
        require(entity.get("work_id") in work_ids, "orphan entity")
        require(entity.get("kind") in ("PERSON_MENTION", "VESSEL_MENTION", "ROLE_MENTION", "SPECIES_MENTION"), "invalid mention type")
        require(isinstance(entity.get("label"), str) and entity["label"], "missing mention label")
        require(entity.get("global_entity_id") is None, "unadmitted global identity")

    for record in evidence:
        require(record.get("work_id") in work_ids, "orphan evidence")
        require(record.get("source_local_id") == source["source_local_id"], "source-local provenance mismatch")
        require(record.get("kind") == "PUBLISHER_DESCRIPTION" and record.get("observation_scope") == "PUBLISHER_TEXT_ONLY", "fiction truth elevated from publisher description")
        require(isinstance(record.get("locator"), str) and "HTML lines" in record["locator"], "missing source locator")
        paraphrase = record.get("paraphrase")
        require(isinstance(paraphrase, str) and 40 <= len(paraphrase) <= 250, "missing or bloated source-relative paraphrase")
        require("<" not in paraphrase and ">" not in paraphrase, "source HTML leak")

    for assertion in assertions:
        work_id, evidence_id = assertion.get("work_id"), assertion.get("evidence_id")
        require(work_id in work_ids and evidence_id in evidence_ids and evidence_by_id[evidence_id]["work_id"] == work_id, "cross-work assertion")
        require(assertion.get("predicate") == "PUBLISHER_SUMMARY_MENTIONS", "unadmitted assertion predicate")
        require(assertion.get("status") == "SOURCE_RELATIVE_UNVERIFIED_EPISODE_CONTENT", "publisher report asserted as fiction fact")
        ref_ids = assertion.get("local_entity_ids")
        require(isinstance(ref_ids, list) and ref_ids, "missing assertion mentions")
        for entity_id in ref_ids:
            require(entity_id in entity_ids and entity_by_id[entity_id]["work_id"] == work_id, "cross-work mention")

    for art, work, (_, _, _, span, _, image_line) in zip(images, works, EXPECTED):
        require(art.get("work_id") == work["local_work_id"], "artwork cross-work association")
        parsed = urlparse(art.get("source_url", ""))
        require(parsed.scheme == "https" and parsed.netloc == "thumbnails.cbsig.net" and parsed.path.endswith(".jpg"), "untrusted artwork URL")
        require(art.get("source_kind") == "PUBLISHER_CARD_THUMBNAIL", "artwork source type")
        require(art.get("html_line") == image_line and span[0] <= image_line <= span[1], "artwork card locator")
        require(art.get("rights_status") == "UNASSESSED", "unverified artwork license")
        require(art.get("local_copy") is False and art.get("repo_distribution") == "NONE" and art.get("explorer_effect") == "NONE", "unreviewed artwork publication")

    require({x.get("kind") for x in data.get("counterevidence_and_limits", [])} == {
        "SHARED_LINEAGE", "PUBLISHER_CARD_SCOPE", "NO_IDENTITY_MERGE", "IMAGE_LOCATORS_ONLY", "WEBSITE_VARIABILITY"
    }, "missing uncertainty classes")
    return len(works)


if __name__ == "__main__":
    n = validate_records(json.loads((HERE / "records.json").read_text(encoding="utf-8")))
    print(f"SNW_S3_PUBLISHER_SOURCE_VALIDATED: {n} candidate cards; no accepted coverage/Works/Explorer effects")
