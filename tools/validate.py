#!/usr/bin/env python3
"""Deterministic repository admission validation with no network dependencies."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA_ROOTS=[ROOT/'registry'/'authoritative',ROOT/'research',ROOT/'reconciliation',ROOT/'external',ROOT/'migrations']
SCHEMA_ROOT=ROOT/'schema'; PREDICATE_REGISTRY=ROOT/'registry'/'predicates.json'; SCOPE_KEY_REGISTRY=ROOT/'registry'/'scope_keys.json'
LIBRARIAN_SCHEMA=ROOT/'registry'/'librarian_registry_contract.schema.json'
SCHEMA_FILES={'source':'source.schema.json','work':'work.schema.json','source_work_binding':'source-work-binding.schema.json','local_entity':'local-entity.schema.json','evidence':'evidence.schema.json','assertion':'assertion.schema.json','batch_manifest':'batch-manifest.schema.json','reconciliation_decision':'reconciliation-decision.schema.json'}
ID_FIELDS={'source':'source_id','work':'work_id','source_work_binding':'binding_id','local_entity':'local_entity_id','evidence':'evidence_id','assertion':'assertion_id','batch_manifest':'batch_id','reconciliation_decision':'decision_id'}
REFERENCE_TYPES={'SOURCE':'source','WORK':'work','LOCAL_ENTITY':'local_entity','EVIDENCE':'evidence','ASSERTION':'assertion','RECONCILIATION_DECISION':'reconciliation_decision'}
COUNT_KEYS={'sources':'source','works':'work','local_entities':'local_entity','evidence':'evidence','assertions':'assertion','reconciliation_decisions':'reconciliation_decision'}
REQUIRED_BATCH_COUNTS=('local_entities','evidence','assertions'); WORKER_FORBIDDEN_RECORD_TYPES={'source','work','source_work_binding','reconciliation_decision'}
CONTENT_BASIS_KINDS={'CONTENT_BODY_AUDIT','CONTENT_FINGERPRINT','BYTE_HASH','NORMALIZED_PASSAGE_FINGERPRINT','CONTAINER_MANIFEST'}
SHA256_PATTERN=re.compile(r'sha256:[0-9a-f]{64}\Z')
PROJECTION_STATUSES={'STABLE','CONTESTED','UNRESOLVED','STRUCTURAL_PARADOX'}; DISPOSITIONS={'PROPOSED','ACCEPTED','REJECTED'}
USAGE_LEVELS={'RESEARCH_ASSERTION','RECONCILIATION_RELATION','EXTERNAL_CROSSWALK','EVIDENCE_ANNOTATION'}
PREDICATE_METADATA_REQUIRED={'name','status','definition','semantic_class','usage_levels','subject_types','object_mode','object_ref_types','symmetry','inverse','transitive','projection_eligibility','examples','near_miss','supersedes','superseded_by','methodology_version','introduced_in_registry'}
RESEARCH_WORKERS={'tos':'TOS','tas':'TAS','tng':'TNG','ds9':'DS9','voyager':'VOY','enterprise':'ENT','discovery':'DIS','short-treks':'SHORT','picard':'PIC','lower-decks':'LD','prodigy':'PRO','strange-new-worlds':'SNW','starfleet-academy':'SFA','films':'FILMS','literature':'LIT'}

def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def sha256_canonical(v):return 'sha256:'+hashlib.sha256(canonical(v).encode()).hexdigest()
def physical_path(path):
 m=re.match(r'^(.*\.jsonl):\d+$',str(path)); return Path(m.group(1)) if m else Path(path)
def unique_json_pairs(pairs):
 result={}
 for key,value in pairs:
  if key in result:raise ValueError(f'duplicate JSON key: {key}')
  result[key]=value
 return result
def strict_json(raw):return json.loads(raw,object_pairs_hook=unique_json_pairs)
def governed_paths(base):
 """Never read through symlinked governed files, directories, or roots."""
 if not base.exists() and not base.is_symlink():return [],[]
 if base.is_symlink() or not base.is_dir():raise ValueError(f'{base}: unsafe symlink or non-directory governed root')
 for item in sorted(base.rglob('*')):
  if item.is_symlink():raise ValueError(f'{item}: symlink in governed input root')
  if not item.resolve().is_relative_to(base.resolve()):raise ValueError(f'{item}: path escapes governed input root')
 return sorted(p for p in base.rglob('*.json') if p.is_file()),sorted(p for p in base.rglob('*.jsonl') if p.is_file())
def iter_records():
 for base in DATA_ROOTS:
  json_files,jsonl_files=governed_paths(base)
  for path in json_files:
   if path.name=='README.json':continue
   try:row=strict_json(path.read_text(encoding='utf-8'))
   except Exception as exc:raise ValueError(f'{path}: invalid JSON: {exc}') from exc
   if not isinstance(row,dict):raise ValueError(f'{path}: governed JSON artifact must be an object record')
   yield path,row
  for path in jsonl_files:
   for line_no,raw in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
    if not raw.strip():continue
    try:row=strict_json(raw)
    except Exception as exc:raise ValueError(f'{path}:{line_no}: invalid JSONL: {exc}') from exc
    if not isinstance(row,dict):raise ValueError(f'{path}:{line_no}: record must be an object')
    yield Path(f'{path}:{line_no}'),row
def load_schemas():return {rt:strict_json((SCHEMA_ROOT/fn).read_text(encoding='utf-8')) for rt,fn in SCHEMA_FILES.items()}
def load_authoritative_librarian_schemas():
 """Reuse the main Librarian registry contract, not a looser duplicate."""
 registry=strict_json(LIBRARIAN_SCHEMA.read_text(encoding='utf-8'))
 defs=registry.get('$defs',{})
 required={'source','work','source_work_binding'}
 if not required.issubset(defs):raise ValueError('Librarian registry contract lacks canonical Source/Work/binding definitions')
 return {rt:defs[rt] for rt in required}
def is_authoritative_librarian_path(path):
 """Recognize real repo paths and isolated test roots with the same topology."""
 p=physical_path(path)
 if p.is_relative_to(ROOT/'registry'/'authoritative'):return True
 return any(p.parts[i:i+2]==('registry','authoritative') for i in range(len(p.parts)-1))
def load_predicate_registry():
 registry=strict_json(PREDICATE_REGISTRY.read_text(encoding='utf-8')); entries={}; errors=[]
 if not registry.get('registry_version'):errors.append('predicate registry missing registry_version')
 if not registry.get('schema_version'):errors.append('predicate registry missing schema_version')
 for item in registry.get('predicates',[]):
  name=item.get('name'); missing=sorted(PREDICATE_METADATA_REQUIRED-set(item))
  if not name:errors.append('predicate registry entry missing name');continue
  if name in entries:errors.append(f'duplicate predicate registry entry {name}');continue
  if missing:errors.append(f"predicate {name} missing metadata: {', '.join(missing)}")
  if item.get('status') not in {'CANDIDATE','EXPERIMENTAL','ACCEPTED','DEPRECATED'}:errors.append(f"predicate {name} has invalid lifecycle status {item.get('status')!r}")
  if item.get('object_mode') not in {'LITERAL','REFERENCE_ONLY','LITERAL_OR_REFERENCE'}:errors.append(f"predicate {name} has invalid object_mode {item.get('object_mode')!r}")
  levels=item.get('usage_levels')
  if not isinstance(levels,list) or not levels:errors.append(f'predicate {name} requires non-empty usage_levels')
  elif len(levels)!=len(set(levels)) or any(level not in USAGE_LEVELS for level in levels):errors.append(f'predicate {name} has invalid usage_levels {levels!r}')
  if not isinstance(item.get('subject_types'),list) or not item.get('subject_types'):errors.append(f'predicate {name} requires subject_types')
  if not isinstance(item.get('object_ref_types'),list):errors.append(f'predicate {name} requires object_ref_types array')
  if not isinstance(item.get('examples'),list) or not item.get('examples'):errors.append(f'predicate {name} requires a positive example')
  if not isinstance(item.get('near_miss'),str) or not item.get('near_miss','').strip():errors.append(f'predicate {name} requires near_miss')
  if not item.get('methodology_version') or not item.get('introduced_in_registry'):errors.append(f'predicate {name} requires methodology/registry provenance')
  if item.get('status')=='ACCEPTED':
   if 'RESEARCH_ASSERTION' in set(levels or []) and item.get('projection_eligibility')!='ACCEPTED_ASSERTION_ALLOWED':errors.append(f'accepted research predicate {name} must declare ACCEPTED_ASSERTION_ALLOWED')
   if 'RESEARCH_ASSERTION' not in set(levels or []) and item.get('projection_eligibility') not in {'CONTEXT_ONLY','ACCEPTED_ASSERTION_ALLOWED'}:errors.append(f'accepted non-research predicate {name} requires context-governed projection eligibility')
  if item.get('status')=='EXPERIMENTAL' and item.get('projection_eligibility')!='EXPERIMENTAL_ONLY':errors.append(f'experimental predicate {name} must declare EXPERIMENTAL_ONLY')
  entries[name]=item
 for name,item in entries.items():
  for field in ('inverse','supersedes','superseded_by'):
   target=item.get(field)
   if target and target not in entries:errors.append(f'predicate {name} {field} references unknown predicate {target}')
 return entries,errors
def load_scope_key_registry():
 registry=strict_json(SCOPE_KEY_REGISTRY.read_text(encoding='utf-8')); entries={}; errors=[]
 if not registry.get('registry_version'):errors.append('scope-key registry missing registry_version')
 if not registry.get('methodology_version'):errors.append('scope-key registry missing methodology_version')
 for item in registry.get('scope_keys',[]):
  key=item.get('key')
  if not isinstance(key,str) or not key.strip():errors.append('scope-key entry missing key');continue
  if key in entries:errors.append(f'duplicate scope key {key}');continue
  types=item.get('subject_types')
  if not isinstance(types,list) or not types:errors.append(f'scope key {key} requires subject_types')
  elif any(t not in {'WORK','LOCAL_ENTITY','ASSERTION'} for t in types):errors.append(f'scope key {key} has unsupported subject type')
  if not isinstance(item.get('definition'),str) or not item.get('definition','').strip():errors.append(f'scope key {key} requires definition')
  entries[key]=item
 return entries,errors
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
  if not any(type_matches(value,t) for t in allowed):return [f'{location}: expected type {allowed}, got {type(value).__name__}']
 if 'const' in schema and value!=schema['const']:errors.append(f"{location}: expected constant {schema['const']!r}, got {value!r}")
 if 'enum' in schema and value not in schema['enum']:errors.append(f"{location}: value {value!r} is not in enum {schema['enum']!r}")
 if isinstance(value,str) and len(value)<schema.get('minLength',0):errors.append(f"{location}: string shorter than minLength {schema['minLength']}")
 if isinstance(value,list):
  if len(value)<schema.get('minItems',0):errors.append(f"{location}: array shorter than minItems {schema['minItems']}")
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
def add_missing_reference(errors,path,field,target_type,target_id,index):
 rt=REFERENCE_TYPES.get(target_type,target_type.lower() if isinstance(target_type,str) else None)
 if rt and target_id and target_id not in index.get(rt,{}):errors.append(f'{path}: {field} references missing {target_type} {target_id}')
def typed_ref(value):
 if not isinstance(value,dict):return None
 if 'ref_type' not in value and 'ref_id' not in value:return None
 return value.get('ref_type'),value.get('ref_id')
def validate_predicate_assertion(path,assertion,registry,index,errors):
 name=assertion.get('predicate'); entry=registry.get(name)
 if entry is None:errors.append(f"{path}: assertion {assertion.get('assertion_id')} uses unregistered predicate {name}");return
 if 'RESEARCH_ASSERTION' not in set(entry.get('usage_levels',[])):errors.append(f'{path}: predicate {name} does not allow RESEARCH_ASSERTION usage')
 lifecycle=entry.get('status'); record_status=assertion.get('status')
 if lifecycle=='CANDIDATE':errors.append(f'{path}: candidate predicate {name} may not be used in research records')
 elif lifecycle=='EXPERIMENTAL' and record_status!='PROPOSED':errors.append(f'{path}: experimental predicate {name} may only be used on PROPOSED assertions')
 elif lifecycle=='DEPRECATED':errors.append(f'{path}: deprecated predicate {name} may not be used for new assertion admission')
 if record_status=='ACCEPTED' and 'RESEARCH_ASSERTION' in set(entry.get('usage_levels',[])) and entry.get('projection_eligibility')!='ACCEPTED_ASSERTION_ALLOWED':errors.append(f'{path}: predicate {name} is not eligible for accepted assertion projection')
 subject_type=assertion.get('subject_type'); allowed=set(entry.get('subject_types',[]))
 if 'ANY' not in allowed and subject_type not in allowed:errors.append(f'{path}: predicate {name} does not allow subject_type {subject_type}')
 obj=assertion.get('object'); ref=typed_ref(obj); mode=entry.get('object_mode')
 if isinstance(obj,dict) and ('ref_type' in obj or 'ref_id' in obj) and set(obj)!={'ref_type','ref_id'}:errors.append(f'{path}: typed assertion object may contain only ref_type and ref_id')
 if mode=='REFERENCE_ONLY' and ref is None:errors.append(f'{path}: predicate {name} requires a typed object reference')
 if mode=='LITERAL' and ref is not None:errors.append(f'{path}: predicate {name} requires a literal object')
 if ref is not None:
  ref_type,ref_id=ref
  if not ref_type or not ref_id:errors.append(f'{path}: typed assertion object requires both ref_type and ref_id')
  elif ref_type not in REFERENCE_TYPES:errors.append(f'{path}: typed assertion object has unsupported ref_type {ref_type}')
  else:
   if ref_type not in set(entry.get('object_ref_types',[])):errors.append(f'{path}: predicate {name} does not allow object ref_type {ref_type}')
   add_missing_reference(errors,path,'object',ref_type,ref_id,index)
def validate_assertion_references(path,a,index,errors):
 st=a.get('subject_type');sid=a.get('subject')
 if st in REFERENCE_TYPES:add_missing_reference(errors,path,'subject',st,sid,index)
 evidence=a.get('evidence',[])
 if len(evidence)!=len(set(evidence)):errors.append(f'{path}: assertion evidence support set contains duplicates')
 for eid in evidence:add_missing_reference(errors,path,'evidence','EVIDENCE',eid,index)
 if a.get('supersedes'):add_missing_reference(errors,path,'supersedes','ASSERTION',a['supersedes'],index)
def validate_references(records,index,errors):
 for path,row in records:
  rt=row.get('record_type')
  if rt=='source':
   for sid in row.get('derived_from',[]):add_missing_reference(errors,path,'derived_from','SOURCE',sid,index)
  elif rt=='work':
   if row.get('parent_work_id'):add_missing_reference(errors,path,'parent_work_id','WORK',row['parent_work_id'],index)
   if not any(isinstance(row.get(k),str) and row[k].strip() for k in ('medium','work_type')):
    errors.append(f'{path}: work requires a non-empty medium or work_type')
  elif rt=='source_work_binding':
   add_missing_reference(errors,path,'source_id','SOURCE',row.get('source_id'),index)
   add_missing_reference(errors,path,'work_id','WORK',row.get('work_id'),index)
   if row.get('supersedes_binding_id'):
    add_missing_reference(errors,path,'supersedes_binding_id','source_work_binding',row['supersedes_binding_id'],index)
  elif rt=='local_entity':add_missing_reference(errors,path,'work_id','WORK',row.get('work_id'),index)
  elif rt=='evidence':
   add_missing_reference(errors,path,'source_id','SOURCE',row.get('source_id'),index);add_missing_reference(errors,path,'work_id','WORK',row.get('work_id'),index)
   if row.get('observer_local_entity_id'):add_missing_reference(errors,path,'observer_local_entity_id','LOCAL_ENTITY',row['observer_local_entity_id'],index)
  elif rt=='assertion':validate_assertion_references(path,row,index,errors)
  elif rt=='reconciliation_decision':
   for eid in row.get('evidence',[]):
    if eid not in index.get('evidence',{}) and eid not in index.get('assertion',{}):errors.append(f'{path}: evidence references missing EVIDENCE/ASSERTION {eid}')
   if row.get('supersedes'):add_missing_reference(errors,path,'supersedes','RECONCILIATION_DECISION',row['supersedes'],index)
   if row.get('subject_type') in REFERENCE_TYPES:add_missing_reference(errors,path,'subject',row['subject_type'],row.get('subject_id'),index)

def validate_source_work_lineage(index,errors):
 """Detect every Source DAG and Work ancestry cycle, not only evidence-reachable ones."""
 sources=index.get('source',{});works=index.get('work',{})
 for sid,source in sources.items():
  parents=source.get('derived_from',[])
  if not isinstance(parents,list):continue
  for parent_id in parents:
   parent=sources.get(parent_id)
   if not parent:continue  # Dangling reference is checked elsewhere.
   child_group=source.get('independence_group');parent_group=parent.get('independence_group')
   if child_group and parent_group and child_group!=parent_group:
    errors.append(f'source {sid}: derived Source cannot mint new independence_group distinct from {parent_id}')

 def detect_cycles(rows,edges,label):
  done=set()
  for start in rows:
   if start in done:continue
   stack=[(start,False)];active=set()
   while stack:
    current,closing=stack.pop()
    if closing:
     active.discard(current);done.add(current);continue
    if current in active:
     errors.append(f'{label} cycle at {current}');continue
    if current in done or current not in rows:continue
    active.add(current);stack.append((current,True))
    for parent in reversed(edges(rows[current])):
     if isinstance(parent,str) and parent:stack.append((parent,False))
 detect_cycles(sources,lambda r:r.get('derived_from',[]) if isinstance(r.get('derived_from',[]),list) else [],'source derivation')
 detect_cycles(works,lambda r:[r['parent_work_id']] if isinstance(r.get('parent_work_id'),str) and r['parent_work_id'] else [],'work parent')

def content_basis_errors(binding,source):
 errors=[];basis=binding.get('basis') or []
 if not isinstance(basis,list):return ['basis must be a list']
 for item in basis:
  if not isinstance(item,dict):continue
  if item.get('kind')=='BYTE_HASH':
   value=item.get('value')
   if not isinstance(value,str) or not SHA256_PATTERN.fullmatch(value):
    errors.append('BYTE_HASH basis must be lowercase sha256:<64-hex>')
   elif value!=source.get('content_hash'):
    errors.append('BYTE_HASH basis must equal the bound Source.content_hash')
 if not any(isinstance(x,dict) and x.get('kind') in CONTENT_BASIS_KINDS
            and isinstance(x.get('value'),str) and x['value'].strip() for x in basis):
  errors.append('binding lacks content/hash/manifest basis')
 return errors

def eligible_evidence_binding(evidence,index):
 """Resolve one active, content-grounded Librarian binding; never infer a scoped match."""
 sources=index.get('source',{});works=index.get('work',{});bindings=index.get('source_work_binding',{})
 source=sources.get(evidence.get('source_id'));work=works.get(evidence.get('work_id'))
 if not source or not work:return None
 if source.get('status')!='ACCEPTED' or work.get('status')!='ACCEPTED':return None
 if source.get('fixture_only') is not False or work.get('fixture_only') is not False:return None
 successor_ids={b.get('supersedes_binding_id') for b in bindings.values() if b.get('lifecycle')=='ACCEPTED' and b.get('supersedes_binding_id')}
 requested=evidence.get('source_work_binding_id')
 if 'source_work_binding_id' in evidence and (not isinstance(requested,str) or not requested.strip()):return None
 eligible=[]
 for b in bindings.values():
  if b.get('binding_id') in successor_ids or b.get('lifecycle')!='ACCEPTED' or b.get('mapping_role')!='EVIDENCE_BEARING' or b.get('fixture_only') is not False:continue
  if b.get('source_id')!=evidence.get('source_id') or b.get('work_id')!=evidence.get('work_id'):continue
  basis=b.get('basis') or []
  if not isinstance(basis,list):continue
  if not isinstance(b.get('method'),str) or not b['method'].strip() or content_basis_errors(b,source):continue
  src_scope=b.get('source_scope') or {};work_scope=b.get('work_scope') or {}
  if not isinstance(src_scope,dict) or not isinstance(work_scope,dict):continue
  if src_scope.get('scope_type') not in {'WHOLE','SLICE','COMPONENT'} or work_scope.get('scope_type') not in {'WHOLE','COMPONENT'}:continue
  if src_scope.get('scope_type') in {'SLICE','COMPONENT'} and not (isinstance(src_scope.get('locator'),str) and src_scope['locator'].strip()):continue
  if work_scope.get('scope_type')=='COMPONENT' and not (isinstance(work_scope.get('component_label'),str) and work_scope['component_label'].strip()):continue
  is_whole=src_scope.get('scope_type')=='WHOLE' and work_scope.get('scope_type')=='WHOLE'
  # Non-whole scopes require explicit binding selection; geometric/range containment
  # remains a separate typed-locator contract, never assumed from a matching pair.
  if not is_whole and not requested:continue
  if requested and b.get('binding_id')!=requested:continue
  eligible.append(b)
 return eligible[0] if len(eligible)==1 else None

def validate_binding_integrity(records,index,errors):
 bindings=index.get('source_work_binding',{});sources=index.get('source',{});works=index.get('work',{})
 for bid,b in bindings.items():
  predecessor=b.get('supersedes_binding_id')
  if predecessor and predecessor==bid:errors.append(f'binding {bid}: cannot supersede itself')
  if b.get('lifecycle')=='ACCEPTED':
   if b.get('fixture_only') is not False:errors.append(f'binding {bid}: fixture-only record cannot be authoritative')
   if b.get('mapping_role')!='EVIDENCE_BEARING':
    errors.append(f'binding {bid}: ACCEPTED binding must be EVIDENCE_BEARING under the current Librarian contract')
   if (sources.get(b.get('source_id'),{}).get('fixture_only') is not False
       or works.get(b.get('work_id'),{}).get('fixture_only') is not False):
    errors.append(f'binding {bid}: non-fixture accepted binding cannot use fixture-only Source or Work')
   if predecessor and bindings.get(predecessor) and bindings[predecessor].get('lifecycle')!='SUPERSEDED':
    errors.append(f'binding {bid}: accepted binding successor requires SUPERSEDED predecessor {predecessor}')
   if b.get('mapping_role')=='EVIDENCE_BEARING':
    if not isinstance(b.get('method'),str) or not b['method'].strip():errors.append(f'binding {bid}: evidence-bearing binding requires method')
    for issue in content_basis_errors(b,sources.get(b.get('source_id'),{})):
     errors.append(f'binding {bid}: {issue}')
   if sources.get(b.get('source_id'),{}).get('status')!='ACCEPTED' or works.get(b.get('work_id'),{}).get('status')!='ACCEPTED':errors.append(f'binding {bid}: Source and Work must be ACCEPTED')
   source_scope=b.get('source_scope') or {};work_scope=b.get('work_scope') or {}
   if not isinstance(source_scope,dict):source_scope={}
   if not isinstance(work_scope,dict):work_scope={}
   if source_scope.get('scope_type') in {'SLICE','COMPONENT'} and not (isinstance(source_scope.get('locator'),str) and source_scope['locator'].strip()):errors.append(f'binding {bid}: scoped Source requires locator')
   if work_scope.get('scope_type')=='COMPONENT' and not (isinstance(work_scope.get('component_label'),str) and work_scope['component_label'].strip()):errors.append(f'binding {bid}: component Work requires component_label')
  seen=set();cur=bid
  while cur:
   if cur in seen:errors.append(f'binding {bid}: supersession cycle');break
   seen.add(cur);row=bindings.get(cur);cur=row.get('supersedes_binding_id') if row else None
 exclusive={}
 for b in bindings.values():
  if b.get('lifecycle')!='ACCEPTED' or not b.get('exclusive_scope_key'):continue
  key=(b.get('source_id'),b.get('exclusive_scope_key'))
  prior=exclusive.setdefault(key,b)
  if prior is not b and prior.get('work_id')!=b.get('work_id'):errors.append(f'binding: conflicting exclusive scope {key}')
 for path,row in records:
  if row.get('record_type')!='evidence':continue
  if eligible_evidence_binding(row,index) is None:
   errors.append(f'{path}: evidence {row.get("evidence_id")} lacks one eligible ACCEPTED EVIDENCE_BEARING Source-Work binding')

def effectively_superseded_assertions(assertions,dispositions):
 """Only effectively accepted successor assertions revoke their predecessors."""
 return {row['supersedes'] for aid,row in assertions.items()
         if row.get('supersedes') and dispositions.get(aid,row.get('status'))=='ACCEPTED'}
def batch_records_for(manifest_path,records):
 root=physical_path(manifest_path).parent;selected=[]
 for path,row in records:
  if row.get('record_type')=='batch_manifest':continue
  try:physical_path(path).relative_to(root)
  except ValueError:continue
  selected.append(row)
 return sorted(selected,key=canonical)
def compute_batch_hash(manifest,batch_records):return sha256_canonical({'manifest':{k:v for k,v in manifest.items() if k!='batch_hash'},'records':batch_records})
def research_lane_for_path(path):
 physical=physical_path(path)
 for root in DATA_ROOTS:
  if root.name!='research':continue
  try:rel=physical.relative_to(root)
  except ValueError:continue
  if rel.parts and rel.parts[0] in RESEARCH_WORKERS:return rel.parts[0]
 return None
def validate_partition_ownership(records,errors):
 for path,row in records:
  lane=research_lane_for_path(path)
  if lane and row.get('record_type') in WORKER_FORBIDDEN_RECORD_TYPES:errors.append(f"{path}: authoritative {row.get('record_type')} record is not allowed under worker research partition {lane}")
  physical=physical_path(path)
  if row.get('record_type')=='source_work_binding' and physical.is_relative_to(ROOT) and not physical.is_relative_to(ROOT/'registry'/'authoritative'):
   errors.append(f'{path}: source_work_binding requires authoritative Librarian registry root')
  if row.get('record_type') in {'source','work'} and row.get('status')=='ACCEPTED' and row.get('fixture_only') is False and physical.is_relative_to(ROOT) and not physical.is_relative_to(ROOT/'registry'/'authoritative'):
   errors.append(f'{path}: accepted {row["record_type"]} requires authoritative Librarian registry root')
def validate_batch_integrity(records,index,errors):
 hashes={r.get('content_hash') for r in index.get('source',{}).values() if r.get('content_hash')}
 for path,m in records:
  if m.get('record_type')!='batch_manifest':continue
  rows=batch_records_for(path,records);expected=compute_batch_hash(m,rows)
  if m.get('batch_hash')!=expected:errors.append(f"{path}: batch_hash mismatch: declared {m.get('batch_hash')}, expected {expected}")
  counts={}
  for row in rows:counts[row.get('record_type')]=counts.get(row.get('record_type'),0)+1
  declared=m.get('record_counts',{})
  for key in REQUIRED_BATCH_COUNTS:
   if key not in declared:errors.append(f'{path}: record_counts.{key} is required for a governed research batch')
  for key,rt in COUNT_KEYS.items():
   if key in declared and declared[key]!=counts.get(rt,0):errors.append(f'{path}: record_counts.{key}={declared[key]} but batch contains {counts.get(rt,0)}')
  for wid in m.get('works',[]):add_missing_reference(errors,path,'works','WORK',wid,index)
  for h in m.get('source_hashes',[]):
   if h not in hashes:errors.append(f'{path}: source_hashes references unknown source content_hash {h}')
  lane=research_lane_for_path(path)
  if lane and m.get('worker_id')!=RESEARCH_WORKERS[lane]:errors.append(f"{path}: worker_id {m.get('worker_id')} does not match research partition owner {RESEARCH_WORKERS[lane]}")
def validate_payload(path,decision,registry,scope_keys,index,errors):
 t=decision.get('decision_type');p=decision.get('payload') or {};status=decision.get('status');st=decision.get('subject_type')
 if t=='ENTITY_LINK':
  if st!='LOCAL_ENTITY':errors.append(f'{path}: ENTITY_LINK requires subject_type LOCAL_ENTITY')
  required={'relation_predicate','target_type','target_id'};missing=sorted(required-set(p))
  if missing:errors.append(f"{path}: ENTITY_LINK payload missing {', '.join(missing)}");return
  if set(p)!=required:errors.append(f'{path}: ENTITY_LINK payload may contain only relation_predicate, target_id, target_type')
  if p.get('target_type')!='LOCAL_ENTITY':errors.append(f'{path}: ENTITY_LINK target_type must be LOCAL_ENTITY until a global-entity schema is governed')
  pred=registry.get(p.get('relation_predicate'))
  if pred is None:errors.append(f"{path}: ENTITY_LINK uses unregistered relation predicate {p.get('relation_predicate')}");return
  if 'RECONCILIATION_RELATION' not in set(pred.get('usage_levels',[])):errors.append(f"{path}: ENTITY_LINK predicate {pred.get('name')} does not allow RECONCILIATION_RELATION usage")
  if pred.get('semantic_class')!='IDENTITY_RELATION':errors.append(f"{path}: ENTITY_LINK predicate {pred.get('name')} is not governed as IDENTITY_RELATION")
  if status=='ACCEPTED' and pred.get('status')!='ACCEPTED':errors.append(f"{path}: accepted ENTITY_LINK may not use {pred.get('status')} predicate {pred.get('name')}")
  if status=='PROPOSED' and pred.get('status') not in {'ACCEPTED','EXPERIMENTAL'}:errors.append(f"{path}: proposed ENTITY_LINK may not use {pred.get('status')} predicate {pred.get('name')}")
  if st not in set(pred.get('subject_types',[])):errors.append(f"{path}: identity predicate {pred.get('name')} does not allow subject_type {st}")
  tt=p.get('target_type')
  if tt not in set(pred.get('object_ref_types',[])):errors.append(f"{path}: identity predicate {pred.get('name')} does not allow target_type {tt}")
  if tt in REFERENCE_TYPES:add_missing_reference(errors,path,'payload.target_id',tt,p.get('target_id'),index)
 elif t=='ASSERTION_DISPOSITION':
  if st!='ASSERTION':errors.append(f'{path}: ASSERTION_DISPOSITION requires subject_type ASSERTION')
  if set(p)!={'disposition'} or p.get('disposition') not in DISPOSITIONS:errors.append(f'{path}: ASSERTION_DISPOSITION payload must contain only a governed disposition')
 elif t=='ASSERTION_PROJECTION_STATUS':
  if st!='ASSERTION':errors.append(f'{path}: ASSERTION_PROJECTION_STATUS requires subject_type ASSERTION')
  if set(p)!={'projection_status'} or p.get('projection_status') not in PROJECTION_STATUSES:errors.append(f'{path}: ASSERTION_PROJECTION_STATUS payload must contain only a governed projection_status')
 elif t=='SCOPE_RESOLUTION':
  if st not in {'ASSERTION','WORK','LOCAL_ENTITY'}:errors.append(f'{path}: SCOPE_RESOLUTION subject_type must be ASSERTION, WORK, or LOCAL_ENTITY')
  if set(p)!={'resolution_key','resolution'} or not isinstance(p.get('resolution_key'),str) or not p.get('resolution_key').strip():errors.append(f'{path}: SCOPE_RESOLUTION payload requires non-empty resolution_key and resolution')
  else:
   entry=scope_keys.get(p['resolution_key'])
   if entry is None:errors.append(f"{path}: SCOPE_RESOLUTION uses ungoverned resolution_key {p['resolution_key']}")
   elif st not in set(entry.get('subject_types',[])):errors.append(f"{path}: scope key {p['resolution_key']} does not allow subject_type {st}")
 elif t=='OTHER' and status=='ACCEPTED':errors.append(f'{path}: OTHER reconciliation decisions are proposal/staging only and may not be ACCEPTED')
def decision_active_key(d):
 t=d.get('decision_type');p=d.get('payload') or {};base=(t,d.get('subject_type'),d.get('subject_id'))
 if t=='ENTITY_LINK':return base+(p.get('relation_predicate'),)
 if t=='SCOPE_RESOLUTION':return base+(p.get('resolution_key'),)
 if t in {'ASSERTION_DISPOSITION','ASSERTION_PROJECTION_STATUS'}:return base
 return None
def validate_assertion_lineage(index,errors):
 assertions=index.get('assertion',{})
 for start in assertions:
  seen=set();cur=start
  while cur:
   if cur in seen:errors.append(f'assertion: supersession cycle detected at {cur}');break
   seen.add(cur);row=assertions.get(cur);cur=row.get('supersedes') if row else None
def validate_reconciliation_integrity(index,registry,scope_keys,errors):
 decisions=index.get('reconciliation_decision',{});accepted=[d for d in decisions.values() if d.get('status')=='ACCEPTED']
 for did,d in decisions.items():
  validate_payload(f'reconciliation:{did}',d,registry,scope_keys,index,errors);predecessor=d.get('supersedes')
  if predecessor:
   if d.get('status')=='ACCEPTED' and (not isinstance(d.get('reason'),str) or not d.get('reason').strip()):errors.append(f'reconciliation: superseding accepted decision {did} requires non-empty reason')
   prior=decisions.get(predecessor)
   if prior and decision_active_key(prior)!=decision_active_key(d):errors.append(f'reconciliation: {did} supersedes predecessor with different active key {predecessor}')
 for start in decisions:
  seen=set();cur=start
  while cur:
   if cur in seen:errors.append(f'reconciliation: supersession cycle detected at {cur}');break
   seen.add(cur);row=decisions.get(cur);cur=row.get('supersedes') if row else None
 superseded={d.get('supersedes') for d in accepted if d.get('supersedes')};active=[d for d in accepted if d.get('decision_id') not in superseded];groups={}
 for d in active:
  key=decision_active_key(d)
  if key is not None:groups.setdefault(key,[]).append(d.get('decision_id'))
 for key,ids in sorted(groups.items(),key=lambda x:repr(x[0])):
  if len(ids)>1:errors.append(f'reconciliation: multiple active decisions for key {key}: {sorted(ids)}')
 dispositions={d.get('subject_id'):d for d in active if d.get('decision_type')=='ASSERTION_DISPOSITION' and d.get('subject_type')=='ASSERTION'}
 effective_statuses={aid:(d.get('payload') or {}).get('disposition') for aid,d in dispositions.items()}
 assertions=index.get('assertion',{});superseded_assertions=effectively_superseded_assertions(assertions,effective_statuses)
 successor_groups={}
 for aid,a in assertions.items():
  if a.get('supersedes') and effective_statuses.get(aid,a.get('status'))=='ACCEPTED':successor_groups.setdefault(a['supersedes'],[]).append(aid)
 for predecessor,successors in successor_groups.items():
  if len(successors)>1:errors.append(f'assertion: multiple accepted successors of {predecessor}: {sorted(successors)}')
 for d in active:
  if d.get('decision_type')!='ASSERTION_PROJECTION_STATUS' or d.get('subject_type')!='ASSERTION':continue
  aid=d.get('subject_id');a=index.get('assertion',{}).get(aid)
  if not a:continue
  effective=a.get('status');override=dispositions.get(aid)
  if override:effective=(override.get('payload') or {}).get('disposition')
  if aid in superseded_assertions:effective='SUPERSEDED'
  if effective!='ACCEPTED':errors.append(f"reconciliation:{d.get('decision_id')}: projection-status decision targets effectively {effective} assertion {aid}")
def main():
 seen={};index={rt:{} for rt in ID_FIELDS};errors=[];schemas=load_schemas();librarian_schemas=load_authoritative_librarian_schemas();registry,reg_errors=load_predicate_registry();scope_keys,scope_errors=load_scope_key_registry();errors.extend(reg_errors);errors.extend(scope_errors)
 try:records=list(iter_records())
 except ValueError as exc:records=[];errors.append(str(exc))
 for path,row in records:
  rt=row.get('record_type')
  if not rt:errors.append(f'{path}: missing record_type');continue
  if rt not in schemas:errors.append(f'{path}: unknown record_type {rt}');continue
  for err in schema_errors(row,schemas[rt]):errors.append(f'{path}: schema: {err}')
  if rt in librarian_schemas and is_authoritative_librarian_path(path):
   for err in schema_errors(row,librarian_schemas[rt]):errors.append(f'{path}: authoritative Librarian schema: {err}')
  id_field=ID_FIELDS.get(rt)
  if id_field:
   rid=row.get(id_field)
   if not rid:errors.append(f'{path}: {rt} missing {id_field}')
   elif (rt,rid) in seen:errors.append(f'duplicate {rt} id {rid}: {seen[(rt,rid)]} and {path}')
   else:seen[(rt,rid)]=path;index[rt][rid]=row
 validate_partition_ownership(records,errors);validate_references(records,index,errors);validate_source_work_lineage(index,errors);validate_binding_integrity(records,index,errors)
 for path,row in records:
  if row.get('record_type')=='assertion':validate_predicate_assertion(path,row,registry,index,errors)
 validate_assertion_lineage(index,errors);validate_batch_integrity(records,index,errors);validate_reconciliation_integrity(index,registry,scope_keys,errors)
 if errors:print('VALIDATION FAILED');print('\n'.join('- '+e for e in errors));return 1
 print(f'VALIDATION PASSED: {len(seen)} identified records');return 0
if __name__=='__main__':sys.exit(main())
