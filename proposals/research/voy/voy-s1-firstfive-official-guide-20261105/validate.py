"""Strict VOY S1 source-relative publisher-guide validation; zero admission."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
RECORDS_SHA = "890fba4f231c566f3f467b045e13cdb5597e014b89e0c515ea8a480215de2942"
NORMALIZED_SHA = "7bef657a899ca288a86e7f5dc6e310784b33ffbc46e04b78d2fa412a7f0e2f80"
RAW_SHA = "d13c1985dc71d8ea560378bac946d4fa07cce2c2929556a4ddf8a0dbbc37be69"
PARAPHRASE_SHAS = [
    "7638c170a1185bb3fbffc60409cf048ccd1ec2535c20307c8e80b1825840399d",
    "9e40a481af781280152d3b48823b3ccd25b644ab0f0c59b27493ac919a43a782",
    "087fbd8424cdecb2d7441570fad27d05026de1bd4ea1367626633de0003a71d7",
    "72f0c7985eb79a10fa048ab1e7c232d4551488c21dc771c22a3f82675b09a055",
    "d98af78b638c7af83e4d4e724f79ed46b702d821395784918e9efcaa11fa8421",
]
EXPECTED = [
    (1, "Caretaker, Part 1 & 2", 118, "57b973908377c1c03024fe21dc89d7a77cbf2e9878f69e8fa7e278dcbccadbd9", "/shows/video/aNy9fyAsPOdixxFtPMHoEXq9oXGz0eie/", "1995-01-16T17:00:00-08:00", 1563, 1581),
    (3, "Parallax", 195, "0b06b096e7c33ba4e71fa19b7f6d449a9b47d01524cf1fa92558972291dd4eb5", "/shows/video/O0h_DNgC3u8NWNWsX4pvg24W1ZXunJD0/", "1995-01-23T17:00:00-08:00", 1591, 1609),
    (4, "Time And Again", 210, "95dc75ce70bd8a4982646600c137c7b78e4767c05832fc801ce7a8ab92f22d18", "/shows/video/k4NTOMBqi_aHZwfZA7vKZ_ZT1IQY4e5M/", "1995-01-30T17:00:00-08:00", 1619, 1637),
    (5, "Phage", 199, "0114c1006b147afc963c3f79b560fd23906e7dd50062793f02459395e3e9dda6", "/shows/video/MKBk0egktsNccEutB4i8YtD1DUs2bMjX/", "1995-02-06T17:00:00-08:00", 1647, 1665),
    (6, "The Cloud", 204, "5e53c9d6e01751af668c13e338c92cdf8ff06242a40858e1a6c340fde513ed8c", "/shows/video/fBbwrRKZwvIoiwAt_Wh9yLu7FWLQYRmO/", "1995-02-13T17:00:00-08:00", 1675, 1693),
]
CLAIM_MODES = [
    "PUBLISHER_TRUNCATED_SETUP_OUTCOME_UNKNOWN",
    "PUBLISHER_REPORTED_CREW_AND_ROLE_NOT_EPISODE_VERIFIED",
    "PUBLISHER_POSES_CONTESTED_CAUSALITY",
    "PUBLISHER_EVENT_SUMMARY_NOT_AV_READ",
    "PUBLISHER_LIVING_NEBULA_RECAP_NOT_AV_READ",
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
    require(packet["schema_version"] == "1.0.0" and packet["batch_id"] == "VOY.PPLUS.ENUS.S1.FIRST5.GUIDE.20261105", "batch identity")
    require(packet["role"] == "VOY" and packet["status"] == "HELD_OFFICIAL_US_PUBLISHER_GUIDE_SOURCE_RELATIVE", "role/status")
    require(packet["accepted_main_baseline"] == "3028765359001b90bc3e6b5c1835ee283b326e91", "accepted main baseline")
    for effect in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "reconciliation_effect", "explorer_publication_effect"):
        require(packet[effect] == "NONE", "protected effect " + effect)
    for flag in ("episode_content_watched", "transcripts_read", "media_bytes_fetched"):
        require(packet[flag] is False, "unearned source use " + flag)
    src = packet["source"]
    keys(src, "source")
    require(src == {
        "local_source_id": "voy-s1-enus-pplus-html-firstfive-20261105",
        "publisher": "Paramount+",
        "url": "https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/",
        "locale": "en-US",
        "source_kind": "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML",
        "independence_group": "publisher:paramountplus.com",
        "http_status": 200,
        "retrieval_date_header": "Thu, 05 Nov 2026 00:33:30 GMT",
        "observed_at_utc": "2026-11-05T00:33:30.736718+00:00",
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
    require(packet["selected_guide_card_ordinals"] == [1,2,3,4,5] and packet["selected_publisher_badges"] == [1,3,4,5,6], "source-local ordinals not global Work IDs")
    for name in ("source_relative_descriptions_read", "original_analyses_proposed"):
        require(type(packet[name]) is int and packet[name] == 5, "actually read five descriptions")
    require(type(packet["selected_description_chars"]) is int and packet["selected_description_chars"] == 926, "observed description characters")
    cards, entities, evidence, assertions = (packet[k] for k in ("cards", "local_entities", "source_relative_evidence", "typed_assertions"))
    require(all(type(v) is list and len(v) == 5 for v in (cards,entities,evidence,assertions)), "five chained local records")
    require(sum(c["description_chars"] for c in cards) == 926, "full selected source length")
    seen = set()
    for i,(card,ent,ev,claim) in enumerate(zip(cards,entities,evidence,assertions)):
        n = i+1
        badge,title,length,digest,route,dt,anchor_line,copy_line = EXPECTED[i]
        keys(card,"card"); keys(ent,"entity"); keys(ev,"evidence"); keys(claim,"assertion")
        for k in ("guide_order","publisher_analytics_ordinal","season_badge","episode_badge","html_anchor_line","html_description_line","description_chars"):
            require(type(card[k]) is int, "strict source card integer: "+k)
        require(card == {"guide_order":n,"publisher_analytics_ordinal":n,"season_badge":1,"episode_badge":badge,"display_title":title,"video_route_path":route,"publisher_datetime":dt,"html_anchor_line":anchor_line,"html_description_line":copy_line,"description_chars":length,"description_sha256":digest}, "immutable official source-local card tuple")
        require(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/",route)), "publisher video route syntax")
        eid = f"voy-s1-card{n:02d}"
        vid = eid+"-publisher-copy"
        require(ent == {"id":eid,"guide_order":n,"publisher_episode_badge":badge,"kind":"PUBLISHER_GUIDE_CARD","canonical_work_id":None}, "no global identity")
        require(ev["id"] == vid and ev["source_id"] == src["local_source_id"] and ev["local_entity_id"] == eid, "source-relative join")
        require(ev["kind"] == "PUBLISHER_GUIDE_DESCRIPTION" and ev["locator"] == f"source HTML line {copy_line}" and ev["description_sha256"] == digest, "source paragraph locator/hash")
        require(ev["claim_mode"] == CLAIM_MODES[i] and type(ev["original_paraphrase"]) is str and 90 <= len(ev["original_paraphrase"]) <= 230, "publisher-attributed original paraphrase")
        require(hashlib.sha256(ev["original_paraphrase"].encode("utf8")).hexdigest() == PARAPHRASE_SHAS[i], "unreviewed semantic paraphrase change")
        require(hashlib.sha256(ev["original_paraphrase"].encode("utf8")).hexdigest() != digest, "cannot republish original source copy")
        require(claim["id"] == eid+"-description-assertion" and claim["evidence_id"] == vid, "assertion links")
        require(claim["predicate"] == ("PUBLISHER_DESCRIBES_CONTESTED_CAUSALITY" if i==2 else "PUBLISHER_DESCRIBES") and claim["status"] == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED", "epistemic frame/status")
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
    print("PASS VOY S1 five source-bound en-US publisher cards; no AV close read/accepted Work/coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
