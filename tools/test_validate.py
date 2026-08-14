#!/usr/bin/env python3
from __future__ import annotations
import contextlib, importlib.util, io, json, tempfile, unittest
from pathlib import Path
MODULE_PATH=Path(__file__).with_name('validate.py'); spec=importlib.util.spec_from_file_location('trek_validate',MODULE_PATH); validate=importlib.util.module_from_spec(spec); spec.loader.exec_module(validate)
VALID='sha256:0fcdb523d4915ff92673fd3492b1f23876088f1b9e610d16959713a035f7afd2'; TOS='sha256:2a799c7ea7f595858bcd2cf50c6635118f08dc2cb53e2c919148577388bfdf0a'; MISSING='sha256:c0d39b7e8189ef573556da8eec328a1a7796e84f7866bf44edfeba2b602de216'; ILLEGAL='sha256:40ca469fdf56fab55a88717f6f5098199ecf3951ca9ed212dc3d34dde83019e0'
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
  wr=[{'record_type':'local_entity','local_entity_id':'local-1','work_id':'work-1','label':'Fixture Entity'},{'record_type':'evidence','evidence_id':'evidence-1','source_id':'source-1','work_id':'work-1','evidence_kind':'depiction','locator':{'line':1},'observed':{'event':'fixture'}},{'record_type':'assertion','assertion_id':'assertion-1','subject':'local-1','predicate':'CLAIMS','object':'x','evidence':['evidence-1'],'status':'ACCEPTED'}]
  b=r/'tng'/'batches'/'batch-1'; b.mkdir(parents=True)
  if illegal: rows=sw+wr; default={'sources':1,'works':1,'local_entities':1,'evidence':1,'assertions':1}
  else:
   reg=r/'_registry'; reg.mkdir(parents=True); (reg/'records.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in sw)); rows=wr; default={'local_entities':1,'evidence':1,'assertions':1}
  (b/'records.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows)); m={'record_type':'batch_manifest','batch_id':'batch-1','schema_version':'0.1.0','worker_id':worker,'works':['work-1'],'source_hashes':['sha256:source'],'record_counts':counts or default,'batch_hash':h}; (b/'manifest.json').write_text(json.dumps(m)+'\n')
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
   r=Path(td)/'research'; self.batch(r,ILLEGAL,illegal=True); rc,o=self.runroot(r); self.assertEqual(rc,1); self.assertIn('Librarian/Consolidator-owned',o)
if __name__=='__main__': unittest.main()
