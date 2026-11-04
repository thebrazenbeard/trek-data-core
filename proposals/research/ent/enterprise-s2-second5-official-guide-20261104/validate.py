"""Fail-closed ENT S2 second publisher-guide five source-relative custody."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
FIRST=HERE.parent/"enterprise-s2-first5-official-guide-20261104"
FIRST_RECORD=FIRST/"records.json"
FIRST_SHA="63d7fca810061115e101fd9277f55c039604c49a76eaefa9fc1f1d3a95f8bb94"
FIRST_COMMIT="f835b3142b3998fe602b33823cfadf561f51b2e5"
FIRST_SOURCE="860df3bd8d3c3e91727ab71c712cd60718da0bddf63fcd5bd5914b83358d9cdd"
SOURCE_SHA="321513d93517b9ea1e50b9ad339352da7dbc38a7564ec1806b4fc4cdc0badc26"
TITLES=["Marauders","The Seventh","The Communicator","Singularity","Vanishing Point"]
HASHES=[
    "68b4109b374fde6c194d56b5f735113eb262d13e24ead999cfe1e30132aec648",
    "82b7e0de2e74e260739a0f7be35756c015c0d415938557a2b6af2d03c461422e",
    "3ee8adb601775a30ee8992264c247ec06e2c17133c4fbc3017d7aa05076f122c",
    "2e7ffc2fcfa631897fadd944ba1e6c90ed54370606f512d3fd8b1cccef3cf378",
    "c96a2ede0435119fc325677be0299ccfab345c9cdfc8f0825055f1c924fca703",
]
EFFECTS=("accepted_source_binding_effect","accepted_work_effect","coverage_effect","denominator_effect","reconciliation_effect","explorer_synopsis_release_effect")


def check(condition:bool,message:str)->None:
    if not condition:
        raise ValueError(message)


def read_json(path:Path)->dict:
    def unique(pairs):
        result={}
        for key,val in pairs:
            if key in result:
                raise ValueError("duplicate JSON key "+key)
            result[key]=val
        return result
    return json.loads(path.read_text(encoding="utf8"),object_pairs_hook=unique)


def validate(packet:dict,first:dict,first_digest:str)->None:
    check(first_digest==FIRST_SHA,"exact predecessor source packet SHA")
    check(first.get("batch_id")=="ENT.PPLUS.S2.FIRST5.GUIDE.20261104" and first.get("status")=="HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE","prior held packet")
    check(first.get("source",{}).get("raw_response_sha256")==FIRST_SOURCE,"prior actual HTML source receipt")
    # Re-run predecessor validator on its own exact accepted discovery source;
    # checksum agreement alone does not prove honest records.
    spec=importlib.util.spec_from_file_location("ent_s2_prior_validator",FIRST/"validate.py")
    check(spec is not None and spec.loader is not None,"prior validator module exists")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    dsha=hashlib.sha256(mod.DISCOVERY.read_bytes()).hexdigest()
    mod.validate(first,mod.read_json(mod.DISCOVERY),dsha)
    check(packet.get("prior_batch")=={
        "path":str(FIRST_RECORD.relative_to(ROOT)),
        "sha256":FIRST_SHA,
        "commit":FIRST_COMMIT,
        "source_response_sha256":FIRST_SOURCE,
        "episode_scope":[1,5],
    },"exact prior episode-scope lineage")
    check(packet.get("schema_version")=="1.0.0" and packet.get("batch_id")=="ENT.PPLUS.S2.SECOND5.GUIDE.20261104","batch identity")
    check(packet.get("role")=="ENT" and packet.get("status")=="HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE","held ENT scope")
    check(packet.get("accepted_main_baseline")=="3028765359001b90bc3e6b5c1835ee283b326e91"==first.get("accepted_main_baseline"),"no shifting accepted main")
    for effect in EFFECTS:
        check(first.get(effect)=="NONE" and packet.get(effect)=="NONE","no protected effect "+effect)
    for field in ("episode_content_watched","transcripts_read","image_bytes_fetched"):
        check(first.get(field) is False and packet.get(field) is False,"no unearned media read "+field)
    source=packet.get("source",{})
    check(source.get("local_source_id")=="ent-s2-paramountplus-guide-html-second5-20261104","source-local identity")
    check(source.get("url")=="https://www.paramountplus.com/shows/enterprise/episodes/2/"==first["source"]["url"],"same official guide")
    check(source.get("independence_group")=="publisher:paramountplus.com"==first["source"]["independence_group"],"repeat read not independent witness")
    check(source.get("source_kind")=="FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML" and source.get("publisher")=="Paramount+","official source family")
    check(type(source.get("response_http_status")) is int and source["response_http_status"]==200,"source HTTP200")
    check(type(source.get("raw_response_bytes")) is int and source["raw_response_bytes"]==312754,"entire response bytes")
    check(source.get("raw_response_sha256")==SOURCE_SHA,"fresh full response hash")
    check(source.get("response_date_header")=="Wed, 04 Nov 2026 22:56:26 GMT" and source.get("observed_at_utc")=="2026-11-04T22:56:26.093633+00:00","timestamp receipt")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True and source.get("reproducible_extractor")=="source_probe.py","copyright/raw source not committed")
    check(packet.get("observed_full_guide_card_count")==26 and type(packet["observed_full_guide_card_count"]) is int,"full source traverse")
    check(packet.get("all_26_metadata_and_description_fingerprints_match_prior_snapshot") is True,"all normalized source metadata matched")
    check(packet.get("raw_html_digest_differs_from_predecessor") is True and SOURCE_SHA!=FIRST_SOURCE,"dynamic HTML differing source receipt")
    full=packet.get("all_26_guide_cards")
    check(isinstance(full,list) and len(full)==26 and full==first.get("all_26_guide_cards"),"all 26 exact normalized publisher cards match")
    check(packet.get("selected_tranche_episode_ordinals")==[6,7,8,9,10],"distinct second-five scope")
    for field in ("second_five_source_descriptions_inspected","second_five_analytical_synopses_proposed"):
        check(type(packet.get(field)) is int and packet[field]==5,"five descriptions actually analyzed "+field)
    cards=packet.get("second_five_guide_cards")
    check(isinstance(cards,list) and len(cards)==5,"five selected guide cards")
    check(type(packet.get("second_five_description_total_chars")) is int and packet["second_five_description_total_chars"]==842,"source actual description lengths")
    check(sum(card["description_chars"] for card in cards)==842,"selected total source characters")
    for i,card in enumerate(cards):
        n=i+6
        check(card==full[n-1] and card.get("title")==TITLES[i],"literal publisher metadata E"+str(n))
        for field in ("season","episode","display_order","analytics_ordinal","html_anchor_line","html_description_line","description_chars"):
            check(type(card.get(field)) is int,f"strict integer E{n}: "+field)
        check(card["season"]==2 and card["episode"]==card["display_order"]==card["analytics_ordinal"]==n,"source ordinal E"+str(n))
        check(card["html_anchor_line"]==1482+28*(n-1) and card["html_description_line"]==1500+28*(n-1),"source lines E"+str(n))
        check(card["description_sha256"]==HASHES[i],"description fingerprint E"+str(n))
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/",card["video_route_path"])),"video route metadata only E"+str(n))
    check(packet.get("prior_source_local_publisher_datetime_anomalies_reobserved")==first.get("source_local_publisher_datetime_anomalies"),"preserve prior ordinal/date inversion findings")
    ids={row["id"] for bucket in ("local_entities","source_relative_evidence","typed_assertions") for row in first[bucket]}
    entities,evidence,assertions=(packet.get(k,[]) for k in ("local_entities","source_relative_evidence","typed_assertions"))
    check(len(entities)==len(evidence)==len(assertions)==5,"five entity/evidence/typed assertion chains")
    for i,(entity,ev,claim) in enumerate(zip(entities,evidence,assertions)):
        n=i+6
        stem=f"ent-s2-e{n:02d}"
        eid=f"{stem}-publisher-card"
        vid=f"{stem}-guide-description"
        check(entity.get("id")==eid and type(entity.get("source_local_episode_hint")) is int and entity["source_local_episode_hint"]==n,"local entity E"+str(n))
        check(entity.get("source_kind")=="PUBLISHER_EPISODE_CARD" and entity.get("canonical_work_id") is None,"no Work binding E"+str(n))
        check(ev.get("id")==vid and ev.get("local_entity_id")==eid and ev.get("source_id")==source["local_source_id"],"source relative evidence links E"+str(n))
        check(ev.get("kind")=="PUBLISHER_GUIDE_DESCRIPTION" and type(ev.get("card_ordinal")) is int and ev["card_ordinal"]==n,"source evidence kind E"+str(n))
        check(ev.get("publisher_description_sha256")==HASHES[i] and str(cards[i]["html_description_line"]) in ev.get("locator",""),"description receipt E"+str(n))
        para=ev.get("original_paraphrase")
        check(isinstance(para,str) and 65<=len(para)<=200 and "\n" not in para,"original short source paraphrase E"+str(n))
        kind=("CHARACTER_MEMORY_EXPERIENCE_NOT_OBJECTIVE_HISTORY" if n==7 else
              "CULTURAL_ACCUSATION_NOT_OBJECTIVE_ESPIONAGE" if n==8 else
              "CHARACTER_QUESTIONS_IDENTITY_NOT_OBJECTIVE_REPLACEMENT" if n==10 else
              "PUBLISHER_PLOT_DESCRIPTION_NOT_VIDEO_VERIFIED")
        check(ev.get("claim_mode")==kind,"source-relative experiential/accusation boundary E"+str(n))
        check(claim.get("id")==f"{stem}-publisher-describes" and claim.get("predicate")=="PUBLISHER_DESCRIBES" and claim.get("evidence_id")==vid,"typed assertion links E"+str(n))
        check(claim.get("status")=="SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED" and claim.get("narrative_claim_kind")==kind and claim.get("frame_claim_status")=="PUBLISHER_DESCRIPTION_ONLY","publisher claims not verified episode reality E"+str(n))
        for row in (entity,ev,claim):
            check(row["id"] not in ids,"unique across both five-episode tranches")
            ids.add(row["id"])
    check([e["source_local_episode_hint"] for e in first["local_entities"]]+[e["source_local_episode_hint"] for e in entities]==list(range(1,11)),"ten disjoint source-relative descriptions E1–E10")
    check(packet.get("held_season_description_partition_summary")=={
        "prior_analyses":5,"this_tranche_analyses":5,
        "total_nonoverlapping_source_relative_description_proposals":10,
        "source_local_guide_cards_observed":26,
        "remaining_unprocessed_publisher_descriptions":16,
        "accepted_work_coverage_or_close_read_claims":0,
        "status":"HELD_PARTIAL_PUBLISHER_GUIDE_DESCRIPTIONS_NOT_EPISODE_CONTENT_CLOSE_READ",
    },"10 held descriptions not accepted Work/CLOSE_READ/coverage")
    check(len(packet.get("holds",[]))>=7,"required evidence/rights holds")


def main()->int:
    try:
        first=read_json(FIRST_RECORD)
        digest=hashlib.sha256(FIRST_RECORD.read_bytes()).hexdigest()
        validate(read_json(HERE/"records.json"),first,digest)
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print("FAIL ENT S2 E06–E10: "+str(exc),file=sys.stderr)
        return 1
    print("PASS ENT S2 second five: 10/26 HELD publisher descriptions, zero accepted Work/CLOSE_READ/coverage")
    return 0


if __name__=="__main__":
    sys.exit(main())
