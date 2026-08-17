#!/usr/bin/env python3
from __future__ import annotations
import contextlib, importlib.util, io, json, tempfile, unittest
from pathlib import Path
MODULE_PATH=Path(__file__).with_name('validate.py'); spec=importlib.util.spec_from_file_location('trek_validate',MODULE_PATH); validate=importlib.util.module_from_spec(spec); spec.loader.exec_module(validate)
VALID='sha256:f26f493dfaf444d51f20ecfbee2190835f80b7c1f27fcc521a49fd8764a316c9'; TOS='sha256:93bae5e8d35fcf9183305b52c36691a7a4deab831a6705b3b210bed7f966a4ca'; MISSING='sha256:98ff16565611f4ec8188f7fc49a5c3d87cbb5cd945ce6a35e27984bd6b60a7e0'; ILLEGAL='sha256:82dc29a5826f9e95716ce9e24743a4f1d801f793740842680b113ff3622719b2'
class ValidationTests(unittest.TestCase):
 def runroot(self,r):
  old=validate.DATA_ROOTS; validate.DATA_ROOTS=[r]
  try:
   out=io.StringIO()
   with contextlib.redirect_stdout(out): rc=validate.main()
  finally: validate.DATA_ROOTS=old
  return rc,out.getvalue()
 def batch(self,r,h,worker='TNG',counts=None,illegal=False):
  sw=[{'record_type':'source','source_id':'source-1','source_kind':'transcript','locator':'fixture://source-1','content_hash':'sha256:source'},{'record_type':'work','work_id':'work-1','title':'Fixture Work','medium':'test'}]
  wr=[{'record_type':'local_entity','local_entity_id':'local-1','work_id':'work-1','label':'Fixture Entity'},{'record_type':'evidence','evidence_id':'evidence-1','source_id':'source-1','work_id':'work-1','evidence_kind':'depiction','locator':{'line':1},'observed':{'event':'fixture'}},{'record_type':'assertion','assertion_id':'assertion-1','subject_type':'LOCAL_ENTITY','subject':'local-1','predicate':'CLAIMS','object':'x','evidence':['evidence-1'],'status':'ACCEPTED'}]
  b=r/'tng'/'batches'/'batch-1'; b.mkdir(parents=True)
  if illegal: rows=sw+wr; default={'sources':1,'works':1,'local_entities':1,'evidence':1,'assertions':1}
  else:
   reg=r/'_registry'; reg.mkdir(parents=True); (reg/'records.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in sw)); rows=wr; default={'local_entities':1,'evidence':1,'assertions':1}
  (b/'records.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows)); m={'record_type':'batch_manifest','batch_id':'batch-1','schema_version':'0.1.0','worker_id':worker,'works':['work-1'],'source_hashes':['sha256:source'],'record_counts':counts if counts is not None else default,'batch_hash':h}; (b/'manifest.json').write_text(json.dumps(m)+'\n')
 def test_schema_required(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td)/'research'; r.mkdir(); (r/'x.jsonl').write_text(json.dumps({'record_type':'source','source_id':'s','source_kind':'transcript'})+'\n'); rc,o=self.runroot(r); self.assertEqual(rc,1); self.assertIn('locator',o)
 def test_batch_hash_and_valid(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td)/'research'; self.batch(r,'sha256:wrong'); self.assertEqual(self.runroot(r)[0],1)
  with tempfile.TemporaryDirectory() as td:
   r=Path(td)/'research'; self.batch(r,VALID); self.assertEqual(self.runroot(r)[0],0)
 def test_worker_partition(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td)/'research'; self.batch(r,TOS,worker='TOS'); rc,o=self.runroot(r); self.assertEqual(rc,1); self.assertIn('worker_id',o)
 def test_required_counts(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td)/'research'; self.batch(r,MISSING,counts={'local_entities':1,'evidence':1}); rc,o=self.runroot(r); self.assertEqual(rc,1); self.assertIn('record_counts.assertions',o)
 def test_worker_cannot_own_source_work(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td)/'research'; self.batch(r,ILLEGAL,illegal=True); rc,o=self.runroot(r); self.assertEqual(rc,1); self.assertIn('authoritative source record',o); self.assertIn('authoritative work record',o)
if __name__=='__main__': unittest.main()
