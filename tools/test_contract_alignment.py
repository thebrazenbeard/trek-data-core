#!/usr/bin/env python3
from __future__ import annotations
import contextlib, importlib.util, io, json, tempfile, unittest
from pathlib import Path

def load(name):
 p=Path(__file__).with_name(name); s=importlib.util.spec_from_file_location('m_'+name.replace('.','_'),p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
validate=load('validate.py'); projection=load('build_projection.py'); diff=load('diff_projection.py')

def records(subject_type='LOCAL_ENTITY', proposed='STABLE', object_value=None, source_hash='sha256:source'):
 if object_value is None: object_value={'text':'fixture'}
 a={'record_type':'assertion','assertion_id':'a1','subject_type':subject_type,'subject':'local-1','predicate':'CLAIMS','object':object_value,'evidence':['e1'],'status':'ACCEPTED','scope':{'continuity':'prime'}}
 if proposed is not None:a['proposed_projection_status']=proposed
 return [
  {'record_type':'source','source_id':'s1','source_kind':'transcript','locator':'fixture://s1','content_hash':source_hash,'source_variant':'v1','retrieved_at':'2026-08-14T00:00:00Z','provenance_family':'family-a'},
  {'record_type':'work','work_id':'w1','title':'Fixture Work','medium':'test'},
  {'record_type':'local_entity','local_entity_id':'local-1','work_id':'w1','label':'Fixture'},
  {'record_type':'evidence','evidence_id':'e1','source_id':'s1','work_id':'w1','evidence_kind':'depiction','locator':{'line':1},'observed':{'event':'fixture'},'frame':'PRIMARY'},
  a,
 ]

def decision(i,t,subject_type,subject_id,payload,sup=None,reason=None):
 r={'record_type':'reconciliation_decision','decision_id':i,'decision_type':t,'subject_type':subject_type,'subject_id':subject_id,'payload':payload,'status':'ACCEPTED','evidence':['e1'],'method':'fixture'}
 if sup:r['supersedes']=sup
 if reason:r['reason']=reason
 return r

def active_decisions():
 return [
  decision('disp1','ASSERTION_DISPOSITION','ASSERTION','a1',{'disposition':'ACCEPTED'}),
  decision('stat1','ASSERTION_PROJECTION_STATUS','ASSERTION','a1',{'projection_status':'STABLE'}),
  decision('scope1','SCOPE_RESOLUTION','ASSERTION','a1',{'resolution_key':'continuity','resolution':{'continuity':'alternate'}}),
 ]

class ContractAlignmentTests(unittest.TestCase):
 def run_validation(self,rows):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'research'; root.mkdir(); (root/'records.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows)); old=validate.DATA_ROOTS; validate.DATA_ROOTS=[root]
   try:
    out=io.StringIO()
    with contextlib.redirect_stdout(out): rc=validate.main()
   finally: validate.DATA_ROOTS=old
   return rc,out.getvalue()
 def test_assertion_requires_subject_type(self):
  rows=records(); del rows[-1]['subject_type']; rc,o=self.run_validation(rows); self.assertEqual(rc,1); self.assertIn('subject_type',o)
 def test_dangling_typed_object_reference_is_rejected(self):
  rows=records(object_value={'ref_type':'WORK','ref_id':'missing-work'}); rc,o=self.run_validation(rows); self.assertEqual(rc,1); self.assertIn('missing-work',o)
 def test_worker_proposed_status_is_not_authoritative(self):
  result=projection.build_logical_projection(records(proposed='STABLE'),[])
  self.assertEqual(result['facts'],[]); self.assertEqual(result['contested'],[]); self.assertEqual(result['unresolved'][0]['projection_status'],'UNRESOLVED'); self.assertEqual(result['unresolved'][0]['projection_reason'],'MISSING_PROJECTION_STATUS')
 def test_typed_reconciliation_drives_projection_without_mutating_worker_fields(self):
  result=projection.build_logical_projection(records(proposed='CONTESTED'),active_decisions()); fact=result['facts'][0]
  self.assertEqual(fact['subject'],'local-1'); self.assertEqual(fact['subject_type'],'LOCAL_ENTITY'); self.assertEqual(fact['proposed_projection_status'],'CONTESTED')
  self.assertEqual(fact['assertion_disposition'],'ACCEPTED'); self.assertEqual(fact['projection_status'],'STABLE')
  self.assertEqual(fact['resolved_scope']['continuity'],{'continuity':'alternate'})
 def test_rejected_disposition_excludes_assertion_from_active_partitions(self):
  ds=[decision('disp1','ASSERTION_DISPOSITION','ASSERTION','a1',{'disposition':'REJECTED'})]
  result=projection.build_logical_projection(records(),ds); self.assertEqual(result['facts'],[]); self.assertEqual(result['contested'],[]); self.assertEqual(result['unresolved'],[])
 def test_provenance_contains_full_reachable_records(self):
  result=projection.build_logical_projection(records(),active_decisions()); p=result['provenance'][0]
  self.assertEqual(p['source_record']['content_hash'],'sha256:source'); self.assertEqual(p['source_record']['source_variant'],'v1'); self.assertEqual(p['evidence_record']['observed'],{'event':'fixture'}); self.assertEqual(p['work_record']['work_id'],'w1'); self.assertEqual(p['local_entity_record']['local_entity_id'],'local-1')
 def test_nonstable_transition_is_provisional_status_change_without_conflict_inference(self):
  with tempfile.TemporaryDirectory() as td:
   old=Path(td)/'old'; new=Path(td)/'new'; old.mkdir(); new.mkdir()
   (old/'unresolved.jsonl').write_text(json.dumps({'assertion_id':'a1','projection_status':'UNRESOLVED','subject':'x','predicate':'CLAIMS','object':'v'})+'\n')
   (new/'contested.jsonl').write_text(json.dumps({'assertion_id':'a1','projection_status':'CONTESTED','subject':'x','predicate':'CLAIMS','object':'v'})+'\n')
   classes=[x['class'] for x in diff.semantic_diff(old,new)]
   self.assertIn('PROVISIONAL_STATUS_CHANGED',classes); self.assertNotIn('STATUS_PROMOTED',classes); self.assertNotIn('STATUS_DEMOTED',classes); self.assertNotIn('CONFLICT_INTRODUCED',classes); self.assertNotIn('CONFLICT_RESOLVED',classes)
 def test_stable_to_contested_is_demotion_without_conflict_inference(self):
  with tempfile.TemporaryDirectory() as td:
   old=Path(td)/'old'; new=Path(td)/'new'; old.mkdir(); new.mkdir()
   (old/'facts.jsonl').write_text(json.dumps({'assertion_id':'a1','projection_status':'STABLE','subject':'x','predicate':'CLAIMS','object':'v'})+'\n')
   (new/'contested.jsonl').write_text(json.dumps({'assertion_id':'a1','projection_status':'CONTESTED','subject':'x','predicate':'CLAIMS','object':'v'})+'\n')
   classes=[x['class'] for x in diff.semantic_diff(old,new)]
   self.assertIn('STATUS_DEMOTED',classes); self.assertNotIn('PROVISIONAL_STATUS_CHANGED',classes); self.assertNotIn('CONFLICT_INTRODUCED',classes)
 def test_reconciliation_history_change_is_not_fact_value_change(self):
  with tempfile.TemporaryDirectory() as td:
   old=Path(td)/'old'; new=Path(td)/'new'; old.mkdir(); new.mkdir(); row={'decision_id':'d1','record_type':'reconciliation_decision','decision_type':'ASSERTION_DISPOSITION','subject_type':'ASSERTION','subject_id':'a1','payload':{'disposition':'ACCEPTED'},'status':'ACCEPTED','evidence':['e1'],'method':'fixture'}
   (new/'accepted_reconciliation.jsonl').write_text(json.dumps(row)+'\n'); changes=diff.semantic_diff(old,new); classes=[x['class'] for x in changes]
   self.assertNotIn('VALUE_CHANGED',classes); self.assertIn('PROVISIONAL_RECONCILIATION_HISTORY_CHANGED',classes)
if __name__=='__main__': unittest.main()
