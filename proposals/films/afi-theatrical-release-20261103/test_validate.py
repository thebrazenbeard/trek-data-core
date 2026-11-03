"""Adversarial checks for source-local film metadata not becoming accepted truth."""

import copy
import importlib.util
import json
import pathlib
import unittest


HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("afi_film_validator", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class FilmAFIProposalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proposal = json.loads(validator.OBSERVATIONS.read_text(encoding="utf-8"))
        cls.discovery = json.loads(validator.DISCOVERY_FILMS.read_text(encoding="utf-8"))

    def test_valid_source_local_tranche(self):
        self.assertEqual(validator.validate(self.proposal, self.discovery), 5)

    def test_cannot_promote_coverage(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["coverage_effect"] = "CLOSE_READ"
        with self.assertRaisesRegex(ValueError, "invalid coverage_effect"):
            validator.validate(proposal, self.discovery)

    def test_cannot_claim_artwork_rights(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["records"][0]["artwork_rights"] = "PUBLIC_DISPLAY_PERMISSION_VERIFIED"
        with self.assertRaisesRegex(ValueError, "no art rights granted"):
            validator.validate(proposal, self.discovery)

    def test_cannot_reconcile_global_identity(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["records"][0]["crosswalk_status"] = "ACCEPTED_SAME_AS"
        with self.assertRaisesRegex(ValueError, "must remain unadmitted"):
            validator.validate(proposal, self.discovery)

    def test_cannot_misattribute_date(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["records"][2]["assertion"]["value"] = "1982-06-01"
        with self.assertRaisesRegex(ValueError, "normalized date differs"):
            validator.validate(proposal, self.discovery)

    def test_cannot_swap_work_or_publisher(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["records"][1]["candidate_work_ref"] = "film-search-for-spock"
        with self.assertRaisesRegex(ValueError, "candidate film mismatch"):
            validator.validate(proposal, self.discovery)
        proposal = copy.deepcopy(self.proposal)
        proposal["records"][1]["source"]["locator"] = "https://startrek.com/Film/67066"
        with self.assertRaisesRegex(ValueError, "invalid AFI locator"):
            validator.validate(proposal, self.discovery)

    def test_rejects_unverified_raw_snapshot_hash(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["records"][0]["source"]["raw_page_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "no raw page snapshot"):
            validator.validate(proposal, self.discovery)


if __name__ == "__main__":
    unittest.main()
