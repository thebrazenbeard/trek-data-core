"""Hostile provenance, version and optimized-mode mutation tests."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("darkness_editions_guard", HERE / "validate.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class DarknessHomeMediaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = guard.read_pinned()
        cls.catalog = json.loads(guard.DISCOVERY.read_text())

    def reject(self, mutate):
        bad = copy.deepcopy(self.packet)
        mutate(bad)
        with self.assertRaises(ValueError):
            guard.validate(bad, self.catalog)

    def test_source_local_five_cards(self):
        self.assertEqual(guard.validate(self.packet, self.catalog), 5)

    def test_version_conflict_cannot_be_silently_reconciled(self):
        self.reject(lambda p: p["studio_listing_observation"].update(runtime_as_listed_minutes=131))
        self.reject(lambda p: p["home_release_observation"].update(runtime_as_announced_minutes=132))
        self.reject(lambda p: p.update(runtime_disposition="BOTH_IDENTICAL_CUT"))
        self.reject(lambda p: p["studio_listing_observation"].update(runtime_edition="BLURAY_2013"))

    def test_source_identity_and_independence_cannot_be_forged(self):
        self.reject(lambda p: p.update(source_group="two-independent-studios"))
        self.reject(lambda p: p.update(source_independence="independent witnesses"))
        self.reject(lambda p: p["source_locators"].update(home_release_pdf="https://unknown.example/a.pdf"))
        self.reject(lambda p: p.update(source_snapshots_sha256="0" * 64))
        self.reject(lambda p: p.update(baseline_accepted_main="0" * 40))

    def test_format_cards_cannot_collapse_or_mutate(self):
        self.reject(lambda p: p["cards"].pop())
        self.reject(lambda p: p["cards"][2].update(local_id="paramount-id-2013-bluray-dvd"))
        self.reject(lambda p: p["cards"][2].update(kind="SINGLE_DISC_DVD"))
        self.reject(lambda p: p["cards"][0].update(announced_us_availability_date="2013-09-10"))
        self.reject(lambda p: p["cards"][4].update(format_as_described="4K VIDEO"))

    def test_no_artwork_and_no_release_or_coverage_inflation(self):
        self.reject(lambda p: p["cards"][0].update(display_eligible=True))
        self.reject(lambda p: p["cards"][0].update(poster_url="https://example.com/poster.jpg"))
        self.reject(lambda p: p.update(media_bytes_fetched=True))
        self.reject(lambda p: p.update(accepted_coverage_effect="CLOSE_READ"))
        self.reject(lambda p: p.update(accepted_source_work_effect="RECONCILED"))
        self.reject(lambda p: p.update(public_synopsis_release_effect="RELEASED"))
        self.reject(lambda p: p.update(artwork_release_effect="DISPLAY_LICENSED"))

    def test_original_description_cannot_be_substituted(self):
        self.reject(lambda p: p["home_release_observation"].update(original_synopsis_candidate="One forged description"))
        self.reject(lambda p: p["home_release_observation"].update(synopsis_release_status="PUBLISHED"))

    def test_duplicate_keys_refused_and_pin_present(self):
        self.assertEqual(len(guard.PINNED_SHA256), 64)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"role":"FILMS","role":"AUDITOR"}', object_pairs_hook=guard.no_duplicate_keys)

    def test_optimized_mode_rejects_hostile_mutation(self):
        code = """
import copy,json,sys
sys.path.insert(0,sys.argv[1]); import validate as g
base=g.read_pinned(); discovery=json.loads(g.DISCOVERY.read_text())
for change in (lambda p:p['cards'][1].update(display_eligible=True),
               lambda p:p['studio_listing_observation'].update(runtime_as_listed_minutes=131),
               lambda p:p.update(accepted_coverage_effect='CLOSE_READ')):
    bad=copy.deepcopy(base); change(bad)
    try:g.validate(bad,discovery)
    except ValueError:pass
    else:raise SystemExit('optimized validation bypass')
"""
        result = subprocess.run([sys.executable, "-O", "-c", code, str(HERE)],
                                capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
