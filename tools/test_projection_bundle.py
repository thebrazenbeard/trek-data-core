#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path

def load(name,alias):
 p=Path(__file__).with_name(name); s=importlib.util.spec_from_file_location(alias,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
bundle=load('projection_bundle.py','trek_projection_bundle_test'); fixture=load('test_projection_fixture.py','trek_projection_fixture_bundle')
class ProjectionBundleTests(unittest.TestCase):
 def test_valid_bundle_returns_verified_receipt(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); manifest=fixture.make_projection(root); verified=bundle.verify_projection(root); self.assertEqual(verified['manifest']['projection_hash'],manifest['projection_hash']); self.assertEqual(set(verified['rows']),set(bundle.REQUIRED_OUTPUTS)); self.assertTrue(verified['receipt_hash'].startswith('sha256:'))
 def test_manifest_arbitrary_projection_hash_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); m=json.loads((root/'manifest.json').read_text()); m['projection_hash']='sha256:'+'0'*64; (root/'manifest.json').write_text(json.dumps(m));
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_file_hash_mismatch_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); (root/'entities.jsonl').write_text('{}\n');
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_record_count_mismatch_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); m=json.loads((root/'manifest.json').read_text()); m['outputs']['entities.jsonl']['count']=99; (root/'manifest.json').write_text(json.dumps(m));
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_missing_required_output_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); (root/'provenance.jsonl').unlink();
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_wrong_partition_status_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); facts=[json.loads(r) for r in (root/'facts.jsonl').read_text().splitlines()]; facts[0]['projection_status']='UNRESOLVED'; payload=''.join(bundle.canonical(r)+'\n' for r in facts).encode(); (root/'facts.jsonl').write_bytes(payload); m=json.loads((root/'manifest.json').read_text()); m['outputs']['facts.jsonl']['hash']=bundle.sha256_bytes(payload); m['projection_hash']=bundle.compute_projection_hash(m['outputs']); (root/'manifest.json').write_text(json.dumps(m));
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_stale_manifest_after_output_change_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); (root/'facts.jsonl').write_text('');
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_unexpected_jsonl_output_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); (root/'bonus.jsonl').write_text('');
   with self.assertRaises(ValueError):bundle.verify_projection(root)
if __name__=='__main__':unittest.main()
