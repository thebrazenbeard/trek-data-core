import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest


HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("film_artwork_proposal_validator", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class FilmArtworkProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(validator.RECORDS.read_text(encoding="utf-8"))
        cls.films = json.loads(validator.FILM_DISCOVERY.read_text(encoding="utf-8"))

    def reject(self, transform, fragment):
        candidate = copy.deepcopy(self.good)
        transform(candidate)
        with self.assertRaisesRegex(ValueError, fragment):
            validator.validate(candidate, self.films)

    def test_valid_bounded_proposal(self):
        self.assertEqual(validator.validate(self.good, self.films), 7)

    def test_no_artwork_display_or_rights_promotion(self):
        self.reject(lambda d: d["records"][0].update(display_eligible=True), "unauthorized image display")
        self.reject(lambda d: d["records"][0].update(rights_status="PUBLIC_DISPLAY_PERMISSION_VERIFIED"), "rights gate bypass")

    def test_no_corpus_coverage_or_admission(self):
        self.reject(lambda d: d.update(coverage_effect="SOURCE_BOUND"), "coverage_effect")
        self.reject(lambda d: d.update(admission_effect="ACCEPTED"), "admission_effect")

    def test_no_invented_direct_fandom_file_page(self):
        self.reject(lambda d: d["records"][4].update(source_locator="https://memory-alpha.fandom.com/wiki/File:Poster_example.jpg"), "reviewed source observation")
        self.reject(lambda d: d["records"][4].update(access="FANDOM_FILE_PAGE_READ"), "reviewed source observation")

    def test_no_source_work_confusion(self):
        self.reject(lambda d: d["records"][2].update(candidate_film_id="film-search-for-spock"), "reviewed source observation")
        self.reject(lambda d: d["records"][5].update(candidate_film_id="film-voyage-home"), "reviewed source observation")

    def test_no_gallery_falsely_certified_as_image(self):
        self.reject(lambda d: d["records"][3].update(artwork_kind="RIGHTS_CLEARED_STILL"), "reviewed source observation")

    def test_no_unverified_media_urls_or_page_hashes(self):
        self.reject(lambda d: d["records"][0].update(image_url="https://cdn.example/poster.jpg"), "unexpected or missing keys")
        self.reject(lambda d: d.update(source_page_snapshots_available=True), "unsupported source snapshot claim")

    def test_no_third_party_host_substitution(self):
        self.reject(lambda d: d["records"][0].update(source_locator="https://images.prismic.io/mystery.jpg"), "reviewed source observation")

    def test_fabricated_fandom_file_title_is_rejected(self):
        self.reject(lambda d: d["records"][4].update(evidence="File:Unverified fabricated fan art.jpg"), "reviewed source observation")

    def test_fabricated_publisher_title_or_license_claim_is_rejected(self):
        self.reject(lambda d: d["records"][0].update(evidence="Poster Art for Star Trek: all assets licensed for reuse"), "reviewed source observation")

    def test_artwork_edition_must_match_the_reviewed_file_title(self):
        self.reject(lambda d: d["records"][5].update(artwork_variant="UNRESOLVED_POSTER_VERSION"), "reviewed source observation")

    def test_lineage_is_bounded_and_cannot_claim_unseen_permission(self):
        self.reject(lambda d: d["source_lineage"].update({"community:memory-alpha.fandom.com": "X" * 1_000_000}), "lineage length")
        self.reject(lambda d: d["source_lineage"].update({"publisher:startrek.com": "Publisher licensed every poster to the public for reuse, the evidence is certain."}), "unreviewed or misleading source lineage")

    def test_accepted_main_sha_cannot_be_forged(self):
        self.reject(lambda d: d.update(baseline_accepted_main="0" * 40), "unreviewed baseline identity")

    def test_optimized_mode_still_rejects_hostile_substitution(self):
        # Not an assert-based gate: prove the real validator fails closed with
        # Python -O, under which `assert` statements would be erased.
        script = """
import copy
import json
import sys
sys.path.insert(0, sys.argv[1])
import validate as v
original = json.loads(v.RECORDS.read_text(encoding='utf-8'))
films = json.loads(v.FILM_DISCOVERY.read_text(encoding='utf-8'))
mutations = (
    ('evidence', 4, 'File:Unverified fabricated fan art.jpg'),
    ('evidence', 0, 'Poster Art for Star Trek: all assets licensed for reuse'),
    ('artwork_variant', 5, 'UNRESOLVED_POSTER_VERSION'),
)
for field, index, replacement in mutations:
    candidate = copy.deepcopy(original)
    candidate['records'][index][field] = replacement
    try:
        v.validate(candidate, films)
    except ValueError:
        continue
    raise SystemExit('optimized validator accepted forged ' + field)
for field, replacement in (
    ('baseline_accepted_main', '0' * 40),
    ('source_lineage', {'publisher:startrek.com': 'X' * 1000000,
                        'community:memory-alpha.fandom.com': 'X' * 1000000}),
):
    candidate = copy.deepcopy(original)
    candidate[field] = replacement
    try:
        v.validate(candidate, films)
    except ValueError:
        continue
    raise SystemExit('optimized validator accepted forged ' + field)
"""
        result = subprocess.run([sys.executable, "-O", "-c", script, str(HERE)],
                                capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
