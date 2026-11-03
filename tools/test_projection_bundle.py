#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path

def load(name,alias):
 p=Path(__file__).with_name(name); s=importlib.util.spec_from_file_location(alias,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
bundle=load('projection_bundle.py','trek_projection_bundle_test'); fixture=load('test_projection_fixture.py','trek_projection_fixture_bundle')
compiler=load('build_projection.py','trek_projection_compiler_bundle')
producer_fixture=load('test_build_projection.py','trek_projection_producer_fixture_bundle')

def rewrite_bundle(root,filename,transform):
 path=root/filename; rows=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]
 rows=transform(rows)
 payload=''.join(bundle.canonical(row)+'\n' for row in sorted(rows,key=lambda row:(row[bundle.ID_KEYS[filename]],bundle.canonical(row)))).encode('utf-8')
 path.write_bytes(payload)
 manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
 manifest['outputs'][filename]['hash']=bundle.sha256_bytes(payload)
 manifest['outputs'][filename]['count']=len(rows)
 manifest['projection_hash']=bundle.compute_projection_hash(manifest['outputs'])
 all_rows={name:[json.loads(line) for line in (root/name).read_text(encoding='utf-8').splitlines() if line]
           for name in bundle.REQUIRED_OUTPUTS}
 manifest['input_hash']=bundle.compute_input_hash(manifest,all_rows)
 (root/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')

class ProjectionBundleTests(unittest.TestCase):
 def test_valid_bundle_returns_verified_receipt(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); manifest=fixture.make_projection(root); verified=bundle.verify_projection(root); self.assertEqual(verified['manifest']['projection_hash'],manifest['projection_hash']); self.assertEqual(set(verified['rows']),set(bundle.REQUIRED_OUTPUTS)); self.assertTrue(verified['receipt_hash'].startswith('sha256:'))
 def test_unpinned_upstream_identity_remains_an_unverified_declaration(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   checked=bundle.verify_projection(root)
   self.assertEqual(checked['receipt']['upstream_identity_status']['research_head'],'UNVERIFIED_DECLARATION')
   self.assertEqual(checked['receipt']['upstream_identity_status']['input_hash'],'UNVERIFIED_DECLARATION')
 def test_forged_research_head_is_not_authenticated_by_matching_bundle_bytes(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); original=fixture.make_projection(root)
   manifest_path=root/'manifest.json'; changed=json.loads(manifest_path.read_text(encoding='utf-8'))
   changed['research_head']='FAKE_GIT_HEAD_UNVERIFIED'
   # v0.3 derives input_hash from the declared identities and full catalogs.
   # A bundle author can recompute that self-issued digest; this is not an
   # independent accepted-Git-head attestation.
   rows={name:bundle.parse_jsonl(root/name,bundle.ID_KEYS[name])[0] for name in bundle.REQUIRED_OUTPUTS}
   changed['input_hash']=bundle.compute_input_hash(changed,rows)
   manifest_path.write_text(json.dumps(changed),encoding='utf-8')
   unpinned=bundle.verify_projection(root)
   self.assertNotEqual(unpinned['manifest']['input_hash'],original['input_hash'],'self-issued input hash follows the forged head')
   self.assertEqual(unpinned['receipt']['upstream_identity_status']['research_head'],'UNVERIFIED_DECLARATION')
   with self.assertRaisesRegex(ValueError,'research_head.*expected'):
    bundle.verify_projection(root,expected_identity={'research_head':original['research_head']})
 def test_duplicate_manifest_identity_claim_rejected_even_when_last_key_matches(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); original=fixture.make_projection(root)
   manifest_path=root/'manifest.json'; original_bytes=manifest_path.read_text().rstrip()
   # JSON's default last-key-wins parsing previously accepted this conflicting
   # first declaration and issued an apparently valid projection receipt.
   manifest_path.write_text(original_bytes[:-1]+',"research_head":"FORGED","research_head":'+json.dumps(original['research_head'])+'}')
   with self.assertRaisesRegex(ValueError,'duplicate JSON key'):
    bundle.verify_projection(root)
 def test_external_identity_expectations_bind_only_the_supplied_fields(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); manifest=fixture.make_projection(root)
   receipt=bundle.verify_projection(root,expected_identity={'research_head':manifest['research_head'],'input_hash':manifest['input_hash']})['receipt']
   self.assertEqual(receipt['upstream_identity_status']['research_head'],'EXTERNAL_EXPECTATION_MATCHED')
   self.assertEqual(receipt['upstream_identity_status']['input_hash'],'EXTERNAL_EXPECTATION_MATCHED')
   self.assertEqual(receipt['upstream_identity_status']['reconciliation_head'],'UNVERIFIED_DECLARATION')
   with self.assertRaisesRegex(ValueError,'unsupported expected identity'):
    bundle.verify_projection(root,expected_identity={'unreviewed_extra':'x'})
 def test_manifest_arbitrary_projection_hash_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); m=json.loads((root/'manifest.json').read_text()); m['projection_hash']='sha256:'+'0'*64; (root/'manifest.json').write_text(json.dumps(m));
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_legacy_projection_version_cannot_label_new_reference_catalog_contract(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);fixture.make_projection(root)
   manifest=json.loads((root/'manifest.json').read_text());manifest['projection_version']='0.2.0'
   (root/'manifest.json').write_text(json.dumps(manifest))
   with self.assertRaisesRegex(ValueError,'unsupported projection_version'):
    bundle.verify_projection(root)
 def test_file_hash_mismatch_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); (root/'entities.jsonl').write_text('{}\n');
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_record_count_mismatch_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); m=json.loads((root/'manifest.json').read_text()); m['outputs']['entities.jsonl']['count']=99; (root/'manifest.json').write_text(json.dumps(m));
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_missing_required_output_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); (root/'provenance.jsonl').unlink();
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_wrong_partition_status_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); facts=[json.loads(r) for r in (root/'facts.jsonl').read_text().splitlines()]; facts[0]['projection_status']='UNRESOLVED'; payload=''.join(bundle.canonical(r)+'\n' for r in facts).encode(); (root/'facts.jsonl').write_bytes(payload); m=json.loads((root/'manifest.json').read_text()); m['outputs']['facts.jsonl']['hash']=bundle.sha256_bytes(payload); m['projection_hash']=bundle.compute_projection_hash(m['outputs']); (root/'manifest.json').write_text(json.dumps(m));
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_stale_manifest_after_output_change_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); (root/'facts.jsonl').write_text('');
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_unexpected_jsonl_output_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root); (root/'bonus.jsonl').write_text('');
   with self.assertRaises(ValueError):bundle.verify_projection(root)
 def test_byte_identical_symlinked_output_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); root=base/'bundle'; root.mkdir(); fixture.make_projection(root)
   outside=base/'outside-entities.jsonl'; (root/'entities.jsonl').replace(outside)
   (root/'entities.jsonl').symlink_to(outside)
   with self.assertRaisesRegex(ValueError,'symlink'):
    bundle.verify_projection(root)
 def test_symlinked_manifest_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); root=base/'bundle'; root.mkdir(); fixture.make_projection(root)
   outside=base/'outside-manifest.json'; (root/'manifest.json').replace(outside)
   (root/'manifest.json').symlink_to(outside)
   with self.assertRaisesRegex(ValueError,'symlink'):
    bundle.verify_projection(root)
 def test_symlinked_bundle_directory_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); root=base/'bundle'; root.mkdir(); fixture.make_projection(root)
   alias=base/'alias'; alias.symlink_to(root,target_is_directory=True)
   with self.assertRaisesRegex(ValueError,'symlink'):
    bundle.verify_projection(alias)
 def test_symlinked_ancestor_cannot_hide_an_otherwise_valid_bundle(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); outside=base/'outside'; outside.mkdir()
   root=outside/'bundle'; root.mkdir(); fixture.make_projection(root)
   alias=base/'alias'; alias.symlink_to(outside,target_is_directory=True)
   with self.assertRaisesRegex(ValueError,'symlinked ancestor'):
    bundle.verify_projection(alias/'bundle')
 def test_dotdot_path_cannot_hide_symlinked_ancestor(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); outside=base/'outside'; outside.mkdir()
   root=base/'bundle'; root.mkdir(); fixture.make_projection(root)
   alias=base/'alias'; alias.symlink_to(outside,target_is_directory=True)
   # The path resolves to base/bundle, but first traverses the aliased parent.
   with self.assertRaisesRegex(ValueError,'symlinked ancestor'):
    bundle.verify_projection(alias/'..'/'bundle')
 def test_byte_identical_hardlinked_output_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td); root=base/'bundle'; root.mkdir(); fixture.make_projection(root)
   (base/'outside-entities.jsonl').hardlink_to(root/'entities.jsonl')
   with self.assertRaisesRegex(ValueError,'hardlinked'):
    bundle.verify_projection(root)
 def test_rehashed_bundle_missing_assertion_provenance_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   rewrite_bundle(root,'provenance.jsonl',lambda rows:[row for row in rows if row['assertion_id']!='a-stable'])
   with self.assertRaisesRegex(ValueError,'missing provenance'):bundle.verify_projection(root)
 def test_rehashed_bundle_orphan_provenance_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   def orphan(rows):
    rows[0]['assertion_id']='not-in-history'; rows[0]['provenance_id']='not-in-history::e1'
    return rows
   rewrite_bundle(root,'provenance.jsonl',orphan)
   with self.assertRaisesRegex(ValueError,'unknown assertion'):bundle.verify_projection(root)
 def test_rehashed_bundle_crossed_source_binding_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   def crossed(rows):
    rows[0]['source_work_binding_record']['source_id']='different-source'
    return rows
   rewrite_bundle(root,'provenance.jsonl',crossed)
   with self.assertRaisesRegex(ValueError,'binding endpoints'):bundle.verify_projection(root)
 def test_rehashed_bundle_changed_assertion_record_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   def changed(rows):
    rows[0]['assertion_record']['object']={'value':'not-the-accepted-history'}
    return rows
   rewrite_bundle(root,'provenance.jsonl',changed)
   with self.assertRaisesRegex(ValueError,'assertion record or support set mismatch'):bundle.verify_projection(root)
 def test_rehashed_bundle_changed_active_projection_status_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   def changed(rows):
    rows[0]['projection_status']='STABLE'
    return rows
   rewrite_bundle(root,'provenance.jsonl',changed)
   with self.assertRaisesRegex(ValueError,'active assertion status mismatch'):bundle.verify_projection(root)
 def test_rehashed_active_payload_must_match_immutable_assertion_history(self):
  for filename in ('facts.jsonl','contested.jsonl','unresolved.jsonl'):
   with self.subTest(filename=filename),tempfile.TemporaryDirectory() as td:
    root=Path(td); fixture.make_projection(root)
    def forged(rows):
     rows[0]['object']={'value':'FORGED_ACCEPTED_FACT'}
     return rows
    rewrite_bundle(root,filename,forged)
    with self.assertRaisesRegex(ValueError,'active assertion.*history payload mismatch'):
     bundle.verify_projection(root)
 def test_rehashed_active_extra_worker_payload_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   def forged(rows):
    rows[0]['unreviewed_truth']='INJECTED'
    return rows
   rewrite_bundle(root,'facts.jsonl',forged)
   with self.assertRaisesRegex(ValueError,'active assertion.*history payload mismatch'):
    bundle.verify_projection(root)
 def test_rehashed_orphan_active_fact_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   def forged(rows):
    rows[0]['assertion_id']='not-in-history'
    return rows
   rewrite_bundle(root,'facts.jsonl',forged)
   with self.assertRaisesRegex(ValueError,'active assertion.*absent from history'):
    bundle.verify_projection(root)
 def test_rehashed_unbacked_projection_decorations_are_rejected(self):
  for decoration in (
   {'resolved_scope':{'TIMELINE_SCOPE':'FORGED_PRIME'},'scope_resolution_decision_ids':{'TIMELINE_SCOPE':'nonexistent'}},
   {'subject_resolved_scope':{'CONTINUITY_SCOPE':'FORGED_PRIME'},'subject_scope_resolution_decision_ids':{'CONTINUITY_SCOPE':'nonexistent'}},
   {'subject_identity_links':[{'relation_predicate':'SAME_AS','target_type':'LOCAL_ENTITY','target_id':'phantom-entity','decision_id':'nonexistent'}]},
   {'projection_status_decision_id':'status-paradox'},
   {'assertion_disposition_decision_id':'nonexistent'},
  ):
   with self.subTest(decoration=decoration),tempfile.TemporaryDirectory() as td:
    root=Path(td); fixture.make_projection(root)
    def forged(rows):rows[0].update(decoration); return rows
    rewrite_bundle(root,'facts.jsonl',forged)
    with self.assertRaisesRegex(ValueError,'decision|decoration|reconciliation'):bundle.verify_projection(root)

 def test_rehashed_status_without_governing_decision_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   rewrite_bundle(root,'reconciliation_history.jsonl',lambda rows:[row for row in rows if row['decision_id']!='status-1'])
   with self.assertRaisesRegex(ValueError,'decision|reconciliation'):bundle.verify_projection(root)

 def test_rehashed_forged_status_decision_payload_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   def forged(rows):rows[0]['payload']={'projection_status':'UNRESOLVED'}; return rows
   rewrite_bundle(root,'reconciliation_history.jsonl',forged)
   with self.assertRaisesRegex(ValueError,'decision|reconciliation'):bundle.verify_projection(root)

 def test_rehashed_accepted_identity_decision_cannot_elevate_experimental_predicate(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   def forged(rows):
    rows.append({'record_type':'reconciliation_decision','decision_id':'forged-link','decision_type':'ENTITY_LINK',
                 'subject_type':'LOCAL_ENTITY','subject_id':'local-1',
                 'payload':{'relation_predicate':'SAME_AS','target_type':'LOCAL_ENTITY','target_id':'nonexistent-local-entity'},
                 'status':'ACCEPTED','evidence':['e1'],'method':'forged'})
    return rows
   rewrite_bundle(root,'reconciliation_history.jsonl',forged)
   with self.assertRaisesRegex(ValueError,'invalid accepted identity link'):bundle.verify_projection(root)

 def test_inactive_assertion_scope_still_replays_to_provenance(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   def accepted_scope(rows):
    rows.append({'record_type':'reconciliation_decision','decision_id':'inactive-scope','decision_type':'SCOPE_RESOLUTION',
                 'subject_type':'ASSERTION','subject_id':'a-rejected',
                 'payload':{'resolution_key':'TIMELINE_SCOPE','resolution':'other'},
                 'status':'ACCEPTED','evidence':['e1'],'method':'fixture'})
    return rows
   rewrite_bundle(root,'reconciliation_history.jsonl',accepted_scope)
   def decorated(rows):
    for row in rows:
     if row['assertion_id']=='a-rejected':row['scope_resolution_decision_ids']={'TIMELINE_SCOPE':'inactive-scope'}
    return rows
   rewrite_bundle(root,'provenance.jsonl',decorated)
   bundle.verify_projection(root)
   def remove_decorations(rows):
    for row in rows:
     if row['assertion_id']=='a-rejected':row.pop('scope_resolution_decision_ids')
    return rows
   rewrite_bundle(root,'provenance.jsonl',remove_decorations)
   with self.assertRaisesRegex(ValueError,'reconciliation decision replay mismatch'):bundle.verify_projection(root)

 def test_rehashed_decision_references_and_supersession_cannot_be_invented(self):
  for kind in ('phantom-work','phantom-evidence','phantom-predecessor','wrong-predecessor','missing-reason'):
   with self.subTest(decision=kind),tempfile.TemporaryDirectory() as td:
    root=Path(td); fixture.make_projection(root)
    def forge(rows):
     if kind=='phantom-work':
      rows.append({'record_type':'reconciliation_decision','decision_id':kind,'decision_type':'SCOPE_RESOLUTION',
                   'subject_type':'WORK','subject_id':'PHANTOM_WORK','payload':{'resolution_key':'TIMELINE_SCOPE','resolution':'fake'},
                   'status':'ACCEPTED','evidence':['e1'],'method':'forged'})
     else:
      decision=next(row for row in rows if row['decision_id']==('status-paradox' if kind=='wrong-predecessor' else 'status-1'))
      if kind=='phantom-evidence':decision['evidence']=['PHANTOM_EVIDENCE']
      elif kind=='phantom-predecessor':decision['supersedes']='PHANTOM_PREDECESSOR'
      elif kind=='wrong-predecessor':decision.update(supersedes='status-1',reason='wrong key')
      elif kind=='missing-reason':
       rows.append({'record_type':'reconciliation_decision','decision_id':'status-old','decision_type':'ASSERTION_PROJECTION_STATUS',
                    'subject_type':'ASSERTION','subject_id':'a-stable','payload':{'projection_status':'CONTESTED'},
                    'status':'SUPERSEDED','evidence':['e1'],'method':'fixture'})
       decision.update(supersedes='status-old',reason='')
     return rows
    rewrite_bundle(root,'reconciliation_history.jsonl',forge)
    with self.assertRaisesRegex(ValueError,'reconciliation|decision'):bundle.verify_projection(root)

 def test_manifest_registry_fingerprint_must_match_verifier_registry(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
   manifest['predicate_registry_hash']='sha256:'+'f'*64
   (root/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'registry'):bundle.verify_projection(root)

 def test_referenced_work_scope_and_valid_decision_supersession(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   def valid(rows):
    rows.append({'record_type':'reconciliation_decision','decision_id':'work-scope','decision_type':'SCOPE_RESOLUTION',
                 'subject_type':'WORK','subject_id':'work-1','payload':{'resolution_key':'TIMELINE_SCOPE','resolution':'branch-a'},
                 'status':'ACCEPTED','evidence':['a-stable'],'method':'fixture'})
    rows.append({'record_type':'reconciliation_decision','decision_id':'status-old','decision_type':'ASSERTION_PROJECTION_STATUS',
                 'subject_type':'ASSERTION','subject_id':'a-stable','payload':{'projection_status':'CONTESTED'},
                 'status':'SUPERSEDED','evidence':['e1'],'method':'fixture'})
    next(r for r in rows if r['decision_id']=='status-1').update(supersedes='status-old',reason='reviewed correction')
    return rows
   rewrite_bundle(root,'reconciliation_history.jsonl',valid)
   bundle.verify_projection(root)

 def test_replay_accepts_genuine_compiler_outputs_including_supersession_and_scope(self):
  cases=(
   [producer_fixture.status_decision('STABLE'),
    producer_fixture.decision('scope-assertion','SCOPE_RESOLUTION','ASSERTION','assertion-1',{'resolution_key':'TIMELINE_SCOPE','resolution':'branch-a'}),
    producer_fixture.decision('scope-entity','SCOPE_RESOLUTION','LOCAL_ENTITY','local-1',{'resolution_key':'CONTINUITY_SCOPE','resolution':'prime'})],
   [producer_fixture.decision('demote','ASSERTION_DISPOSITION','ASSERTION','assertion-1',{'disposition':'REJECTED'}),
    producer_fixture.decision('scope-inactive','SCOPE_RESOLUTION','ASSERTION','assertion-1',{'resolution_key':'TIMELINE_SCOPE','resolution':'branch-a'})],
   [],
  )
  for decisions in cases:
   with self.subTest(decisions=[d['decision_id'] for d in decisions]),tempfile.TemporaryDirectory() as td:
    root=Path(td); logical=compiler.build_logical_projection(producer_fixture.fixture_records(),decisions)
    outputs={}
    for filename in bundle.REQUIRED_OUTPUTS:
     entries=logical[filename.removesuffix('.jsonl')]
     raw=''.join(bundle.canonical(r)+'\n' for r in sorted(entries,key=lambda r:r[bundle.ID_KEYS[filename]])).encode('utf-8')
     (root/filename).write_bytes(raw)
     outputs[filename]={'role':filename.removesuffix('.jsonl'),'hash':bundle.sha256_bytes(raw),'count':len(entries)}
    manifest={'record_type':'projection_manifest','projection_version':'0.3.0','schema_version':'0.2.0',
              'methodology_version':'0.1.0','compiler_commit':'fixture','research_head':'fixture','reconciliation_head':'fixture',
              'predicate_registry_hash':bundle.sha256_bytes(bundle.canonical(json.loads((bundle.ROOT/'registry'/'predicates.json').read_text())).encode()),
              'scope_key_registry_hash':bundle.sha256_bytes(bundle.canonical(json.loads((bundle.ROOT/'registry'/'scope_keys.json').read_text())).encode()),
              'input_hash':None,'projection_hash':bundle.compute_projection_hash(outputs),'outputs':outputs}
    manifest['input_hash']=bundle.compute_input_hash(manifest,{name:logical[name.removesuffix('.jsonl')] for name in bundle.REQUIRED_OUTPUTS})
    (root/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
    self.assertEqual(bundle.verify_projection(root)['manifest']['projection_hash'],manifest['projection_hash'])

 def test_genuine_compiler_unreferenced_work_and_standalone_evidence_close_reference_contract(self):
  """A valid corpus can contain governed records absent from assertion provenance."""
  records=producer_fixture.fixture_records()
  orphan=dict(next(r for r in records if r['record_type']=='work'))
  orphan.update(work_id='work-without-assertion',title='Accepted unreferenced Work')
  evidence=dict(next(r for r in records if r['record_type']=='evidence'))
  evidence.update(evidence_id='evidence-not-in-any-assertion',locator={'line':99})
  records.extend((orphan,evidence))
  decisions=[producer_fixture.status_decision('STABLE')]
  work_scope=producer_fixture.decision('scope-unreferenced-work','SCOPE_RESOLUTION','WORK','work-without-assertion',
                                        {'resolution_key':'TIMELINE_SCOPE','resolution':'prime'})
  decisions.append(work_scope)
  status=decisions[0];status['evidence']=['evidence-not-in-any-assertion']
  logical=compiler.build_logical_projection(records,decisions)
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);outputs={}
   for filename in bundle.REQUIRED_OUTPUTS:
    entries=logical[filename.removesuffix('.jsonl')]
    raw=''.join(bundle.canonical(row)+'\n' for row in entries).encode('utf-8')
    (root/filename).write_bytes(raw)
    outputs[filename]={'role':filename.removesuffix('.jsonl'),'hash':bundle.sha256_bytes(raw),'count':len(entries)}
   manifest={'record_type':'projection_manifest','projection_version':'0.3.0','schema_version':'0.2.0',
             'methodology_version':'0.1.0','compiler_commit':'fixture','research_head':'fixture','reconciliation_head':'fixture',
             'predicate_registry_hash':bundle.sha256_bytes(bundle.canonical(json.loads((bundle.ROOT/'registry'/'predicates.json').read_text())).encode()),
             'scope_key_registry_hash':bundle.sha256_bytes(bundle.canonical(json.loads((bundle.ROOT/'registry'/'scope_keys.json').read_text())).encode()),
             'input_hash':None,'projection_hash':bundle.compute_projection_hash(outputs),'outputs':outputs}
   manifest['input_hash']=bundle.compute_input_hash(manifest,{name:logical[name.removesuffix('.jsonl')] for name in bundle.REQUIRED_OUTPUTS})
   (root/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
   verified=bundle.verify_projection(root)
   self.assertEqual(verified['rows']['works.jsonl'][-1]['work_id'],'work-without-assertion')
   self.assertEqual(len(verified['rows']['evidence.jsonl']),2)
   self.assertTrue(any(d['decision_id']=='scope-unreferenced-work' for d in verified['rows']['reconciliation_history.jsonl']))

 def test_self_rehashed_bundle_cannot_replace_referenced_evidence_catalog(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);fixture.make_projection(root)
   def forge(rows):rows[0]['observed']={'text':'fiction invented by rehasher'};return rows
   rewrite_bundle(root,'evidence.jsonl',forge)
   with self.assertRaisesRegex(ValueError,'evidence differs from reference catalog'):
    bundle.verify_projection(root)

 def test_standalone_evidence_cannot_claim_unknown_source(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);fixture.make_projection(root)
   def forge(rows):
    rows.append({**rows[0],'evidence_id':'e-standalone','source_id':'PHANTOM_SOURCE'})
    return rows
   rewrite_bundle(root,'evidence.jsonl',forge)
   with self.assertRaisesRegex(ValueError,'absent Source/Work'):
    bundle.verify_projection(root)

 def test_self_rehashed_schema_invalid_phantom_work_with_decision_is_rejected(self):
  """A forged catalog row is not admitted just because it has a plausible ID."""
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);fixture.make_projection(root)
   def forge_work(rows):
    rows.append({'record_type':'work','work_id':'schema-invalid-phantom'})
    return rows
   rewrite_bundle(root,'works.jsonl',forge_work)
   def forge_decision(rows):
    rows.append({'record_type':'reconciliation_decision','decision_id':'phantom-scope',
                 'decision_type':'SCOPE_RESOLUTION','subject_type':'WORK','subject_id':'schema-invalid-phantom',
                 'payload':{'resolution_key':'TIMELINE_SCOPE','resolution':'fake'},
                 'status':'ACCEPTED','evidence':['e1'],'method':'forged'})
    return rows
   rewrite_bundle(root,'reconciliation_history.jsonl',forge_decision)
   with self.assertRaisesRegex(ValueError,'invalid catalog record.*title'):
    bundle.verify_projection(root)

 def test_standalone_evidence_cannot_cross_explicit_source_work_binding(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);fixture.make_projection(root)
   def more_work(rows):
    rows.append({**rows[0],'work_id':'second-work','title':'Other Work'})
    return rows
   rewrite_bundle(root,'works.jsonl',more_work)
   def crossed_evidence(rows):
    rows.append({**rows[0],'evidence_id':'other-evidence','work_id':'second-work',
                 'source_work_binding_id':'binding-1'})
    return rows
   rewrite_bundle(root,'evidence.jsonl',crossed_evidence)
   def supporter(rows):
    next(r for r in rows if r['decision_id']=='status-1')['evidence']=['other-evidence']
    return rows
   rewrite_bundle(root,'reconciliation_history.jsonl',supporter)
   with self.assertRaisesRegex(ValueError,'explicit binding endpoints'):
    bundle.verify_projection(root)

 def test_standalone_evidence_requires_unique_accepted_evidence_bearing_binding(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);fixture.make_projection(root)
   def more_work(rows):
    rows.append({**rows[0],'work_id':'orphan-work','title':'Work with no Source binding'})
    return rows
   rewrite_bundle(root,'works.jsonl',more_work)
   def add_evidence(rows):
    rows.append({**rows[0],'evidence_id':'orphan-evidence','work_id':'orphan-work'})
    return rows
   rewrite_bundle(root,'evidence.jsonl',add_evidence)
   def decision_support(rows):
    next(r for r in rows if r['decision_id']=='status-1')['evidence']=['orphan-evidence']
    return rows
   rewrite_bundle(root,'reconciliation_history.jsonl',decision_support)
   with self.assertRaisesRegex(ValueError,'no uniquely eligible accepted evidence-bearing'):
    bundle.verify_projection(root)

 def test_unreferenced_binding_cannot_form_self_supersession_cycle(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);fixture.make_projection(root)
   def loop(rows):
    rows.append({**rows[0],'binding_id':'binding-loop','lifecycle':'PROPOSED',
                 'supersedes_binding_id':'binding-loop'})
    return rows
   rewrite_bundle(root,'source_work_bindings.jsonl',loop)
   with self.assertRaisesRegex(ValueError,'binding integrity.*cycle'):
    bundle.verify_projection(root)

 def test_unreferenced_derived_source_cannot_mint_independent_family(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);fixture.make_projection(root)
   def false_independence(rows):
    rows[0]['independence_group']='upstream-family'
    rows.append({**rows[0],'source_id':'source-derived','derived_from':['source-1'],
                 'independence_group':'fake-independent-family'})
    return rows
   rewrite_bundle(root,'sources.jsonl',false_independence)
   # First repair the legitimate fixture's Source snapshot so the falsifier is
   # caught by the independent lineage contract, not an unrelated mismatch.
   def update_provenance(rows):
    for row in rows:row['source_record']['independence_group']='upstream-family'
    return rows
   rewrite_bundle(root,'provenance.jsonl',update_provenance)
   with self.assertRaisesRegex(ValueError,'lineage integrity.*independence_group'):
    bundle.verify_projection(root)

 def test_unchanged_input_identity_detects_unreferenced_catalog_addition(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);fixture.make_projection(root)
   accepted_input_hash=json.loads((root/'manifest.json').read_text())['input_hash']
   def addition(rows):
    rows.append({**rows[0],'source_id':'unreferenced-added-source'})
    return rows
   rewrite_bundle(root,'sources.jsonl',addition)
   manifest=json.loads((root/'manifest.json').read_text())
   manifest['input_hash']=accepted_input_hash
   (root/'manifest.json').write_text(json.dumps(manifest))
   with self.assertRaisesRegex(ValueError,'input_hash mismatch'):
    bundle.verify_projection(root)

 def test_legitimate_accepted_scope_decisions_replay(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); fixture.make_projection(root)
   def add_scope(rows):
    for did,st,sid,key,value in (
     ('scope-assertion','ASSERTION','a-stable','TIMELINE_SCOPE','prime'),
     ('scope-subject','LOCAL_ENTITY','local-1','CONTINUITY_SCOPE','prime')):
     rows.append({'record_type':'reconciliation_decision','decision_id':did,'decision_type':'SCOPE_RESOLUTION','subject_type':st,'subject_id':sid,'payload':{'resolution_key':key,'resolution':value},'status':'ACCEPTED','evidence':['e1'],'method':'fixture'})
    return rows
   rewrite_bundle(root,'reconciliation_history.jsonl',add_scope)
   def decorated(rows):
    rows[0].update({
     'resolved_scope':{'TIMELINE_SCOPE':'prime'},
     'scope_resolution_decision_ids':{'TIMELINE_SCOPE':'scope-assertion'},
     'subject_resolved_scope':{'CONTINUITY_SCOPE':'prime'},
     'subject_scope_resolution_decision_ids':{'CONTINUITY_SCOPE':'scope-subject'}
    })
    return rows
   rewrite_bundle(root,'facts.jsonl',decorated)
   for filename in ('contested.jsonl','unresolved.jsonl'):
    def decorated_subject(rows):
     rows[0].update({'subject_resolved_scope':{'CONTINUITY_SCOPE':'prime'},'subject_scope_resolution_decision_ids':{'CONTINUITY_SCOPE':'scope-subject'}})
     return rows
    rewrite_bundle(root,filename,decorated_subject)
   def decorated_entity(rows):
    rows[0].update({'resolved_scope':{'CONTINUITY_SCOPE':'prime'},'scope_resolution_decision_ids':{'CONTINUITY_SCOPE':'scope-subject'}})
    return rows
   rewrite_bundle(root,'entities.jsonl',decorated_entity)
   def decorated_provenance(rows):
    for row in rows:
     if row['assertion_id']=='a-stable':row['scope_resolution_decision_ids']={'TIMELINE_SCOPE':'scope-assertion'}
    return rows
   rewrite_bundle(root,'provenance.jsonl',decorated_provenance)
   verified=bundle.verify_projection(root)
   self.assertEqual(verified['rows']['facts.jsonl'][0]['object'],{'value':'stable'})
if __name__=='__main__':unittest.main()
