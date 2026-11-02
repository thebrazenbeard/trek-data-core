#!/usr/bin/env python3
"""Deterministically diff canonical logical projections without semantic guessing."""
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path

ASSERTION_FILES=("facts.jsonl","contested.jsonl","unresolved.jsonl")
NONSTABLE={"CONTESTED","UNRESOLVED","STRUCTURAL_PARADOX"}
ASSERTION_DERIVED={
 "effective_assertion_status","assertion_disposition_decision_id","projection_status","projection_status_decision_id","projection_reason",
 "resolved_scope","scope_resolution_decision_ids","subject_identity_links","subject_resolved_scope","subject_scope_resolution_decision_ids",
}
ENTITY_DERIVED={"identity_links","resolved_scope","scope_resolution_decision_ids"}

def canonical(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def digest(v): return "sha256:"+hashlib.sha256(canonical(v).encode()).hexdigest()
def load_rows(path):
 path=Path(path)
 if not path.exists(): return []
 return [json.loads(raw) for raw in path.read_text(encoding="utf-8").splitlines() if raw.strip()]
def load_index(path,key):
 result={}
 for row in load_rows(path):
  rid=row.get(key)
  if not rid: raise ValueError(f"{path}: row missing {key}")
  if rid in result: raise ValueError(f"{path}: duplicate {key} {rid}")
  result[rid]=row
 return result
def load_manifest(root):
 path=Path(root)/"manifest.json"
 return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
def comparison_context(old_root,new_root):
 old=load_manifest(old_root); new=load_manifest(new_root)
 if not old and not new:return None
 keys=("projection_hash","input_hash","schema_version","methodology_version","compiler_commit","research_head","reconciliation_head","predicate_registry_hash","scope_key_registry_hash")
 return {"old":{k:old.get(k) for k in keys if old and k in old},"new":{k:new.get(k) for k in keys if new and k in new}}
def event(cls,record_type,record_id,comparison=None,**details):
 row={"class":cls,"record_type":record_type,"record_id":record_id}
 if details: row["details"]=details
 if comparison: row["comparison"]=copy.deepcopy(comparison)
 return row
def load_active_assertions(root):
 result={}
 for filename in ASSERTION_FILES:
  for aid,row in load_index(Path(root)/filename,"assertion_id").items():
   if aid in result: raise ValueError(f"{root}: assertion {aid} appears in multiple active partitions")
   result[aid]=row
 return result
def invariant_view(row,derived): return {k:copy.deepcopy(v) for k,v in row.items() if k not in derived}
def proposition_key(row): return (row.get("subject_type"),row.get("subject"),row.get("predicate"))
def history_index(root): return load_index(Path(root)/"assertion_history.jsonl","assertion_id")
def reconciliation_index(root):
 primary=Path(root)/"reconciliation_history.jsonl"; legacy=Path(root)/"accepted_reconciliation.jsonl"
 return load_index(primary if primary.exists() else legacy,"decision_id")
def grouped_provenance(root):
 result={}
 for row in load_rows(Path(root)/"provenance.jsonl"):
  aid=row.get("assertion_id")
  if not aid: raise ValueError(f"{root}: provenance row missing assertion_id")
  result.setdefault(aid,[]).append(row)
 return {aid:sorted(rows,key=canonical) for aid,rows in result.items()}
def scope_events(changes,record_type,record_id,old_scope,new_scope,comparison):
 old_scope=old_scope or {}; new_scope=new_scope or {}
 if not isinstance(old_scope,dict) or not isinstance(new_scope,dict): raise ValueError(f"{record_type} {record_id}: resolved_scope must be object")
 for key in sorted(set(old_scope)|set(new_scope)):
  if canonical(old_scope.get(key))!=canonical(new_scope.get(key)):
   changes.append(event("SCOPE_CHANGED",record_type,record_id,comparison,resolution_key=key,old_resolution=old_scope.get(key),new_resolution=new_scope.get(key)))
def status_events(changes,record_id,old_status,new_status,comparison):
 if old_status==new_status:return
 if old_status=="STABLE" and new_status in NONSTABLE:
  changes.append(event("STATUS_DEMOTED","assertion",record_id,comparison,old_status=old_status,new_status=new_status)); return
 if old_status in NONSTABLE and new_status=="STABLE":
  changes.append(event("STATUS_PROMOTED","assertion",record_id,comparison,old_status=old_status,new_status=new_status)); return
 if old_status in NONSTABLE and new_status in NONSTABLE:
  changes.append(event("PROVISIONAL_STATUS_CHANGED","assertion",record_id,comparison,provisional_taxonomy_version="director-67-proposed",old_status=old_status,new_status=new_status)); return
 raise ValueError(f"unsupported projection-status transition {old_status!r}->{new_status!r} for {record_id}")
def assertion_pairs(old_active,new_active,new_history):
 pairs={aid:aid for aid in sorted(set(old_active)&set(new_active))}; used_old=set(pairs); used_new=set(pairs)
 for new_id in sorted(set(new_active)-used_new):
  row=new_history.get(new_id,new_active[new_id]); predecessor=row.get("supersedes")
  if predecessor and predecessor in old_active and predecessor not in used_old and predecessor not in new_active:
   if proposition_key(old_active[predecessor])!=proposition_key(new_active[new_id]):
    raise ValueError(f"unsupported proposition-key change across explicit supersession {predecessor}->{new_id}")
   pairs[predecessor]=new_id; used_old.add(predecessor); used_new.add(new_id)
 return pairs,used_old,used_new
def normalized_provenance(rows,old_id,new_id):
 normalized=[]
 for row in rows:
  item=copy.deepcopy(row)
  if old_id!=new_id:
   item.pop("provenance_id",None); item.pop("assertion_id",None)
  normalized.append(item)
 return sorted(normalized,key=canonical)
def decision_ids(value):
 found=set()
 def walk(v,key=None):
  if isinstance(v,dict):
   for k,x in v.items():
    if k.endswith("decision_id") and isinstance(x,str): found.add(x)
    elif k.endswith("decision_ids"):
     if isinstance(x,list): found.update(i for i in x if isinstance(i,str))
     elif isinstance(x,dict): found.update(i for i in x.values() if isinstance(i,str))
    walk(x,k)
  elif isinstance(v,list):
   for x in v: walk(x,key)
 walk(value); return found

def semantic_diff(old_root,new_root):
 old_root=Path(old_root); new_root=Path(new_root); comparison=comparison_context(old_root,new_root); changes=[]
 old_active=load_active_assertions(old_root); new_active=load_active_assertions(new_root); old_hist=history_index(old_root); new_hist=history_index(new_root)
 pairs,used_old,used_new=assertion_pairs(old_active,new_active,new_hist)
 for aid in sorted(set(old_active)-used_old): changes.append(event("REMOVED_FACT","assertion",aid,comparison,old_hash=digest(old_active[aid])))
 for aid in sorted(set(new_active)-used_new): changes.append(event("ADDED_FACT","assertion",aid,comparison,new_hash=digest(new_active[aid])))
 for old_id,new_id in sorted(pairs.items()):
  old=old_active[old_id]; new=new_active[new_id]
  if old_id==new_id:
   if canonical(invariant_view(old,ASSERTION_DERIVED))!=canonical(invariant_view(new,ASSERTION_DERIVED)):
    raise ValueError(f"immutable assertion {old_id} changed under the same assertion_id")
  else:
   if old.get("object")!=new.get("object"):
    changes.append(event("VALUE_CHANGED","assertion",f"{old_id}->{new_id}",comparison,old_assertion_id=old_id,new_assertion_id=new_id,old_value=old.get("object"),new_value=new.get("object"),old_hash=digest(old),new_hash=digest(new)))
  status_events(changes,f"{old_id}->{new_id}" if old_id!=new_id else old_id,old.get("projection_status"),new.get("projection_status"),comparison)
  scope_events(changes,"assertion",f"{old_id}->{new_id}" if old_id!=new_id else old_id,old.get("resolved_scope"),new.get("resolved_scope"),comparison)
  if canonical(old.get("subject_identity_links",[]))!=canonical(new.get("subject_identity_links",[])):
   changes.append(event("ENTITY_LINK_CHANGED","assertion",f"{old_id}->{new_id}" if old_id!=new_id else old_id,comparison,old_links=old.get("subject_identity_links",[]),new_links=new.get("subject_identity_links",[])))
 old_prov=grouped_provenance(old_root); new_prov=grouped_provenance(new_root)
 for old_id,new_id in sorted(pairs.items()):
  old_rows=normalized_provenance(old_prov.get(old_id,[]),old_id,new_id); new_rows=normalized_provenance(new_prov.get(new_id,[]),old_id,new_id)
  if canonical(old_rows)!=canonical(new_rows):
   changes.append(event("PROVENANCE_CHANGED","assertion",f"{old_id}->{new_id}" if old_id!=new_id else old_id,comparison,old_provenance_hash=digest(old_rows),new_provenance_hash=digest(new_rows)))

 old_entities=load_index(old_root/"entities.jsonl","local_entity_id"); new_entities=load_index(new_root/"entities.jsonl","local_entity_id")
 for eid in sorted(set(new_entities)-set(old_entities)): changes.append(event("PROVISIONAL_ENTITY_ADDED","local_entity",eid,comparison,provisional_taxonomy_version="director-67-proposed",new_hash=digest(new_entities[eid])))
 for eid in sorted(set(old_entities)-set(new_entities)): changes.append(event("PROVISIONAL_ENTITY_REMOVED","local_entity",eid,comparison,provisional_taxonomy_version="director-67-proposed",old_hash=digest(old_entities[eid])))
 for eid in sorted(set(old_entities)&set(new_entities)):
  old=old_entities[eid]; new=new_entities[eid]
  if canonical(invariant_view(old,ENTITY_DERIVED))!=canonical(invariant_view(new,ENTITY_DERIVED)): raise ValueError(f"immutable local entity {eid} changed under the same local_entity_id")
  if canonical(old.get("identity_links",[]))!=canonical(new.get("identity_links",[])): changes.append(event("ENTITY_LINK_CHANGED","local_entity",eid,comparison,old_links=old.get("identity_links",[]),new_links=new.get("identity_links",[])))
  scope_events(changes,"local_entity",eid,old.get("resolved_scope"),new.get("resolved_scope"),comparison)

 old_rel=load_index(old_root/"relations.jsonl","relation_id"); new_rel=load_index(new_root/"relations.jsonl","relation_id")
 old_identity=[r for r in old_rel.values() if r.get("relation_kind")=="IDENTITY_LINK"]; new_identity=[r for r in new_rel.values() if r.get("relation_kind")=="IDENTITY_LINK"]
 def identity_groups(rows):
  result={}
  for r in rows: result.setdefault((r.get("subject_type"),r.get("subject_id")),[]).append(r)
  return {k:sorted(v,key=canonical) for k,v in result.items()}
 old_ig=identity_groups(old_identity); new_ig=identity_groups(new_identity)
 for key in sorted(set(old_ig)|set(new_ig),key=repr):
  if canonical(old_ig.get(key,[]))!=canonical(new_ig.get(key,[])): changes.append(event("ENTITY_LINK_CHANGED","identity_subject",f"{key[0]}:{key[1]}",comparison,old_links=old_ig.get(key,[]),new_links=new_ig.get(key,[])))
 for rid in sorted(set(new_rel)-set(old_rel)):
  row=new_rel[rid]; changes.append(event("PROVISIONAL_RELATION_ADDED","relation",rid,comparison,provisional_taxonomy_version="director-67-proposed",new_hash=digest(row)))
  if row.get("predicate")=="CONTRADICTS": changes.append(event("CONFLICT_INTRODUCED","relation",rid,comparison,conflict_basis=copy.deepcopy(row)))
 for rid in sorted(set(old_rel)-set(new_rel)):
  row=old_rel[rid]; changes.append(event("PROVISIONAL_RELATION_REMOVED","relation",rid,comparison,provisional_taxonomy_version="director-67-proposed",old_hash=digest(row)))
  if row.get("predicate")=="CONTRADICTS": changes.append(event("CONFLICT_RESOLVED","relation",rid,comparison,conflict_basis=copy.deepcopy(row)))
 for rid in sorted(set(old_rel)&set(new_rel)):
  old=old_rel[rid]; new=new_rel[rid]
  if canonical(old)!=canonical(new):
   changes.append(event("PROVISIONAL_RELATION_CHANGED","relation",rid,comparison,provisional_taxonomy_version="director-67-proposed",old_hash=digest(old),new_hash=digest(new)))
   if old.get("relation_kind")=="IDENTITY_LINK" or new.get("relation_kind")=="IDENTITY_LINK": changes.append(event("ENTITY_LINK_CHANGED","relation",rid,comparison,old_relation=old,new_relation=new))
   if old.get("predicate")!="CONTRADICTS" and new.get("predicate")=="CONTRADICTS": changes.append(event("CONFLICT_INTRODUCED","relation",rid,comparison,conflict_basis=new))
   if old.get("predicate")=="CONTRADICTS" and new.get("predicate")!="CONTRADICTS": changes.append(event("CONFLICT_RESOLVED","relation",rid,comparison,conflict_basis=old))

 old_recon=reconciliation_index(old_root); new_recon=reconciliation_index(new_root); used_decisions=set()
 for row in list(old_active.values())+list(new_active.values())+list(old_entities.values())+list(new_entities.values())+list(old_rel.values())+list(new_rel.values()): used_decisions.update(decision_ids(row))
 for did in sorted(set(new_recon)-set(old_recon)):
  if did not in used_decisions: changes.append(event("PROVISIONAL_RECONCILIATION_HISTORY_CHANGED","reconciliation_decision",did,comparison,provisional_taxonomy_version="director-67-proposed",operation="ADDED_HISTORY",new_hash=digest(new_recon[did])))
 for did in sorted(set(old_recon)-set(new_recon)):
  if did not in used_decisions: changes.append(event("PROVISIONAL_RECONCILIATION_HISTORY_CHANGED","reconciliation_decision",did,comparison,provisional_taxonomy_version="director-67-proposed",operation="REMOVED_HISTORY",old_hash=digest(old_recon[did])))
 for did in sorted(set(old_recon)&set(new_recon)):
  if canonical(old_recon[did])!=canonical(new_recon[did]): raise ValueError(f"immutable reconciliation decision {did} changed under the same decision_id")

 changes=sorted(changes,key=lambda r:(r["record_type"],r["record_id"],r["class"],canonical(r.get("details",{}))))
 old_manifest=load_manifest(old_root); new_manifest=load_manifest(new_root)
 if old_manifest and new_manifest:
  old_hash=old_manifest.get("projection_hash"); new_hash=new_manifest.get("projection_hash")
  if old_hash==new_hash and changes: raise ValueError("identical projection_hash values produced semantic changes")
  if old_hash!=new_hash and not changes: raise ValueError("projection_hash changed but semantic diff produced no events")
 return changes

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("old"); ap.add_argument("new"); args=ap.parse_args(); changes=semantic_diff(Path(args.old),Path(args.new))
 for row in changes: print(canonical(row))
 print(f"changes={len(changes)}")
if __name__=="__main__": main()
