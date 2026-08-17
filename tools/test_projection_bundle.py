#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path
MODULE_PATH=Path(__file__).with_name('projection_bundle.py'); spec=importlib.util.spec_from_file_location('trek_projection_bundle',MODULE_PATH); bundle=importlib.util.module_from_spec(spec); spec.loader.exec_module(bundle)

def make_projection(root, fact_status='STABLE'):
 rows={
  'entities.jsonl':[{'record_type':'local_entity','local_entity_id':'l1','work_id':'w1','label':'Entity'}],
  'facts.jsonl':[{'record_type':'assertion','assertion_id':'a1','subject_type':'LOCAL_ENTITY','subject':'l1','predicate':'CLAIMS','object':'v','evidence':['e1'],'status':'ACCEPTED','effective_assertion_status':'ACCEPTED','projection_status':fact_status}],
  'relations.jsonl':[], 'contested.jsonl':[], 'unresolved.jsonl':[],
  'provenance.jsonl':[{'record_type':'projection_provenance','provenance_id':'a1::e1','assertion_id':'a1','evidence_id':'e1'}],
  'assertion_history.jsonl':[{'record_type':'assertion','assertion_id':'a1','subject_type':'LOCAL_ENTITY','subject':'l1','predicate':'CLAIMS','object':'v','evidence':['e1'],'status':'ACCEPTED'}],
  'reconciliation_history.jsonl':[],
 }
 outputs={}
 for name,data in rows.items():
  payload=''.join(bundle.canonical(r)+'\n' for r in data).encode(); (root/name).write_bytes(payload); outputs[name]={'role':name.removesuffix('.jsonl'),'hash':bundle.sha256_bytes(payload),'count':len(data)}
 projection_hash=bundle.compute_projection_hash(outputs)
 manifest={'record_type':'projection_manifest','projection_version':'0.2.0','schema_version':'0.2.0','methodology_version':'0.1.0','compiler_commit':'fixture','research_head':'research','reconciliation_head':'recon','predicate_registry_hash':'sha256:'+'1'*64,'scope_key_registry_hash':'sha256:'+'2'*64,'input_hash':'sha256:'+'3'*64,'projection_hash':projection_hash,'outputs':outputs}
 (root/'manifest.json').write_text(json.dumps(manifest,sort_keys=True)+'\n'); return manifest

class ProjectionBundleTests(unittest.TestCase):
 def test_valid_bundle_returns_verified_receipt(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); manifest=make_projection(root); verified=bundle.verify_projection(root); self.assertEqual(verified['manifest']['projection_hash'],manifest['projection_hash']); self.assertEqual(set(verified['rows']),set(bundle.REQUIRED_OUTPUTS)); self.assertTrue(verified['receipt_hash'].startswith('sha256:'))
 def test_manifest_arbitrary_projection_hash_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); make_projection(root); m=json.loads((root/'manifest.json').read_text()); m['projection_hash']='sha256:'+'0'*64; (root/'manifest.json').write_text(json.dumps(m));
   with self.assertRaises(ValueError): bundle.verify_projection(root)
 def test_file_hash_mismatch_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); make_projection(root); (root/'entities.jsonl').write_text('{}\n');
   with self.assertRaises(ValueError): bundle.verify_projection(root)
 def test_record_count_mismatch_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); make_projection(root); m=json.loads((root/'manifest.json').read_text()); m['outputs']['entities.jsonl']['count']=99; (root/'manifest.json').write_text(json.dumps(m));
   with self.assertRaises(ValueError): bundle.verify_projection(root)
 def test_missing_required_output_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); make_projection(root); (root/'provenance.jsonl').unlink();
   with self.assertRaises(ValueError): bundle.verify_projection(root)
 def test_wrong_partition_status_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); make_projection(root,fact_status='UNRESOLVED')
   with self.assertRaises(ValueError): bundle.verify_projection(root)
 def test_stale_manifest_after_output_change_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); make_projection(root); (root/'facts.jsonl').write_text('');
   with self.assertRaises(ValueError): bundle.verify_projection(root)
 def test_unexpected_jsonl_output_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); make_projection(root); (root/'bonus.jsonl').write_text('');
   with self.assertRaises(ValueError): bundle.verify_projection(root)
if __name__=='__main__': unittest.main()
