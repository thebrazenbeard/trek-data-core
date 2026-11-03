"""Synthetic adversarial checks only; no genuine Trek source is present."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location('trek_source_bound_preflight', ROOT / 'tools' / 'check_source_bound_readiness.py')
assert spec and spec.loader
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)

CONTENT = b'Noncanonical synthetic fixture, nothing from a Trek source.\n'
HASH = 'sha256:' + hashlib.sha256(CONTENT).hexdigest()
WORK = {'record_type': 'work', 'work_id': 'fixture-episode', 'work_type': 'EPISODE',
        'status': 'ACCEPTED', 'fixture_only': False, 'parent_work_id': 'fixture-series'}
SOURCE = {'record_type': 'source', 'source_id': 'fixture-source', 'status': 'ACCEPTED',
          'fixture_only': False, 'source_kind': 'TRANSCRIPT_REPRESENTATION',
          'locator': 'private:FixtureSource1', 'source_version': 'fixture-version',
          'provenance_family': 'FIXTURE_FAMILY', 'independence_group': 'FIXTURE_GROUP',
          'content_hash': HASH}
BINDING = {'record_type': 'source_work_binding', 'binding_id': 'fixture-binding',
           'source_id': 'fixture-source', 'work_id': 'fixture-episode', 'lifecycle': 'ACCEPTED',
           'fixture_only': False, 'mapping_role': 'EVIDENCE_BEARING', 'method': 'synthetic fixture',
           'basis': [{'kind': 'BYTE_HASH', 'value': HASH}]}
DISCOVERED = {'record_type': 'coverage_event', 'coverage_event_id': 'fixture-discovered',
              'status': 'ACCEPTED', 'effect': 'ATTAINED', 'coverage_state': 'DISCOVERED',
              'work_id': 'fixture-episode', 'subject_type': 'WORK', 'subject_id': 'fixture-episode',
              'producer_role': 'LIBRARIAN'}
REQUEST = {'record_type': 'source_custody_request', 'schema_version': '1.0.0',
           'receipt_id': 'FixtureReceipt1', 'source_candidate_id': SOURCE['source_id'],
           'source_kind': SOURCE['source_kind'], 'locator_kind': 'PRIVATE_OPAQUE',
           'source_locator': SOURCE['locator'], 'source_version': SOURCE['source_version'],
           'edition_identity': 'synthetic fixture version',
           'provenance_family': SOURCE['provenance_family'],
           'independence_group': SOURCE['independence_group'],
           'rights_basis_reported': 'UNKNOWN', 'observed_on': '2026-11-03',
           'declared_sha256': HASH.removeprefix('sha256:')}


class SourceBoundReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.bytes_path = self.base / 'fixture-source.bin'
        self.bytes_path.write_bytes(CONTENT)
        self.request_path = self.base / 'request.json'
        self.request_path.write_text(json.dumps(REQUEST), encoding='utf-8')
        self.receipt_path = self.base / 'receipt.json'
        self.receipt_path.write_text(json.dumps(preflight.custody.build_receipt(REQUEST, self.bytes_path)), encoding='utf-8')
        self.works = {WORK['work_id']: dict(WORK)}
        self.sources = {SOURCE['source_id']: dict(SOURCE)}
        self.bindings = {BINDING['binding_id']: dict(BINDING)}
        self.records = [dict(DISCOVERED)]

    def assess(self, include_bytes=True):
        args = (self.request_path, self.receipt_path, self.bytes_path) if include_bytes else (None, None, None)
        return preflight.assess(WORK['work_id'], SOURCE['source_id'], BINDING['binding_id'],
                                self.works, self.sources, self.bindings, self.records, *args)

    def test_exact_bytes_and_accepted_context_only_open_proposal_review(self):
        report = self.assess()
        self.assertEqual(report['status'], 'READY_FOR_EVENT_PROPOSAL_REVIEW_REQUIRED')
        self.assertEqual(report['accepted_discovered_event_ids'], ['fixture-discovered'])
        self.assertEqual(report['coverage_effect'], 'NONE')
        self.assertFalse(report['coverage_event_created'])
        self.assertEqual(report['rights_identity_and_independent_review'], 'NOT_ESTABLISHED_BY_THIS_REPORT')

    def test_declared_matching_hash_without_private_bytes_is_not_ready(self):
        report = self.assess(include_bytes=False)
        self.assertEqual(report['status'], 'BLOCKED')
        self.assertIn('EXACT_PRIVATE_BYTE_CUSTODY_NOT_SUPPLIED', report['blockers'])

    def test_modified_source_bytes_fail_exact_receipt_replay(self):
        self.bytes_path.write_bytes(CONTENT + b'new bytes')
        self.assertIn('PRIVATE_BYTE_CUSTODY_REPLAY_OR_SOURCE_MATCH_FAILED', self.assess()['blockers'])

    def test_receipt_changed_even_when_computed_checksum_is_valid_is_rejected(self):
        receipt = json.loads(self.receipt_path.read_text())
        receipt['source_locator'] = 'private:DifferentSource'
        receipt['receipt_sha256'] = hashlib.sha256(preflight.custody.canonical({
            key: value for key, value in receipt.items() if key != 'receipt_sha256'})).hexdigest()
        self.receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
        self.assertIn('PRIVATE_BYTE_CUSTODY_REPLAY_OR_SOURCE_MATCH_FAILED', self.assess()['blockers'])

    def test_custody_identity_must_match_accepted_source_fields(self):
        self.sources[SOURCE['source_id']]['independence_group'] = 'FAKE_SECOND_GROUP'
        self.assertIn('PRIVATE_BYTE_CUSTODY_REPLAY_OR_SOURCE_MATCH_FAILED', self.assess()['blockers'])

    def test_metadata_only_or_superseded_binding_is_not_ready(self):
        self.bindings[BINDING['binding_id']]['mapping_role'] = 'METADATA_ONLY'
        self.assertIn('NOT_EVIDENCE_BEARING_BINDING', self.assess()['blockers'])
        self.bindings[BINDING['binding_id']]['mapping_role'] = 'EVIDENCE_BEARING'
        self.bindings['successor'] = {'lifecycle': 'ACCEPTED', 'supersedes_binding_id': BINDING['binding_id']}
        self.assertIn('BINDING_SUPERSEDED', self.assess()['blockers'])

    def test_absent_discovered_or_existing_source_bound_blocks_new_event(self):
        self.records = []
        self.assertIn('NO_ACCEPTED_DISCOVERED_PREDECESSOR', self.assess()['blockers'])
        self.records = [dict(DISCOVERED), {'record_type': 'coverage_event', 'coverage_event_id': 'fixture-bound',
                        'status': 'ACCEPTED', 'effect': 'ATTAINED', 'coverage_state': 'SOURCE_BOUND',
                        'work_id': WORK['work_id'], 'source_id': SOURCE['source_id'],
                        'binding_id': BINDING['binding_id']}]
        self.assertIn('SOURCE_BOUND_ALREADY_ATTAINED', self.assess()['blockers'])

    def test_no_nonfixture_authoritative_data_on_live_main_remains_blocked(self):
        run = subprocess.run([sys.executable, str(ROOT / 'tools' / 'check_source_bound_readiness.py'),
                              '--work-id', 'none', '--source-id', 'none', '--binding-id', 'none',
                              '--require-ready'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 2, run.stderr)
        report = json.loads(run.stdout)
        self.assertEqual(report['status'], 'BLOCKED')
        self.assertIn('NO_ACCEPTED_NONFIXTURE_WORK', report['blockers'])
        self.assertIn('NO_ACCEPTED_NONFIXTURE_SOURCE', report['blockers'])
        self.assertIn('NO_ACCEPTED_NONFIXTURE_BINDING', report['blockers'])
        self.assertEqual(report['coverage_effect'], 'NONE')


if __name__ == '__main__':
    unittest.main()
