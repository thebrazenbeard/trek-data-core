#!/usr/bin/env python3
import copy, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from validate_librarian_registry import load_fixture_file, validate_registry, source_bound_pairs
FIX=Path(__file__).parents[1]/"registry"/"librarian_registry_fixtures.json"
class RegistryTests(unittest.TestCase):
    def setUp(self): self.s,self.w,self.b,self.c,self.rp,self.passes=load_fixture_file(FIX)
    def validate(self,s=None,w=None,b=None,c=None,rp=None): return validate_registry(self.s if s is None else s,self.w if w is None else w,self.b if b is None else b,self.c if c is None else c,self.rp if rp is None else rp)
    def test_positive_fixture(self): self.assertEqual(self.validate(),[])
    def test_one_source_to_many_works_allowed(self):
        pairs=source_bound_pairs(self.b); self.assertIn(("FIXSRC-PRO-SPRINGFIELD-COMBINED","FIXWORK-PRO-LOST-FOUND-P1"),pairs); self.assertIn(("FIXSRC-PRO-SPRINGFIELD-COMBINED","FIXWORK-PRO-LOST-FOUND-P2"),pairs)
    def test_many_sources_to_one_work_allowed(self):
        pairs=source_bound_pairs(self.b); self.assertIn(("FIXSRC-PRO-SPRINGFIELD-COMBINED","FIXWORK-PRO-LOST-FOUND-P1"),pairs); self.assertIn(("FIXSRC-PRO-TVSUB-P1","FIXWORK-PRO-LOST-FOUND-P1"),pairs)
    def test_proposed_does_not_source_bound(self): self.assertNotIn(("FIXSRC-SFA-SPRINGFIELD-S01E10","FIXWORK-SFA-RUBINCON"),source_bound_pairs(self.b))
    def test_dangling_source(self):
        b=copy.deepcopy(self.b); b[0]["source_id"]="MISSING"; self.assertTrue(any("dangling source_id" in e for e in self.validate(b=b)))
    def test_dangling_work(self):
        b=copy.deepcopy(self.b); b[0]["work_id"]="MISSING"; self.assertTrue(any("dangling work_id" in e for e in self.validate(b=b)))
    def test_accepted_metadata_only(self):
        b=copy.deepcopy(self.b); b[0]["mapping_role"]="METADATA_ONLY"; self.assertTrue(any("must be EVIDENCE_BEARING" in e for e in self.validate(b=b)))
    def test_accepted_without_content_basis(self):
        b=copy.deepcopy(self.b); b[0]["basis"]=[{"kind":"EXTERNAL_METADATA","value":"title match"}]; self.assertTrue(any("lacks evidence-bearing" in e for e in self.validate(b=b)))
    def test_dangling_supersession(self):
        b=copy.deepcopy(self.b); b[0]["supersedes_binding_id"]="MISSING"; self.assertTrue(any("dangling supersedes" in e for e in self.validate(b=b)))
    def test_supersession_cycle(self):
        b=copy.deepcopy(self.b); b[0]["supersedes_binding_id"]=b[1]["binding_id"]; b[1]["supersedes_binding_id"]=b[0]["binding_id"]; self.assertTrue(any("supersession cycle" in e for e in self.validate(b=b)))
    def test_derivative_pseudo_independence(self):
        s=copy.deepcopy(self.s); child=copy.deepcopy(s[0]); child["source_id"]="FIXSRC-DERIVED"; child["derived_from"]=[s[0]["source_id"]]; child["independence_group"]="FAKE_NEW_WITNESS"; s.append(child); self.assertTrue(any("different independence_group" in e for e in self.validate(s=s)))
    def test_source_derivation_cycle(self):
        s=copy.deepcopy(self.s); s[0]["derived_from"]=[s[1]["source_id"]]; s[1]["derived_from"]=[s[0]["source_id"]]; s[1]["independence_group"]=s[0]["independence_group"]; self.assertTrue(any("source derivation cycle" in e for e in self.validate(s=s)))
    def test_conflicting_exclusive_binding(self):
        b=copy.deepcopy(self.b); x=copy.deepcopy(b[0]); x["binding_id"]="FIXBIND-CONFLICT"; x["work_id"]="FIXWORK-DS9-PAST-PROLOGUE"; b.append(x); self.assertTrue(any("conflicting ACCEPTED" in e for e in self.validate(b=b)))
    def test_crosswalk_dangling_target(self):
        c=copy.deepcopy(self.c); c[0]["target_id"]="MISSING"; self.assertTrue(any("dangling WORK target" in e for e in self.validate(c=c)))
    def test_research_partition_ownership(self):
        rp=list(self.rp)+[(Path("research/tng/bad.jsonl"),self.s[0])]; self.assertTrue(any("under research partition" in e for e in self.validate(rp=rp)))
    def test_analysis_passes_do_not_mint_sources(self): self.assertEqual(len({p["source_id"] for p in self.passes}),1); self.assertEqual(len([x for x in self.s if x["source_id"]==self.passes[0]["source_id"]]),1)
if __name__=="__main__": unittest.main(verbosity=2)
