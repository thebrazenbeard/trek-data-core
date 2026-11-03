"""Regression gates for the append-only, strict literary modal supersession."""

import copy
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
SPEC = importlib.util.spec_from_file_location('lit_modal_correction', ROOT / 'tools/build_lit_modal_corrected_request.py')
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class ModalCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = builder.build_legacy()
        cls.corrected = builder.build()

    def test_exact_v2_output_and_legacy_immutability(self):
        self.assertEqual(builder._read(builder.OUTPUT), builder._render(self.corrected))
        self.assertEqual(builder._read(builder.LEGACY_OUTPUT), builder._render(self.original))
        self.assertEqual(self.corrected['corrected_paraphrase_count'], 2)
        self.assertEqual(self.corrected['public_site_effect'], 'NONE')
        self.assertEqual(self.corrected['source_work_evidence_admission_effect'], 'NONE')
        self.assertEqual(len(self.corrected['candidates']), 18)

    def test_only_two_exact_source_local_claims_superseded(self):
        old = {row['candidate_work_id']: row for row in self.original['candidates']}
        new = {row['candidate_work_id']: row for row in self.corrected['candidates']}
        self.assertEqual(old.keys(), new.keys())
        changed = {k for k in old if old[k]['original_paraphrase_sha256'] != new[k]['original_paraphrase_sha256']}
        self.assertEqual(changed, set(builder.TARGETS))
        self.assertEqual(sum(row['display_supersession_source'] == builder.CORRECTIONS
                             for row in new.values()), 2)

    def _tampered(self, change):
        original = builder._json

        def read(path):
            result = original(path)
            if path == builder.CORRECTIONS:
                result = copy.deepcopy(result)
                change(result)
            return result

        with mock.patch.object(builder, '_json', side_effect=read):
            with self.assertRaises(builder.CandidateError):
                builder.build()

    def test_source_sha_and_prior_text_rebinding_rejected(self):
        self._tampered(lambda d: d.update(supersedes_source_sha256='0' * 64))
        self._tampered(lambda d: d['corrections'][0].update(prior_paraphrase_sha256='0' * 64))
        self._tampered(lambda d: d['corrections'][0].update(publisher_edition_isbn13='9781668046364'))

    def test_missing_duplicate_or_extra_corrections_rejected(self):
        self._tampered(lambda d: d['corrections'].__setitem__(1, copy.deepcopy(d['corrections'][0])))
        self._tampered(lambda d: d['corrections'].pop())
        self._tampered(lambda d: d['corrections'][0].update(unreviewed_claim=True))

    def test_modal_regressions_private_paths_and_html_rejected(self):
        self._tampered(lambda d: d['corrections'][0].update(replacement_paraphrase='A publisher claim draws them into new danger.' * 4))
        self._tampered(lambda d: d['corrections'][1].update(replacement_paraphrase='Seven considers joining the Rangers.' * 4))
        self._tampered(lambda d: d['corrections'][0].update(replacement_paraphrase='C:\\Users\\owner\\secret ' * 5))
        self._tampered(lambda d: d['corrections'][1].update(replacement_paraphrase='<script>bad</script>' * 5))

    def test_accepted_strict_source_contract_still_enforced(self):
        source_reader = builder.build_legacy
        with mock.patch.object(builder, 'build_legacy', side_effect=builder.CandidateError('strict source contract')):
            with self.assertRaisesRegex(builder.CandidateError, 'strict source contract'):
                builder.build()
        self.assertEqual(builder.build_legacy, source_reader)


if __name__ == '__main__':
    unittest.main()
