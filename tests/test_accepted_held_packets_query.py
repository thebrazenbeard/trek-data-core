"""Hostile checks for a source-local-only query of three accepted-file HELD packets."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from tools import query_accepted_held_packets as held


class AcceptedHeldPacketsQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = held.build()

    def test_exact_pinned_input_receipts_original_validators_and_unadmitted_scope(self):
        report = self.report
        self.assertEqual(report["row_count"], 14)
        self.assertEqual(report["source_file_count"], 3)
        self.assertEqual(Counter(row["kind"] for row in report["rows"]), {
            "VOY_GUIDE_CARD": 5, "TNG_EDITORIAL_OBSERVATION": 6,
            "LITERARY_EDITION_CROSSCHECK": 3,
        })
        self.assertEqual(report["identity_scope"], held.IDENTITY_SCOPE)
        self.assertEqual(report["work_admissions"], 0)
        self.assertEqual(report["full_work_reads"], 0)
        self.assertEqual(report["coverage_effect"], "NONE")
        self.assertEqual(report["public_explorer_effect"], "NONE")
        for receipt, packet in zip(report["source_input_receipts"], held.PACKETS):
            kind, path, sha, validator_sha = packet
            self.assertEqual((receipt["kind"], receipt["source_input"], receipt["sha256"],
                              receipt["validator_sha256"]), (kind, path, sha, validator_sha))
            self.assertEqual(hashlib.sha256((held.ROOT / path).read_bytes()).hexdigest(), sha)
            self.assertEqual(hashlib.sha256((held.ROOT / Path(path).with_name("validate.py")).read_bytes()).hexdigest(),
                             validator_sha)
        self.assertEqual(held.build(), report)
        self.assertEqual([r["row_id"] for r in report["rows"]],
                         sorted(r["row_id"] for r in report["rows"]))
        for row in report["rows"]:
            self.assertEqual(row["identity_scope"], held.IDENTITY_SCOPE)
            self.assertEqual(row["source_lineage_independence"], "NOT_ESTABLISHED")
            self.assertEqual(row["work_admission_effect"], "NONE")
            self.assertEqual(row["coverage_effect"], "NONE")
            self.assertEqual(row["public_release_effect"], "NONE")
            self.assertIs(row["full_work_read"], False)
            self.assertTrue(row["source_url"].startswith("https://"))
            for disallowed in ("synopsis", "artwork", "image_url", "private_path", "global_work_id",
                               "accepted_work_id", "work_id"):
                self.assertNotIn(disallowed, row)

    def test_exact_ids_and_unresolved_isbn_mismatch_remain_source_local(self):
        report = self.report
        literature = [r for r in report["rows"] if r["kind"] == "LITERARY_EDITION_CROSSCHECK"]
        mismatch = next(r for r in literature if r["source_local_id"] == "opf-local:0091")
        self.assertIn("ISBN", mismatch["source_relative_note"])
        self.assertEqual(mismatch["source_status"],
                         "TITLE_AUTHOR_PRODUCT_MATCH_ISBN_EDITION_MISMATCH_UNRESOLVED")
        self.assertIn("opf-isbn13:9780743421225", mismatch["tags"])
        self.assertIn("publisher-isbn13:9780743422888", mismatch["tags"])
        self.assertEqual(held.query(report, row_id=mismatch["row_id"])["rows"], [mismatch])
        self.assertEqual(held.query(report, row_id="work:0091")["total_matches"], 0)
        self.assertEqual(held.query(report, kind="VOY_GUIDE_CARD")["total_matches"], 5)
        self.assertEqual(held.query(report, text="brother")["total_matches"], 1)
        self.assertEqual(held.query(report, tag="subject:lore")["total_matches"], 6)
        self.assertEqual(held.query(report, text="9780743422888")["total_matches"], 1)
        self.assertEqual(held.query(report, status="PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED")
                         ["total_matches"], 2)

    def test_pagination_facets_and_query_bounds(self):
        report = self.report
        first = held.query(report, limit=4)
        self.assertEqual(first["total_matches"], 14)
        self.assertEqual(first["next_offset"], 4)
        self.assertEqual(first["facet_counts"]["kind"], {
            "LITERARY_EDITION_CROSSCHECK": 3, "TNG_EDITORIAL_OBSERVATION": 6, "VOY_GUIDE_CARD": 5,
        })
        rebuilt = []
        for offset in (0, 4, 8, 12):
            part = held.query(report, offset=offset, limit=4)
            self.assertEqual(part["total_matches"], 14)
            rebuilt.extend(part["rows"])
        self.assertEqual(rebuilt, report["rows"])
        self.assertIsNone(held.query(report, offset=12, limit=4)["next_offset"])
        self.assertEqual(held.query(report, offset=99)["rows"], [])
        for bad in (-1, 0, 101, True, None):
            with self.subTest(limit=bad), self.assertRaisesRegex(ValueError, "Invalid query window"):
                held.query(report, limit=bad)
        for bad in (-1, True, 1_000_001):
            with self.subTest(offset=bad), self.assertRaisesRegex(ValueError, "Invalid query window"):
                held.query(report, offset=bad)
        for key in ("text", "row_id", "kind", "status", "source_family", "tag"):
            with self.subTest(field=key), self.assertRaisesRegex(ValueError, "Invalid bounded"):
                held.query(report, **{key: "x" * 161})

    def test_all_three_accepted_packet_mutations_fail_before_projection(self):
        for kind, relative, pin, _ in held.PACKETS:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                target = root / relative
                target.parent.mkdir(parents=True)
                target.write_bytes((held.ROOT / relative).read_bytes())
                self.assertEqual(hashlib.sha256(held._pinned_bytes(root, relative, pin)).hexdigest(), pin)
                data = json.loads(target.read_text(encoding="utf-8"))
                data["coverage_effect"] = "CLOSE_READ"
                target.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Accepted source digest drift"):
                    held._pinned_bytes(root, relative, pin)
                target.unlink()
                try:
                    target.symlink_to(held.ROOT / relative)
                except OSError:
                    # Windows accounts without the symlink privilege cannot
                    # create this fixture; the host-independent hash checks
                    # above still execute.
                    pass
                else:
                    with self.assertRaisesRegex(ValueError, "Source alias refused"):
                        held._pinned_bytes(root, relative, pin)

    def test_validator_integrity_and_failure_are_fail_closed(self):
        kind, path, sha, validator_sha = held.PACKETS[0]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / path
            source.parent.mkdir(parents=True)
            shutil.copy2(held.ROOT / path, source)
            validator = source.with_name("validate.py")
            shutil.copy2(held.ROOT / Path(path).with_name("validate.py"), validator)
            validator.write_text("print('tampered')", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Accepted source digest drift"):
                held._validated_packet(root, kind, path, sha, validator_sha)
        with patch.object(held.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "failed")):
            with self.assertRaisesRegex(ValueError, "Original .* validator rejected"):
                held._validated_packet(held.ROOT, kind, path, sha, validator_sha)

    def test_cli_is_callable_and_does_not_release_held_synopses_or_art(self):
        command = [sys.executable, str(held.ROOT / "tools/query_accepted_held_packets.py")]
        process = subprocess.run(command + ["--kind", "VOY_GUIDE_CARD", "--limit", "2"],
                                 check=True, capture_output=True, text=True)
        data = json.loads(process.stdout)
        self.assertEqual(data["total_matches"], 5)
        self.assertEqual(len(data["rows"]), 2)
        self.assertEqual(data["public_explorer_effect"], "NONE")
        self.assertNotIn("Janeway makes an uneasy pact", process.stdout)
        invalid = subprocess.run(command + ["--limit", "0"], capture_output=True, text=True)
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("Invalid query window", invalid.stderr)
        self.assertNotIn("Traceback", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
