"""Synthetic adversarial checks only; no genuine Trek source is present."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager, redirect_stdout
from unittest.mock import patch

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

    def test_revoked_discovered_predecessor_cannot_authorize_source_bound(self):
        self.records.append({
            'record_type': 'coverage_event', 'coverage_event_id': 'fixture-revocation',
            'status': 'ACCEPTED', 'effect': 'REVOKED', 'coverage_state': 'DISCOVERED',
            'work_id': WORK['work_id'], 'subject_type': 'WORK',
            'subject_id': WORK['work_id'], 'producer_role': 'LIBRARIAN',
            'supersedes': DISCOVERED['coverage_event_id'],
        })
        result = self.assess()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result['accepted_discovered_event_ids'], [])
        self.assertIn('NO_ACCEPTED_DISCOVERED_PREDECESSOR', result['blockers'])

    def test_wrong_binding_context_remains_blocked_with_matching_source_bytes(self):
        self.bindings[BINDING['binding_id']]['work_id'] = 'different-episode'
        result = self.assess()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn('BINDING_CONTEXT_MISMATCH', result['blockers'])
        self.assertNotIn('PRIVATE_BYTE_CUSTODY_REPLAY_OR_SOURCE_MATCH_FAILED', result['blockers'])

    def test_work_roster_key_cannot_mask_wrong_row_identity(self):
        self.works[WORK['work_id']]['work_id'] = 'different-episode'
        result = self.assess()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn('WORK_IDENTITY_MISMATCH', result['blockers'])

    def test_source_roster_key_cannot_mask_wrong_row_identity(self):
        self.sources[SOURCE['source_id']]['source_id'] = 'different-source'
        result = self.assess()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn('SOURCE_IDENTITY_MISMATCH', result['blockers'])

    def test_binding_roster_key_cannot_mask_wrong_row_identity(self):
        self.bindings[BINDING['binding_id']]['binding_id'] = 'different-binding'
        result = self.assess()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn('BINDING_IDENTITY_MISMATCH', result['blockers'])

    def test_replayed_receipt_with_duplicate_json_key_is_rejected(self):
        receipt = self.receipt_path.read_text(encoding='utf-8')
        self.receipt_path.write_text(receipt[:-1] + ',"receipt_id":"ForgedReceipt"}', encoding='utf-8')
        result = self.assess()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn('PRIVATE_BYTE_CUSTODY_REPLAY_OR_SOURCE_MATCH_FAILED', result['blockers'])

    def test_source_hash_change_blocks_both_basis_and_receipt_context(self):
        self.sources[SOURCE['source_id']]['content_hash'] = 'sha256:' + '0' * 64
        result = self.assess()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn('NO_EXACT_SOURCE_BYTE_HASH_BASIS', result['blockers'])
        self.assertIn('PRIVATE_BYTE_CUSTODY_REPLAY_OR_SOURCE_MATCH_FAILED', result['blockers'])

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

    def test_cli_report_pins_exact_governed_inputs_even_when_blocked(self):
        run = subprocess.run([sys.executable, str(ROOT / 'tools' / 'check_source_bound_readiness.py'),
                              '--work-id', 'none', '--source-id', 'none', '--binding-id', 'none'],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)
        self.assertRegex(report['governed_inputs_sha256'], r'^sha256:[0-9a-f]{64}$')
        self.assertEqual(report['governed_inputs_scope'],
                         'LOCAL_AUTHORITATIVE_REGISTRY_AND_COVERAGE_BYTES_NOT_REMOTE_ACCEPTANCE')

    def test_governed_byte_pin_detects_each_roster_and_coverage_file_change(self):
        root = self.base / 'mock-repo'
        registry = root / 'registry' / 'authoritative'
        coverage = root / 'coverage'
        registry.mkdir(parents=True)
        coverage.mkdir()
        files = [registry / 'work.json', registry / 'source.jsonl',
                 registry / 'binding.json', coverage / 'event.jsonl']
        for path in files:
            path.write_text('{"a":1}\n', encoding='utf-8')
        with patch.object(preflight.ledger, 'ROOT', root):
            original = preflight.governed_input_sha256()
            self.assertRegex(original, r'^sha256:[0-9a-f]{64}$')
            for path in files:
                initial = path.read_bytes()
                path.write_bytes(initial + b' ')
                self.assertNotEqual(original, preflight.governed_input_sha256(), path.name)
                path.write_bytes(initial)
                self.assertEqual(original, preflight.governed_input_sha256(), path.name)
            # Path identity matters too, not just record content.
            moved = registry / 'renamed-work.json'
            files[0].rename(moved)
            self.assertNotEqual(original, preflight.governed_input_sha256())

    def test_governed_pin_rejects_linked_inputs_and_excludes_unrelated_files(self):
        root = self.base / 'mock-repo'
        registry = root / 'registry' / 'authoritative'
        registry.mkdir(parents=True)
        file = registry / 'work.json'
        file.write_text('{"record_type":"work"}\n', encoding='utf-8')
        with patch.object(preflight.ledger, 'ROOT', root):
            original = preflight.governed_input_sha256()
            (root / 'private-staging-not-governed.json').write_text('sensitive', encoding='utf-8')
            self.assertEqual(original, preflight.governed_input_sha256())
            (registry / 'linked.json').symlink_to(file)
            with self.assertRaises(ValueError):
                preflight.governed_input_sha256()

    def test_governed_pin_distinguishes_raw_lf_and_crlf_bytes(self):
        root = self.base / 'mock-repo'
        registry = root / 'registry' / 'authoritative'
        registry.mkdir(parents=True)
        file = registry / 'work.json'
        file.write_bytes(b'{"record_type":"work"}\n')
        with patch.object(preflight.ledger, 'ROOT', root):
            lf = preflight.governed_input_sha256()
            file.write_bytes(b'{"record_type":"work"}\r\n')
            crlf = preflight.governed_input_sha256()
            self.assertNotEqual(lf, crlf, 'byte identity must not normalize newlines')
            file.write_bytes(b'{"record_type":"work"}\n')
            self.assertEqual(lf, preflight.governed_input_sha256())

    def test_custody_claim_and_review_receipts_change_preflight_input_pin(self):
        """The canonical SOURCE_BOUND gate's new files belong to preflight state."""
        root = self.base / 'mock-repo'
        registry = root / 'registry' / 'authoritative'
        registry.mkdir(parents=True)
        (registry / 'work.json').write_bytes(b'{"record_type":"work"}\n')
        with patch.object(preflight.ledger, 'ROOT', root):
            baseline = preflight.governed_input_sha256()
            previous = baseline
            for kind, receipt_type in (
                    ('bound-claims', 'SOURCE_BOUND_CUSTODY_CLAIM'),
                    ('bound-reviews', 'SOURCE_BOUND_CUSTODY_REVIEW')):
                receipt = root / 'coverage' / kind / ('f' * 64 + '.json')
                receipt.parent.mkdir(parents=True, exist_ok=True)
                receipt.write_bytes(json.dumps({'receipt_kind': receipt_type}).encode() + b'\n')
                current = preflight.governed_input_sha256()
                self.assertNotEqual(previous, current, kind)
                previous = current
                receipt.write_bytes(receipt.read_bytes().replace(b'\n', b'\r\n'))
                self.assertNotEqual(current, preflight.governed_input_sha256(),
                                    f'{kind} exact byte content must be pinned')
                previous = preflight.governed_input_sha256()
            self.assertNotEqual(baseline, previous)

    def test_governed_raw_reader_rejects_midread_path_replacement(self):
        root = self.base / 'mock-repo'
        registry = root / 'registry' / 'authoritative'
        registry.mkdir(parents=True)
        file = registry / 'work.json'
        file.write_bytes(b'{"record_type":"work"}\n')
        original_open = preflight.ledger._open_governed
        swapped = False

        @contextmanager
        def replace_after_read(path, directory=False):
            nonlocal swapped
            with original_open(path, directory=directory) as fd:
                yield fd
            if path == file and not swapped:
                file.rename(registry / 'original.json.bak')
                file.write_bytes(b'{"record_type":"forged"}\n')
                swapped = True

        with patch.object(preflight.ledger, 'ROOT', root):
            with patch.object(preflight.ledger, '_open_governed', side_effect=replace_after_read):
                with self.assertRaisesRegex(ValueError, 'replaced during read'):
                    preflight.governed_input_sha256()

    def test_governed_drift_during_main_preflight_fails_closed(self):
        output = io.StringIO()
        with patch.object(preflight, 'governed_input_sha256', side_effect=[
                'sha256:' + 'a' * 64, 'sha256:' + 'b' * 64]):
            with redirect_stdout(output):
                code = preflight.main(['--work-id', 'none', '--source-id', 'none',
                                       '--binding-id', 'none'])
        self.assertEqual(code, 3)
        self.assertEqual(json.loads(output.getvalue()),
                         {'status': 'INVALID_GOVERNED_INPUT', 'coverage_effect': 'NONE'})


if __name__ == '__main__':
    unittest.main()
