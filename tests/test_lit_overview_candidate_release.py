"""A future public candidate synopsis catalog must have a real separate receipt."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
import sys
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location('literary_candidate_release', TOOLS / 'build_lit_overview_candidate_release.py')
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class LiteraryCandidateReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = release.build()
        cls.receipt = {
            'schema_version': '1.0.0',
            'review_kind': 'MODEL_EDITORIAL_REVIEW',
            'review_result': 'PASS_18_OFFICIAL_PUBLISHER_PARAPHRASES_FOR_DISPLAY_ONLY',
            'reviewer_agent': '/root/repo_workflow_merger_audit',
            'provider': 'OpenAI',
            'runtime': 'ChatGPT native subagent (model identity not externally attested)',
            'review_independence': 'SEPARATE_MODEL_AGENT_FROM_CANDIDATE_AND_RELEASE_AUTHORS',
            'review_request_sha256': release._sha(release._render(cls.request)),
            'reviewed_on_utc': '2026-11-03',
            'reviewed_source_tuples': [list(row) for row in release._expected_source_tuples(cls.request)],
            'reviewed_paraphrase_count': 18,
            'passed_paraphrase_count': 18,
            'failed_paraphrase_count': 0,
            'review_method': 'SIMULATED_IN_UNIT_TEST_ONLY_NOT_A_PRODUCTION_REVIEW',
            'limitations': ['Unit test fixture; not real independent review'],
            'coverage_effect': 'NONE',
            'source_work_admission_effect': 'NONE',
            'artwork_release_effect': 'NONE',
        }

    def _receipt_fixture(self, fn):
        original_read = release._read

        def read(path):
            if path == release.REVIEW_PATH:
                return release._render(self.receipt)
            return original_read(path)

        with mock.patch.object(release, '_read', side_effect=read):
            return fn()

    def test_default_missing_editorial_receipt_fails_closed(self):
        with self.assertRaises((OSError, release.ReleaseError, release.CandidateError)):
            release._load(release.REVIEW_PATH)

    def test_simulated_complete_receipt_maps_18_unadmitted_candidates(self):
        result = self._receipt_fixture(lambda: release.release(self.request, self.receipt))
        self.assertEqual(result['candidate_count'], 18)
        self.assertEqual(result['source_local_correction_sha256'], self.request['source_local_correction_sha256'])
        self.assertEqual(result['directory_snapshot_rows_unchanged'], 1214)
        self.assertTrue(result['separate_from_directory'])
        self.assertEqual(result['admission_effect'], 'NONE')
        self.assertEqual(result['coverage_effect'], 'NONE')
        for c in result['candidates']:
            self.assertTrue(c['row_id'].startswith('candidate:literature:'))
            self.assertEqual(c['identity_status'], 'SOURCE_LOCAL_UNRECONCILED')
            self.assertIsNone(c['accepted_directory_row_id'])
            self.assertIsNone(c['raw_webpage_sha256'])
            self.assertEqual(c['artwork_release_effect'], 'NONE')
        self.assertEqual(sum(c['source_correction_path'] is not None for c in result['candidates']), 2)

    def test_self_review_or_bad_source_tuple_rejected(self):
        for make_change in (
            lambda d: d.update(reviewer_agent='/root/literary_editorial'),
            lambda d: d.update(review_result='PENDING'),
            lambda d: d.update(review_request_sha256='a' * 64),
            lambda d: d['reviewed_source_tuples'][0].__setitem__(2, 'b' * 64),
            lambda d: d.update(reviewed_paraphrase_count=17),
            lambda d: d.update(artwork_release_effect='RELEASED'),
        ):
            tampered = copy.deepcopy(self.receipt)
            make_change(tampered)
            with self.assertRaises(release.ReleaseError):
                self._receipt_fixture(lambda: release.verify_receipt(self.request, tampered))


if __name__ == '__main__':
    unittest.main()
