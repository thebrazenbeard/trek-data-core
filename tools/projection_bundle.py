#!/usr/bin/env python3
"""Shared deterministic verifier for canonical projection bundles consumed by derived adapters."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA=ROOT/'schema'/'projection-manifest.schema.json'; RELATION_SCHEMA=ROOT/'schema'/'projection-relation.schema.json'; PROVENANCE_SCHEMA=ROOT/'schema'/'projection-provenance.schema.json'
RECONCILIATION_SCHEMA=ROOT/'schema'/'reconciliation-decision.schema.json'
REQUIRED_OUTPUTS=('entities.jsonl','facts.jsonl','relations.jsonl','contested.jsonl','unresolved.jsonl','provenance.jsonl','assertion_history.jsonl','reconciliation_history.jsonl')
ID_KEYS={'entities.jsonl':'local_entity_id','facts.jsonl':'assertion_id','relations.jsonl':'relation_id','contested.jsonl':'assertion_id','unresolved.jsonl':'assertion_id','provenance.jsonl':'provenance_id','assertion_history.jsonl':'assertion_id','reconciliation_history.jsonl':'decision_id'}
ASSERTION_PROJECTION_DECORATIONS=frozenset({
 'effective_assertion_status','assertion_disposition_decision_id','projection_status','projection_status_decision_id','projection_reason',
 'resolved_scope','scope_resolution_decision_ids','subject_identity_links','subject_resolved_scope','subject_scope_resolution_decision_ids',
})
ENTITY_PROJECTION_DECORATIONS=frozenset({'identity_links','resolved_scope','scope_resolution_decision_ids'})
PROVENANCE_DECORATIONS=frozenset({'effective_assertion_status','assertion_disposition_decision_id','projection_status','projection_status_decision_id','projection_reason','scope_resolution_decision_ids','entity_link_decision_ids'})
HASH_RE=re.compile(r'^sha256:[0-9a-f]{64}$')

def canonical(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def sha256_bytes(data): return 'sha256:'+hashlib.sha256(data).hexdigest()
def compute_projection_hash(outputs): return sha256_bytes(canonical({name:outputs[name]['hash'] for name in REQUIRED_OUTPUTS}).encode())
def tool_identity(*paths):
 material=[]
 for path in sorted((Path(p) for p in paths),key=lambda p:str(p)): material.append({'path':path.name,'hash':sha256_bytes(path.read_bytes())})
 return sha256_bytes(canonical(material).encode('utf-8'))
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
  if not any(type_matches(value,t) for t in allowed): return [f'{location}: expected type {allowed}']
 if 'const' in schema and value!=schema['const']:errors.append(f"{location}: expected constant {schema['const']!r}")
 if 'enum' in schema and value not in schema['enum']:errors.append(f'{location}: value not in enum')
 if isinstance(value,str) and len(value)<schema.get('minLength',0):errors.append(f'{location}: string shorter than minLength')
 if isinstance(value,list):
  if len(value)<schema.get('minItems',0):errors.append(f'{location}: array shorter than minItems')
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
def parse_jsonl(path,id_key):
 rows=[]; seen=set(); raw_bytes=path.read_bytes()
 for line_no,raw in enumerate(raw_bytes.decode('utf-8').splitlines(),1):
  if not raw.strip():continue
  try:row=json.loads(raw)
  except Exception as exc:raise ValueError(f'{path}:{line_no}: invalid JSON: {exc}') from exc
  if not isinstance(row,dict):raise ValueError(f'{path}:{line_no}: row must be object')
  rid=row.get(id_key)
  if not isinstance(rid,str) or not rid:raise ValueError(f'{path}:{line_no}: row missing {id_key}')
  if rid in seen:raise ValueError(f'{path}: duplicate {id_key} {rid}')
  seen.add(rid); rows.append(row)
 canonical_bytes=''.join(canonical(r)+'\n' for r in sorted(rows,key=lambda r:(str(r.get(id_key,'')),canonical(r)))).encode('utf-8')
 if raw_bytes!=canonical_bytes:raise ValueError(f'{path}: JSONL bytes are not canonical deterministic serialization')
 return rows,raw_bytes

def verify_reconciliation_replay(rows):
 """Replay compiler-owned fields from accepted decisions, never accepting a bare ID or decoration.

 This checks the published decision history against its derived rows; it does not
 authenticate that the decision history itself was approved by a trusted Git head.
 """
 history={r['assertion_id']:r for r in rows['assertion_history.jsonl']}
 entities={r['local_entity_id']:r for r in rows['entities.jsonl']}
 recon=rows['reconciliation_history.jsonl']; decisions={d['decision_id']:d for d in recon}
 decision_schema=json.loads(RECONCILIATION_SCHEMA.read_text(encoding='utf-8'))
 predicates={p['name']:p for p in json.loads((ROOT/'registry'/'predicates.json').read_text(encoding='utf-8'))['predicates']}
 scope_keys={s['key']:s for s in json.loads((ROOT/'registry'/'scope_keys.json').read_text(encoding='utf-8'))['scope_keys']}
 # The projection does not contain the complete Source/Work/Evidence catalog.
 # Only independently present, referenced records can establish targets here;
 # unverifiable references fail closed rather than inventing a source record.
 refs={'ASSERTION':set(history),'LOCAL_ENTITY':set(entities),'RECONCILIATION_DECISION':set(decisions),
       'SOURCE':set(),'WORK':set(),'EVIDENCE':set()}
 for p in rows['provenance.jsonl']:
  refs['SOURCE'].add(p['source_record']['source_id'])
  refs['SOURCE'].update(s['source_id'] for s in p['source_lineage_records'])
  refs['WORK'].add(p['work_record']['work_id'])
  refs['WORK'].update(w['work_id'] for w in p['work_lineage_records'])
  refs['EVIDENCE'].add(p['evidence_record']['evidence_id'])
 def decision_key(d):
  typ=d['decision_type']; base=(typ,d['subject_type'],d['subject_id']); payload=d['payload']
  if typ=='ENTITY_LINK':return base+(payload.get('relation_predicate'),)
  if typ=='SCOPE_RESOLUTION':return base+(payload.get('resolution_key'),)
  if typ in {'ASSERTION_DISPOSITION','ASSERTION_PROJECTION_STATUS'}:return base
  return None
 for d in recon:
  errs=schema_errors(d,decision_schema)
  if errs:raise ValueError(f"reconciliation decision {d['decision_id']}: "+'; '.join(errs))
  if d['status'] not in {'ACCEPTED','SUPERSEDED'}:raise ValueError(f"reconciliation decision {d['decision_id']}: nonpublished status")
  if d['subject_id'] not in refs.get(d['subject_type'],set()):
   raise ValueError(f"reconciliation decision {d['decision_id']}: unknown {d['subject_type']} subject {d['subject_id']}")
  for eid in d['evidence']:
   if eid not in refs['EVIDENCE'] and eid not in refs['ASSERTION']:
    raise ValueError(f"reconciliation decision {d['decision_id']}: evidence {eid} not verifiable in projection")
  prior_id=d.get('supersedes')
  if prior_id:
   prior=decisions.get(prior_id)
   if prior is None:raise ValueError(f"reconciliation decision {d['decision_id']}: unknown superseded decision {prior_id}")
   if decision_key(prior)!=decision_key(d):raise ValueError(f"reconciliation decision {d['decision_id']}: superseded decision key mismatch")
   if d['status']=='ACCEPTED' and (not isinstance(d.get('reason'),str) or not d['reason'].strip()):
    raise ValueError(f"reconciliation decision {d['decision_id']}: accepted supersession requires reason")
 for start in decisions:
  seen=set(); cur=start
  while cur:
   if cur in seen:raise ValueError(f'reconciliation supersession cycle at {cur}')
   seen.add(cur); cur=decisions[cur].get('supersedes') if cur in decisions else None
 superseded={d.get('supersedes') for d in recon if d['status']=='ACCEPTED' and d.get('supersedes')}
 active={}
 for d in recon:
  if d['status']!='ACCEPTED' or d['decision_id'] in superseded:continue
  typ=d['decision_type']; st=d['subject_type']; sid=d['subject_id']; payload=d['payload']
  if typ=='ENTITY_LINK':
   pred=predicates.get(payload.get('relation_predicate'))
   if (st!='LOCAL_ENTITY' or set(payload)!={'relation_predicate','target_type','target_id'} or payload.get('target_type')!='LOCAL_ENTITY'
       or sid not in entities or payload.get('target_id') not in entities or not pred or pred.get('status')!='ACCEPTED'
       or pred.get('semantic_class')!='IDENTITY_RELATION' or 'RECONCILIATION_RELATION' not in pred.get('usage_levels',[])):
    raise ValueError(f"reconciliation decision {d['decision_id']}: invalid accepted identity link")
   key=(typ,st,sid,payload['relation_predicate'])
  elif typ=='SCOPE_RESOLUTION':
   entry=scope_keys.get(payload.get('resolution_key'))
   if (st not in {'ASSERTION','LOCAL_ENTITY','WORK'} or set(payload)!={'resolution_key','resolution'}
       or not entry or st not in entry['subject_types'] or sid not in refs[st]):
    raise ValueError(f"reconciliation decision {d['decision_id']}: invalid accepted scope resolution")
   key=(typ,st,sid,payload['resolution_key'])
  elif typ=='ASSERTION_DISPOSITION':
   if st!='ASSERTION' or sid not in history or set(payload)!={'disposition'} or payload.get('disposition') not in {'PROPOSED','ACCEPTED','REJECTED'}:
    raise ValueError(f"reconciliation decision {d['decision_id']}: invalid disposition")
   key=(typ,st,sid)
  elif typ=='ASSERTION_PROJECTION_STATUS':
   if st!='ASSERTION' or sid not in history or set(payload)!={'projection_status'} or payload.get('projection_status') not in {'STABLE','CONTESTED','UNRESOLVED','STRUCTURAL_PARADOX'}:
    raise ValueError(f"reconciliation decision {d['decision_id']}: invalid projection status")
   key=(typ,st,sid)
  else:raise ValueError(f"reconciliation decision {d['decision_id']}: nonexecutable type")
  if key in active:raise ValueError(f'reconciliation decision collision for {key}')
  active[key]=d

 dispositions={aid:(active[('ASSERTION_DISPOSITION','ASSERTION',aid)]['payload']['disposition']
                   if ('ASSERTION_DISPOSITION','ASSERTION',aid) in active else assertion.get('status'))
               for aid,assertion in history.items()}
 superseded_assertions={assertion['supersedes'] for aid,assertion in history.items()
                        if assertion.get('supersedes') and dispositions[aid]=='ACCEPTED'}

 def scoped(st,sid):
  selected={key[3]:d for key,d in active.items() if len(key)==4 and key[:3]==('SCOPE_RESOLUTION',st,sid)}
  if not selected:return {}
  return {'resolved_scope':{k:d['payload']['resolution'] for k,d in sorted(selected.items())},
          'scope_resolution_decision_ids':{k:d['decision_id'] for k,d in sorted(selected.items())}}
 def links(lid):
  return sorted((d for key,d in active.items() if len(key)==4 and key[:3]==('ENTITY_LINK','LOCAL_ENTITY',lid)),
                key=lambda d:(d['payload']['relation_predicate'],d['decision_id']))
 def expected_decorations(assertion,active_assertion):
  aid=assertion['assertion_id']; disposition=active.get(('ASSERTION_DISPOSITION','ASSERTION',aid))
  status=active.get(('ASSERTION_PROJECTION_STATUS','ASSERTION',aid))
  effective='SUPERSEDED' if aid in superseded_assertions else dispositions[aid]
  expected={'effective_assertion_status':effective}
  if disposition:expected['assertion_disposition_decision_id']=disposition['decision_id']
  if effective=='ACCEPTED':
   if status:
    expected.update(projection_status=status['payload']['projection_status'],projection_status_decision_id=status['decision_id'])
   else:expected.update(projection_status='UNRESOLVED',projection_reason='MISSING_PROJECTION_STATUS')
   if active_assertion:
    expected.update(scoped('ASSERTION',aid))
    if assertion.get('subject_type')=='LOCAL_ENTITY':
     ls=links(assertion.get('subject'))
     if ls:expected['subject_identity_links']=[{**d['payload'],'decision_id':d['decision_id']} for d in ls]
    subject_scope=scoped(assertion.get('subject_type'),assertion.get('subject'))
    if subject_scope:
     expected['subject_resolved_scope']=subject_scope['resolved_scope']
     expected['subject_scope_resolution_decision_ids']=subject_scope['scope_resolution_decision_ids']
  if status and effective!='ACCEPTED':
   raise ValueError(f'reconciliation status decision for nonaccepted assertion {aid}')
  return expected
 def require_fields(row,expected,fieldset,description):
  actual={k:v for k,v in row.items() if k in fieldset}
  want={k:v for k,v in expected.items() if k in fieldset}
  if actual!=want:raise ValueError(f'{description}: reconciliation decision replay mismatch')

 active_assertions={r['assertion_id']:r for name in ('facts.jsonl','contested.jsonl','unresolved.jsonl') for r in rows[name]}
 for aid,assertion in history.items():
  expected=expected_decorations(assertion,aid in active_assertions)
  actual=active_assertions.get(aid)
  if (expected['effective_assertion_status']=='ACCEPTED')!=(actual is not None):
   raise ValueError(f'assertion {aid}: reconciliation decision active partition mismatch')
  if actual:require_fields(actual,expected,ASSERTION_PROJECTION_DECORATIONS,f'assertion {aid}')
 for lid,row in entities.items():
  expected=scoped('LOCAL_ENTITY',lid)
  ls=links(lid)
  if ls:expected['identity_links']=[{**d['payload'],'decision_id':d['decision_id']} for d in ls]
  require_fields(row,expected,ENTITY_PROJECTION_DECORATIONS,f'entity {lid}')
 expected_identity_relations={f"reconciliation:{d['decision_id']}":d for d in active.values() if d['decision_type']=='ENTITY_LINK'}
 observed_identity_relations={r['relation_id']:r for r in rows['relations.jsonl'] if r.get('relation_kind')=='IDENTITY_LINK' or r['relation_id'].startswith('reconciliation:')}
 if set(observed_identity_relations)!=set(expected_identity_relations):raise ValueError('identity relations: reconciliation decision replay mismatch')
 for rid,d in expected_identity_relations.items():
  p=d['payload']; expected={'record_type':'projection_relation','relation_id':rid,'relation_kind':'IDENTITY_LINK','subject_type':'LOCAL_ENTITY',
                            'subject_id':d['subject_id'],'predicate':p['relation_predicate'],'target_type':p['target_type'],
                            'target_id':p['target_id'],'reconciliation_decision_id':d['decision_id']}
  if observed_identity_relations[rid]!=expected:raise ValueError(f'identity relation {rid}: reconciliation decision replay mismatch')
 for provenance in rows['provenance.jsonl']:
  assertion=history[provenance['assertion_id']]
  expected=expected_decorations(assertion,False)
  sc=scoped('ASSERTION',assertion['assertion_id'])
  if sc:expected['scope_resolution_decision_ids']=sc['scope_resolution_decision_ids']
  if assertion.get('subject_type')=='LOCAL_ENTITY':
   ls=links(assertion.get('subject'))
   if ls:expected['entity_link_decision_ids']=[d['decision_id'] for d in ls]
  require_fields(provenance,expected,PROVENANCE_DECORATIONS,f"provenance {provenance['provenance_id']}")

def verify_provenance_links(rows):
 """Reject self-hashed bundles with broken assertion/evidence/source custody links."""
 history={row['assertion_id']:row for row in rows['assertion_history.jsonl']}
 expected={(aid,eid) for aid,assertion in history.items() for eid in assertion.get('evidence',[])}
 found=set()
 for provenance in rows['provenance.jsonl']:
  aid=provenance['assertion_id']; eid=provenance['evidence_id']; assertion=history.get(aid)
  if assertion is None:raise ValueError(f'provenance {aid}::{eid}: unknown assertion in history')
  if provenance['provenance_id']!=f'{aid}::{eid}' or (aid,eid) in found:
   raise ValueError(f'provenance {aid}::{eid}: noncanonical or duplicate assertion/evidence pair')
  found.add((aid,eid))
  if provenance['assertion_record']!=assertion or provenance['support_set']!=sorted(assertion.get('evidence',[])) or eid not in assertion.get('evidence',[]):
   raise ValueError(f'provenance {aid}::{eid}: assertion record or support set mismatch')
  evidence=provenance['evidence_record']; source=provenance['source_record']; work=provenance['work_record']; binding=provenance['source_work_binding_record']
  if evidence.get('evidence_id')!=eid:
   raise ValueError(f'provenance {aid}::{eid}: evidence record mismatch')
  if (source.get('source_id')!=evidence.get('source_id') or work.get('work_id')!=evidence.get('work_id')
      or binding.get('source_id')!=source.get('source_id') or binding.get('work_id')!=work.get('work_id')):
   raise ValueError(f'provenance {aid}::{eid}: source/work binding endpoints mismatch')
 if found!=expected:
  raise ValueError(f'missing provenance for assertion/evidence pairs: {sorted(expected-found)}')
 active={row['assertion_id']:row for name in ('facts.jsonl','contested.jsonl','unresolved.jsonl') for row in rows[name]}
 for aid,active_row in active.items():
  historical=history.get(aid)
  if historical is None:raise ValueError(f'active assertion {aid}: absent from history')
  # The compiler may add only its explicitly enumerated projection fields;
  # the underlying worker assertion must remain byte-semantic equivalent.
  base_payload={k:v for k,v in active_row.items() if k not in ASSERTION_PROJECTION_DECORATIONS}
  historical_payload={k:v for k,v in historical.items() if k not in ASSERTION_PROJECTION_DECORATIONS}
  if base_payload!=historical_payload:
   raise ValueError(f'active assertion {aid}: history payload mismatch')
 for provenance in rows['provenance.jsonl']:
  active_row=active.get(provenance['assertion_id'])
  if active_row and (provenance['effective_assertion_status']!='ACCEPTED' or provenance.get('projection_status')!=active_row['projection_status']):
   raise ValueError(f"provenance {provenance['provenance_id']}: active assertion status mismatch")
def verify_projection(root):
 root=Path(root); manifest_path=root/'manifest.json'
 if not manifest_path.exists():raise ValueError('projection manifest is missing')
 try:manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
 except Exception as exc:raise ValueError(f'invalid projection manifest: {exc}') from exc
 if not isinstance(manifest,dict):raise ValueError('projection manifest must be object')
 schema=json.loads(MANIFEST_SCHEMA.read_text(encoding='utf-8')); errors=schema_errors(manifest,schema)
 if errors:raise ValueError('projection manifest schema failure: '+'; '.join(errors))
 outputs=manifest.get('outputs',{})
 if set(outputs)!=set(REQUIRED_OUTPUTS):raise ValueError(f'projection outputs must be exactly {sorted(REQUIRED_OUTPUTS)}')
 actual_jsonl={p.name for p in root.glob('*.jsonl')}
 if actual_jsonl!=set(REQUIRED_OUTPUTS):raise ValueError(f'unexpected or missing JSONL projection outputs: {sorted(actual_jsonl ^ set(REQUIRED_OUTPUTS))}')
 for key in ('predicate_registry_hash','scope_key_registry_hash','input_hash','projection_hash'):
  if not HASH_RE.match(str(manifest.get(key,''))):raise ValueError(f'manifest {key} is not a sha256 identity')
 # Registry semantics are used during the replay, so verify against those exact
 # local bytes. This is a version-match check, NOT external origin authentication.
 for key,filename in (('predicate_registry_hash','predicates.json'),('scope_key_registry_hash','scope_keys.json')):
  actual=sha256_bytes(canonical(json.loads((ROOT/'registry'/filename).read_text(encoding='utf-8'))).encode('utf-8'))
  if manifest[key]!=actual:raise ValueError(f'manifest {key}: registry version mismatch with local verifier')
 for key in ('projection_version','schema_version','methodology_version','compiler_commit','research_head','reconciliation_head'):
  if not isinstance(manifest.get(key),str) or not manifest[key].strip():raise ValueError(f'manifest {key} is missing')
 rows={}
 for name in REQUIRED_OUTPUTS:
  meta=outputs[name]
  if meta.get('role')!=name.removesuffix('.jsonl'):raise ValueError(f'{name}: role mismatch')
  path=root/name
  if not path.exists():raise ValueError(f'{name}: required output missing')
  parsed,raw_bytes=parse_jsonl(path,ID_KEYS[name]); rows[name]=parsed
  if meta.get('hash')!=sha256_bytes(raw_bytes):raise ValueError(f'{name}: content hash mismatch')
  if meta.get('count')!=len(parsed):raise ValueError(f'{name}: record count mismatch')
 active_ids=set()
 for name,allowed in (('facts.jsonl',{'STABLE'}),('unresolved.jsonl',{'UNRESOLVED'}),('contested.jsonl',{'CONTESTED','STRUCTURAL_PARADOX'})):
  for row in rows[name]:
   if row.get('projection_status') not in allowed:raise ValueError(f"{name}: invalid projection_status {row.get('projection_status')}")
   if row.get('effective_assertion_status')!='ACCEPTED':raise ValueError(f'{name}: active assertion is not effectively ACCEPTED')
   aid=row['assertion_id']
   if aid in active_ids:raise ValueError(f'assertion {aid} appears in multiple active partitions')
   active_ids.add(aid)
 relation_schema=json.loads(RELATION_SCHEMA.read_text(encoding='utf-8')); provenance_schema=json.loads(PROVENANCE_SCHEMA.read_text(encoding='utf-8'))
 for row in rows['relations.jsonl']:
  errs=schema_errors(row,relation_schema)
  if errs:raise ValueError('invalid projection relation: '+'; '.join(errs))
 for row in rows['provenance.jsonl']:
  errs=schema_errors(row,provenance_schema)
  if errs:raise ValueError('invalid projection provenance: '+'; '.join(errs))
 verify_provenance_links(rows)
 verify_reconciliation_replay(rows)
 recomputed=compute_projection_hash(outputs)
 if manifest.get('projection_hash')!=recomputed:raise ValueError(f"projection_hash mismatch: declared {manifest.get('projection_hash')}, expected {recomputed}")
 receipt={'projection_hash':manifest['projection_hash'],'input_hash':manifest['input_hash'],'projection_version':manifest['projection_version'],'schema_version':manifest['schema_version'],'methodology_version':manifest['methodology_version'],'compiler_commit':manifest['compiler_commit'],'research_head':manifest['research_head'],'reconciliation_head':manifest['reconciliation_head'],'predicate_registry_hash':manifest['predicate_registry_hash'],'scope_key_registry_hash':manifest['scope_key_registry_hash'],'verified_outputs':{name:outputs[name] for name in REQUIRED_OUTPUTS},'imported_output_contract':list(REQUIRED_OUTPUTS)}
 receipt_hash=sha256_bytes(canonical(receipt).encode('utf-8')); return {'manifest':manifest,'rows':rows,'receipt':receipt,'receipt_hash':receipt_hash}
