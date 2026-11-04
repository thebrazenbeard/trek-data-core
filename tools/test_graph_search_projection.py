#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path
from unittest import mock

def load(name,alias):
 p=Path(__file__).with_name(name); s=importlib.util.spec_from_file_location(alias,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
graph=load('build_graph_search.py','trek_graph_search'); fixture=load('test_projection_fixture.py','trek_projection_fixture_graph')
def read_jsonl(path):return [json.loads(r) for r in Path(path).read_text().splitlines() if r.strip()]

class GraphSearchProjectionTests(unittest.TestCase):
 def test_graph_maps_governed_relation_without_using_predicate_as_edge_kind(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; fixture.make_projection(root); out=Path(td)/'out'; graph.build_bundle(root,out); edges=read_jsonl(out/'graph_edges.jsonl'); kinds={e['edge_kind'] for e in edges}; self.assertIn('GOVERNED_RELATION',kinds); self.assertNotIn('CLAIMS',kinds); governed=[e for e in edges if e['edge_kind']=='GOVERNED_RELATION'][0]; self.assertEqual(governed['predicate'],'CLAIMS'); self.assertEqual(governed['relation_id'],'assertion:a-stable')
 def test_graph_contains_structural_provenance_edges_and_history(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; fixture.make_projection(root); out=Path(td)/'out'; graph.build_bundle(root,out); edges=read_jsonl(out/'graph_edges.jsonl'); kinds={e['edge_kind'] for e in edges}; self.assertTrue({'ASSERTION_SUBJECT','ASSERTION_EVIDENCE','EVIDENCE_SOURCE','EVIDENCE_WORK','ENTITY_WORK','RECONCILIATION_SUBJECT'}.issubset(kinds)); nodes={n['node_id']:n for n in read_jsonl(out/'graph_nodes.jsonl')}; self.assertIn('assertion_history:a-rejected',nodes); self.assertIn('reconciliation:status-1',nodes)
 def test_graph_nodes_and_search_preserve_projection_status_and_literal_text(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; fixture.make_projection(root); out=Path(td)/'out'; graph.build_bundle(root,out); nodes={r['node_id']:r for r in read_jsonl(out/'graph_nodes.jsonl')}; docs={r['document_id']:r for r in read_jsonl(out/'search_documents.jsonl')}; self.assertEqual(nodes['assertion:a-paradox']['projection_status'],'STRUCTURAL_PARADOX'); self.assertEqual(nodes['assertion:a-paradox']['partition'],'contested'); self.assertIn('paradox',docs['assertion:a-paradox']['text']); self.assertIn('rejected',docs['assertion_history:a-rejected']['text'])
 def test_bundle_is_deterministic_and_carries_verification_receipt(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; manifest=fixture.make_projection(root); a=Path(td)/'a'; b=Path(td)/'b'; ma=graph.build_bundle(root,a); mb=graph.build_bundle(root,b); self.assertEqual(ma,mb); self.assertEqual(ma['projection_hash'],manifest['projection_hash']); self.assertTrue(ma['builder_identity'].startswith('sha256:')); self.assertTrue(ma['verification_receipt_hash'].startswith('sha256:')); self.assertEqual(ma['imported_output_contract'],list(graph.bundle.REQUIRED_OUTPUTS));
   for name in ('graph_nodes.jsonl','graph_edges.jsonl','search_documents.jsonl','manifest.json'):self.assertEqual((a/name).read_bytes(),(b/name).read_bytes())
 def test_invalid_projection_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; fixture.make_projection(root); (root/'relations.jsonl').write_text('');
   with self.assertRaises(ValueError):graph.build_bundle(root,Path(td)/'out')
 def test_output_must_not_overlap_verified_projection(self):
  with tempfile.TemporaryDirectory() as td:
   parent=Path(td); root=parent/'projection'; fixture.make_projection(root)
   original=(root/'manifest.json').read_bytes()
   for output in (root,parent,root/'derived'):
    with self.subTest(output=output):
     with self.assertRaisesRegex(ValueError,'overlap'):graph.build_bundle(root,output)
     self.assertEqual((root/'manifest.json').read_bytes(),original)
     self.assertFalse((root/'graph_nodes.jsonl').exists())
   alias=parent/'projection-link'; alias.symlink_to(root,target_is_directory=True)
   with self.assertRaisesRegex(ValueError,'overlap'):graph.build_bundle(root,alias)
 def test_output_directory_replaced_during_verification_cannot_redirect_writes(self):
  with tempfile.TemporaryDirectory() as td:
   parent=Path(td); root=parent/'projection'; fixture.make_projection(root)
   output=parent/'out'; output.mkdir(); moved=parent/'moved-out'
   original=(root/'manifest.json').read_bytes()
   verify=graph.bundle.verify_projection
   def adversarial_verify(path):
    result=verify(path)
    output.rename(moved)
    output.symlink_to(root,target_is_directory=True)
    return result
   with mock.patch.object(graph.bundle,'verify_projection',side_effect=adversarial_verify):
    with self.assertRaisesRegex(ValueError,'output.*changed|overlap'):
     graph.build_bundle(root,output)
   self.assertEqual((root/'manifest.json').read_bytes(),original)
   self.assertFalse((root/'graph_nodes.jsonl').exists())
   self.assertFalse((root/'graph_edges.jsonl').exists())
 def test_output_directory_replaced_during_output_write_stays_pinned(self):
  with tempfile.TemporaryDirectory() as td:
   parent=Path(td); root=parent/'projection'; fixture.make_projection(root)
   output=parent/'out'; output.mkdir(); moved=parent/'moved-out'
   original=(root/'manifest.json').read_bytes()
   write=graph.write_output_bytes
   swapped=False
   def adversarial_write(output_fd,name,payload):
    nonlocal swapped
    if not swapped:
     swapped=True
     output.rename(moved)
     output.symlink_to(root,target_is_directory=True)
    return write(output_fd,name,payload)
   with mock.patch.object(graph,'write_output_bytes',side_effect=adversarial_write):
    with self.assertRaisesRegex(ValueError,'output directory changed'):
     graph.build_bundle(root,output)
   self.assertTrue(swapped)
   self.assertEqual((root/'manifest.json').read_bytes(),original)
   self.assertFalse((root/'graph_nodes.jsonl').exists())
   self.assertTrue((moved/'graph_nodes.jsonl').exists())
 def test_existing_output_hardlink_does_not_truncate_projection_manifest(self):
  with tempfile.TemporaryDirectory() as td:
   parent=Path(td); root=parent/'projection'; fixture.make_projection(root)
   original=(root/'manifest.json').read_bytes(); output=parent/'out'; output.mkdir()
   try:(output/'manifest.json').hardlink_to(root/'manifest.json')
   except OSError as exc:self.skipTest(f'hardlinks unavailable: {exc}')
   with graph.pinned_output_directory(output,root) as fd:
    graph.write_output_bytes(fd,'manifest.json',b'{"derived":true}\n')
   self.assertEqual((root/'manifest.json').read_bytes(),original)
   self.assertNotEqual((output/'manifest.json').read_bytes(),original)
 def test_unrelated_symlink_output_directory_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   parent=Path(td); root=parent/'projection'; fixture.make_projection(root)
   actual=parent/'actual-out'; actual.mkdir(); alias=parent/'output-alias'; alias.symlink_to(actual,target_is_directory=True)
   with self.assertRaisesRegex(ValueError,'symlinks'):
    graph.build_bundle(root,alias)
   self.assertFalse((actual/'graph_nodes.jsonl').exists())
 def test_unsupported_secure_writer_fails_closed_without_explicit_trusted_opt_in(self):
  with tempfile.TemporaryDirectory() as td:
   parent=Path(td); root=parent/'projection'; fixture.make_projection(root)
   out=parent/'out'
   with mock.patch.object(graph,'require_safe_directory_writes',side_effect=OSError('unsupported')):
    with self.assertRaisesRegex(OSError,'unsupported'):
     graph.build_bundle(root,out)
   self.assertFalse(out.exists())
   with mock.patch.object(graph,'require_safe_directory_writes',side_effect=OSError('unsupported')):
    manifest=graph.build_bundle(root,out,trusted_output_path=True)
   self.assertEqual(json.loads((out/'manifest.json').read_text()),manifest)
 def test_trusted_output_fallback_rejects_symlink_path(self):
  with tempfile.TemporaryDirectory() as td:
   parent=Path(td); root=parent/'projection'; fixture.make_projection(root)
   actual=parent/'actual'; actual.mkdir(); link=parent/'link'; link.symlink_to(actual,target_is_directory=True)
   with mock.patch.object(graph,'require_safe_directory_writes',side_effect=OSError('unsupported')):
    with self.assertRaisesRegex(ValueError,'symlink'):
     graph.build_bundle(root,link,trusted_output_path=True)
   self.assertFalse((actual/'graph_nodes.jsonl').exists())
if __name__=='__main__':unittest.main()
