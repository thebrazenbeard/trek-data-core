#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path
MODULE_PATH=Path(__file__).with_name('coverage_ledger.py'); spec=importlib.util.spec_from_file_location('trek_coverage_ledger_test',MODULE_PATH); coverage=importlib.util.module_from_spec(spec); spec.loader.exec_module(coverage)
WORK={'record_type':'work','work_id':'w1','title':'Fixture','work_type':'EPISODE','parent_work_id':None,'component_label':None,'status':'ACCEPTED','fixture_only':False}
SOURCE={'record_type':'source','source_id':'s1','status':'ACCEPTED','source_kind':'TRANSCRIPT','provider':'synthetic-test','locator':'fixture://s1','provider_metadata':{},'source_version':'fixture','retrieved_at':'2026-11-02T00:00:00Z','content_hash':'sha256:'+'a'*64,'content_fingerprint':None,'source_variant':'SYNTHETIC','provenance_family':'synthetic-test','independence_group':'synthetic-test','derived_from':[],'fixture_only':False}
BINDING={'record_type':'source_work_binding','binding_id':'b1','source_id':'s1','work_id':'w1','lifecycle':'ACCEPTED','mapping_role':'EVIDENCE_BEARING','source_scope':{'scope_type':'WHOLE','locator':None},'work_scope':{'scope_type':'WHOLE','component_label':None},'method':'synthetic test only','basis':[{'kind':'BYTE_HASH','value':SOURCE['content_hash']}],'exclusive_scope_key':None,'supersedes_binding_id':None,'notes':'Isolated fixture, never admitted corpus','fixture_only':False}
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
   authoritative=kwargs.pop('authoritative_works',None)
   if authoritative is None:
    candidates=kwargs.get('works') or coverage.index_records(records,'work','work_id')
    authoritative=[w for w in candidates.values() if w.get('status')=='ACCEPTED' and w.get('fixture_only') is False]
   if authoritative:
    authorized_root=coverage.ROOT/'registry'/'authoritative';authorized_root.mkdir(parents=True)
    for w in authoritative:
     (authorized_root/f"{w['work_id']}.json").write_text(json.dumps(w),encoding='utf-8')
   allowed_sources=kwargs.pop('authoritative_sources',None)
   if allowed_sources is None:
    candidates=kwargs.get('sources') or coverage.index_records(records,'source','source_id')
    allowed_sources=[s for s in candidates.values() if s.get('status')=='ACCEPTED' and s.get('fixture_only') is False]
   allowed_bindings=kwargs.pop('authoritative_bindings',None)
   if allowed_bindings is None:
    candidates=kwargs.get('bindings') or coverage.index_records(records,'source_work_binding','binding_id')
    allowed_bindings=[b for b in candidates.values() if b.get('lifecycle')=='ACCEPTED' and b.get('fixture_only') is False]
   if allowed_sources or allowed_bindings:
    authorized_root=coverage.ROOT/'registry'/'authoritative';authorized_root.mkdir(parents=True,exist_ok=True)
    for s in allowed_sources:
     (authorized_root/f"{s['source_id']}.json").write_text(json.dumps(s),encoding='utf-8')
    for b in allowed_bindings:
     (authorized_root/f"{b['binding_id']}.json").write_text(json.dumps(b),encoding='utf-8')
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
 row={'record_type':'coverage_denominator_snapshot','snapshot_id':'registry:fixture@abc','dimension':'DISCOVERED','unit_type':'WORK','scope':{'claim':'ACCEPTED_AUTHORITATIVE_WORK_REGISTRY_ROSTER','work_type':'EPISODE','parent_work_id':None},'registry_head':coverage.accepted_registry_head({'w1':WORK}),'status':'RESOLVED','unit_ids':['w1'],'exclusions':[],'blockers':[],'schema_version':'0.2.0','methodology_version':'0.1.0'}
 row.update(overrides);row['snapshot_hash']=coverage.content_hash({k:v for k,v in row.items() if k!='snapshot_hash'});return row
class CoverageLedgerTests(unittest.TestCase):
 def test_scanner_rejects_symlinked_coverage_file_and_root(self):
  with tempfile.TemporaryDirectory() as tmp:
   old_root=coverage.ROOT;coverage.ROOT=Path(tmp)/'repo'
   try:
    events=coverage.ROOT/'coverage'/'events';events.mkdir(parents=True)
    (events/'original.jsonl').write_text('{}\n',encoding='utf-8')
    (events/'alias.jsonl').symlink_to(events/'original.jsonl')
    with self.assertRaisesRegex(ValueError,'symlink'):
     coverage.scan_typed_records()
    (events/'alias.jsonl').unlink()
    outside=Path(tmp)/'outside';outside.mkdir()
    (coverage.ROOT/'coverage').rename(outside/'coverage-original')
    (coverage.ROOT/'coverage').symlink_to(outside/'coverage-original',target_is_directory=True)
    with self.assertRaisesRegex(ValueError,'symlink'):
     coverage.scan_typed_records()
   finally:coverage.ROOT=old_root

 def test_public_report_rejects_symlinked_accepted_event_origin(self):
  with tempfile.TemporaryDirectory() as tmp:
   old_root=coverage.ROOT;coverage.ROOT=Path(tmp)/'repo'
   try:
    registry=coverage.ROOT/'registry'/'authoritative';registry.mkdir(parents=True)
    (registry/'w1.json').write_text(json.dumps(WORK),encoding='utf-8')
    events=coverage.ROOT/'coverage'/'events';events.mkdir(parents=True)
    discovered=event('via-alias','DISCOVERED',role='LIBRARIAN')
    direct=events/'direct.jsonl';direct.write_text(json.dumps(discovered)+'\n',encoding='utf-8')
    alias=events/'alias.jsonl';alias.symlink_to(direct)
    with self.assertRaisesRegex(ValueError,'symlink'):
     coverage.coverage_report([WORK,discovered],record_paths={'via-alias':alias})
   finally:coverage.ROOT=old_root

 def test_accepted_discovered_cannot_claim_a_different_work_in_governed_scope(self):
  discovered=event('forged-scope','DISCOVERED',role='LIBRARIAN',scope={'work_id':'w-different','source_id':None})
  with self.assertRaisesRegex(ValueError,'scope.*Work|Work.*scope'):
   make_report([WORK,discovered],works={'w1':WORK})
 def test_accepted_full_text_cannot_claim_a_different_source_in_governed_scope(self):
  discovered=event('d0','DISCOVERED',role='LIBRARIAN')
  bound=event('b0','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1',prereqs=['d0'])
  full=event('f0','FULL_TEXT_AVAILABLE',role='TNG',source_id='s1',prereqs=['b0'],scope={'work_id':'w1','source_id':'s-different'},representation_scope={'representation_type':'synthetic transcript','completeness_scope':'full synthetic fixture'})
  with self.assertRaisesRegex(ValueError,'scope.*Source|Source.*scope'):
   make_report([WORK,SOURCE,BINDING,discovered,bound,full])
 def test_accepted_discovered_requires_its_work_subject_identity(self):
  discovered=event('forged-subject','DISCOVERED',role='LIBRARIAN',subject_type='WORK',subject_id='w-different')
  with self.assertRaisesRegex(ValueError,'subject.*Work|Work.*subject'):
   make_report([WORK,discovered])
 def test_supersession_cannot_cross_work_with_the_same_forged_subject_and_scope(self):
  first=event('first','DISCOVERED',role='LIBRARIAN')
  second=event('second','DISCOVERED',role='LIBRARIAN',work_id='w2',subject_id='w1',supersedes='first',effect='REVOKED',reason='forged correction')
  other=dict(WORK,work_id='w2',title='Other')
  errors=coverage.validate_coverage([WORK,other,first,second],works={'w1':WORK,'w2':other})
  self.assertTrue(any('supersession' in error and 'Work' in error for error in errors),errors)
 def test_source_bound_rejects_proposed_source_with_accepted_binding(self):
  proposed=dict(SOURCE,status='PROPOSED')
  discovered=event('d0','DISCOVERED',role='LIBRARIAN')
  bound=event('b0','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1',prereqs=['d0'])
  with self.assertRaisesRegex(ValueError,'Source|ACCEPTED|authoritative'):
   make_report([WORK,proposed,BINDING,discovered,bound],works={'w1':WORK},denominator_snapshot=denominator())
 def test_source_bound_rejects_counterfeit_in_memory_source_binding(self):
  claimed=dict(SOURCE,status='ACCEPTED')
  discovered=event('d0','DISCOVERED',role='LIBRARIAN')
  bound=event('b0','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1',prereqs=['d0'])
  with self.assertRaisesRegex(ValueError,'authoritative|binding|Source'):
   make_report([WORK,claimed,BINDING,discovered,bound],works={'w1':WORK},denominator_snapshot=denominator(),authoritative_sources=[],authoritative_bindings=[])
 def test_source_bound_rejects_unfiled_binding_with_genuine_authoritative_source(self):
  discovered=event('d0','DISCOVERED',role='LIBRARIAN')
  bound=event('b0','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1',prereqs=['d0'])
  with self.assertRaisesRegex(ValueError,'disk-backed authoritative Librarian'):
   make_report([WORK,SOURCE,BINDING,discovered,bound],works={'w1':WORK},denominator_snapshot=denominator(),authoritative_sources=[SOURCE],authoritative_bindings=[])
 def test_source_bound_rejects_mismatched_sha256_binding_basis(self):
  bad_binding=dict(BINDING,basis=[{'kind':'BYTE_HASH','value':'sha256:'+'b'*64}])
  discovered=event('d0','DISCOVERED',role='LIBRARIAN')
  bound=event('b0','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1',prereqs=['d0'])
  with self.assertRaisesRegex(ValueError,'exact accepted Source SHA-256 BYTE_HASH'):
   make_report([WORK,SOURCE,bad_binding,discovered,bound],works={'w1':WORK},denominator_snapshot=denominator())
 def test_source_bound_rejects_blank_binding_method(self):
  missing_method=dict(BINDING,method='')
  discovered=event('d0','DISCOVERED',role='LIBRARIAN')
  bound=event('b0','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1',prereqs=['d0'])
  with self.assertRaisesRegex(ValueError,'binding method'):
   make_report([WORK,SOURCE,missing_method,discovered,bound],works={'w1':WORK},denominator_snapshot=denominator())
 def test_source_bound_rejects_accepted_binding_without_content_basis(self):
  claimed=dict(SOURCE,status='ACCEPTED')
  invalid=dict(BINDING,basis=[])
  discovered=event('d0','DISCOVERED',role='LIBRARIAN')
  bound=event('b0','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1',prereqs=['d0'])
  with self.assertRaisesRegex(ValueError,'basis|hash|fingerprint|authoritative'):
   make_report([WORK,claimed,invalid,discovered,bound],works={'w1':WORK},denominator_snapshot=denominator())
 def test_source_bound_rejects_forged_subject_and_scope(self):
  discovered=event('d0','DISCOVERED',role='LIBRARIAN')
  bound=event('b0','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1',prereqs=['d0'],subject_type='WORK',subject_id='forged:subject',scope={'work_id':'w1','source_id':'s-mismatch'})
  with self.assertRaisesRegex(ValueError,'subject|scope'):
   make_report([WORK,SOURCE,BINDING,discovered,bound],works={'w1':WORK},denominator_snapshot=denominator())
 def test_resolved_denominator_rejects_proposed_work_even_with_self_hash(self):
  proposed=dict(WORK,status='PROPOSED')
  with self.assertRaisesRegex(ValueError,'ACCEPTED|authoritative|registry'):
   make_report([proposed],works={'w1':proposed},denominator_snapshot=denominator(registry_head='invented:unverified'))
 def test_resolved_denominator_rejects_forged_registry_head(self):
  with self.assertRaisesRegex(ValueError,'registry_head|registry'):
   make_report([WORK],works={'w1':WORK},denominator_snapshot=denominator(registry_head='invented:unverified'))
 def test_resolved_denominator_rejects_research_only_accepted_work(self):
  accepted=dict(WORK,status='ACCEPTED',fixture_only=False,work_type='EPISODE')
  with self.assertRaisesRegex(ValueError,'authoritative|registry'):
   make_report([accepted],works={'w1':accepted},denominator_snapshot=denominator(),authoritative_works=[])
 def test_resolved_denominator_rejects_partial_roster(self):
  with self.assertRaisesRegex(ValueError,'roster|unit_ids|scope'):
   make_report([WORK],works={'w1':WORK},denominator_snapshot=denominator(unit_ids=[]))
 def test_accepted_discovered_cannot_count_proposed_work(self):
  proposed=dict(WORK,status='PROPOSED')
  discovered=event('accepted_on_proposal','DISCOVERED',role='LIBRARIAN')
  with self.assertRaisesRegex(ValueError,'ACCEPTED|authoritative|Work'):
   make_report([proposed,discovered],works={'w1':proposed})
 def test_accepted_discovered_cannot_count_research_only_accepted_work(self):
  discovered=event('accepted_from_research','DISCOVERED',role='LIBRARIAN')
  with self.assertRaisesRegex(ValueError,'disk-backed authoritative'):
   make_report([WORK,discovered],works={'w1':WORK},authoritative_works=[])
 def test_resolved_denominator_requires_all_scoped_accepted_works(self):
  second=dict(WORK,work_id='w2',title='Second fixture')
  registry_head=coverage.accepted_registry_head({'w1':WORK,'w2':second})
  snap=denominator(registry_head=registry_head)
  with self.assertRaisesRegex(ValueError,'complete authoritative accepted Work roster'):
   make_report([WORK,second],works={'w1':WORK,'w2':second},denominator_snapshot=snap)
 def test_resolved_denominator_rejects_relabelled_authoritative_work(self):
  altered=dict(WORK,title='Unreviewed replacement')
  with self.assertRaisesRegex(ValueError,'registry_head'):
   make_report([altered],works={'w1':altered},denominator_snapshot=denominator())
 def test_authoritative_registry_parent_symlink_is_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   old_root=coverage.ROOT;coverage.ROOT=Path(tmp)/'repo'
   try:
    coverage.ROOT.mkdir();outside=Path(tmp)/'outside';outside.mkdir()
    (coverage.ROOT/'registry').symlink_to(outside,target_is_directory=True)
    with self.assertRaisesRegex(ValueError,'symlink'):
     coverage.authoritative_work_roster()
   finally:coverage.ROOT=old_root
 def test_duplicate_json_keys_in_authoritative_work_are_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   old_root=coverage.ROOT;coverage.ROOT=Path(tmp)
   try:
    registry=coverage.ROOT/'registry'/'authoritative';registry.mkdir(parents=True)
    (registry/'bad.json').write_text('{"record_type":"work","work_id":"w1","work_id":"w2","status":"ACCEPTED"}',encoding='utf-8')
    with self.assertRaisesRegex(ValueError,'duplicate JSON key'):
     coverage.authoritative_work_roster()
   finally:coverage.ROOT=old_root
 def test_fixture_only_accepted_work_cannot_resolve_denominator(self):
  fixture=dict(WORK,fixture_only=True)
  with self.assertRaisesRegex(ValueError,'no nonfixture ACCEPTED'):
   make_report([fixture],works={'w1':fixture},denominator_snapshot=denominator(),authoritative_works=[fixture])
 def test_resolved_denominator_rejects_unscoped_whole_universe_claim(self):
  with self.assertRaisesRegex(ValueError,'scope|roster|claim'):
   make_report([WORK],works={'w1':WORK},denominator_snapshot=denominator(scope={'definition':'complete Star Trek episode universe'}))
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
  discovered=event('d0','DISCOVERED',role='LIBRARIAN'); snap=denominator(exclusions=[{'unit_id':'x','reason':'not in scope'}]); result=make_report([WORK,discovered],works={'w1':WORK},denominator_snapshot=snap); self.assertEqual(result['denominator_status'],'RESOLVED'); self.assertEqual(result['denominator'],1); self.assertEqual(result['denominator_definition'],coverage.canonical({'claim':'ACCEPTED_AUTHORITATIVE_WORK_REGISTRY_ROSTER','work_type':'EPISODE','parent_work_id':None})); self.assertEqual(result['denominator_snapshot_ref'],'registry:fixture@abc'); self.assertEqual(result['exclusions'],[{'unit_id':'x','reason':'not in scope'}]); self.assertEqual(result['states']['DISCOVERED']['numerator'],1); self.assertEqual(result['states']['DISCOVERED']['denominator'],1); self.assertEqual(result['states']['DISCOVERED']['coverage_fraction'],1.0); self.assertEqual(result['states']['AUDITED']['denominator_status'],'DENOMINATOR_UNRESOLVED')
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
