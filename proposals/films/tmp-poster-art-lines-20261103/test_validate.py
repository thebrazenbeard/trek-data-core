"""Independent hostile mutations of artist, edition, source and rights claims."""

import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest


HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tmp_art_guard", HERE / "validate.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class TMPPosterFamiliesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(guard.RECORDS.read_text(encoding="utf-8"))
        cls.discovery = json.loads(guard.DISCOVERY.read_text(encoding="utf-8"))

    def reject(self, mutation, phrase):
        packet = copy.deepcopy(self.packet)
        mutation(packet)
        with self.assertRaisesRegex(ValueError, phrase):
            guard.validate(packet, self.discovery)

    def test_valid_proposal(self):
        self.assertEqual(guard.validate(self.packet, self.discovery), 4)

    def test_artist_role_cannot_be_collapsed(self):
        self.reject(lambda x: x["artwork_families"][0].update(original_artist_credit="Matt Ferguson"), "reviewed evidence")
        self.reject(lambda x: x["artwork_families"][1].update(remaster_credit="Bob Peak"), "reviewed evidence")

    def test_foil_editions_not_interchangeable(self):
        self.reject(lambda x: x["print_variants"][1].update(edition_limit=175), "reviewed evidence")
        self.reject(lambda x: x["print_variants"][3].update(edition_limit=200), "reviewed evidence")
        self.reject(lambda x: x["print_variants"][1].update(artwork_family_ref="vice-press-tmp-matt-ferguson-2023"), "reviewed evidence")

    def test_timed_is_not_numbered(self):
        self.reject(lambda x: x["print_variants"][0].update(edition_limit=200), "reviewed evidence")

    def test_no_wrong_media_version_promotions(self):
        self.reject(lambda x: x.update(version_exclusion="SAME_AS_2022_4K_CASE"), "version_exclusion")
        self.reject(lambda x: x.update(accepted_identity_effect="MERGED"), "accepted_identity_effect")

    def test_no_image_release_or_false_rights_receipt(self):
        self.reject(lambda x: x["print_variants"][0].update(display_eligible=True), "reviewed evidence")
        self.reject(lambda x: x["artwork_families"][0].update(rights_status="PUBLIC_DISPLAY_LICENSED"), "reviewed evidence")
        self.reject(lambda x: x["print_variants"][0].update(image_url="https://cdn.shopify.com/poster.jpg"), "unexpected/missing field")

    def test_source_and_unseen_hash_cannot_be_forged(self):
        self.reject(lambda x: x["sources"].update(bob_peak_2023="https://memory-alpha.fandom.com/wiki/File:Fake.jpg"), "unreviewed source locator")
        self.reject(lambda x: x.update(source_page_sha256="0" * 64), "source_page_sha256")

    def test_baseline_lineage_and_coverage_are_pinned(self):
        self.reject(lambda x: x.update(baseline_accepted_main="0" * 40), "baseline_accepted_main")
        self.reject(lambda x: x.update(accepted_coverage_effect="CLOSE_READ"), "accepted_coverage_effect")
        self.reject(lambda x: x.update(source_family_independence="X" * 1_000_000), "unbounded source lineage")

    def test_optimized_mode_rejects_multiple_hostile_mutations(self):
        code = """
import copy, json, sys
sys.path.insert(0, sys.argv[1])
import validate as g
packet = json.loads(g.RECORDS.read_text())
baseline = json.loads(g.DISCOVERY.read_text())
for field, index, value in (
  ('original_artist_credit', 0, 'Matt Ferguson'),
  ('rights_status', 1, 'PUBLIC_DISPLAY_PERMISSION_VERIFIED'),
):
  candidate = copy.deepcopy(packet)
  candidate['artwork_families'][index][field] = value
  try: g.validate(candidate, baseline)
  except ValueError: pass
  else: raise SystemExit('optimized mode bypassed ' + field)
candidate = copy.deepcopy(packet)
candidate['print_variants'][3]['edition_limit'] = 200
try: g.validate(candidate, baseline)
except ValueError: pass
else: raise SystemExit('optimized mode bypassed edition-limit')
"""
        result = subprocess.run([sys.executable, "-O", "-c", code, str(HERE)],
                                capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
