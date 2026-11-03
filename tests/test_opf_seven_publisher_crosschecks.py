"""Hostile drift and work-admission regressions for seven held OPF rows."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import build_opf_seven_publisher_crosschecks as subject


class HeldSevenPublisherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="trek-held-seven-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in (subject.SOURCE, subject.OPF, subject.HELD, subject.OLDER, subject.BASE):
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(subject.ROOT / name, dest)

    def replace(self, name: str, update) -> None:
        path = self.root / name
        obj = json.loads(path.read_text(encoding="utf-8"))
        update(obj)
        path.write_text(json.dumps(obj), encoding="utf-8")

    def test_projection_exact_generated_bytes_and_zero_work_claim(self):
        result = subject.build(self.root)
        self.assertEqual(subject.encode(result), (subject.ROOT / subject.OUTPUT).read_bytes())
        self.assertEqual(result["candidate_rows"], 7)
        self.assertEqual(result["owner_opf_member_records"], 347)
        self.assertIsNone(result["distinct_work_count"])
        self.assertEqual(result["work_admissions"], 0)
        self.assertEqual(result["prior_same_family_candidate_reused"], 1)
        self.assertEqual(len({r["publisher_candidate_isbn13"] for r in result["rows"]}), 7)
        self.assertTrue(all(r["public_explorer_release"] == "HELD" for r in result["rows"]))
        self.assertTrue(all(r["private_opf_xml_rehashed_this_wave"] is False for r in result["rows"]))

    def test_private_local_source_hash_swap_fails(self):
        self.replace(subject.OPF, lambda obj: obj["rows"][149].update({"opf_entry_sha256": "0" * 64}))
        with self.assertRaisesRegex(ValueError, "accepted source receipt SHA changed"):
            subject.build(self.root)

    def test_publisher_edition_isbn_spoof_fails(self):
        self.replace(subject.SOURCE, lambda obj: obj["rows"][4].update({"publisher_isbn13": "9780743455725"}))
        with self.assertRaisesRegex(ValueError, "accepted source receipt SHA changed"):
            subject.build(self.root)

    def test_cannot_claim_original_opf_xml_rehash_or_work_admission(self):
        self.replace(subject.SOURCE, lambda obj: obj.update({"original_opf_members_independently_rehashed_in_this_wave": True}))
        with self.assertRaisesRegex(ValueError, "accepted source receipt SHA changed"):
            subject.build(self.root)
        self.assertTrue(all(r["global_work_identity"] == "NOT_RECONCILED"
                            for r in subject.build(subject.ROOT)["rows"]))

    def test_prior_same_family_homecoming_dedupe_lineage_pinned(self):
        self.replace(subject.OLDER, lambda obj: obj["edition_candidates"][2].update({"isbn13": "9780743419628"}))
        with self.assertRaisesRegex(ValueError, "accepted source receipt SHA changed"):
            subject.build(self.root)
        home = next(r for r in subject.build(subject.ROOT)["rows"]
                    if r["opf_source_local_id"] == "opf-local:0275")
        self.assertEqual(home["prior_same_family_publisher_candidate"],
                         "SSEBOOK-VOY-HOMECOMING-9780743475631")

    def test_private_paths_and_copyrighted_content_not_exported(self):
        raw = subject.encode(subject.build(subject.ROOT)).decode("utf-8")
        self.assertNotIn("C:\\Users\\", raw)
        self.assertNotIn("OneDrive", raw)
        self.assertNotIn("\\\\", raw)
        self.assertNotIn("chapter_text", raw)
        self.assertNotIn("image_data", raw)
        self.assertNotIn('"work_admissions": 7', raw)


if __name__ == "__main__":
    unittest.main()
