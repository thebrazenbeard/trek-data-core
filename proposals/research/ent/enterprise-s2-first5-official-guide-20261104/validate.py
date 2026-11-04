"""Fail-closed Enterprise S2 publisher-guide description research validation."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
DISCOVERY=ROOT / "proposals/discovery/legacy-paramount-season2-20261102/ent/bundle.json"
DISCOVERY_SHA="b3ba6c175202d0bd55b711a850a939af6aee2786d0900bc1365cbd109086ef84"
SOURCE_SHA="860df3bd8d3c3e91727ab71c712cd60718da0bddf63fcd5bd5914b83358d9cdd"
TITLES=["Shockwave Part II","Carbon Creek","Minefield","Dead Stop","A Night in Sickbay"]
HASHES=[
    "002d314336f29209603e9dc4ff30820ff37ccc87bc9d393460aa1412b9d6970e",
    "8cd473070d262c6a33a51eec0ea7d83be938dd82a414b4daa415b33fa0e8b4de",
    "df06736f37dd8fafdff4f0a57d9f6cdb0c1f566e39ef5462ab261a3e87896c4c",
    "5dd65d877019abd6af5d949684675f3db1e2bd5b49b1fba54787940fd3bbb563",
    "35a16decfa3813aaa532b342574231ede51a5d4a0c162d924eb22aad0abdeedc",
]
EFFECTS=("accepted_source_binding_effect","accepted_work_effect","coverage_effect","denominator_effect","reconciliation_effect","explorer_synopsis_release_effect")


def check(value:bool,message:str)->None:
    if not value:
        raise ValueError(message)


def read_json(path:Path)->dict:
    def no_duplicates(pairs):
        result={}
        for key,value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key: "+key)
            result[key]=value
        return result
    return json.loads(path.read_text(encoding="utf8"),object_pairs_hook=no_duplicates)


def validate(packet:dict,discovery:dict,discovery_sha:str)->None:
    check(discovery_sha==DISCOVERY_SHA,"accepted discovery pinned source-byte SHA")
    check(discovery.get("batch_id")=="PARAMOUNT-S2-20261102-ENT" and discovery.get("proposal_status")=="CANDIDATE_METADATA_ONLY","discovery is candidates only")
    check(type(discovery.get("listed_slot_count")) is int and discovery["listed_slot_count"]==26,"accepted S2 discovery 26 candidate cards")
    for effect in ("accepted_source_binding_effect","accepted_work_effect","coverage_effect","denominator_effect"):
        check(discovery.get(effect)=="NONE","discovery no protected effect "+effect)
    check(packet.get("batch_id")=="ENT.PPLUS.S2.FIRST5.GUIDE.20261104" and packet.get("schema_version")=="1.0.0","batch identity")
    check(packet.get("role")=="ENT" and packet.get("status")=="HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE","HELD ENT scope")
    check(packet.get("accepted_main_baseline")=="3028765359001b90bc3e6b5c1835ee283b326e91","exact accepted main baseline")
    check(packet.get("accepted_discovery_context")=={
        "path":str(DISCOVERY.relative_to(ROOT)),"sha256":DISCOVERY_SHA,
        "batch_id":"PARAMOUNT-S2-20261102-ENT","proposal_status":"CANDIDATE_METADATA_ONLY",
        "listed_slot_count":26,"meaning":"Accepted main contains discovery candidates only, not 26 admitted episode Works or 26 read descriptions.",
    },"discovery context does not promote Works")
    for effect in EFFECTS:
        check(packet.get(effect)=="NONE","unearned protected effect "+effect)
    for flag in ("episode_content_watched","transcripts_read","image_bytes_fetched"):
        check(packet.get(flag) is False,"unearned source read "+flag)
    source=packet.get("source",{})
    check(source.get("local_source_id")=="ent-s2-paramountplus-guide-html-first5-20261104","source local identifier")
    check(source.get("url")=="https://www.paramountplus.com/shows/enterprise/episodes/2/"==discovery["observation"]["primary_locator"],"first-party URL")
    check(source.get("source_kind")=="FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML" and source.get("publisher")=="Paramount+","publisher source class")
    check(source.get("independence_group")=="publisher:paramountplus.com","single publisher lineage")
    check(type(source.get("response_http_status")) is int and source["response_http_status"]==200,"HTTP 200")
    check(type(source.get("raw_response_bytes")) is int and source["raw_response_bytes"]==312754,"entire HTML response byte count")
    check(source.get("raw_response_sha256")==SOURCE_SHA,"exact first-party HTML source digest")
    check(source.get("response_date_header")=="Wed, 04 Nov 2026 22:48:50 GMT" and source.get("observed_at_utc")=="2026-11-04T22:48:51.067817+00:00","source observation time")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True and source.get("reproducible_extractor")=="source_probe.py","raw copyrighted HTML stays out")
    check(type(packet.get("observed_full_guide_card_count")) is int and packet["observed_full_guide_card_count"]==26,"full guide source traversal")
    full=packet.get("all_26_guide_cards",[])
    check(isinstance(full,list) and len(full)==26,"26 source metadata cards")
    check(len(discovery.get("episode_slots",[]))==26,"26 prior discovery slots")
    for i,(card,discovered) in enumerate(zip(full,discovery["episode_slots"])):
        n=i+1
        for field in ("display_order","season","episode","analytics_ordinal","html_anchor_line","html_description_line","description_chars"):
            check(type(card.get(field)) is int,f"strict integer card E{n} {field}")
        check(card.get("title")==discovered.get("title") and card.get("episode")==discovered.get("episode_number"),f"source/discovery crosswalk E{n}")
        check(type(card.get("display_order")) is int and card["display_order"]==n and type(card.get("analytics_ordinal")) is int and card["analytics_ordinal"]==n,f"source guide ordinal E{n}")
        check(type(card.get("season")) is int and card["season"]==2,"no mixed seasons")
        check(card.get("title_variant_status")=="EXACT_MATCH" and card["analytics_title"]==card["title"]==card["analytics_series_title"],f"publisher source local title triplet E{n}")
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/",card.get("video_route_path",""))),f"route locator metadata E{n}")
        check(type(card.get("html_anchor_line")) is int and card["html_anchor_line"]==1482+28*i,f"anchor line E{n}")
        check(type(card.get("html_description_line")) is int and card["html_description_line"]==1500+28*i,f"publisher description locator E{n}")
        check(type(card.get("description_chars")) is int and card["description_chars"]>0,"source description length")
        check(bool(re.fullmatch(r"[a-f0-9]{64}",card.get("description_sha256",""))),"description fingerprint")
    check(len(set(card["video_route_path"] for card in full))==26,"no route duplication")
    check(packet.get("selected_tranche_episode_ordinals")==[1,2,3,4,5],"five actually processed")
    for k in ("first_five_source_descriptions_inspected","first_five_analytical_synopses_proposed"):
        check(type(packet.get(k)) is int and packet[k]==5,"five actual descriptions "+k)
    cards=packet.get("first_five_guide_cards",[])
    check(isinstance(cards,list) and len(cards)==5,"exact five cards")
    check(type(packet.get("first_five_description_total_chars")) is int and packet["first_five_description_total_chars"]==1184,"source description lengths five")
    check(sum(card["description_chars"] for card in cards)==1184,"five description length sum")
    for i,c in enumerate(cards):
        for field in ("display_order","season","episode","analytics_ordinal","html_anchor_line","html_description_line","description_chars"):
            check(type(c.get(field)) is int,f"strict selected card E{i+1} {field}")
        check(c==full[i] and c["title"]==TITLES[i] and c["description_sha256"]==HASHES[i],f"literal first-party title and paragraph fingerprint E{i+1}")
    expected_anomalies=[
        {"earlier_guide_slot":1,"later_guide_slot":2,"earlier_slot_datetime":cards[0]["publisher_datetime"],"later_slot_datetime":cards[1]["publisher_datetime"],"status":"SOURCE_PUBLISHER_DATETIME_DESCENDS_WITH_ASCENDING_EPISODE_SLOT","air_order_resolution":"UNRESOLVED"},
        {"earlier_guide_slot":4,"later_guide_slot":5,"earlier_slot_datetime":cards[3]["publisher_datetime"],"later_slot_datetime":cards[4]["publisher_datetime"],"status":"SOURCE_PUBLISHER_DATETIME_DESCENDS_WITH_ASCENDING_EPISODE_SLOT","air_order_resolution":"UNRESOLVED"},
    ]
    check(cards[0]["publisher_datetime"]>cards[1]["publisher_datetime"] and cards[3]["publisher_datetime"]>cards[4]["publisher_datetime"],"two source-local datetime inversions actually observed")
    check(packet.get("source_local_publisher_datetime_anomalies")==expected_anomalies,"date inversions not silently reordered")
    entities,evidence,claims=(packet.get(k,[]) for k in ("local_entities","source_relative_evidence","typed_assertions"))
    check(len(entities)==len(evidence)==len(claims)==5,"five linked source relative entity/evidence/assertion chains")
    identifiers=[]
    for i,(ent,ev,claim) in enumerate(zip(entities,evidence,claims)):
        n=i+1
        stem=f"ent-s2-e{n:02d}"
        eid=f"{stem}-publisher-card"
        vid=f"{stem}-guide-description"
        check(ent.get("id")==eid and type(ent.get("source_local_episode_hint")) is int and ent["source_local_episode_hint"]==n,"source local entity E"+str(n))
        check(ent.get("source_kind")=="PUBLISHER_EPISODE_CARD" and ent.get("canonical_work_id") is None,"Work identity unresolved E"+str(n))
        check(ev.get("id")==vid and ev.get("source_id")==source["local_source_id"] and ev.get("local_entity_id")==eid,"source evidence link E"+str(n))
        check(ev.get("kind")=="PUBLISHER_GUIDE_DESCRIPTION" and type(ev.get("card_ordinal")) is int and ev["card_ordinal"]==n,"source evidence kind E"+str(n))
        check(ev.get("publisher_description_sha256")==HASHES[i] and str(cards[i]["html_description_line"]) in ev.get("locator",""),"source description hash/locator E"+str(n))
        text=ev.get("original_paraphrase","")
        check(isinstance(text,str) and 65<=len(text)<=200 and "\n" not in text,"original short synopsis E"+str(n))
        mode="PUBLISHER_REPORT_OF_IN_UNIVERSE_CHARACTER_ACCOUNT" if n==2 else "PUBLISHER_DESCRIPTION_OF_PLOT"
        check(ev.get("claim_mode")==mode,"in-universe utterance evidence separation E"+str(n))
        check(claim.get("id")==f"{stem}-publisher-describes" and claim.get("predicate")=="PUBLISHER_DESCRIBES" and claim.get("evidence_id")==vid,"publisher assertion linkage E"+str(n))
        kind="CHARACTER_REPORTED_ACCOUNT_NOT_OBJECTIVE_EVENT" if n==2 else "PUBLISHER_PLOT_DESCRIPTION_NOT_VIDEO_VERIFIED"
        check(claim.get("status")=="SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED" and claim.get("narrative_claim_kind")==kind,"publisher assertion limitation E"+str(n))
        identifiers.extend([eid,vid,claim["id"]])
    check(len(set(identifiers))==15,"unique source local IDs")
    check(packet.get("held_season_description_partition_summary")=={
        "this_tranche_analyses":5,
        "total_nonoverlapping_source_relative_description_proposals":5,
        "source_local_guide_cards_observed":26,
        "remaining_unprocessed_publisher_descriptions":21,
        "accepted_work_coverage_or_close_read_claims":0,
        "status":"HELD_PARTIAL_PUBLISHER_GUIDE_DESCRIPTIONS_NOT_EPISODE_CONTENT_CLOSE_READ",
    },"no source-card count as watched episode or Work coverage")
    check(len(packet.get("holds",[]))>=7,"research/rights limitations visible")


def main()->int:
    try:
        sha=hashlib.sha256(DISCOVERY.read_bytes()).hexdigest()
        validate(read_json(HERE/"records.json"),read_json(DISCOVERY),sha)
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print("FAIL ENT S2 E01–E05: "+str(exc),file=sys.stderr)
        return 1
    print("PASS ENT S2 first five: five HELD publisher descriptions, 26 observed cards, no Work/CLOSE_READ/coverage")
    return 0


if __name__=="__main__":
    sys.exit(main())
