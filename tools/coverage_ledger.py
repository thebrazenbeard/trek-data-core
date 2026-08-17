#!/usr/bin/env python3
"""Validate and report append-only independent Trek coverage ledgers.

Coverage events never infer later states. Accepted SOURCE_BOUND remains impossible until a
Librarian-owned accepted evidence-bearing source_work_binding exists.
"""
from __future__ import annotations
import argparse, importlib.util, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/'schema'/'coverage-event.schema.json'
PB=Path(__file__).with_name('projection_bundle.py'); SPEC=importlib.util.spec_from_file_location('trek_coverage_schema',PB); schema_tools=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(schema_tools)
STATES=('DISCOVERED','SOURCE_BOUND','FULL_TEXT_AVAILABLE','STRUCTURALLY_INDEXED','CLOSE_READ','SEMANTICALLY_ANALYZED','ENTITY_LINKED','CROSS_REFERENCED','AUDITED')
PREDECESSOR={state:STATES[i-1] for i,state in enumerate(STATES) if i>0}
SOURCE_STATES={'SOURCE_BOUND','FULL_TEXT_AVAILABLE','STRUCTURALLY_INDEXED','CLOSE_READ','SEMANTICALLY_ANALYZED'}
RESEARCH_ROLES={'TOS','TAS','TNG','DS9','VOY','ENT','DIS','SHORT','PIC','LD','PRO','SNW','SFA','FILMS','LIT'}


def canonical(v):return schema_tools.canonical(v)
def read_jsonl(path):
 rows=[]
 if not Path(path).exists():return rows
 for line_no,raw in enumerate(Path(path).read_text(encoding='utf-8').splitlines(),1):
  if not raw.strip():continue
  row=json.loads(raw)
  if not isinstance(row,dict):raise ValueError(f'{path}:{line_no}: row must be object')
  rows.append(row)
 return rows

def scan_typed_records():
 records=[]
 for base in (ROOT/'research',ROOT/'external',ROOT/'migrations',ROOT/'coverage',ROOT/'registry'):
  if not base.exists():continue
  for path in sorted(base.rglob('*.jsonl')):
   records.extend(read_jsonl(path))
  if base.name=='coverage':
   for path in sorted(base.rglob('*.json')):
    row=json.loads(path.read_text(encoding='utf-8'))
    if isinstance(row,dict) and row.get('record_type'):records.append(row)
 return records

def index_records(records,record_type,id_key):
 out={}
 for row in records:
  if row.get('record_type')!=record_type:continue
  rid=row.get(id_key)
  if not rid:continue
  if rid in out:raise ValueError(f'duplicate {record_type} id {rid}')
  out[rid]=row
 return out

def active_events(events):
 superseded={row.get('supersedes') for row in events.values() if row.get('supersedes') and row.get('status') in {'ACCEPTED','REJECTED'}}
 return {eid:row for eid,row in events.items() if row.get('status')=='ACCEPTED' and eid not in superseded}
def coverage_key(row):return (row.get('coverage_state'),row.get('work_id'),row.get('source_id') if row.get('coverage_state') in SOURCE_STATES else None)
def role_errors(row):
 state=row.get('coverage_state'); role=row.get('producer_role'); errors=[]
 if state in {'DISCOVERED','SOURCE_BOUND'} and role!='LIBRARIAN':errors.append(f'{state} must be produced by LIBRARIAN')
 if state in {'CLOSE_READ','SEMANTICALLY_ANALYZED'} and role not in RESEARCH_ROLES:errors.append(f'{state} must be produced by a research lane role')
 if state in {'ENTITY_LINKED','CROSS_REFERENCED'} and role!='CONSOLIDATOR':errors.append(f'{state} must be produced by CONSOLIDATOR')
 if state=='AUDITED' and role!='AUDITOR':errors.append('AUDITED must be produced by AUDITOR')
 return errors

def validate_coverage(records,works=None,sources=None,bindings=None):
 works=works if works is not None else index_records(records,'work','work_id'); sources=sources if sources is not None else index_records(records,'source','source_id'); bindings=bindings if bindings is not None else index_records(records,'source_work_binding','binding_id')
 events=index_records(records,'coverage_event','coverage_event_id'); schema=json.loads(SCHEMA.read_text(encoding='utf-8')); errors=[]
 for eid,row in events.items():
  for err in schema_tools.schema_errors(row,schema):errors.append(f'{eid}: schema: {err}')
  prereqs=row.get('prerequisite_event_ids',[])
  if len(prereqs)!=len(set(prereqs)):errors.append(f'{eid}: duplicate prerequisite_event_ids')
  if row.get('supersedes'):
   predecessor=events.get(row['supersedes'])
   if predecessor is None:errors.append(f'{eid}: supersedes missing coverage event {row["supersedes"]}')
   else:
    if predecessor.get('work_id')!=row.get('work_id') or predecessor.get('coverage_state')!=row.get('coverage_state'):errors.append(f'{eid}: supersession must preserve work_id and coverage_state')
    if row.get('status') in {'ACCEPTED','REJECTED'} and not isinstance(row.get('reason'),str):errors.append(f'{eid}: correction requires reason')
 for start in events:
  seen=set(); current=start
  while current:
   if current in seen:errors.append(f'coverage supersession cycle at {current}');break
   seen.add(current); row=events.get(current); current=row.get('supersedes') if row else None
 active=active_events(events)
 grouped={}
 for eid,row in active.items():grouped.setdefault(coverage_key(row),[]).append(eid)
 for key,ids in grouped.items():
  if len(ids)>1:errors.append(f'multiple active accepted coverage events for {key}: {sorted(ids)}')
 for eid,row in active.items():
  state=row['coverage_state']; work_id=row['work_id']; source_id=row.get('source_id')
  if work_id not in works:errors.append(f'{eid}: accepted coverage references missing Work {work_id}')
  errors.extend(f'{eid}: {err}' for err in role_errors(row))
  if state in SOURCE_STATES:
   if not source_id:errors.append(f'{eid}: {state} requires source_id')
   elif source_id not in sources:errors.append(f'{eid}: accepted coverage references missing Source {source_id}')
  if state=='SOURCE_BOUND':
   binding_id=row.get('binding_id'); binding=bindings.get(binding_id) if binding_id else None
   if not binding_id:errors.append(f'{eid}: SOURCE_BOUND requires binding_id')
   elif binding is None:errors.append(f'{eid}: SOURCE_BOUND requires governed source_work_binding {binding_id}; Librarian binding surface is unavailable or reference is missing')
   else:
    if binding.get('status')!='ACCEPTED':errors.append(f'{eid}: SOURCE_BOUND requires ACCEPTED binding {binding_id}')
    if binding.get('mapping_role')!='EVIDENCE_BEARING':errors.append(f'{eid}: metadata-only binding cannot establish SOURCE_BOUND')
    if binding.get('work_id')!=work_id or binding.get('source_id')!=source_id:errors.append(f'{eid}: binding Source/Work context does not match coverage event')
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

def coverage_report(records,works=None):
 works=works if works is not None else index_records(records,'work','work_id'); events=index_records(records,'coverage_event','coverage_event_id'); active=active_events(events)
 result={'denominator_status':'RESOLVED' if works else 'DENOMINATOR_UNRESOLVED','work_denominator':len(works) if works else None,'history_event_count':len(events),'active_accepted_event_count':len(active),'states':{}}
 for state in STATES:
  rows=[r for r in active.values() if r.get('coverage_state')==state]; work_ids=sorted({r.get('work_id') for r in rows if r.get('work_id') in works}); result['states'][state]={'event_count':len(rows),'covered_work_count':len(work_ids),'covered_work_ids':work_ids}
 return result

def main():
 ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='command',required=True); sub.add_parser('validate'); sub.add_parser('report'); args=sub.parse_args(); records=scan_typed_records()
 if args.command=='validate':
  errors=validate_coverage(records)
  if errors:
   print('COVERAGE VALIDATION FAILED');print('\n'.join('- '+e for e in errors));raise SystemExit(1)
  print('COVERAGE VALIDATION PASSED')
 else:print(json.dumps(coverage_report(records),indent=2,sort_keys=True))
if __name__=='__main__':main()
