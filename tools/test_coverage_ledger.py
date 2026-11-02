#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path
MODULE_PATH=Path(__file__).with_name('coverage_ledger.py'); spec=importlib.util.spec_from_file_location('trek_coverage_ledger_test',MODULE_PATH); coverage=importlib.util.module_from_spec(spec); spec.loader.exec_module(coverage)
WORK={'record_type':'work','work_id':'w1','title':'Fixture','medium':'test'}; SOURCE={'record_type':'source','source_id':'s1','source_kind':'transcript','locator':'fixture://s1'}; BINDING={'record_type':'source_work_binding','binding_id':'b1','source_id':'s1','work_id':'w1','lifecycle':'ACCEPTED','mapping_role':'EVIDENCE_BEARING'}
def event(i,state,status='ACCEPTED',role='CONSOLIDATOR',prereqs=None,**extra):
 scope={'work_id':'w1','source_id':extra.get('source_id'),'fixture_partition':'unit'}
 subject_type='SOURCE_WORK_BINDING' if state in {'SOURCE_BOUND','FULL_TEXT_AVAILABLE','STRUCTURALLY_INDEXED'} else 'LOCAL_ENTITY' if state=='ENTITY_LINKED' else 'WORK'
 subject_id=extra.get('binding_id','b1') if subject_type=='SOURCE_WORK_BINDING' else 'l1' if subject_type=='LOCAL_ENTITY' else 'w1'
 row={'record_type':'coverage_event','coverage_event_id':i,'coverage_state':state,'status':status,'effect':'ATTAINED','subject_type':subject_type,'subject_id':subject_id,'scope':scope,'scope_key':coverage.scope_key(scope),'work_id':'w1','producer_role':role,'producer_ref':'fixture:'+i,'basis_refs':['basis:'+i],'prerequisite_event_ids':prereqs or [],'schema_version':'0.2.0','methodology_version':'0.1.0'}
 row.update(extra)
 if 'scope' in extra and 'scope_key' not in extra:row['scope_key']=coverage.scope_key(row['scope'])
 return row
def record_paths(records):
 return {r['coverage_event_id']:coverage.ROOT/'coverage'/'events'/(r['coverage_event_id']+'.json') for r in records if r.get('record_type')=='coverage_event'}
def make_report(records,**kwargs):
 with tempfile.TemporaryDirectory() as tmp:
  original_root=coverage.ROOT;coverage.ROOT=Path(tmp)
  try:
   (coverage.ROOT/'coverage'/'events').mkdir(parents=True)
   paths=record_paths(records)
   for row in records:
    if row.get('record_type')=='coverage_event':paths[row['coverage_event_id']].write_text(json.dumps(row),encoding='utf-8')
   snapshot=kwargs.get('denominator_snapshot')
   if snapshot is not None:
    denominator_dir=coverage.ROOT/'coverage'/'denominators';denominator_dir.mkdir()
    snapshot_path=denominator_dir/'fixture.json';snapshot_path.write_text(json.dumps(snapshot),encoding='utf-8')
    kwargs['denominator_path']=snapshot_path
   return coverage.coverage_report(records,record_paths=paths,**kwargs)
  finally:coverage.ROOT=original_root
def denominator(**overrides):
 row={'record_type':'coverage_denominator_snapshot','snapshot_id':'registry:fixture@abc','dimension':'DISCOVERED','unit_type':'WORK','scope':{'definition':'accepted fixture Work registry'},'registry_head':'main:fixture','status':'RESOLVED','unit_ids':['w1'],'exclusions':[],'blockers':[],'schema_version':'0.2.0','methodology_version':'0.1.0'}
 row.update(overrides);row['snapshot_hash']=coverage.content_hash({k:v for k,v in row.items() if k!='snapshot_hash'});return row
class CoverageLedgerTests(unittest.TestCase):
 def test_authoritative_registry_json_works_are_visible_to_coverage(self):
  with tempfile.TemporaryDirectory() as tmp:
   old_root=coverage.ROOT;coverage.ROOT=Path(tmp)
   try:
    directory=coverage.ROOT/'registry'/'authoritative';directory.mkdir(parents=True)
    (directory/'work.json').write_text(json.dumps(WORK),encoding='utf-8')
    rows=coverage.scan_typed_records()
    self.assertEqual(coverage.index_records(rows,'work','work_id'),{'w1':WORK})
   finally:coverage.ROOT=old_root
 def test_authoritative_registry_json_rejects_untyped_objects(self):
  with tempfile.TemporaryDirectory() as tmp:
   old_root=coverage.ROOT;coverage.ROOT=Path(tmp)
   try:
    directory=coverage.ROOT/'registry'/'authoritative';directory.mkdir(parents=True)
    (directory/'invalid.json').write_text(json.dumps({'work_id':'w1'}),encoding='utf-8')
    with self.assertRaisesRegex(ValueError,'must be a typed object'):
     coverage.scan_typed_records()
   finally:coverage.ROOT=old_root
 def test_typed_research_json_records_are_visible_to_coverage(self):
  with tempfile.TemporaryDirectory() as tmp:
   old_root=coverage.ROOT;coverage.ROOT=Path(tmp)
   try:
    directory=coverage.ROOT/'research'/'tng';directory.mkdir(parents=True)
    (directory/'work.json').write_text(json.dumps(WORK),encoding='utf-8')
    self.assertEqual(coverage.index_records(coverage.scan_typed_records(),'work','work_id'),{'w1':WORK})
   finally:coverage.ROOT=old_root
 def test_direct_report_rejects_self_computed_unverified_denominator(self):
  with self.assertRaisesRegex(ValueError,'unverified denominator snapshot origin'):
   coverage.coverage_report([WORK],denominator_snapshot=denominator())
 def test_denominator_from_outside_authoritative_root_is_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   old_root=coverage.ROOT;coverage.ROOT=Path(tmp)
   try:
    outside=coverage.ROOT/'untrusted.json';snap=denominator();outside.write_text(json.dumps(snap),encoding='utf-8')
    with self.assertRaisesRegex(ValueError,'outside authoritative denominator root'):
     coverage.coverage_report([WORK],denominator_snapshot=snap,denominator_path=outside)
   finally:coverage.ROOT=old_root
 def test_denominator_origin_bytes_must_match_claimed_snapshot(self):
  with tempfile.TemporaryDirectory() as tmp:
   old_root=coverage.ROOT;coverage.ROOT=Path(tmp)
   try:
    directory=coverage.ROOT/'coverage'/'denominators';directory.mkdir(parents=True)
    snap=denominator();path=directory/'fixture.json';path.write_text(json.dumps(denominator(unit_ids=[])),encoding='utf-8')
    with self.assertRaisesRegex(ValueError,'differs from authoritative origin bytes'):
     coverage.coverage_report([WORK],denominator_snapshot=snap,denominator_path=path)
   finally:coverage.ROOT=old_root
 def test_accepted_revocation_removes_current_attainment_but_keeps_history(self):
  attained=event('attained','DISCOVERED',role='LIBRARIAN')
  revoked=event('revoked','DISCOVERED',role='LIBRARIAN',effect='REVOKED',supersedes='attained',reason='confirmed correction')
  result=make_report([WORK,attained,revoked],works={'w1':WORK},denominator_snapshot=denominator())
  self.assertEqual(result['states']['DISCOVERED']['numerator'],0)
  self.assertEqual(result['history_event_count'],2)
 def test_unverified_accepted_event_origin_is_rejected_by_public_report(self):
  accepted=event('forged','DISCOVERED',role='LIBRARIAN')
  with self.assertRaisesRegex(ValueError,'outside authoritative coverage root'):
   coverage.coverage_report([WORK,accepted],record_paths={'forged':coverage.ROOT/'research'/'tng'/'forged.json'})
 def test_origin_path_cannot_substitute_different_event_bytes(self):
  accepted=event('event1','DISCOVERED',role='LIBRARIAN')
  with tempfile.TemporaryDirectory() as tmp:
   old_root=coverage.ROOT;coverage.ROOT=Path(tmp)
   try:
    path=coverage.ROOT/'coverage'/'event1.json';path.parent.mkdir()
    path.write_text(json.dumps(dict(accepted,subject_id='different')))
    with self.assertRaisesRegex(ValueError,'does not match its authoritative origin bytes'):
     coverage.coverage_report([WORK,accepted],record_paths={'event1':path})
   finally:coverage.ROOT=old_root
 def test_typed_subject_and_scope_are_required(self):
  bad=event('bad','DISCOVERED',role='LIBRARIAN')
  del bad['subject_type'];bad['scope_key']='sha256:invalid'
  errors=coverage.validate_coverage([WORK,bad],works={'w1':WORK})
  self.assertTrue(any('missing required property subject_type' in e for e in errors))
  self.assertTrue(any('scope_key does not match' in e for e in errors))
 def test_denominator_hash_must_verify(self):
  snap=denominator();snap['unit_ids'].append('w2')
  with self.assertRaisesRegex(ValueError,'snapshot_hash'):
   coverage.normalize_denominator_snapshot(snap,{'w1':WORK,'w2':dict(WORK,work_id='w2')})
 def test_unresolved_denominator_requires_blocker(self):
  with self.assertRaisesRegex(ValueError,'requires explicit blockers'):
   coverage.normalize_denominator_snapshot(denominator(status='DENOMINATOR_UNRESOLVED'),{'w1':WORK})
 def test_rejected_proposal_cannot_revoke_accepted_history(self):
  accepted=event('old','FULL_TEXT_AVAILABLE',source_id='s1')
  rejected=event('new','FULL_TEXT_AVAILABLE',status='REJECTED',source_id='s1',supersedes='old',reason='unsupported proposal')
  self.assertIn('old',coverage.active_events({'old':accepted,'new':rejected}))
 def test_public_reporting_rejects_forged_accepted_audit(self):
  forged=event('forged','AUDITED',role='TNG',audit_ref='audit:invented')
  with self.assertRaises(ValueError):
   make_report([WORK,forged],works={'w1':WORK},denominator_snapshot=denominator())
 def test_supersession_cannot_cross_source_scope(self):
  original=event('old','FULL_TEXT_AVAILABLE',source_id='s1')
  mutation=event('new','FULL_TEXT_AVAILABLE',source_id='s2',supersedes='old',reason='wrong source')
  errors=coverage.validate_coverage([WORK,SOURCE,original,mutation],works={'w1':WORK},sources={'s1':SOURCE,'s2':dict(SOURCE,source_id='s2')},bindings={})
  self.assertTrue(any('supersession' in err and 'scope' in err for err in errors))
 def test_source_presence_does_not_imply_source_bound(self):
  report=make_report([WORK,SOURCE]); self.assertEqual(report['states']['SOURCE_BOUND']['numerator'],0); self.assertEqual(report['states']['FULL_TEXT_AVAILABLE']['numerator'],0)
 def test_source_bound_does_not_imply_later_ledgers(self):
  discovered=event('d0','DISCOVERED',role='LIBRARIAN'); bound=event('c1','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1',prereqs=['d0']); records=[WORK,SOURCE,BINDING,discovered,bound]; errors=coverage.validate_coverage(records,works={'w1':WORK},sources={'s1':SOURCE},bindings={'b1':BINDING}); self.assertEqual(errors,[]); result=make_report(records,works={'w1':WORK},denominator_snapshot=denominator()); self.assertEqual(result['states']['SOURCE_BOUND']['numerator'],1); self.assertEqual(result['states']['FULL_TEXT_AVAILABLE']['numerator'],0); self.assertEqual(result['states']['CLOSE_READ']['numerator'],0)
 def test_completed_staging_read_does_not_advance_accepted_coverage(self):
  proposed=event('c1','CLOSE_READ',status='PROPOSED',role='TNG',source_id='s1'); report=make_report([WORK,SOURCE,proposed],works={'w1':WORK},denominator_snapshot=denominator()); self.assertEqual(report['states']['CLOSE_READ']['numerator'],0); self.assertEqual(report['history_event_count'],1)
 def test_local_entity_presence_does_not_imply_entity_linked(self):
  local={'record_type':'local_entity','local_entity_id':'l1','work_id':'w1','label':'Known Name'}; report=make_report([WORK,local],works={'w1':WORK},denominator_snapshot=denominator()); self.assertEqual(report['states']['ENTITY_LINKED']['numerator'],0)
 def test_producer_cannot_self_declare_audited(self):
  audited=event('c1','AUDITED',role='TNG',audit_ref='audit:fake'); errors=coverage.validate_coverage([WORK,audited],works={'w1':WORK},sources={},bindings={}); self.assertTrue(any('AUDITED must be produced by AUDITOR' in e for e in errors)); self.assertTrue(any('CROSS_REFERENCED prerequisite' in e for e in errors))
 def test_missing_work_denominator_is_explicitly_unresolved(self):
  report=make_report([]); self.assertEqual(report['denominator_status'],'DENOMINATOR_UNRESOLVED'); self.assertIsNone(report['denominator']); self.assertEqual(report['known_work_record_count'],0)
 def test_known_work_records_without_snapshot_still_leave_denominator_unresolved(self):
  report=make_report([WORK],works={'w1':WORK}); self.assertEqual(report['denominator_status'],'DENOMINATOR_UNRESOLVED'); self.assertEqual(report['known_work_record_count'],1); self.assertIsNone(report['denominator']); self.assertIn('No governed denominator snapshot supplied',report['unknowns'])
 def test_explicit_denominator_snapshot_exposes_definition_snapshot_exclusions_and_unknowns(self):
  discovered=event('d0','DISCOVERED',role='LIBRARIAN'); snap=denominator(exclusions=[{'unit_id':'x','reason':'not in scope'}]); result=make_report([WORK,discovered],works={'w1':WORK},denominator_snapshot=snap); self.assertEqual(result['denominator_status'],'RESOLVED'); self.assertEqual(result['denominator'],1); self.assertEqual(result['denominator_definition'],coverage.canonical({'definition':'accepted fixture Work registry'})); self.assertEqual(result['denominator_snapshot_ref'],'registry:fixture@abc'); self.assertEqual(result['exclusions'],[{'unit_id':'x','reason':'not in scope'}]); self.assertEqual(result['states']['DISCOVERED']['numerator'],1); self.assertEqual(result['states']['DISCOVERED']['denominator'],1); self.assertEqual(result['states']['DISCOVERED']['coverage_fraction'],1.0); self.assertEqual(result['states']['AUDITED']['denominator_status'],'DENOMINATOR_UNRESOLVED')
 def test_denominator_snapshot_cannot_reference_missing_work(self):
  with self.assertRaises(ValueError): make_report([WORK],works={'w1':WORK},denominator_snapshot=denominator(unit_ids=['w-missing']))
 def test_rejected_correction_preserves_prior_accepted_history(self):
  discovered=event('c1','DISCOVERED',role='LIBRARIAN'); correction=event('c2','DISCOVERED',status='REJECTED',role='LIBRARIAN',supersedes='c1',reason='unsupported correction'); records=[WORK,discovered,correction]; errors=coverage.validate_coverage(records,works={'w1':WORK},sources={},bindings={}); self.assertEqual(errors,[]); result=make_report(records,works={'w1':WORK},denominator_snapshot=denominator()); self.assertEqual(result['states']['DISCOVERED']['numerator'],1); self.assertEqual(result['history_event_count'],2)
 def test_full_text_is_bound_to_specific_source_and_completeness_scope(self):
  discovered=event('d0','DISCOVERED',role='LIBRARIAN'); bound=event('c1','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1',prereqs=['d0']); full=event('c2','FULL_TEXT_AVAILABLE',role='TNG',source_id='s1',prereqs=['c1'],representation_scope={'representation_type':'complete transcript','completeness_scope':'full research representation','limitations':'not audiovisual-master inspection'}); records=[WORK,SOURCE,discovered,bound,full]; errors=coverage.validate_coverage(records,works={'w1':WORK},sources={'s1':SOURCE},bindings={'b1':BINDING}); self.assertEqual(errors,[])
 def test_source_bound_fails_closed_without_librarian_binding(self):
  discovered=event('d0','DISCOVERED',role='LIBRARIAN'); bound=event('c1','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b-missing',prereqs=['d0']); errors=coverage.validate_coverage([WORK,SOURCE,discovered,bound],works={'w1':WORK},sources={'s1':SOURCE},bindings={}); self.assertTrue(any('requires governed source_work_binding' in e for e in errors))
 def test_close_read_requires_structurally_indexed_prerequisite_same_source(self):
  close=event('c1','CLOSE_READ',role='TNG',source_id='s1'); errors=coverage.validate_coverage([WORK,SOURCE,close],works={'w1':WORK},sources={'s1':SOURCE},bindings={}); self.assertTrue(any('STRUCTURALLY_INDEXED prerequisite' in e for e in errors))
if __name__=='__main__':unittest.main()
