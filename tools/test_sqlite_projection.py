#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, sqlite3, tempfile, unittest
from pathlib import Path

def load(name,alias):
 p=Path(__file__).with_name(name); s=importlib.util.spec_from_file_location(alias,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
sqlite_projection=load('build_sqlite.py','trek_build_sqlite'); fixture=load('test_projection_fixture.py','trek_projection_fixture')

class SQLiteProjectionTests(unittest.TestCase):
 def test_database_pins_verified_projection_and_builder_receipt(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; manifest=fixture.make_projection(root); db=Path(td)/'query.db'; sqlite_projection.build_database(root,db)
   with sqlite3.connect(db) as con:
    meta=dict(con.execute('select key,value from metadata').fetchall()); self.assertEqual(meta['projection_hash'],manifest['projection_hash']); self.assertTrue(meta['verification_receipt_hash'].startswith('sha256:')); self.assertTrue(meta['derived_builder_identity'].startswith('sha256:')); self.assertEqual(meta['derived_schema_version'],'0.2.0')
 def test_active_partitions_and_inactive_history_are_preserved(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; fixture.make_projection(root); db=Path(td)/'query.db'; sqlite_projection.build_database(root,db)
   with sqlite3.connect(db) as con:
    rows=con.execute('select assertion_id,projection_status,partition from assertions order by assertion_id').fetchall(); self.assertEqual(rows,[('a-paradox','STRUCTURAL_PARADOX','contested'),('a-stable','STABLE','facts'),('a-unresolved','UNRESOLVED','unresolved')]); self.assertEqual(con.execute("select status from assertion_history where assertion_id='a-rejected'").fetchone()[0],'REJECTED'); self.assertEqual(con.execute('select count(*) from provenance').fetchone()[0],4); self.assertEqual(con.execute('select count(*) from relations').fetchone()[0],1)
 def test_rebuild_is_query_deterministic(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; fixture.make_projection(root); first=Path(td)/'a.db'; second=Path(td)/'b.db'; sqlite_projection.build_database(root,first); sqlite_projection.build_database(root,second); self.assertEqual(sqlite_projection.query_snapshot(first),sqlite_projection.query_snapshot(second))
 def test_invalid_new_projection_leaves_previous_database_intact(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; fixture.make_projection(root); db=Path(td)/'query.db'; sqlite_projection.build_database(root,db); before=sqlite_projection.query_snapshot(db); (root/'facts.jsonl').write_text('')
   with self.assertRaises(ValueError): sqlite_projection.build_database(root,db)
   self.assertEqual(before,sqlite_projection.query_snapshot(db))
 def test_provenance_catalogs_are_queryable(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'projection'; fixture.make_projection(root); db=Path(td)/'query.db'; sqlite_projection.build_database(root,db)
   with sqlite3.connect(db) as con:
    self.assertEqual(con.execute('select count(*) from sources').fetchone()[0],1); self.assertEqual(con.execute('select count(*) from works').fetchone()[0],1); self.assertEqual(con.execute('select count(*) from evidence').fetchone()[0],1)
if __name__=='__main__': unittest.main()
