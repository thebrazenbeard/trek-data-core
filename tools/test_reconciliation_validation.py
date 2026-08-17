#!/usr/bin/env python3
from __future__ import annotations
import contextlib, importlib.util, io, json, tempfile, unittest
from pathlib import Path
MODULE_PATH=Path(__file__).with_name('validate.py'); spec=importlib.util.spec_from_file_location('trek_validate_recon',MODULE_PATH); validate=importlib.util.module_from_spec(spec); spec.loader.exec_module(validate)

def base():
 return [
  {'record_type':'source','source_id':'source-1','source_kind':'transcript','locator':'fixture://source-1'},
  {'record_type':'work','work_id':'work-1','title':'Fixture Work','medium':'test'},
  {'record_type':'local_entity','local_entity_id':'local-1','work_id':'work-1','label':'Fixture'},
  {'record_type':'evidence','evidence_id':'evidence-1','source_id':'source-1','work_id':'work-1','evidence_kind':'depiction','locator':{'line':1},'observed':{'event':'fixture'}},
  {'record_type':'assertion','assertion_id':'assertion-1','subject_type':'LOCAL_ENTITY','subject':'local-1','predicate':'CLAIMS','object':'fixture','evidence':['evidence-1'],'status':'ACCEPTED'},
 ]

def disposition(i,value='ACCEPTED',subject='assertion-1',sup=None,reason=None):
 r={'record_type':'reconciliation_decision','decision_id':i,'decision_type':'ASSERTION_DISPOSITION','subject_type':'ASSERTION','subject_id':subject,'payload':{'disposition':value},'status':'ACCEPTED','evidence':['evidence-1'],'method':'fixture'}
 if sup:r['supersedes']=sup
 if reason:r['reason']=reason
 return r

class ReconTests(unittest.TestCase):
 def run_records(self,rows):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'reconciliation'; root.mkdir(); (root/'records.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows)); old=validate.DATA_ROOTS; validate.DATA_ROOTS=[root]
   try:
    out=io.StringIO()
    with contextlib.redirect_stdout(out): rc=validate.main()
   finally: validate.DATA_ROOTS=old
   return rc,out.getvalue()
 def test_conflicting_active_disposition_decisions_are_rejected(self):
  rc,o=self.run_records(base()+[disposition('d1','ACCEPTED'),disposition('d2','REJECTED')]); self.assertEqual(rc,1); self.assertIn('multiple active',o)
 def test_supersession_requires_reason_and_valid_successor_passes(self):
  rc,o=self.run_records(base()+[disposition('d1','ACCEPTED'),disposition('d2','REJECTED',sup='d1')]); self.assertEqual(rc,1); self.assertIn('reason',o)
  rc,o=self.run_records(base()+[disposition('d1','ACCEPTED'),disposition('d2','REJECTED',sup='d1',reason='correction')]); self.assertEqual(rc,0,o)
 def test_cross_subject_supersession_is_rejected(self):
  rows=base()+[{'record_type':'assertion','assertion_id':'assertion-2','subject_type':'LOCAL_ENTITY','subject':'local-1','predicate':'CLAIMS','object':'fixture-2','evidence':['evidence-1'],'status':'ACCEPTED'}]
  rc,o=self.run_records(rows+[disposition('d1','ACCEPTED','assertion-1'),disposition('d2','REJECTED','assertion-2',sup='d1',reason='bad')]); self.assertEqual(rc,1); self.assertIn('different active key',o)
 def test_supersession_cycle_is_rejected(self):
  rc,o=self.run_records(base()+[disposition('d1','ACCEPTED',sup='d2',reason='a'),disposition('d2','REJECTED',sup='d1',reason='b')]); self.assertEqual(rc,1); self.assertIn('cycle',o)
if __name__=='__main__': unittest.main()
