"""Failure-mode tests for the proposal-only literary synopsis expansion request."""

import copy
import importlib.util
import json
import subprocess
import sys
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

    def test_invalid_isbn_checksum_rejected_even_if_url_suffix_matches(self):
        with self.assertRaisesRegex(builder.CandidateError, 'checksum'):
            builder._official_url('https://www.simonandschuster.com/books/Example/9780000000000', '9780000000000')

    def test_every_source_candidate_schema_rejects_private_text_and_rights_keys(self):
        for source in builder.INPUTS:
            raw = builder._json(source)['candidate_works'][0]
            digest = builder._sha(builder._read(source))
            for forbidden, value in (
                ('private_host_path', r'C:\Users\Example\OneDrive\Books\book.epub'),
                ('full_book_text', 'Copyrighted source chapter ' * 250),
                ('rights_to_republish_cover', 'GRANTED'),
                ('image_url', 'https://example.invalid/cover.jpg'),
            ):
                with self.subTest(source=source, forbidden=forbidden):
                    amended = copy.deepcopy(raw)
                    amended[forbidden] = value
                    with self.assertRaisesRegex(builder.CandidateError, 'publisher candidate'):
                        builder._candidate(amended, source, digest)

    def test_each_source_packet_root_rejects_extra_private_or_rights_field(self):
        original = builder._json
        for source in builder.INPUTS:
            for field in ('private_host_path', 'full_book_text', 'rights_to_republish_cover'):
                def tampered(path, source=source, field=field):
                    data = original(path)
                    if path == source:
                        data = copy.deepcopy(data)
                        data[field] = 'GRANTED' if field.startswith('rights_') else '/private/ebook.epub'
                    return data

                with self.subTest(source=source, field=field):
                    with mock.patch.object(builder, '_json', side_effect=tampered):
                        with self.assertRaisesRegex(builder.CandidateError, 'publisher source packet'):
                            builder.build()

    def test_duplicate_json_keys_fail_closed(self):
        with self.assertRaisesRegex(builder.CandidateError, 'Duplicate JSON'):
            json.loads('{"private_host_path":"a","private_host_path":"b"}',
                       object_pairs_hook=builder._distinct_json_fields)

    def test_private_source_path_or_rights_claim_hidden_inside_synopsis_rejected(self):
        source = builder.INPUTS[0]
        raw = builder._json(source)['candidate_works'][0]
        digest = builder._sha(builder._read(source))
        for injection in (r' C:\Users\Example\Private\book.epub',
                          ' rights_to_republish_cover=GRANTED', ' full_book_text=CHAPTER1'):
            with self.subTest(injection=injection):
                altered = copy.deepcopy(raw)
                altered['synopsis'] += injection
                with self.assertRaisesRegex(builder.CandidateError, 'Unsuitable source-relative synopsis'):
                    builder._candidate(altered, source, digest)

    def test_source_packet_cannot_invent_higher_evidence_tier(self):
        original = builder._json
        def tampered(path):
            obj = original(path)
            if path == builder.INPUTS[0]:
                obj = copy.deepcopy(obj)
                obj['verification_class'] = 'AUTHENTICATED_FULL_BOOK_READ'
            return obj
        with mock.patch.object(builder, '_json', side_effect=tampered):
            with self.assertRaisesRegex(builder.CandidateError, 'reader or evidence tier'):
                builder.build()

    def test_optimized_mode_rejects_mutant_candidates_and_root_packets(self):
        script = (
            'import importlib.util,copy\n'
            f'p={str(ROOT / "tools" / "build_lit_overview_expansion_request.py")!r}\n'
            's=importlib.util.spec_from_file_location("lit_gate",p)\n'
            'm=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n'
            'a=m._json(m.INPUTS[0]);r=copy.deepcopy(a["candidate_works"][0])\n'
            'r["full_book_text"]="copyrighted chapter"*500\n'
            'm._candidate(r,m.INPUTS[0],"0"*64)\n'
        )
        result = subprocess.run([sys.executable, '-O', '-c', script], cwd=ROOT,
                                capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('CandidateError: Unexpected or missing publisher candidate fields', result.stderr)

        root_script = (
            'import importlib.util,copy\n'
            f'p={str(ROOT / "tools" / "build_lit_overview_expansion_request.py")!r}\n'
            's=importlib.util.spec_from_file_location("lit_gate",p)\n'
            'm=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n'
            'old=m._json\n'
            'def mutated(path):\n'
            ' d=old(path)\n'
            ' if path==m.INPUTS[0]:\n'
            '  d=copy.deepcopy(d);d["private_host_path"]="/private/book.epub"\n'
            ' return d\n'
            'm._json=mutated\n'
            'm.build()\n'
        )
        result = subprocess.run([sys.executable, '-O', '-c', root_script], cwd=ROOT,
                                capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('CandidateError: Unexpected or missing publisher source packet fields', result.stderr)

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

    def test_committed_review_request_exactly_rebuilds(self):
        self.assertEqual(builder._read(builder.OUTPUT), builder._render(self.request))


if __name__ == '__main__':
    unittest.main()
