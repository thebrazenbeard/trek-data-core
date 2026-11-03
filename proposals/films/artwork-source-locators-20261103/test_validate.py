import copy
import importlib.util
import json
import pathlib
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
        self.reject(lambda d: d["records"][4].update(source_locator="https://memory-alpha.fandom.com/wiki/File:Poster_example.jpg"), "unsupported Fandom locator")
        self.reject(lambda d: d["records"][4].update(access="FANDOM_FILE_PAGE_READ"), "Fandom direct-access claim")

    def test_no_source_work_confusion(self):
        self.reject(lambda d: d["records"][2].update(candidate_film_id="film-search-for-spock"), "source linked to wrong film")
        self.reject(lambda d: d["records"][5].update(candidate_film_id="film-voyage-home"), "indexed category mapped to wrong film")

    def test_no_gallery_falsely_certified_as_image(self):
        self.reject(lambda d: d["records"][3].update(artwork_kind="RIGHTS_CLEARED_STILL"), "gallery evidence mismatch")

    def test_no_unverified_media_urls_or_page_hashes(self):
        self.reject(lambda d: d["records"][0].update(image_url="https://cdn.example/poster.jpg"), "unexpected or missing keys")
        self.reject(lambda d: d.update(source_page_snapshots_available=True), "unsupported source snapshot claim")

    def test_no_third_party_host_substitution(self):
        self.reject(lambda d: d["records"][0].update(source_locator="https://images.prismic.io/mystery.jpg"), "unverified publisher path")


if __name__ == "__main__":
    unittest.main()
