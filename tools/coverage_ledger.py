#!/usr/bin/env python3
"""Validate and report append-only independent Trek coverage ledgers.

Coverage events never infer later states. A report denominator is RESOLVED only when an
explicit governed denominator snapshot is supplied; the mere presence of Work records is
not evidence that the corpus denominator is complete.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/'schema'/'coverage-event.schema.json'
DENOMINATOR_SCHEMA=ROOT/'schema'/'coverage-denominator-snapshot.schema.json'
LIBRARIAN_CONTRACT=Path(__file__).resolve().parents[1]/'registry'/'librarian_registry_contract.schema.json'
PB=Path(__file__).with_name('projection_bundle.py'); SPEC=importlib.util.spec_from_file_location('trek_coverage_schema',PB); schema_tools=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(schema_tools)
STATES=('DISCOVERED','SOURCE_BOUND','FULL_TEXT_AVAILABLE','STRUCTURALLY_INDEXED','CLOSE_READ','SEMANTICALLY_ANALYZED','ENTITY_LINKED','CROSS_REFERENCED','AUDITED')
PREDECESSOR={state:STATES[i-1] for i,state in enumerate(STATES) if i>0}
SOURCE_STATES={'SOURCE_BOUND','FULL_TEXT_AVAILABLE','STRUCTURALLY_INDEXED','CLOSE_READ','SEMANTICALLY_ANALYZED'}
RESEARCH_ROLES={'TOS','TAS','TNG','DS9','VOY','ENT','DIS','SHORT','PIC','LD','PRO','SNW','SFA','FILMS','LIT'}

def canonical(v):return schema_tools.canonical(v)
def content_hash(v):return 'sha256:'+hashlib.sha256(canonical(v).encode('utf-8')).hexdigest()
def scope_key(v):return content_hash(v)

def reject_duplicate_keys(pairs):
 result={}
 for key,value in pairs:
  if key in result:raise ValueError(f'duplicate JSON key {key}')
  result[key]=value
 return result
def strict_json(raw):
 return json.loads(raw,object_pairs_hook=reject_duplicate_keys)

def read_jsonl(path):
 rows=[]
 if not Path(path).exists():return rows
 for line_no,raw in enumerate(Path(path).read_text(encoding='utf-8').splitlines(),1):
  if not raw.strip():continue
  row=strict_json(raw)
  if not isinstance(row,dict):raise ValueError(f'{path}:{line_no}: row must be object')
  rows.append(row)
 return rows
def scan_typed_records(with_paths=False):
 records=[];paths={}
 for base in (ROOT/'research',ROOT/'external',ROOT/'migrations',ROOT/'coverage',ROOT/'registry'):
  if not base.exists():continue
  for path in sorted(base.rglob('*.jsonl')):
   for row in read_jsonl(path):
    records.append(row)
    if row.get('record_type')=='coverage_event' and row.get('coverage_event_id'):paths[row['coverage_event_id']]=path
  if base.name=='coverage':
   for path in sorted(base.rglob('*.json')):
    row=strict_json(path.read_text(encoding='utf-8'))
    if isinstance(row,dict) and row.get('record_type'):
     records.append(row)
     if row.get('record_type')=='coverage_event' and row.get('coverage_event_id'):paths[row['coverage_event_id']]=path
 for base in (ROOT/'research',ROOT/'external',ROOT/'migrations',ROOT/'registry'/'authoritative'):
  for path in sorted(base.rglob('*.json')):
   row=strict_json(path.read_text(encoding='utf-8'))
   if not isinstance(row,dict) or not row.get('record_type'):
    raise ValueError(f'{path}: governed JSON must be a typed object')
   records.append(row)
   if row.get('record_type')=='coverage_event' and row.get('coverage_event_id'):paths[row['coverage_event_id']]=path
 return (records,paths) if with_paths else records
def index_records(records,record_type,id_key):
 out={}
 for row in records:
  if row.get('record_type')!=record_type:continue
  rid=row.get(id_key)
  if not rid:continue
  if rid in out:raise ValueError(f'duplicate {record_type} id {rid}')
  out[rid]=row
 return out

def authoritative_work_roster():
 """Read the complete accepted, nonfixture Work roster from governed file bytes.

 A reviewable registry-relative denominator is not a claim about all Star Trek
 installments; it is only a census of accepted Work records in this tree.
 """
 root=ROOT/'registry'/'authoritative'
 if (ROOT/'registry').is_symlink() or root.is_symlink():
  raise ValueError('authoritative registry root/parent must not be a symlink')
 if not root.is_dir():return {}
 work_schema=strict_json(LIBRARIAN_CONTRACT.read_text(encoding='utf-8'))['$defs']['work']
 items={}
 for path in sorted(root.rglob('*')):
  if path.is_symlink():raise ValueError(f'symlinked authoritative registry input {path}')
  if path.is_dir() or path.suffix not in {'.json','.jsonl'}:continue
  if not path.is_file():raise ValueError(f'non-file authoritative registry input {path}')
  try:path.resolve().relative_to(root.resolve())
  except ValueError:raise ValueError(f'authoritative registry input escapes root: {path}') from None
  raw=path.read_text(encoding='utf-8')
  try:rows=read_jsonl(path) if path.suffix=='.jsonl' else [strict_json(raw)]
  except ValueError as exc:raise ValueError(f'invalid authoritative registry bytes at {path}: {exc}') from exc
  for row in rows:
   if not isinstance(row,dict):raise ValueError(f'non-object authoritative registry input {path}')
   if row.get('record_type')!='work':continue
   work_id=row.get('work_id')
   if not isinstance(work_id,str) or not work_id:raise ValueError(f'invalid authoritative Work identity in {path}')
   if work_id in items:raise ValueError(f'duplicate authoritative Work ID {work_id}')
   if row.get('status')=='ACCEPTED':
    errors=schema_tools.schema_errors(row,work_schema)
    if errors:raise ValueError(f'invalid ACCEPTED authoritative Work {work_id}: '+'; '.join(errors))
   items[work_id]=row
 accepted={wid:row for wid,row in items.items() if row.get('status')=='ACCEPTED' and row.get('fixture_only') is False}
 for wid,row in accepted.items():
  seen={wid};parent=row.get('parent_work_id')
  while parent is not None:
   if parent in seen:raise ValueError(f'authoritative Work parent cycle at {wid}')
   seen.add(parent)
   target=accepted.get(parent)
   if target is None:raise ValueError(f'authoritative Work {wid} requires ACCEPTED nonfixture parent Work {parent}')
   parent=target.get('parent_work_id')
 return items

def accepted_registry_head(authoritative_works):
 records=[row for _,row in sorted(authoritative_works.items()) if row.get('status')=='ACCEPTED' and row.get('fixture_only') is False]
 return content_hash({'record_type':'authoritative_accepted_work_roster','works':records})

def authoritative_source_binding_rosters():
 """Read exact, nonfixture Librarian Source and binding origins for coverage."""
 root=ROOT/'registry'/'authoritative'
 if (ROOT/'registry').is_symlink() or root.is_symlink():
  raise ValueError('authoritative Librarian registry root/parent must not be a symlink')
 if not root.is_dir():return {},{}
 contracts=strict_json(LIBRARIAN_CONTRACT.read_text(encoding='utf-8'))['$defs']
 kinds={'source':('source_id','status'), 'source_work_binding':('binding_id','lifecycle')}
 rows={'source':{},'source_work_binding':{}}
 for path in sorted(root.rglob('*')):
  if path.is_symlink():raise ValueError(f'symlinked authoritative Librarian input {path}')
  if path.is_dir() or path.suffix not in {'.json','.jsonl'}:continue
  if not path.is_file():raise ValueError(f'non-file authoritative Librarian input {path}')
  try:path.resolve().relative_to(root.resolve())
  except ValueError:raise ValueError(f'authoritative Librarian input escapes root: {path}') from None
  try:entries=read_jsonl(path) if path.suffix=='.jsonl' else [strict_json(path.read_text(encoding='utf-8'))]
  except ValueError as exc:raise ValueError(f'invalid authoritative Librarian bytes at {path}: {exc}') from exc
  for item in entries:
   if not isinstance(item,dict):raise ValueError(f'non-object authoritative Librarian input {path}')
   kind=item.get('record_type')
   if kind not in kinds:continue
   key,life=kinds[kind];rid=item.get(key)
   if not isinstance(rid,str) or not rid:raise ValueError(f'invalid authoritative {kind} identity in {path}')
   if rid in rows[kind]:raise ValueError(f'duplicate authoritative {kind} identity {rid}')
   if item.get(life)=='ACCEPTED':
    errors=schema_tools.schema_errors(item,contracts[kind])
    if errors:raise ValueError(f'invalid ACCEPTED authoritative {kind} {rid}: '+'; '.join(errors))
   rows[kind][rid]=item
 return rows['source'],rows['source_work_binding']

def accepted_source_binding_basis(source,binding):
 """Only exact SHA-256 byte evidence currently establishes SOURCE_BOUND.

 Other evidence methods need the canonical projection/Librarian admission
 review before they can be counted as coverage. A matching declared digest
 is consistency evidence, never independent proof of retrieved source bytes.
 """
 digest=source.get('content_hash')
 if not isinstance(digest,str) or re.fullmatch(r'sha256:[0-9a-f]{64}',digest) is None:return False
 basis=binding.get('basis')
 return isinstance(basis,list) and any(isinstance(b,dict) and b.get('kind')=='BYTE_HASH' and b.get('value')==digest for b in basis)
def active_events(events):
 # Rejection of a proposed correction cannot revoke previously accepted history.
 superseded={row.get('supersedes') for row in events.values() if row.get('supersedes') and row.get('status')=='ACCEPTED'}
 return {eid:row for eid,row in events.items() if row.get('status')=='ACCEPTED' and eid not in superseded}
def coverage_key(row):return (row.get('coverage_state'),row.get('subject_type'),row.get('subject_id'),row.get('scope_key'))
def role_errors(row):
 state=row.get('coverage_state');role=row.get('producer_role');errors=[]
 if state in {'DISCOVERED','SOURCE_BOUND'} and role!='LIBRARIAN':errors.append(f'{state} must be produced by LIBRARIAN')
 if state in {'CLOSE_READ','SEMANTICALLY_ANALYZED'} and role not in RESEARCH_ROLES:errors.append(f'{state} must be produced by a research lane role')
 if state in {'ENTITY_LINKED','CROSS_REFERENCED'} and role!='CONSOLIDATOR':errors.append(f'{state} must be produced by CONSOLIDATOR')
 if state=='AUDITED' and role!='AUDITOR':errors.append('AUDITED must be produced by AUDITOR')
 return errors
def validate_coverage(records,works=None,sources=None,bindings=None,record_paths=None,enforce_origins=False):
 works=works if works is not None else index_records(records,'work','work_id');sources=sources if sources is not None else index_records(records,'source','source_id');bindings=bindings if bindings is not None else index_records(records,'source_work_binding','binding_id')
 authoritative=authoritative_work_roster() if enforce_origins else {}
 authoritative_sources,authoritative_bindings=authoritative_source_binding_rosters() if enforce_origins else ({},{})
 events=index_records(records,'coverage_event','coverage_event_id');schema=json.loads(SCHEMA.read_text(encoding='utf-8'));errors=[]
 for eid,row in events.items():
  for err in schema_tools.schema_errors(row,schema):errors.append(f'{eid}: schema: {err}')
  if not isinstance(row.get('scope'),dict) or not row.get('scope'):
   errors.append(f'{eid}: event requires a non-empty governed scope')
  elif row.get('scope_key')!=scope_key(row['scope']):
   errors.append(f'{eid}: scope_key does not match canonical scope')
  if row.get('status')=='ACCEPTED' and enforce_origins:
   origin=(record_paths or {}).get(eid)
   if origin is None:errors.append(f'{eid}: unverified accepted event origin')
   else:
    try:Path(origin).resolve().relative_to((ROOT/'coverage').resolve())
    except ValueError:errors.append(f'{eid}: accepted coverage event outside authoritative coverage root')
    else:
     path=Path(origin)
     if not path.is_file():errors.append(f'{eid}: accepted coverage event origin is not a file')
     else:
      try:
       located=read_jsonl(path) if path.suffix=='.jsonl' else [json.loads(path.read_text(encoding='utf-8'))] if path.suffix=='.json' else []
       if canonical(row) not in {canonical(v) for v in located}:errors.append(f'{eid}: accepted coverage event does not match its authoritative origin bytes')
      except (ValueError,OSError) as exc:errors.append(f'{eid}: coverage origin unreadable: {exc}')
  prereqs=row.get('prerequisite_event_ids',[])
  if len(prereqs)!=len(set(prereqs)):errors.append(f'{eid}: duplicate prerequisite_event_ids')
  for prereq in prereqs:
   if prereq not in events:errors.append(f'{eid}: dangling prerequisite_event_id {prereq}')
  if row.get('supersedes'):
   predecessor=events.get(row['supersedes'])
   if predecessor is None:errors.append(f'{eid}: supersedes missing coverage event {row["supersedes"]}')
   else:
    if coverage_key(predecessor)!=coverage_key(row):errors.append(f'{eid}: supersession must preserve dimension, subject and scope key')
    if row.get('status')=='ACCEPTED' and predecessor.get('status')!='ACCEPTED':errors.append(f'{eid}: accepted correction requires accepted predecessor')
    if row.get('status') in {'ACCEPTED','REJECTED'} and (not isinstance(row.get('reason'),str) or not row.get('reason').strip()):errors.append(f'{eid}: correction requires non-empty reason')
  if row.get('status')=='ACCEPTED' and row.get('effect')=='REVOKED':
   predecessor=events.get(row.get('supersedes'))
   if predecessor is None or predecessor.get('status')!='ACCEPTED' or predecessor.get('effect')!='ATTAINED':
    errors.append(f'{eid}: REVOKED requires accepted ATTAINED predecessor')
 for start in events:
  seen=set();current=start
  while current:
   if current in seen:errors.append(f'coverage supersession cycle at {current}');break
   seen.add(current);row=events.get(current);current=row.get('supersedes') if row else None
 active=active_events(events);grouped={}
 for eid,row in active.items():grouped.setdefault(coverage_key(row),[]).append(eid)
 for key,ids in grouped.items():
  if len(ids)>1:errors.append(f'multiple active accepted coverage events for {key}: {sorted(ids)}')
 for eid,row in active.items():
  state=row['coverage_state'];work_id=row['work_id'];source_id=row.get('source_id')
  if work_id not in works:errors.append(f'{eid}: accepted coverage references missing Work {work_id}')
  else:
   work=works[work_id]
   if work.get('status')!='ACCEPTED' or work.get('fixture_only') is not False:
    errors.append(f'{eid}: accepted coverage requires nonfixture ACCEPTED Work {work_id}')
   if enforce_origins and (work_id not in authoritative or canonical(authoritative[work_id])!=canonical(work)):
    errors.append(f'{eid}: accepted coverage Work {work_id} is not an exact disk-backed authoritative registry record')
  errors.extend(f'{eid}: {err}' for err in role_errors(row))
  if state in SOURCE_STATES:
   if not source_id:errors.append(f'{eid}: {state} requires source_id')
   elif source_id not in sources:errors.append(f'{eid}: accepted coverage references missing Source {source_id}')
   else:
    source=sources[source_id]
    if source.get('status')!='ACCEPTED' or source.get('fixture_only') is not False:
     errors.append(f'{eid}: accepted {state} requires nonfixture ACCEPTED Source {source_id}')
    if enforce_origins and (source_id not in authoritative_sources or canonical(authoritative_sources[source_id])!=canonical(source)):
     errors.append(f'{eid}: accepted {state} Source {source_id} is not an exact disk-backed authoritative registry record')
  if state=='SOURCE_BOUND':
   binding_id=row.get('binding_id');binding=bindings.get(binding_id) if binding_id else None
   if row.get('subject_type')!='SOURCE_WORK_BINDING' or row.get('subject_id')!=binding_id:
    errors.append(f'{eid}: SOURCE_BOUND subject_type and subject_id must identify its exact source_work_binding')
   if not isinstance(row.get('scope'),dict) or row['scope'].get('work_id')!=work_id or row['scope'].get('source_id')!=source_id:
    errors.append(f'{eid}: SOURCE_BOUND governed scope must match the bound Source/Work identifiers')
   if not binding_id:errors.append(f'{eid}: SOURCE_BOUND requires binding_id')
   elif binding is None:errors.append(f'{eid}: SOURCE_BOUND requires governed source_work_binding {binding_id}; Librarian binding surface is unavailable or reference is missing')
   else:
    if binding.get('lifecycle')!='ACCEPTED':errors.append(f'{eid}: SOURCE_BOUND requires ACCEPTED binding lifecycle {binding_id}')
    if binding.get('mapping_role')!='EVIDENCE_BEARING':errors.append(f'{eid}: metadata-only binding cannot establish SOURCE_BOUND')
    if not isinstance(binding.get('method'),str) or not binding['method'].strip():
     errors.append(f'{eid}: SOURCE_BOUND requires a nonempty Librarian binding method')
    if binding.get('fixture_only') is not False:errors.append(f'{eid}: SOURCE_BOUND requires nonfixture accepted binding {binding_id}')
    if binding.get('work_id')!=work_id or binding.get('source_id')!=source_id:errors.append(f'{eid}: binding Source/Work context does not match coverage event')
    if enforce_origins and (binding_id not in authoritative_bindings or canonical(authoritative_bindings[binding_id])!=canonical(binding)):
     errors.append(f'{eid}: SOURCE_BOUND binding {binding_id} is not an exact disk-backed authoritative Librarian record')
    source=sources.get(source_id)
    if source is None or not accepted_source_binding_basis(source,binding):
     errors.append(f'{eid}: SOURCE_BOUND requires exact accepted Source SHA-256 BYTE_HASH binding basis')
  if state=='FULL_TEXT_AVAILABLE':
   scope=row.get('representation_scope')
   if not isinstance(scope,dict) or not scope.get('representation_type') or not scope.get('completeness_scope'):errors.append(f'{eid}: FULL_TEXT_AVAILABLE requires representation_scope with representation_type and completeness_scope')
  if state in {'ENTITY_LINKED','CROSS_REFERENCED'} and not row.get('integration_ref'):errors.append(f'{eid}: {state} requires integration_ref')
  if state=='AUDITED' and not row.get('audit_ref'):errors.append(f'{eid}: AUDITED requires audit_ref')
  predecessor_state=PREDECESSOR.get(state)
  if predecessor_state:
   candidates=[]
   for prereq_id in row.get('prerequisite_event_ids',[]):
    prereq=active.get(prereq_id)
    if prereq and prereq.get('coverage_state')==predecessor_state and prereq.get('work_id')==work_id:
     if predecessor_state in SOURCE_STATES and state in SOURCE_STATES and prereq.get('source_id')!=source_id:continue
     candidates.append(prereq_id)
   if not candidates:errors.append(f'{eid}: accepted {state} requires active accepted {predecessor_state} prerequisite for the same governed context')
 return errors
def normalize_denominator_snapshot(snapshot,works,origin_path=None,enforce_origin=False):
 if snapshot is None:return None
 if not isinstance(snapshot,dict):raise ValueError('denominator snapshot must be an object')
 if enforce_origin:
  if origin_path is None:raise ValueError('unverified denominator snapshot origin')
  path=Path(origin_path)
  if (ROOT/'coverage').is_symlink() or (ROOT/'coverage'/'denominators').is_symlink() or path.is_symlink():
   raise ValueError('symlinked denominator origin is forbidden')
  if any(parent.is_symlink() for parent in path.parents if parent!=ROOT.parent and parent!=ROOT):
   raise ValueError('symlinked denominator parent is forbidden')
  try:path.resolve().relative_to((ROOT/'coverage'/'denominators').resolve())
  except ValueError:raise ValueError('denominator snapshot outside authoritative denominator root') from None
  if path.suffix!='.json' or not path.is_file():raise ValueError('denominator snapshot must be a file under authoritative denominator root')
  try:origin=strict_json(path.read_text(encoding='utf-8'))
  except (OSError,ValueError) as exc:raise ValueError(f'denominator snapshot origin unreadable: {exc}') from exc
  if canonical(origin)!=canonical(snapshot):raise ValueError('denominator snapshot differs from authoritative origin bytes')
 schema=json.loads(DENOMINATOR_SCHEMA.read_text(encoding='utf-8'))
 errors=schema_tools.schema_errors(snapshot,schema)
 if errors:raise ValueError('denominator schema: '+'; '.join(errors))
 ids=snapshot['unit_ids']
 if ids!=sorted(set(ids)):raise ValueError('denominator unit_ids must be deterministically sorted and unique')
 if snapshot['snapshot_hash']!=content_hash({k:v for k,v in snapshot.items() if k!='snapshot_hash'}):
  raise ValueError('denominator snapshot_hash does not match its canonical content')
 if snapshot['unit_type']!='WORK':raise ValueError('native-unit denominator reporting is pending; Work denominator cannot represent other unit types')
 missing_works=sorted(set(ids)-set(works))
 if missing_works:raise ValueError(f'denominator snapshot references missing governed Work IDs: {missing_works}')
 if snapshot['status']=='RESOLVED':
  scope=snapshot['scope']
  if not isinstance(scope,dict) or set(scope)!={'claim','work_type','parent_work_id'} or scope.get('claim')!='ACCEPTED_AUTHORITATIVE_WORK_REGISTRY_ROSTER' or not isinstance(scope.get('work_type'),str) or not scope['work_type'] or not (scope.get('parent_work_id') is None or isinstance(scope.get('parent_work_id'),str) and bool(scope['parent_work_id'])):
   raise ValueError('RESOLVED scope must select an explicit accepted authoritative Work registry roster, not a complete Mission/series universe')
  authoritative=authoritative_work_roster()
  accepted={wid:row for wid,row in authoritative.items() if row.get('status')=='ACCEPTED' and row.get('fixture_only') is False}
  if not accepted:raise ValueError('no nonfixture ACCEPTED authoritative Work registry available for denominator resolution')
  actual_head=accepted_registry_head(authoritative)
  if snapshot['registry_head']!=actual_head:
   raise ValueError(f'denominator registry_head does not match authoritative accepted Work roster ({actual_head})')
  scoped_ids=sorted(wid for wid,row in accepted.items() if row.get('work_type')==scope['work_type'] and row.get('parent_work_id')==scope['parent_work_id'])
  if not scoped_ids:raise ValueError('no ACCEPTED authoritative Works match denominator scope')
  if ids!=scoped_ids:raise ValueError('denominator unit_ids must equal the complete authoritative accepted Work roster for the declared scope')
  for wid in ids:
   if canonical(works[wid])!=canonical(accepted[wid]):raise ValueError(f'denominator Work {wid} does not match ACCEPTED authoritative registry origin')
 if snapshot['status']=='RESOLVED' and snapshot['blockers']:
  raise ValueError('resolved denominator cannot retain unresolved blockers')
 if snapshot['status']=='DENOMINATOR_UNRESOLVED' and not snapshot['blockers']:
  raise ValueError('unresolved denominator requires explicit blockers')
 return {'snapshot_ref':snapshot['snapshot_id'],'definition':canonical(snapshot['scope']),'work_ids':ids,'exclusions':snapshot['exclusions'],'unknowns':snapshot['blockers'],'dimension':snapshot['dimension'],'status':snapshot['status'],'snapshot_hash':snapshot['snapshot_hash']}
def coverage_report(records,works=None,denominator_snapshot=None,sources=None,bindings=None,record_paths=None,denominator_path=None):
 """Fail closed before publication; origin paths are supplied by the repository scanner."""
 works=works if works is not None else index_records(records,'work','work_id')
 errors=validate_coverage(records,works=works,sources=sources,bindings=bindings,record_paths=record_paths,enforce_origins=True)
 if errors:raise ValueError('unverified coverage report input:\n'+'\n'.join(errors))
 events=index_records(records,'coverage_event','coverage_event_id');active=active_events(events);denom=normalize_denominator_snapshot(denominator_snapshot,works,denominator_path,enforce_origin=denominator_snapshot is not None)
 resolved=denom is not None and denom['status']=='RESOLVED'
 result={'denominator_status':'RESOLVED' if resolved else 'DENOMINATOR_UNRESOLVED','denominator_definition':denom['definition'] if denom else None,'denominator_snapshot_ref':denom['snapshot_ref'] if denom else None,'denominator_snapshot_hash':denom['snapshot_hash'] if denom else None,'denominator':len(denom['work_ids']) if resolved else None,'known_work_record_count':len(works),'exclusions':denom['exclusions'] if denom else [],'unknowns':denom['unknowns'] if denom else ['No governed denominator snapshot supplied'],'history_event_count':len(events),'active_accepted_event_count':len(active),'states':{}}
 for state in STATES:
  rows=[r for r in active.values() if r.get('coverage_state')==state and r.get('effect')=='ATTAINED']
  all_ids=sorted({r.get('work_id') for r in rows if r.get('work_id') in works})
  denominator_ids=set(denom['work_ids']) if resolved and denom['dimension']==state else None
  numerator_ids=sorted(set(all_ids)&denominator_ids) if denominator_ids is not None else all_ids
  outside=sorted(set(all_ids)-denominator_ids) if denominator_ids is not None else []
  result['states'][state]={'event_count':len(rows),'attained_count':len(all_ids),'numerator':len(numerator_ids),'denominator_status':'RESOLVED' if denominator_ids is not None else 'DENOMINATOR_UNRESOLVED','denominator':len(denominator_ids) if denominator_ids is not None else None,'covered_work_ids':numerator_ids,'outside_denominator_work_ids':outside,'coverage_fraction':(len(numerator_ids)/len(denominator_ids) if denominator_ids else None)}
 return result
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='command',required=True);sub.add_parser('validate');report_parser=sub.add_parser('report');report_parser.add_argument('--denominator-json');args=ap.parse_args();records,paths=scan_typed_records(with_paths=True)
 if args.command=='validate':
  errors=validate_coverage(records,record_paths=paths,enforce_origins=True)
  if errors:print('COVERAGE VALIDATION FAILED');print('\n'.join('- '+e for e in errors));raise SystemExit(1)
  print('COVERAGE VALIDATION PASSED')
 else:
  denominator=strict_json(Path(args.denominator_json).read_text(encoding='utf-8')) if args.denominator_json else None
  try:report=coverage_report(records,denominator_snapshot=denominator,denominator_path=args.denominator_json,record_paths=paths)
  except ValueError as exc:raise SystemExit(str(exc)) from exc
  print(json.dumps(report,indent=2,sort_keys=True))
if __name__=='__main__':main()
