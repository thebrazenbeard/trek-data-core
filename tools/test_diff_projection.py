#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path
MODULE_PATH=Path(__file__).with_name('diff_projection.py'); spec=importlib.util.spec_from_file_location('trek_diff_projection',MODULE_PATH); diff=importlib.util.module_from_spec(spec); spec.loader.exec_module(diff)

def write_jsonl(root,filename,rows): (root/filename).write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
def assertion(i='a1',status='STABLE',value='v1',supersedes=None,scopes=None):
 r={'record_type':'assertion','assertion_id':i,'subject_type':'LOCAL_ENTITY','subject':'local-1','predicate':'CLAIMS','object':{'value':value},'evidence':['e1'],'status':'ACCEPTED','projection_status':status}
 if supersedes:r['supersedes']=supersedes
 if scopes is not None:r['resolved_scope']=scopes
 return r

def relation(i='r1',predicate='CLAIMS',target='work-1',kind='ASSERTION_PREDICATE'):
 return {'record_type':'projection_relation','relation_id':i,'relation_kind':kind,'subject_type':'LOCAL_ENTITY','subject_id':'local-1','predicate':predicate,'target_type':'WORK','target_id':target}
def provenance(aid='a1',source_hash='sha256:a'):
 return {'record_type':'projection_provenance','provenance_id':f'{aid}::e1','assertion_id':aid,'evidence_id':'e1','source_record':{'source_id':'s1','content_hash':source_hash},'evidence_record':{'evidence_id':'e1'},'work_record':{'work_id':'w1'}}

class SemanticDiffTests(unittest.TestCase):
 def run_diff(self,old_files,new_files):
  with tempfile.TemporaryDirectory() as td:
   old=Path(td)/'old'; new=Path(td)/'new'; old.mkdir(); new.mkdir()
   for f,rows in old_files.items(): write_jsonl(old,f,rows)
   for f,rows in new_files.items(): write_jsonl(new,f,rows)
   return diff.semantic_diff(old,new)
 def classes(self,changes): return [c['class'] for c in changes]
 def test_fact_added(self): self.assertIn('ADDED_FACT',self.classes(self.run_diff({}, {'facts.jsonl':[assertion()]})))
 def test_fact_removed(self): self.assertIn('REMOVED_FACT',self.classes(self.run_diff({'facts.jsonl':[assertion()]}, {})))
 def test_explicit_supersession_with_changed_value_is_value_changed(self):
  old=assertion('a1','STABLE','v1'); new=assertion('a2','STABLE','v2','a1')
  changes=self.run_diff({'facts.jsonl':[old],'assertion_history.jsonl':[old]}, {'facts.jsonl':[new],'assertion_history.jsonl':[old,new]})
  self.assertIn('VALUE_CHANGED',self.classes(changes)); self.assertNotIn('ADDED_FACT',self.classes(changes)); self.assertNotIn('REMOVED_FACT',self.classes(changes))
 def test_unrelated_replacement_is_remove_plus_add(self):
  changes=self.run_diff({'facts.jsonl':[assertion('a1')]},{'facts.jsonl':[assertion('a2')]}); classes=self.classes(changes)
  self.assertIn('ADDED_FACT',classes); self.assertIn('REMOVED_FACT',classes); self.assertNotIn('VALUE_CHANGED',classes)
 def test_unresolved_to_stable_is_promoted(self):
  changes=self.run_diff({'unresolved.jsonl':[assertion(status='UNRESOLVED')]},{'facts.jsonl':[assertion(status='STABLE')]}); self.assertIn('STATUS_PROMOTED',self.classes(changes))
 def test_stable_to_contested_is_demoted_not_conflict(self):
  changes=self.run_diff({'facts.jsonl':[assertion(status='STABLE')]},{'contested.jsonl':[assertion(status='CONTESTED')]}); classes=self.classes(changes)
  self.assertIn('STATUS_DEMOTED',classes); self.assertNotIn('CONFLICT_INTRODUCED',classes)
 def test_nonstable_transition_uses_provisional_status_change(self):
  changes=self.run_diff({'unresolved.jsonl':[assertion(status='UNRESOLVED')]},{'contested.jsonl':[assertion(status='CONTESTED')]}); classes=self.classes(changes)
  self.assertIn('PROVISIONAL_STATUS_CHANGED',classes); self.assertNotIn('STATUS_PROMOTED',classes); self.assertNotIn('STATUS_DEMOTED',classes)
 def test_identity_relation_change_is_entity_link_changed(self):
  old=relation('reconciliation:d1','SAME_AS','local-2','IDENTITY_LINK'); new=relation('reconciliation:d2','COUNTERPART_OF','local-3','IDENTITY_LINK')
  changes=self.run_diff({'relations.jsonl':[old]},{'relations.jsonl':[new]}); self.assertIn('ENTITY_LINK_CHANGED',self.classes(changes))
 def test_scope_keys_diff_independently(self):
  changes=self.run_diff({'facts.jsonl':[assertion(scopes={'CONTINUITY_SCOPE':'prime','TIMELINE_SCOPE':'a'})]},{'facts.jsonl':[assertion(scopes={'CONTINUITY_SCOPE':'prime','TIMELINE_SCOPE':'b'})]})
  events=[c for c in changes if c['class']=='SCOPE_CHANGED']; self.assertEqual(len(events),1); self.assertEqual(events[0]['details']['resolution_key'],'TIMELINE_SCOPE')
 def test_provenance_union_detects_source_change(self):
  changes=self.run_diff({'facts.jsonl':[assertion()],'provenance.jsonl':[provenance(source_hash='sha256:a')]},{'facts.jsonl':[assertion()],'provenance.jsonl':[provenance(source_hash='sha256:b')]}); self.assertIn('PROVENANCE_CHANGED',self.classes(changes))
 def test_provenance_and_status_emit_atomic_events(self):
  changes=self.run_diff({'unresolved.jsonl':[assertion(status='UNRESOLVED')],'provenance.jsonl':[provenance(source_hash='sha256:a')]},{'facts.jsonl':[assertion(status='STABLE')],'provenance.jsonl':[provenance(source_hash='sha256:b')]}); classes=self.classes(changes)
  self.assertIn('STATUS_PROMOTED',classes); self.assertIn('PROVENANCE_CHANGED',classes)
 def test_explicit_contradiction_relation_introduces_conflict(self):
  conflict={'record_type':'projection_relation','relation_id':'assertion:conflict','relation_kind':'ASSERTION_PREDICATE','assertion_id':'conflict','subject_type':'ASSERTION','subject_id':'a1','predicate':'CONTRADICTS','target_type':'ASSERTION','target_id':'a2'}
  changes=self.run_diff({}, {'relations.jsonl':[conflict]}); self.assertIn('CONFLICT_INTRODUCED',self.classes(changes))
 def test_removed_contradiction_relation_resolves_conflict(self):
  conflict={'record_type':'projection_relation','relation_id':'assertion:conflict','relation_kind':'ASSERTION_PREDICATE','assertion_id':'conflict','subject_type':'ASSERTION','subject_id':'a1','predicate':'CONTRADICTS','target_type':'ASSERTION','target_id':'a2'}
  changes=self.run_diff({'relations.jsonl':[conflict]}, {}); self.assertIn('CONFLICT_RESOLVED',self.classes(changes))
 def test_scope_only_move_out_of_contested_does_not_resolve_conflict(self):
  changes=self.run_diff({'contested.jsonl':[assertion(status='CONTESTED',scopes={'TIMELINE_SCOPE':'a'})]},{'facts.jsonl':[assertion(status='STABLE',scopes={'TIMELINE_SCOPE':'b'})]}); self.assertNotIn('CONFLICT_RESOLVED',self.classes(changes))
 def test_same_id_worker_assertion_mutation_fails_closed(self):
  with self.assertRaises(ValueError): self.run_diff({'facts.jsonl':[assertion(value='v1')]},{'facts.jsonl':[assertion(value='v2')]})
 def test_relation_lifecycle_is_visible_provisionally(self):
  changes=self.run_diff({}, {'relations.jsonl':[relation()]}); self.assertIn('PROVISIONAL_RELATION_ADDED',self.classes(changes))
 def test_entity_lifecycle_is_visible_provisionally(self):
  changes=self.run_diff({}, {'entities.jsonl':[{'record_type':'local_entity','local_entity_id':'l1','work_id':'w1','label':'x'}]}); self.assertIn('PROVISIONAL_ENTITY_ADDED',self.classes(changes))
 def test_reconciliation_history_change_is_provisional_not_value_change(self):
  row={'record_type':'reconciliation_decision','decision_id':'d1','decision_type':'ASSERTION_DISPOSITION','subject_type':'ASSERTION','subject_id':'a1','payload':{'disposition':'ACCEPTED'},'status':'ACCEPTED','evidence':['e1'],'method':'fixture'}
  changes=self.run_diff({}, {'reconciliation_history.jsonl':[row]}); classes=self.classes(changes); self.assertIn('PROVISIONAL_RECONCILIATION_HISTORY_CHANGED',classes); self.assertNotIn('VALUE_CHANGED',classes)

if __name__=='__main__': unittest.main()
