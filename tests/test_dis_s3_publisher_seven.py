"""Source-relative DIS S3 metadata and adversarial invariants."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANE = ROOT / "proposals" / "research" / "dis" / "s3-publisher-seven-20261103"
spec = importlib.util.spec_from_file_location("dis_s3_b009_validator", LANE / "validate.py")
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublisherSevenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((LANE / "records.json").read_text(encoding="utf-8"))

    def test_unmodified_and_pinned_snapshot(self) -> None:
        module.validate_records(self.data)
        completed = subprocess.run(
            [sys.executable, str(LANE / "validate.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def assert_rejected(self, edit) -> None:
        candidate = copy.deepcopy(self.data)
        edit(candidate)
        with self.assertRaises((ValueError, TypeError, KeyError)):
            module.validate_records(candidate)

    def test_reject_premature_work_identity(self) -> None:
        self.assert_rejected(lambda x: x["works"][0].__setitem__("canonical_work_id", "work:burnham"))

    def test_reject_claimed_episode_close_read(self) -> None:
        self.assert_rejected(lambda x: x.__setitem__("audiovisual_content_inspected", True))

    def test_reject_title_identity_swap(self) -> None:
        self.assert_rejected(lambda x: x["works"][0].__setitem__("title", "Die Trying"))

    def test_reject_video_cross_binding(self) -> None:
        self.assert_rejected(lambda x: x["works"][0].__setitem__("publisher_video_url", x["works"][1]["publisher_video_url"]))

    def test_reject_image_cross_binding(self) -> None:
        self.assert_rejected(lambda x: x["artwork_candidates"][0].__setitem__("source_url", x["artwork_candidates"][1]["source_url"]))

    def test_reject_artwork_publication_claim(self) -> None:
        self.assert_rejected(lambda x: x["artwork_candidates"][0].__setitem__("rights_status", "CLEARED"))

    def test_reject_missing_evidence(self) -> None:
        self.assert_rejected(lambda x: x["evidence"].pop())

    def test_reject_unknown_entity(self) -> None:
        self.assert_rejected(lambda x: x["assertions"][0]["local_entity_ids"].append("global:spock"))

    def test_reject_evidence_promotion(self) -> None:
        self.assert_rejected(lambda x: x["evidence"][0].__setitem__("observation_scope", "EPISODE_WATCHED"))

    def test_reject_assertion_status_promotion(self) -> None:
        self.assert_rejected(lambda x: x["assertions"][0].__setitem__("status", "CANON_VERIFIED"))

    def test_sanctuary_must_preserve_source_rescue_not_defense(self) -> None:
        def corrupt(x):
            synopsis = x["evidence"][4]["paraphrase"]
            x["evidence"][4]["paraphrase"] = synopsis.replace("help rescue it from Osyraa", "help defend it from Osyraa")
        self.assert_rejected(corrupt)

    def test_reject_forged_immutable_retrieval(self) -> None:
        self.assert_rejected(lambda x: x["source"].__setitem__("response_digest_stability", "STABLE"))

    def test_reject_unexpected_claim_field(self) -> None:
        self.assert_rejected(lambda x: x["works"][0].__setitem__("verified_canon", True))

    def test_reject_part_1_and_part_2_collapse(self) -> None:
        self.assert_rejected(lambda x: x["works"][6].__setitem__("local_work_id", x["works"][5]["local_work_id"]))

    def test_raw_hash_pin_rejects_semantically_valid_tamper(self) -> None:
        candidate = copy.deepcopy(self.data)
        candidate["evidence"][0]["paraphrase"] += " A later editorial addition."
        module.validate_records(candidate)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "records.json"
            path.write_text(json.dumps(candidate), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(LANE / "validate.py"), "--path", str(path)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("unpinned", completed.stderr)


if __name__ == "__main__":
    unittest.main()
