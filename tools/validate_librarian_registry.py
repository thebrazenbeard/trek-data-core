#!/usr/bin/env python3
import argparse, json, sys
from collections import defaultdict
from pathlib import Path

LIFECYCLES={"PROPOSED","ACCEPTED","CONTESTED","SUPERSEDED"}
MAPPING_ROLES={"EVIDENCE_BEARING","METADATA_ONLY","CROSSWALK_ONLY"}
CONTENT_BASIS_KINDS={"CONTENT_BODY_AUDIT","CONTENT_FINGERPRINT","BYTE_HASH","NORMALIZED_PASSAGE_FINGERPRINT","CONTAINER_MANIFEST"}
AUTHORITATIVE_TYPES={"source","work","source_work_binding","external_crosswalk"}

# The registry deliberately uses only this subset of JSON Schema 2020-12.
# Keep validation dependency-free while enforcing the checked-in contract,
# including nested scopes, unexpected properties and JSON types.
SCHEMA_PATH=Path(__file__).resolve().parents[1]/"registry"/"librarian_registry_contract.schema.json"
SCHEMA_DEFS=json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))["$defs"]

def schema_errors(value, schema, path):
    errors=[]
    types={"object":lambda v:isinstance(v,dict),
           "array":lambda v:isinstance(v,list),
           "string":lambda v:isinstance(v,str),
           "null":lambda v:v is None,
           "boolean":lambda v:isinstance(v,bool),
           "integer":lambda v:isinstance(v,int) and not isinstance(v,bool),
           "number":lambda v:isinstance(v,(int,float)) and not isinstance(v,bool)}
    expected=schema.get("type")
    if expected is not None:
        allowed=[expected] if isinstance(expected,str) else expected
        if not any(types[t](value) for t in allowed):
            return [f"{path}: expected type {'|'.join(allowed)}"]
    if "const" in schema and value!=schema["const"]:
        errors.append(f"{path}: does not match required const")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: invalid enum value")
    if isinstance(value,str) and len(value)<schema.get("minLength",0):
        errors.append(f"{path}: shorter than minLength")
    if isinstance(value,dict):
        properties=schema.get("properties",{})
        for key in schema.get("required",[]):
            if key not in value: errors.append(f"{path}: missing required field {key}")
        for key,child in value.items():
            if key in properties:
                errors.extend(schema_errors(child,properties[key],f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected field {key}")
    if isinstance(value,list) and isinstance(schema.get("items"),dict):
        for index,child in enumerate(value):
            errors.extend(schema_errors(child,schema["items"],f"{path}[{index}]"))
    return errors

def validate_registry(sources, works, bindings, crosswalks, record_paths=None):
    errors=[]
    record_sets=[("source",sources,"source_id"),("work",works,"work_id"),
                 ("source_work_binding",bindings,"binding_id"),
                 ("external_crosswalk",crosswalks,"crosswalk_id")]
    for kind,rows,id_field in record_sets:
        if not isinstance(rows,list):
            return [f"{kind}: records must be an array"]
        for index,row in enumerate(rows):
            if not isinstance(row,dict):
                return [f"{kind}[{index}]: record must be an object"]
            errors.extend(schema_errors(row,SCHEMA_DEFS[kind],str(row.get(id_field,f"{kind}[{index}]"))))
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
    detect_cycle({w.get("work_id"):[w["parent_work_id"]] if w.get("parent_work_id") else [] for w in works if w.get("work_id")},"work parent")

    accepted_exclusive=defaultdict(list)
    for b in bindings:
        bid=b.get("binding_id")
        if b.get("source_id") not in source_map: errors.append(f"{bid}: dangling source_id {b.get('source_id')}")
        if b.get("work_id") not in work_map: errors.append(f"{bid}: dangling work_id {b.get('work_id')}")
        if b.get("supersedes_binding_id") and b.get("supersedes_binding_id") not in bind_map:
            errors.append(f"{bid}: dangling supersedes_binding_id {b.get('supersedes_binding_id')}")
        if b.get("lifecycle")=="ACCEPTED":
            source=source_map.get(b.get("source_id")); work=work_map.get(b.get("work_id"))
            if source is not None and work is not None:
                fixture=bool(b.get("fixture_only"))
                if bool(source.get("fixture_only"))!=fixture or bool(work.get("fixture_only"))!=fixture:
                    errors.append(f"{bid}: fixture/authoritative identity boundary mismatch")
                if not fixture and (source.get("status")!="ACCEPTED" or work.get("status")!="ACCEPTED"):
                    errors.append(f"{bid}: ACCEPTED binding requires ACCEPTED Source and Work")
            if b.get("mapping_role")!="EVIDENCE_BEARING": errors.append(f"{bid}: ACCEPTED binding must be EVIDENCE_BEARING")
            if not str(b.get("method","")).strip(): errors.append(f"{bid}: ACCEPTED binding missing method")
            basis=b.get("basis") or []
            if not basis: errors.append(f"{bid}: ACCEPTED binding missing basis")
            kinds={x.get("kind") for x in basis if isinstance(x,dict)}
            if not (kinds & CONTENT_BASIS_KINDS): errors.append(f"{bid}: ACCEPTED binding lacks evidence-bearing content/hash/manifest basis")
            key=b.get("exclusive_scope_key")
            if key: accepted_exclusive[(b.get("source_id"),key)].append(b)
            predecessor=bind_map.get(b.get("supersedes_binding_id"))
            if predecessor and predecessor.get("lifecycle")!="SUPERSEDED":
                errors.append(f"{bid}: ACCEPTED successor requires SUPERSEDED predecessor")
        source_scope=b.get("source_scope")
        work_scope=b.get("work_scope")
        if isinstance(source_scope,dict) and source_scope.get("scope_type") in {"SLICE","COMPONENT"} and not str(source_scope.get("locator") or "").strip():
            errors.append(f"{bid}: bounded source scope requires locator")
        if isinstance(work_scope,dict) and work_scope.get("scope_type")=="COMPONENT" and not str(work_scope.get("component_label") or "").strip():
            errors.append(f"{bid}: component work scope requires component_label")
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
