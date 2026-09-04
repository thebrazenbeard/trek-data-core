#!/usr/bin/env python3
import argparse, json, sys
from collections import defaultdict
from pathlib import Path

LIFECYCLES={"PROPOSED","ACCEPTED","CONTESTED","SUPERSEDED"}
MAPPING_ROLES={"EVIDENCE_BEARING","METADATA_ONLY","CROSSWALK_ONLY"}
CONTENT_BASIS_KINDS={"CONTENT_BODY_AUDIT","CONTENT_FINGERPRINT","BYTE_HASH","NORMALIZED_PASSAGE_FINGERPRINT","CONTAINER_MANIFEST"}
AUTHORITATIVE_TYPES={"source","work","source_work_binding","external_crosswalk"}

def validate_registry(sources, works, bindings, crosswalks, record_paths=None):
    errors=[]
    def req(row, fields, rid):
        for f in fields:
            if f not in row: errors.append(f"{rid}: missing required field {f}")
    for r in sources:
        rid=r.get("source_id","<source>"); req(r,["record_type","source_id","status","source_kind","provider","locator","provider_metadata","source_version","retrieved_at","content_hash","content_fingerprint","source_variant","provenance_family","independence_group","derived_from","fixture_only"],rid)
        if r.get("record_type")!="source": errors.append(f"{rid}: wrong record_type")
        if r.get("status") not in LIFECYCLES: errors.append(f"{rid}: invalid status")
        if not r.get("provenance_family"): errors.append(f"{rid}: missing provenance_family")
        if not r.get("independence_group"): errors.append(f"{rid}: missing independence_group")
        if not isinstance(r.get("derived_from"),list): errors.append(f"{rid}: derived_from must be list")
    for r in works:
        rid=r.get("work_id","<work>"); req(r,["record_type","work_id","status","title","work_type","parent_work_id","component_label","fixture_only"],rid)
        if r.get("record_type")!="work": errors.append(f"{rid}: wrong record_type")
        if r.get("status") not in LIFECYCLES: errors.append(f"{rid}: invalid status")
    for r in bindings:
        rid=r.get("binding_id","<binding>"); req(r,["record_type","binding_id","source_id","work_id","lifecycle","mapping_role","source_scope","work_scope","method","basis","exclusive_scope_key","supersedes_binding_id","notes","fixture_only"],rid)
        if r.get("record_type")!="source_work_binding": errors.append(f"{rid}: wrong record_type")
        if r.get("lifecycle") not in LIFECYCLES: errors.append(f"{rid}: invalid lifecycle")
        if r.get("mapping_role") not in MAPPING_ROLES: errors.append(f"{rid}: invalid mapping_role")
    for r in crosswalks:
        rid=r.get("crosswalk_id","<crosswalk>"); req(r,["record_type","crosswalk_id","target_kind","target_id","external_system","external_id","snapshot","retrieved_at","mapping_status","independence_group","lineage_note","fixture_only"],rid)
        if r.get("record_type")!="external_crosswalk": errors.append(f"{rid}: wrong record_type")

    id_fields=[("source",sources,"source_id"),("work",works,"work_id"),("binding",bindings,"binding_id"),("crosswalk",crosswalks,"crosswalk_id")]
    all_ids={}
    for kind,rows,f in id_fields:
        for r in rows:
            if f not in r: continue
            rid=r[f]
            if rid in all_ids: errors.append(f"duplicate id {rid} ({all_ids[rid]} and {kind})")
            all_ids[rid]=kind

    source_map={r.get("source_id"):r for r in sources if r.get("source_id")}
    work_map={r.get("work_id"):r for r in works if r.get("work_id")}
    bind_map={r.get("binding_id"):r for r in bindings if r.get("binding_id")}

    for w in works:
        p=w.get("parent_work_id")
        if p and p not in work_map: errors.append(f"{w.get('work_id')}: dangling parent_work_id {p}")

    for s in sources:
        sid=s.get("source_id")
        for parent in s.get("derived_from",[]) if isinstance(s.get("derived_from"),list) else []:
            if parent not in source_map: errors.append(f"{sid}: dangling derived_from {parent}")
            elif s.get("independence_group") != source_map[parent].get("independence_group"):
                errors.append(f"{sid}: derivative source uses different independence_group than parent {parent}")
    def detect_cycle(graph,label):
        visiting=set(); visited=set()
        def walk(n):
            if n in visiting: errors.append(f"{label} cycle detected at {n}"); return
            if n in visited: return
            visiting.add(n)
            for m in graph.get(n,[]): walk(m)
            visiting.remove(n); visited.add(n)
        for n in graph: walk(n)
    detect_cycle({s.get("source_id"):s.get("derived_from",[]) for s in sources if s.get("source_id")},"source derivation")

    accepted_exclusive=defaultdict(list)
    for b in bindings:
        bid=b.get("binding_id")
        if b.get("source_id") not in source_map: errors.append(f"{bid}: dangling source_id {b.get('source_id')}")
        if b.get("work_id") not in work_map: errors.append(f"{bid}: dangling work_id {b.get('work_id')}")
        if b.get("supersedes_binding_id") and b.get("supersedes_binding_id") not in bind_map:
            errors.append(f"{bid}: dangling supersedes_binding_id {b.get('supersedes_binding_id')}")
        if b.get("lifecycle")=="ACCEPTED":
            if b.get("mapping_role")!="EVIDENCE_BEARING": errors.append(f"{bid}: ACCEPTED binding must be EVIDENCE_BEARING")
            if not str(b.get("method","")).strip(): errors.append(f"{bid}: ACCEPTED binding missing method")
            basis=b.get("basis") or []
            if not basis: errors.append(f"{bid}: ACCEPTED binding missing basis")
            kinds={x.get("kind") for x in basis if isinstance(x,dict)}
            if not (kinds & CONTENT_BASIS_KINDS): errors.append(f"{bid}: ACCEPTED binding lacks evidence-bearing content/hash/manifest basis")
            key=b.get("exclusive_scope_key")
            if key: accepted_exclusive[(b.get("source_id"),key)].append(b)
    for key,bs in accepted_exclusive.items():
        works_here={b.get("work_id") for b in bs}
        if len(works_here)>1: errors.append(f"conflicting ACCEPTED bindings for exclusive source scope {key}: {sorted(works_here)}")
    detect_cycle({b.get("binding_id"):[b.get("supersedes_binding_id")] if b.get("supersedes_binding_id") else [] for b in bindings if b.get("binding_id")},"binding supersession")
    successors=defaultdict(list)
    for b in bindings:
        if b.get("supersedes_binding_id"): successors[b["supersedes_binding_id"]].append(b["binding_id"])
    for b in bindings:
        if b.get("lifecycle")=="SUPERSEDED" and not successors.get(b.get("binding_id")):
            errors.append(f"{b.get('binding_id')}: SUPERSEDED binding has no explicit successor")

    for c in crosswalks:
        cid=c.get("crosswalk_id"); target=c.get("target_id")
        if c.get("target_kind")=="SOURCE" and target not in source_map: errors.append(f"{cid}: dangling SOURCE target {target}")
        if c.get("target_kind")=="WORK" and target not in work_map: errors.append(f"{cid}: dangling WORK target {target}")

    for p,row in record_paths or []:
        norm=str(p).replace("\\","/")
        if "/research/" in f"/{norm}" and row.get("record_type") in AUTHORITATIVE_TYPES:
            errors.append(f"{norm}: authoritative {row.get('record_type')} record under research partition")
    return errors

def source_bound_pairs(bindings):
    return sorted({(b["source_id"],b["work_id"]) for b in bindings if b.get("lifecycle")=="ACCEPTED" and b.get("mapping_role")=="EVIDENCE_BEARING"})

def load_fixture_file(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    sources=data.get("sources",[]); works=data.get("works",[]); bindings=data.get("bindings",[]); crosswalks=data.get("crosswalks",[])
    record_paths=[]
    for rows in (sources,works,bindings,crosswalks): record_paths += [(Path(path),r) for r in rows]
    return sources,works,bindings,crosswalks,record_paths,data.get("analysis_passes",[])

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("fixture_file",nargs="?",default="registry/librarian_registry_fixtures.json"); args=ap.parse_args()
    s,w,b,c,rp,passes=load_fixture_file(args.fixture_file)
    errors=validate_registry(s,w,b,c,rp)
    source_ids={x.get("source_id") for x in s}
    for p in passes:
        if p.get("source_id") not in source_ids: errors.append(f"{p.get('analysis_pass_id')}: dangling analysis-pass source_id {p.get('source_id')}")
    if errors:
        print("LIBRARIAN REGISTRY VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    pairs=source_bound_pairs(b)
    print(f"LIBRARIAN REGISTRY VALIDATION PASSED: {len(s)} sources, {len(w)} works, {len(b)} bindings, {len(c)} crosswalks, {len(passes)} analysis-pass fixtures")
    print(f"FIXTURE SOURCE_BOUND-ELIGIBLE PAIRS: {len(pairs)}")
    return 0
if __name__=="__main__": sys.exit(main())
