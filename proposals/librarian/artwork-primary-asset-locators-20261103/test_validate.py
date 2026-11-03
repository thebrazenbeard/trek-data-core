"""Mutation tests for artwork hold and exact edition/card crosswalks."""
import copy
import json
import unittest
from pathlib import Path

from validate import errors


ORIGINAL = json.loads((Path(__file__).parent / "records.json").read_text(encoding="utf-8"))


class ArtworkPacketTest(unittest.TestCase):
    def test_original(self):
        self.assertEqual(errors(ORIGINAL), [])

    def mutated(self, mutate):
        packet = copy.deepcopy(ORIGINAL)
        mutate(packet)
        self.assertNotEqual(errors(packet), [], "mutation escaped invariant checks")

    def test_rights_release_fails(self):
        self.mutated(lambda d: d["observations"][0].update(rights_status="CLEARED"))

    def test_display_flag_fails(self):
        self.mutated(lambda d: d["observations"][0].update(display_eligible=True))

    def test_explorer_effect_fails(self):
        self.mutated(lambda d: d.update(explorer_effect="PUBLISHED"))

    def test_claimed_image_retrieval_fails(self):
        self.mutated(lambda d: d.update(image_bytes_retrieved=True))

    def test_tampered_accepted_source_digest_fails(self):
        self.mutated(lambda d: d["source_inputs"][0].update(sha256="0" * 64))

    def test_card_swapping_fails(self):
        self.mutated(lambda d: d["observations"][6].update(image_locator=d["observations"][7]["image_locator"]))

    def test_wrong_film_binding_fails(self):
        self.mutated(lambda d: d["observations"][0].update(source_local_work_id="film-search-for-spock"))

    def test_wrong_edition_fails(self):
        self.mutated(lambda d: d["observations"][3].update(source_local_work_id=d["observations"][4]["source_local_work_id"]))

    def test_untrusted_image_host_fails(self):
        self.mutated(lambda d: d["observations"][0].update(image_locator="https://evil.example/pixel.jpg"))

    def test_embedded_userinfo_fails(self):
        self.mutated(lambda d: d["observations"][0].update(image_locator="https://user@images.prismic.io/pixel.jpg"))

    def test_duplicate_ids_fails(self):
        self.mutated(lambda d: d["observations"][1].update(local_id=d["observations"][0]["local_id"]))

    def test_hidden_newline_fails(self):
        self.mutated(lambda d: d["observations"][0].update(image_locator="https://images.prismic.io/abc\npixel.jpg"))


if __name__ == "__main__":
    unittest.main()
