"""Fail-closed structural validation for one SFA publisher-page observation.

This does not authenticate a publisher snapshot, resolve Work identity, or
grant third-party image rights. It guards the research proposal's scope.
"""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR_ROSTER = ROOT / "proposals/librarian/sfa-publisher-roster-20261102/bundle.json"
FORBIDDEN_KEYS = {"canonical_work_id", "source_binding_id", "image_url", "image_path", "image_binary", "transcript"}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
PHOTO_LABEL = re.compile(r"SFA_200_[A-Z0-9_]+\.(?:jpg|JPG)\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def walk_no_promotion(value):
    if isinstance(value, dict):
        require(not (FORBIDDEN_KEYS & value.keys()), "forbidden Work/image/source promotion field")
        for child in value.values():
            walk_no_promotion(child)
    elif isinstance(value, list):
        for child in value:
            walk_no_promotion(child)


def validate(data, prior_roster):
    require(data.get("schema_version") == "1.0.0", "schema version mismatch")
    require(data.get("batch_id") == "SFA-PRESS-REFRESH-20261103-001", "wrong source batch")
    require(data.get("role") == "SFA" and data.get("status") == "PROPOSAL_ONLY_PUBLISHER_METADATA", "not a research proposal")
    for effect in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect", "public_artwork_release_effect"):
        require(data.get(effect) == "NONE", f"forbidden promotion: {effect}")
    require(data.get("av_content_inspected") is False and data.get("image_bytes_retrieved") is False, "unobserved media claim")
    walk_no_promotion(data)

    sources = data.get("source_snapshots")
    require(isinstance(sources, list) and len(sources) == 2, "expected two bounded publisher page snapshots")
    ids = set()
    for source in sources:
        ident = source.get("source_id")
        require(isinstance(ident, str) and ident not in ids, "duplicate source identity")
        ids.add(ident)
        parsed = urlsplit(source.get("url", ""))
        require(parsed.scheme == "https" and parsed.hostname == "www.paramountpressexpress.com" and not parsed.username and not parsed.query and not parsed.fragment, "source URL is not the exact public publisher page")
        require(source.get("independence_group") == "publisher:paramount", "one publisher cannot become independent witnesses")
        require(source.get("http_status") == 200 and source.get("content_type") == "text/html; charset=UTF-8", "unverified HTTP receipt")
        require(isinstance(source.get("raw_response_bytes"), int) and source["raw_response_bytes"] > 10000, "missing response byte receipt")
        require(isinstance(source.get("raw_response_sha256"), str) and SHA256.fullmatch(source["raw_response_sha256"]), "malformed response digest")
        require(source.get("snapshot_bytes_public") is False, "unapproved HTML release")
        require(source.get("observed_after_retrieval_utc") == "2026-11-03T01:23:34Z", "source observation date missing or altered")
    require({s["source_id"] for s in sources} == {"sfa-paramount-press-episodes-20261103", "sfa-cbs-studios-show-20261103"}, "source identity changed")
    require(len({s["raw_response_sha256"] for s in sources}) == 2, "distinct page receipt collision")

    entities = data.get("local_entities")
    require(isinstance(entities, list) and len(entities) == 12, "expected ten publisher slots and two media buckets")
    entity_ids = [e.get("id") for e in entities]
    require(all(isinstance(v, str) for v in entity_ids) and len(set(entity_ids)) == len(entity_ids), "duplicate local entities")
    slots = [e for e in entities if e.get("kind") == "PUBLISHER_EPISODE_SLOT_REFERENCE"]
    media = [e for e in entities if e.get("kind") == "PUBLISHER_MEDIA_BUCKET"]
    require(len(slots) == 10 and len(media) == 2, "unsupported media/episode promotion")
    require(all(e.get("season_label") == 1 and isinstance(e.get("raw_html_line"), int) and e["raw_html_line"] > 0 for e in slots), "season or line mismatch")
    codes = [e.get("publisher_episode_code") for e in slots]
    require(codes == [str(i) for i in range(101, 111)], "publisher code gap or duplication")

    old_slots = prior_roster.get("episode_slots")
    require(isinstance(old_slots, list) and len(old_slots) == 10, "historical roster shape changed")
    for i, (new, old) in enumerate(zip(slots, old_slots), start=1):
        require(old["season"] == 1 and old["episode_number"] == i, "baseline publisher slot ordering changed")
        require(new.get("title") == old["title"], "current observation does not match baseline title")
        require(new.get("id") == f"sfa-press-20261103-slot-{i:02d}", "source-local identity changed")
    media_by_id = {e["id"]: e for e in media}
    require(set(media_by_id) == {"sfa-press-20261103-s2-promotional", "sfa-press-20261103-s1-promotional"}, "publisher media-bucket identities changed")
    require(media_by_id["sfa-press-20261103-s2-promotional"]["publisher_episode_code"] == "200", "S2 publisher bucket code changed")
    require(media_by_id["sfa-press-20261103-s2-promotional"]["season_label"] == 2, "S2 bucket season changed")
    require(media_by_id["sfa-press-20261103-s2-promotional"]["title"] == "Season 2 - Early Release", "S2 bucket label changed")
    require(media_by_id["sfa-press-20261103-s1-promotional"]["publisher_episode_code"] == "Multiple", "S1 media bucket code changed")
    require(media_by_id["sfa-press-20261103-s1-promotional"]["title"] == "Early Release Images", "S1 media bucket label changed")

    evidence = data.get("evidence")
    require(isinstance(evidence, list) and len(evidence) == 4, "missing or invented evidence groups")
    evidence_ids = {e.get("id") for e in evidence}
    require(len(evidence_ids) == 4, "duplicate evidence IDs")
    for item in evidence:
        if item.get("kind") == "PUBLISHER_PHOTO_FILENAME_AND_CAPTION_LISTING":
            require(item.get("source_id") == "sfa-cbs-studios-show-20261103", "photo evidence lacks its source")
            require(item.get("photo_metadata_ids") == ["sfa-cbs-photo-200-01", "sfa-cbs-photo-200-02", "sfa-cbs-photo-200-03"], "photo evidence lacks exact local metadata IDs")
        else:
            require(item.get("source_id") == "sfa-paramount-press-episodes-20261103", "evidence lacks official publisher-page source")
            require(item.get("local_entity_ids") and set(item["local_entity_ids"]) <= set(entity_ids), "evidence has missing local entities")
            require(item.get("kind") in {"PUBLISHER_PAGE_TITLE_AND_CODE_OBSERVATION", "PUBLISHER_PAGE_MEDIA_LISTING"}, "invented scene evidence")
        require("HTML lines" in item.get("locator", ""), "unlocated evidence")

    photos = data.get("photo_metadata_observations")
    require(isinstance(photos, list) and len(photos) == 3, "unexpected photo metadata set")
    require(len({p.get("id") for p in photos}) == 3, "duplicate photo metadata ID")
    for photo in photos:
        require(photo.get("source_id") == "sfa-cbs-studios-show-20261103", "unproven photo source")
        require(isinstance(photo.get("file_label"), str) and PHOTO_LABEL.fullmatch(photo["file_label"]), "invalid publisher photo file label")
        require(isinstance(photo.get("raw_html_line"), int) and photo["raw_html_line"] > 0, "unlocated photo filename")
        require(photo.get("rights_status") == "UNRESOLVED" and photo.get("image_bytes_retrieved") is False, "photo rights claim or binary promotion")
        require(isinstance(photo.get("caption_subjects"), list) and photo["caption_subjects"] and all(isinstance(v, str) and v for v in photo["caption_subjects"]), "missing source-local caption subjects")

    assertions = data.get("assertions")
    require(isinstance(assertions, list) and len(assertions) == 3, "missing assertions")
    require(len({a.get("id") for a in assertions}) == 3, "duplicate assertions")
    for assertion in assertions:
        require(assertion.get("status") in {"SOURCE_LOCAL_OBSERVATION", "UNRESOLVED"}, "assertion is overpromoted")
        require(assertion.get("predicate") and assertion.get("scope"), "unscoped assertion")
        require(assertion.get("support_evidence_ids") and set(assertion["support_evidence_ids"]) <= evidence_ids, "unsupported assertion")
    require(any(a.get("id") == "sfa-press-assert-s2-classification-hold" and a.get("status") == "UNRESOLVED" for a in assertions), "S2 metadata-identity hold removed")
    return len(slots), len(media), len(photos)


def main():
    record = json.loads((HERE / "records.json").read_text(encoding="utf-8"))
    prior = json.loads(PRIOR_ROSTER.read_text(encoding="utf-8"))
    slots, holds, photos = validate(record, prior)
    print(f"SFA_SOURCE_REFRESH_PASS: {slots} publisher slots, {holds} media-bucket holds, {photos} unreleased photo metadata observations; 0 admitted Works")


if __name__ == "__main__":
    main()
