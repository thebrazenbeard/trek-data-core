#!/usr/bin/env python3
"""Adversarial cross-title metadata tests, including Python -O."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

import validate as v


class FirstPartyGapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = v.load(v.ROOT / "records.json")
        cls.obs = v.load(v.OBS_PATH)
        cls.obs_bytes = v.OBS_PATH.read_bytes()
        cls.prior = v.load(v.PRIOR_PATH)
        cls.prior_bytes = v.PRIOR_PATH.read_bytes()

    def check(self, obj, obs=None, obs_bytes=None, prior=None, prior_bytes=None):
        v.validate(obj, self.obs if obs is None else obs,
                   self.obs_bytes if obs_bytes is None else obs_bytes,
                   self.prior if prior is None else prior,
                   self.prior_bytes if prior_bytes is None else prior_bytes)

    def reject(self, update):
        obj = copy.deepcopy(self.good)
        update(obj)
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError)):
            self.check(obj)

    def test_positive(self):
        self.check(copy.deepcopy(self.good))

    def test_duplicate_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "duplicate.json"
            path.write_text('{"records":[],"records":[]}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                v.load(path)

    def test_source_digest_swap(self):
        self.reject(lambda x: x.__setitem__("source_observation_sha256", "f" * 64))

    def test_source_byte_change(self):
        with self.assertRaisesRegex(ValueError, "Sanitized OPF source drift"):
            self.check(self.good, obs_bytes=self.obs_bytes + b" ")

    def test_prior_accepted_digest_change(self):
        self.reject(lambda x: x.__setitem__("prior_crosscheck_sha256", "f" * 64))

    def test_prior_accepted_state_cannot_relabel(self):
        prior = copy.deepcopy(self.prior)
        for item in prior["records"]:
            if item["opf_source_local_id"] == "opf-local:0091":
                item["crosscheck_state"] = "VERIFIED"
        with self.assertRaisesRegex(ValueError, "Prior unresolved"):
            self.check(self.good, prior=prior)

    def test_0089_no_author_guess(self):
        self.reject(lambda x: x["records"][0].__setitem__("opf_creators", ["W.R. Thompson"]))

    def test_0089_no_isbn_guess(self):
        self.reject(lambda x: x["records"][0].__setitem__("opf_isbn10", "0743421205"))

    def test_infiltrator_invalid_edition_binding(self):
        self.reject(lambda x: x.__setitem__("private_edition_identity_verified", True))

    def test_death_wrong_converted_isbn(self):
        self.reject(lambda x: x["records"][1].__setitem__("isbn13_from_opf", "9780743422888"))

    def test_death_wrong_publisher_isbn(self):
        self.reject(lambda x: x["records"][1].__setitem__("publisher_isbn13", "9780743421225"))

    def test_balance_publisher_title_forged(self):
        self.reject(lambda x: x["records"][2].__setitem__("publisher_title", "The Death of Princes"))

    def test_balance_author_forged(self):
        self.reject(lambda x: x["records"][2].__setitem__("publisher_authors", ["John Peel"]))

    def test_cross_title_collision_hidden(self):
        self.reject(lambda x: x["records"][2].__setitem__("crosscheck_state", "SAME_TITLE_SAME_EDITION"))

    def test_publisher_url_wrong_book(self):
        self.reject(lambda x: x["records"][2].__setitem__("publisher_locator", x["records"][1]["publisher_locator"]))

    def test_publisher_provenance_family_forged(self):
        self.reject(lambda x: x.__setitem__("publisher_source_family", "two-independent-sources"))

    def test_duplicate_observation_id(self):
        self.reject(lambda x: x["records"][2].__setitem__("source_local_observation_id",
                                                    x["records"][1]["source_local_observation_id"]))

    def test_private_path_leak(self):
        self.reject(lambda x: x["records"][0].__setitem__("uncertainty", "C:/Users/patri/source.epub"))

    def test_new_public_synopsis_on_conflicted_opf(self):
        self.reject(lambda x: x["records"][2].__setitem__("original_publisher_description_paraphrase", "A misleading plot"))

    def test_synopsis_release_forbidden(self):
        self.reject(lambda x: x.__setitem__("public_synopsis_effect", "PUBLISHED"))

    def test_cover_rights_promotion_forbidden(self):
        self.reject(lambda x: x.__setitem__("publisher_cover_bytes_exported", True))

    def test_private_full_text_overclaim_forbidden(self):
        self.reject(lambda x: x.__setitem__("private_ebook_text_read", True))

    def test_global_work_promotion_forbidden(self):
        self.reject(lambda x: x.__setitem__("global_work_admission", "ADMITTED"))

    def test_coverage_promotion_forbidden(self):
        self.reject(lambda x: x.__setitem__("coverage_effect", "CLOSE_READ"))

    def test_unreviewed_synopsis_mutation(self):
        self.reject(lambda x: x["records"][0].__setitem__("original_publisher_description_paraphrase", "Entirely new summary"))

    def test_extra_global_identity_field(self):
        self.reject(lambda x: x["records"][0].__setitem__("resolved_work_id", "work:infiltrator"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
