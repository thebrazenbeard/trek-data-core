"""Strict ENT Season 2 E16–E20 publisher-only provenance and semantic holds."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SIBLING=HERE.parent
PRIOR=[
    ("enterprise-s2-first5-official-guide-20261104","63d7fca810061115e101fd9277f55c039604c49a76eaefa9fc1f1d3a95f8bb94","f835b3142b3998fe602b33823cfadf561f51b2e5","860df3bd8d3c3e91727ab71c712cd60718da0bddf63fcd5bd5914b83358d9cdd","ENT.PPLUS.S2.FIRST5.GUIDE.20261104",list(range(1,6))),
    ("enterprise-s2-second5-official-guide-20261104","2a5c960ed71e7964b283561582127b203ba0e904969caedaf5b3df7faa39f2e2","62535a078f37b1c344b91093fd5fb60e42c5618b","321513d93517b9ea1e50b9ad339352da7dbc38a7564ec1806b4fc4cdc0badc26","ENT.PPLUS.S2.SECOND5.GUIDE.20261104",list(range(6,11))),
    ("enterprise-s2-third5-official-guide-20261104","4eee832f25ce61b8b8531db1cc916c6265a93147a338b679bf2d0cb1536986dc","2393da8cf35835199cd482cfa452723fe063d5da","d2322c72a2069e2813798c9ad497453cc3e7092d75bee30853d129db58a7d84b","ENT.PPLUS.S2.THIRD5.GUIDE.20261104",list(range(11,16))),
]
SOURCE_SHA="c4e8be2b5f387ee4f66f3028d49f979917d69acbaeb5d614dcc7520d79930f01"
TITLES=["Future Tense","Canamar","The Crossing","Judgement","Horizon"]
HASHES=[
    "2dfc93f038711c1c38d73664dba2508f654460f3b2b078d7a0522cd83f487715",
    "67e33c3ed9262014761cbdb762bcb07d6b90751b5d95fad246d78daae02937c8",
    "6932145a418e7fbdddeb05d747adea0bff2f637a73b4098885c48d91e738f459",
    "39151362a85745b857fe721da865667f30250ee5983fd0f9e14783c57985bdea",
    "e09ac73fd3a9de71954df2276a7c37cfedd485b14c7ae2f3fd3607bbbf238508",
]
CLAIM_KINDS={
    16:"APPARENT_HUMAN_CORPSE_NOT_CONFIRMED_DEATH",
    17:"MISTAKEN_ARREST_NOT_PROVEN_GUILT",
    18:"PROPOSED_CONSCIOUSNESS_EXCHANGE_NOT_COMPLETED_TRANSFER_VERIFIED",
    19:"KLINGON_TRIBUNAL_ACCUSATION_NOT_CONSPIRACY_PROVEN",
    20:"PUBLISHER_PLOT_DESCRIPTION_NOT_VIDEO_VERIFIED",
}
PRIOR_SEMANTIC=[
    (2,"CHARACTER_REPORTED_ACCOUNT_NOT_OBJECTIVE_EVENT","T_POL_NARRATED_ACCOUNT"),
    (7,"CHARACTER_MEMORY_EXPERIENCE_NOT_OBJECTIVE_HISTORY","T_POL_MEMORY"),
    (8,"CULTURAL_ACCUSATION_NOT_OBJECTIVE_ESPIONAGE","SPY_ACCUSATION"),
    (10,"CHARACTER_QUESTIONS_IDENTITY_NOT_OBJECTIVE_REPLACEMENT","HOSHI_IDENTITY_QUESTION"),
]
EFFECTS=("accepted_source_binding_effect","accepted_work_effect","coverage_effect","denominator_effect","reconciliation_effect","explorer_synopsis_release_effect")


def check(ok:bool,why:str)->None:
    if not ok:
        raise ValueError(why)


def read_json(path:Path)->dict:
    def no_duplicates(pairs):
        out={}
        for key,value in pairs:
            if key in out:
                raise ValueError("duplicate JSON key "+key)
            out[key]=value
        return out
    return json.loads(path.read_text(encoding="utf8"),object_pairs_hook=no_duplicates)


def validate_prior(predecessors:list[tuple[dict,str]])->None:
    check(len(predecessors)==3,"exact three predecessor batches")
    for i,((record,digest),(folder,expected,commit,raw,batch,ordinals)) in enumerate(zip(predecessors,PRIOR)):
        check(digest==expected,"exact predecessor records SHA "+str(i))
        check(record.get("batch_id")==batch and record.get("status")=="HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE","prior HELD batch "+str(i))
        check(record.get("source",{}).get("raw_response_sha256")==raw,"prior raw first-party source receipt "+str(i))
        check([row.get("source_local_episode_hint") for row in record.get("local_entities",[])]==ordinals,"prior episode scope "+str(i))
        for effect in EFFECTS:
            check(record.get(effect)=="NONE","prior protected effect "+effect)
        path=SIBLING/folder/"validate.py"
        spec=importlib.util.spec_from_file_location(f"ent_s2_fourth_prior_{i}",path)
        check(spec is not None and spec.loader is not None,"prior validator import")
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if i==0:
            discovery_sha=hashlib.sha256(mod.DISCOVERY.read_bytes()).hexdigest()
            mod.validate(record,mod.read_json(mod.DISCOVERY),discovery_sha)
        elif i==1:
            mod.validate(record,predecessors[0][0],predecessors[0][1])
        else:
            mod.validate(record,predecessors[:i])


def validate(packet:dict,predecessors:list[tuple[dict,str]])->None:
    validate_prior(predecessors)
    check(packet.get("schema_version")=="1.0.0" and packet.get("batch_id")=="ENT.PPLUS.S2.FOURTH5.GUIDE.20261104","batch identity")
    check(packet.get("role")=="ENT" and packet.get("status")=="HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE","ENT HELD partition")
    check(packet.get("accepted_main_baseline")=="3028765359001b90bc3e6b5c1835ee283b326e91","accepted main baseline")
    for effect in EFFECTS:
        check(packet.get(effect)=="NONE","no protected effect "+effect)
    for flag in ("episode_content_watched","transcripts_read","image_bytes_fetched"):
        check(packet.get(flag) is False,"unearned source read "+flag)
    check(len(packet.get("prior_batches",[]))==3,"three exact prior receipts")
    seen_ids=set()
    prior_ordinals=[]
    for i,((rec,digest),(folder,expected,commit,raw,batch,scope)) in enumerate(zip(predecessors,PRIOR)):
        ref=packet["prior_batches"][i]
        check(ref=={
            "path":str((SIBLING/folder/"records.json").relative_to(ROOT)),
            "sha256":expected,"commit":commit,
            "source_response_sha256":raw,"episode_scope":[scope[0],scope[-1]],
        },"predecessor exact link "+str(i))
        prior_ordinals.extend(scope)
        for bucket in ("local_entities","source_relative_evidence","typed_assertions"):
            for row in rec[bucket]:
                check(row.get("id") not in seen_ids,"prior ID collision")
                seen_ids.add(row["id"])
    source=packet.get("source",{})
    check(source.get("local_source_id")=="ent-s2-paramountplus-guide-html-fourth5-20261104","local source ID")
    check(source.get("url")=="https://www.paramountplus.com/shows/enterprise/episodes/2/","publisher source URL")
    check(source.get("independence_group")=="publisher:paramountplus.com","same publisher lineage not three witnesses")
    check(source.get("source_kind")=="FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML" and source.get("publisher")=="Paramount+","source kind")
    check(type(source.get("response_http_status")) is int and source["response_http_status"]==200,"HTTP200")
    check(type(source.get("raw_response_bytes")) is int and source["raw_response_bytes"]==312754,"full official HTML bytes")
    check(source.get("raw_response_sha256")==SOURCE_SHA,"live full response SHA")
    check(source.get("response_date_header")=="Wed, 04 Nov 2026 23:11:44 GMT" and source.get("observed_at_utc")=="2026-11-04T23:11:43.808995+00:00","source timestamps")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True and source.get("reproducible_extractor")=="source_probe.py","copyright/private raw source custody")
    for rec,_ in predecessors:
        check(source["url"]==rec["source"]["url"] and source["independence_group"]==rec["source"]["independence_group"],"same source lineage")
    check(type(packet.get("observed_full_guide_card_count")) is int and packet["observed_full_guide_card_count"]==26,"all 26 HTML cards")
    check(packet.get("all_26_metadata_and_description_fingerprints_match_three_prior_snapshots") is True,"all normalized card fingerprints match")
    check(packet.get("raw_html_digest_differs_from_three_predecessors") is True and SOURCE_SHA not in [row[3] for row in PRIOR],"dynamic raw HTML differs from prior receipts")
    full=packet.get("all_26_guide_cards",[])
    check(isinstance(full,list) and len(full)==26,"26 metadata cards")
    for rec,_ in predecessors:
        check(full==rec.get("all_26_guide_cards"),"26 normalized metadata and description fingerprints identical to predecessor")
    check(packet.get("selected_tranche_episode_ordinals")==[16,17,18,19,20],"exclusive new E16–E20 scope")
    for field in ("fourth_five_source_descriptions_inspected","fourth_five_analytical_synopses_proposed"):
        check(type(packet.get(field)) is int and packet[field]==5,"five actual publisher descriptions processed "+field)
    cards=packet.get("fourth_five_guide_cards",[])
    check(isinstance(cards,list) and len(cards)==5,"five exact cards")
    check(type(packet.get("fourth_five_description_total_chars")) is int and packet["fourth_five_description_total_chars"]==677,"677 actual characters")
    check(sum(card["description_chars"] for card in cards)==677,"five description lengths sum")
    for i,card in enumerate(cards):
        n=i+16
        check(card==full[n-1] and card.get("title")==TITLES[i],"exact source title E"+str(n))
        for field in ("season","episode","display_order","analytics_ordinal","html_anchor_line","html_description_line","description_chars"):
            check(type(card.get(field)) is int,"strict source integer E"+str(n)+" "+field)
        check(card["season"]==2 and card["episode"]==card["display_order"]==card["analytics_ordinal"]==n,"source-local ordinal E"+str(n))
        check(card["html_anchor_line"]==1482+28*(n-1) and card["html_description_line"]==1500+28*(n-1),"exact source line E"+str(n))
        check(card["description_sha256"]==HASHES[i],"exact publisher paragraph fingerprint E"+str(n))
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/",card.get("video_route_path",""))),"metadata route only E"+str(n))
    expected_anomalies=predecessors[0][0]["source_local_publisher_datetime_anomalies"]
    check(packet.get("prior_source_local_publisher_datetime_anomalies_reobserved")==expected_anomalies==predecessors[1][0]["prior_source_local_publisher_datetime_anomalies_reobserved"]==predecessors[2][0]["prior_source_local_publisher_datetime_anomalies_reobserved"],"carry two unresolved datetime-order anomalies")
    fixture=[{"source_local_episode_hint":n,"claim_kind":kind,"scope":scope} for n,kind,scope in PRIOR_SEMANTIC]
    check(packet.get("prior_semantic_ambiguity_fixtures_reobserved")==fixture,"prior speech/memory/accusation/identity semantic holds exact")
    check(predecessors[0][0]["typed_assertions"][1]["narrative_claim_kind"]==PRIOR_SEMANTIC[0][1],"E2 character utterance fixture provenance")
    for index,pindex in ((1,1),(2,2),(4,3)):
        check(predecessors[1][0]["typed_assertions"][index]["narrative_claim_kind"]==PRIOR_SEMANTIC[pindex][1],"E7/E8/E10 prior semantic fixture provenance")
    entities,evidence,claims=(packet.get(x,[]) for x in ("local_entities","source_relative_evidence","typed_assertions"))
    check(len(entities)==len(evidence)==len(claims)==5,"five entity/evidence/assertion chains")
    for i,(ent,ev,claim) in enumerate(zip(entities,evidence,claims)):
        n=i+16
        stem=f"ent-s2-e{n:02d}"
        eid=f"{stem}-publisher-card"
        vid=f"{stem}-guide-description"
        check(ent.get("id")==eid and type(ent.get("source_local_episode_hint")) is int and ent["source_local_episode_hint"]==n,"source local entity E"+str(n))
        check(ent.get("source_kind")=="PUBLISHER_EPISODE_CARD" and ent.get("canonical_work_id") is None,"no global Work reconciliation E"+str(n))
        check(ev.get("id")==vid and ev.get("source_id")==source["local_source_id"] and ev.get("local_entity_id")==eid,"source relative evidence E"+str(n))
        check(ev.get("kind")=="PUBLISHER_GUIDE_DESCRIPTION" and type(ev.get("card_ordinal")) is int and ev["card_ordinal"]==n,"source evidence class E"+str(n))
        check(ev.get("publisher_description_sha256")==HASHES[i] and str(cards[i]["html_description_line"]) in ev.get("locator",""),"paragraph receipt E"+str(n))
        para=ev.get("original_paraphrase")
        check(isinstance(para,str) and 65<=len(para)<=200 and "\n" not in para,"original synopsis E"+str(n))
        check(ev.get("claim_mode")==CLAIM_KINDS[n],"source-relative semantic ambiguity E"+str(n))
        check(claim.get("id")==f"{stem}-publisher-describes" and claim.get("predicate")=="PUBLISHER_DESCRIBES" and claim.get("evidence_id")==vid,"typed assertion E"+str(n))
        check(claim.get("status")=="SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED" and claim.get("narrative_claim_kind")==CLAIM_KINDS[n] and claim.get("frame_claim_status")=="PUBLISHER_DESCRIPTION_ONLY","publisher attribution E"+str(n))
        for row in (ent,ev,claim):
            check(row["id"] not in seen_ids,"unique across all four batches")
            seen_ids.add(row["id"])
    check(prior_ordinals+[e["source_local_episode_hint"] for e in entities]==list(range(1,21)),"four disjoint description scopes E01–E20")
    check(packet.get("held_season_description_partition_summary")=={
        "prior_analyses":15,"this_tranche_analyses":5,
        "total_nonoverlapping_source_relative_description_proposals":20,
        "source_local_guide_cards_observed":26,
        "remaining_unprocessed_publisher_descriptions":6,
        "accepted_work_coverage_or_close_read_claims":0,
        "status":"HELD_PARTIAL_PUBLISHER_GUIDE_DESCRIPTIONS_NOT_EPISODE_CONTENT_CLOSE_READ",
    },"held description count not accepted Work/episode CLOSE_READ coverage")
    check(len(packet.get("holds",[]))>=8,"explicit method/copyright/identity holds")


def main()->int:
    try:
        prior=[(read_json(SIBLING/folder/"records.json"),hashlib.sha256((SIBLING/folder/"records.json").read_bytes()).hexdigest()) for folder,*_ in PRIOR]
        validate(read_json(HERE/"records.json"),prior)
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print("FAIL ENT S2 E16–E20: "+str(exc),file=sys.stderr)
        return 1
    print("PASS ENT S2 fourth five: 20/26 HELD publisher descriptions; zero accepted Work/audiovisual CLOSE_READ/coverage")
    return 0


if __name__=="__main__":
    sys.exit(main())
