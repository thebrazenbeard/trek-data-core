"""Fail-closed source-relative ENT S1 first-five publisher-guide validation."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
SOURCE_SHA = "e4c46b3b56ecaf2bc20ac562b69e94be7fbc9321ade1939e080ccaefc0d543f4"
NORMALIZED_SHA = "a6ca94bbdfbe7a32e304e3bc9c0f4ce516e639f9d8f505af97fb82b92df8a9c4"
RECORDS_SHA = "e6b1b49ad21151dc25c1307b305ca28dd8a2bac015d26d794731b02298c98439"
PARAPHRASE_SHAS = [
    "27db66f4450700275dabb6e495393c7cc944a83ea31e1b381dc7077b3c77af1c",
    "88b8206bbe77b0ce6a79ccbecbf9cc50d5424d02f3fa693c4014deeff0311e25",
    "99c0ffe4a4a23a4afa5ccda2cd890ba388b5fdc95fc63a05cefe5c1c7d2de685",
    "4448442feaa79539748f9a3f9837b29bc7ee2722a83e38a08864c825885d8bf5",
    "111bf41cb23d2ceb51b2fe901808d07b4e376f8a0a3282a5afe9b8b50aeb967c",
]
EXPECTED = [
    (1, "Broken Bow - Part 1 and 2", 230, "f9cdbebc04c72787fb2d4fbd27a18b7328f560a67e48f95360c0842a439bcd04"),
    (3, "Fight or Flight", 200, "13e04b4fee6e130a6e24d101a6f6867ea7f718bbdf1d971db04f66ee3e7ef113"),
    (4, "Strange New World", 209, "cacf492e4be677014615a61dbbd655e64112ba3b2372a20129ab04587f2ff101"),
    (5, "Unexpected", 165, "21e7fe97c79abfb50c4e6f7d08214ab1b480d559f2c7b0280eab38ca88c5f8ea"),
    (6, "Terra Nova", 208, "2ee93b94196b39c376dc5d6259bbb34dd76cf2947833837b5205af30c8448832"),
]
ROUTES = [
    "/shows/video/vDnTX2qyJMb41JRFGjBNY2SmJKplW9uD/",
    "/shows/video/1476847392/",
    "/shows/video/1476847956/",
    "/shows/video/1476848062/",
    "/shows/video/1477078878/",
]
SOURCE_DATES = [
    "2001-09-25T21:00:00-07:00", "2001-10-02T21:00:00-07:00",
    "2001-10-09T21:00:00-07:00", "2001-10-16T21:00:00-07:00",
    "2001-10-23T21:00:00-07:00",
]
CLAIMS = [
    "PUBLISHER_MISSION_SETUP_NOT_COMPLETION_VERIFIED",
    "PUBLISHER_ETHICAL_DILEMMA_NOT_OUTCOME_VERIFIED",
    "HALLUCINATORY_FRAME_NOT_OBJECTIVE_DANGER_CONFIRMED",
    "PUBLISHER_BIOLOGICAL_EVENT_NOT_INDEPENDENTLY_VERIFIED",
    "PUBLISHER_COLONY_DESCENDANT_FRAME_NOT_EVOLUTION_VERIFIED",
]
EFFECTS = ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect")
FIELDS = {
    "packet": "schema_version batch_id role status accepted_main_baseline accepted_source_binding_effect accepted_work_effect coverage_effect denominator_effect reconciliation_effect explorer_synopsis_release_effect episode_content_watched transcripts_read image_bytes_fetched source observed_publisher_guide_card_count pilot_structure selected_guide_card_ordinals selected_publisher_episode_badges five_source_descriptions_inspected five_original_analyses_proposed five_publisher_description_chars first_five_guide_cards local_entities source_relative_evidence typed_assertions held_description_partition holds".split(),
    "source": "local_source_id url publisher independence_group source_kind response_http_status response_date_header observed_at_utc raw_response_bytes raw_response_sha256 all_25_cards_fingerprint_sha256 raw_html_committed snapshot_mutable reproducible_extractor".split(),
    "pilot": "first_guide_card_title first_guide_card_display_order first_guide_card_episode_badge second_guide_card_display_order second_guide_card_episode_badge publisher_analytics_card_ordinals publisher_episode_badges two_part_pilot_global_episode_count".split(),
    "card": "display_order analytics_ordinal season episode_badge title video_route_path publisher_datetime html_anchor_line html_description_line description_chars description_sha256".split(),
    "entity": "id guide_card_ordinal publisher_episode_badge kind canonical_work_id".split(),
    "evidence": "id source_id local_entity_id kind locator publisher_description_sha256 original_paraphrase claim_mode".split(),
    "assertion": "id predicate evidence_id status frame_claim_status".split(),
    "partition": "publisher_cards_seen source_relative_descriptions_read remaining_unprocessed_card_descriptions accepted_episode_close_reads status".split(),
}


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def exact_fields(row: dict, kind: str) -> None:
    require(isinstance(row, dict) and set(row) == set(FIELDS[kind]), f"{kind} unreviewed or missing keys")


def read_json(path: Path) -> dict:
    def reject_duplicate_keys(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError("duplicate key: " + k)
            out[k] = v
        return out
    return json.loads(path.read_text(encoding="utf8"), object_pairs_hook=reject_duplicate_keys)


def validate(packet: dict) -> None:
    exact_fields(packet, "packet")
    require(packet["schema_version"] == "1.0.0" and packet["batch_id"] == "ENT.PPLUS.S1.FIRST5.GUIDE.20261104", "batch identity")
    require(packet["role"] == "ENT" and packet["status"] == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "role/status")
    require(packet["accepted_main_baseline"] == "3028765359001b90bc3e6b5c1835ee283b326e91", "accepted main anchor")
    for name in EFFECTS:
        require(packet[name] == "NONE", "protected effect: " + name)
    for name in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
        require(packet[name] is False, "unearned media read: " + name)
    src = packet["source"]
    exact_fields(src, "source")
    require(src["local_source_id"] == "ent-s1-paramountplus-guide-html-first5-20261104", "source local ID")
    require(src["url"] == "https://www.paramountplus.com/shows/enterprise/episodes/1/", "source official URL")
    require(src["publisher"] == "Paramount+" and src["source_kind"] == "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML", "source class")
    require(src["independence_group"] == "publisher:paramountplus.com", "one original publisher lineage")
    require(type(src["response_http_status"]) is int and src["response_http_status"] == 200, "source response HTTP")
    require(type(src["raw_response_bytes"]) is int and src["raw_response_bytes"] == 311889, "full source byte count")
    require(src["raw_response_sha256"] == SOURCE_SHA and src["all_25_cards_fingerprint_sha256"] == NORMALIZED_SHA, "source full/normalized SHA")
    require(src["response_date_header"] == "Wed, 04 Nov 2026 23:58:50 GMT" and src["observed_at_utc"] == "2026-11-04T23:58:50.902109+00:00", "source snapshot timestamp")
    require(src["raw_html_committed"] is False and src["snapshot_mutable"] is True and src["reproducible_extractor"] == "source_probe.py", "no raw source bytes")
    require(type(packet["observed_publisher_guide_card_count"]) is int and packet["observed_publisher_guide_card_count"] == 25, "25 publisher cards not 26 episodes")
    exact_fields(packet["pilot_structure"], "pilot")
    require(packet["pilot_structure"] == {
        "first_guide_card_title": "Broken Bow - Part 1 and 2",
        "first_guide_card_display_order": 1,
        "first_guide_card_episode_badge": 1,
        "second_guide_card_display_order": 2,
        "second_guide_card_episode_badge": 3,
        "publisher_analytics_card_ordinals": "CONTIGUOUS_1_TO_25",
        "publisher_episode_badges": "BADGE_1_THEN_3_TO_26",
        "two_part_pilot_global_episode_count": "UNRESOLVED_NOT_WORK_RECONCILED",
    }, "pilot is one guide card; identity unresolved")
    require(packet["selected_guide_card_ordinals"] == [1, 2, 3, 4, 5], "publisher guide-card ordinals")
    require(packet["selected_publisher_episode_badges"] == [1, 3, 4, 5, 6], "source-local badges distinct from display")
    for name in ("five_source_descriptions_inspected", "five_original_analyses_proposed"):
        require(type(packet[name]) is int and packet[name] == 5, "five actually read descriptions: " + name)
    require(type(packet["five_publisher_description_chars"]) is int and packet["five_publisher_description_chars"] == 1012, "actual first-five description length")
    cards, entities, evidence, claims = (packet[n] for n in ("first_five_guide_cards", "local_entities", "source_relative_evidence", "typed_assertions"))
    require(all(isinstance(x, list) and len(x) == 5 for x in (cards, entities, evidence, claims)), "exact five chains")
    require(sum(c["description_chars"] for c in cards) == 1012, "source paragraph lengths sum")
    ids = set()
    for i, (card, ent, ev, assertion) in enumerate(zip(cards, entities, evidence, claims)):
        n = i + 1
        badge, title, length, digest = EXPECTED[i]
        exact_fields(card, "card")
        exact_fields(ent, "entity")
        exact_fields(ev, "evidence")
        exact_fields(assertion, "assertion")
        for field in ("display_order", "analytics_ordinal", "season", "episode_badge", "html_anchor_line", "html_description_line", "description_chars"):
            require(type(card[field]) is int, "strict card integer " + field)
        require(card["display_order"] == card["analytics_ordinal"] == n and card["season"] == 1 and card["episode_badge"] == badge, "ordinal vs episode badge")
        require(card["title"] == title and card["description_chars"] == length and card["description_sha256"] == digest, "exact official source metadata")
        require(card["html_anchor_line"] == 1482 + (n - 1) * 28 and card["html_description_line"] == 1500 + (n - 1) * 28, "line locator")
        require(card["video_route_path"] == ROUTES[i] and bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/", card["video_route_path"])), "exact publisher video route metadata only")
        require(card["publisher_datetime"] == SOURCE_DATES[i], "exact source-local datetime without canonical airdate inference")
        entity_id = f"ent-s1-card{n:02d}"
        evidence_id = f"{entity_id}-guide-description"
        require(ent["id"] == entity_id and type(ent["guide_card_ordinal"]) is int and ent["guide_card_ordinal"] == n and type(ent["publisher_episode_badge"]) is int and ent["publisher_episode_badge"] == badge, "local entity")
        require(ent["kind"] == "PUBLISHER_EPISODE_CARD" and ent["canonical_work_id"] is None, "no global work identity")
        require(ev["id"] == evidence_id and ev["source_id"] == src["local_source_id"] and ev["local_entity_id"] == entity_id, "source-relative evidence binding")
        require(ev["kind"] == "PUBLISHER_GUIDE_DESCRIPTION" and ev["publisher_description_sha256"] == digest and str(card["html_description_line"]) in ev["locator"], "paragraph fingerprint/locator")
        require(ev["claim_mode"] == CLAIMS[i] and isinstance(ev["original_paraphrase"], str) and 65 <= len(ev["original_paraphrase"]) <= 240, "original summary and epistemic frame")
        require(hashlib.sha256(ev["original_paraphrase"].encode("utf8")).hexdigest() == PARAPHRASE_SHAS[i], "unreviewed source-relative paraphrase drift")
        require(hashlib.sha256(ev["original_paraphrase"].encode()).hexdigest() != digest, "never paste source prose unchanged")
        require(assertion["id"] == f"{entity_id}-publisher-describes" and assertion["evidence_id"] == evidence_id, "assertion link")
        require(assertion["predicate"] == "PUBLISHER_DESCRIBES" and assertion["status"] == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED" and assertion["frame_claim_status"] == "PUBLISHER_DESCRIPTION_ONLY", "not objective narrative claim")
        for row in (ent, ev, assertion):
            require(row["id"] not in ids, "duplicate local IDs")
            ids.add(row["id"])
    exact_fields(packet["held_description_partition"], "partition")
    require(packet["held_description_partition"] == {
        "publisher_cards_seen": 25,
        "source_relative_descriptions_read": 5,
        "remaining_unprocessed_card_descriptions": 20,
        "accepted_episode_close_reads": 0,
        "status": "HELD_PARTIAL_PUBLISHER_GUIDE_NOT_EPISODE_CLOSE_READ",
    }, "held noncoverage arithmetic")
    require(isinstance(packet["holds"], list) and len(packet["holds"]) >= 7, "explicit pilot, copyright and epistemic holds")


def validate_serialized(raw: bytes) -> None:
    """Gate this exact audited packet, including otherwise unconstrained free text."""
    require(hashlib.sha256(raw).hexdigest() == RECORDS_SHA, "original packet SHA changed; audit required")

    def reject_duplicate_keys(items):
        out = {}
        for key, val in items:
            require(key not in out, "duplicate JSON key: " + key)
            out[key] = val
        return out

    validate(json.loads(raw.decode("utf8"), object_pairs_hook=reject_duplicate_keys))


def main() -> int:
    try:
        validate_serialized((HERE / "records.json").read_bytes())
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print("FAIL ENT S1 publisher first-five: " + str(exc), file=sys.stderr)
        return 1
    print("PASS ENT S1 five source-local description proposals; pilot one guide card/two parts, no accepted coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
