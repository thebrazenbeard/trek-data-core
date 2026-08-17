#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, unittest
from pathlib import Path
MODULE_PATH=Path(__file__).with_name('coverage_ledger.py'); spec=importlib.util.spec_from_file_location('trek_coverage_ledger_test',MODULE_PATH); coverage=importlib.util.module_from_spec(spec); spec.loader.exec_module(coverage)
WORK={'record_type':'work','work_id':'w1','title':'Fixture','medium':'test'}; SOURCE={'record_type':'source','source_id':'s1','source_kind':'transcript','locator':'fixture://s1'}; BINDING={'record_type':'source_work_binding','binding_id':'b1','source_id':'s1','work_id':'w1','status':'ACCEPTED','mapping_role':'EVIDENCE_BEARING'}
def event(i,state,status='ACCEPTED',role='CONSOLIDATOR',prereqs=None,**extra):
 row={'record_type':'coverage_event','coverage_event_id':i,'coverage_state':state,'status':status,'work_id':'w1','producer_role':role,'producer_ref':'fixture:'+i,'basis_refs':['basis:'+i],'prerequisite_event_ids':prereqs or [],'schema_version':'0.1.0','methodology_version':'0.1.0'}; row.update(extra); return row
class CoverageLedgerTests(unittest.TestCase):
 def test_source_presence_does_not_imply_source_bound(self):
  report=coverage.coverage_report([WORK,SOURCE]); self.assertEqual(report['states']['SOURCE_BOUND']['covered_work_count'],0); self.assertEqual(report['states']['FULL_TEXT_AVAILABLE']['covered_work_count'],0)
 def test_source_bound_does_not_imply_later_ledgers(self):
  bound=event('c1','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1'); records=[WORK,SOURCE,bound]; errors=coverage.validate_coverage(records,works={'w1':WORK},sources={'s1':SOURCE},bindings={'b1':BINDING}); self.assertEqual(errors,[]); report=coverage.coverage_report(records,works={'w1':WORK}); self.assertEqual(report['states']['SOURCE_BOUND']['covered_work_count'],1); self.assertEqual(report['states']['FULL_TEXT_AVAILABLE']['covered_work_count'],0); self.assertEqual(report['states']['CLOSE_READ']['covered_work_count'],0)
 def test_completed_staging_read_does_not_advance_accepted_coverage(self):
  proposed=event('c1','CLOSE_READ',status='PROPOSED',role='TNG',source_id='s1'); report=coverage.coverage_report([WORK,SOURCE,proposed],works={'w1':WORK}); self.assertEqual(report['states']['CLOSE_READ']['covered_work_count'],0); self.assertEqual(report['history_event_count'],1)
 def test_local_entity_presence_does_not_imply_entity_linked(self):
  local={'record_type':'local_entity','local_entity_id':'l1','work_id':'w1','label':'Known Name'}; report=coverage.coverage_report([WORK,local],works={'w1':WORK}); self.assertEqual(report['states']['ENTITY_LINKED']['covered_work_count'],0)
 def test_producer_cannot_self_declare_audited(self):
  audited=event('c1','AUDITED',role='TNG',audit_ref='audit:fake'); errors=coverage.validate_coverage([WORK,audited],works={'w1':WORK},sources={},bindings={}); self.assertTrue(any('AUDITED must be produced by AUDITOR' in e for e in errors)); self.assertTrue(any('CROSS_REFERENCED prerequisite' in e for e in errors))
 def test_missing_work_denominator_is_explicitly_unresolved(self):
  report=coverage.coverage_report([]); self.assertEqual(report['denominator_status'],'DENOMINATOR_UNRESOLVED'); self.assertIsNone(report['work_denominator'])
 def test_rejected_correction_supersedes_prior_without_erasing_history(self):
  discovered=event('c1','DISCOVERED',role='LIBRARIAN'); correction=event('c2','DISCOVERED',status='REJECTED',role='LIBRARIAN',supersedes='c1',reason='Work identity withdrawn'); records=[WORK,discovered,correction]; errors=coverage.validate_coverage(records,works={'w1':WORK},sources={},bindings={}); self.assertEqual(errors,[]); report=coverage.coverage_report(records,works={'w1':WORK}); self.assertEqual(report['states']['DISCOVERED']['covered_work_count'],0); self.assertEqual(report['history_event_count'],2)
 def test_full_text_is_bound_to_specific_source_and_completeness_scope(self):
  bound=event('c1','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b1'); full=event('c2','FULL_TEXT_AVAILABLE',role='TNG',source_id='s1',prereqs=['c1'],representation_scope={'representation_type':'complete transcript','completeness_scope':'full research representation','limitations':'not audiovisual-master inspection'}); records=[WORK,SOURCE,bound,full]; errors=coverage.validate_coverage(records,works={'w1':WORK},sources={'s1':SOURCE},bindings={'b1':BINDING}); self.assertEqual(errors,[])
 def test_source_bound_fails_closed_without_librarian_binding(self):
  bound=event('c1','SOURCE_BOUND',role='LIBRARIAN',source_id='s1',binding_id='b-missing'); errors=coverage.validate_coverage([WORK,SOURCE,bound],works={'w1':WORK},sources={'s1':SOURCE},bindings={}); self.assertTrue(any('requires governed source_work_binding' in e for e in errors))
 def test_close_read_requires_structurally_indexed_prerequisite_same_source(self):
  close=event('c1','CLOSE_READ',role='TNG',source_id='s1'); errors=coverage.validate_coverage([WORK,SOURCE,close],works={'w1':WORK},sources={'s1':SOURCE},bindings={}); self.assertTrue(any('STRUCTURALLY_INDEXED prerequisite' in e for e in errors))
if __name__=='__main__':unittest.main()
