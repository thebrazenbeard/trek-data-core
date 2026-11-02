"""Candidate-only, allowlisted publisher discovery compilation contract."""

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import build_publisher_catalog as publisher


ROOT = Path(__file__).resolve().parents[1]


class PublisherCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        manifest = json.loads((ROOT / publisher.ALLOWLIST).read_text(encoding="utf-8"))
        self.manifest = manifest
        for file in [publisher.ALLOWLIST, Path("registry/mission_catalog.json"),
                     *(Path(source["path"]) for source in manifest["sources"])]:
            target = self.root / file
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / file, target)

    def _manifest(self, value):
        (self.root / publisher.ALLOWLIST).write_text(json.dumps(value), encoding="utf-8")

    def _edit_bundle(self, idx, func, repin=True):
        item = self.manifest["sources"][idx]
        path = self.root / item["path"]
        data = json.loads(path.read_text(encoding="utf-8"))
        func(data)
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        path.write_bytes(raw)
        if repin:
            item["sha256"] = hashlib.sha256(raw).hexdigest()
            self._manifest(self.manifest)

    def test_build_is_deterministic_and_claims_no_admission(self):
        first = publisher.build_bytes(ROOT)
        self.assertEqual(first, publisher.build_bytes(ROOT))
        result = json.loads(first)
        self.assertEqual(result["candidate_row_count"], 15)
        self.assertEqual(result["publisher_source_count"], 2)
        self.assertEqual(result["roster_completeness"], "UNRESOLVED")
        for name in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
            self.assertEqual(result[name], "NONE")
        self.assertEqual(len([x for x in result["rows"] if x["mission_id"] == "sfa"]), 10)
        tng = [x for x in result["rows"] if x["mission_id"] == "tng"]
        self.assertEqual(len(tng), 5)
        self.assertEqual(sum(x["episode_number"] is None for x in tng), 3)
        self.assertTrue(all(x["verification_status"] == "UNVERIFIED_METADATA" and
                            x["coverage_effect"] == "NONE" for x in result["rows"]))
        self.assertEqual(len({(r["source_bundle_path"], r["row_id"]) for r in result["rows"]}), 15)

    def test_committed_output_matches_check_mode(self):
        run = subprocess.run([sys.executable, str(ROOT / "tools/build_publisher_catalog.py"), "--check"],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("15 candidate-only", run.stdout)

    def test_tampered_bundle_rejected_before_parsing(self):
        self._edit_bundle(1, lambda x: x["episode_slots"][0].__setitem__("title", "Unexpected title"), repin=False)
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            publisher.build_bytes(self.root)

    def test_allowlist_fails_closed_on_traversal_and_duplicate(self):
        entry = copy.deepcopy(self.manifest["sources"][0])
        entry["path"] = "proposals/librarian/../../private/bundle.json"
        self.manifest["sources"][0] = entry
        self._manifest(self.manifest)
        with self.assertRaisesRegex(ValueError, "unsafe"):
            publisher.build_bytes(self.root)
        self.manifest["sources"][0] = copy.deepcopy(self.manifest["sources"][1])
        self._manifest(self.manifest)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            publisher.build_bytes(self.root)

    def test_symlinked_publisher_bundle_rejected(self):
        item = self.manifest["sources"][0]
        source = self.root / item["path"]
        replica = source.with_name("saved.json")
        source.rename(replica)
        source.symlink_to(replica)
        with self.assertRaisesRegex(ValueError, "symlink"):
            publisher.build_bytes(self.root)

    def test_manifest_forbids_admission_or_coverage(self):
        for key in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
            changed = copy.deepcopy(self.manifest)
            changed[key] = "ACCEPTED"
            self._manifest(changed)
            with self.assertRaisesRegex(ValueError, key):
                publisher.build_bytes(self.root)

    def test_publisher_roster_cannot_promote_work_or_invent_slots(self):
        self._edit_bundle(1, lambda x: x["episode_slots"][0].__setitem__("canonical_work_id", "accepted:episode"))
        with self.assertRaisesRegex(ValueError, "cannot create Work"):
            publisher.build_bytes(self.root)

    def test_publisher_roster_cannot_change_host_or_owner_with_repin(self):
        self._edit_bundle(1, lambda x: x["observation"].__setitem__(
            "primary_locator", "https://example.org/shows/star-trek-starfleet-academy/episodes/1/"))
        with self.assertRaisesRegex(ValueError, "publisher lineage"):
            publisher.build_bytes(self.root)

    def test_publisher_roster_cannot_change_independence_group_with_repin(self):
        self._edit_bundle(1, lambda x: x["observation"].__setitem__(
            "independence_group", "publisher:example"))
        with self.assertRaisesRegex(ValueError, "publisher lineage"):
            publisher.build_bytes(self.root)

    def test_publisher_roster_cannot_change_publisher_with_repin(self):
        self._edit_bundle(1, lambda x: x["observation"].__setitem__(
            "publisher", "Example Streaming"))
        with self.assertRaisesRegex(ValueError, "publisher lineage"):
            publisher.build_bytes(self.root)

    def test_safe_write_rejects_symlinked_output_file_without_touching_target(self):
        target = self.root / publisher.OUTPUT
        target.parent.mkdir(parents=True, exist_ok=True)
        victim = self.root / "victim.json"
        victim.write_bytes(b"do not modify")
        target.symlink_to(victim)
        with self.assertRaisesRegex(ValueError, "non-symlink"):
            publisher.safe_write(self.root, publisher.OUTPUT, b"wrong")
        self.assertEqual(victim.read_bytes(), b"do not modify")
        self.assertTrue(target.is_symlink())

    def test_safe_write_rejects_symlinked_output_ancestor(self):
        sibling = self.root / "outside"
        sibling.mkdir()
        parent = self.root / "proposals/discovery"
        parent.symlink_to(sibling, target_is_directory=True)
        with self.assertRaises(OSError):
            publisher.safe_write(self.root, publisher.OUTPUT, b"wrong")
        self.assertEqual(list(sibling.iterdir()), [])

    def test_safe_write_replaces_regular_output_atomically(self):
        target = self.root / publisher.OUTPUT
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"old")
        publisher.safe_write(self.root, publisher.OUTPUT, b"new")
        self.assertEqual(target.read_bytes(), b"new")
        self.assertEqual([p.name for p in target.parent.iterdir()], [target.name])

    def test_tng_references_reject_admitted_binding(self):
        self._edit_bundle(0, lambda x: x["bindings"][0].__setitem__("lifecycle", "ACCEPTED"))
        with self.assertRaisesRegex(ValueError, "binding admission"):
            publisher.build_bytes(self.root)

    def test_tng_crosswalk_cannot_claim_accepted_identity(self):
        self._edit_bundle(0, lambda x: x["crosswalks"][0].__setitem__("mapping_status", "ACCEPTED"))
        with self.assertRaisesRegex(ValueError, "accepted identity"):
            publisher.build_bytes(self.root)

    def test_tng_sources_cannot_claim_captured_content(self):
        self._edit_bundle(0, lambda x: x["sources"][0].__setitem__("content_fingerprint", "invented"))
        with self.assertRaisesRegex(ValueError, "unverified"):
            publisher.build_bytes(self.root)

    def test_tng_preview_does_not_gain_fake_ordinal(self):
        self._edit_bundle(0, lambda x: x["sources"][2]["provider_metadata"].__setitem__("observed_season", 1))
        with self.assertRaisesRegex(ValueError, "ambiguous episode ordinal"):
            publisher.build_bytes(self.root)

    def test_tng_publisher_ownership_rejected_if_changed(self):
        self._edit_bundle(0, lambda x: x["sources"][0].__setitem__("independence_group", "publisher:unrelated"))
        with self.assertRaisesRegex(ValueError, "publisher ownership"):
            publisher.build_bytes(self.root)

    def test_duplicate_json_keys_rejected_even_when_repinning(self):
        item = self.manifest["sources"][1]
        path = self.root / item["path"]
        raw = path.read_bytes().replace(b'"coverage_effect": "NONE",',
                                        b'"coverage_effect": "NONE", "coverage_effect": "ACCEPTED",')
        path.write_bytes(raw)
        item["sha256"] = hashlib.sha256(raw).hexdigest()
        self._manifest(self.manifest)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            publisher.build_bytes(self.root)


if __name__ == "__main__":
    unittest.main()
