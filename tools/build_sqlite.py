#!/usr/bin/env python3
"""Build an atomic, rebuildable SQLite query database from a verified canonical projection."""
from __future__ import annotations
import argparse, importlib.util, os, sqlite3, tempfile
from pathlib import Path
_MODULE=Path(__file__).with_name('projection_bundle.py'); _SPEC=importlib.util.spec_from_file_location('trek_projection_bundle_sqlite',_MODULE); bundle=importlib.util.module_from_spec(_SPEC); _SPEC.loader.exec_module(bundle)
ASSERTION_PARTITIONS={'facts.jsonl':'facts','contested.jsonl':'contested','unresolved.jsonl':'unresolved'}; DERIVED_SCHEMA_VERSION='0.2.0'
def canonical(v):return bundle.canonical(v)
def json_value(v):return None if v is None else canonical(v)
def create_schema(con):
 con.executescript('''PRAGMA foreign_keys=ON;
 CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
 CREATE TABLE entities(local_entity_id TEXT PRIMARY KEY,work_id TEXT,label TEXT,identity_links_json TEXT,resolved_scope_json TEXT,record_json TEXT NOT NULL);
 CREATE TABLE assertions(assertion_id TEXT PRIMARY KEY,projection_status TEXT NOT NULL,partition TEXT NOT NULL CHECK(partition IN ('facts','contested','unresolved')),subject_type TEXT,subject TEXT,predicate TEXT,object_json TEXT,scope_json TEXT,resolved_scope_json TEXT,effective_assertion_status TEXT NOT NULL,record_json TEXT NOT NULL);
 CREATE TABLE assertion_history(assertion_id TEXT PRIMARY KEY,status TEXT,supersedes TEXT,record_json TEXT NOT NULL);
 CREATE TABLE provenance(provenance_id TEXT PRIMARY KEY,assertion_id TEXT NOT NULL,evidence_id TEXT,record_json TEXT NOT NULL);
 CREATE TABLE reconciliation_history(decision_id TEXT PRIMARY KEY,decision_type TEXT,subject_type TEXT,subject_id TEXT,status TEXT,supersedes TEXT,payload_json TEXT,record_json TEXT NOT NULL);
 CREATE TABLE relations(relation_id TEXT PRIMARY KEY,relation_kind TEXT,subject_type TEXT,subject_id TEXT,predicate TEXT,target_type TEXT,target_id TEXT,record_json TEXT NOT NULL);
 CREATE TABLE sources(source_id TEXT PRIMARY KEY,record_json TEXT NOT NULL); CREATE TABLE works(work_id TEXT PRIMARY KEY,record_json TEXT NOT NULL); CREATE TABLE evidence(evidence_id TEXT PRIMARY KEY,record_json TEXT NOT NULL);
 CREATE INDEX idx_assertions_status ON assertions(projection_status); CREATE INDEX idx_assertions_subject ON assertions(subject_type,subject); CREATE INDEX idx_assertions_predicate ON assertions(predicate); CREATE INDEX idx_provenance_assertion ON provenance(assertion_id); CREATE INDEX idx_reconciliation_subject ON reconciliation_history(subject_type,subject_id); CREATE INDEX idx_relations_subject ON relations(subject_type,subject_id); CREATE INDEX idx_relations_target ON relations(target_type,target_id);''')
def add_catalog(catalog,key,row,label):
 if not isinstance(row,dict):return
 rid=row.get(key)
 if not rid:return
 if rid in catalog and canonical(catalog[rid])!=canonical(row):raise ValueError(f'conflicting {label} metadata for {rid}')
 catalog[rid]=row
def build_database(projection_root,database_path):
 projection_root=Path(projection_root); database_path=Path(database_path); verified=bundle.verify_projection(projection_root); rows=verified['rows']; manifest=verified['manifest']; database_path.parent.mkdir(parents=True,exist_ok=True); fd,tmp_name=tempfile.mkstemp(prefix=database_path.name+'.',suffix='.tmp',dir=database_path.parent); os.close(fd); os.unlink(tmp_name); tmp_path=Path(tmp_name); con=None
 try:
  con=sqlite3.connect(tmp_path); create_schema(con); builder_identity=bundle.tool_identity(Path(__file__),_MODULE)
  metadata={'projection_hash':manifest['projection_hash'],'input_hash':manifest['input_hash'],'projection_version':manifest['projection_version'],'schema_version':manifest['schema_version'],'methodology_version':manifest['methodology_version'],'research_head':manifest['research_head'],'reconciliation_head':manifest['reconciliation_head'],'predicate_registry_hash':manifest['predicate_registry_hash'],'scope_key_registry_hash':manifest['scope_key_registry_hash'],'compiler_commit':manifest['compiler_commit'],'derived_schema_version':DERIVED_SCHEMA_VERSION,'derived_builder_identity':builder_identity,'verification_receipt_hash':verified['receipt_hash'],'verification_receipt_json':canonical(verified['receipt']),'imported_output_contract':canonical(list(bundle.REQUIRED_OUTPUTS))}; con.executemany('INSERT INTO metadata(key,value) VALUES (?,?)',sorted((k,str(v)) for k,v in metadata.items()))
  for row in rows['entities.jsonl']:con.execute('INSERT INTO entities VALUES (?,?,?,?,?,?)',(row['local_entity_id'],row.get('work_id'),row.get('label'),json_value(row.get('identity_links')),json_value(row.get('resolved_scope')),canonical(row)))
  for filename,partition in ASSERTION_PARTITIONS.items():
   for row in rows[filename]:con.execute('INSERT INTO assertions VALUES (?,?,?,?,?,?,?,?,?,?,?)',(row['assertion_id'],row['projection_status'],partition,row.get('subject_type'),row.get('subject'),row.get('predicate'),json_value(row.get('object')),json_value(row.get('scope')),json_value(row.get('resolved_scope')),row.get('effective_assertion_status'),canonical(row)))
  for row in rows['assertion_history.jsonl']:con.execute('INSERT INTO assertion_history VALUES (?,?,?,?)',(row['assertion_id'],row.get('status'),row.get('supersedes'),canonical(row)))
  sources={}; works={}; evidence={}
  for row in rows['provenance.jsonl']:
   con.execute('INSERT INTO provenance VALUES (?,?,?,?)',(row['provenance_id'],row['assertion_id'],row.get('evidence_id'),canonical(row))); add_catalog(sources,'source_id',row.get('source_record'),'source'); add_catalog(works,'work_id',row.get('work_record'),'work'); add_catalog(evidence,'evidence_id',row.get('evidence_record'),'evidence')
   for item in row.get('source_lineage_records',[]):add_catalog(sources,'source_id',item,'source')
   for item in row.get('work_lineage_records',[]):add_catalog(works,'work_id',item,'work')
  for sid,row in sorted(sources.items()):con.execute('INSERT INTO sources VALUES (?,?)',(sid,canonical(row)))
  for wid,row in sorted(works.items()):con.execute('INSERT INTO works VALUES (?,?)',(wid,canonical(row)))
  for eid,row in sorted(evidence.items()):con.execute('INSERT INTO evidence VALUES (?,?)',(eid,canonical(row)))
  for row in rows['reconciliation_history.jsonl']:con.execute('INSERT INTO reconciliation_history VALUES (?,?,?,?,?,?,?,?)',(row['decision_id'],row.get('decision_type'),row.get('subject_type'),row.get('subject_id'),row.get('status'),row.get('supersedes'),json_value(row.get('payload')),canonical(row)))
  for row in rows['relations.jsonl']:con.execute('INSERT INTO relations VALUES (?,?,?,?,?,?,?,?)',(row['relation_id'],row.get('relation_kind'),row.get('subject_type'),row.get('subject_id'),row.get('predicate'),row.get('target_type'),row.get('target_id'),canonical(row)))
  if con.execute('SELECT count(*) FROM assertions').fetchone()[0]!=sum(len(rows[n]) for n in ASSERTION_PARTITIONS):raise ValueError('SQLite active assertion count mismatch')
  if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite integrity_check failed')
  con.commit(); con.close(); con=None; os.replace(tmp_path,database_path)
 except Exception:
  if con is not None:
   try:con.rollback(); con.close()
   except sqlite3.Error:pass
  if tmp_path.exists():tmp_path.unlink()
  raise
 return manifest['projection_hash']
def query_snapshot(database_path):
 with sqlite3.connect(database_path) as con:
  metadata=sorted(con.execute('SELECT key,value FROM metadata ORDER BY key').fetchall()); return {'projection_hash':dict(metadata).get('projection_hash'),'metadata':metadata,'entities':con.execute('SELECT * FROM entities ORDER BY local_entity_id').fetchall(),'assertions':con.execute('SELECT * FROM assertions ORDER BY assertion_id').fetchall(),'assertion_history':con.execute('SELECT * FROM assertion_history ORDER BY assertion_id').fetchall(),'provenance':con.execute('SELECT * FROM provenance ORDER BY provenance_id').fetchall(),'reconciliation_history':con.execute('SELECT * FROM reconciliation_history ORDER BY decision_id').fetchall(),'relations':con.execute('SELECT * FROM relations ORDER BY relation_id').fetchall(),'sources':con.execute('SELECT * FROM sources ORDER BY source_id').fetchall(),'works':con.execute('SELECT * FROM works ORDER BY work_id').fetchall(),'evidence':con.execute('SELECT * FROM evidence ORDER BY evidence_id').fetchall()}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('projection'); ap.add_argument('database'); args=ap.parse_args(); print(build_database(Path(args.projection),Path(args.database)))
if __name__=='__main__':main()
