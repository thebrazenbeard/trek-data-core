#!/usr/bin/env python3
"""Synthetic admission tests. These records are never accepted Trek corpus state."""
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
    spec = importlib.util.spec_from_file_location('trek_binding_test_' + name.replace('.', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate = load('validate.py')
projection = load('build_projection.py')


def records():
    # Work intentionally uses the Librarian's work_type, without legacy medium.
    return [
        {'record_type': 'source', 'source_id': 's1', 'status': 'ACCEPTED', 'source_kind': 'transcript',
         'locator': 'fixture://s1', 'provider': 'synthetic test source', 'provider_metadata': {},
         'source_version': None, 'retrieved_at': None, 'content_hash': 'sha256:fixture',
         'content_fingerprint': None, 'source_variant': 'original',
         'provenance_family': 'synthetic', 'independence_group': 'synthetic',
         'derived_from': [], 'fixture_only': False},
        {'record_type': 'work', 'work_id': 'w1', 'status': 'ACCEPTED', 'title': 'Synthetic Work',
         'work_type': 'EPISODE', 'parent_work_id': None, 'component_label': None, 'fixture_only': False},
        {'record_type': 'source_work_binding', 'binding_id': 'b1', 'source_id': 's1', 'work_id': 'w1',
         'lifecycle': 'ACCEPTED', 'mapping_role': 'EVIDENCE_BEARING',
         'source_scope': {'scope_type': 'WHOLE', 'locator': None},
         'work_scope': {'scope_type': 'WHOLE', 'component_label': None},
         'method': 'synthetic content check', 'basis': [{'kind': 'BYTE_HASH', 'value': 'sha256:fixture'}],
         'exclusive_scope_key': None, 'supersedes_binding_id': None, 'notes': '', 'fixture_only': False},
        {'record_type': 'local_entity', 'local_entity_id': 'l1', 'work_id': 'w1', 'label': 'Synthetic'},
        {'record_type': 'evidence', 'evidence_id': 'e1', 'source_id': 's1', 'work_id': 'w1',
         'evidence_kind': 'depiction', 'locator': {'line': 1}, 'observed': {'action': 'test'}},
        {'record_type': 'assertion', 'assertion_id': 'a1', 'subject_type': 'LOCAL_ENTITY', 'subject': 'l1',
         'predicate': 'CLAIMS', 'object': 'synthetic', 'evidence': ['e1'], 'status': 'ACCEPTED'},
    ]


class LibrarianBindingBridgeTests(unittest.TestCase):
    def validate_rows(self, rows, split=False):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            if split:
                librarian = root / 'registry' / 'authoritative'
                research = root / 'research'
                librarian.mkdir(parents=True)
                research.mkdir()
                (librarian / 'records.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows
                    if r['record_type'] in ('source', 'work', 'source_work_binding')))
                (research / 'records.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows
                    if r['record_type'] not in ('source', 'work', 'source_work_binding')))
                roots = [librarian, research]
            else:
                research = root / 'research'
                research.mkdir()
                (research / 'records.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
                roots = [research]
            prior = validate.DATA_ROOTS
            validate.DATA_ROOTS = roots
            try:
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    status = validate.main()
            finally:
                validate.DATA_ROOTS = prior
            return status, out.getvalue()

    def test_work_type_only_is_compatible_with_canonical_work_schema(self):
        work = records()[1]
        self.assertNotIn('medium', work)
        self.assertEqual(validate.schema_errors(work, validate.load_schemas()['work']), [])
        self.assertEqual(self.validate_rows(records(), split=True)[0], 0)

    def test_missing_binding_blocks_evidence_and_projection(self):
        rows = [r for r in records() if r['record_type'] != 'source_work_binding']
        status, out = self.validate_rows(rows)
        self.assertEqual(status, 1)
        self.assertIn('lacks one eligible ACCEPTED EVIDENCE_BEARING', out)
        with self.assertRaisesRegex(ValueError, 'lacks one eligible'):
            projection.build_logical_projection(rows, [])

    def test_proposed_binding_does_not_authorize_evidence(self):
        rows = records()
        rows[2]['lifecycle'] = 'PROPOSED'
        self.assertEqual(self.validate_rows(rows)[0], 1)

    def test_metadata_only_binding_is_not_evidence_bearing(self):
        rows = records()
        rows[2]['mapping_role'] = 'METADATA_ONLY'
        status, out = self.validate_rows(rows)
        self.assertEqual(status, 1)
        self.assertIn('EVIDENCE_BEARING', out)

    def test_accepted_metadata_only_mapping_is_rejected_by_main_librarian_contract(self):
        rows = [r for r in records() if r['record_type'] not in ('evidence', 'assertion')]
        rows[2]['mapping_role'] = 'METADATA_ONLY'
        rows[2]['basis'] = []
        status, output = self.validate_rows(rows)
        self.assertEqual(status, 1)
        self.assertIn('ACCEPTED binding must be EVIDENCE_BEARING', output)

    def test_proposed_metadata_only_mapping_can_remain_a_candidate_without_evidence(self):
        rows = [r for r in records() if r['record_type'] not in ('evidence', 'assertion')]
        rows[2]['mapping_role'] = 'METADATA_ONLY'
        rows[2]['lifecycle'] = 'PROPOSED'
        rows[2]['basis'] = []
        self.assertEqual(self.validate_rows(rows)[0], 0)

    def test_fixture_only_binding_cannot_promote_corpus_evidence(self):
        rows = records()
        rows[2]['fixture_only'] = True
        status, out = self.validate_rows(rows)
        self.assertEqual(status, 1)
        self.assertIn('fixture-only', out)

    def test_missing_explicit_fixture_flag_is_not_eligible(self):
        rows = records()
        del rows[0]['fixture_only']
        self.assertEqual(self.validate_rows(rows)[0], 1)

    def test_wrong_work_pair_is_not_authorized_by_other_valid_binding(self):
        rows = records()
        rows.insert(2, {'record_type': 'work', 'work_id': 'w2', 'status': 'ACCEPTED',
                        'title': 'Other', 'work_type': 'EPISODE', 'fixture_only': False})
        rows[3]['work_id'] = 'w2'
        status, out = self.validate_rows(rows)
        self.assertEqual(status, 1)
        self.assertIn('lacks one eligible', out)

    def test_unsupported_basis_does_not_authorize_evidence(self):
        rows = records()
        rows[2]['basis'] = [{'kind': 'PROVIDER_HEADING', 'value': 'unverified title'}]
        status, out = self.validate_rows(rows)
        self.assertEqual(status, 1)
        self.assertIn('lacks content/hash/manifest basis', out)

    def test_scoped_binding_requires_explicit_evidence_reference(self):
        rows = records()
        rows[2]['source_scope'] = {'scope_type': 'SLICE', 'locator': 'line:1'}
        self.assertEqual(self.validate_rows(rows)[0], 1)
        rows[4]['source_work_binding_id'] = 'b1'
        self.assertEqual(self.validate_rows(rows)[0], 0)

    def test_scoped_binding_requires_nonempty_locator(self):
        rows = records()
        rows[2]['source_scope'] = {'scope_type': 'SLICE', 'locator': None}
        rows[4]['source_work_binding_id'] = 'b1'
        status, out = self.validate_rows(rows)
        self.assertEqual(status, 1)
        self.assertIn('scoped Source requires locator', out)

    def test_malformed_scope_fails_as_validation_error_not_exception(self):
        rows = records()
        rows[2]['source_scope'] = 'not-an-object'
        status, out = self.validate_rows(rows)
        self.assertEqual(status, 1)
        self.assertIn('expected type', out)

    def test_malformed_basis_fails_as_validation_error_not_exception(self):
        rows = records()
        rows[2]['basis'] = True
        status, out = self.validate_rows(rows)
        self.assertEqual(status, 1)
        self.assertIn('expected type', out)

    def test_projection_emits_binding_record_and_changes_with_binding(self):
        rows = records()
        first = projection.build_logical_projection(rows, [])['provenance'][0]
        self.assertEqual(first['source_work_binding_record']['binding_id'], 'b1')
        self.assertEqual(first['source_work_binding_record']['basis'][0]['kind'], 'BYTE_HASH')
        updated = copy.deepcopy(rows)
        updated[2]['basis'][0]['value'] = 'sha256:changed'
        second = projection.build_logical_projection(updated, [])['provenance'][0]
        self.assertNotEqual(projection.canonical(first), projection.canonical(second))

    def test_separate_authoritative_registry_and_research_roots_compose(self):
        rows = records()
        self.assertEqual(self.validate_rows(rows, split=True)[0], 0)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            librarian = root / 'registry' / 'authoritative'
            research = root / 'research'
            librarian.mkdir(parents=True)
            research.mkdir()
            (librarian / 'records.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows[:3]))
            (research / 'records.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows[3:]))
            scanned = list(projection.iter_typed_records((librarian, research)))
            self.assertEqual(len(scanned), len(rows))
            result = projection.build_logical_projection(scanned, [])
            self.assertEqual(result['provenance'][0]['source_work_binding_record']['source_id'], 's1')

    def test_binding_cannot_be_admitted_from_staging_partition(self):
        binding = records()[2]
        errors = []
        validate.validate_partition_ownership([(validate.ROOT / 'external' / 'staging.json', binding)], errors)
        self.assertTrue(any('authoritative Librarian registry root' in error for error in errors))

    def test_authoritative_source_requires_provider_and_independence_fields(self):
        rows = records()
        del rows[0]['provider']
        status, output = self.validate_rows(rows, split=True)
        self.assertEqual(status, 1)
        self.assertIn('provider', output)

    def test_authoritative_work_requires_parent_and_component_fields(self):
        rows = records()
        del rows[1]['component_label']
        status, output = self.validate_rows(rows, split=True)
        self.assertEqual(status, 1)
        self.assertIn('component_label', output)

    def test_authoritative_binding_requires_notes_and_rejects_extra_keys(self):
        rows = records()
        del rows[2]['notes']
        status, output = self.validate_rows(rows, split=True)
        self.assertEqual(status, 1)
        self.assertIn('notes', output)
        rows[2]['notes'] = ''
        rows[2]['undeclared'] = True
        status, output = self.validate_rows(rows, split=True)
        self.assertEqual(status, 1)
        self.assertIn('unexpected property undeclared', output)

    def test_real_accepted_source_work_cannot_live_in_staging(self):
        rows = records()
        errors = []
        validate.validate_partition_ownership([
            (validate.ROOT / 'external' / 'source.json', rows[0]),
            (validate.ROOT / 'migrations' / 'work.json', rows[1]),
        ], errors)
        self.assertIn('authoritative Librarian registry root', '\n'.join(errors))

    def test_accepted_metadata_only_binding_cannot_mix_fixture_and_real_identity(self):
        rows = [r for r in records() if r['record_type'] not in ('evidence', 'assertion')]
        rows[0]['fixture_only'] = True
        status, output = self.validate_rows(rows, split=True)
        self.assertEqual(status, 1)
        self.assertIn('fixture-only', output)

    def test_accepted_binding_cannot_supersede_unaccepted_predecessor(self):
        rows = [r for r in records() if r['record_type'] not in ('evidence', 'assertion')]
        rows[2]['lifecycle'] = 'PROPOSED'
        successor = copy.deepcopy(rows[2])
        successor.update({'binding_id': 'b2', 'lifecycle': 'ACCEPTED', 'supersedes_binding_id': 'b1'})
        rows.append(successor)
        status, output = self.validate_rows(rows, split=True)
        self.assertEqual(status, 1)
        self.assertIn('accepted binding successor', output)


if __name__ == '__main__':
    unittest.main()
