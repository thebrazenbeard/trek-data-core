"""Hostile provenance, variant and rights checks."""

import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest


HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("vice_press_variant_guard", HERE / "validate.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class VicePressArtworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(guard.RECORDS.read_text(encoding="utf-8"))
        cls.films = json.loads(guard.FILM_DISCOVERY.read_text(encoding="utf-8"))

    def reject(self, mutation, message):
        packet = copy.deepcopy(self.packet)
        mutation(packet)
        with self.assertRaisesRegex(ValueError, message):
            guard.validate(packet, self.films)

    def test_tranche_is_bounded_and_valid(self):
        self.assertEqual(guard.validate(self.packet, self.films), 3)

    def test_media_and_display_not_silently_approved(self):
        self.reject(lambda d: d.update(media_bytes_fetched=True), "media_bytes_fetched")
        self.reject(lambda d: d.update(artwork_release_effect="PUBLIC"), "artwork_release_effect")
        self.reject(lambda d: d["variants"][0].update(eligible_for_thumbnail=True), "rights mismatch")

    def test_original_creator_and_remaster_credit_cannot_be_spoofed(self):
        self.reject(lambda d: d["source_attributed_creator_chain"].update(remaster_credit="Anonymous"), "creator chain not supported")
        self.reject(lambda d: d["source_attributed_creator_chain"].update(original_artwork_credit="Thomas Peak"), "creator chain not supported")

    def test_edition_limits_and_variants_cannot_be_swapped(self):
        self.reject(lambda d: d["variants"][1].update(edition_limit=150), "evidence/edition/rights mismatch")
        self.reject(lambda d: d["variants"][2].update(variant_kind="FOIL_VARIANT"), "evidence/edition/rights mismatch")

    def test_generic_current_retail_page_cannot_masquerade_as_timed_2024(self):
        self.reject(lambda d: d["variants"][0].update(product_locator="https://vice-press.com/products/star-trek-iv-the-voyage-home"), "evidence/edition/rights mismatch")

    def test_unexamined_source_and_copyright_claim_rejected(self):
        self.reject(lambda d: d.update(source_family="community:memory-alpha.fandom.com"), "source_family")
        self.reject(lambda d: d["variants"][1].update(rights_status="PUBLIC_DISPLAY_PERMISSION_VERIFIED"), "evidence/edition/rights mismatch")
        self.reject(lambda d: d["variants"][1].update(image_url="https://cdn.shopify.com/example.jpg"), "missing/extra field")

    def test_lineage_and_accepted_baseline_are_immutable(self):
        self.reject(lambda d: d.update(accepted_main_at_start="0" * 40), "accepted_main_at_start")
        self.reject(lambda d: d.update(source_lineage_note="Rights holder has permitted every web preview."), "source lineage claim")
        self.reject(lambda d: d.update(source_lineage_note="x" * 1_000_000), "lineage note too long")

    def test_unobserved_source_bytes_hash_cannot_be_invented(self):
        self.reject(lambda d: d.update(raw_source_snapshot_sha256="0" * 64), "raw_source_snapshot_sha256")

    def test_optimized_interpreter_still_rejects_forgery(self):
        code = """
import copy, json, sys
sys.path.insert(0, sys.argv[1])
import validate as v
p = json.loads(v.RECORDS.read_text(encoding='utf-8'))
films = json.loads(v.FILM_DISCOVERY.read_text(encoding='utf-8'))
for key, val in (('accepted_main_at_start', '0'*40), ('media_bytes_fetched', True)):
    q = copy.deepcopy(p)
    q[key] = val
    try: v.validate(q, films)
    except ValueError: pass
    else: raise SystemExit('optimized gate bypass: ' + key)
q = copy.deepcopy(p)
q['variants'][0]['eligible_for_thumbnail'] = True
try: v.validate(q, films)
except ValueError: pass
else: raise SystemExit('optimized gate bypass: thumbnail')
"""
        result = subprocess.run([sys.executable, "-O", "-c", code, str(HERE)],
                                capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
