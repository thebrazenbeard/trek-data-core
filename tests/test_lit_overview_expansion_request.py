"""Failure-mode tests for the proposal-only literary synopsis expansion request."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('lit_overview_request', ROOT / 'tools' / 'build_lit_overview_expansion_request.py')
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class LiteraryOverviewExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = builder.build()

    def test_18_new_source_local_candidates_are_not_publicly_published(self):
        request = self.request
        self.assertEqual(request['candidate_count'], 18)
        self.assertEqual(request['accepted_directory_snapshot_row_count'], 1214)
        self.assertEqual(request['source_lineage_group'], 'publisher:simonandschuster.com')
        self.assertEqual(request['independent_source_count'], 1)
        self.assertEqual(request['public_site_effect'], 'NONE')
        self.assertEqual(request['source_work_evidence_admission_effect'], 'NONE')
        self.assertEqual(len(request['source_artifacts']), 3)
        self.assertEqual(request['corrected_paraphrase_count'], 2)
        self.assertEqual(request['request_state'], 'V2_SUPERSEDING_PROPOSAL_FOR_SEPARATE_EDITORIAL_REVIEW')
        self.assertEqual(request['supersedes_review_request_sha256'], 'bf9cc901d772a11b9c6e92260575a1116e4de132938a037ea087a6be036b5f42')
        self.assertEqual(len({c['proposed_directory_row_id'] for c in request['candidates']}), 18)
        for entry in request['candidates']:
            self.assertIsNone(entry['accepted_directory_row_id'])
            self.assertEqual(entry['identity_status'], 'SOURCE_LOCAL_UNRECONCILED')
            self.assertIsNone(entry['raw_webpage_sha256'])
            self.assertEqual(entry['editorial_review_status'], 'INDEPENDENT_REVIEW_REQUIRED')
            self.assertEqual(entry['public_release_status'], 'NOT_RELEASED')
            self.assertEqual(entry['artwork_release_status'], 'HELD_NO_PUBLIC_DISPLAY')
            self.assertEqual(entry['accepted_work_effect'], 'NONE')
            self.assertEqual(entry['accepted_coverage_effect'], 'NONE')
            self.assertEqual(entry['original_paraphrase_sha256'], builder._sha(entry['original_paraphrase'].encode('utf-8')))

    def test_no_existing_accepted_directory_titles_or_rows_reused(self):
        directory = builder._json('explorer/discovery-catalog.json')
        accepted_lit = {row['title'].casefold() for row in directory['rows'] if row['medium'] == 'LITERATURE'}
        accepted_rows = {row['row_id'] for row in directory['rows']}
        for entry in self.request['candidates']:
            self.assertNotIn(entry['title'].casefold(), accepted_lit)
            self.assertNotIn(entry['proposed_directory_row_id'], accepted_rows)

    def test_wrong_publisher_edition_isbn_rejected(self):
        value = copy.deepcopy(self.request['candidates'][0])
        with self.assertRaises(builder.CandidateError):
            builder._official_url(value['publisher_edition_url'], '9780000000000')

    def test_copyrighted_cover_url_is_never_authorized_by_source(self):
        source = builder.INPUTS[0]
        raw = builder._json(source)['candidate_works'][0]
        digest = builder._sha(builder._read(source))
        amended = copy.deepcopy(raw)
        amended['cover_rights_status'] = 'APPROVED'
        with self.assertRaisesRegex(builder.CandidateError, 'Cover candidate rights'):
            builder._candidate(amended, source, digest)
        amended = copy.deepcopy(raw)
        amended['cover_candidate_locator'] = 'https://attacker.example/image.jpg'
        with self.assertRaisesRegex(builder.CandidateError, 'Cover candidate rights'):
            builder._candidate(amended, source, digest)

    def test_book_synopsis_without_accepted_source_packet_is_rejected(self):
        original = builder._json

        def tampered(path):
            obj = original(path)
            if path == builder.INPUTS[1]:
                obj = copy.deepcopy(obj)
                obj['close_read'] = True
            return obj

        with mock.patch.object(builder, '_json', side_effect=tampered):
            with self.assertRaisesRegex(builder.CandidateError, 'Not source-local six-title'):
                builder.build()

    def test_source_artifact_hash_pinned_exactly(self):
        for artifact in self.request['source_artifacts']:
            self.assertEqual(artifact['sha256'], builder._sha(builder._read(artifact['path'])))
            self.assertEqual(artifact['candidate_count'], 6)

    def test_two_source_relative_modal_corrections_preserve_old_request_and_packet(self):
        r = self.request
        self.assertEqual(r['supersedes_review_request_sha256'], builder._sha(builder._read(builder.LEGACY_OUTPUT)))
        self.assertEqual(r['source_local_correction_sha256'], builder._sha(builder._read(builder.CORRECTIONS)))
        by_id = {c['candidate_work_id']: c for c in r['candidates']}
        old = {c['candidate_work_id']: c for c in builder._json(builder.LEGACY_OUTPUT)['candidates']}
        somewhere = by_id['lit-source-local-sns-discovery-somewhere-to-belong-20261103']
        firewall = by_id['lit-source-local-sns-picard-firewall-20261103']
        self.assertNotEqual(somewhere['original_paraphrase_sha256'], old[somewhere['candidate_work_id']]['original_paraphrase_sha256'])
        self.assertNotEqual(firewall['original_paraphrase_sha256'], old[firewall['candidate_work_id']]['original_paraphrase_sha256'])
        self.assertIn('may lead to a new crisis', somewhere['original_paraphrase'])
        self.assertIn('finds a new home with the Fenris Rangers', firewall['original_paraphrase'])
        self.assertEqual(sum(c['display_supersession_source'] is not None for c in r['candidates']), 2)

    def test_correction_source_hash_mismatch_or_old_modal_text_rejected(self):
        original = builder._json

        def tamper_source(path):
            data = original(path)
            if path == builder.CORRECTIONS:
                data = copy.deepcopy(data)
                data['supersedes_source_sha256'] = 'a' * 64
            return data

        with mock.patch.object(builder, '_json', side_effect=tamper_source):
            with self.assertRaisesRegex(builder.CandidateError, 'provenance/version'):
                builder.build()

        def tamper_semantics(path):
            data = original(path)
            if path == builder.CORRECTIONS:
                data = copy.deepcopy(data)
                data['corrections'][0]['replacement_paraphrase'] = 'The publisher follows Discovery and its crew through a new danger after a distress signal from their earlier century draws them into crisis.'
            return data

        with mock.patch.object(builder, '_json', side_effect=tamper_semantics):
            with self.assertRaisesRegex(builder.CandidateError, 'modal regression'):
                builder.build()

    def test_committed_review_request_exactly_rebuilds(self):
        self.assertEqual(builder._read(builder.OUTPUT), builder._render(self.request))


if __name__ == '__main__':
    unittest.main()
