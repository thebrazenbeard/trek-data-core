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
    def test_schema_rejects_invalid_nested_source_scope(self):
        b=copy.deepcopy(self.b); b[0]["source_scope"]="INVALID"
        self.assertTrue(any("source_scope: expected type object" in e for e in self.validate(b=b)))
    def test_schema_rejects_invalid_nested_scope_enum_and_type(self):
        b=copy.deepcopy(self.b); b[0]["source_scope"]={"scope_type":"IMPOSSIBLE","locator":42}
        self.assertTrue(any("source_scope.scope_type: invalid enum" in e for e in self.validate(b=b)))
        self.assertTrue(any("source_scope.locator: expected type" in e for e in self.validate(b=b)))
    def test_schema_rejects_unexpected_fields_and_bad_fixture_type(self):
        s=copy.deepcopy(self.s); s[0]["unapproved_identity"]="silent extension"; s[0]["fixture_only"]="yes"
        errors=self.validate(s=s)
        self.assertTrue(any("unexpected field unapproved_identity" in e for e in errors))
        self.assertTrue(any("fixture_only: expected type boolean" in e for e in errors))
    def test_schema_rejects_non_object_record(self):
        s=copy.deepcopy(self.s); s[0]="invalid"
        self.assertTrue(any("record must be an object" in e for e in self.validate(s=s)))
    def test_work_parent_cycle(self):
        w=copy.deepcopy(self.w); w[0]["parent_work_id"]=w[1]["work_id"]; w[1]["parent_work_id"]=w[0]["work_id"]
        self.assertTrue(any("work parent cycle" in e for e in self.validate(w=w)))
    def test_accepted_nonfixture_binding_requires_accepted_source_and_work(self):
        s=copy.deepcopy(self.s); w=copy.deepcopy(self.w); b=copy.deepcopy(self.b)
        b[0]["fixture_only"]=False
        next(x for x in s if x["source_id"]==b[0]["source_id"])["fixture_only"]=False
        next(x for x in w if x["work_id"]==b[0]["work_id"])["fixture_only"]=False
        self.assertTrue(any("requires ACCEPTED Source and Work" in e for e in self.validate(s=s,w=w,b=b)))
        next(x for x in s if x["source_id"]==b[0]["source_id"])["status"]="ACCEPTED"
        next(x for x in w if x["work_id"]==b[0]["work_id"])["status"]="ACCEPTED"
        self.assertEqual(self.validate(s=s,w=w,b=b),[])
    def test_fixture_cannot_bind_nonfixture_identity(self):
        b=copy.deepcopy(self.b); b[0]["fixture_only"]=False
        self.assertTrue(any("fixture/authoritative identity boundary" in e for e in self.validate(b=b)))
    def test_accepted_successor_requires_superseded_predecessor(self):
        b=copy.deepcopy(self.b); b[1]["supersedes_binding_id"]=b[0]["binding_id"]
        self.assertTrue(any("requires SUPERSEDED predecessor" in e for e in self.validate(b=b)))
    def test_bounded_scopes_require_locators(self):
        b=copy.deepcopy(self.b); b[2]["source_scope"]["locator"]=None; b[2]["work_scope"]["component_label"]=None
        errors=self.validate(b=b)
        self.assertTrue(any("bounded source scope requires locator" in e for e in errors))
        self.assertTrue(any("component work scope requires component_label" in e for e in errors))
if __name__=="__main__": unittest.main(verbosity=2)
