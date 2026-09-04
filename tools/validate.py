#!/usr/bin/env python3
"""Deterministic repository admission validation with no network dependencies."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA_ROOTS=[ROOT/'research',ROOT/'reconciliation',ROOT/'external',ROOT/'migrations']
SCHEMA_ROOT=ROOT/'schema'; PREDICATE_REGISTRY=ROOT/'registry'/'predicates.json'; SCOPE_KEY_REGISTRY=ROOT/'registry'/'scope_keys.json'
SCHEMA_FILES={'source':'source.schema.json','work':'work.schema.json','local_entity':'local-entity.schema.json','evidence':'evidence.schema.json','assertion':'assertion.schema.json','batch_manifest':'batch-manifest.schema.json','reconciliation_decision':'reconciliation-decision.schema.json'}
ID_FIELDS={'source':'source_id','work':'work_id','local_entity':'local_entity_id','evidence':'evidence_id','assertion':'assertion_id','batch_manifest':'batch_id','reconciliation_decision':'decision_id'}
REFERENCE_TYPES={'SOURCE':'source','WORK':'work','LOCAL_ENTITY':'local_entity','EVIDENCE':'evidence','ASSERTION':'assertion','RECONCILIATION_DECISION':'reconciliation_decision'}
COUNT_KEYS={'sources':'source','works':'work','local_entities':'local_entity','evidence':'evidence','assertions':'assertion','reconciliation_decisions':'reconciliation_decision'}
REQUIRED_BATCH_COUNTS=('local_entities','evidence','assertions'); WORKER_FORBIDDEN_RECORD_TYPES={'source','work','reconciliation_decision'}
PROJECTION_STATUSES={'STABLE','CONTESTED','UNRESOLVED','STRUCTURAL_PARADOX'}; DISPOSITIONS={'PROPOSED','ACCEPTED','REJECTED'}
USAGE_LEVELS={'RESEARCH_ASSERTION','RECONCILIATION_RELATION','EXTERNAL_CROSSWALK','EVIDENCE_ANNOTATION'}
PREDICATE_METADATA_REQUIRED={'name','status','definition','semantic_class','usage_levels','subject_types','object_mode','object_ref_types','symmetry','inverse','transitive','projection_eligibility','examples','near_miss','supersedes','superseded_by','methodology_version','introduced_in_registry'}
RESEARCH_WORKERS={'tos':'TOS','tas':'TAS','tng':'TNG','ds9':'DS9','voyager':'VOY','enterprise':'ENT','discovery':'DIS','short-treks':'SHORT','picard':'PIC','lower-decks':'LD','prodigy':'PRO','strange-new-worlds':'SNW','starfleet-academy':'SFA','films':'FILMS','literature':'LIT'}

def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def sha256_canonical(v):return 'sha256:'+hashlib.sha256(canonical(v).encode()).hexdigest()
def physical_path(path):
 m=re.match(r'^(.*\.jsonl):\d+$',str(path)); return Path(m.group(1)) if m else Path(path)
def iter_records():
 for base in DATA_ROOTS:
  if not base.exists():continue
  for path in sorted(base.rglob('*.json')):
   if path.name=='README.json':continue
   try:row=json.loads(path.read_text(encoding='utf-8'))
   except Exception as exc:raise ValueError(f'{path}: invalid JSON: {exc}') from exc
   if not isinstance(row,dict):raise ValueError(f'{path}: governed JSON artifact must be an object record')
   yield path,row
  for path in sorted(base.rglob('*.jsonl')):
   for line_no,raw in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
    if not raw.strip():continue
    try:row=json.loads(raw)
    except Exception as exc:raise ValueError(f'{path}:{line_no}: invalid JSONL: {exc}') from exc
    if not isinstance(row,dict):raise ValueError(f'{path}:{line_no}: record must be an object')
    yield Path(f'{path}:{line_no}'),row
def load_schemas():return {rt:json.loads((SCHEMA_ROOT/fn).read_text(encoding='utf-8')) for rt,fn in SCHEMA_FILES.items()}
def load_predicate_registry():
 registry=json.loads(PREDICATE_REGISTRY.read_text(encoding='utf-8')); entries={}; errors=[]
 if not registry.get('registry_version'):errors.append('predicate registry missing registry_version')
 if not registry.get('schema_version'):errors.append('predicate registry missing schema_version')
 for item in registry.get('predicates',[]):
  name=item.get('name'); missing=sorted(PREDICATE_METADATA_REQUIRED-set(item))
  if not name:errors.append('predicate registry entry missing name');continue
  if name in entries:errors.append(f'duplicate predicate registry entry {name}');continue
  if missing:errors.append(f"predicate {name} missing metadata: {', '.join(missing)}")
  if item.get('status') not in {'CANDIDATE','EXPERIMENTAL','ACCEPTED','DEPRECATED'}:errors.append(f"predicate {name} has invalid lifecycle status {item.get('status')!r}")
  if item.get('object_mode') not in {'LITERAL','REFERENCE_ONLY','LITERAL_OR_REFERENCE'}:errors.append(f"predicate {name} has invalid object_mode {item.get('object_mode')!r}")
  levels=item.get('usage_levels')
  if not isinstance(levels,list) or not levels:errors.append(f'predicate {name} requires non-empty usage_levels')
  elif len(levels)!=len(set(levels)) or any(level not in USAGE_LEVELS for level in levels):errors.append(f'predicate {name} has invalid usage_levels {levels!r}')
  if not isinstance(item.get('subject_types'),list) or not item.get('subject_types'):errors.append(f'predicate {name} requires subject_types')
  if not isinstance(item.get('object_ref_types'),list):errors.append(f'predicate {name} requires object_ref_types array')
  if not isinstance(item.get('examples'),list) or not item.get('examples'):errors.append(f'predicate {name} requires a positive example')
  if not isinstance(item.get('near_miss'),str) or not item.get('near_miss','').strip():errors.append(f'predicate {name} requires near_miss')
  if not item.get('methodology_version') or not item.get('introduced_in_registry'):errors.append(f'predicate {name} requires methodology/registry provenance')
  if item.get('status')=='ACCEPTED':
   if 'RESEARCH_ASSERTION' in set(levels or []) and item.get('projection_eligibility')!='ACCEPTED_ASSERTION_ALLOWED':errors.append(f'accepted research predicate {name} must declare ACCEPTED_ASSERTION_ALLOWED')
   if 'RESEARCH_ASSERTION' not in set(levels or []) and item.get('projection_eligibility') not in {'CONTEXT_ONLY','ACCEPTED_ASSERTION_ALLOWED'}:errors.append(f'accepted non-research predicate {name} requires context-governed projection eligibility')
  if item.get('status')=='EXPERIMENTAL' and item.get('projection_eligibility')!='EXPERIMENTAL_ONLY':errors.append(f'experimental predicate {name} must declare EXPERIMENTAL_ONLY')
  entries[name]=item
 for name,item in entries.items():
  for field in ('inverse','supersedes','superseded_by'):
   target=item.get(field)
   if target and target not in entries:errors.append(f'predicate {name} {field} references unknown predicate {target}')
 return entries,errors
def load_scope_key_registry():
 registry=json.loads(SCOPE_KEY_REGISTRY.read_text(encoding='utf-8')); entries={}; errors=[]
 if not registry.get('registry_version'):errors.append('scope-key registry missing registry_version')
 if not registry.get('methodology_version'):errors.append('scope-key registry missing methodology_version')
 for item in registry.get('scope_keys',[]):
  key=item.get('key')
  if not isinstance(key,str) or not key.strip():errors.append('scope-key entry missing key');continue
  if key in entries:errors.append(f'duplicate scope key {key}');continue
  types=item.get('subject_types')
  if not isinstance(types,list) or not types:errors.append(f'scope key {key} requires subject_types')
  elif any(t not in {'WORK','LOCAL_ENTITY','ASSERTION'} for t in types):errors.append(f'scope key {key} has unsupported subject type')
  if not isinstance(item.get('definition'),str) or not item.get('definition','').strip():errors.append(f'scope key {key} requires definition')
  entries[key]=item
 return entries,errors
def type_matches(value,expected):
 if expected=='null':return value is None
 if expected=='object':return isinstance(value,dict)
 if expected=='array':return isinstance(value,list)
 if expected=='string':return isinstance(value,str)
 if expected=='boolean':return isinstance(value,bool)
 if expected=='integer':return isinstance(value,int) and not isinstance(value,bool)
 if expected=='number':return isinstance(value,(int,float)) and not isinstance(value,bool)
 return True
def schema_errors(value,schema,location='$'):
 errors=[]; expected=schema.get('type')
 if expected is not None:
  allowed=expected if isinstance(expected,list) else [expected]
  if not any(type_matches(value,t) for t in allowed):return [f'{location}: expected type {allowed}, got {type(value).__name__}']
 if 'const' in schema and value!=schema['const']:errors.append(f"{location}: expected constant {schema['const']!r}, got {value!r}")
 if 'enum' in schema and value not in schema['enum']:errors.append(f"{location}: value {value!r} is not in enum {schema['enum']!r}")
 if isinstance(value,str) and len(value)<schema.get('minLength',0):errors.append(f"{location}: string shorter than minLength {schema['minLength']}")
 if isinstance(value,list):
  if len(value)<schema.get('minItems',0):errors.append(f"{location}: array shorter than minItems {schema['minItems']}")
  if 'items' in schema:
   for i,item in enumerate(value):errors.extend(schema_errors(item,schema['items'],f'{location}[{i}]'))
 if isinstance(value,dict):
  for req in schema.get('required',[]):
   if req not in value:errors.append(f'{location}: missing required property {req}')
  props=schema.get('properties',{})
  for key,item in value.items():
   if key in props:errors.extend(schema_errors(item,props[key],f'{location}.{key}'))
   elif schema.get('additionalProperties') is False:errors.append(f'{location}: unexpected property {key}')
 return errors
def add_missing_reference(errors,path,field,target_type,target_id,index):
 rt=REFERENCE_TYPES.get(target_type,target_type.lower() if isinstance(target_type,str) else None)
 if rt and target_id and target_id not in index.get(rt,{}):errors.append(f'{path}: {field} references missing {target_type} {target_id}')
def typed_ref(value):
 if not isinstance(value,dict):return None
 if 'ref_type' not in value and 'ref_id' not in value:return None
 return value.get('ref_type'),value.get('ref_id')
def validate_predicate_assertion(path,assertion,registry,index,errors):
 name=assertion.get('predicate'); entry=registry.get(name)
 if entry is None:errors.append(f"{path}: assertion {assertion.get('assertion_id')} uses unregistered predicate {name}");return
 if 'RESEARCH_ASSERTION' not in set(entry.get('usage_levels',[])):errors.append(f'{path}: predicate {name} does not allow RESEARCH_ASSERTION usage')
 lifecycle=entry.get('status'); record_status=assertion.get('status')
 if lifecycle=='CANDIDATE':errors.append(f'{path}: candidate predicate {name} may not be used in research records')
 elif lifecycle=='EXPERIMENTAL' and record_status!='PROPOSED':errors.append(f'{path}: experimental predicate {name} may only be used on PROPOSED assertions')
 elif lifecycle=='DEPRECATED':errors.append(f'{path}: deprecated predicate {name} may not be used for new assertion admission')
 if record_status=='ACCEPTED' and 'RESEARCH_ASSERTION' in set(entry.get('usage_levels',[])) and entry.get('projection_eligibility')!='ACCEPTED_ASSERTION_ALLOWED':errors.append(f'{path}: predicate {name} is not eligible for accepted assertion projection')
 subject_type=assertion.get('subject_type'); allowed=set(entry.get('subject_types',[]))
 if 'ANY' not in allowed and subject_type not in allowed:errors.append(f'{path}: predicate {name} does not allow subject_type {subject_type}')
 obj=assertion.get('object'); ref=typed_ref(obj); mode=entry.get('object_mode')
 if isinstance(obj,dict) and ('ref_type' in obj or 'ref_id' in obj) and set(obj)!={'ref_type','ref_id'}:errors.append(f'{path}: typed assertion object may contain only ref_type and ref_id')
 if mode=='REFERENCE_ONLY' and ref is None:errors.append(f'{path}: predicate {name} requires a typed object reference')
 if mode=='LITERAL' and ref is not None:errors.append(f'{path}: predicate {name} requires a literal object')
 if ref is not None:
  ref_type,ref_id=ref
  if not ref_type or not ref_id:errors.append(f'{path}: typed assertion object requires both ref_type and ref_id')
  elif ref_type not in REFERENCE_TYPES:errors.append(f'{path}: typed assertion object has unsupported ref_type {ref_type}')
  else:
   if ref_type not in set(entry.get('object_ref_types',[])):errors.append(f'{path}: predicate {name} does not allow object ref_type {ref_type}')
   add_missing_reference(errors,path,'object',ref_type,ref_id,index)
def validate_assertion_references(path,a,index,errors):
 st=a.get('subject_type');sid=a.get('subject')
 if st in REFERENCE_TYPES:add_missing_reference(errors,path,'subject',st,sid,index)
 evidence=a.get('evidence',[])
 if len(evidence)!=len(set(evidence)):errors.append(f'{path}: assertion evidence support set contains duplicates')
 for eid in evidence:add_missing_reference(errors,path,'evidence','EVIDENCE',eid,index)
 if a.get('supersedes'):add_missing_reference(errors,path,'supersedes','ASSERTION',a['supersedes'],index)
def validate_references(records,index,errors):
 for path,row in records:
  rt=row.get('record_type')
  if rt=='source':
   for sid in row.get('derived_from',[]):add_missing_reference(errors,path,'derived_from','SOURCE',sid,index)
  elif rt=='work' and row.get('parent_work_id'):add_missing_reference(errors,path,'parent_work_id','WORK',row['parent_work_id'],index)
  elif rt=='local_entity':add_missing_reference(errors,path,'work_id','WORK',row.get('work_id'),index)
  elif rt=='evidence':
   add_missing_reference(errors,path,'source_id','SOURCE',row.get('source_id'),index);add_missing_reference(errors,path,'work_id','WORK',row.get('work_id'),index)
   if row.get('observer_local_entity_id'):add_missing_reference(errors,path,'observer_local_entity_id','LOCAL_ENTITY',row['observer_local_entity_id'],index)
  elif rt=='assertion':validate_assertion_references(path,row,index,errors)
  elif rt=='reconciliation_decision':
   for eid in row.get('evidence',[]):
    if eid not in index.get('evidence',{}) and eid not in index.get('assertion',{}):errors.append(f'{path}: evidence references missing EVIDENCE/ASSERTION {eid}')
   if row.get('supersedes'):add_missing_reference(errors,path,'supersedes','RECONCILIATION_DECISION',row['supersedes'],index)
   if row.get('subject_type') in REFERENCE_TYPES:add_missing_reference(errors,path,'subject',row['subject_type'],row.get('subject_id'),index)
def batch_records_for(manifest_path,records):
 root=physical_path(manifest_path).parent;selected=[]
 for path,row in records:
  if row.get('record_type')=='batch_manifest':continue
  try:physical_path(path).relative_to(root)
  except ValueError:continue
  selected.append(row)
 return sorted(selected,key=canonical)
def compute_batch_hash(manifest,batch_records):return sha256_canonical({'manifest':{k:v for k,v in manifest.items() if k!='batch_hash'},'records':batch_records})
def research_lane_for_path(path):
 physical=physical_path(path)
 for root in DATA_ROOTS:
  if root.name!='research':continue
  try:rel=physical.relative_to(root)
  except ValueError:continue
  if rel.parts and rel.parts[0] in RESEARCH_WORKERS:return rel.parts[0]
 return None
def validate_partition_ownership(records,errors):
 for path,row in records:
  lane=research_lane_for_path(path)
  if lane and row.get('record_type') in WORKER_FORBIDDEN_RECORD_TYPES:errors.append(f"{path}: authoritative {row.get('record_type')} record is not allowed under worker research partition {lane}")
def validate_batch_integrity(records,index,errors):
 hashes={r.get('content_hash') for r in index.get('source',{}).values() if r.get('content_hash')}
 for path,m in records:
  if m.get('record_type')!='batch_manifest':continue
  rows=batch_records_for(path,records);expected=compute_batch_hash(m,rows)
  if m.get('batch_hash')!=expected:errors.append(f"{path}: batch_hash mismatch: declared {m.get('batch_hash')}, expected {expected}")
  counts={}
  for row in rows:counts[row.get('record_type')]=counts.get(row.get('record_type'),0)+1
  declared=m.get('record_counts',{})
  for key in REQUIRED_BATCH_COUNTS:
   if key not in declared:errors.append(f'{path}: record_counts.{key} is required for a governed research batch')
  for key,rt in COUNT_KEYS.items():
   if key in declared and declared[key]!=counts.get(rt,0):errors.append(f'{path}: record_counts.{key}={declared[key]} but batch contains {counts.get(rt,0)}')
  for wid in m.get('works',[]):add_missing_reference(errors,path,'works','WORK',wid,index)
  for h in m.get('source_hashes',[]):
   if h not in hashes:errors.append(f'{path}: source_hashes references unknown source content_hash {h}')
  lane=research_lane_for_path(path)
  if lane and m.get('worker_id')!=RESEARCH_WORKERS[lane]:errors.append(f"{path}: worker_id {m.get('worker_id')} does not match research partition owner {RESEARCH_WORKERS[lane]}")
def validate_payload(path,decision,registry,scope_keys,index,errors):
 t=decision.get('decision_type');p=decision.get('payload') or {};status=decision.get('status');st=decision.get('subject_type')
 if t=='ENTITY_LINK':
  if st!='LOCAL_ENTITY':errors.append(f'{path}: ENTITY_LINK requires subject_type LOCAL_ENTITY')
  required={'relation_predicate','target_type','target_id'};missing=sorted(required-set(p))
  if missing:errors.append(f"{path}: ENTITY_LINK payload missing {', '.join(missing)}");return
  if set(p)!=required:errors.append(f'{path}: ENTITY_LINK payload may contain only relation_predicate, target_id, target_type')
  if p.get('target_type')!='LOCAL_ENTITY':errors.append(f'{path}: ENTITY_LINK target_type must be LOCAL_ENTITY until a global-entity schema is governed')
  pred=registry.get(p.get('relation_predicate'))
  if pred is None:errors.append(f"{path}: ENTITY_LINK uses unregistered relation predicate {p.get('relation_predicate')}");return
  if 'RECONCILIATION_RELATION' not in set(pred.get('usage_levels',[])):errors.append(f"{path}: ENTITY_LINK predicate {pred.get('name')} does not allow RECONCILIATION_RELATION usage")
  if pred.get('semantic_class')!='IDENTITY_RELATION':errors.append(f"{path}: ENTITY_LINK predicate {pred.get('name')} is not governed as IDENTITY_RELATION")
  if status=='ACCEPTED' and pred.get('status')!='ACCEPTED':errors.append(f"{path}: accepted ENTITY_LINK may not use {pred.get('status')} predicate {pred.get('name')}")
  if status=='PROPOSED' and pred.get('status') not in {'ACCEPTED','EXPERIMENTAL'}:errors.append(f"{path}: proposed ENTITY_LINK may not use {pred.get('status')} predicate {pred.get('name')}")
  if st not in set(pred.get('subject_types',[])):errors.append(f"{path}: identity predicate {pred.get('name')} does not allow subject_type {st}")
  tt=p.get('target_type')
  if tt not in set(pred.get('object_ref_types',[])):errors.append(f"{path}: identity predicate {pred.get('name')} does not allow target_type {tt}")
  if tt in REFERENCE_TYPES:add_missing_reference(errors,path,'payload.target_id',tt,p.get('target_id'),index)
 elif t=='ASSERTION_DISPOSITION':
  if st!='ASSERTION':errors.append(f'{path}: ASSERTION_DISPOSITION requires subject_type ASSERTION')
  if set(p)!={'disposition'} or p.get('disposition') not in DISPOSITIONS:errors.append(f'{path}: ASSERTION_DISPOSITION payload must contain only a governed disposition')
 elif t=='ASSERTION_PROJECTION_STATUS':
  if st!='ASSERTION':errors.append(f'{path}: ASSERTION_PROJECTION_STATUS requires subject_type ASSERTION')
  if set(p)!={'projection_status'} or p.get('projection_status') not in PROJECTION_STATUSES:errors.append(f'{path}: ASSERTION_PROJECTION_STATUS payload must contain only a governed projection_status')
 elif t=='SCOPE_RESOLUTION':
  if st not in {'ASSERTION','WORK','LOCAL_ENTITY'}:errors.append(f'{path}: SCOPE_RESOLUTION subject_type must be ASSERTION, WORK, or LOCAL_ENTITY')
  if set(p)!={'resolution_key','resolution'} or not isinstance(p.get('resolution_key'),str) or not p.get('resolution_key').strip():errors.append(f'{path}: SCOPE_RESOLUTION payload requires non-empty resolution_key and resolution')
  else:
   entry=scope_keys.get(p['resolution_key'])
   if entry is None:errors.append(f"{path}: SCOPE_RESOLUTION uses ungoverned resolution_key {p['resolution_key']}")
   elif st not in set(entry.get('subject_types',[])):errors.append(f"{path}: scope key {p['resolution_key']} does not allow subject_type {st}")
 elif t=='OTHER' and status=='ACCEPTED':errors.append(f'{path}: OTHER reconciliation decisions are proposal/staging only and may not be ACCEPTED')
def decision_active_key(d):
 t=d.get('decision_type');p=d.get('payload') or {};base=(t,d.get('subject_type'),d.get('subject_id'))
 if t=='ENTITY_LINK':return base+(p.get('relation_predicate'),)
 if t=='SCOPE_RESOLUTION':return base+(p.get('resolution_key'),)
 if t in {'ASSERTION_DISPOSITION','ASSERTION_PROJECTION_STATUS'}:return base
 return None
def validate_assertion_lineage(index,errors):
 assertions=index.get('assertion',{})
 for start in assertions:
  seen=set();cur=start
  while cur:
   if cur in seen:errors.append(f'assertion: supersession cycle detected at {cur}');break
   seen.add(cur);row=assertions.get(cur);cur=row.get('supersedes') if row else None
def validate_reconciliation_integrity(index,registry,scope_keys,errors):
 decisions=index.get('reconciliation_decision',{});accepted=[d for d in decisions.values() if d.get('status')=='ACCEPTED']
 for did,d in decisions.items():
  validate_payload(f'reconciliation:{did}',d,registry,scope_keys,index,errors);predecessor=d.get('supersedes')
  if predecessor:
   if d.get('status')=='ACCEPTED' and (not isinstance(d.get('reason'),str) or not d.get('reason').strip()):errors.append(f'reconciliation: superseding accepted decision {did} requires non-empty reason')
   prior=decisions.get(predecessor)
   if prior and decision_active_key(prior)!=decision_active_key(d):errors.append(f'reconciliation: {did} supersedes predecessor with different active key {predecessor}')
 for start in decisions:
  seen=set();cur=start
  while cur:
   if cur in seen:errors.append(f'reconciliation: supersession cycle detected at {cur}');break
   seen.add(cur);row=decisions.get(cur);cur=row.get('supersedes') if row else None
 superseded={d.get('supersedes') for d in accepted if d.get('supersedes')};active=[d for d in accepted if d.get('decision_id') not in superseded];groups={}
 for d in active:
  key=decision_active_key(d)
  if key is not None:groups.setdefault(key,[]).append(d.get('decision_id'))
 for key,ids in sorted(groups.items(),key=lambda x:repr(x[0])):
  if len(ids)>1:errors.append(f'reconciliation: multiple active decisions for key {key}: {sorted(ids)}')
 dispositions={d.get('subject_id'):d for d in active if d.get('decision_type')=='ASSERTION_DISPOSITION' and d.get('subject_type')=='ASSERTION'};superseded_assertions={a.get('supersedes') for a in index.get('assertion',{}).values() if a.get('supersedes')}
 for d in active:
  if d.get('decision_type')!='ASSERTION_PROJECTION_STATUS' or d.get('subject_type')!='ASSERTION':continue
  aid=d.get('subject_id');a=index.get('assertion',{}).get(aid)
  if not a:continue
  effective=a.get('status');override=dispositions.get(aid)
  if override:effective=(override.get('payload') or {}).get('disposition')
  if aid in superseded_assertions:effective='SUPERSEDED'
  if effective!='ACCEPTED':errors.append(f"reconciliation:{d.get('decision_id')}: projection-status decision targets effectively {effective} assertion {aid}")
def main():
 seen={};index={rt:{} for rt in ID_FIELDS};errors=[];schemas=load_schemas();registry,reg_errors=load_predicate_registry();scope_keys,scope_errors=load_scope_key_registry();errors.extend(reg_errors);errors.extend(scope_errors)
 try:records=list(iter_records())
 except ValueError as exc:records=[];errors.append(str(exc))
 for path,row in records:
  rt=row.get('record_type')
  if not rt:errors.append(f'{path}: missing record_type');continue
  if rt not in schemas:errors.append(f'{path}: unknown record_type {rt}');continue
  for err in schema_errors(row,schemas[rt]):errors.append(f'{path}: schema: {err}')
  id_field=ID_FIELDS.get(rt)
  if id_field:
   rid=row.get(id_field)
   if not rid:errors.append(f'{path}: {rt} missing {id_field}')
   elif (rt,rid) in seen:errors.append(f'duplicate {rt} id {rid}: {seen[(rt,rid)]} and {path}')
   else:seen[(rt,rid)]=path;index[rt][rid]=row
 validate_partition_ownership(records,errors);validate_references(records,index,errors)
 for path,row in records:
  if row.get('record_type')=='assertion':validate_predicate_assertion(path,row,registry,index,errors)
 validate_assertion_lineage(index,errors);validate_batch_integrity(records,index,errors);validate_reconciliation_integrity(index,registry,scope_keys,errors)
 if errors:print('VALIDATION FAILED');print('\n'.join('- '+e for e in errors));return 1
 print(f'VALIDATION PASSED: {len(seen)} identified records');return 0
if __name__=='__main__':sys.exit(main())
