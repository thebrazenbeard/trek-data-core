#!/usr/bin/env python3
"""Shared deterministic verifier for canonical projection bundles consumed by derived adapters."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA=ROOT/'schema'/'projection-manifest.schema.json'
REQUIRED_OUTPUTS=('entities.jsonl','facts.jsonl','relations.jsonl','contested.jsonl','unresolved.jsonl','provenance.jsonl','assertion_history.jsonl','reconciliation_history.jsonl')
ID_KEYS={'entities.jsonl':'local_entity_id','facts.jsonl':'assertion_id','relations.jsonl':'relation_id','contested.jsonl':'assertion_id','unresolved.jsonl':'assertion_id','provenance.jsonl':'provenance_id','assertion_history.jsonl':'assertion_id','reconciliation_history.jsonl':'decision_id'}
HASH_RE=re.compile(r'^sha256:[0-9a-f]{64}$')

def canonical(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def sha256_bytes(data): return 'sha256:'+hashlib.sha256(data).hexdigest()
def compute_projection_hash(outputs): return sha256_bytes(canonical({name:outputs[name]['hash'] for name in REQUIRED_OUTPUTS}).encode())
def tool_identity(*paths):
 material=[]
 for path in sorted((Path(p) for p in paths),key=lambda p:str(p)):
  material.append({'path':path.name,'hash':sha256_bytes(path.read_bytes())})
 return sha256_bytes(canonical(material).encode('utf-8'))

def type_matches(value,expected):
 if expected=='null':return value is None
 if expected=='object':return isinstance(value,dict)
 if expected=='array':return isinstance(value,list)
 if expected=='string':return isinstance(value,str)
 if expected=='boolean':return isinstance(value,bool)
 if expected=='integer':return isinstance(value,int) and not isinstance(value,bool)
 if expected=='number':return isinstance(value,(int,float)) and not isinstance(value,bool)
 return True

def schema_errors(value,schema,location='$'):
 errors=[]; expected=schema.get('type')
 if expected is not None:
  allowed=expected if isinstance(expected,list) else [expected]
  if not any(type_matches(value,t) for t in allowed): return [f'{location}: expected type {allowed}']
 if 'const' in schema and value!=schema['const']:errors.append(f"{location}: expected constant {schema['const']!r}")
 if 'enum' in schema and value not in schema['enum']:errors.append(f'{location}: value not in enum')
 if isinstance(value,str) and len(value)<schema.get('minLength',0):errors.append(f'{location}: string shorter than minLength')
 if isinstance(value,list):
  if len(value)<schema.get('minItems',0):errors.append(f'{location}: array shorter than minItems')
  if 'items' in schema:
   for i,item in enumerate(value):errors.extend(schema_errors(item,schema['items'],f'{location}[{i}]'))
 if isinstance(value,dict):
  for req in schema.get('required',[]):
   if req not in value:errors.append(f'{location}: missing required property {req}')
  props=schema.get('properties',{})
  for key,item in value.items():
   if key in props:errors.extend(schema_errors(item,props[key],f'{location}.{key}'))
   elif schema.get('additionalProperties') is False:errors.append(f'{location}: unexpected property {key}')
 return errors

def parse_jsonl(path,id_key):
 rows=[]; seen=set(); raw_bytes=path.read_bytes()
 for line_no,raw in enumerate(raw_bytes.decode('utf-8').splitlines(),1):
  if not raw.strip():continue
  try:row=json.loads(raw)
  except Exception as exc:raise ValueError(f'{path}:{line_no}: invalid JSON: {exc}') from exc
  if not isinstance(row,dict):raise ValueError(f'{path}:{line_no}: row must be object')
  rid=row.get(id_key)
  if not isinstance(rid,str) or not rid:raise ValueError(f'{path}:{line_no}: row missing {id_key}')
  if rid in seen:raise ValueError(f'{path}: duplicate {id_key} {rid}')
  seen.add(rid); rows.append(row)
 canonical_bytes=''.join(canonical(r)+'\n' for r in sorted(rows,key=lambda r:(str(r.get(id_key,'')),canonical(r)))).encode('utf-8')
 if raw_bytes!=canonical_bytes:raise ValueError(f'{path}: JSONL bytes are not canonical deterministic serialization')
 return rows,raw_bytes

def verify_projection(root):
 root=Path(root); manifest_path=root/'manifest.json'
 if not manifest_path.exists():raise ValueError('projection manifest is missing')
 try:manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
 except Exception as exc:raise ValueError(f'invalid projection manifest: {exc}') from exc
 if not isinstance(manifest,dict):raise ValueError('projection manifest must be object')
 schema=json.loads(MANIFEST_SCHEMA.read_text(encoding='utf-8')); errors=schema_errors(manifest,schema)
 if errors:raise ValueError('projection manifest schema failure: '+'; '.join(errors))
 outputs=manifest.get('outputs',{})
 if set(outputs)!=set(REQUIRED_OUTPUTS):raise ValueError(f'projection outputs must be exactly {sorted(REQUIRED_OUTPUTS)}')
 actual_jsonl={p.name for p in root.glob('*.jsonl')}
 if actual_jsonl!=set(REQUIRED_OUTPUTS):raise ValueError(f'unexpected or missing JSONL projection outputs: {sorted(actual_jsonl ^ set(REQUIRED_OUTPUTS))}')
 for key in ('predicate_registry_hash','scope_key_registry_hash','input_hash','projection_hash'):
  if not HASH_RE.match(str(manifest.get(key,''))):raise ValueError(f'manifest {key} is not a sha256 identity')
 for key in ('projection_version','schema_version','methodology_version','compiler_commit','research_head','reconciliation_head'):
  if not isinstance(manifest.get(key),str) or not manifest[key].strip():raise ValueError(f'manifest {key} is missing')
 rows={}
 for name in REQUIRED_OUTPUTS:
  meta=outputs[name]
  if meta.get('role')!=name.removesuffix('.jsonl'):raise ValueError(f'{name}: role mismatch')
  path=root/name
  if not path.exists():raise ValueError(f'{name}: required output missing')
  parsed,raw_bytes=parse_jsonl(path,ID_KEYS[name]); rows[name]=parsed
  if meta.get('hash')!=sha256_bytes(raw_bytes):raise ValueError(f'{name}: content hash mismatch')
  if meta.get('count')!=len(parsed):raise ValueError(f'{name}: record count mismatch')
 active_ids=set()
 for name,allowed in (('facts.jsonl',{'STABLE'}),('unresolved.jsonl',{'UNRESOLVED'}),('contested.jsonl',{'CONTESTED','STRUCTURAL_PARADOX'})):
  for row in rows[name]:
   if row.get('projection_status') not in allowed:raise ValueError(f"{name}: invalid projection_status {row.get('projection_status')}")
   if row.get('effective_assertion_status')!='ACCEPTED':raise ValueError(f'{name}: active assertion is not effectively ACCEPTED')
   aid=row['assertion_id']
   if aid in active_ids:raise ValueError(f'assertion {aid} appears in multiple active partitions')
   active_ids.add(aid)
 for row in rows['relations.jsonl']:
  if row.get('record_type')!='projection_relation':raise ValueError('relations.jsonl contains non-projection_relation row')
 for row in rows['provenance.jsonl']:
  if row.get('record_type')!='projection_provenance':raise ValueError('provenance.jsonl contains non-projection_provenance row')
 recomputed=compute_projection_hash(outputs)
 if manifest.get('projection_hash')!=recomputed:raise ValueError(f"projection_hash mismatch: declared {manifest.get('projection_hash')}, expected {recomputed}")
 receipt={'projection_hash':manifest['projection_hash'],'input_hash':manifest['input_hash'],'projection_version':manifest['projection_version'],'schema_version':manifest['schema_version'],'methodology_version':manifest['methodology_version'],'compiler_commit':manifest['compiler_commit'],'research_head':manifest['research_head'],'reconciliation_head':manifest['reconciliation_head'],'predicate_registry_hash':manifest['predicate_registry_hash'],'scope_key_registry_hash':manifest['scope_key_registry_hash'],'verified_outputs':{name:outputs[name] for name in REQUIRED_OUTPUTS},'imported_output_contract':list(REQUIRED_OUTPUTS)}
 receipt_hash=sha256_bytes(canonical(receipt).encode('utf-8'))
 return {'manifest':manifest,'rows':rows,'receipt':receipt,'receipt_hash':receipt_hash}
