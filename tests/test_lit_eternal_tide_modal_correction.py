"""Hostile modal regression for the publisher-only Eternal Tide correction."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
VALIDATOR_FILE = HERE / "proposals/research/lit-eternal-tide-modal-correction-20261103/validate.py"
SPEC = importlib.util.spec_from_file_location("lit_eternal_tide_modal_validator", VALIDATOR_FILE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load exact source-local validator")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class ModalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(mod.CORRECTION.read_text(encoding="utf-8"))
        # Minimal exact accepted source observation required by validator.
        cls.source = {"candidates": [{"candidate_id": cls.good["superseded_candidate_id"], "original_overview": mod.EXPECTED_OLD}]}

    def test_valid(self):
        mod.validate(self.good, self.source)

    def test_anticipated_return_rejected(self):
        bad = copy.deepcopy(self.good)
        bad["replacement_original_overview"] = bad["replacement_original_overview"].replace("unexpected return", "anticipated return")
        with self.assertRaises(ValueError):
            mod.validate(bad, self.source)

    def test_absent_unforeseen_modal_rejected(self):
        bad = copy.deepcopy(self.good)
        bad["replacement_original_overview"] = bad["replacement_original_overview"].replace("unforeseen by the fleet", "widely discussed by the fleet")
        with self.assertRaises(ValueError):
            mod.validate(bad, self.source)

    def test_privileged_effect_rejected(self):
        bad = copy.deepcopy(self.good)
        bad["public_synopsis_effect"] = "PUBLISH_NOW"
        with self.assertRaises(ValueError):
            mod.validate(bad, self.source)

    def test_unsourced_tag_rejected(self):
        bad = copy.deepcopy(self.good)
        bad["source_relative_tags"].append("identity:returning-leader-is-janeway")
        with self.assertRaises(ValueError):
            mod.validate(bad, self.source)


if __name__ == "__main__":
    unittest.main()
