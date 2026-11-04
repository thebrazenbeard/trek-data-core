"""Adversarial tests for a held publisher metadata comparison; no episode reads."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("tos_s1_boundary_validator", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def fixtures():
    receipt = json.loads((HERE / "RECEIPT.json").read_text(encoding="utf-8"))
    with (ROOT / "proposals/discovery/legacy-paramount-season1-20261102/tos.csv").open(
        newline="", encoding="utf-8") as stream:
        csv_rows = list(csv.DictReader(stream))
    def read(path):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    return [
        receipt,
        csv_rows,
        read("proposals/discovery/tos-publisher-s01-b001-20261102/paramountplus.json"),
        read("proposals/discovery/tos-publisher-s01-b001-20261102/plutotv.json"),
        read("proposals/research/tos-charlie-x-derivative-close-read-20261103/MANIFEST.json"),
    ]


class SourceLocalBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.args = fixtures()

    def rejects(self, mutate):
        modified = copy.deepcopy(self.args)
        mutate(modified)
        with self.assertRaises(ValueError):
            validator.check(*modified)

    def test_baseline(self):
        self.assertEqual(validator.check(*self.args), {
            "publisher_cards_checked": 5,
            "csv_rows_checked": 6,
            "roster_slots_checked": 10,
            "source_local_ordinal_discrepancies_preserved": 2,
            "coverage_admitted": 0,
        })

    def test_rejects_publisher_cage_omission(self):
        self.rejects(lambda a: a[0]["publisher_guide_cards"].pop(0))

    def test_rejects_silent_charlie_renumber(self):
        self.rejects(lambda a: a[0]["publisher_guide_cards"][2].update(episode_number=2))

    def test_rejects_punctuation_normalization(self):
        self.rejects(lambda a: a[2]["episode_slots"][2].update(title="Charlie X"))

    def test_rejects_pluto_as_independent_corroboration(self):
        self.rejects(lambda a: a[3]["observation"].update(independence_group="publisher:pluto"))

    def test_rejects_source_work_binding(self):
        self.rejects(lambda a: a[3]["episode_slots"][0].update(source_binding_id="fictional-id"))

    def test_rejects_promoted_coverage(self):
        self.rejects(lambda a: a[2].update(coverage_effect="CLOSE_READ"))

    def test_rejects_raw_html_digest_claim(self):
        self.rejects(lambda a: a[0].update(raw_html_sha256="0" * 64))

    def test_rejects_derivative_caption_collapse(self):
        self.rejects(lambda a: a[4]["work"].update(derivative_site_image_caption_ordinal="Season 1, episode 3"))

    def test_rejects_derivative_primary_promotion(self):
        self.rejects(lambda a: a[4]["source"].update(authenticated_primary_av_or_studio_script=True))

    def test_rejects_csv_drift(self):
        self.rejects(lambda a: a[1][1].update(title="Charlie X"))

    def test_rejects_changed_baseline_bytes(self):
        with self.assertRaises(ValueError):
            validator.checked_blob(
                ROOT / "proposals/discovery/legacy-paramount-season1-20261102/tos.csv",
                "0" * 40,
            )


if __name__ == "__main__":
    unittest.main()
