#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, unittest
from pathlib import Path

def load(name,alias):
 p=Path(__file__).with_name(name); s=importlib.util.spec_from_file_location(alias,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
validate=load('validate.py','trek_validate_usage'); projection=load('build_projection.py','trek_projection_usage')
BASE_INDEX={'source':{},'work':{'w1':{'record_type':'work','work_id':'w1'}},'local_entity':{'l1':{'record_type':'local_entity','local_entity_id':'l1'},'l2':{'record_type':'local_entity','local_entity_id':'l2'}},'evidence':{'e1':{'record_type':'evidence','evidence_id':'e1'}},'assertion':{},'reconciliation_decision':{}}
def assertion(predicate,status='PROPOSED',object_value='x'):
 return {'record_type':'assertion','assertion_id':'a1','subject_type':'LOCAL_ENTITY','subject':'l1','predicate':predicate,'object':object_value,'evidence':['e1'],'status':status}
def link(predicate):
 return {'record_type':'reconciliation_decision','decision_id':'d1','decision_type':'ENTITY_LINK','subject_type':'LOCAL_ENTITY','subject_id':'l1','payload':{'relation_predicate':predicate,'target_type':'LOCAL_ENTITY','target_id':'l2'},'status':'PROPOSED','evidence':['e1'],'method':'fixture'}
class PredicateUsageTests(unittest.TestCase):
 def setUp(self):self.registry,_=validate.load_predicate_registry()
 def test_maps_to_is_rejected_as_research_assertion(self):
  errors=[]; validate.validate_predicate_assertion('fixture',assertion('MAPS_TO',object_value={'ref_type':'WORK','ref_id':'w1'}),self.registry,BASE_INDEX,errors); self.assertTrue(any('RESEARCH_ASSERTION' in e for e in errors))
 def test_reconciliation_only_identity_predicate_is_rejected_as_research_assertion(self):
  errors=[]; validate.validate_predicate_assertion('fixture',assertion('SAME_AS',object_value={'ref_type':'LOCAL_ENTITY','ref_id':'l2'}),self.registry,BASE_INDEX,errors); self.assertTrue(any('RESEARCH_ASSERTION' in e for e in errors))
 def test_research_only_predicate_is_rejected_in_entity_link(self):
  errors=[]; validate.validate_payload('fixture',link('CLAIMS'),self.registry,{},BASE_INDEX,errors); self.assertTrue(any('RECONCILIATION_RELATION' in e for e in errors))
 def test_explicit_multi_level_predicate_succeeds_in_both_declared_contexts(self):
  entry={'name':'MULTI','status':'ACCEPTED','definition':'fixture','semantic_class':'IDENTITY_RELATION','usage_levels':['RESEARCH_ASSERTION','RECONCILIATION_RELATION'],'subject_types':['LOCAL_ENTITY'],'object_mode':'REFERENCE_ONLY','object_ref_types':['LOCAL_ENTITY'],'symmetry':False,'inverse':None,'transitive':None,'projection_eligibility':'ACCEPTED_ASSERTION_ALLOWED','examples':['fixture'],'near_miss':'fixture miss','supersedes':None,'superseded_by':None,'methodology_version':'0.1.0','introduced_in_registry':'test'}
  reg={'MULTI':entry}; errors=[]; validate.validate_predicate_assertion('fixture',assertion('MULTI',status='ACCEPTED',object_value={'ref_type':'LOCAL_ENTITY','ref_id':'l2'}),reg,BASE_INDEX,errors); self.assertEqual(errors,[]); errors=[]; validate.validate_payload('fixture',link('MULTI'),reg,{},BASE_INDEX,errors); self.assertEqual(errors,[])
 def test_compiler_rejects_identity_semantics_without_reconciliation_usage(self):
  original=projection.load_registry
  try:
   def fake(path,key):
    if key=='name':return {'BAD':{'name':'BAD','status':'ACCEPTED','semantic_class':'IDENTITY_RELATION','usage_levels':['RESEARCH_ASSERTION'],'subject_types':['LOCAL_ENTITY'],'object_ref_types':['LOCAL_ENTITY']}}
    return original(path,key)
   projection.load_registry=fake
   records=[{'record_type':'work','work_id':'w1','title':'x','medium':'test'},{'record_type':'local_entity','local_entity_id':'l1','work_id':'w1','label':'one'},{'record_type':'local_entity','local_entity_id':'l2','work_id':'w1','label':'two'}]
   decision={'record_type':'reconciliation_decision','decision_id':'d1','decision_type':'ENTITY_LINK','subject_type':'LOCAL_ENTITY','subject_id':'l1','payload':{'relation_predicate':'BAD','target_type':'LOCAL_ENTITY','target_id':'l2'},'status':'ACCEPTED','evidence':['e1'],'method':'fixture'}
   with self.assertRaises(ValueError):projection.build_logical_projection(records,[decision])
  finally:projection.load_registry=original
if __name__=='__main__':unittest.main()
