#!/usr/bin/env python3
"""Build deterministic graph/search outputs without writing through mutable output paths.

POSIX output writes are anchored to a no-symlink directory descriptor. The
output directory and its parents must be under trusted local filesystem
administration: another actor able to rename directories or mount filesystems
can still invalidate a path while the build runs. On platforms without the
required directory-descriptor primitives, fail closed rather than risk writing
to the verified canonical projection.
"""
from __future__ import annotations
import argparse, contextlib, hashlib, importlib.util, json, os, secrets, stat
from pathlib import Path
_MODULE=Path(__file__).with_name('projection_bundle.py'); _SPEC=importlib.util.spec_from_file_location('trek_projection_bundle_graph',_MODULE); bundle=importlib.util.module_from_spec(_SPEC); _SPEC.loader.exec_module(bundle)
ASSERTION_PARTITIONS={'facts.jsonl':'facts','contested.jsonl':'contested','unresolved.jsonl':'unresolved'}; BUNDLE_VERSION='0.2.0'

def canonical(v):return bundle.canonical(v)
def sha256_bytes(data):return 'sha256:'+hashlib.sha256(data).hexdigest()
def merge_node(nodes,node_id,values):
 incoming={'node_id':node_id,**{k:v for k,v in values.items() if v is not None}}; existing=nodes.get(node_id)
 if existing is None:nodes[node_id]=incoming; return
 for key,value in incoming.items():
  if key=='node_id':continue
  if key not in existing or existing[key] is None:existing[key]=value
  elif value is not None and canonical(existing[key])!=canonical(value):raise ValueError(f'conflicting structural metadata for {node_id}.{key}')
def add_edge(edges,edge_id,edge_kind,source_node,target_node,**metadata):
 row={'edge_id':edge_id,'edge_kind':edge_kind,'source_node':source_node,'target_node':target_node,**{k:v for k,v in metadata.items() if v is not None}}; existing=edges.get(edge_id)
 if existing is not None and canonical(existing)!=canonical(row):raise ValueError(f'conflicting structural edge {edge_id}')
 edges[edge_id]=row
def string_values(v):
 if v is None:return []
 if isinstance(v,str):return [v]
 if isinstance(v,(int,float,bool)):return [str(v)]
 if isinstance(v,list):
  out=[]
  for x in v:out.extend(string_values(x))
  return out
 if isinstance(v,dict):
  out=[]
  for k in sorted(v):out.extend(string_values(v[k]))
  return out
 return []
def paths_overlap(first,second):
 return first==second or first in second.parents or second in first.parents

def require_safe_directory_writes():
 primitives=(os.open,os.mkdir,os.rename,os.unlink)
 if not hasattr(os,'O_NOFOLLOW') or not hasattr(os,'O_DIRECTORY') or any(op not in os.supports_dir_fd for op in primitives):
  raise OSError('graph-search output requires no-follow directory-relative writes on this platform')

def ensure_output_binding(output_fd,output_path,projection_root):
 try: current=output_path.stat(follow_symlinks=False)
 except OSError as exc:raise ValueError('graph-search output directory changed during build') from exc
 pinned=os.fstat(output_fd)
 if not stat.S_ISDIR(current.st_mode) or (current.st_dev,current.st_ino)!=(pinned.st_dev,pinned.st_ino):
  raise ValueError('graph-search output directory changed during build')
 if paths_overlap(output_path.resolve(),projection_root.resolve()):
  raise ValueError('graph-search output overlaps verified projection tree')

@contextlib.contextmanager
def pinned_output_directory(output_root,projection_root):
 """Pin a directory without following symlinks in any path component."""
 require_safe_directory_writes()
 output_path=Path(os.path.abspath(output_root)); flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW
 if paths_overlap(output_path.resolve(),projection_root.resolve()):
  raise ValueError('graph-search output overlaps verified projection tree')
 fd=os.open(output_path.anchor,flags)
 try:
  for part in output_path.parts[1:]:
   try:os.mkdir(part,dir_fd=fd)
   except FileExistsError:pass
   try:next_fd=os.open(part,flags,dir_fd=fd)
   except OSError as exc:raise ValueError('graph-search output path must not contain symlinks or non-directories') from exc
   os.close(fd); fd=next_fd
  ensure_output_binding(fd,output_path,projection_root)
  yield fd
  ensure_output_binding(fd,output_path,projection_root)
 finally:os.close(fd)

def trusted_output_binding(output_path,pinned_path,projection_root):
 """Best-effort consistency check; only valid with trusted, non-mutating parents."""
 path=output_path
 while path!=path.parent:
  if path.is_symlink() or (hasattr(path,'is_junction') and path.is_junction()):
   raise ValueError('graph-search trusted output path contains symlink or junction')
  path=path.parent
 if output_path.resolve()!=pinned_path or paths_overlap(pinned_path,projection_root.resolve()):
  raise ValueError('graph-search trusted output directory changed or overlaps verified projection')

@contextlib.contextmanager
def output_directory(output_root,projection_root,*,trusted_output_path=False):
 try:require_safe_directory_writes()
 except OSError:
  if not trusted_output_path:raise
  requested=Path(os.path.abspath(output_root)); target=requested.resolve()
  if paths_overlap(target,projection_root.resolve()):
   raise ValueError('graph-search output overlaps verified projection tree')
  trusted_output_binding(requested,target,projection_root)
  target.mkdir(parents=True,exist_ok=True)
  trusted_output_binding(requested,target,projection_root)
  yield target
  trusted_output_binding(requested,target,projection_root)
 else:
  with pinned_output_directory(output_root,projection_root) as fd:yield fd

def write_output_bytes(output_fd,name,payload):
 """Replace a destination entry atomically; never truncate an existing hardlink."""
 if isinstance(output_fd,Path):
  # Explicit opt-in compatibility path. It relies on trusted, stable ancestors.
  temp=output_fd/f'.{name}.{secrets.token_hex(12)}.tmp'
  file_fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  try:
   with os.fdopen(file_fd,'wb') as f:f.write(payload)
   os.replace(temp,output_fd/name)
  finally:temp.unlink(missing_ok=True)
  return
 temp=f'.{name}.{secrets.token_hex(12)}.tmp'; file_fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=output_fd)
 try:
  with os.fdopen(file_fd,'wb') as f:f.write(payload)
  os.rename(temp,name,src_dir_fd=output_fd,dst_dir_fd=output_fd)
 finally:
  try:os.unlink(temp,dir_fd=output_fd)
  except FileNotFoundError:pass

def write_jsonl(output_fd,name,rows,id_key):
 ordered=sorted(rows,key=lambda r:(str(r.get(id_key,'')),canonical(r))); payload=''.join(canonical(r)+'\n' for r in ordered).encode(); write_output_bytes(output_fd,name,payload); return {'hash':sha256_bytes(payload),'count':len(ordered)}
def ref_node_id(ref_type,ref_id,active_ids):
 return {'SOURCE':f'source:{ref_id}','WORK':f'work:{ref_id}','LOCAL_ENTITY':f'entity:{ref_id}','EVIDENCE':f'evidence:{ref_id}','ASSERTION':f'assertion:{ref_id}' if ref_id in active_ids else f'assertion_history:{ref_id}','RECONCILIATION_DECISION':f'reconciliation:{ref_id}'}.get(ref_type,f'reference:{ref_type}:{ref_id}')
def ensure_ref_node(nodes,ref_type,ref_id,active_ids):
 node_id=ref_node_id(ref_type,ref_id,active_ids); kind={'SOURCE':'source','WORK':'work','LOCAL_ENTITY':'local_entity','EVIDENCE':'evidence','ASSERTION':'assertion' if ref_id in active_ids else 'assertion_history','RECONCILIATION_DECISION':'reconciliation_decision'}.get(ref_type,'reference'); merge_node(nodes,node_id,{'node_kind':kind,'ref_type':ref_type,'ref_id':ref_id}); return node_id
def add_catalog(catalog,key,row,label):
 if not isinstance(row,dict):return
 rid=row.get(key)
 if not rid:return
 if rid in catalog and canonical(catalog[rid])!=canonical(row):raise ValueError(f'conflicting {label} metadata for {rid}')
 catalog[rid]=row

def build_bundle(projection_root,output_root,*,trusted_output_path=False):
 projection_root=Path(projection_root); output_root=Path(output_root)
 source_path=projection_root.resolve(); target_path=output_root.resolve()
 if paths_overlap(source_path,target_path):
  raise ValueError('graph-search output overlaps verified projection tree')
 verified=bundle.verify_projection(projection_root); rows=verified['rows']; manifest=verified['manifest']; nodes={}; edges={}; search={}; active_ids=set()
 for entity in rows['entities.jsonl']:
  eid=entity['local_entity_id']; node=f'entity:{eid}'; merge_node(nodes,node,{'node_kind':'local_entity','local_entity_id':eid,'work_id':entity.get('work_id'),'label':entity.get('label'),'record':entity})
  if entity.get('work_id'):
   work=f"work:{entity['work_id']}"; merge_node(nodes,work,{'node_kind':'work','work_id':entity['work_id']}); add_edge(edges,f'{node}::work::{entity["work_id"]}','ENTITY_WORK',node,work)
 for filename,partition in ASSERTION_PARTITIONS.items():
  for assertion in rows[filename]:
   aid=assertion['assertion_id']; active_ids.add(aid); node=f'assertion:{aid}'; merge_node(nodes,node,{'node_kind':'assertion','assertion_id':aid,'projection_status':assertion.get('projection_status'),'partition':partition,'predicate':assertion.get('predicate'),'record':assertion})
 for assertion in rows['assertion_history.jsonl']:
  aid=assertion['assertion_id']; node=f'assertion_history:{aid}'; merge_node(nodes,node,{'node_kind':'assertion_history','assertion_id':aid,'status':assertion.get('status'),'record':assertion})
  if assertion.get('supersedes'):
   target=f'assertion_history:{assertion["supersedes"]}'; merge_node(nodes,target,{'node_kind':'assertion_history','assertion_id':assertion['supersedes']}); add_edge(edges,f'{node}::supersedes::{assertion["supersedes"]}','ASSERTION_SUPERSEDES',node,target)
 for filename in ASSERTION_PARTITIONS:
  for assertion in rows[filename]:
   aid=assertion['assertion_id']; subject_type=assertion.get('subject_type'); subject_id=assertion.get('subject')
   if subject_type and subject_id:
    target=ensure_ref_node(nodes,subject_type,subject_id,active_ids); add_edge(edges,f'assertion:{aid}::subject::{subject_type}:{subject_id}','ASSERTION_SUBJECT',f'assertion:{aid}',target,subject_type=subject_type)
 sources={}; works={}; evidence_records={}
 for prov in rows['provenance.jsonl']:
  aid=prov['assertion_id']; source_assertion=f'assertion:{aid}' if aid in active_ids else f'assertion_history:{aid}'; merge_node(nodes,source_assertion,{'node_kind':'assertion' if aid in active_ids else 'assertion_history','assertion_id':aid})
  ev=prov.get('evidence_record') or {}; evid=prov['evidence_id']; evnode=f'evidence:{evid}'; merge_node(nodes,evnode,{'node_kind':'evidence','evidence_id':evid,'record':ev}); add_edge(edges,f'{source_assertion}::evidence::{evid}','ASSERTION_EVIDENCE',source_assertion,evnode)
  add_catalog(evidence_records,'evidence_id',ev,'evidence'); src=prov.get('source_record') or {}; work=prov.get('work_record') or {}; add_catalog(sources,'source_id',src,'source'); add_catalog(works,'work_id',work,'work')
  for item in prov.get('source_lineage_records',[]):add_catalog(sources,'source_id',item,'source')
  for item in prov.get('work_lineage_records',[]):add_catalog(works,'work_id',item,'work')
  if src.get('source_id'):
   sn=f"source:{src['source_id']}"; merge_node(nodes,sn,{'node_kind':'source','source_id':src['source_id'],'record':src}); add_edge(edges,f'{evnode}::source::{src["source_id"]}','EVIDENCE_SOURCE',evnode,sn)
  if work.get('work_id'):
   wn=f"work:{work['work_id']}"; merge_node(nodes,wn,{'node_kind':'work','work_id':work['work_id'],'record':work}); add_edge(edges,f'{evnode}::work::{work["work_id"]}','EVIDENCE_WORK',evnode,wn)
  observer=ev.get('observer_local_entity_id')
  if observer:
   on=f'entity:{observer}'; merge_node(nodes,on,{'node_kind':'local_entity','local_entity_id':observer}); add_edge(edges,f'{evnode}::observer::{observer}','EVIDENCE_OBSERVER',evnode,on)
 for sid,src in sorted(sources.items()):
  sn=f'source:{sid}'; merge_node(nodes,sn,{'node_kind':'source','source_id':sid,'record':src})
  for parent in sorted(src.get('derived_from',[])):
   pn=f'source:{parent}'; merge_node(nodes,pn,{'node_kind':'source','source_id':parent}); add_edge(edges,f'{sn}::derived_from::{parent}','SOURCE_DERIVED_FROM',sn,pn)
 for wid,work in sorted(works.items()):
  wn=f'work:{wid}'; merge_node(nodes,wn,{'node_kind':'work','work_id':wid,'record':work}); parent=work.get('parent_work_id')
  if parent:
   pn=f'work:{parent}'; merge_node(nodes,pn,{'node_kind':'work','work_id':parent}); add_edge(edges,f'{wn}::parent::{parent}','WORK_PARENT',wn,pn)
 for decision in rows['reconciliation_history.jsonl']:
  did=decision['decision_id']; dn=f'reconciliation:{did}'; merge_node(nodes,dn,{'node_kind':'reconciliation_decision','decision_id':did,'decision_type':decision.get('decision_type'),'status':decision.get('status'),'record':decision}); st=decision.get('subject_type'); sid=decision.get('subject_id')
  if st and sid:
   target=ensure_ref_node(nodes,st,sid,active_ids); add_edge(edges,f'{dn}::subject::{st}:{sid}','RECONCILIATION_SUBJECT',dn,target,subject_type=st)
  if decision.get('supersedes'):
   target=f'reconciliation:{decision["supersedes"]}'; merge_node(nodes,target,{'node_kind':'reconciliation_decision','decision_id':decision['supersedes']}); add_edge(edges,f'{dn}::supersedes::{decision["supersedes"]}','RECONCILIATION_SUPERSEDES',dn,target)
 for relation in rows['relations.jsonl']:
  source=ensure_ref_node(nodes,relation['subject_type'],relation['subject_id'],active_ids); target=ensure_ref_node(nodes,relation['target_type'],relation['target_id'],active_ids); add_edge(edges,f"relation:{relation['relation_id']}",'GOVERNED_RELATION',source,target,relation_id=relation['relation_id'],relation_kind=relation.get('relation_kind'),predicate=relation.get('predicate'),projection_status=relation.get('projection_status'),record=relation); search[f"relation:{relation['relation_id']}"]={'document_id':f"relation:{relation['relation_id']}",'document_kind':'relation','text':' '.join(string_values(relation)),'record':relation}
 for node_id,node in sorted(nodes.items()):search[node_id]={'document_id':node_id,'document_kind':node.get('node_kind'),'projection_status':node.get('projection_status'),'partition':node.get('partition'),'text':' '.join(string_values(node)),'record':node}
 with output_directory(output_root,projection_root,trusted_output_path=trusted_output_path) as output_fd:
  outputs={'graph_nodes.jsonl':write_jsonl(output_fd,'graph_nodes.jsonl',nodes.values(),'node_id'),'graph_edges.jsonl':write_jsonl(output_fd,'graph_edges.jsonl',edges.values(),'edge_id'),'search_documents.jsonl':write_jsonl(output_fd,'search_documents.jsonl',search.values(),'document_id')}
  result={'record_type':'graph_search_projection_bundle','bundle_version':BUNDLE_VERSION,'projection_hash':manifest['projection_hash'],'builder_identity':bundle.tool_identity(Path(__file__),_MODULE),'verification_receipt_hash':verified['receipt_hash'],'verification_receipt':verified['receipt'],'imported_output_contract':list(bundle.REQUIRED_OUTPUTS),'relation_mapping_contract':'projection-relation.schema.json@0.2.0','outputs':outputs}
  write_output_bytes(output_fd,'manifest.json',(json.dumps(result,indent=2,sort_keys=True)+'\n').encode())
 return result

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('projection'); ap.add_argument('output'); ap.add_argument('--trusted-output-path',action='store_true',help='opt in to path-based output only where no-follow dirfd writes are unavailable; requires trusted, non-mutating filesystem paths'); args=ap.parse_args(); print(build_bundle(Path(args.projection),Path(args.output),trusted_output_path=args.trusted_output_path)['projection_hash'])
if __name__=='__main__':main()
