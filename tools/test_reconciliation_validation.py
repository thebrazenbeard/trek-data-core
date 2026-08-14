#!/usr/bin/env python3
from __future__ import annotations
import contextlib, importlib.util, io, json, tempfile, unittest
from pathlib import Path
MODULE_PATH=Path(__file__).with_name('validate.py'); spec=importlib.util.spec_from_file_location('trek_validate_recon',MODULE_PATH); validate=importlib.util.module_from_spec(spec); spec.loader.exec_module(validate)
def base(): return [{'record_type':'source','source_id':'source-1','source_kind':'transcript','locator':'fixture://source-1'},{'record_type':'work','work_id':'work-1','title':'Fixture Work','medium':'test'},{'record_type':'evidence','evidence_id':'evidence-1','source_id':'source-1','work_id':'work-1','evidence_kind':'depiction','locator':{'line':1},'observed':{'event':'fixture'}}]
def link(i,v,sub='local-1',sup=None,reason=None):
 r={'record_type':'reconciliation_decision','decision_id':i,'decision_type':'ENTITY_LINK','subject_id':sub,'value':v,'status':'ACCEPTED','evidence':['evidence-1'],'method':'fixture'}
 if sup:r['supersedes']=sup
 if reason:r['reason']=reason
 return r
class ReconTests(unittest.TestCase):
 def run(self,rows):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'reconciliation'; root.mkdir(); (root/'records.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows)); old=validate.DATA_ROOTS; validate.DATA_ROOTS=[root]
   try:
    out=io.StringIO()
    with contextlib.redirect_stdout(out): rc=validate.main()
   finally: validate.DATA_ROOTS=old
   return rc,out.getvalue()
 def test_conflict(self):
  rc,o=self.run(base()+[link('l1','g1'),link('l2','g2')]); self.assertEqual(rc,1); self.assertIn('multiple active',o)
 def test_supersession_reason_and_valid(self):
  rc,o=self.run(base()+[link('l1','g1'),link('l2','g2',sup='l1')]); self.assertEqual(rc,1); self.assertIn('reason',o)
  rc,o=self.run(base()+[link('l1','g1'),link('l2','g2',sup='l1',reason='correction')]); self.assertEqual(rc,0,o)
 def test_cross_subject_and_cycle(self):
  rc,o=self.run(base()+[link('l1','g1','a'),link('l2','g2','b',sup='l1',reason='bad')]); self.assertEqual(rc,1); self.assertIn('different subject_id',o)
  rc,o=self.run(base()+[link('l1','g1',sup='l2',reason='a'),link('l2','g2',sup='l1',reason='b')]); self.assertEqual(rc,1); self.assertIn('cycle',o)
if __name__=='__main__': unittest.main()
