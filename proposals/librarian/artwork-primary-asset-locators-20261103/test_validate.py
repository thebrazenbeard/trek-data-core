"""Mutation tests for artwork hold and exact edition/card crosswalks."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate import _read_json, errors


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

    def test_two_film_work_page_bindings_swapped_but_image_hashes_unchanged_fails(self):
        # Regression: accepted-main validator used to return [] here. Both work
        # IDs and page URLs still matched film-catalog; the unordered ID census
        # and unchanged per-local-ID image hashes concealed the crossed wires.
        def swap(d):
            a, b = d["observations"][:2]
            for field in ("source_local_work_id", "publisher_source_url"):
                a[field], b[field] = b[field], a[field]
        self.mutated(swap)

    def test_same_source_family_different_film_page_fails(self):
        self.mutated(lambda d: d["observations"][0].update(
            publisher_source_url=ORIGINAL["observations"][1]["publisher_source_url"]))

    def test_same_family_episode_input_swap_fails(self):
        self.mutated(lambda d: d["observations"][6].update(
            source_input=ORIGINAL["observations"][8]["source_input"]))

    def test_source_input_path_and_digest_substitution_fails(self):
        # An existing JSON source with its true matching digest must not be
        # admitted as the original reviewed source merely by recomputing SHA.
        def substitute(d):
            original = d["source_inputs"][0]
            original["path"] = "proposals/librarian/artwork-primary-asset-locators-20261103/records.json"
            import hashlib
            original["sha256"] = hashlib.sha256((Path(__file__).parent / "records.json").read_bytes()).hexdigest()
        self.mutated(substitute)

    def test_known_source_digest_forgery_fails_even_if_path_exists(self):
        self.mutated(lambda d: d["source_inputs"][2].update(sha256="f" * 64))

    def test_root_rights_escalation_new_field_fails(self):
        self.mutated(lambda d: d.update(rights_to_republish_images=True))

    def test_per_observation_new_license_claim_fails(self):
        self.mutated(lambda d: d["observations"][0].update(public_image_license="CLEARED"))

    def test_per_observation_new_public_url_claim_fails(self):
        self.mutated(lambda d: d["observations"][0].update(public_image_url=d["observations"][0]["image_locator"]))

    def test_per_observation_new_full_text_claim_fails(self):
        self.mutated(lambda d: d["observations"][6].update(episode_full_text_available=True))

    def test_source_worker_reported_receipt_must_not_claim_extra_rights(self):
        self.mutated(lambda d: d["observations"][0].update(locator_evidence="Rights holder cleared all public reuse"))
        self.mutated(lambda d: d["observations"][1].update(locator_evidence="SOURCE_BYTES_VERIFIED"))

    def test_secondary_crosswalk_cannot_claim_independent_license(self):
        self.mutated(lambda d: d["observations"][0].update(secondary_crosswalk="Rights independently certified"))
        self.mutated(lambda d: d["observations"][2].update(secondary_crosswalk={"licensed": True}))

    def test_unknown_source_input_evidence_field_fails(self):
        self.mutated(lambda d: d["source_inputs"][0].update(full_text_verified=True))

    def test_duplicate_json_key_rejected_during_load(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "dup.json"
            path.write_text('{"rights_assessment":"NO_PUBLIC_DISPLAY_LICENSE_ESTABLISHED","rights_assessment":"CLEARED"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                _read_json(path)

    def test_wrong_edition_fails(self):
        self.mutated(lambda d: d["observations"][3].update(source_local_work_id=d["observations"][4]["source_local_work_id"]))

    def test_untrusted_image_host_fails(self):
        self.mutated(lambda d: d["observations"][0].update(image_locator="https://evil.example/pixel.jpg"))

    def test_same_allowed_host_other_film_image_fails(self):
        self.mutated(lambda d: d["observations"][0].update(image_locator="https://images.prismic.io/star-trek-untold/not-wrath-of-khan.png?auto=compress,format"))

    def test_same_allowed_host_other_film_row_swap_fails(self):
        self.mutated(lambda d: d["observations"][1].update(image_locator=d["observations"][0]["image_locator"]))

    def test_same_isbn_fake_publisher_cover_fails(self):
        self.mutated(lambda d: d["observations"][3].update(image_locator="https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr9780743419987/not-the-linked-book-9780743419987_hr.jpg"))

    def test_same_edition_other_cdn_path_fails(self):
        self.mutated(lambda d: d["observations"][5].update(image_locator="https://d28hgpri8am2if.cloudfront.net/book_images/cvr9780743546591_fake_9780743546591_hr.jpg"))

    def test_embedded_userinfo_fails(self):
        self.mutated(lambda d: d["observations"][0].update(image_locator="https://user@images.prismic.io/pixel.jpg"))

    def test_duplicate_ids_fails(self):
        self.mutated(lambda d: d["observations"][1].update(local_id=d["observations"][0]["local_id"]))

    def test_hidden_newline_fails(self):
        self.mutated(lambda d: d["observations"][0].update(image_locator="https://images.prismic.io/abc\npixel.jpg"))

    def test_optimized_interpreter_keeps_exact_provenance_gate(self):
        source = '''
import copy, json, pathlib, sys
sys.path.insert(0, sys.argv[1])
from validate import errors
base = json.loads((pathlib.Path(sys.argv[1]) / "records.json").read_text(encoding="utf-8"))
mutant = copy.deepcopy(base)
a, b = mutant["observations"][:2]
for field in ("source_local_work_id", "publisher_source_url"):
    a[field], b[field] = b[field], a[field]
if not errors(mutant):
    raise SystemExit("optimized validator accepted crossed film identity")
mutant = copy.deepcopy(base)
mutant["source_inputs"][0]["path"] = "explorer/discovery-catalog.json"
if not errors(mutant):
    raise SystemExit("optimized validator accepted source path substitution")
for target, index, field, value in (
    ("root", 0, "rights_to_republish_images", True),
    ("row", 0, "public_image_license", "CLEARED"),
    ("row", 0, "public_image_url", base["observations"][0]["image_locator"]),
    ("row", 6, "episode_full_text_available", True),
    ("row", 0, "locator_evidence", "Rights holder cleared all public reuse"),
    ("row", 1, "locator_evidence", "SOURCE_BYTES_VERIFIED"),
    ("row", 0, "secondary_crosswalk", "Rights independently certified"),
):
    mutant = copy.deepcopy(base)
    obj = mutant if target == "root" else mutant["observations"][index]
    obj[field] = value
    if not errors(mutant):
        raise SystemExit("optimized validator accepted rights/provenance spoof " + field)
'''
        result = subprocess.run([sys.executable, "-O", "-c", source, str(Path(__file__).parent)],
                                check=False, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
