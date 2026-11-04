"""Fail-closed structural checks; not a validation of transcript truth or rights."""

import json
import re
from pathlib import Path


RECORDS = Path(__file__).with_name("records.json")
HASH = re.compile(r"[0-9a-f]{64}\Z")
SOURCE_URL = "https://www.springfieldspringfield.co.uk/view_episode_scripts.php?episode=s01e01&tv-show=star-trek-the-animated-series-1973"
RAW_HTML_SHA256 = "07bdbddad2000679c6c97b86b0fb7aa7316c2891c248e42e711cbdabac8ee198"
FRAGMENT_STREAM_SHA256 = "9b5bba7a654c66b8d294c5b08bdc299ea1bbbf09245ac3c5c4fe8024cc1652a3"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(data):
    require(data.get("schema_version") == "1.0.0", "schema version drift")
    require(data.get("role") == "TAS", "wrong worker lane")
    require(data.get("proposal_only") is True, "nonproposal research")
    for effect in ("admission_effect", "coverage_effect", "global_identity_effect", "public_artwork_release_effect"):
        require(data.get(effect) == "NONE", f"prohibited effect: {effect}")
    source = data.get("source", {})
    work = data.get("work", {})
    require(source.get("url") == SOURCE_URL, "source URL identity mismatch")
    require(source.get("source_id") == "src:tas001:springfield-20261103", "source identity drift")
    require(source.get("kind") == "THIRD_PARTY_DERIVATIVE_TRANSCRIPT", "source type elevated")
    require(source.get("lineage_status") == "UNKNOWN_NOT_INDEPENDENTLY_ESTABLISHED", "unverified lineage promoted")
    require(source.get("http_status") == 200, "source not retrieved")
    require(source.get("raw_html_bytes") == 43366 and source.get("raw_html_sha256") == RAW_HTML_SHA256,
            "invalid raw-source receipt")
    require(source.get("fragment_count") == 263 and source.get("normalized_fragment_stream_sha256") == FRAGMENT_STREAM_SHA256,
            "invalid fragment receipt")
    require(source.get("all_fragments_read") is True, "source batch not actually processed")
    for flag in ("authenticated_primary_audiovisual", "transcript_accuracy_independently_verified", "copyright_source_text_committed"):
        require(source.get(flag) is False, f"unverified promotion: {flag}")
    require(source.get("private_source_custody") == "TRANSIENT_LOCAL_ONLY", "private custody invented")
    require(work.get("work_id") == "work:tas001:beyond-farthest-star", "global Work identity invented")
    require(work.get("work_identity_status") == "CANDIDATE_UNRECONCILED", "Work identity promoted")
    require(work.get("publisher_season_episode_label") == "S1E1", "source-local episode label drift")

    entities = data.get("local_entities")
    evidence = data.get("evidence")
    assertions = data.get("assertions")
    require(isinstance(entities, list) and len(entities) == 12, "entity inventory mismatch")
    require(isinstance(evidence, list) and len(evidence) == 15, "evidence inventory mismatch")
    require(isinstance(assertions, list) and len(assertions) == 7, "assertion inventory mismatch")
    ent_ids = [e.get("id") for e in entities]
    require(all(isinstance(i, str) and i.startswith("ent:tas001:") for i in ent_ids), "nonlocal entity")
    require(len(set(ent_ids)) == len(ent_ids), "duplicate entity")
    evid_ids = [e.get("id") for e in evidence]
    require(all(isinstance(i, str) and i.startswith("ev:tas001:") for i in evid_ids), "nonlocal evidence")
    require(len(set(evid_ids)) == len(evid_ids), "duplicate evidence")
    previous_start = 0
    for e in evidence:
        r = e.get("fragment_range", [])
        require(len(r) == 2 and all(type(n) is int for n in r) and 1 <= r[0] <= r[1] <= 263,
                "invalid fragment locator")
        require(r[0] > previous_start, "out-of-order or duplicate fragment start")
        previous_start = r[0]
        require(HASH.fullmatch(e.get("segment_sha256", "")), "invalid fragment fingerprint")
        require(e.get("kind") in {"LOG_RECORD", "SENSOR_REPORT", "DIALOGUE_TESTIMONY", "COMMUNICATION_REPORT", "TRANSLATED_MESSAGE", "SYSTEM_REPORT", "EXPERIMENT_REPORT", "DIALOGUE_AND_HYPOTHESIS", "ACTION_AND_DIALOGUE"}, "unknown evidence kind")
        require(isinstance(e.get("frame"), str) and len(e["frame"]) >= 8, "missing evidence frame")
        require(isinstance(e.get("paraphrase"), str) and 35 <= len(e["paraphrase"]) <= 360 and "<" not in e["paraphrase"],
                "missing paraphrase or source text injection")
        require(isinstance(e.get("entity_ids"), list) and e["entity_ids"] and set(e["entity_ids"]) <= set(ent_ids),
                "entity reference mismatch")
    assertion_ids = [a.get("id") for a in assertions]
    require(len(set(assertion_ids)) == len(assertion_ids), "duplicate assertion")
    for a in assertions:
        require(isinstance(a.get("id"), str) and a["id"].startswith("as:tas001:"), "nonlocal assertion")
        require(isinstance(a.get("predicate"), str) and re.fullmatch(r"[A-Z_]{8,80}", a["predicate"]),
                "invalid predicate")
        require(isinstance(a.get("proposition"), str) and len(a["proposition"]) >= 40, "missing original assertion")
        buckets = []
        for field in ("support_evidence_ids", "neutral_evidence_ids", "counterevidence_ids"):
            ids = a.get(field)
            require(isinstance(ids, list), f"missing evidence class: {field}")
            require(set(ids) <= set(evid_ids), "foreign or fabricated evidence link")
            buckets.extend(ids)
        require(a["support_evidence_ids"] and len(set(buckets)) == len(buckets), "missing support or double-counted evidence")
        require(isinstance(a.get("falsifier"), str) and len(a["falsifier"]) >= 40, "missing adversarial falsifier")
    forbidden = ("image_url", "image_path", "copyright_passage", "transcript_text", "accepted_briefing")
    serialized = json.dumps(data)
    for token in forbidden:
        require(f'"{token}"' not in serialized, f"forbidden release field: {token}")
    return len(entities), len(evidence), len(assertions)


if __name__ == "__main__":
    counts = validate(json.loads(RECORDS.read_text(encoding="utf-8")))
    print(f"TAS_DERIVATIVE_PROPOSAL_OK: {counts[0]} local entities, {counts[1]} evidence, {counts[2]} assertions; 0 admitted")
