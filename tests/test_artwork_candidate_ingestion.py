"""Adversarial held-only tests; no remote URL requests or image downloads."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/build_artwork_candidate_intake.py"
SPEC = importlib.util.spec_from_file_location("artwork_candidate_intake", SCRIPT)
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class ArtworkCandidateIngestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = gate.build()

    def test_real_source_receipts_and_no_release(self):
        gate.validate(self.packet)
        self.assertEqual(self.packet["candidate_count"], 10)
        self.assertEqual(self.packet["medium_counts"], {"EPISODE": 4, "FILM": 3, "LITERATURE": 3})
        self.assertEqual(self.packet["public_release_candidate_ids"], [])
        self.assertEqual(self.packet["reviewed_public_image_count"], 0)
        self.assertTrue(all(not item["public_display_eligible"] and not item["rehost_eligible"]
                            for item in self.packet["candidates"]))

    def test_checked_in_packet_equals_deterministic_source_derivation(self):
        packet = gate._strict_json((ROOT / gate.OUTPUT).read_bytes())
        gate.validate(packet)
        self.assertEqual(packet, self.packet)

    def _reject(self, mutation):
        packet = copy.deepcopy(self.packet)
        mutation(packet)
        with self.assertRaises(gate.IntakeRejected):
            gate.validate(packet)

    def test_no_license_self_promotion(self):
        self._reject(lambda p: p["candidates"][0]["rights"].update(rights_class="PUBLIC_DISPLAY_PERMISSION_VERIFIED"))

    def test_no_forged_permission_receipt(self):
        self._reject(lambda p: p["candidates"][0]["rights"].update(permission_receipt_sha256="a" * 64))

    def test_no_claim_of_independent_rights_reviewer(self):
        self._reject(lambda p: p["candidates"][0]["rights"].update(rights_reviewer="Imaginary Rights Owner"))

    def test_no_auto_public_display_on_license_guess(self):
        self._reject(lambda p: p["candidates"][0].update(public_display_eligible=True))

    def test_no_self_hosted_binary_path(self):
        self._reject(lambda p: p["candidates"][0].update(public_image_path="./licensed-artwork/guess.jpg"))

    def test_no_rehost_rights_from_publisher_url(self):
        self._reject(lambda p: p["candidates"][1].update(rehost_eligible=True))

    def test_no_episode_image_swap(self):
        def swap(p):
            episode = [i for i, row in enumerate(p["candidates"]) if row["medium"] == "EPISODE"]
            p["candidates"][episode[0]]["image_url_observed"] = p["candidates"][episode[1]]["image_url_observed"]
        self._reject(swap)

    def test_no_film_header_as_poster(self):
        self._reject(lambda p: next(item for item in p["candidates"] if item["medium"] == "FILM")
                     .update(image_kind_observed="LICENSED_THEATRICAL_POSTER"))

    def test_no_audio_edition_as_print_cover(self):
        self._reject(lambda p: next(item for item in p["candidates"]
                                    if "AUDIO" in item["image_kind_observed"])
                     .update(image_kind_observed="PUBLISHER_BOOK_JACKET"))

    def test_no_work_admission_by_renaming_scope(self):
        self._reject(lambda p: p["candidates"][0].update(identity_scope="ACCEPTED_GLOBAL_WORK"))

    def test_no_false_release_numerator(self):
        self._reject(lambda p: p.update(reviewed_public_image_count=10))

    def test_no_extra_candidate_record(self):
        self._reject(lambda p: p["candidates"].append(copy.deepcopy(p["candidates"][0])))

    def test_no_source_receipt_substitution(self):
        self._reject(lambda p: p["candidates"][0]["source_receipt"].update(locator_evidence_sha256="f" * 64))

    def test_no_metadata_driven_external_source_path(self):
        self._reject(lambda p: p["candidates"][0]["source_receipt"].update(source_input_path="../../private-books.zip"))

    def test_no_hidden_payload_fields(self):
        self._reject(lambda p: p["candidates"][0].update(base64_image="data:image/png;base64,fake"))

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(gate.IntakeRejected):
            gate._strict_json(b'{"candidate_count":10,"candidate_count":100}')

    def test_nonfinite_json_rejected(self):
        with self.assertRaises(gate.IntakeRejected):
            gate._strict_json(b'{"x": NaN}')

    def test_changed_source_byte_digest_rejected(self):
        original = gate._checked_file
        def mutate(root, relative):
            raw = original(root, relative)
            if relative == gate.SOURCE:
                return raw + b" "
            return raw
        with mock.patch.object(gate, "_checked_file", side_effect=mutate):
            with self.assertRaises(gate.IntakeRejected):
                gate.build()


if __name__ == "__main__":
    unittest.main()
