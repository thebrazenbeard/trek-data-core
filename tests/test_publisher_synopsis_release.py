"""Adversarial exact-source review and publisher synopsis display gates."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('publisher_synopsis_builder', ROOT / 'tools' / 'build_publisher_synopsis_release.py')
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class PublisherSynopsisReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = builder.candidate_entries()
        cls.request = builder.review_request(cls.candidates)

    def test_exact_23_qualified_source_local_publisher_descriptions(self):
        rows = self.candidates
        self.assertEqual(len(rows), 23)
        self.assertEqual(sum(x['medium'] == 'LITERATURE' for x in rows), 9)
        self.assertEqual(sum(x['medium'] == 'FILM' for x in rows), 14)
        self.assertEqual(len(set(x['row_id'] for x in rows)), 23)
        self.assertTrue(all(x['raw_webpage_sha256'] is None and x['coverage_effect'] == 'NONE' and
                            x['admission_effect'] == 'NONE' for x in rows))
        self.assertTrue(all(x['overview_basis'] == 'PUBLISHER_DESCRIPTION_PARAPHRASE' for x in rows))
        self.assertEqual({x['source_snapshot_date'] for x in rows}, {'2026-11-03'})

    def test_exact_ebook_to_paperback_crosswalk_must_be_visible_not_silent(self):
        by_id = {x['candidate_work_id']: x for x in self.candidates}
        expected = {
            'proposed-lit-picard-second-self': ('9781982194833', '9781982194840'),
            'proposed-lit-snw-high-country': ('9781668002391', '9781668002407'),
            'proposed-lit-discovery-enterprise-war': ('9781982113315', '9781982113322'),
        }
        for candidate, (row_isbn, evidence_isbn) in expected.items():
            entry = by_id[candidate]
            self.assertTrue(entry['source_locator'].endswith(row_isbn))
            self.assertTrue(entry['overview_evidence_locator'].endswith(evidence_isbn))
            self.assertIn(row_isbn, entry['edition_crosswalk'])
            self.assertIn(evidence_isbn, entry['edition_crosswalk'])
        self.assertEqual(sum(x['source_locator'] != x['overview_evidence_locator'] for x in self.candidates), 3)

    def test_film_source_local_alias_is_exactly_the_same_source_observation(self):
        for entry in self.candidates:
            if entry['medium'] == 'FILM':
                self.assertEqual(entry['directory_alias_row_id'], 'directory:' + entry['row_id'])
                self.assertEqual(entry['directory_alias_context'], 'Star Trek films')
                self.assertEqual(entry['source_input'], 'explorer/film-catalog.json')
                self.assertEqual(entry['overview_evidence_locator'], entry['source_locator'])
            else:
                self.assertIsNone(entry['directory_alias_row_id'])
                self.assertIsNone(entry['directory_alias_context'])

    def test_accepted_local_observations_not_imaginary_html_hashes(self):
        for entry in self.candidates:
            self.assertEqual(entry['research_observation_sha256'], builder._digest(builder._raw(entry['research_observation_path'])))
            self.assertIsNone(entry['raw_webpage_sha256'])

    def test_conflicting_duplicate_publication_effect_keys_are_rejected(self):
        # This is a deliberately small producer artifact; validation must
        # reject its ambiguous serialization before reading any semantic keys.
        forged = (b'{"proposal_only":true,"observed_on_utc":"2026-11-03",'
                  b'"source_bound":false,"accepted_coverage_effect":"CLOSE_READ",'
                  b'"accepted_coverage_effect":"NONE","accepted_evidence_effect":"NONE"}')
        with mock.patch.object(builder, '_raw', return_value=forged):
            with self.assertRaisesRegex(builder.ReleaseError, 'Duplicate JSON key'):
                builder._source_artifact('forged.json')

        nested = b'{"receipt":{"coverage_effect":"AUDITED","coverage_effect":"NONE"}}'
        with mock.patch.object(builder, '_raw', return_value=nested):
            with self.assertRaisesRegex(builder.ReleaseError, 'Duplicate JSON key'):
                builder._load('forged.json')

    def test_cross_edition_source_change_or_wrong_work_family_rejected(self):
        original_source = builder._source_artifact

        def tampered(path):
            data, sha = original_source(path)
            if 'lit-three-publisher-editions' in path:
                data = copy.deepcopy(data)
                row = next(x for x in data['work_synopses'] if x['candidate_work_id'] == 'proposed-lit-picard-second-self')
                row['source_locator'] = 'https://www.simonandschuster.com/books/Other-Book/Author/Other-Series/9781982194840'
            return data, sha

        with mock.patch.object(builder, '_source_artifact', side_effect=tampered):
            with self.assertRaisesRegex(builder.ReleaseError, 'paired source|title family'):
                builder.candidate_entries()

    def test_swapped_film_directory_url_and_alias_context_rejected(self):
        original_load = builder._load

        def tamper(path):
            data = original_load(path)
            if path == 'explorer/discovery-catalog.json':
                data = copy.deepcopy(data)
                row = next(x for x in data['rows'] if x['row_id'] == 'film:film-search-for-spock')
                row['context'] = 'Forged Work category'
            return data

        with mock.patch.object(builder, '_load', side_effect=tamper):
            with self.assertRaisesRegex(builder.ReleaseError, 'source observation'):
                builder.candidate_entries()

    def test_self_declared_review_or_wrong_exact_request_digest_rejected(self):
        receipt = builder._load(builder.REVIEW_PATH)
        for change in (
            lambda x: x.update(review_result='PENDING'),
            lambda x: x.update(review_request_sha256='a' * 64),
            lambda x: x.update(reviewed_paraphrase_count=1),
            lambda x: x.update(reviewer_agent='/root/live_index_integrator'),
            lambda x: x.update(provider='UNKNOWN'),
            lambda x: x.update(accepted_observation_commit='a' * 40),
            lambda x: x['source_artifacts'][0].update(sha256='a' * 64),
            lambda x: x['source_artifacts'][0].update(reviewed_paraphrases=1),
            lambda x: x['reviewed_paraphrases'][0].__setitem__(1, 'a' * 64),
        ):
            fake = copy.deepcopy(receipt)
            change(fake)
            with self.assertRaises(builder.ReleaseError):
                builder.public_release(self.candidates, fake, self.request)

    def test_public_sidecar_and_review_request_exactly_rebuild(self):
        self.assertEqual(builder._raw(builder.REQUEST_PATH), builder._pretty(self.request))
        public = builder.public_release(self.candidates, builder._load(builder.REVIEW_PATH), self.request)
        self.assertEqual(builder._raw(builder.PUBLIC_PATH), builder._pretty(public))
        self.assertEqual(public['synopsis_count'], 23)
        self.assertEqual(len({x['editorial_receipt_sha256'] for x in public['synopses']}), 1)


if __name__ == '__main__':
    unittest.main()
