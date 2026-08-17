#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, unittest
from pathlib import Path
MODULE_PATH=Path(__file__).with_name('build_projection.py'); spec=importlib.util.spec_from_file_location('trek_projection_adversarial',MODULE_PATH); projection=importlib.util.module_from_spec(spec); spec.loader.exec_module(projection)

def base_records():
 return [
  {'record_type':'source','source_id':'s0','source_kind':'transcript','locator':'fixture://root','content_hash':'sha256:root','derived_from':[]},
  {'record_type':'source','source_id':'s1','source_kind':'conversion','locator':'fixture://one','content_hash':'sha256:one','derived_from':['s0']},
  {'record_type':'source','source_id':'s2','source_kind':'conversion','locator':'fixture://two','content_hash':'sha256:two','derived_from':['s0']},
  {'record_type':'source','source_id':'s3','source_kind':'conversion','locator':'fixture://three','content_hash':'sha256:three','derived_from':['s1','s2']},
  {'record_type':'work','work_id':'w1','title':'Work One','medium':'test'},
  {'record_type':'work','work_id':'w2','title':'Work Two','medium':'test'},
  {'record_type':'local_entity','local_entity_id':'l1','work_id':'w1','label':'Same Name'},
  {'record_type':'local_entity','local_entity_id':'l2','work_id':'w2','label':'Same Name'},
  {'record_type':'evidence','evidence_id':'e1','source_id':'s3','work_id':'w1','evidence_kind':'testimony','locator':{'line':1},'observed':{'utterance':'X'},'frame':'TESTIMONY','epistemic_status':'UNKNOWN'},
  {'record_type':'assertion','assertion_id':'a1','subject_type':'LOCAL_ENTITY','subject':'l1','predicate':'CLAIMS','object':'X','evidence':['e1'],'status':'ACCEPTED','proposed_projection_status':'STABLE'},
 ]
class AdversarialInvariantTests(unittest.TestCase):
 def test_source_lineage_diamond_is_deduplicated_not_misclassified_as_cycle(self):
  sources={r['source_id']:r for r in base_records() if r['record_type']=='source'}; lineage=projection.source_lineage('s3',sources); self.assertEqual([r['source_id'] for r in lineage],['s0','s1','s2'])
 def test_same_display_name_does_not_merge_local_entities(self):
  result=projection.build_logical_projection(base_records(),[]); self.assertEqual([r['local_entity_id'] for r in result['entities']],['l1','l2']); self.assertTrue(all('identity_links' not in r for r in result['entities']))
 def test_testimony_frame_survives_without_worker_proposal_promoting_world_state(self):
  result=projection.build_logical_projection(base_records(),[]); self.assertEqual(result['facts'],[]); self.assertEqual(result['unresolved'][0]['projection_status'],'UNRESOLVED'); provenance=result['provenance'][0]; self.assertEqual(provenance['evidence_record']['frame'],'TESTIMONY'); self.assertEqual(provenance['evidence_record']['observed'],{'utterance':'X'})
 def test_input_iteration_order_does_not_change_logical_projection(self):
  records=base_records(); a=projection.build_logical_projection(records,[]); b=projection.build_logical_projection(list(reversed(records)),[]); self.assertEqual(projection.canonical(a),projection.canonical(b))
 def test_source_derivation_cycle_fails_closed(self):
  sources={'a':{'source_id':'a','derived_from':['b']},'b':{'source_id':'b','derived_from':['a']}}
  with self.assertRaises(ValueError):projection.source_lineage('a',sources)
if __name__=='__main__':unittest.main()
