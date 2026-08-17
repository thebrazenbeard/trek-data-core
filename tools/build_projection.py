#!/usr/bin/env python3
"""Deterministically compile governed Git records into the canonical logical projection."""
from __future__ import annotations
import argparse, contextlib, copy, hashlib, importlib.util, io, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREDICATE_REGISTRY=ROOT/'registry'/'predicates.json'; SCOPE_KEY_REGISTRY=ROOT/'registry'/'scope_keys.json'
DATA_ROOTS=(ROOT/'research',ROOT/'external',ROOT/'migrations')
PROJECTION_STATUSES={'STABLE','CONTESTED','UNRESOLVED','STRUCTURAL_PARADOX'}; DISPOSITIONS={'PROPOSED','ACCEPTED','REJECTED'}
CANONICAL_OUTPUTS=('entities.jsonl','facts.jsonl','relations.jsonl','contested.jsonl','unresolved.jsonl','provenance.jsonl','assertion_history.jsonl','reconciliation_history.jsonl')

def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def sha256_bytes(data):return 'sha256:'+hashlib.sha256(data).hexdigest()
def canonical_json_hash(path):return sha256_bytes(canonical(json.loads(Path(path).read_text(encoding='utf-8'))).encode())
def load_registry(path,key):
 data=json.loads(Path(path).read_text(encoding='utf-8')); return {r[key]:r for r in data.get('predicates' if key=='name' else 'scope_keys',[]) if r.get(key)}
def iter_typed_records(roots):
 for root in roots:
  if not root.exists():continue
  for path in sorted(root.rglob('*.json')):
   if path.name=='README.json':continue
   row=json.loads(path.read_text(encoding='utf-8'))
   if not isinstance(row,dict) or not row.get('record_type'):raise ValueError(f'{path}: governed JSON must be typed object')
   yield row
  for path in sorted(root.rglob('*.jsonl')):
   for line_no,raw in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
    if not raw.strip():continue
    row=json.loads(raw)
    if not isinstance(row,dict) or not row.get('record_type'):raise ValueError(f'{path}:{line_no}: governed JSONL must be typed object')
    yield row
def index_unique(records,record_type,id_key):
 out={}
 for row in records:
  if row.get('record_type')!=record_type:continue
  rid=row.get(id_key)
  if not rid:raise ValueError(f'{record_type} missing {id_key}')
  if rid in out:raise ValueError(f'duplicate {record_type} id {rid}')
  out[rid]=row
 return out
def supersession_active(records,id_key='decision_id'):
 accepted=[r for r in records if r.get('status')=='ACCEPTED']; by_id={r[id_key]:r for r in records if r.get(id_key)}
 for start in by_id:
  seen=set(); cur=start
  while cur:
   if cur in seen:raise ValueError(f'supersession cycle at {cur}')
   seen.add(cur); row=by_id.get(cur); cur=row.get('supersedes') if row else None
 superseded={r.get('supersedes') for r in accepted if r.get('supersedes')}; return [r for r in accepted if r.get(id_key) not in superseded]
def decision_key(d):
 t=d.get('decision_type'); p=d.get('payload') or {}; base=(t,d.get('subject_type'),d.get('subject_id'))
 if t=='ENTITY_LINK':return base+(p.get('relation_predicate'),)
 if t=='SCOPE_RESOLUTION':return base+(p.get('resolution_key'),)
 if t in {'ASSERTION_DISPOSITION','ASSERTION_PROJECTION_STATUS'}:return base
 return None
def validate_decision(d,predicates,scope_keys,indexes):
 t=d.get('decision_type'); p=d.get('payload') or {}; st=d.get('subject_type')
 if t=='OTHER':raise ValueError('accepted OTHER decision is not executable')
 if t=='ENTITY_LINK':
  if st!='LOCAL_ENTITY' or set(p)!={'relation_predicate','target_type','target_id'} or p.get('target_type')!='LOCAL_ENTITY':raise ValueError('invalid ENTITY_LINK payload/domain')
  pred=predicates.get(p.get('relation_predicate'))
  if not pred or 'RECONCILIATION_RELATION' not in set(pred.get('usage_levels',[])) or pred.get('semantic_class')!='IDENTITY_RELATION' or pred.get('status')!='ACCEPTED':raise ValueError(f"ENTITY_LINK predicate {p.get('relation_predicate')} is not accepted RECONCILIATION_RELATION identity semantics")
  if d.get('subject_id') not in indexes['local_entity'] or p.get('target_id') not in indexes['local_entity']:raise ValueError('ENTITY_LINK references missing local entity')
 elif t=='ASSERTION_DISPOSITION':
  if st!='ASSERTION' or set(p)!={'disposition'} or p.get('disposition') not in DISPOSITIONS:raise ValueError('invalid ASSERTION_DISPOSITION')
 elif t=='ASSERTION_PROJECTION_STATUS':
  if st!='ASSERTION' or set(p)!={'projection_status'} or p.get('projection_status') not in PROJECTION_STATUSES:raise ValueError('invalid ASSERTION_PROJECTION_STATUS')
 elif t=='SCOPE_RESOLUTION':
  if st not in {'ASSERTION','WORK','LOCAL_ENTITY'} or set(p)!={'resolution_key','resolution'}:raise ValueError('invalid SCOPE_RESOLUTION')
  entry=scope_keys.get(p.get('resolution_key'))
  if not entry or st not in set(entry.get('subject_types',[])):raise ValueError(f"ungoverned scope key {p.get('resolution_key')} for {st}")
 else:raise ValueError(f'unknown reconciliation decision type {t}')
def active_decision_index(decisions,predicates,scope_keys,indexes):
 out={}
 for d in supersession_active([r for r in decisions if r.get('record_type')=='reconciliation_decision']):
  validate_decision(d,predicates,scope_keys,indexes); key=decision_key(d)
  if key is None:continue
  if key in out:raise ValueError(f'multiple active decisions for {key}')
  out[key]=d
 return out
def typed_ref(v):return (v.get('ref_type'),v.get('ref_id')) if isinstance(v,dict) and set(v)=={'ref_type','ref_id'} else None
def scoped(decisions,subject_type,subject_id):
 return {k[3]:d for k,d in decisions.items() if len(k)==4 and k[0]=='SCOPE_RESOLUTION' and k[1]==subject_type and k[2]==subject_id}
def links(decisions,local_id):return sorted([d for k,d in decisions.items() if len(k)==4 and k[0]=='ENTITY_LINK' and k[1]=='LOCAL_ENTITY' and k[2]==local_id],key=lambda d:(d['payload']['relation_predicate'],d['decision_id']))
def source_lineage(source_id,sources):
 result=[]; seen=set(); stack=[]
 def visit(cur):
  if cur in stack:raise ValueError(f'source derivation cycle at {cur}')
  if cur in seen:return
  row=sources.get(cur)
  if row is None:raise ValueError(f'missing source lineage {cur}')
  seen.add(cur); stack.append(cur)
  for parent in sorted(row.get('derived_from',[])):visit(parent)
  stack.pop()
  if cur!=source_id:result.append(copy.deepcopy(row))
 visit(source_id); return sorted(result,key=lambda r:r['source_id'])
def work_lineage(work_id,works):
 result=[]; seen=set(); row=works.get(work_id)
 while row and row.get('parent_work_id'):
  parent=row['parent_work_id']
  if parent in seen:raise ValueError(f'work parent cycle at {parent}')
  seen.add(parent); row=works.get(parent)
  if row is None:raise ValueError(f'missing parent work {parent}')
  result.append(copy.deepcopy(row))
 return result
def referenced_record(ref_type,ref_id,indexes):
 mapping={'SOURCE':'source','WORK':'work','LOCAL_ENTITY':'local_entity','EVIDENCE':'evidence','ASSERTION':'assertion','RECONCILIATION_DECISION':'reconciliation_decision'}; rt=mapping.get(ref_type); return copy.deepcopy(indexes.get(rt,{}).get(ref_id)) if rt else None
def effective_disposition(assertion,decisions,superseded_assertions):
 aid=assertion['assertion_id']; decision=decisions.get(('ASSERTION_DISPOSITION','ASSERTION',aid)); value=(decision.get('payload') or {}).get('disposition') if decision else assertion.get('status')
 if aid in superseded_assertions:value='SUPERSEDED'
 return value,decision
def projection_status(assertion,decisions):
 aid=assertion['assertion_id']; decision=decisions.get(('ASSERTION_PROJECTION_STATUS','ASSERTION',aid))
 if not decision:return 'UNRESOLVED',None,'MISSING_PROJECTION_STATUS'
 value=decision['payload'].get('projection_status')
 if value not in PROJECTION_STATUSES:raise ValueError(f'invalid projection status for {aid}')
 return value,decision,None
def build_logical_projection(records,reconciliation_decisions):
 records=[copy.deepcopy(r) for r in records]; reconciliation_decisions=[copy.deepcopy(r) for r in reconciliation_decisions]
 indexes={'source':index_unique(records,'source','source_id'),'work':index_unique(records,'work','work_id'),'local_entity':index_unique(records,'local_entity','local_entity_id'),'evidence':index_unique(records,'evidence','evidence_id'),'assertion':index_unique(records,'assertion','assertion_id'),'reconciliation_decision':index_unique(reconciliation_decisions,'reconciliation_decision','decision_id')}
 predicates=load_registry(PREDICATE_REGISTRY,'name'); scope_keys=load_registry(SCOPE_KEY_REGISTRY,'key'); decisions=active_decision_index(reconciliation_decisions,predicates,scope_keys,indexes); assertions=indexes['assertion']; superseded_assertions={a.get('supersedes') for a in assertions.values() if a.get('supersedes')}
 effective={aid:effective_disposition(a,decisions,superseded_assertions) for aid,a in assertions.items()}
 for aid,a in assertions.items():
  if effective[aid][0]=='ACCEPTED':
   pred=predicates.get(a.get('predicate'))
   if not pred or 'RESEARCH_ASSERTION' not in set(pred.get('usage_levels',[])):raise ValueError(f"active assertion {aid} predicate {a.get('predicate')} is not governed for RESEARCH_ASSERTION usage")
 for key,d in decisions.items():
  if key[0]=='ASSERTION_PROJECTION_STATUS' and effective.get(d['subject_id'],(None,None))[0]!='ACCEPTED':raise ValueError(f"projection status targets non-accepted assertion {d['subject_id']}")
 entities=[]; relations=[]
 for lid,entity in sorted(indexes['local_entity'].items()):
  row=copy.deepcopy(entity); ls=links(decisions,lid); sc=scoped(decisions,'LOCAL_ENTITY',lid)
  if ls:
   row['identity_links']=[{**copy.deepcopy(d['payload']),'decision_id':d['decision_id']} for d in ls]
   for d in ls:
    p=d['payload']; relations.append({'record_type':'projection_relation','relation_id':f"reconciliation:{d['decision_id']}",'relation_kind':'IDENTITY_LINK','subject_type':'LOCAL_ENTITY','subject_id':lid,'predicate':p['relation_predicate'],'target_type':p['target_type'],'target_id':p['target_id'],'reconciliation_decision_id':d['decision_id']})
  if sc:row['resolved_scope']={k:copy.deepcopy(d['payload']['resolution']) for k,d in sorted(sc.items())}; row['scope_resolution_decision_ids']={k:d['decision_id'] for k,d in sorted(sc.items())}
  entities.append(row)
 facts=[]; contested=[]; unresolved=[]; provenance=[]
 for aid,a in sorted(assertions.items()):
  eff,disp=effective[aid]
  if eff!='ACCEPTED':continue
  row=copy.deepcopy(a); row['effective_assertion_status']='ACCEPTED'
  if disp:row['assertion_disposition_decision_id']=disp['decision_id']
  status,sdecision,reason=projection_status(a,decisions); row['projection_status']=status
  if sdecision:row['projection_status_decision_id']=sdecision['decision_id']
  if reason:row['projection_reason']=reason
  sc=scoped(decisions,'ASSERTION',aid)
  if sc:row['resolved_scope']={k:copy.deepcopy(d['payload']['resolution']) for k,d in sorted(sc.items())}; row['scope_resolution_decision_ids']={k:d['decision_id'] for k,d in sorted(sc.items())}
  if a.get('subject_type')=='LOCAL_ENTITY':
   ls=links(decisions,a.get('subject'))
   if ls:row['subject_identity_links']=[{**copy.deepcopy(d['payload']),'decision_id':d['decision_id']} for d in ls]
  ssc=scoped(decisions,a.get('subject_type'),a.get('subject'))
  if ssc:row['subject_resolved_scope']={k:copy.deepcopy(d['payload']['resolution']) for k,d in sorted(ssc.items())}; row['subject_scope_resolution_decision_ids']={k:d['decision_id'] for k,d in sorted(ssc.items())}
  (facts if status=='STABLE' else contested if status in {'CONTESTED','STRUCTURAL_PARADOX'} else unresolved).append(row)
  ref=typed_ref(a.get('object'))
  if ref:
   relations.append({'record_type':'projection_relation','relation_id':f'assertion:{aid}','relation_kind':'ASSERTION_PREDICATE','assertion_id':aid,'subject_type':a.get('subject_type'),'subject_id':a.get('subject'),'predicate':a.get('predicate'),'target_type':ref[0],'target_id':ref[1],'projection_status':status})
 for aid,a in sorted(assertions.items()):
  eff,disp=effective[aid]; status=sdecision=reason=None
  if eff=='ACCEPTED':status,sdecision,reason=projection_status(a,decisions)
  sc=scoped(decisions,'ASSERTION',aid); ls=links(decisions,a.get('subject')) if a.get('subject_type')=='LOCAL_ENTITY' else []
  for evidence_id in sorted(a.get('evidence',[])):
   ev=indexes['evidence'].get(evidence_id)
   if ev is None:raise ValueError(f'assertion {aid} references missing evidence {evidence_id}')
   source=indexes['source'].get(ev.get('source_id')); work=indexes['work'].get(ev.get('work_id'))
   if source is None or work is None:raise ValueError(f'evidence {evidence_id} has missing source/work')
   prow={'record_type':'projection_provenance','provenance_id':f'{aid}::{evidence_id}','assertion_id':aid,'evidence_id':evidence_id,'assertion_record':copy.deepcopy(a),'effective_assertion_status':eff,'support_set':sorted(a.get('evidence',[])),'evidence_record':copy.deepcopy(ev),'source_record':copy.deepcopy(source),'source_lineage_records':source_lineage(source['source_id'],indexes['source']),'work_record':copy.deepcopy(work),'work_lineage_records':work_lineage(work['work_id'],indexes['work'])}
   if disp:prow['assertion_disposition_decision_id']=disp['decision_id']
   if status:prow['projection_status']=status
   if sdecision:prow['projection_status_decision_id']=sdecision['decision_id']
   if reason:prow['projection_reason']=reason
   if sc:prow['scope_resolution_decision_ids']={k:d['decision_id'] for k,d in sorted(sc.items())}
   if ls:prow['entity_link_decision_ids']=[d['decision_id'] for d in ls]
   observer=ev.get('observer_local_entity_id')
   if observer:
    record=indexes['local_entity'].get(observer)
    if record:prow['observer_local_entity_record']=copy.deepcopy(record)
   subject_record=referenced_record(a.get('subject_type'),a.get('subject'),indexes)
   if subject_record:prow['subject_record']=subject_record
   ref=typed_ref(a.get('object'))
   if ref:
    obj=referenced_record(ref[0],ref[1],indexes)
    if obj:prow['object_record']=obj
   provenance.append(prow)
 history=sorted([copy.deepcopy(a) for a in assertions.values()],key=lambda r:r['assertion_id']); recon_history=sorted([copy.deepcopy(d) for d in reconciliation_decisions if d.get('record_type')=='reconciliation_decision' and d.get('status') in {'ACCEPTED','SUPERSEDED'}],key=lambda r:r['decision_id'])
 return {'entities':sorted(entities,key=lambda r:r['local_entity_id']),'facts':sorted(facts,key=lambda r:r['assertion_id']),'relations':sorted(relations,key=lambda r:r['relation_id']),'contested':sorted(contested,key=lambda r:r['assertion_id']),'unresolved':sorted(unresolved,key=lambda r:r['assertion_id']),'provenance':sorted(provenance,key=lambda r:r['provenance_id']),'assertion_history':history,'reconciliation_history':recon_history}
def write_jsonl(path,rows,id_key):
 ordered=sorted(rows,key=lambda r:(str(r.get(id_key,'')),canonical(r))); payload=''.join(canonical(r)+'\n' for r in ordered).encode(); path.write_bytes(payload); return sha256_bytes(payload),len(ordered)
def run_repository_validation():
 path=Path(__file__).with_name('validate.py'); spec=importlib.util.spec_from_file_location('trek_validate_before_build',path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); output=io.StringIO()
 with contextlib.redirect_stdout(output):rc=module.main()
 if rc:raise ValueError('repository admission validation failed before projection build: '+output.getvalue())
def verify_written_bundle(out):
 path=Path(__file__).with_name('projection_bundle.py'); spec=importlib.util.spec_from_file_location('trek_projection_bundle_compiler',path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); module.verify_projection(out)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); ap.add_argument('--projection-version',default='0.2.0'); ap.add_argument('--schema-version',required=True); ap.add_argument('--methodology-version',required=True); ap.add_argument('--research-head',required=True); ap.add_argument('--reconciliation-head',required=True); ap.add_argument('--compiler-commit',required=True); args=ap.parse_args(); run_repository_validation(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
 records=list(iter_typed_records(DATA_ROOTS)); decisions=list(iter_typed_records((ROOT/'reconciliation',))); logical=build_logical_projection(records,decisions); specs={'entities.jsonl':(logical['entities'],'local_entity_id'),'facts.jsonl':(logical['facts'],'assertion_id'),'relations.jsonl':(logical['relations'],'relation_id'),'contested.jsonl':(logical['contested'],'assertion_id'),'unresolved.jsonl':(logical['unresolved'],'assertion_id'),'provenance.jsonl':(logical['provenance'],'provenance_id'),'assertion_history.jsonl':(logical['assertion_history'],'assertion_id'),'reconciliation_history.jsonl':(logical['reconciliation_history'],'decision_id')}; outputs={}
 for name,(rows,key) in specs.items():h,count=write_jsonl(out/name,rows,key); outputs[name]={'role':name.removesuffix('.jsonl'),'hash':h,'count':count}
 predicate_hash=canonical_json_hash(PREDICATE_REGISTRY); scope_hash=canonical_json_hash(SCOPE_KEY_REGISTRY); logical_input=[r for r in records if r.get('record_type') in {'source','work','local_entity','evidence','assertion'}]; logical_input_hash=sha256_bytes(''.join(canonical(r)+'\n' for r in sorted(logical_input,key=canonical)).encode()); input_identity={'research_head':args.research_head,'reconciliation_head':args.reconciliation_head,'schema_version':args.schema_version,'methodology_version':args.methodology_version,'predicate_registry_hash':predicate_hash,'scope_key_registry_hash':scope_hash,'compiler_commit':args.compiler_commit,'logical_input_records_hash':logical_input_hash,'reconciliation_history_hash':outputs['reconciliation_history.jsonl']['hash']}; input_hash=sha256_bytes(canonical(input_identity).encode()); projection_hash=sha256_bytes(canonical({n:outputs[n]['hash'] for n in CANONICAL_OUTPUTS}).encode()); manifest={'record_type':'projection_manifest','projection_version':args.projection_version,'schema_version':args.schema_version,'methodology_version':args.methodology_version,'compiler_commit':args.compiler_commit,'research_head':args.research_head,'reconciliation_head':args.reconciliation_head,'predicate_registry_hash':predicate_hash,'scope_key_registry_hash':scope_hash,'input_hash':input_hash,'projection_hash':projection_hash,'outputs':outputs}; (out/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8'); verify_written_bundle(out); print(projection_hash)
if __name__=='__main__':main()
