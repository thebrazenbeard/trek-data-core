"""Adversarial release-denial tests for versioned CC2 and CC4 source metadata."""

from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import check_cc_license_version_held as policy


class CCLicenseVersionHeldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = policy._json(policy.PACKET / "records.json")

    def rejects(self, mutate, pattern="drift"):
        obj = copy.deepcopy(self.original)
        mutate(obj)
        with self.assertRaisesRegex(policy.HeldPolicyRejected, pattern):
            policy.validate(obj)

    def test_accepted_source_case_policy_is_held(self):
        policy.validate(self.original)
        self.assertEqual(len(self.original["accepted_source_examples"]), 3)
        self.assertEqual(self.original["accepted_release_gate"]["reviewed_local_artwork_pin_count"], 0)
        self.assertFalse(self.original["public_release_eligible"])

    def test_cc_2_source_version_is_never_silently_upgraded(self):
        for old, new in (("CC-BY-2.0", "CC-BY-4.0"),
                         ("CC-BY-SA-2.0", "CC-BY-SA-4.0"),
                         ("CC-BY-4.0", "CC-BY-2.0")):
            with self.subTest(old=old, new=new):
                with self.assertRaisesRegex(policy.HeldPolicyRejected, "relabel/upgrade"):
                    policy.classify(old, proposed_release_license=new)

    def test_each_license_version_has_independent_held_result(self):
        for identifier in policy.LICENSES:
            with self.subTest(identifier=identifier):
                receipt = policy.classify(identifier)
                self.assertEqual(receipt["observed_license"], identifier)
                self.assertFalse(receipt["public_release_eligible"])
                self.assertTrue(receipt["decision"].startswith("HELD_"))
                self.assertEqual(receipt["allowlisted"], identifier.endswith("4.0"))
        self.assertFalse(policy.classify("CC-BY-SA-2.0")["allowlisted"])
        self.assertTrue(policy.classify("CC-BY-SA-2.0")["sharealike_for_adaptations"])
        self.assertFalse(policy.classify("CC-BY-2.0")["sharealike_for_adaptations"])

    def test_unknown_version_is_not_promoted(self):
        for unknown in ("CC-BY-3.0", "CC BY 2.0", "CC-BY-SA-5.0", "CC0", "BY2"):
            with self.subTest(unknown=unknown):
                receipt = policy.classify(unknown)
                self.assertEqual(receipt["decision"], "HELD_UNRECOGNIZED_LICENSE")
                self.assertFalse(receipt["public_release_eligible"])

    def test_even_a_recognized_4_0_license_does_not_satisfy_other_rights(self):
        self.assertTrue(policy.classify("CC-BY-SA-4.0")["allowlisted"])
        self.assertEqual(policy.classify("CC-BY-SA-4.0")["decision"],
                         "HELD_FILE_LEVEL_RIGHTS_UNVERIFIED")
        self.rejects(lambda obj: obj.update(public_release_eligible=True))
        self.rejects(lambda obj: obj.update(public_artwork_release_effect="PUBLISHED"))

    def test_false_legacy_release_routes_are_rejected(self):
        self.rejects(lambda obj: obj["alternatives_for_legacy_2_0"][1].update(
            automatically_approves_publication=True))
        self.rejects(lambda obj: obj["alternatives_for_legacy_2_0"][1].update(
            preconditions_for_future_release=["PASS_LICENSE_CHECK"]), pattern="prerequisites")
        self.rejects(lambda obj: obj["alternatives_for_legacy_2_0"][2].update(
            current_status="RELEASE_READY"))

    def test_source_license_rewrite_or_rights_caveat_erasure_fails(self):
        self.rejects(lambda obj: obj["accepted_source_examples"][0].update(
            observed_source_license="CC-BY-4.0"))
        self.rejects(lambda obj: obj["accepted_source_examples"][1].update(
            raw_license_value="CC_BY_SA_4_0_GENERIC"))
        self.rejects(lambda obj: obj["accepted_source_examples"][2].update(
            rights_limit_field="no_rights_issue"), pattern="limitation")

    def test_policy_schema_and_version_map_are_closed(self):
        self.rejects(lambda obj: obj.update(authorized_deploy=True), pattern="unexpected")
        self.rejects(lambda obj: obj["version_policy"].update(
            {"CC-BY-2.0": {"decision": "PUBLIC"}}), pattern="version_policy")
        self.rejects(lambda obj: obj["accepted_release_gate"].update(
            license_bases=obj["accepted_release_gate"]["license_bases"] + ["CC-BY-2.0"]))

    def test_accepted_source_hash_is_checked_before_finding(self):
        with tempfile.TemporaryDirectory(prefix="trek-cc-version-") as tmp:
            root = Path(tmp)
            for source in [policy.RELEASE_GATE] + [row[0] for row in policy.SOURCE_EXAMPLES.values()]:
                dest = root / source
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(policy.ROOT / source, dest)
            source = root / "explorer/beyond-premiere-photo.json"
            source.write_text(source.read_text(encoding="utf-8").replace("CC BY 2.0", "CC BY 4.0"),
                              encoding="utf-8")
            with self.assertRaisesRegex(policy.HeldPolicyRejected, "source SHA drift"):
                policy.validate(self.original, root=root)
            shutil.copyfile(policy.ROOT / "explorer/beyond-premiere-photo.json", source)
            gate = root / policy.RELEASE_GATE
            gate.write_text(gate.read_text(encoding="utf-8") + "\n# malicious allowlist mutation\n",
                            encoding="utf-8")
            with self.assertRaisesRegex(policy.HeldPolicyRejected, "release gate SHA drift"):
                policy.validate(self.original, root=root)

    def test_duplicate_json_key_does_not_override_held_status(self):
        with tempfile.TemporaryDirectory(prefix="trek-cc-dupe-") as tmp:
            file = Path(tmp) / "fake.json"
            file.write_text('{"public_release_eligible":false,"public_release_eligible":true}',
                            encoding="utf-8")
            with self.assertRaisesRegex(policy.HeldPolicyRejected, "duplicate JSON key"):
                policy._json(file)

    def test_policy_packet_cannot_ship_pixels_or_embedded_media(self):
        with tempfile.TemporaryDirectory(prefix="trek-cc-packet-") as tmp:
            directory = Path(tmp)
            for name in ("records.json", "MANIFEST.md"):
                shutil.copyfile(policy.PACKET / name, directory / name)
            (directory / "legacy-photo.jpg").write_bytes(b"\xff\xd8\xff\x00fake")
            with self.assertRaisesRegex(policy.HeldPolicyRejected, "inventory"):
                policy.check_packet_inventory(directory)
            (directory / "legacy-photo.jpg").unlink()
            (directory / "MANIFEST.md").write_text("![picture](https://example.com/photo.jpg)", encoding="utf-8")
            with self.assertRaisesRegex(policy.HeldPolicyRejected, "embedded public/media"):
                policy.check_packet_inventory(directory)


if __name__ == "__main__":
    unittest.main()
