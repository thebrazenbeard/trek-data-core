"""Adversarial tests: indexed wiki file titles may never bootstrap public art or canon."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "proposals/librarian/memory-alpha-artwork-discovery-20261103"
SPEC = importlib.util.spec_from_file_location("memory_alpha_artwork_validation", FOLDER / "validate.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class MemoryAlphaArtworkDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads((FOLDER / "records.json").read_text(encoding="utf-8"))
        cls.catalog = json.loads((ROOT / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))

    def reject(self, mutate):
        altered = copy.deepcopy(self.packet)
        mutate(altered)
        with self.assertRaises(ValueError):
            mod.validate(altered, self.catalog)

    def test_current_packet_valid_and_separate_source_local_rows(self):
        mod.validate(self.packet, self.catalog)
        self.assertEqual(len(self.packet["file_candidates"]), 8)
        self.assertEqual(len(self.packet["commons_alternative_candidates"]), 2)
        self.assertEqual(len(self.packet["secondary_metadata_leads"]), 2)
        two_rows = next(c for c in self.packet["file_candidates"] if c["candidate_id"] ==
                        "ma-file-doomsday-remastered-title-card")["source_local_row_ids"]
        self.assertEqual(two_rows, ["lead:0000", "legacy:s2:tos:005"])
        # A future, separately reviewed Explorer sidecar must not invalidate
        # this permanently blocked metadata packet.
        self.assertTrue(all(item["image_url"] is None
                            for item in self.packet["file_candidates"] +
                            self.packet["commons_alternative_candidates"]))
        self.assertFalse(any(path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
                             for path in FOLDER.rglob("*") if path.is_file()))

    def test_no_image_urls_and_no_file_pages_read(self):
        self.assertFalse(self.packet["file_description_pages_read"])
        self.assertFalse(self.packet["image_urls_released"])
        self.assertTrue(all(candidate["image_url"] is None
                            for candidate in self.packet["file_candidates"] +
                            self.packet["commons_alternative_candidates"]))
        self.assertTrue(all(candidate["file_page_status"] == "NOT_READ_ROBOTS_RESTRICTED"
                            for candidate in self.packet["file_candidates"]))

    def test_any_admission_or_published_effect_rejected(self):
        for field, value in (("accepted_source_effect", "SOURCE_BOUND"),
                             ("accepted_work_effect", "ADMITTED"),
                             ("accepted_evidence_effect", "ADMITTED"),
                             ("coverage_effect", "STRUCTURALLY_INDEXED"),
                             ("public_artwork_release_effect", "DISPLAY"),
                             ("file_description_pages_read", True),
                             ("file_bytes_retrieved", True),
                             ("hotlink_permission_verified", True),
                             ("source_independence_group", "primary:memory-alpha")):
            with self.subTest(field=field):
                self.reject(lambda p: p.__setitem__(field, value))

    def test_forged_file_identity_or_rights_claim_rejected(self):
        for field, value in (("file_title_from_index", "Altered title.jpg"),
                             ("category_locator", "https://other.example/category"),
                             ("medium_hint", "LITERATURE"),
                             ("source_local_row_ids", ["literature:prh-autobiography-kirk"]),
                             ("subject_mapping", "EXACT_EDITION_CONFIRMED"),
                             ("file_page_status", "VERIFIED"),
                             ("uploader_and_license_status", "CC_BY_LICENSED"),
                             ("display_status", "CLEARED"),
                             ("image_url", "https://static.wikia.nocookie.net/picard.jpg")):
            with self.subTest(field=field):
                self.reject(lambda p: p["file_candidates"][5].__setitem__(field, value))

    def test_forged_metadata_reconciliation_rejected(self):
        for field, value in (("isbn10_from_search_excerpt", "1789095336"),
                             ("mapping_status", "CANONICAL_EDITION"),
                             ("evidence_status", "PRIMARY_FULL_TEXT_READ"),
                             ("existing_source_local_row_id", "lead:0000")):
            with self.subTest(field=field):
                self.reject(lambda p: p["secondary_metadata_leads"][1].__setitem__(field, value))

    def test_commons_claim_is_not_rights_release(self):
        for field, value in (("asset_publication", "CLEARED"),
                             ("underlying_prop_design_and_trademark_status", "CLEARED"),
                             ("image_url", "https://upload.wikimedia.org/wikipedia/commons/test.jpg"),
                             ("license", "PUBLIC_DOMAIN"),
                             ("creator", "Unknown")):
            with self.subTest(field=field):
                self.reject(lambda p: p["commons_alternative_candidates"][0].__setitem__(field, value))

    def test_unknown_gates_and_duplicate_candidates_rejected(self):
        self.reject(lambda p: p["file_candidates"][0].__setitem__("license_verified", True))
        self.reject(lambda p: p["commons_alternative_candidates"][0].__setitem__("rights_waiver", True))
        self.reject(lambda p: p["file_candidates"].append(copy.deepcopy(p["file_candidates"][0])))
        self.reject(lambda p: p["secondary_metadata_leads"].append(
            copy.deepcopy(p["secondary_metadata_leads"][0])))
        self.reject(lambda p: p["rights_policy_sources"].append("https://untrusted.invalid"))


if __name__ == "__main__":
    unittest.main()
