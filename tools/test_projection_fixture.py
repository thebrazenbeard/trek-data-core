#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path
MODULE_PATH=Path(__file__).with_name('projection_bundle.py'); spec=importlib.util.spec_from_file_location('trek_projection_bundle_fixture',MODULE_PATH); bundle=importlib.util.module_from_spec(spec); spec.loader.exec_module(bundle)

def make_projection(root, stable_value='stable', include_relation=True, inactive_history=True):
 root=Path(root); root.mkdir(parents=True,exist_ok=True)
 stable={'record_type':'assertion','assertion_id':'a-stable','subject_type':'LOCAL_ENTITY','subject':'local-1','predicate':'CLAIMS','object':{'value':stable_value},'evidence':['e1'],'status':'ACCEPTED','effective_assertion_status':'ACCEPTED','projection_status':'STABLE','scope':{}}
 paradox={'record_type':'assertion','assertion_id':'a-paradox','subject_type':'LOCAL_ENTITY','subject':'local-1','predicate':'CLAIMS','object':{'value':'paradox'},'evidence':['e1'],'status':'ACCEPTED','effective_assertion_status':'ACCEPTED','projection_status':'STRUCTURAL_PARADOX'}
 unresolved={'record_type':'assertion','assertion_id':'a-unresolved','subject_type':'LOCAL_ENTITY','subject':'local-1','predicate':'CLAIMS','object':{'value':'unknown'},'evidence':['e1'],'status':'ACCEPTED','effective_assertion_status':'ACCEPTED','projection_status':'UNRESOLVED','projection_reason':'MISSING_PROJECTION_STATUS'}
 history=[{k:v for k,v in stable.items() if k not in {'effective_assertion_status','projection_status'}},{k:v for k,v in paradox.items() if k not in {'effective_assertion_status','projection_status'}},{k:v for k,v in unresolved.items() if k not in {'effective_assertion_status','projection_status','projection_reason'}}]
 if inactive_history: history.append({'record_type':'assertion','assertion_id':'a-rejected','subject_type':'LOCAL_ENTITY','subject':'local-1','predicate':'CLAIMS','object':{'value':'rejected'},'evidence':['e1'],'status':'REJECTED'})
 source={'record_type':'source','source_id':'source-1','source_kind':'transcript','locator':'fixture://source','content_hash':'sha256:source','source_variant':'v1','provenance_family':'fam','derived_from':[]}
 work={'record_type':'work','work_id':'work-1','title':'Fixture Work','medium':'test'}
 evidence={'record_type':'evidence','evidence_id':'e1','source_id':'source-1','work_id':'work-1','evidence_kind':'depiction','locator':{'line':1},'observed':{'text':"It's a fixture\\path\nnext"},'frame':'PRIMARY','epistemic_status':'DIRECT'}
 provenance=[]
 for row in history:
  provenance.append({'record_type':'projection_provenance','provenance_id':row['assertion_id']+'::e1','assertion_id':row['assertion_id'],'evidence_id':'e1','assertion_record':row,'effective_assertion_status':row['status'],'support_set':['e1'],'evidence_record':evidence,'source_record':source,'source_lineage_records':[],'work_record':work,'work_lineage_records':[],'subject_record':{'record_type':'local_entity','local_entity_id':'local-1','work_id':'work-1','label':'Fixture'}})
 relations=[{'record_type':'projection_relation','relation_id':'assertion:a-stable','relation_kind':'ASSERTION_PREDICATE','assertion_id':'a-stable','subject_type':'LOCAL_ENTITY','subject_id':'local-1','predicate':'CLAIMS','target_type':'WORK','target_id':'work-1','projection_status':'STABLE'}] if include_relation else []
 recon=[{'record_type':'reconciliation_decision','decision_id':'status-1','decision_type':'ASSERTION_PROJECTION_STATUS','subject_type':'ASSERTION','subject_id':'a-stable','payload':{'projection_status':'STABLE'},'status':'ACCEPTED','evidence':['e1'],'method':'fixture'}]
 rows={'entities.jsonl':[{'record_type':'local_entity','local_entity_id':'local-1','work_id':'work-1','label':'Fixture'}],'facts.jsonl':[stable],'relations.jsonl':relations,'contested.jsonl':[paradox],'unresolved.jsonl':[unresolved],'provenance.jsonl':provenance,'assertion_history.jsonl':history,'reconciliation_history.jsonl':recon}
 outputs={}
 for name,data in rows.items():
  key=bundle.ID_KEYS[name]; ordered=sorted(data,key=lambda r:(str(r.get(key,'')),bundle.canonical(r))); payload=''.join(bundle.canonical(r)+'\n' for r in ordered).encode('utf-8'); (root/name).write_bytes(payload); outputs[name]={'role':name.removesuffix('.jsonl'),'hash':bundle.sha256_bytes(payload),'count':len(ordered)}
 manifest={'record_type':'projection_manifest','projection_version':'0.2.0','schema_version':'0.2.0','methodology_version':'0.1.0','compiler_commit':'fixture','research_head':'research-fixture','reconciliation_head':'recon-fixture','predicate_registry_hash':'sha256:'+'1'*64,'scope_key_registry_hash':'sha256:'+'2'*64,'input_hash':'sha256:'+'3'*64,'projection_hash':bundle.compute_projection_hash(outputs),'outputs':outputs}
 (root/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8'); return manifest
