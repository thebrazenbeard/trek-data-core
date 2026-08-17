#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

MODULE_PATH=Path(__file__).with_name('build_projection.py'); spec=importlib.util.spec_from_file_location('trek_build_projection',MODULE_PATH); projection=importlib.util.module_from_spec(spec); spec.loader.exec_module(projection)

def fixture_records(source_hash='sha256:source-a', assertion_status='ACCEPTED', proposed='STABLE', object_value=None):
 if object_value is None: object_value={'value':'fixture'}
 assertion={'record_type':'assertion','assertion_id':'assertion-1','subject_type':'LOCAL_ENTITY','subject':'local-1','predicate':'CLAIMS','object':object_value,'evidence':['evidence-1'],'status':assertion_status,'scope':{'worker_scope':'fixture'}}
 if proposed is not None: assertion['proposed_projection_status']=proposed
 return [
  {'record_type':'source','source_id':'source-1','source_kind':'transcript','locator':'fixture://source-1','content_hash':source_hash,'retrieved_at':'2026-08-14T00:00:00Z','source_variant':'v1','provenance_family':'family-a','derived_from':[]},
  {'record_type':'work','work_id':'work-1','title':'Fixture Work','medium':'test','continuity_scope':'fixture'},
  {'record_type':'local_entity','local_entity_id':'local-1','work_id':'work-1','label':'Fixture Entity'},
  {'record_type':'evidence','evidence_id':'evidence-1','source_id':'source-1','work_id':'work-1','evidence_kind':'depiction','locator':{'line':1},'observed':{'event':'fixture'},'frame':'PRIMARY','epistemic_status':'DIRECT','passage_fingerprint':'fp-1'},
  assertion,
 ]

def decision(i,t,subject_type,subject_id,payload,status='ACCEPTED',sup=None):
 r={'record_type':'reconciliation_decision','decision_id':i,'decision_type':t,'subject_type':subject_type,'subject_id':subject_id,'payload':payload,'status':status,'evidence':['evidence-1'],'method':'fixture'}
 if sup: r['supersedes']=sup; r['reason']='fixture correction'
 return r

def status_decision(value='STABLE'):
 return decision('status-1','ASSERTION_PROJECTION_STATUS','ASSERTION','assertion-1',{'projection_status':value})

class LogicalProjectionTests(unittest.TestCase):
 def test_accepted_assertion_without_projection_decision_fails_closed_to_unresolved(self):
  result=projection.build_logical_projection(fixture_records(proposed='STABLE'),[])
  self.assertEqual(result['facts'],[]); self.assertEqual(result['contested'],[]); self.assertEqual(result['unresolved'][0]['projection_status'],'UNRESOLVED'); self.assertEqual(result['unresolved'][0]['projection_reason'],'MISSING_PROJECTION_STATUS')
 def test_worker_proposed_projection_status_is_preserved_but_not_authoritative(self):
  result=projection.build_logical_projection(fixture_records(proposed='CONTESTED'),[status_decision('STABLE')]); fact=result['facts'][0]
  self.assertEqual(fact['proposed_projection_status'],'CONTESTED'); self.assertEqual(fact['projection_status'],'STABLE')
 def test_disposition_can_promote_proposed_assertion_without_mutating_record(self):
  ds=[decision('disp-1','ASSERTION_DISPOSITION','ASSERTION','assertion-1',{'disposition':'ACCEPTED'}),status_decision('STABLE')]
  result=projection.build_logical_projection(fixture_records(assertion_status='PROPOSED'),ds); fact=result['facts'][0]
  self.assertEqual(fact['status'],'PROPOSED'); self.assertEqual(fact['effective_assertion_status'],'ACCEPTED'); self.assertEqual(fact['assertion_disposition_decision_id'],'disp-1')
 def test_disposition_can_demote_accepted_assertion(self):
  result=projection.build_logical_projection(fixture_records(),[decision('disp-1','ASSERTION_DISPOSITION','ASSERTION','assertion-1',{'disposition':'REJECTED'})])
  self.assertEqual(result['facts'],[]); self.assertEqual(result['contested'],[]); self.assertEqual(result['unresolved'],[]); self.assertEqual(len(result['assertion_history']),1)
 def test_projection_status_controls_partition_separately_from_disposition(self):
  result=projection.build_logical_projection(fixture_records(),[status_decision('CONTESTED')])
  self.assertEqual(result['facts'],[]); self.assertEqual(result['unresolved'],[]); self.assertEqual(result['contested'][0]['status'],'ACCEPTED'); self.assertEqual(result['contested'][0]['effective_assertion_status'],'ACCEPTED'); self.assertEqual(result['contested'][0]['projection_status'],'CONTESTED')
 def test_keyed_scope_resolutions_coexist_without_rewriting_worker_scope(self):
  ds=[decision('scope-1','SCOPE_RESOLUTION','ASSERTION','assertion-1',{'resolution_key':'CONTINUITY_SCOPE','resolution':'alternate'}),decision('scope-2','SCOPE_RESOLUTION','ASSERTION','assertion-1',{'resolution_key':'TIMELINE_SCOPE','resolution':'branch-a'}),status_decision('STABLE')]
  result=projection.build_logical_projection(fixture_records(),ds); fact=result['facts'][0]
  self.assertEqual(fact['scope'],{'worker_scope':'fixture'}); self.assertEqual(fact['resolved_scope'],{'CONTINUITY_SCOPE':'alternate','TIMELINE_SCOPE':'branch-a'}); self.assertEqual(set(fact['scope_resolution_decision_ids']),{'CONTINUITY_SCOPE','TIMELINE_SCOPE'})
 def test_structural_paradox_is_preserved_as_nonstable(self):
  result=projection.build_logical_projection(fixture_records(),[status_decision('STRUCTURAL_PARADOX')]); self.assertEqual(result['facts'],[]); self.assertEqual(result['unresolved'],[]); self.assertEqual(result['contested'][0]['projection_status'],'STRUCTURAL_PARADOX')
 def test_explicit_assertion_supersession_excludes_predecessor_from_active_projection(self):
  rows=fixture_records(); successor=dict(rows[-1]); successor.update({'assertion_id':'assertion-2','object':{'value':'successor'},'supersedes':'assertion-1'}); rows.append(successor)
  ds=[status_decision('STABLE'),decision('status-2','ASSERTION_PROJECTION_STATUS','ASSERTION','assertion-2',{'projection_status':'STABLE'})]
  result=projection.build_logical_projection(rows,ds); self.assertEqual([r['assertion_id'] for r in result['facts']],['assertion-2']); self.assertEqual(len(result['assertion_history']),2)
 def test_provenance_contains_full_reachable_records_and_changes_with_source(self):
  first=projection.build_logical_projection(fixture_records('sha256:source-a'),[status_decision('STABLE')]); second=projection.build_logical_projection(fixture_records('sha256:source-b'),[status_decision('STABLE')]); p=first['provenance'][0]
  self.assertEqual(p['source_record']['content_hash'],'sha256:source-a'); self.assertEqual(p['source_record']['source_variant'],'v1'); self.assertEqual(p['evidence_record']['observed'],{'event':'fixture'}); self.assertEqual(p['evidence_record']['frame'],'PRIMARY'); self.assertEqual(p['work_record']['continuity_scope'],'fixture'); self.assertEqual(p['local_entity_record']['local_entity_id'],'local-1'); self.assertNotEqual(projection.canonical(first['provenance']),projection.canonical(second['provenance']))
 def test_typed_reference_assertion_emits_governed_relation_row(self):
  rows=fixture_records(object_value={'ref_type':'WORK','ref_id':'work-1'}); result=projection.build_logical_projection(rows,[status_decision('STABLE')]); rel=result['relations'][0]
  self.assertEqual(rel['assertion_id'],'assertion-1'); self.assertEqual(rel['predicate'],'CLAIMS'); self.assertEqual(rel['target_type'],'WORK'); self.assertEqual(rel['target_id'],'work-1')
 def test_accepted_experimental_identity_link_fails_closed(self):
  rows=fixture_records(); rows.insert(3,{'record_type':'local_entity','local_entity_id':'local-2','work_id':'work-1','label':'Second'})
  link=decision('link-1','ENTITY_LINK','LOCAL_ENTITY','local-1',{'relation_predicate':'SAME_AS','target_type':'LOCAL_ENTITY','target_id':'local-2'})
  with self.assertRaises(ValueError): projection.build_logical_projection(rows,[link])

if __name__=='__main__': unittest.main()
