#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path

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
if __name__=='__main__':unittest.main()
