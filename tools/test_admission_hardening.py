"""Adversarial admission regressions for source identity and physical record custody."""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


def load(name):
    path = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location('trek_hardening_' + name.replace('.', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate = load('validate.py')
projection = load('build_projection.py')
bridge = load('test_librarian_binding_bridge.py')


class AdmissionHardeningTests(unittest.TestCase):
    def admit(self, rows):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            librarian = root / 'registry' / 'authoritative'
            research = root / 'research'
            librarian.mkdir(parents=True)
            research.mkdir()
            (librarian / 'records.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in rows
                if row['record_type'] in ('source', 'work', 'source_work_binding')))
            (research / 'records.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in rows
                if row['record_type'] not in ('source', 'work', 'source_work_binding')))
            old = validate.DATA_ROOTS
            validate.DATA_ROOTS = [librarian, research]
            try:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    status = validate.main()
            finally:
                validate.DATA_ROOTS = old
            return status, output.getvalue()

    def test_byte_hash_requires_sha256_hex_and_matches_source(self):
        records = bridge.records()
        records[2]['basis'][0]['value'] = 'sha256:arbitrary'
        status, output = self.admit(records)
        self.assertEqual(status, 1)
        self.assertIn('BYTE_HASH', output)
        records[2]['basis'][0]['value'] = 'sha256:' + '0' * 64
        status, output = self.admit(records)
        self.assertEqual(status, 1)
        self.assertIn('BYTE_HASH', output)

    def test_source_derivation_cycle_rejected_before_projection(self):
        records = bridge.records()
        records[0]['derived_from'] = ['s1']
        status, output = self.admit(records)
        self.assertEqual(status, 1)
        self.assertIn('source derivation cycle', output)
        with self.assertRaisesRegex(ValueError, 'source derivation cycle'):
            projection.build_logical_projection(records, [])

    def test_work_parent_cycle_rejected_before_projection(self):
        records = bridge.records()
        records[1]['parent_work_id'] = 'w1'
        status, output = self.admit(records)
        self.assertEqual(status, 1)
        self.assertIn('work parent cycle', output)
        with self.assertRaisesRegex(ValueError, 'work parent cycle'):
            projection.build_logical_projection(records, [])

    def test_derivative_cannot_mint_new_independence_group(self):
        records = bridge.records()
        parent = copy.deepcopy(records[0])
        parent['source_id'] = 's0'
        parent['derived_from'] = []
        records[0]['derived_from'] = ['s0']
        records[0]['independence_group'] = 'new-false-witness'
        records.insert(0, parent)
        status, output = self.admit(records)
        self.assertEqual(status, 1)
        self.assertIn('independence_group', output)
        records[1]['independence_group'] = parent['independence_group']
        self.assertEqual(self.admit(records)[0], 0)

    def test_symlink_file_and_directory_rejected_by_both_scanners(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            trusted = root / 'registry' / 'authoritative'
            trusted.mkdir(parents=True)
            external = root / 'external'
            external.mkdir()
            (external / 'outside.json').write_text(json.dumps(bridge.records()[0]))
            (trusted / 'hidden.json').symlink_to(external / 'outside.json')
            old = validate.DATA_ROOTS
            validate.DATA_ROOTS = [trusted]
            try:
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    status = validate.main()
                self.assertEqual(status, 1)
                self.assertIn('symlink', out.getvalue().lower())
            finally:
                validate.DATA_ROOTS = old
            with self.assertRaisesRegex(ValueError, 'symlink'):
                list(projection.iter_typed_records([trusted]))
            (trusted / 'hidden.json').unlink()
            (trusted / 'other').symlink_to(external, target_is_directory=True)
            validate.DATA_ROOTS = [trusted]
            try:
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    status = validate.main()
                self.assertEqual(status, 1)
                self.assertIn('symlink', out.getvalue().lower())
            finally:
                validate.DATA_ROOTS = old
            with self.assertRaisesRegex(ValueError, 'symlink'):
                list(projection.iter_typed_records([trusted]))

    def test_duplicate_json_keys_rejected_by_both_scanners(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            root.mkdir(exist_ok=True)
            (root / 'duplicate.jsonl').write_text('{"record_type":"source","source_id":"s1","source_id":"s2"}\n')
            old = validate.DATA_ROOTS
            validate.DATA_ROOTS = [root]
            try:
                with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                    list(validate.iter_records())
            finally:
                validate.DATA_ROOTS = old
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                list(projection.iter_typed_records([root]))
            (root / 'duplicate.jsonl').unlink()
            (root / 'duplicate.json').write_text('{"record_type":"work","work_id":"w1","work_id":"w2"}')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                list(projection.iter_typed_records([root]))


if __name__ == '__main__':
    unittest.main()
