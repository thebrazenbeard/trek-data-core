"""Hostile mutation checks for a source-only, unpublished Discovery S1 tranche."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from validate import unique_object, validate, validate_private_source_html

DATA = json.loads(Path(__file__).with_name("records.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)


class DiscoveryPublisherTests(unittest.TestCase):
    def test_good(self):
        self.assertEqual(validate(DATA), 5)

    def reject(self, change):
        data = deepcopy(DATA)
        change(data)
        with self.assertRaises(ValueError):
            validate(data)

    def test_cannot_claim_av_view(self):
        self.reject(lambda d: d.update(audiovisual_episodes_watched=True))

    def test_cannot_admit_work(self):
        self.reject(lambda d: d["works"][0].update(canonical_work_id="canonical:dis:e01"))

    def test_cannot_claim_coverage(self):
        self.reject(lambda d: d.update(coverage_effect="CLOSE_READ"))

    def test_cannot_release_synopsis(self):
        self.reject(lambda d: d.update(explorer_synopsis_release_effect="PUBLISHED"))

    def test_cannot_release_image(self):
        self.reject(lambda d: d["artwork_candidates"][0].update(rights_status="PUBLIC_DOMAIN"))

    def test_cannot_inject_fictional_canon(self):
        self.reject(lambda d: d["evidence"][0].update(observation="The audiovisual episode proves Burnham did not exist."))

    def test_cannot_inject_synopsis(self):
        self.reject(lambda d: d["works"][0].update(original_synopsis="Lore really inhabits this current model."))

    def test_cannot_change_predicate(self):
        self.reject(lambda d: d["assertions"][0].update(predicate="OBJECTIVE_CANON_FACT"))

    def test_cannot_rebind_image(self):
        self.reject(lambda d: d["artwork_candidates"][0].update(url=d["artwork_candidates"][1]["url"]))

    def test_cannot_rebind_source_description_hash(self):
        self.reject(lambda d: d["works"][0].update(publisher_description_sha256=d["works"][1]["publisher_description_sha256"]))

    def test_cannot_reinterpret_release_instant(self):
        self.reject(lambda d: d["works"][0].update(source_datetime="2017-09-25T00:30:00+00:00"))

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"coverage_effect":"NONE","coverage_effect":"CLOSE_READ"}', object_pairs_hook=unique_object)

    def test_private_source_bytes_mismatch(self):
        with self.assertRaises(ValueError):
            validate_private_source_html(DATA, b"not the publisher response")


if __name__ == "__main__":
    unittest.main()
