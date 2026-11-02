#!/usr/bin/env python3
"""Generate a deterministic PostgreSQL rebuild script from a verified canonical projection. No database connection is made."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path
_MODULE=Path(__file__).with_name('projection_bundle.py'); _SPEC=importlib.util.spec_from_file_location('trek_projection_bundle_pg',_MODULE); bundle=importlib.util.module_from_spec(_SPEC); _SPEC.loader.exec_module(bundle)
SCHEMA='trek_projection_v0_2'; BUNDLE_VERSION='0.2.0'; ASSERTION_PARTITIONS={'facts.jsonl':'facts','contested.jsonl':'contested','unresolved.jsonl':'unresolved'}

def canonical(v):return bundle.canonical(v)
def sha256_text(text):return 'sha256:'+hashlib.sha256(text.encode('utf-8')).hexdigest()
def sql_text(value):return 'NULL' if value is None else "'"+str(value).replace("'","''")+"'"
def sql_jsonb(value):return 'NULL' if value is None else sql_text(canonical(value))+'::jsonb'
def insert(table,columns,values):return f"INSERT INTO {SCHEMA}.{table} ({','.join(columns)}) VALUES ({','.join(values)});"
def add_catalog(catalog,key,row,label):
 if not isinstance(row,dict):return
 rid=row.get(key)
 if not rid:return
 if rid in catalog and canonical(catalog[rid])!=canonical(row):raise ValueError(f'conflicting {label} metadata for {rid}')
 catalog[rid]=row

def generate_sql(projection_root):
 verified=bundle.verify_projection(Path(projection_root)); rows=verified['rows']; manifest=verified['manifest']; builder_identity=bundle.tool_identity(Path(__file__),_MODULE)
 lines=['-- Generated derived PostgreSQL projection. Canonical JSONL remains source truth.',f"-- canonical_projection_hash: {manifest['projection_hash']}",f'-- verification_receipt_hash: {verified["receipt_hash"]}','BEGIN;','SET standard_conforming_strings = on;',"SET client_encoding = 'UTF8';",f'DROP SCHEMA IF EXISTS {SCHEMA} CASCADE;',f'CREATE SCHEMA {SCHEMA};','',
  f'CREATE TABLE {SCHEMA}.metadata (key text PRIMARY KEY,value text NOT NULL);',
  f'CREATE TABLE {SCHEMA}.entities (local_entity_id text PRIMARY KEY,work_id text,label text,identity_links jsonb,resolved_scope jsonb,record_json jsonb NOT NULL);',
  f"CREATE TABLE {SCHEMA}.assertions (assertion_id text PRIMARY KEY,projection_status text NOT NULL,partition text NOT NULL CHECK(partition IN ('facts','contested','unresolved')),subject_type text,subject text,predicate text,object_json jsonb,scope_json jsonb,resolved_scope jsonb,effective_assertion_status text NOT NULL,record_json jsonb NOT NULL);",
  f'CREATE TABLE {SCHEMA}.assertion_history (assertion_id text PRIMARY KEY,status text,supersedes text,record_json jsonb NOT NULL);',
  f'CREATE TABLE {SCHEMA}.provenance (provenance_id text PRIMARY KEY,assertion_id text NOT NULL,evidence_id text,record_json jsonb NOT NULL);',
  f'CREATE TABLE {SCHEMA}.reconciliation_history (decision_id text PRIMARY KEY,decision_type text,subject_type text,subject_id text,status text,supersedes text,payload_json jsonb,record_json jsonb NOT NULL);',
  f'CREATE TABLE {SCHEMA}.relations (relation_id text PRIMARY KEY,relation_kind text,subject_type text,subject_id text,predicate text,target_type text,target_id text,record_json jsonb NOT NULL);',
  f'CREATE TABLE {SCHEMA}.sources (source_id text PRIMARY KEY,record_json jsonb NOT NULL);',f'CREATE TABLE {SCHEMA}.works (work_id text PRIMARY KEY,record_json jsonb NOT NULL);',f'CREATE TABLE {SCHEMA}.evidence (evidence_id text PRIMARY KEY,record_json jsonb NOT NULL);','']
 metadata={'projection_hash':manifest['projection_hash'],'input_hash':manifest['input_hash'],'projection_version':manifest['projection_version'],'schema_version':manifest['schema_version'],'methodology_version':manifest['methodology_version'],'research_head':manifest['research_head'],'reconciliation_head':manifest['reconciliation_head'],'predicate_registry_hash':manifest['predicate_registry_hash'],'scope_key_registry_hash':manifest['scope_key_registry_hash'],'compiler_commit':manifest['compiler_commit'],'derived_schema_version':BUNDLE_VERSION,'derived_builder_identity':builder_identity,'verification_receipt_hash':verified['receipt_hash'],'verification_receipt_json':canonical(verified['receipt']),'imported_output_contract':canonical(list(bundle.REQUIRED_OUTPUTS))}
 for key,value in sorted(metadata.items()):lines.append(insert('metadata',['key','value'],[sql_text(key),sql_text(value)]))
 for row in rows['entities.jsonl']:lines.append(insert('entities',['local_entity_id','work_id','label','identity_links','resolved_scope','record_json'],[sql_text(row['local_entity_id']),sql_text(row.get('work_id')),sql_text(row.get('label')),sql_jsonb(row.get('identity_links')),sql_jsonb(row.get('resolved_scope')),sql_jsonb(row)]))
 for filename,partition in ASSERTION_PARTITIONS.items():
  for row in rows[filename]:lines.append(insert('assertions',['assertion_id','projection_status','partition','subject_type','subject','predicate','object_json','scope_json','resolved_scope','effective_assertion_status','record_json'],[sql_text(row['assertion_id']),sql_text(row['projection_status']),sql_text(partition),sql_text(row.get('subject_type')),sql_text(row.get('subject')),sql_text(row.get('predicate')),sql_jsonb(row.get('object')),sql_jsonb(row.get('scope')),sql_jsonb(row.get('resolved_scope')),sql_text(row.get('effective_assertion_status')),sql_jsonb(row)]))
 for row in rows['assertion_history.jsonl']:lines.append(insert('assertion_history',['assertion_id','status','supersedes','record_json'],[sql_text(row['assertion_id']),sql_text(row.get('status')),sql_text(row.get('supersedes')),sql_jsonb(row)]))
 sources={}; works={}; evidence={}
 for row in rows['provenance.jsonl']:
  lines.append(insert('provenance',['provenance_id','assertion_id','evidence_id','record_json'],[sql_text(row['provenance_id']),sql_text(row['assertion_id']),sql_text(row.get('evidence_id')),sql_jsonb(row)])); add_catalog(sources,'source_id',row.get('source_record'),'source'); add_catalog(works,'work_id',row.get('work_record'),'work'); add_catalog(evidence,'evidence_id',row.get('evidence_record'),'evidence')
  for item in row.get('source_lineage_records',[]):add_catalog(sources,'source_id',item,'source')
  for item in row.get('work_lineage_records',[]):add_catalog(works,'work_id',item,'work')
 for sid,row in sorted(sources.items()):lines.append(insert('sources',['source_id','record_json'],[sql_text(sid),sql_jsonb(row)]))
 for wid,row in sorted(works.items()):lines.append(insert('works',['work_id','record_json'],[sql_text(wid),sql_jsonb(row)]))
 for eid,row in sorted(evidence.items()):lines.append(insert('evidence',['evidence_id','record_json'],[sql_text(eid),sql_jsonb(row)]))
 for row in rows['reconciliation_history.jsonl']:lines.append(insert('reconciliation_history',['decision_id','decision_type','subject_type','subject_id','status','supersedes','payload_json','record_json'],[sql_text(row['decision_id']),sql_text(row.get('decision_type')),sql_text(row.get('subject_type')),sql_text(row.get('subject_id')),sql_text(row.get('status')),sql_text(row.get('supersedes')),sql_jsonb(row.get('payload')),sql_jsonb(row)]))
 for row in rows['relations.jsonl']:lines.append(insert('relations',['relation_id','relation_kind','subject_type','subject_id','predicate','target_type','target_id','record_json'],[sql_text(row['relation_id']),sql_text(row.get('relation_kind')),sql_text(row.get('subject_type')),sql_text(row.get('subject_id')),sql_text(row.get('predicate')),sql_text(row.get('target_type')),sql_text(row.get('target_id')),sql_jsonb(row)]))
 lines.extend(['',f'CREATE INDEX assertions_status_idx ON {SCHEMA}.assertions(projection_status);',f'CREATE INDEX assertions_subject_idx ON {SCHEMA}.assertions(subject_type,subject);',f'CREATE INDEX assertions_predicate_idx ON {SCHEMA}.assertions(predicate);',f'CREATE INDEX provenance_assertion_idx ON {SCHEMA}.provenance(assertion_id);',f'CREATE INDEX reconciliation_subject_idx ON {SCHEMA}.reconciliation_history(subject_type,subject_id);',f'CREATE INDEX relations_subject_idx ON {SCHEMA}.relations(subject_type,subject_id);',f'CREATE INDEX relations_target_idx ON {SCHEMA}.relations(target_type,target_id);','COMMIT;',''])
 return '\n'.join(lines)

def write_bundle(projection_root,output_root):
 projection_root=Path(projection_root); output_root=Path(output_root); verified=bundle.verify_projection(projection_root); output_root.mkdir(parents=True,exist_ok=True); sql=generate_sql(projection_root); (output_root/'projection.sql').write_text(sql,encoding='utf-8'); manifest={'record_type':'postgres_projection_bundle','bundle_version':BUNDLE_VERSION,'schema':SCHEMA,'projection_hash':verified['manifest']['projection_hash'],'builder_identity':bundle.tool_identity(Path(__file__),_MODULE),'verification_receipt_hash':verified['receipt_hash'],'verification_receipt':verified['receipt'],'imported_output_contract':list(bundle.REQUIRED_OUTPUTS),'sql_hash':sha256_text(sql),'sql_file':'projection.sql'}; (output_root/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8'); return manifest

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('projection'); ap.add_argument('output'); args=ap.parse_args(); print(write_bundle(Path(args.projection),Path(args.output))['sql_hash'])
if __name__=='__main__':main()
