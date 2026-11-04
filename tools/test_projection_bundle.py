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
 def test_unpinned_upstream_identity_remains_an_unverified_declaration(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   checked=bundle.verify_projection(root)
   self.assertEqual(checked['receipt']['upstream_identity_status']['research_head'],'UNVERIFIED_DECLARATION')
   self.assertEqual(checked['receipt']['upstream_identity_status']['input_hash'],'UNVERIFIED_DECLARATION')
 def test_forged_research_head_is_not_authenticated_by_matching_bundle_bytes(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); original=fixture.make_projection(root)
   manifest_path=root/'manifest.json'; changed=json.loads(manifest_path.read_text(encoding='utf-8'))
   changed['research_head']='FAKE_GIT_HEAD_UNVERIFIED'
   manifest_path.write_text(json.dumps(changed),encoding='utf-8')
   unpinned=bundle.verify_projection(root)
   self.assertEqual(unpinned['manifest']['input_hash'],original['input_hash'],'input hash has not authenticated the changed head')
   self.assertEqual(unpinned['receipt']['upstream_identity_status']['research_head'],'UNVERIFIED_DECLARATION')
   with self.assertRaisesRegex(ValueError,'research_head.*expected'):
    bundle.verify_projection(root,expected_identity={'research_head':original['research_head']})
 def test_duplicate_manifest_identity_claim_rejected_even_when_last_key_matches(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); original=fixture.make_projection(root)
   manifest_path=root/'manifest.json'; original_bytes=manifest_path.read_text().rstrip()
   # JSON's default last-key-wins parsing previously accepted this conflicting
   # first declaration and issued an apparently valid projection receipt.
   manifest_path.write_text(original_bytes[:-1]+',"research_head":"FORGED","research_head":'+json.dumps(original['research_head'])+'}')
   with self.assertRaisesRegex(ValueError,'duplicate JSON key'):
    bundle.verify_projection(root)
 def test_nonfinite_jsonl_constant_rejected_even_when_hashes_match(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   path=root/'entities.jsonl'; entity=json.loads(path.read_text(encoding='utf-8'))
   entity['unreviewed_numeric_value']=float('nan')
   payload=(json.dumps(entity,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
   path.write_bytes(payload)
   manifest_path=root/'manifest.json'; manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
   manifest['outputs']['entities.jsonl']['hash']=bundle.sha256_bytes(payload)
   manifest['projection_hash']=bundle.compute_projection_hash(manifest['outputs'])
   manifest_path.write_text(json.dumps(manifest),encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'non-finite JSON constant'):
    bundle.verify_projection(root)
 def test_nonfinite_manifest_constant_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   manifest_path=root/'manifest.json'; manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
   manifest['unreviewed_numeric_value']=float('inf')
   manifest_path.write_text(json.dumps(manifest),encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'non-finite JSON constant'):
    bundle.verify_projection(root)
 def test_manifest_numeric_exponent_overflow_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   manifest_path=root/'manifest.json'; manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
   text=json.dumps({**manifest,'unreviewed_numeric_value':'OVERFLOW_SENTINEL'})
   manifest_path.write_text(text.replace('"OVERFLOW_SENTINEL"','1e999'),encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'non-finite JSON number'):
    bundle.verify_projection(root)
 def test_external_identity_expectations_bind_only_the_supplied_fields(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); manifest=fixture.make_projection(root)
   receipt=bundle.verify_projection(root,expected_identity={'research_head':manifest['research_head'],'input_hash':manifest['input_hash']})['receipt']
   self.assertEqual(receipt['upstream_identity_status']['research_head'],'EXTERNAL_EXPECTATION_MATCHED')
   self.assertEqual(receipt['upstream_identity_status']['input_hash'],'EXTERNAL_EXPECTATION_MATCHED')
   self.assertEqual(receipt['upstream_identity_status']['reconciliation_head'],'UNVERIFIED_DECLARATION')
   with self.assertRaisesRegex(ValueError,'unsupported expected identity'):
    bundle.verify_projection(root,expected_identity={'unreviewed_extra':'x'})
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
 def test_byte_identical_symlinked_output_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); root=base/'bundle'; root.mkdir(); fixture.make_projection(root)
   outside=base/'outside-entities.jsonl'; (root/'entities.jsonl').replace(outside)
   (root/'entities.jsonl').symlink_to(outside)
   with self.assertRaisesRegex(ValueError,'symlink'):
    bundle.verify_projection(root)
 def test_symlinked_manifest_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); root=base/'bundle'; root.mkdir(); fixture.make_projection(root)
   outside=base/'outside-manifest.json'; (root/'manifest.json').replace(outside)
   (root/'manifest.json').symlink_to(outside)
   with self.assertRaisesRegex(ValueError,'symlink'):
    bundle.verify_projection(root)
 def test_symlinked_bundle_directory_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); root=base/'bundle'; root.mkdir(); fixture.make_projection(root)
   alias=base/'alias'; alias.symlink_to(root,target_is_directory=True)
   with self.assertRaisesRegex(ValueError,'symlink'):
    bundle.verify_projection(alias)
 def test_symlinked_ancestor_cannot_hide_an_otherwise_valid_bundle(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); outside=base/'outside'; outside.mkdir()
   root=outside/'bundle'; root.mkdir(); fixture.make_projection(root)
   alias=base/'alias'; alias.symlink_to(outside,target_is_directory=True)
   with self.assertRaisesRegex(ValueError,'symlinked ancestor'):
    bundle.verify_projection(alias/'bundle')
 def test_dotdot_path_cannot_hide_symlinked_ancestor(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); outside=base/'outside'; outside.mkdir()
   root=base/'bundle'; root.mkdir(); fixture.make_projection(root)
   alias=base/'alias'; alias.symlink_to(outside,target_is_directory=True)
   # The path resolves to base/bundle, but first traverses the aliased parent.
   with self.assertRaisesRegex(ValueError,'symlinked ancestor'):
    bundle.verify_projection(alias/'..'/'bundle')
 def test_byte_identical_hardlinked_output_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); root=base/'bundle'; root.mkdir(); fixture.make_projection(root)
   (base/'outside-entities.jsonl').hardlink_to(root/'entities.jsonl')
   with self.assertRaisesRegex(ValueError,'hardlinked'):
    bundle.verify_projection(root)
if __name__=='__main__':unittest.main()
