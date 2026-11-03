import json, pathlib, re
p=pathlib.Path(__file__).with_name("observations.json")
def unique_pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise ValueError("duplicate JSON key")
        out[k]=v
    return out
d=json.loads(p.read_text(encoding="utf-8"),object_pairs_hook=unique_pairs)
def require(ok, message):
    if not ok: raise ValueError(message)
require(d["source_url"]=="https://www.startrek.com/news/star-trek-prodigy-season-2-now-available","source URL drift")
require(d["raw_html_sha256"]=="453aeb5dc7f69ff005f3da70f41a43d4755f4157253e0bba3f5d76d54a57b12a","source hash drift")
rows=d["records"]
titles=["Into the Breach, Part I","Into the Breach, Part II","Who Saves the Saviors","Temporal Mechanics 101","Observer's Paradox"]
require(len(rows)==5,"wrong row count")
require([x["publisher_slot"] for x in rows]==[str(i) for i in range(201,206)],"slot drift")
require([x["source_local_id"] for x in rows]==[f"startrek-pro-s2-{i}" for i in range(201,206)],"id drift")
require([x["publisher_title"] for x in rows]==titles,"title drift")
require(all(x["source_status"]=="SOURCE_BOUND_PUBLISHER_DESCRIPTION_ONLY" and x["work_identity"]=="UNRESOLVED" and x["coverage_effect"]=="NONE" and x["artwork_rights"]=="HELD_NO_PUBLIC_DISPLAY_LICENSE" for x in rows),"publication gate")
require(all(x["original_source_relative_synopsis"].strip() for x in rows),"missing paraphrase")
print("PRODIGY_S2_SOURCE_LOCAL_VALIDATION_PASS")
