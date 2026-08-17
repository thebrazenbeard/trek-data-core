#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, tempfile, unittest
from pathlib import Path

def load(name,alias):
 p=Path(__file__).with_name(name); s=importlib.util.spec_from_file_location(alias,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
pg=load('build_postgres.py','trek_build_postgres'); fixture=load('test_projection_fixture.py','trek_projection_fixture_pg')

class PostgresProjectionTests(unittest.TestCase):
 def test_generated_sql_is_deterministic_verified_and_projection_pinned(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; manifest=fixture.make_projection(root); first=pg.generate_sql(root); second=pg.generate_sql(root); self.assertEqual(first,second); self.assertIn(manifest['projection_hash'],first); self.assertIn('CREATE SCHEMA trek_projection_v0_2',first); self.assertIn('SET standard_conforming_strings = on',first)
 def test_generated_sql_preserves_history_relations_and_projection_states(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; fixture.make_projection(root); sql=pg.generate_sql(root); self.assertIn('STRUCTURAL_PARADOX',sql); self.assertIn('assertion_history',sql); self.assertIn('reconciliation_history',sql); self.assertIn('ASSERTION_PREDICATE',sql)
 def test_sql_literal_escaping_is_deterministic_for_hostile_text(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; fixture.make_projection(root,stable_value="It's a fixture\\path\n'; DROP SCHEMA public; --"); sql=pg.generate_sql(root); self.assertIn("It''s a fixture",sql); self.assertIn('DROP SCHEMA public',sql); self.assertIn('standard_conforming_strings',sql)
 def test_bundle_manifest_contains_builder_identity_and_verification_receipt(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; manifest=fixture.make_projection(root); out=Path(td)/'bundle'; result=pg.write_bundle(root,out); self.assertEqual(result['projection_hash'],manifest['projection_hash']); self.assertTrue(result['builder_identity'].startswith('sha256:')); self.assertTrue(result['verification_receipt_hash'].startswith('sha256:')); self.assertEqual(result['imported_output_contract'],list(pg.bundle.REQUIRED_OUTPUTS)); self.assertEqual((out/'projection.sql').read_text(),pg.generate_sql(root))
 def test_invalid_projection_is_rejected_before_sql_generation(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; fixture.make_projection(root); (root/'facts.jsonl').write_text('')
   with self.assertRaises(ValueError): pg.generate_sql(root)
if __name__=='__main__': unittest.main()
