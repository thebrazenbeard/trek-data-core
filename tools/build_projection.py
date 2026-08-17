#!/usr/bin/env python3
"""Deterministically compile governed Git records into canonical logical projections."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREDICATE_REGISTRY = ROOT / "registry" / "predicates.json"
SCOPE_KEY_REGISTRY = ROOT / "registry" / "scope_keys.json"
DATA_ROOTS = (ROOT / "research", ROOT / "external", ROOT / "migrations")
PROJECTION_STATUSES = {"STABLE", "CONTESTED", "UNRESOLVED", "STRUCTURAL_PARADOX"}
DISPOSITIONS = {"PROPOSED", "ACCEPTED", "REJECTED"}
CANONICAL_OUTPUTS = (
    "entities.jsonl", "facts.jsonl", "relations.jsonl", "contested.jsonl", "unresolved.jsonl",
    "provenance.jsonl", "assertion_history.jsonl", "reconciliation_history.jsonl",
)


def canonical(obj): return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def sha256_bytes(data: bytes) -> str: return "sha256:" + hashlib.sha256(data).hexdigest()
def canonical_json_hash(path: Path) -> str:
    obj = json.loads(path.read_text(encoding="utf-8")); return sha256_bytes(canonical(obj).encode("utf-8"))


def load_predicates():
    registry=json.loads(PREDICATE_REGISTRY.read_text(encoding="utf-8")); return {r["name"]:r for r in registry.get("predicates",[]) if r.get("name")}

def load_scope_keys():
    registry=json.loads(SCOPE_KEY_REGISTRY.read_text(encoding="utf-8")); return {r["key"]:r for r in registry.get("scope_keys",[]) if r.get("key")}


def iter_typed_records(roots):
    """Read typed JSON/JSONL deterministically and fail closed on untyped governed data."""
    for root in roots:
        if not root.exists(): continue
        for path in sorted(root.rglob("*.json")):
            if path.name == "README.json": continue
            obj=json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(obj,dict): raise ValueError(f"{path}: governed JSON record must be an object")
            if not obj.get("record_type"): raise ValueError(f"{path}: governed JSON record missing record_type")
            yield obj
        for path in sorted(root.rglob("*.jsonl")):
            for line_no,raw in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
                if not raw.strip(): continue
                obj=json.loads(raw)
                if not isinstance(obj,dict): raise ValueError(f"{path}:{line_no}: JSONL record must be an object")
                if not obj.get("record_type"): raise ValueError(f"{path}:{line_no}: governed JSONL record missing record_type")
                yield obj


def index_unique(records, record_type, id_key):
    indexed={}
    for record in records:
        if record.get("record_type") != record_type: continue
        rid=record.get(id_key)
        if not rid: raise ValueError(f"{record_type} record missing {id_key}")
        if rid in indexed: raise ValueError(f"duplicate {record_type} id {rid}")
        indexed[rid]=record
    return indexed


def active_accepted_decisions(decisions):
    accepted=[d for d in decisions if d.get("record_type")=="reconciliation_decision" and d.get("status")=="ACCEPTED"]
    superseded={d.get("supersedes") for d in accepted if d.get("supersedes")}
    return [d for d in accepted if d.get("decision_id") not in superseded]


def decision_key(decision):
    dtype=decision.get("decision_type"); subject_type=decision.get("subject_type"); subject_id=decision.get("subject_id"); payload=decision.get("payload") or {}
    base=(dtype,subject_type,subject_id)
    if dtype=="ENTITY_LINK": return base+(payload.get("relation_predicate"),)
    if dtype=="SCOPE_RESOLUTION": return base+(payload.get("resolution_key"),)
    if dtype in {"ASSERTION_DISPOSITION","ASSERTION_PROJECTION_STATUS"}: return base
    return None


def validate_executable_decision(decision, predicates, scope_keys, indexes):
    dtype=decision.get("decision_type"); payload=decision.get("payload") or {}; subject_type=decision.get("subject_type")
    if dtype=="OTHER": raise ValueError("accepted OTHER reconciliation decision is not executable")
    if dtype=="ENTITY_LINK":
        if subject_type!="LOCAL_ENTITY": raise ValueError("ENTITY_LINK requires LOCAL_ENTITY subject")
        if set(payload)!={"relation_predicate","target_type","target_id"}: raise ValueError("ENTITY_LINK requires typed relation payload")
        if payload.get("target_type")!="LOCAL_ENTITY": raise ValueError("ENTITY_LINK target must be LOCAL_ENTITY until global entity schema exists")
        predicate=predicates.get(payload.get("relation_predicate"))
        if not predicate or predicate.get("semantic_class")!="IDENTITY_RELATION" or predicate.get("status")!="ACCEPTED": raise ValueError(f"ENTITY_LINK predicate {payload.get('relation_predicate')} is not accepted identity semantics")
        if decision.get("subject_id") not in indexes["local_entity"] or payload.get("target_id") not in indexes["local_entity"]: raise ValueError("ENTITY_LINK references missing local entity")
    elif dtype=="ASSERTION_DISPOSITION":
        if subject_type!="ASSERTION" or set(payload)!={"disposition"} or payload.get("disposition") not in DISPOSITIONS: raise ValueError("invalid ASSERTION_DISPOSITION decision")
    elif dtype=="ASSERTION_PROJECTION_STATUS":
        if subject_type!="ASSERTION" or set(payload)!={"projection_status"} or payload.get("projection_status") not in PROJECTION_STATUSES: raise ValueError("invalid ASSERTION_PROJECTION_STATUS decision")
    elif dtype=="SCOPE_RESOLUTION":
        if subject_type not in {"ASSERTION","WORK","LOCAL_ENTITY"} or set(payload)!={"resolution_key","resolution"}: raise ValueError("invalid SCOPE_RESOLUTION decision")
        entry=scope_keys.get(payload.get("resolution_key"))
        if not entry or subject_type not in set(entry.get("subject_types",[])): raise ValueError(f"ungoverned scope resolution {payload.get('resolution_key')} for {subject_type}")
    else:
        raise ValueError(f"unknown executable reconciliation decision type {dtype}")


def decision_index(decisions, predicates, scope_keys, indexes):
    indexed={}
    for decision in active_accepted_decisions(decisions):
        validate_executable_decision(decision,predicates,scope_keys,indexes)
        key=decision_key(decision)
        if key is None: continue
        if key in indexed: raise ValueError(f"multiple active reconciliation decisions for {key}")
        indexed[key]=decision
    return indexed


def typed_ref(value):
    if not isinstance(value,dict) or set(value)!={"ref_type","ref_id"}: return None
    return value.get("ref_type"),value.get("ref_id")


def scope_decisions_for(decisions, subject_type, subject_id):
    found={}
    for key,decision in decisions.items():
        if len(key)==4 and key[0]=="SCOPE_RESOLUTION" and key[1]==subject_type and key[2]==subject_id:
            found[key[3]]=decision
    return found


def entity_link_decisions_for(decisions, local_id):
    found=[]
    for key,decision in decisions.items():
        if len(key)==4 and key[0]=="ENTITY_LINK" and key[1]=="LOCAL_ENTITY" and key[2]==local_id: found.append(decision)
    return sorted(found,key=lambda d:(d.get("payload",{}).get("relation_predicate",""),d.get("decision_id","")))


def source_lineage(source_id, sources):
    result=[]; seen=set(); stack=[]
    def visit(current):
        if current in stack: raise ValueError(f"source derivation cycle at {current}")
        if current in seen: return
        record=sources.get(current)
        if record is None: raise ValueError(f"missing source lineage record {current}")
        seen.add(current); stack.append(current)
        for parent in sorted(record.get("derived_from",[])): visit(parent)
        stack.pop()
        if current!=source_id: result.append(copy.deepcopy(record))
    visit(source_id)
    return sorted(result,key=lambda r:r.get("source_id",""))


def work_lineage(work_id, works):
    result=[]; seen=set(); current=works.get(work_id)
    while current and current.get("parent_work_id"):
        parent_id=current.get("parent_work_id")
        if parent_id in seen: raise ValueError(f"work parent cycle at {parent_id}")
        seen.add(parent_id); parent=works.get(parent_id)
        if parent is None: raise ValueError(f"missing parent work {parent_id}")
        result.append(copy.deepcopy(parent)); current=parent
    return result


def referenced_record(ref_type, ref_id, indexes):
    mapping={"SOURCE":"source","WORK":"work","LOCAL_ENTITY":"local_entity","EVIDENCE":"evidence","ASSERTION":"assertion"}
    record_type=mapping.get(ref_type); return copy.deepcopy(indexes.get(record_type,{}).get(ref_id)) if record_type else None


def effective_disposition(assertion, decisions, superseded_assertions):
    assertion_id=assertion.get("assertion_id"); decision=decisions.get(("ASSERTION_DISPOSITION","ASSERTION",assertion_id))
    value=assertion.get("status")
    if decision is not None: value=(decision.get("payload") or {}).get("disposition")
    if assertion_id in superseded_assertions: value="SUPERSEDED"
    return value,decision


def projection_status(assertion, decisions):
    assertion_id=assertion.get("assertion_id"); decision=decisions.get(("ASSERTION_PROJECTION_STATUS","ASSERTION",assertion_id))
    if decision is None: return "UNRESOLVED",None,"MISSING_PROJECTION_STATUS"
    value=(decision.get("payload") or {}).get("projection_status")
    if value not in PROJECTION_STATUSES: raise ValueError(f"invalid projection status for {assertion_id}")
    return value,decision,None


def build_logical_projection(records, reconciliation_decisions):
    records=[copy.deepcopy(r) for r in records]; reconciliation_decisions=[copy.deepcopy(r) for r in reconciliation_decisions]
    indexes={
        "source":index_unique(records,"source","source_id"), "work":index_unique(records,"work","work_id"),
        "local_entity":index_unique(records,"local_entity","local_entity_id"), "evidence":index_unique(records,"evidence","evidence_id"),
        "assertion":index_unique(records,"assertion","assertion_id"),
    }
    predicates=load_predicates(); scope_keys=load_scope_keys(); decisions=decision_index(reconciliation_decisions,predicates,scope_keys,indexes)
    assertions=indexes["assertion"]; superseded_assertions={a.get("supersedes") for a in assertions.values() if a.get("supersedes")}

    relations=[]; entities=[]
    for local_id,entity in sorted(indexes["local_entity"].items()):
        row=copy.deepcopy(entity); links=entity_link_decisions_for(decisions,local_id); scopes=scope_decisions_for(decisions,"LOCAL_ENTITY",local_id)
        if links:
            row["identity_links"]=[{**copy.deepcopy(d["payload"]),"decision_id":d["decision_id"]} for d in links]
            for d in links:
                payload=d["payload"]; relations.append({"record_type":"projection_relation","relation_id":f"reconciliation:{d['decision_id']}","relation_kind":"IDENTITY_LINK","subject_type":"LOCAL_ENTITY","subject_id":local_id,"predicate":payload["relation_predicate"],"target_type":payload["target_type"],"target_id":payload["target_id"],"reconciliation_decision_id":d["decision_id"]})
        if scopes:
            row["resolved_scope"]={k:copy.deepcopy(d["payload"]["resolution"]) for k,d in sorted(scopes.items())}; row["scope_resolution_decision_ids"]={k:d["decision_id"] for k,d in sorted(scopes.items())}
        entities.append(row)

    facts=[]; contested=[]; unresolved=[]; provenance=[]
    effective_cache={}
    for assertion_id,assertion in assertions.items(): effective_cache[assertion_id]=effective_disposition(assertion,decisions,superseded_assertions)

    for assertion_id,assertion in sorted(assertions.items()):
        effective,disp_decision=effective_cache[assertion_id]
        if effective!="ACCEPTED": continue
        row=copy.deepcopy(assertion); row["effective_assertion_status"]=effective
        if disp_decision: row["assertion_disposition_decision_id"]=disp_decision.get("decision_id")
        status,status_decision,reason=projection_status(assertion,decisions); row["projection_status"]=status
        if status_decision: row["projection_status_decision_id"]=status_decision.get("decision_id")
        if reason: row["projection_reason"]=reason
        scopes=scope_decisions_for(decisions,"ASSERTION",assertion_id)
        if scopes:
            row["resolved_scope"]={k:copy.deepcopy(d["payload"]["resolution"]) for k,d in sorted(scopes.items())}; row["scope_resolution_decision_ids"]={k:d["decision_id"] for k,d in sorted(scopes.items())}
        if assertion.get("subject_type")=="LOCAL_ENTITY":
            links=entity_link_decisions_for(decisions,assertion.get("subject"))
            if links: row["subject_identity_links"]=[{**copy.deepcopy(d["payload"]),"decision_id":d["decision_id"]} for d in links]
        subject_scopes=scope_decisions_for(decisions,assertion.get("subject_type"),assertion.get("subject"))
        if subject_scopes:
            row["subject_resolved_scope"]={k:copy.deepcopy(d["payload"]["resolution"]) for k,d in sorted(subject_scopes.items())}; row["subject_scope_resolution_decision_ids"]={k:d["decision_id"] for k,d in sorted(subject_scopes.items())}
        if status=="STABLE": facts.append(row)
        elif status in {"CONTESTED","STRUCTURAL_PARADOX"}: contested.append(row)
        else: unresolved.append(row)
        ref=typed_ref(assertion.get("object"))
        if ref:
            target_type,target_id=ref; relations.append({"record_type":"projection_relation","relation_id":f"assertion:{assertion_id}","relation_kind":"ASSERTION_PREDICATE","assertion_id":assertion_id,"subject_type":assertion.get("subject_type"),"subject_id":assertion.get("subject"),"predicate":assertion.get("predicate"),"target_type":target_type,"target_id":target_id,"projection_status":status})

    for assertion_id,assertion in sorted(assertions.items()):
        effective,disp_decision=effective_cache[assertion_id]; status=None; status_decision=None; reason=None
        if effective=="ACCEPTED": status,status_decision,reason=projection_status(assertion,decisions)
        assertion_scopes=scope_decisions_for(decisions,"ASSERTION",assertion_id)
        subject_links=entity_link_decisions_for(decisions,assertion.get("subject")) if assertion.get("subject_type")=="LOCAL_ENTITY" else []
        for evidence_id in sorted(assertion.get("evidence",[])):
            ev=indexes["evidence"].get(evidence_id)
            if ev is None: raise ValueError(f"assertion {assertion_id} references missing evidence {evidence_id}")
            source=indexes["source"].get(ev.get("source_id")); work=indexes["work"].get(ev.get("work_id"))
            if source is None or work is None: raise ValueError(f"evidence {evidence_id} has missing source/work")
            row={
                "record_type":"projection_provenance","provenance_id":f"{assertion_id}::{evidence_id}","assertion_id":assertion_id,"evidence_id":evidence_id,
                "assertion_record":copy.deepcopy(assertion),"effective_assertion_status":effective,"support_set":sorted(assertion.get("evidence",[])),
                "evidence_record":copy.deepcopy(ev),"source_record":copy.deepcopy(source),"source_lineage_records":source_lineage(source["source_id"],indexes["source"]),
                "work_record":copy.deepcopy(work),"work_lineage_records":work_lineage(work["work_id"],indexes["work"]),
            }
            if disp_decision: row["assertion_disposition_decision_id"]=disp_decision["decision_id"]
            if status is not None: row["projection_status"]=status
            if status_decision: row["projection_status_decision_id"]=status_decision["decision_id"]
            if reason: row["projection_reason"]=reason
            if assertion_scopes: row["scope_resolution_decision_ids"]={k:d["decision_id"] for k,d in sorted(assertion_scopes.items())}
            if subject_links: row["entity_link_decision_ids"]=[d["decision_id"] for d in subject_links]
            observer=ev.get("observer_local_entity_id")
            if observer: row["observer_local_entity_record"]=copy.deepcopy(indexes["local_entity"].get(observer))
            subject_record=referenced_record(assertion.get("subject_type"),assertion.get("subject"),indexes)
            if subject_record: row["subject_record"]=subject_record
            ref=typed_ref(assertion.get("object"))
            if ref:
                object_record=referenced_record(ref[0],ref[1],indexes)
                if object_record: row["object_record"]=object_record
            provenance.append(row)

    assertion_history=sorted([copy.deepcopy(a) for a in assertions.values()],key=lambda a:a.get("assertion_id",""))
    reconciliation_history=sorted([copy.deepcopy(d) for d in reconciliation_decisions if d.get("record_type")=="reconciliation_decision" and d.get("status") in {"ACCEPTED","SUPERSEDED"}],key=lambda d:d.get("decision_id",""))
    return {
        "entities":sorted(entities,key=lambda r:r.get("local_entity_id","")), "facts":sorted(facts,key=lambda r:r.get("assertion_id","")),
        "relations":sorted(relations,key=lambda r:r.get("relation_id","")), "contested":sorted(contested,key=lambda r:r.get("assertion_id","")),
        "unresolved":sorted(unresolved,key=lambda r:r.get("assertion_id","")), "provenance":sorted(provenance,key=lambda r:r.get("provenance_id","")),
        "assertion_history":assertion_history, "reconciliation_history":reconciliation_history,
    }


def write_jsonl(path: Path, records, id_key: str):
    ordered=sorted(records,key=lambda r:(str(r.get(id_key,"")),canonical(r))); payload="".join(canonical(r)+"\n" for r in ordered).encode("utf-8"); path.write_bytes(payload); return sha256_bytes(payload),len(ordered)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); ap.add_argument("--projection-version",default="0.2.0"); ap.add_argument("--schema-version",required=True); ap.add_argument("--methodology-version",required=True); ap.add_argument("--research-head",required=True); ap.add_argument("--reconciliation-head",required=True); ap.add_argument("--compiler-commit",required=True); args=ap.parse_args()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    records=list(iter_typed_records(DATA_ROOTS)); decisions=list(iter_typed_records((ROOT/"reconciliation",))); logical=build_logical_projection(records,decisions)
    specs={
        "entities.jsonl":(logical["entities"],"local_entity_id"),"facts.jsonl":(logical["facts"],"assertion_id"),"relations.jsonl":(logical["relations"],"relation_id"),
        "contested.jsonl":(logical["contested"],"assertion_id"),"unresolved.jsonl":(logical["unresolved"],"assertion_id"),"provenance.jsonl":(logical["provenance"],"provenance_id"),
        "assertion_history.jsonl":(logical["assertion_history"],"assertion_id"),"reconciliation_history.jsonl":(logical["reconciliation_history"],"decision_id"),
    }
    outputs={}
    for filename,(rows,id_key) in specs.items():
        row_hash,count=write_jsonl(out/filename,rows,id_key); outputs[filename]={"role":filename.removesuffix('.jsonl'),"hash":row_hash,"count":count}
    # Temporary compatibility aliases for downstream proposal adapters. They are not canonical manifest outputs.
    (out/"accepted_reconciliation.jsonl").write_bytes((out/"reconciliation_history.jsonl").read_bytes())
    (out/"accepted_assertions.jsonl").write_bytes((out/"assertion_history.jsonl").read_bytes())
    predicate_registry_hash=canonical_json_hash(PREDICATE_REGISTRY); scope_key_registry_hash=canonical_json_hash(SCOPE_KEY_REGISTRY)
    logical_input_records=[r for r in records if r.get("record_type") in {"source","work","local_entity","evidence","assertion"}]
    logical_input_hash=sha256_bytes("".join(canonical(r)+"\n" for r in sorted(logical_input_records,key=canonical)).encode("utf-8"))
    input_identity={"research_head":args.research_head,"reconciliation_head":args.reconciliation_head,"schema_version":args.schema_version,"methodology_version":args.methodology_version,"predicate_registry_hash":predicate_registry_hash,"scope_key_registry_hash":scope_key_registry_hash,"compiler_commit":args.compiler_commit,"logical_input_records_hash":logical_input_hash,"reconciliation_history_hash":outputs["reconciliation_history.jsonl"]["hash"]}
    input_hash=sha256_bytes(canonical(input_identity).encode("utf-8")); projection_material=canonical({name:outputs[name]["hash"] for name in CANONICAL_OUTPUTS}).encode("utf-8"); projection_hash=sha256_bytes(projection_material)
    manifest={"record_type":"projection_manifest","projection_version":args.projection_version,"schema_version":args.schema_version,"methodology_version":args.methodology_version,"compiler_commit":args.compiler_commit,"research_head":args.research_head,"reconciliation_head":args.reconciliation_head,"predicate_registry_hash":predicate_registry_hash,"scope_key_registry_hash":scope_key_registry_hash,"input_hash":input_hash,"projection_hash":projection_hash,"outputs":outputs}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8"); print(projection_hash)

if __name__=="__main__": main()
