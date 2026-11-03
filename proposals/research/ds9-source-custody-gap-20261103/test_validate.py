"""Negative checks that the DS9 custody proposal cannot self-promote."""

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from validate import REPO, check_archive_item_leads, check_contract, reject_duplicate_json_keys  # noqa: E402


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


class TestCustodyGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = load("source_routes.json")
        cls.evidence = load("evidence.json")
        cls.assertions = load("assertions.json")
        prior = json.loads((REPO / "proposals/research/ds9-paramount-s1-guide-20261103/records.json").read_text())
        cls.cards = {x["id"] for x in prior["source_local_episode_slots"]}

    def test_untouched(self):
        check_contract(self.routes, self.evidence, self.assertions, self.cards)

    def reject(self, mutate):
        routes, evidence, assertions = copy.deepcopy((self.routes, self.evidence, self.assertions))
        mutate(routes, evidence, assertions)
        with self.assertRaises(ValueError):
            check_contract(routes, evidence, assertions, self.cards)

    def test_reject_coverage(self):
        self.reject(lambda r, e, a: r.__setitem__("coverage_effect", "SOURCE_BOUND"))

    def test_reject_primary_read(self):
        self.reject(lambda r, e, a: r.__setitem__("primary_script_or_av_reads_completed", 1))

    def test_reject_work_identity(self):
        self.reject(lambda r, e, a: r.__setitem__("target_work_identity_status", "ACCEPTED"))

    def test_reject_untrusted_url(self):
        self.reject(lambda r, e, a: r["routes"][0]["public_observation_urls"].append("https://example.org/script"))

    def test_reject_claimed_rights(self):
        self.reject(lambda r, e, a: r["routes"][0].__setitem__("rights_to_republish_script_text", "GRANTED"))

    def test_reject_fiction_evidence(self):
        self.reject(lambda r, e, a: e.__setitem__("episode_scene_or_dialogue_evidence_count", 5))

    def test_reject_unresolved_promotion(self):
        self.reject(lambda r, e, a: a["assertions"][0].__setitem__("status", "STABLE"))

    def test_reject_route_identity_substitution(self):
        self.reject(lambda r, e, a: r["routes"][0].__setitem__("route_id", "made-up-route"))

    def test_reject_source_class_upgrade(self):
        self.reject(lambda r, e, a: r["routes"][3].__setitem__("source_class", "PRIMARY_STUDIO_SCRIPT"))

    def test_reject_lineage_substitution(self):
        self.reject(lambda r, e, a: r["routes"][3].__setitem__("lineage_group", "publisher:paramount"))

    def test_reject_same_host_different_page(self):
        self.reject(lambda r, e, a: r["routes"][0]["public_observation_urls"].__setitem__(
            0, "https://gaming.trekcore.com/unrelated-page"))

    def test_reject_claimed_access_for_all_routes(self):
        cases = [
            (0, "matching_target_script_bytes_read", True),
            (0, "publisher_master_or_custody_chain_verified", True),
            (0, "script_versions_and_revision_pages_verified", True),
            (0, "exact_media_hash", "f" * 64),
            (1, "source_pages_or_images_read", True),
            (1, "exact_target_titles_located_in_catalog", True),
            (2, "source_pages_or_images_read", True),
            (2, "exact_target_titles_located_in_catalog", True),
            (3, "episode_text_read", True),
            (3, "source_pages_or_images_read", "false"),
            (4, "episode_video_or_audio_read", True),
        ]
        for index, field, value in cases:
            with self.subTest(route=index, field=field):
                self.reject(lambda r, e, a: r["routes"][index].__setitem__(field, value))

    def test_reject_claimed_remote_access(self):
        self.reject(lambda r, e, a: r["routes"][2].__setitem__(
            "remote_access_status", "FULL_SCRIPT_DOWNLOADED"))

    def test_reject_missing_rights_status(self):
        self.reject(lambda r, e, a: r["routes"][4].pop("rights_to_republish_episode_media"))

    def test_reject_evidence_source_level_upgrade(self):
        self.reject(lambda r, e, a: e["evidence"][0].__setitem__(
            "source_level", "PRIMARY_SCRIPT_READ"))

    def test_reject_evidence_route_collision(self):
        self.reject(lambda r, e, a: e["evidence"][1].__setitem__(
            "route_id", "ds9-licensed-companion-cdrom"))

    def test_reject_reclassified_evidence_kind(self):
        self.reject(lambda r, e, a: e["evidence"][1].__setitem__(
            "kind", "SCRIPT_BODY_CLOSE_READ"))

    def test_reject_erased_source_identity(self):
        self.reject(lambda r, e, a: r["routes"][0].pop("exact_media_hash"))

    def test_reject_erased_mandatory_unread_flag(self):
        self.reject(lambda r, e, a: r["routes"][3].pop("episode_text_read"))

    def test_reject_claim_evidence_class_upgrade(self):
        self.reject(lambda r, e, a: r["routes"][0].__setitem__(
            "claim_evidence_class", "PRIMARY_SCRIPT_BYTES_VERIFIED"))

    def test_reject_forged_evidence_locator(self):
        self.reject(lambda r, e, a: e["evidence"][0].__setitem__(
            "locator", "authenticated script page 1"))

    def test_reject_unexpected_source_route_field(self):
        self.reject(lambda r, e, a: r["routes"][4].__setitem__(
            "primary_content_admitted", True))

    def run_optimized_contract(self, mutate):
        routes, evidence, assertions = copy.deepcopy((self.routes, self.evidence, self.assertions))
        mutate(routes, evidence, assertions)
        payload = {"routes": routes, "evidence": evidence, "assertions": assertions,
                   "cards": sorted(self.cards)}
        code = (f"import json,sys;sys.path.insert(0,{str(HERE)!r});"
                "from validate import check_contract;d=json.load(sys.stdin);"
                "check_contract(d['routes'],d['evidence'],d['assertions'],set(d['cards']))")
        result = subprocess.run([sys.executable, "-O", "-c", code], input=json.dumps(payload),
                                capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError", result.stderr)

    def test_optimized_python_rejects_removed_read_flag(self):
        self.run_optimized_contract(lambda r, e, a: r["routes"][3].pop("episode_text_read"))

    def test_optimized_python_rejects_rewritten_evidence(self):
        self.run_optimized_contract(lambda r, e, a: e["evidence"][2].__setitem__(
            "locator", "invented primary page locator"))

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"proposal_only":true,"proposal_only":false}',
                       object_pairs_hook=reject_duplicate_json_keys)


class TestArchiveItemGate(unittest.TestCase):
    def test_catalog_only_item_is_valid(self):
        check_archive_item_leads(load("archive_item_leads.json"))

    def reject(self, mutate):
        item_leads = load("archive_item_leads.json")
        mutate(item_leads)
        with self.assertRaises(ValueError):
            check_archive_item_leads(item_leads)

    def test_reject_accepted_work_link(self):
        self.reject(lambda d: d["items"][0].__setitem__("accepted_work_id", "ds9-for-the-uniform"))

    def test_reject_fabricated_folder_hash(self):
        self.reject(lambda d: d["items"][0].__setitem__("source_content_hash", "a" * 64))

    def test_reject_material_upgrade_to_script(self):
        self.reject(lambda d: d["items"][0].__setitem__(
            "held_material_scope", "VERIFIED_STUDIO_SCRIPT"))

    def test_reject_claimed_archive_read(self):
        self.reject(lambda d: d["items"][0].__setitem__("item_bytes_read", True))

    def test_reject_item_locator_substitution(self):
        self.reject(lambda d: d["items"][0].__setitem__("folder", "16"))

    def test_reject_renamed_archive_custodian(self):
        self.reject(lambda d: d["items"][0].__setitem__("archive", "Paramount Studios"))

    def test_reject_archive_root_admission_injection(self):
        self.reject(lambda d: d.__setitem__("admission_status", "ADMITTED"))

    def test_reject_archive_private_path_injection(self):
        self.reject(lambda d: d["items"][0].__setitem__(
            "private_host_path", "D:/VERA/private/source.rtf"))

    def test_reject_archive_copyrighted_text_injection(self):
        self.reject(lambda d: d["items"][0].__setitem__(
            "full_script_text", "This string stands for a forbidden source-text payload"))

    def test_reject_archive_schema_drift(self):
        self.reject(lambda d: d.__setitem__("schema_version", "9.9.9"))

    def test_optimized_python_rejects_injected_archive_payload(self):
        forged = load("archive_item_leads.json")
        forged["items"][0]["full_script_text"] = "Forbidden embedded source payload"
        code = (f"import json,sys;sys.path.insert(0,{str(HERE)!r});"
                "from validate import check_archive_item_leads;"
                "check_archive_item_leads(json.load(sys.stdin))")
        result = subprocess.run([sys.executable, "-O", "-c", code], input=json.dumps(forged),
                                capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError", result.stderr)


if __name__ == "__main__":
    unittest.main()
