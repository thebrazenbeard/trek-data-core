"""Strict VOY S1 source-relative publisher-guide validation; zero admission."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
RECORDS_SHA = "ab0031ae6e6dd64402d64bd667ddad61c34e864bcf7055bcad220d9d7c06abb5"
NORMALIZED_SHA = "7bef657a899ca288a86e7f5dc6e310784b33ffbc46e04b78d2fa412a7f0e2f80"
RAW_SHA = "1c079a6bfd707c9252a576d71884344ce6fab0ef8cb963c90a8ffc6df47bbdbf"
PARAPHRASE_SHAS = [
    "0d8d9bd42f4b8134e75764f95633995f95aee34d73e6f1f0fa42aeadd1f96f90",
    "8d3922b68e98b6b0cec13fc82c9ef862731084638ceeabefb29c5962860dcbf9",
    "f68de5527ddc1b5f50bf3a03e64ec66812406018c5b87022729fa1f3934acf0b",
    "bd1f57bc7df7bd4ffafbf7130becba5c29cbc92e5adb84bd86fd7ed5b82881a1",
    "da168c9b0304fd05464ad2d327162901bda8055f4763717aeaf04b616a7eb726",
]
EXPECTED = [
    (7, "Eye Of The Needle", 228, "16a7a5027e316987f9b97a8b8fd6669905f63c62922509c323e9384689cfe27a", "/shows/video/t7wLoDpWS_d40TGqJjfZTLNeGL57wRo_/", "1995-02-20T17:00:00-08:00", 1703, 1721),
    (8, "Ex Post Facto", 295, "ed1f20d85a6923980cd61d17389bf494122cb441d57d5a2b6410a05ec7dc8ca9", "/shows/video/I_FyNlKxfo6VepIb8GqyJterhl803s53/", "1995-02-27T17:00:00-08:00", 1731, 1749),
    (9, "Emanations", 268, "fb2d422ac834ce8f8ec16cddb5cb0ff4fc282535042f9bd61a8f6f0d5f420413", "/shows/video/jlNtWPx19RZ6fefERgUImN288gPs3R5d/", "1995-03-13T17:00:00-08:00", 1759, 1777),
    (10, "Prime Factors", 287, "a2edab2366531da64beca8da9cac0434a24d6033bea0c118aaef29331d80eb00", "/shows/video/il7VjsVIcD9hyWIhvFPqUTg2QbAJZMhj/", "1995-03-20T17:00:00-08:00", 1787, 1805),
    (11, "State Of Flux", 236, "4b659f8bead1ae52b324c17c51816e27bb53f48a816b1503676111e7dd54d4b9", "/shows/video/4g6HGQR37ow_uHF05ZaoED8f2I86MDTP/", "1995-04-10T17:00:00-07:00", 1815, 1833),
]
CLAIM_MODES = [
    "PUBLISHER_CONTACT_APPEARS_WILLING_NOT_VERIFIED",
    "PUBLISHER_ACCUSATION_AND_INVESTIGATION_NOT_AV_READ",
    "PUBLISHER_EXPLICITLY_CONTESTS_AFTERLIFE_EXPLANATION",
    "PUBLISHER_NONINTERFERENCE_AND_UNRESOLVED_CHOICE",
    "PUBLISHER_ALLEGED_INFILTRATOR_NOT_INDEPENDENTLY_CONFIRMED",
]
FIELD_SETS = {
    "packet": "schema_version batch_id role status accepted_main_baseline accepted_source_binding_effect accepted_work_effect coverage_effect denominator_effect reconciliation_effect explorer_publication_effect episode_content_watched transcripts_read media_bytes_fetched source publisher_guide_card_count publisher_guide_card_ordinals publisher_guide_badges pilot_representation selected_guide_card_ordinals selected_publisher_badges source_relative_descriptions_read original_analyses_proposed selected_description_chars cards local_entities source_relative_evidence typed_assertions held_description_partition holds".split(),
    "source": "local_source_id publisher url locale source_kind independence_group http_status retrieval_date_header observed_at_utc response_bytes response_sha256 normalized_15_card_sha256 source_html_committed retrieval_mutable reproducible_extractor".split(),
    "pilot": "source_local_first_card_title first_card_guide_ordinal first_card_publisher_episode_badge second_card_guide_ordinal second_card_publisher_episode_badge cross_locale_discrepancy canonical_two_part_episode_identity".split(),
    "card": "guide_order publisher_analytics_ordinal season_badge episode_badge display_title video_route_path publisher_datetime html_anchor_line html_description_line description_chars description_sha256".split(),
    "entity": "id guide_order publisher_episode_badge kind canonical_work_id".split(),
    "evidence": "id source_id local_entity_id kind locator description_sha256 original_paraphrase claim_mode".split(),
    "assertion": "id predicate evidence_id status".split(),
    "partition": "publisher_cards_discovered first_party_descriptions_actually_read publisher_descriptions_not_yet_processed audiovisual_episodes_close_read status".split(),
}


def require(condition: bool, why: str) -> None:
    if not condition:
        raise ValueError(why)


def keys(obj: dict, kind: str) -> None:
    require(type(obj) is dict and set(obj) == set(FIELD_SETS[kind]), kind + " unreviewed/missing fields")


def validate(packet: dict) -> None:
    keys(packet, "packet")
    require(packet["schema_version"] == "1.0.0" and packet["batch_id"] == "VOY.PPLUS.ENUS.S1.SECOND5.GUIDE.20261105", "batch identity")
    require(packet["role"] == "VOY" and packet["status"] == "HELD_OFFICIAL_US_PUBLISHER_GUIDE_SOURCE_RELATIVE", "role/status")
    require(packet["accepted_main_baseline"] == "3028765359001b90bc3e6b5c1835ee283b326e91", "accepted main baseline")
    for effect in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "reconciliation_effect", "explorer_publication_effect"):
        require(packet[effect] == "NONE", "protected effect " + effect)
    for flag in ("episode_content_watched", "transcripts_read", "media_bytes_fetched"):
        require(packet[flag] is False, "unearned source use " + flag)
    src = packet["source"]
    keys(src, "source")
    require(src == {
        "local_source_id": "voy-s1-enus-pplus-html-secondfive-20261105",
        "publisher": "Paramount+",
        "url": "https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/",
        "locale": "en-US",
        "source_kind": "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML",
        "independence_group": "publisher:paramountplus.com",
        "http_status": 200,
        "retrieval_date_header": None,
        "observed_at_utc": "2026-11-05 UTC (day-level, exact retrieval timestamp unavailable)",
        "response_bytes": 292338,
        "response_sha256": RAW_SHA,
        "normalized_15_card_sha256": NORMALIZED_SHA,
        "source_html_committed": False,
        "retrieval_mutable": True,
        "reproducible_extractor": "source_probe.py",
    }, "exact official US response snapshot/lineage")
    require(type(packet["publisher_guide_card_count"]) is int and packet["publisher_guide_card_count"] == 15, "15 observed US publisher cards")
    require(packet["publisher_guide_card_ordinals"] == "CONTIGUOUS_1_TO_15" and packet["publisher_guide_badges"] == "BADGE_1_THEN_3_TO_16", "guide ordinals/badges")
    keys(packet["pilot_representation"], "pilot")
    require(packet["pilot_representation"] == {
        "source_local_first_card_title": "Caretaker, Part 1 & 2",
        "first_card_guide_ordinal": 1,
        "first_card_publisher_episode_badge": 1,
        "second_card_guide_ordinal": 2,
        "second_card_publisher_episode_badge": 3,
        "cross_locale_discrepancy": "GERMAN_PAGE_REPORTS_SEPARATE_PILOT_CARDS_HELD_UNRECONCILED",
        "canonical_two_part_episode_identity": "UNRESOLVED",
    }, "US composite pilot and unresolved German-locale card identity")
    require(packet["selected_guide_card_ordinals"] == [6,7,8,9,10] and packet["selected_publisher_badges"] == [7,8,9,10,11], "source-local ordinals not global Work IDs")
    for name in ("source_relative_descriptions_read", "original_analyses_proposed"):
        require(type(packet[name]) is int and packet[name] == 5, "actually read five descriptions")
    require(type(packet["selected_description_chars"]) is int and packet["selected_description_chars"] == 1314, "observed description characters")
    cards, entities, evidence, assertions = (packet[k] for k in ("cards", "local_entities", "source_relative_evidence", "typed_assertions"))
    require(all(type(v) is list and len(v) == 5 for v in (cards,entities,evidence,assertions)), "five chained local records")
    require(sum(c["description_chars"] for c in cards) == 1314, "full selected source length")
    seen = set()
    for i,(card,ent,ev,claim) in enumerate(zip(cards,entities,evidence,assertions)):
        n = i+6
        badge,title,length,digest,route,dt,anchor_line,copy_line = EXPECTED[i]
        keys(card,"card"); keys(ent,"entity"); keys(ev,"evidence"); keys(claim,"assertion")
        for k in ("guide_order","publisher_analytics_ordinal","season_badge","episode_badge","html_anchor_line","html_description_line","description_chars"):
            require(type(card[k]) is int, "strict source card integer: "+k)
        require(card == {"guide_order":n,"publisher_analytics_ordinal":n,"season_badge":1,"episode_badge":badge,"display_title":title,"video_route_path":route,"publisher_datetime":dt,"html_anchor_line":anchor_line,"html_description_line":copy_line,"description_chars":length,"description_sha256":digest}, "immutable official source-local card tuple")
        require(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/",route)), "publisher video route syntax")
        eid = f"voy-s1-card{n}"
        vid = eid+"-publisher-copy"
        require(ent == {"id":eid,"guide_order":n,"publisher_episode_badge":badge,"kind":"PUBLISHER_GUIDE_CARD","canonical_work_id":None}, "no global identity")
        require(ev["id"] == vid and ev["source_id"] == src["local_source_id"] and ev["local_entity_id"] == eid, "source-relative join")
        require(ev["kind"] == "PUBLISHER_GUIDE_DESCRIPTION" and ev["locator"] == f"source HTML line {copy_line}" and ev["description_sha256"] == digest, "source paragraph locator/hash")
        require(ev["claim_mode"] == CLAIM_MODES[i] and type(ev["original_paraphrase"]) is str and 90 <= len(ev["original_paraphrase"]) <= 230, "publisher-attributed original paraphrase")
        require(hashlib.sha256(ev["original_paraphrase"].encode("utf8")).hexdigest() == PARAPHRASE_SHAS[i], "unreviewed semantic paraphrase change")
        require(hashlib.sha256(ev["original_paraphrase"].encode("utf8")).hexdigest() != digest, "cannot republish original source copy")
        require(claim["id"] == eid+"-description-assertion" and claim["evidence_id"] == vid, "assertion links")
        require(claim["predicate"] == ("PUBLISHER_POSES_CONTESTED_AFTERLIFE" if i==2 else "PUBLISHER_DESCRIBES") and claim["status"] == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED", "epistemic frame/status")
        for row in (ent,ev,claim):
            require(row["id"] not in seen, "duplicate evidence/local entity ID")
            seen.add(row["id"])
    keys(packet["held_description_partition"],"partition")
    require(packet["held_description_partition"] == {"publisher_cards_discovered":15,"first_party_descriptions_actually_read":5,"publisher_descriptions_not_yet_processed":10,"audiovisual_episodes_close_read":0,"status":"HELD_PARTIAL_PUBLISHER_GUIDE_NOT_AV_EPISODE_RESEARCH"}, "honest noncoverage partition")
    require(type(packet["holds"]) is list and len(packet["holds"]) == 6 and all(type(x) is str and len(x) >= 40 for x in packet["holds"]), "hold explanations")


def validate_serialized(raw: bytes) -> None:
    require(hashlib.sha256(raw).hexdigest() == RECORDS_SHA, "exact reviewed research packet bytes changed")
    def no_duplicate_pairs(pairs):
        result = {}
        for key,val in pairs:
            require(key not in result, "duplicate JSON key: "+key)
            result[key] = val
        return result
    validate(json.loads(raw.decode("utf8"), object_pairs_hook=no_duplicate_pairs))


def main() -> int:
    try:
        validate_serialized((HERE/"records.json").read_bytes())
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
        print("FAIL VOY publisher source-relative packet: "+str(exc), file=sys.stderr)
        return 1
    print("PASS VOY S1 second-five source-bound en-US publisher cards; no AV close read/accepted Work/coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
