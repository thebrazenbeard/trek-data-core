"""Fail-closed provenance and scope checks for ENT S2 E11–E15 guide reading."""

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
]
SOURCE_SHA="d2322c72a2069e2813798c9ad497453cc3e7092d75bee30853d129db58a7d84b"
TITLES=["Precious Cargo","The Catwalk","Dawn","Stigma","Cease Fire"]
HASHES=[
    "b7206134bd508b0ffa9691c38280dcc7544fb15206a1d8ff8c57b1bcd6be1b70",
    "ef545ed58147cfa3c6c70762930100aef938712cc306e149e590f83a27652668",
    "37e271ac937a2376361ed0a8eec3ab9a3110964079adf0ed6f48b9e384e9de29",
    "b710b055e12b193a1d6edfe4a24bf765617d947d44dc88c8a8066fdb27ffd39b",
    "dbb61e31f7795309719f12034794fa61f9058ba19fed10538596112a7a6d28bd",
]
EFFECTS=("accepted_source_binding_effect","accepted_work_effect","coverage_effect","denominator_effect","reconciliation_effect","explorer_synopsis_release_effect")


def check(condition:bool,message:str)->None:
    if not condition:
        raise ValueError(message)


def read_json(path:Path)->dict:
    def no_duplicates(pairs):
        result={}
        for key,val in pairs:
            if key in result:
                raise ValueError("duplicate JSON key "+key)
            result[key]=val
        return result
    return json.loads(path.read_text(encoding="utf8"),object_pairs_hook=no_duplicates)


def check_prior(predecessors:list[tuple[dict,str]])->None:
    check(len(predecessors)==2,"exact two predecessor batches")
    for i,((record,actual_sha),(folder,sha,commit,source_sha,batch_id,scope)) in enumerate(zip(predecessors,PRIOR)):
        check(actual_sha==sha,"exact predecessor file fingerprint")
        check(record.get("batch_id")==batch_id and record.get("status")=="HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE","held prior")
        check(record.get("source",{}).get("raw_response_sha256")==source_sha,"prior first-party HTML receipt")
        check([x.get("source_local_episode_hint") for x in record.get("local_entities",[])]==scope,"prior nonoverlapping scope")
        for effect in EFFECTS:
            check(record.get(effect)=="NONE","prior protected effect "+effect)
        module_path=SIBLING/folder/"validate.py"
        spec=importlib.util.spec_from_file_location(f"ent_s2_prior_{i}",module_path)
        check(spec is not None and spec.loader is not None,"prior validator module")
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if i==0:
            discovery_sha=hashlib.sha256(mod.DISCOVERY.read_bytes()).hexdigest()
            mod.validate(record,mod.read_json(mod.DISCOVERY),discovery_sha)
        else:
            mod.validate(record,predecessors[0][0],predecessors[0][1])


def validate(packet:dict,predecessors:list[tuple[dict,str]])->None:
    check_prior(predecessors)
    check(packet.get("schema_version")=="1.0.0" and packet.get("batch_id")=="ENT.PPLUS.S2.THIRD5.GUIDE.20261104","batch identity")
    check(packet.get("role")=="ENT" and packet.get("status")=="HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE","held ENT scope")
    check(packet.get("accepted_main_baseline")=="3028765359001b90bc3e6b5c1835ee283b326e91","baseline")
    for effect in EFFECTS:
        check(packet.get(effect)=="NONE","protected effect "+effect)
    for flag in ("episode_content_watched","transcripts_read","image_bytes_fetched"):
        check(packet.get(flag) is False,"unearned media read "+flag)
    check(len(packet.get("prior_batches",[]))==2,"two source-lineage receipts")
    prior_ids=set()
    ordinals=[]
    for i,((rec,digest),(folder,sha,commit,raw_sha,batch,scope)) in enumerate(zip(predecessors,PRIOR)):
        expected={
            "path":str((SIBLING/folder/"records.json").relative_to(ROOT)),
            "sha256":sha,"commit":commit,
            "source_response_sha256":raw_sha,"episode_scope":[scope[0],scope[-1]],
        }
        check(packet["prior_batches"][i]==expected,"exact predecessor scope and commit receipt")
        ordinals.extend(scope)
        for bucket in ("local_entities","source_relative_evidence","typed_assertions"):
            for row in rec.get(bucket,[]):
                check(row.get("id") not in prior_ids,"prior ID collision")
                prior_ids.add(row["id"])
    source=packet.get("source",{})
    check(source.get("local_source_id")=="ent-s2-paramountplus-guide-html-third5-20261104","source local ID")
    check(source.get("url")=="https://www.paramountplus.com/shows/enterprise/episodes/2/","publisher guide URL")
    check(source.get("independence_group")=="publisher:paramountplus.com","single publisher family")
    check(source.get("publisher")=="Paramount+" and source.get("source_kind")=="FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML","source publisher/kind")
    check(type(source.get("response_http_status")) is int and source["response_http_status"]==200,"HTTP 200")
    check(type(source.get("raw_response_bytes")) is int and source["raw_response_bytes"]==312754,"full HTML source bytes")
    check(source.get("raw_response_sha256")==SOURCE_SHA,"fresh response hash")
    check(source.get("response_date_header")=="Wed, 04 Nov 2026 23:04:38 GMT" and source.get("observed_at_utc")=="2026-11-04T23:04:38.278646+00:00","timestamp receipt")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True and source.get("reproducible_extractor")=="source_probe.py","raw text custody")
    for rec,_ in predecessors:
        check(source["url"]==rec["source"]["url"] and source["independence_group"]==rec["source"]["independence_group"],"same first-party source, not corroborating independent witness")
    check(type(packet.get("observed_full_guide_card_count")) is int and packet["observed_full_guide_card_count"]==26,"full page count")
    check(packet.get("all_26_metadata_and_description_fingerprints_match_two_prior_snapshots") is True,"normalized two-source-repeat agreement")
    check(packet.get("raw_html_digest_differs_from_two_predecessors") is True and SOURCE_SHA not in [x[3] for x in PRIOR],"raw HTML dynamic")
    all_cards=packet.get("all_26_guide_cards",[])
    check(isinstance(all_cards,list) and len(all_cards)==26,"26 card structural context")
    for rec,_ in predecessors:
        check(all_cards==rec.get("all_26_guide_cards"),"all 26 normalized cards match prior entire guide")
    check(packet.get("selected_tranche_episode_ordinals")==[11,12,13,14,15],"strict E11–E15 scope")
    for field in ("third_five_source_descriptions_inspected","third_five_analytical_synopses_proposed"):
        check(type(packet.get(field)) is int and packet[field]==5,"five source descriptions actually processed")
    cards=packet.get("third_five_guide_cards",[])
    check(isinstance(cards,list) and len(cards)==5,"five selected cards")
    check(type(packet.get("third_five_description_total_chars")) is int and packet["third_five_description_total_chars"]==531,"source description total")
    check(sum(c["description_chars"] for c in cards)==531,"source characters sum")
    for i,c in enumerate(cards):
        n=i+11
        check(c==all_cards[n-1] and c.get("title")==TITLES[i],"source title E"+str(n))
        for field in ("season","episode","display_order","analytics_ordinal","html_anchor_line","html_description_line","description_chars"):
            check(type(c.get(field)) is int,"strict numeric E"+str(n)+" "+field)
        check(c["season"]==2 and c["episode"]==c["display_order"]==c["analytics_ordinal"]==n,"source ordinal E"+str(n))
        check(c["html_anchor_line"]==1482+28*(n-1) and c["html_description_line"]==1500+28*(n-1),"exact source HTML lines E"+str(n))
        check(c["description_sha256"]==HASHES[i],"publisher paragraph fingerprint E"+str(n))
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/",c["video_route_path"])),"metadata route E"+str(n))
    check(packet.get("prior_source_local_publisher_datetime_anomalies_reobserved")==predecessors[0][0].get("source_local_publisher_datetime_anomalies")==predecessors[1][0].get("prior_source_local_publisher_datetime_anomalies_reobserved"),"date inversion preserved throughout lineage")
    entities,evidence,claims=(packet.get(k,[]) for k in ("local_entities","source_relative_evidence","typed_assertions"))
    check(len(entities)==len(evidence)==len(claims)==5,"five chain triples")
    for i,(ent,ev,claim) in enumerate(zip(entities,evidence,claims)):
        n=i+11
        stem=f"ent-s2-e{n:02d}"
        eid=f"{stem}-publisher-card"
        vid=f"{stem}-guide-description"
        check(ent.get("id")==eid and type(ent.get("source_local_episode_hint")) is int and ent["source_local_episode_hint"]==n,"local entity E"+str(n))
        check(ent.get("source_kind")=="PUBLISHER_EPISODE_CARD" and ent.get("canonical_work_id") is None,"no global Work identity E"+str(n))
        check(ev.get("id")==vid and ev.get("source_id")==source["local_source_id"] and ev.get("local_entity_id")==eid,"evidence linked E"+str(n))
        check(ev.get("kind")=="PUBLISHER_GUIDE_DESCRIPTION" and type(ev.get("card_ordinal")) is int and ev["card_ordinal"]==n,"source-relative evidence E"+str(n))
        check(ev.get("publisher_description_sha256")==HASHES[i] and str(cards[i]["html_description_line"]) in ev.get("locator",""),"source fingerprint and line E"+str(n))
        synopsis=ev.get("original_paraphrase")
        check(isinstance(synopsis,str) and 65<=len(synopsis)<=200 and "\n" not in synopsis,"original short publisher-derived paraphrase E"+str(n))
        check(ev.get("claim_mode")=="PUBLISHER_PLOT_DESCRIPTION_NOT_VIDEO_VERIFIED","claim mode E"+str(n))
        check(claim.get("id")==f"{stem}-publisher-describes" and claim.get("predicate")=="PUBLISHER_DESCRIBES" and claim.get("evidence_id")==vid,"typed assertion E"+str(n))
        check(claim.get("status")=="SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED" and claim.get("narrative_claim_kind")=="PUBLISHER_PLOT_DESCRIPTION_NOT_VIDEO_VERIFIED" and claim.get("frame_claim_status")=="PUBLISHER_DESCRIPTION_ONLY","publisher description attribution E"+str(n))
        for row in (ent,ev,claim):
            check(row["id"] not in prior_ids,"unique across three held batches")
            prior_ids.add(row["id"])
    check(ordinals+[e["source_local_episode_hint"] for e in entities]==list(range(1,16)),"three disjoint batches exactly E01–E15")
    check(packet.get("held_season_description_partition_summary")=={
        "prior_analyses":10,"this_tranche_analyses":5,
        "total_nonoverlapping_source_relative_description_proposals":15,
        "source_local_guide_cards_observed":26,
        "remaining_unprocessed_publisher_descriptions":11,
        "accepted_work_coverage_or_close_read_claims":0,
        "status":"HELD_PARTIAL_PUBLISHER_GUIDE_DESCRIPTIONS_NOT_EPISODE_CONTENT_CLOSE_READ",
    },"held synopsis count cannot become Work/CLOSE_READ")
    check(len(packet.get("holds",[]))>=8,"honest limits")


def main()->int:
    try:
        predecessors=[(read_json(SIBLING/folder/"records.json"),hashlib.sha256((SIBLING/folder/"records.json").read_bytes()).hexdigest()) for folder,*_ in PRIOR]
        validate(read_json(HERE/"records.json"),predecessors)
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print("FAIL ENT S2 E11–E15: "+str(exc),file=sys.stderr)
        return 1
    print("PASS ENT S2 third five: 15/26 HELD publisher descriptions, no accepted Work/episode CLOSE_READ/coverage")
    return 0


if __name__=="__main__":
    sys.exit(main())
